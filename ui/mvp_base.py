"""
MVP架构基础类
提供Model-View-Presenter模式的基础框架，确保UI重构的安全性和可维护性
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable
import logging


class BaseModel(ABC):
    """
    Model基类：负责数据管理和业务逻辑
    """
    def __init__(self):
        self._observers = []
        self._data = {}
    
    def add_observer(self, observer: Callable):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: Callable):
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: Any = None):
        """通知所有观察者"""
        for observer in self._observers:
            try:
                observer(event, data)
            except Exception as e:
                logging.error(f"Observer notification failed: {e}")
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self._data.get(key, default)
    
    def set_data(self, key: str, value: Any, notify: bool = True):
        """设置数据"""
        old_value = self._data.get(key)
        self._data[key] = value
        
        if notify and old_value != value:
            self.notify_observers(f"data_changed_{key}", {
                'key': key,
                'old_value': old_value,
                'new_value': value
            })


class BaseView(ABC):
    """
    View基类：负责UI显示和用户交互
    """
    def __init__(self):
        self._presenter = None
    
    def set_presenter(self, presenter: 'BasePresenter'):
        """设置Presenter"""
        self._presenter = presenter
    
    @abstractmethod
    def update_view(self, data: Dict[str, Any]):
        """更新视图显示"""
        pass
    
    @abstractmethod
    def show_error(self, message: str):
        """显示错误信息"""
        pass
    
    @abstractmethod
    def show_success(self, message: str):
        """显示成功信息"""
        pass


class BasePresenter(ABC):
    """
    Presenter基类：负责协调Model和View
    """
    def __init__(self, model: BaseModel, view: BaseView):
        self._model = model
        self._view = view
        
        # 建立双向绑定
        self._view.set_presenter(self)
        self._model.add_observer(self._on_model_changed)
    
    def _on_model_changed(self, event: str, data: Any):
        """处理Model变化"""
        try:
            self.handle_model_change(event, data)
        except Exception as e:
            logging.error(f"Presenter handle model change failed: {e}")
            self._view.show_error(f"处理数据变化时出错: {str(e)}")
    
    @abstractmethod
    def handle_model_change(self, event: str, data: Any):
        """处理Model变化的具体逻辑"""
        pass
    
    @property
    def model(self) -> BaseModel:
        """获取Model"""
        return self._model
    
    @property
    def view(self) -> BaseView:
        """获取View"""
        return self._view


class ConfigurationModel(BaseModel):
    """
    配置管理Model
    负责所有配置相关的数据管理
    """
    def __init__(self):
        super().__init__()
        self._config_file = "config.json"
        self._loaded_config = None
    
    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        from config_manager import load_config
        
        if config_file:
            self._config_file = config_file
        
        try:
            self._loaded_config = load_config(self._config_file)
            if self._loaded_config:
                # 将配置数据存储到内部数据结构
                for key, value in self._loaded_config.items():
                    self.set_data(key, value, notify=False)
                
                self.notify_observers("config_loaded", self._loaded_config)
                return self._loaded_config
            else:
                self.notify_observers("config_load_failed", None)
                return {}
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            self.notify_observers("config_load_error", str(e))
            return {}
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """保存配置文件"""
        from config_manager import save_config
        
        try:
            success = save_config(self._config_file, config_data)
            if success:
                self._loaded_config = config_data
                # 更新内部数据
                for key, value in config_data.items():
                    self.set_data(key, value, notify=False)
                
                self.notify_observers("config_saved", config_data)
            else:
                self.notify_observers("config_save_failed", None)
            
            return success
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            self.notify_observers("config_save_error", str(e))
            return False
    
    def get_llm_config(self, config_name: str = None) -> Dict[str, Any]:
        """获取LLM配置"""
        llm_configs = self.get_data("llm_configs", {})
        if not llm_configs:
            return self._get_default_llm_config()
        
        if config_name and config_name in llm_configs:
            return llm_configs[config_name]
        
        # 返回第一个配置
        return next(iter(llm_configs.values())) if llm_configs else self._get_default_llm_config()
    
    def get_embedding_config(self, interface_format: str = "OpenAI") -> Dict[str, Any]:
        """获取Embedding配置"""
        embedding_configs = self.get_data("embedding_configs", {})
        if interface_format in embedding_configs:
            return embedding_configs[interface_format]
        
        return self._get_default_embedding_config()
    
    def _get_default_llm_config(self) -> Dict[str, Any]:
        """获取默认LLM配置"""
        return {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        }
    
    def _get_default_embedding_config(self) -> Dict[str, Any]:
        """获取默认Embedding配置"""
        return {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "text-embedding-ada-002",
            "retrieval_k": 4
        }