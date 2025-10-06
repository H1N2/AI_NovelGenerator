# plugins/crash_handler.py
"""
插件崩溃处理模块
提供插件异常捕获、重启尝试、自动禁用等功能
"""

import logging
import traceback
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import json

class CrashSeverity(Enum):
    """崩溃严重程度"""
    LOW = "low"          # 轻微错误，可以继续运行
    MEDIUM = "medium"    # 中等错误，需要重启
    HIGH = "high"        # 严重错误，需要禁用插件
    CRITICAL = "critical" # 致命错误，立即禁用

@dataclass
class CrashRecord:
    """崩溃记录"""
    plugin_name: str
    timestamp: datetime
    exception_type: str
    exception_message: str
    traceback_info: str
    severity: CrashSeverity
    operation: str = ""  # 发生崩溃的操作
    recovery_attempted: bool = False
    recovery_successful: bool = False
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'plugin_name': self.plugin_name,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'traceback_info': self.traceback_info,
            'severity': self.severity.value,
            'operation': self.operation,
            'recovery_attempted': self.recovery_attempted,
            'recovery_successful': self.recovery_successful
        }

@dataclass
class CrashPolicy:
    """崩溃处理策略"""
    max_crashes_per_hour: int = 3      # 每小时最大崩溃次数
    max_crashes_total: int = 10        # 总最大崩溃次数
    restart_attempts: int = 2          # 重启尝试次数
    restart_delay: float = 1.0         # 重启延迟（秒）
    auto_disable_threshold: int = 5    # 自动禁用阈值
    recovery_timeout: float = 30.0     # 恢复超时时间（秒）
    
    # 不同严重程度的处理策略
    severity_policies: Dict[CrashSeverity, dict] = field(default_factory=lambda: {
        CrashSeverity.LOW: {
            'auto_restart': True,
            'max_restarts': 5,
            'disable_on_failure': False
        },
        CrashSeverity.MEDIUM: {
            'auto_restart': True,
            'max_restarts': 3,
            'disable_on_failure': True
        },
        CrashSeverity.HIGH: {
            'auto_restart': False,
            'max_restarts': 1,
            'disable_on_failure': True
        },
        CrashSeverity.CRITICAL: {
            'auto_restart': False,
            'max_restarts': 0,
            'disable_on_failure': True
        }
    })

class PluginCrashHandler:
    """插件崩溃处理器"""
    
    def __init__(self, crash_log_dir: str = "logs/crashes"):
        self.crash_log_dir = Path(crash_log_dir)
        self.crash_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 崩溃记录存储
        self._crash_records: Dict[str, List[CrashRecord]] = {}
        self._crash_counts: Dict[str, int] = {}
        self._disabled_plugins: set = set()
        self._restart_attempts: Dict[str, int] = {}
        
        # 默认崩溃策略
        self._default_policy = CrashPolicy()
        self._plugin_policies: Dict[str, CrashPolicy] = {}
        
        # 恢复回调函数
        self._recovery_callbacks: Dict[str, Callable] = {}
        
        # 设置日志
        self.logger = logging.getLogger(f"{__name__}.CrashHandler")
        
        # 加载历史崩溃记录
        self._load_crash_history()
    
    def set_plugin_policy(self, plugin_name: str, policy: CrashPolicy):
        """设置插件特定的崩溃处理策略"""
        self._plugin_policies[plugin_name] = policy
        self.logger.info(f"为插件 {plugin_name} 设置崩溃处理策略")
    
    def get_plugin_policy(self, plugin_name: str) -> CrashPolicy:
        """获取插件的崩溃处理策略"""
        return self._plugin_policies.get(plugin_name, self._default_policy)
    
    def register_recovery_callback(self, plugin_name: str, callback: Callable):
        """注册插件恢复回调函数"""
        self._recovery_callbacks[plugin_name] = callback
        self.logger.debug(f"为插件 {plugin_name} 注册恢复回调")
    
    def handle_crash(self, plugin_name: str, exception: Exception, 
                    operation: str = "", severity: Optional[CrashSeverity] = None) -> bool:
        """
        处理插件崩溃
        
        Args:
            plugin_name: 插件名称
            exception: 异常对象
            operation: 发生崩溃的操作
            severity: 崩溃严重程度（如果未指定则自动判断）
            
        Returns:
            bool: 是否成功处理崩溃
        """
        # 自动判断严重程度
        if severity is None:
            severity = self._assess_crash_severity(exception)
        
        # 创建崩溃记录
        crash_record = CrashRecord(
            plugin_name=plugin_name,
            timestamp=datetime.now(),
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            traceback_info=traceback.format_exc(),
            severity=severity,
            operation=operation
        )
        
        # 记录崩溃
        self._record_crash(crash_record)
        
        # 获取处理策略
        policy = self.get_plugin_policy(plugin_name)
        
        # 检查是否应该禁用插件
        if self._should_disable_plugin(plugin_name, policy):
            self._disable_plugin(plugin_name)
            return False
        
        # 尝试恢复
        recovery_success = self._attempt_recovery(plugin_name, crash_record, policy)
        
        # 更新恢复状态
        crash_record.recovery_attempted = True
        crash_record.recovery_successful = recovery_success
        
        return recovery_success
    
    def _assess_crash_severity(self, exception: Exception) -> CrashSeverity:
        """评估崩溃严重程度"""
        # 根据异常类型判断严重程度
        if isinstance(exception, (MemoryError, SystemError)):
            return CrashSeverity.CRITICAL
        elif isinstance(exception, (ImportError, AttributeError, TypeError)):
            return CrashSeverity.HIGH
        elif isinstance(exception, (ValueError, KeyError, IndexError)):
            return CrashSeverity.MEDIUM
        else:
            return CrashSeverity.LOW
    
    def _record_crash(self, crash_record: CrashRecord):
        """记录崩溃信息"""
        plugin_name = crash_record.plugin_name
        
        # 添加到内存记录
        if plugin_name not in self._crash_records:
            self._crash_records[plugin_name] = []
        self._crash_records[plugin_name].append(crash_record)
        
        # 更新崩溃计数
        self._crash_counts[plugin_name] = self._crash_counts.get(plugin_name, 0) + 1
        
        # 记录到日志文件
        self._log_crash_to_file(crash_record)
        
        # 记录到系统日志
        self.logger.error(
            f"插件 {plugin_name} 发生 {crash_record.severity.value} 级别崩溃: "
            f"{crash_record.exception_type}: {crash_record.exception_message}"
        )
    
    def _log_crash_to_file(self, crash_record: CrashRecord):
        """将崩溃记录写入文件"""
        log_file = self.crash_log_dir / f"{crash_record.plugin_name}_crashes.json"
        
        # 读取现有记录
        crashes = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    crashes = json.load(f)
            except Exception as e:
                self.logger.warning(f"读取崩溃日志文件失败: {e}")
        
        # 添加新记录
        crashes.append(crash_record.to_dict())
        
        # 保持最近100条记录
        crashes = crashes[-100:]
        
        # 写入文件
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(crashes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"写入崩溃日志文件失败: {e}")
    
    def _should_disable_plugin(self, plugin_name: str, policy: CrashPolicy) -> bool:
        """判断是否应该禁用插件"""
        if plugin_name in self._disabled_plugins:
            return True
        
        crash_count = self._crash_counts.get(plugin_name, 0)
        
        # 检查总崩溃次数
        if crash_count >= policy.auto_disable_threshold:
            return True
        
        # 检查每小时崩溃次数
        recent_crashes = self._get_recent_crashes(plugin_name, hours=1)
        if len(recent_crashes) >= policy.max_crashes_per_hour:
            return True
        
        return False
    
    def _attempt_recovery(self, plugin_name: str, crash_record: CrashRecord, 
                         policy: CrashPolicy) -> bool:
        """尝试恢复插件"""
        severity_policy = policy.severity_policies.get(crash_record.severity, {})
        
        if not severity_policy.get('auto_restart', False):
            return False
        
        max_restarts = severity_policy.get('max_restarts', 0)
        current_attempts = self._restart_attempts.get(plugin_name, 0)
        
        if current_attempts >= max_restarts:
            self.logger.warning(f"插件 {plugin_name} 重启次数已达上限")
            return False
        
        # 执行重启
        self._restart_attempts[plugin_name] = current_attempts + 1
        
        try:
            # 延迟重启
            time.sleep(policy.restart_delay)
            
            # 调用恢复回调
            if plugin_name in self._recovery_callbacks:
                callback = self._recovery_callbacks[plugin_name]
                callback()
                
                self.logger.info(f"插件 {plugin_name} 恢复成功 (第{current_attempts + 1}次尝试)")
                return True
            else:
                self.logger.warning(f"插件 {plugin_name} 没有注册恢复回调")
                return False
                
        except Exception as e:
            self.logger.error(f"插件 {plugin_name} 恢复失败: {e}")
            return False
    
    def _disable_plugin(self, plugin_name: str):
        """禁用插件"""
        self._disabled_plugins.add(plugin_name)
        self.logger.warning(f"插件 {plugin_name} 已被自动禁用")
    
    def _get_recent_crashes(self, plugin_name: str, hours: int = 1) -> List[CrashRecord]:
        """获取最近指定小时内的崩溃记录"""
        if plugin_name not in self._crash_records:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            record for record in self._crash_records[plugin_name]
            if record.timestamp > cutoff_time
        ]
    
    def get_crash_history(self, plugin_name: str) -> List[CrashRecord]:
        """获取插件崩溃历史记录"""
        return self._crash_records.get(plugin_name, [])
    
    def get_crash_statistics(self, plugin_name: Optional[str] = None) -> dict:
        """获取崩溃统计信息"""
        if plugin_name:
            records = self._crash_records.get(plugin_name, [])
            return {
                'plugin_name': plugin_name,
                'total_crashes': len(records),
                'crash_count_by_severity': self._count_by_severity(records),
                'recent_crashes_1h': len(self._get_recent_crashes(plugin_name, 1)),
                'recent_crashes_24h': len(self._get_recent_crashes(plugin_name, 24)),
                'is_disabled': plugin_name in self._disabled_plugins,
                'restart_attempts': self._restart_attempts.get(plugin_name, 0)
            }
        else:
            # 全局统计
            total_crashes = sum(len(records) for records in self._crash_records.values())
            all_records = [record for records in self._crash_records.values() for record in records]
            
            return {
                'total_plugins_with_crashes': len(self._crash_records),
                'total_crashes': total_crashes,
                'crash_count_by_severity': self._count_by_severity(all_records),
                'disabled_plugins': list(self._disabled_plugins),
                'plugins_with_recent_crashes': [
                    name for name in self._crash_records.keys()
                    if self._get_recent_crashes(name, 1)
                ]
            }
    
    def _count_by_severity(self, records: List[CrashRecord]) -> Dict[str, int]:
        """按严重程度统计崩溃次数"""
        counts = {severity.value: 0 for severity in CrashSeverity}
        for record in records:
            counts[record.severity.value] += 1
        return counts
    
    def _load_crash_history(self):
        """加载历史崩溃记录"""
        try:
            for log_file in self.crash_log_dir.glob("*_crashes.json"):
                plugin_name = log_file.stem.replace("_crashes", "")
                
                with open(log_file, 'r', encoding='utf-8') as f:
                    crash_data = json.load(f)
                
                records = []
                for data in crash_data:
                    try:
                        record = CrashRecord(
                            plugin_name=data['plugin_name'],
                            timestamp=datetime.fromisoformat(data['timestamp']),
                            exception_type=data['exception_type'],
                            exception_message=data['exception_message'],
                            traceback_info=data['traceback_info'],
                            severity=CrashSeverity(data['severity']),
                            operation=data.get('operation', ''),
                            recovery_attempted=data.get('recovery_attempted', False),
                            recovery_successful=data.get('recovery_successful', False)
                        )
                        records.append(record)
                    except Exception as e:
                        self.logger.warning(f"解析崩溃记录失败: {e}")
                
                if records:
                    self._crash_records[plugin_name] = records
                    self._crash_counts[plugin_name] = len(records)
                    
        except Exception as e:
            self.logger.error(f"加载崩溃历史失败: {e}")
    
    def clear_crash_history(self, plugin_name: Optional[str] = None):
        """清除崩溃历史"""
        if plugin_name:
            # 清除特定插件的记录
            self._crash_records.pop(plugin_name, None)
            self._crash_counts.pop(plugin_name, 0)
            self._restart_attempts.pop(plugin_name, 0)
            
            # 删除日志文件
            log_file = self.crash_log_dir / f"{plugin_name}_crashes.json"
            if log_file.exists():
                log_file.unlink()
                
            self.logger.info(f"已清除插件 {plugin_name} 的崩溃历史")
        else:
            # 清除所有记录
            self._crash_records.clear()
            self._crash_counts.clear()
            self._restart_attempts.clear()
            
            # 删除所有日志文件
            for log_file in self.crash_log_dir.glob("*_crashes.json"):
                log_file.unlink()
                
            self.logger.info("已清除所有插件的崩溃历史")
    
    def enable_plugin(self, plugin_name: str):
        """重新启用被禁用的插件"""
        if plugin_name in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_name)
            self._restart_attempts.pop(plugin_name, 0)  # 重置重启计数
            self.logger.info(f"插件 {plugin_name} 已重新启用")
    
    def is_plugin_disabled(self, plugin_name: str) -> bool:
        """检查插件是否被禁用"""
        return plugin_name in self._disabled_plugins

# 全局崩溃处理器实例
_crash_handler = None

def get_crash_handler() -> PluginCrashHandler:
    """获取全局崩溃处理器实例"""
    global _crash_handler
    if _crash_handler is None:
        _crash_handler = PluginCrashHandler()
    return _crash_handler

def handle_plugin_crash(plugin_name: str, exception: Exception, 
                       operation: str = "", severity: Optional[CrashSeverity] = None) -> bool:
    """便捷函数：处理插件崩溃"""
    return get_crash_handler().handle_crash(plugin_name, exception, operation, severity)