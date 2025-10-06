# plugins/base.py
"""
插件基类定义
所有插件都必须继承NovelGeneratorPlugin基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import customtkinter as ctk




class PluginState(Enum):
    """插件状态枚举"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    UNLOADED = "unloaded"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    description: str
    author: str
    min_app_version: str = "1.0.0"
    max_app_version: Optional[str] = None
    dependencies: List[str] = None
    entry_point: str = "main"
    main: str = "main.py"  # 主文件名
    ui_components: List[str] = None
    permissions: List[str] = None
    config: Dict[str, Any] = None
    requirements: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.ui_components is None:
            self.ui_components = []
        if self.permissions is None:
            self.permissions = []
        if self.config is None:
            self.config = {}
        if self.requirements is None:
            self.requirements = {}
        if self.metadata is None:
            self.metadata = {}


class PluginContext:
    """插件上下文，提供插件与主应用的接口"""
    
    def __init__(self, app_instance, plugin_manager):
        self.app = app_instance
        self.plugin_manager = plugin_manager
        self._services = {}
        
    def get_app_data(self, key: str) -> Any:
        """获取应用数据"""
        return getattr(self.app, key, None)
        
    def set_app_data(self, key: str, value: Any):
        """设置应用数据"""
        setattr(self.app, key, value)
        
    def call_plugin_service(self, plugin_name: str, service_name: str, *args, **kwargs) -> Any:
        """调用其他插件的服务"""
        return self.plugin_manager.call_plugin_service(plugin_name, service_name, *args, **kwargs)
        
    def emit_event(self, event_name: str, data: Any = None):
        """发送事件"""
        self.plugin_manager.emit_event(event_name, data)
        
    def show_message(self, message: str, title: str = "插件消息"):
        """显示消息"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)


class NovelGeneratorPlugin(ABC):
    """
    小说生成器插件基类
    所有插件都必须继承此类并实现必要的方法
    """
    
    def __init__(self):
        self.metadata: Optional[PluginMetadata] = None
        self.context: Optional[PluginContext] = None
        self.state = PluginState.DISCOVERED
        self._services = {}
        self._ui_components = {}
        self._settings = {}
        
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        pass
        
    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """
        初始化插件
        Args:
            context: 插件上下文
        Returns:
            bool: 初始化是否成功
        """
        pass
        
    def cleanup(self):
        """清理插件资源"""
        pass
        
    def get_services(self) -> Dict[str, callable]:
        """返回插件提供的服务"""
        return self._services
        
    def get_ui_components(self) -> Dict[str, Any]:
        """返回插件的UI组件"""
        return self._ui_components
        
    def on_event(self, event_name: str, data: Any = None):
        """处理事件"""
        pass
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """返回插件设置的JSON Schema"""
        return {}
        
    def get_settings(self) -> Dict[str, Any]:
        """获取插件设置"""
        return self._settings.copy()
        
    def update_settings(self, settings: Dict[str, Any]):
        """更新插件设置"""
        self._settings.update(settings)
        
    def on_generation_start(self, generation_type: str, params: Dict[str, Any]):
        """生成开始时的回调"""
        pass
        
    def on_generation_complete(self, generation_type: str, result: Any):
        """生成完成时的回调"""
        pass
        
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """处理文本内容"""
        return text
        
    def export_data(self, data: Any, format_type: str) -> bytes:
        """导出数据"""
        return b""
        
    def get_menu_items(self) -> List[Dict[str, Any]]:
        """返回插件的菜单项"""
        return []


# 为了向后兼容，添加BasePlugin别名
BasePlugin = NovelGeneratorPlugin