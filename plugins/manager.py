# plugins/manager.py
"""
插件管理器
负责插件的发现、加载、卸载、生命周期管理等
"""

import os
import json
import importlib.util
import logging
from .version_manager import get_version_manager, CompatibilityLevel
import traceback
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from .base import NovelGeneratorPlugin, PluginMetadata, PluginState, PluginContext
from .registry import PluginRegistry
from .events import PluginEventSystem
from .performance import PluginPerformanceMonitor
from .crash_handler import get_crash_handler, CrashSeverity
from .logging_system import get_plugin_logging_system, LogLevel


class PluginManager:
    """插件管理器"""
    
    def __init__(self, app_instance, plugins_dir: str = "plugins"):
        self.app = app_instance
        self.plugins_dir = Path(plugins_dir)
        self.registry = PluginRegistry()
        self.event_system = PluginEventSystem()
        self.performance_monitor = PluginPerformanceMonitor()
        self.version_manager = get_version_manager(getattr(app_instance, 'version', '1.0.0'))
        self.crash_handler = get_crash_handler()
        self.logging_system = get_plugin_logging_system()
        
        # 插件实例存储
        self._loaded_plugins: Dict[str, NovelGeneratorPlugin] = {}
        self._plugin_modules: Dict[str, Any] = {}
        self._plugin_states: Dict[str, PluginState] = {}
        self._disabled_plugins: set = set()
        
        # 崩溃处理
        self._crash_counts: Dict[str, int] = {}
        self._max_crash_count = 3
        
        # 日志设置
        self._setup_logging()
        
        # 注册崩溃恢复回调
        self._setup_crash_recovery()
        
        # 确保插件目录存在
        self.plugins_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"插件管理器初始化完成，插件目录: {self.plugins_dir}")
        
        # 自动发现插件
        self.discover_plugins()
        
    def _setup_logging(self):
        """设置插件专用日志"""
        log_dir = Path("logs/plugins")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建插件日志记录器
        self.logger = logging.getLogger("plugin_manager")
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_dir / "plugin_manager.log", encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 错误日志处理器
        error_handler = logging.FileHandler(log_dir / "plugin_errors.log", encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def _setup_crash_recovery(self):
        """设置崩溃恢复回调"""
        # 为每个插件注册恢复回调
        def create_recovery_callback(plugin_name: str):
            def recovery_callback():
                """插件恢复回调函数"""
                try:
                    # 尝试重新加载插件
                    if plugin_name in self._loaded_plugins:
                        # 先卸载
                        self.unload_plugin(plugin_name)
                    
                    # 重新加载
                    success = self.load_plugin(plugin_name)
                    if success:
                        self.logger.info(f"插件 {plugin_name} 恢复成功")
                    else:
                        self.logger.error(f"插件 {plugin_name} 恢复失败")
                        
                    return success
                except Exception as e:
                    self.logger.error(f"插件 {plugin_name} 恢复过程中发生异常: {e}")
                    return False
            
            return recovery_callback
        
        # 注册所有已发现插件的恢复回调
        for metadata in self.registry.get_all_plugins():
            callback = create_recovery_callback(metadata.name)
            self.crash_handler.register_recovery_callback(metadata.name, callback)
        
    def discover_plugins(self) -> List[PluginMetadata]:
        """发现插件"""
        discovered = []
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
                
            plugin_json = plugin_dir / "plugin.json"
            if not plugin_json.exists():
                continue
                
            try:
                with open(plugin_json, 'r', encoding='utf-8') as f:
                    plugin_data = json.load(f)
                    
                metadata = PluginMetadata(**plugin_data)
                self.registry.register_plugin(metadata)
                discovered.append(metadata)
                
                self.logger.info(f"发现插件: {metadata.name} v{metadata.version}")
                
            except Exception as e:
                self.logger.error(f"解析插件配置失败 {plugin_dir}: {e}")
                
        return discovered
        
    def load_plugin(self, plugin_name: str) -> bool:
        """加载插件"""
        try:
            # 检查插件是否被禁用
            if self.crash_handler.is_plugin_disabled(plugin_name):
                self.logger.warning(f"插件 {plugin_name} 已被禁用，无法加载")
                return False
                
            if plugin_name in self._loaded_plugins:
                self.logger.warning(f"插件 {plugin_name} 已经加载")
                return True
                
            metadata = self.registry.get_plugin(plugin_name)
            if not metadata:
                self.logger.error(f"未找到插件: {plugin_name}")
                return False
                
            # 检查版本兼容性
            if not self._check_version_compatibility(metadata):
                self.logger.error(f"插件 {plugin_name} 版本不兼容")
                return False
                
            # 加载插件模块
            plugin_module = self._load_plugin_module(metadata)
            if not plugin_module:
                return False
                
            # 创建插件实例
            plugin_class = getattr(plugin_module, metadata.entry_point, None)
            if not plugin_class:
                self.logger.error(f"插件 {plugin_name} 未找到入口点: {metadata.entry_point}")
                return False
                
            plugin_instance = plugin_class()
            plugin_instance.metadata = metadata
            plugin_instance.state = PluginState.LOADED
            
            # 为插件创建专用日志记录器
            plugin_logger = self.logging_system.create_plugin_logger(plugin_name)
            plugin_instance.logger = plugin_logger
            
            # 初始化插件
            context = PluginContext(self.app, self)
            if not plugin_instance.initialize(context):
                self.logger.error(f"插件 {plugin_name} 初始化失败")
                return False
                
            plugin_instance.context = context
            plugin_instance.state = PluginState.INITIALIZED
            
            # 存储插件
            self._loaded_plugins[plugin_name] = plugin_instance
            self._plugin_modules[plugin_name] = plugin_module
            
            # 注册事件监听
            self.event_system.register_listener(plugin_name, plugin_instance.on_event)
            
            # 激活插件
            plugin_instance.state = PluginState.ACTIVE
            
            # 注册崩溃恢复回调
            def recovery_callback():
                return self.reload_plugin(plugin_name)
            self.crash_handler.register_recovery_callback(plugin_name, recovery_callback)
            
            self.logger.info(f"插件 {plugin_name} 加载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"加载插件 {plugin_name} 失败: {e}")
            self.logger.error(traceback.format_exc())
            
            # 使用崩溃处理器记录加载失败
            self.crash_handler.handle_crash(plugin_name, e, "plugin_load", CrashSeverity.HIGH)
            return False
            
    def _load_plugin_module(self, metadata: PluginMetadata):
        """加载插件模块"""
        plugin_dir = self.plugins_dir / metadata.name
        main_file = plugin_dir / "main.py"
        
        if not main_file.exists():
            self.logger.error(f"插件 {metadata.name} 主文件不存在: {main_file}")
            return None
            
        spec = importlib.util.spec_from_file_location(
            f"plugin_{metadata.name}", main_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
        
    def _check_version_compatibility(self, metadata: PluginMetadata) -> bool:
        """检查版本兼容性"""
        try:
            # 使用版本管理器进行兼容性检查
            compatibility, message = self.version_manager.check_compatibility(
                metadata.name, 
                metadata.version,
                metadata.min_app_version
            )
            
            # 记录兼容性检查结果
            if compatibility == CompatibilityLevel.COMPATIBLE:
                self.logger.info(f"插件 {metadata.name} 版本兼容: {message}")
                return True
            elif compatibility == CompatibilityLevel.BACKWARD_COMPATIBLE:
                self.logger.warning(f"插件 {metadata.name} 向后兼容: {message}")
                return True
            elif compatibility == CompatibilityLevel.DEPRECATED:
                self.logger.warning(f"插件 {metadata.name} 版本已弃用: {message}")
                # 弃用版本仍可加载，但发出警告
                return True
            else:
                self.logger.error(f"插件 {metadata.name} 版本不兼容: {message}")
                return False
                
        except Exception as e:
            self.logger.error(f"检查插件 {metadata.name} 版本兼容性时出错: {e}")
            return False
        
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        try:
            if plugin_name not in self._loaded_plugins:
                return True
                
            plugin = self._loaded_plugins[plugin_name]
            
            # 清理插件
            plugin.cleanup()
            plugin.state = PluginState.UNLOADED
            
            # 移除事件监听
            self.event_system.unregister_listener(plugin_name)
            
            # 清理插件日志记录器
            self.logging_system.remove_plugin_logger(plugin_name)
            
            # 移除插件
            del self._loaded_plugins[plugin_name]
            if plugin_name in self._plugin_modules:
                del self._plugin_modules[plugin_name]
                
            self.logger.info(f"插件 {plugin_name} 卸载成功")
            return True
            
        except Exception as e:
            self.logger.error(f"卸载插件 {plugin_name} 失败: {e}")
            return False
            
    def get_loaded_plugins(self) -> Dict[str, NovelGeneratorPlugin]:
        """获取已加载的插件"""
        return self._loaded_plugins.copy()
        
    def get_plugin(self, plugin_name: str) -> Optional[NovelGeneratorPlugin]:
        """获取指定插件"""
        return self._loaded_plugins.get(plugin_name)
        
    def call_plugin_service(self, plugin_name: str, service_name: str, *args, **kwargs) -> Any:
        """调用插件服务"""
        # 检查插件是否被禁用
        if self.crash_handler.is_plugin_disabled(plugin_name):
            raise ValueError(f"插件 {plugin_name} 已被禁用")
            
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"插件 {plugin_name} 未加载")
            
        services = plugin.get_services()
        if service_name not in services:
            raise ValueError(f"插件 {plugin_name} 不提供服务 {service_name}")
            
        try:
            # 性能监控
            start_time = time.time()
            result = services[service_name](*args, **kwargs)
            execution_time = time.time() - start_time
            
            self.performance_monitor.record_service_call(
                plugin_name, service_name, execution_time
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"调用插件服务失败 {plugin_name}.{service_name}: {e}")
            # 使用新的崩溃处理器
            self.crash_handler.handle_crash(plugin_name, e, f"service_call:{service_name}")
            raise
            
    def emit_event(self, event_name: str, data: Any = None):
        """发送事件"""
        self.event_system.emit_event(event_name, data)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.performance_monitor.get_statistics()
        
    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        if self.unload_plugin(plugin_name):
            return self.load_plugin(plugin_name)
        return False
            
    def get_crash_statistics(self) -> dict:
        """获取崩溃统计信息"""
        return self.crash_handler.get_crash_statistics()
    
    def get_plugin_crash_statistics(self, plugin_name: str) -> dict:
        """获取特定插件的崩溃统计信息"""
        return self.crash_handler.get_crash_statistics(plugin_name)
    
    def enable_disabled_plugin(self, plugin_name: str) -> bool:
        """重新启用被禁用的插件"""
        if not self.crash_handler.is_plugin_disabled(plugin_name):
            self.logger.info(f"插件 {plugin_name} 未被禁用")
            return True
            
        # 启用插件
        self.crash_handler.enable_plugin(plugin_name)
        
        # 尝试重新加载
        return self.load_plugin(plugin_name)
    
    def clear_plugin_crash_history(self, plugin_name: str):
        """清除插件崩溃历史"""
        self.crash_handler.clear_crash_history(plugin_name)
    
    # 日志系统相关方法
    def get_plugin_logger(self, plugin_name: str):
        """获取插件的日志记录器"""
        return self.logging_system.get_plugin_logger(plugin_name)
    
    def get_plugin_logs(self, plugin_name: str, level: LogLevel = None, limit: int = 100):
        """获取插件日志记录"""
        return self.logging_system.get_plugin_logs(plugin_name, level, limit)
    
    def search_plugin_logs(self, plugin_name: str, keyword: str, start_time=None, end_time=None):
        """搜索插件日志"""
        return self.logging_system.search_plugin_logs(plugin_name, keyword, start_time, end_time)
    
    def export_plugin_logs(self, plugin_name: str, format_type: str = "json"):
        """导出插件日志"""
        return self.logging_system.export_plugin_logs(plugin_name, format_type)
    
    def get_logging_statistics(self):
        """获取日志统计信息"""
        return self.logging_system.get_statistics()