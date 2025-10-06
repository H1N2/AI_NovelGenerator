# plugins/events.py
"""
插件事件系统
支持插件间的事件通信和应用程序事件处理
"""

import threading
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time
import weakref


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """事件数据类"""
    name: str
    data: Any = None
    source: Optional[str] = None
    timestamp: float = None
    priority: EventPriority = EventPriority.NORMAL
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventHandler:
    """事件处理器包装类"""
    
    def __init__(self, handler: Callable, plugin_name: str, priority: EventPriority = EventPriority.NORMAL):
        self.handler = handler
        self.plugin_name = plugin_name
        self.priority = priority
        self.call_count = 0
        self.total_time = 0.0
        self.last_called = None
        
    def __call__(self, event: Event) -> Any:
        """调用处理器"""
        start_time = time.time()
        try:
            result = self.handler(event)
            self.call_count += 1
            self.total_time += time.time() - start_time
            self.last_called = time.time()
            return result
        except Exception as e:
            logging.error(f"事件处理器 {self.plugin_name}.{self.handler.__name__} 执行失败: {e}")
            raise
            
    @property
    def avg_time(self) -> float:
        """平均执行时间"""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0


class PluginEventSystem:
    """插件事件系统"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._lock = threading.RLock()
        self._logger = logging.getLogger("plugin_events")
        
        # 性能统计
        self._stats = {
            'total_events': 0,
            'total_handlers_called': 0,
            'total_execution_time': 0.0,
            'events_by_name': {},
            'handlers_by_plugin': {}
        }
        
    def register_handler(self, event_name: str, handler: Callable, 
                        plugin_name: str, priority: EventPriority = EventPriority.NORMAL):
        """注册事件处理器"""
        with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
                
            event_handler = EventHandler(handler, plugin_name, priority)
            self._handlers[event_name].append(event_handler)
            
            # 按优先级排序
            self._handlers[event_name].sort(key=lambda h: h.priority.value, reverse=True)
            
            self._logger.info(f"注册事件处理器: {plugin_name}.{handler.__name__} -> {event_name}")
            
    def unregister_handler(self, event_name: str, plugin_name: str, handler: Callable = None):
        """注销事件处理器"""
        with self._lock:
            if event_name not in self._handlers:
                return
                
            handlers = self._handlers[event_name]
            if handler is None:
                # 移除该插件的所有处理器
                self._handlers[event_name] = [h for h in handlers if h.plugin_name != plugin_name]
            else:
                # 移除特定处理器
                self._handlers[event_name] = [
                    h for h in handlers 
                    if not (h.plugin_name == plugin_name and h.handler == handler)
                ]
                
            # 如果没有处理器了，删除事件
            if not self._handlers[event_name]:
                del self._handlers[event_name]
                
            self._logger.info(f"注销事件处理器: {plugin_name} -> {event_name}")
    
    def unregister_plugin_handlers(self, plugin_name: str):
        """注销插件的所有事件处理器"""
        with self._lock:
            for event_name in list(self._handlers.keys()):
                self.unregister_handler(event_name, plugin_name)
    
    def emit_event(self, event_name: str, data: Any = None, source: str = None, 
                   priority: EventPriority = EventPriority.NORMAL) -> List[Any]:
        """发送事件"""
        event = Event(event_name, data, source, priority=priority)
        return self.emit_event_object(event)
    
    def emit_event_object(self, event: Event) -> List[Any]:
        """发送事件对象"""
        results = []
        
        with self._lock:
            # 记录事件历史
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # 更新统计
            self._stats['total_events'] += 1
            if event.name not in self._stats['events_by_name']:
                self._stats['events_by_name'][event.name] = 0
            self._stats['events_by_name'][event.name] += 1
            
            # 获取处理器
            handlers = self._handlers.get(event.name, [])
            
            start_time = time.time()
            
            for handler in handlers:
                try:
                    result = handler(event)
                    results.append(result)
                    
                    # 更新统计
                    self._stats['total_handlers_called'] += 1
                    if handler.plugin_name not in self._stats['handlers_by_plugin']:
                        self._stats['handlers_by_plugin'][handler.plugin_name] = {
                            'calls': 0,
                            'total_time': 0.0,
                            'avg_time': 0.0
                        }
                    
                    plugin_stats = self._stats['handlers_by_plugin'][handler.plugin_name]
                    plugin_stats['calls'] += 1
                    plugin_stats['total_time'] += handler.total_time
                    plugin_stats['avg_time'] = plugin_stats['total_time'] / plugin_stats['calls']
                    
                except Exception as e:
                    self._logger.error(f"事件处理器执行失败 {handler.plugin_name}: {e}")
                    results.append(None)
            
            self._stats['total_execution_time'] += time.time() - start_time
            
        return results
    
    def emit_event_async(self, event_name: str, data: Any = None, source: str = None,
                        priority: EventPriority = EventPriority.NORMAL):
        """异步发送事件"""
        import threading
        
        def async_emit():
            self.emit_event(event_name, data, source, priority)
        
        thread = threading.Thread(target=async_emit, daemon=True)
        thread.start()
        return thread
    
    def emit_event_with_filter(self, event_name: str, data: Any = None, source: str = None,
                              priority: EventPriority = EventPriority.NORMAL,
                              plugin_filter: Callable[[str], bool] = None) -> List[Any]:
        """带过滤器的事件发送"""
        event = Event(event_name, data, source, priority=priority)
        results = []
        
        with self._lock:
            # 记录事件历史
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # 更新统计
            self._stats['total_events'] += 1
            if event.name not in self._stats['events_by_name']:
                self._stats['events_by_name'][event.name] = 0
            self._stats['events_by_name'][event.name] += 1
            
            # 获取处理器并应用过滤器
            handlers = self._handlers.get(event.name, [])
            if plugin_filter:
                handlers = [h for h in handlers if plugin_filter(h.plugin_name)]
            
            start_time = time.time()
            
            for handler in handlers:
                try:
                    result = handler(event)
                    results.append(result)
                    self._stats['total_handlers_called'] += 1
                except Exception as e:
                    self._logger.error(f"事件处理器执行失败 {handler.plugin_name}: {e}")
                    results.append(None)
            
            self._stats['total_execution_time'] += time.time() - start_time
            
        return results
    
    def emit_batch_events(self, events: List[Event]) -> Dict[str, List[Any]]:
        """批量发送事件"""
        results = {}
        
        for event in events:
            results[f"{event.name}_{event.timestamp}"] = self.emit_event_object(event)
        
        return results
    
    def register_listener(self, plugin_name: str, listener: Callable):
        """注册插件监听器（兼容旧接口）"""
        # 这是一个通用监听器，监听所有事件
        def universal_handler(event: Event):
            return listener(event.name, event.data)
        
        # 为常见事件注册处理器
        common_events = [
            AppEvents.APP_STARTUP, AppEvents.APP_SHUTDOWN,
            AppEvents.PLUGIN_LOADED, AppEvents.PLUGIN_UNLOADED,
            AppEvents.CONFIG_CHANGE
        ]
        
        for event_name in common_events:
            self.register_handler(event_name, universal_handler, plugin_name)
    
    def unregister_listener(self, plugin_name: str):
        """注销插件监听器（兼容旧接口）"""
        self.unregister_plugin_handlers(plugin_name)

    def get_event_handlers(self, event_name: str) -> List[EventHandler]:
        """获取事件的处理器列表"""
        with self._lock:
            return self._handlers.get(event_name, []).copy()
            
    def get_all_events(self) -> List[str]:
        """获取所有已注册的事件名称"""
        with self._lock:
            return list(self._handlers.keys())
            
    def get_plugin_handlers(self, plugin_name: str) -> Dict[str, List[EventHandler]]:
        """获取插件注册的所有处理器"""
        result = {}
        with self._lock:
            for event_name, handlers in self._handlers.items():
                plugin_handlers = [h for h in handlers if h.plugin_name == plugin_name]
                if plugin_handlers:
                    result[event_name] = plugin_handlers
        return result
        
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """获取事件历史记录"""
        with self._lock:
            return self._event_history[-limit:].copy()
            
    def get_statistics(self) -> Dict[str, Any]:
        """获取事件系统统计信息"""
        with self._lock:
            stats = self._stats.copy()
            
            # 添加处理器统计
            stats['total_handlers'] = sum(len(handlers) for handlers in self._handlers.values())
            stats['events_registered'] = len(self._handlers)
            
            # 计算平均执行时间
            if stats['total_handlers_called'] > 0:
                stats['avg_execution_time'] = stats['total_execution_time'] / stats['total_handlers_called']
            else:
                stats['avg_execution_time'] = 0.0
                
            # 添加插件平均时间
            for plugin_name, plugin_stats in stats['handlers_by_plugin'].items():
                if plugin_stats['calls'] > 0:
                    plugin_stats['avg_time'] = plugin_stats['total_time'] / plugin_stats['calls']
                else:
                    plugin_stats['avg_time'] = 0.0
                    
            return stats
            
    def clear_history(self):
        """清空事件历史记录"""
        with self._lock:
            self._event_history.clear()
            
    def clear_statistics(self):
        """清空统计信息"""
        with self._lock:
            self._stats = {
                'total_events': 0,
                'total_handlers_called': 0,
                'total_execution_time': 0.0,
                'events_by_name': {},
                'handlers_by_plugin': {}
            }


# 全局事件系统实例
_global_event_system = None


def get_event_system() -> PluginEventSystem:
    """获取全局事件系统实例"""
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = PluginEventSystem()
    return _global_event_system


# 应用程序事件常量
class AppEvents:
    """应用程序事件常量"""
    
    # 应用程序生命周期事件
    APP_STARTUP = "app.startup"
    APP_SHUTDOWN = "app.shutdown"
    APP_READY = "app.ready"
    APP_ERROR = "app.error"
    
    # 小说生成事件
    NOVEL_GENERATION_START = "novel.generation.start"
    NOVEL_GENERATION_COMPLETE = "novel.generation.complete"
    NOVEL_GENERATION_ERROR = "novel.generation.error"
    NOVEL_GENERATION_PROGRESS = "novel.generation.progress"
    
    # 章节事件
    CHAPTER_GENERATION_START = "chapter.generation.start"
    CHAPTER_GENERATION_COMPLETE = "chapter.generation.complete"
    CHAPTER_SAVE = "chapter.save"
    CHAPTER_LOAD = "chapter.load"
    CHAPTER_DELETE = "chapter.delete"
    CHAPTER_EDIT = "chapter.edit"
    
    # 配置事件
    CONFIG_LOAD = "config.load"
    CONFIG_SAVE = "config.save"
    CONFIG_CHANGE = "config.change"
    CONFIG_VALIDATE = "config.validate"
    
    # 插件事件
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    PLUGIN_ERROR = "plugin.error"
    PLUGIN_CRASH = "plugin.crash"
    PLUGIN_RECOVERY = "plugin.recovery"
    PLUGIN_DISABLED = "plugin.disabled"
    PLUGIN_ENABLED = "plugin.enabled"
    
    # UI事件
    UI_TAB_CHANGE = "ui.tab.change"
    UI_WINDOW_CLOSE = "ui.window.close"
    UI_THEME_CHANGE = "ui.theme.change"
    UI_LANGUAGE_CHANGE = "ui.language.change"
    
    # 数据事件
    DATA_IMPORT = "data.import"
    DATA_EXPORT = "data.export"
    DATA_PROCESS = "data.process"
    DATA_BACKUP = "data.backup"
    DATA_RESTORE = "data.restore"
    
    # 文件系统事件
    FILE_CREATED = "file.created"
    FILE_MODIFIED = "file.modified"
    FILE_DELETED = "file.deleted"
    FILE_MOVED = "file.moved"
    
    # 网络事件
    NETWORK_CONNECTED = "network.connected"
    NETWORK_DISCONNECTED = "network.disconnected"
    NETWORK_ERROR = "network.error"
    
    # 性能事件
    PERFORMANCE_WARNING = "performance.warning"
    PERFORMANCE_CRITICAL = "performance.critical"
    MEMORY_WARNING = "memory.warning"
    
    # 用户交互事件
    USER_ACTION = "user.action"
    USER_INPUT = "user.input"
    USER_SELECTION = "user.selection"


# 便捷函数
def emit_event(event_name: str, data: Any = None, source: str = None):
    """发送事件的便捷函数"""
    return get_event_system().emit_event(event_name, data, source)


def register_handler(event_name: str, handler: Callable, plugin_name: str, 
                    priority: EventPriority = EventPriority.NORMAL):
    """注册事件处理器的便捷函数"""
    return get_event_system().register_handler(event_name, handler, plugin_name, priority)


def unregister_handler(event_name: str, plugin_name: str, handler: Callable = None):
    """注销事件处理器的便捷函数"""
    return get_event_system().unregister_handler(event_name, plugin_name, handler)