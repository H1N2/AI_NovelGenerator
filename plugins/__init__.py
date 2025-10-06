# plugins/__init__.py
"""
插件系统核心模块
提供插件管理、事件系统、通信等功能
"""

from .base import NovelGeneratorPlugin, PluginState, PluginMetadata, PluginContext
from .manager import PluginManager
from .registry import PluginRegistry
from .events import PluginEventSystem, get_event_system, AppEvents, EventPriority
from .communicator import PluginCommunicator
from .version_manager import VersionCompatibilityManager, get_version_manager, CompatibilityLevel
from .performance import PluginPerformanceMonitor, get_performance_monitor
from .crash_handler import (
    PluginCrashHandler, get_crash_handler, 
    CrashSeverity, handle_plugin_crash
)
from .logging_system import (
    PluginLoggingSystem, get_plugin_logging_system, 
    LogLevel, LogFormat, PluginLogger
)

__all__ = [
    'NovelGeneratorPlugin',
    'PluginState', 
    'PluginMetadata',
    'PluginContext',
    'PluginManager',
    'PluginRegistry',
    'PluginEventSystem',
    'get_event_system',
    'AppEvents',
    'EventPriority',
    'PluginCommunicator',
    'VersionCompatibilityManager',
    'get_version_manager',
    'CompatibilityLevel',
    'PluginPerformanceMonitor',
    'get_performance_monitor',
    'PluginCrashHandler',
    'get_crash_handler',
    'CrashSeverity',
    'handle_plugin_crash',
    'PluginLoggingSystem',
    'get_plugin_logging_system',
    'LogLevel',
    'LogFormat',
    'PluginLogger'
]