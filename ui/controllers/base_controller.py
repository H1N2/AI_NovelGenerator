"""
基础控制器类
定义MVP架构中Presenter层的基础接口和通用功能
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List
import logging
import asyncio
from enum import Enum
from dataclasses import dataclass


class ControllerState(Enum):
    """控制器状态枚举"""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class ControllerEvent:
    """控制器事件数据类"""
    event_type: str
    source: str
    data: Any = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class BaseController(ABC):
    """
    基础控制器类
    所有具体控制器都应继承此类
    """
    
    def __init__(self, name: str):
        self.name = name
        self.state = ControllerState.IDLE
        self.logger = logging.getLogger(f"Controller.{name}")
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._error_handlers: List[Callable] = []
        self._model = None
        self._view = None
    
    def set_model(self, model):
        """设置Model"""
        self._model = model
        self.on_model_set(model)
    
    def set_view(self, view):
        """设置View"""
        self._view = view
        self.on_view_set(view)
    
    @property
    def model(self):
        """获取Model"""
        return self._model
    
    @property
    def view(self):
        """获取View"""
        return self._view
    
    def on_model_set(self, model):
        """Model设置完成后的回调"""
        pass
    
    def on_view_set(self, view):
        """View设置完成后的回调"""
        pass
    

    
    def remove_event_listener(self, event_type: str, handler: callable) -> None:
        """移除事件监听器"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                if not self._event_handlers[event_type]:
                    del self._event_handlers[event_type]
            except ValueError:
                pass
    
    def add_event_handler(self, event_type: str, handler: callable) -> None:
        """添加事件处理器（别名方法）"""
        self.add_event_listener(event_type, handler)
    
    def add_event_listener(self, event_type: str, handler: callable) -> None:
        """添加事件监听器"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def emit_event(self, event: ControllerEvent):
        """发出事件"""
        handlers = self._event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")
                self._handle_error(e, f"Event handler for {event.event_type}")
    
    def add_error_handler(self, handler: Callable):
        """添加错误处理器"""
        self._error_handlers.append(handler)
    
    def _handle_error(self, error: Exception, context: str = ""):
        """处理错误"""
        self.state = ControllerState.ERROR
        self.logger.error(f"Error in {context}: {error}")
        
        # 调用错误处理器
        for handler in self._error_handlers:
            try:
                handler(error, context)
            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
        
        # 通知View显示错误
        if self._view and hasattr(self._view, 'show_error'):
            try:
                self._view.show_error(f"{context}: {str(error)}")
            except Exception as e:
                self.logger.error(f"Failed to show error in view: {e}")
    
    def set_state(self, state: ControllerState, data: Any = None):
        """设置控制器状态"""
        old_state = self.state
        self.state = state
        
        # 发出状态变化事件
        event = ControllerEvent(
            event_type="state_changed",
            source=self.name,
            data={
                'old_state': old_state,
                'new_state': state,
                'data': data
            }
        )
        self.emit_event(event)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化控制器"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """清理资源"""
        pass
    
    def validate_dependencies(self) -> bool:
        """验证依赖项"""
        if self._model is None:
            self.logger.error("Model not set")
            return False
        if self._view is None:
            self.logger.error("View not set")
            return False
        return True


class ControllerRegistry:
    """
    控制器注册中心
    管理所有控制器的生命周期
    """
    
    def __init__(self):
        self._controllers: Dict[str, BaseController] = {}
        self.logger = logging.getLogger("ControllerRegistry")
    
    def register(self, controller: BaseController):
        """注册控制器"""
        if controller.name in self._controllers:
            self.logger.warning(f"Controller {controller.name} already registered, replacing")
        
        self._controllers[controller.name] = controller
        self.logger.info(f"Controller {controller.name} registered")
    
    def unregister(self, name: str) -> bool:
        """注销控制器"""
        if name in self._controllers:
            controller = self._controllers[name]
            # 同步清理，避免事件循环问题
            try:
                import asyncio
                if asyncio.iscoroutinefunction(controller.cleanup):
                    # 如果在事件循环中，直接调用
                    try:
                        loop = asyncio.get_running_loop()
                        asyncio.create_task(controller.cleanup())
                    except RuntimeError:
                        # 如果没有运行的事件循环，创建新的
                        asyncio.run(controller.cleanup())
                else:
                    controller.cleanup()
            except Exception as e:
                print(f"清理控制器时出错: {e}")
            
            del self._controllers[name]
            return True
        return False
    
    def get(self, name: str) -> Optional[BaseController]:
        """获取控制器"""
        return self._controllers.get(name)
    
    def get_all(self) -> Dict[str, BaseController]:
        """获取所有控制器"""
        return self._controllers.copy()
    
    async def initialize_all(self) -> bool:
        """初始化所有控制器"""
        success = True
        for name, controller in self._controllers.items():
            try:
                if not await controller.initialize():
                    self.logger.error(f"Failed to initialize controller {name}")
                    success = False
            except Exception as e:
                self.logger.error(f"Exception during initialization of {name}: {e}")
                success = False
        
        return success
    
    async def cleanup_all(self):
        """清理所有控制器"""
        for name, controller in self._controllers.items():
            try:
                await controller.cleanup()
            except Exception as e:
                self.logger.error(f"Exception during cleanup of {name}: {e}")


# 全局控制器注册中心实例
controller_registry = ControllerRegistry()