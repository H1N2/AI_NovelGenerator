# plugins/logging_system.py
"""
插件专用日志系统
为每个插件提供独立的日志记录、调试支持和日志管理功能
"""

import logging
import logging.handlers
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import traceback
import sys
from contextlib import contextmanager

class LogLevel(Enum):
    """日志级别"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class LogFormat(Enum):
    """日志格式"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    CUSTOM = "custom"

@dataclass
class LogConfig:
    """日志配置"""
    level: LogLevel = LogLevel.INFO
    format_type: LogFormat = LogFormat.DETAILED
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_debug_mode: bool = False
    custom_format: Optional[str] = None
    
    # 日志过滤配置
    filter_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    # 性能配置
    async_logging: bool = False
    buffer_size: int = 1000

@dataclass
class LogRecord:
    """日志记录"""
    timestamp: datetime
    plugin_name: str
    level: str
    message: str
    module: str = ""
    function: str = ""
    line_number: int = 0
    thread_id: int = 0
    exception_info: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'plugin_name': self.plugin_name,
            'level': self.level,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'thread_id': self.thread_id,
            'exception_info': self.exception_info,
            'extra_data': self.extra_data
        }

class PluginLogFilter(logging.Filter):
    """插件日志过滤器"""
    
    def __init__(self, plugin_name: str, config: LogConfig):
        super().__init__()
        self.plugin_name = plugin_name
        self.config = config
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录"""
        # 检查包含模式
        if self.config.filter_patterns:
            if not any(pattern in record.getMessage() for pattern in self.config.filter_patterns):
                return False
        
        # 检查排除模式
        if self.config.exclude_patterns:
            if any(pattern in record.getMessage() for pattern in self.config.exclude_patterns):
                return False
        
        return True

class JSONFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def __init__(self, plugin_name: str):
        super().__init__()
        self.plugin_name = plugin_name
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'plugin_name': self.plugin_name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data['exception_info'] = self.formatException(record.exc_info)
        
        # 添加额外数据
        if hasattr(record, 'extra_data'):
            log_data['extra_data'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)

class PluginLogger:
    """插件专用日志记录器"""
    
    def __init__(self, plugin_name: str, config: LogConfig, log_dir: Path):
        self.plugin_name = plugin_name
        self.config = config
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger(f"plugin.{plugin_name}")
        self.logger.setLevel(config.level.value)
        self.logger.propagate = False  # 防止传播到根日志记录器
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 设置处理器
        self._setup_handlers()
        
        # 日志记录存储
        self._log_records: List[LogRecord] = []
        self._max_records = 1000
        self._lock = threading.Lock()
        
        # 调试模式
        self._debug_mode = config.enable_debug_mode
        self._debug_breakpoints: set = set()
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 文件处理器
        if self.config.enable_file:
            self._setup_file_handler()
        
        # 控制台处理器
        if self.config.enable_console:
            self._setup_console_handler()
    
    def _setup_file_handler(self):
        """设置文件处理器"""
        log_file = self.log_dir / f"{self.plugin_name}.log"
        
        # 使用轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        
        file_handler.setLevel(self.config.level.value)
        file_handler.setFormatter(self._get_formatter())
        file_handler.addFilter(PluginLogFilter(self.plugin_name, self.config))
        
        self.logger.addHandler(file_handler)
        
        # 错误日志单独文件
        error_file = self.log_dir / f"{self.plugin_name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_formatter())
        
        self.logger.addHandler(error_handler)
    
    def _setup_console_handler(self):
        """设置控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.config.level.value)
        console_handler.setFormatter(self._get_formatter())
        console_handler.addFilter(PluginLogFilter(self.plugin_name, self.config))
        
        self.logger.addHandler(console_handler)
    
    def _get_formatter(self) -> logging.Formatter:
        """获取格式化器"""
        if self.config.format_type == LogFormat.JSON:
            return JSONFormatter(self.plugin_name)
        elif self.config.format_type == LogFormat.SIMPLE:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        elif self.config.format_type == LogFormat.DETAILED:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - '
                '[%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
            )
        elif self.config.format_type == LogFormat.CUSTOM and self.config.custom_format:
            return logging.Formatter(self.config.custom_format)
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def _record_log(self, level: str, message: str, extra_data: Optional[Dict] = None):
        """记录日志到内存"""
        with self._lock:
            # 获取调用栈信息
            frame = sys._getframe(3)  # 跳过内部调用
            
            record = LogRecord(
                timestamp=datetime.now(),
                plugin_name=self.plugin_name,
                level=level,
                message=message,
                module=frame.f_code.co_filename.split('/')[-1],
                function=frame.f_code.co_name,
                line_number=frame.f_lineno,
                thread_id=threading.get_ident(),
                extra_data=extra_data or {}
            )
            
            self._log_records.append(record)
            
            # 保持记录数量限制
            if len(self._log_records) > self._max_records:
                self._log_records = self._log_records[-self._max_records:]
    
    def debug(self, message: str, extra_data: Optional[Dict] = None):
        """调试日志"""
        self.logger.debug(message, extra=extra_data or {})
        self._record_log("DEBUG", message, extra_data)
        
        # 调试断点检查
        if self._debug_mode and message in self._debug_breakpoints:
            self._trigger_breakpoint(message)
    
    def info(self, message: str, extra_data: Optional[Dict] = None):
        """信息日志"""
        self.logger.info(message, extra=extra_data or {})
        self._record_log("INFO", message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[Dict] = None):
        """警告日志"""
        self.logger.warning(message, extra=extra_data or {})
        self._record_log("WARNING", message, extra_data)
    
    def error(self, message: str, exception: Optional[Exception] = None, extra_data: Optional[Dict] = None):
        """错误日志"""
        if exception:
            self.logger.error(message, exc_info=exception, extra=extra_data or {})
            # 记录异常信息
            record_data = extra_data or {}
            record_data['exception_type'] = type(exception).__name__
            record_data['exception_message'] = str(exception)
            self._record_log("ERROR", message, record_data)
        else:
            self.logger.error(message, extra=extra_data or {})
            self._record_log("ERROR", message, extra_data)
    
    def critical(self, message: str, exception: Optional[Exception] = None, extra_data: Optional[Dict] = None):
        """严重错误日志"""
        if exception:
            self.logger.critical(message, exc_info=exception, extra=extra_data or {})
            record_data = extra_data or {}
            record_data['exception_type'] = type(exception).__name__
            record_data['exception_message'] = str(exception)
            self._record_log("CRITICAL", message, record_data)
        else:
            self.logger.critical(message, extra=extra_data or {})
            self._record_log("CRITICAL", message, extra_data)
    
    def exception(self, message: str, extra_data: Optional[Dict] = None):
        """异常日志（自动包含异常信息）"""
        self.logger.exception(message, extra=extra_data or {})
        
        # 获取异常信息
        exc_info = sys.exc_info()
        record_data = extra_data or {}
        if exc_info[1]:
            record_data['exception_type'] = type(exc_info[1]).__name__
            record_data['exception_message'] = str(exc_info[1])
            record_data['traceback'] = traceback.format_exc()
        
        self._record_log("ERROR", message, record_data)
    
    @contextmanager
    def log_context(self, context_name: str, extra_data: Optional[Dict] = None):
        """日志上下文管理器"""
        start_time = time.time()
        self.debug(f"进入上下文: {context_name}", extra_data)
        
        try:
            yield
        except Exception as e:
            self.error(f"上下文 {context_name} 发生异常", e, extra_data)
            raise
        finally:
            duration = time.time() - start_time
            final_data = extra_data or {}
            final_data['duration'] = duration
            self.debug(f"退出上下文: {context_name} (耗时: {duration:.3f}s)", final_data)
    
    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self._debug_mode = enabled
        if enabled:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(self.config.level.value)
    
    def add_debug_breakpoint(self, message: str):
        """添加调试断点"""
        self._debug_breakpoints.add(message)
    
    def remove_debug_breakpoint(self, message: str):
        """移除调试断点"""
        self._debug_breakpoints.discard(message)
    
    def _trigger_breakpoint(self, message: str):
        """触发调试断点"""
        print(f"\n=== 调试断点触发 ===")
        print(f"插件: {self.plugin_name}")
        print(f"消息: {message}")
        print(f"时间: {datetime.now()}")
        print("===================\n")
        
        # 这里可以集成调试器或提供交互式调试
        # import pdb; pdb.set_trace()
    
    def get_recent_logs(self, count: int = 100, level: Optional[str] = None) -> List[LogRecord]:
        """获取最近的日志记录"""
        with self._lock:
            records = self._log_records[-count:] if count > 0 else self._log_records[:]
            
            if level:
                records = [r for r in records if r.level == level.upper()]
            
            return records
    
    def search_logs(self, query: str, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None) -> List[LogRecord]:
        """搜索日志记录"""
        with self._lock:
            results = []
            
            for record in self._log_records:
                # 时间范围过滤
                if start_time and record.timestamp < start_time:
                    continue
                if end_time and record.timestamp > end_time:
                    continue
                
                # 文本搜索
                if query.lower() in record.message.lower():
                    results.append(record)
            
            return results
    
    def export_logs(self, file_path: str, format_type: str = "json", 
                   start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None):
        """导出日志记录"""
        with self._lock:
            records = self._log_records[:]
            
            # 时间范围过滤
            if start_time or end_time:
                filtered_records = []
                for record in records:
                    if start_time and record.timestamp < start_time:
                        continue
                    if end_time and record.timestamp > end_time:
                        continue
                    filtered_records.append(record)
                records = filtered_records
            
            # 导出
            if format_type.lower() == "json":
                data = [record.to_dict() for record in records]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format_type.lower() == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if records:
                        writer = csv.DictWriter(f, fieldnames=records[0].to_dict().keys())
                        writer.writeheader()
                        for record in records:
                            writer.writerow(record.to_dict())
    
    def clear_logs(self):
        """清除日志记录"""
        with self._lock:
            self._log_records.clear()

class PluginLoggingSystem:
    """插件日志系统管理器"""
    
    def __init__(self, base_log_dir: str = "logs/plugins"):
        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(parents=True, exist_ok=True)
        
        self._plugin_loggers: Dict[str, PluginLogger] = {}
        self._default_config = LogConfig()
        self._plugin_configs: Dict[str, LogConfig] = {}
        
        # 全局日志统计
        self._log_statistics: Dict[str, Dict[str, int]] = {}
        self._lock = threading.Lock()
    
    def get_logger(self, plugin_name: str, config: Optional[LogConfig] = None) -> PluginLogger:
        """获取插件日志记录器"""
        if plugin_name not in self._plugin_loggers:
            # 使用插件特定配置或默认配置
            logger_config = config or self._plugin_configs.get(plugin_name, self._default_config)
            
            # 创建插件专用日志目录
            plugin_log_dir = self.base_log_dir / plugin_name
            
            # 创建日志记录器
            logger = PluginLogger(plugin_name, logger_config, plugin_log_dir)
            self._plugin_loggers[plugin_name] = logger
            
            # 初始化统计
            with self._lock:
                self._log_statistics[plugin_name] = {
                    'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0
                }
        
        return self._plugin_loggers[plugin_name]
    
    def set_plugin_config(self, plugin_name: str, config: LogConfig):
        """设置插件日志配置"""
        self._plugin_configs[plugin_name] = config
        
        # 如果日志记录器已存在，重新创建
        if plugin_name in self._plugin_loggers:
            del self._plugin_loggers[plugin_name]
    
    def set_default_config(self, config: LogConfig):
        """设置默认日志配置"""
        self._default_config = config
    
    def get_all_loggers(self) -> Dict[str, PluginLogger]:
        """获取所有插件日志记录器"""
        return self._plugin_loggers.copy()
    
    def get_log_statistics(self) -> Dict[str, Dict[str, int]]:
        """获取日志统计信息"""
        with self._lock:
            return self._log_statistics.copy()
    
    def cleanup_old_logs(self, days: int = 30):
        """清理旧日志文件"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for plugin_dir in self.base_log_dir.iterdir():
            if plugin_dir.is_dir():
                for log_file in plugin_dir.glob("*.log*"):
                    try:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_time:
                            log_file.unlink()
                    except Exception:
                        pass  # 忽略清理错误

# 全局日志系统实例
_logging_system = None

def get_logging_system() -> PluginLoggingSystem:
    """获取全局日志系统实例"""
    global _logging_system
    if _logging_system is None:
        _logging_system = PluginLoggingSystem()
    return _logging_system

def get_plugin_logger(plugin_name: str, config: Optional[LogConfig] = None) -> PluginLogger:
    """便捷函数：获取插件日志记录器"""
    return get_logging_system().get_logger(plugin_name, config)