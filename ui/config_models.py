"""
配置管理模型
负责所有配置相关的数据管理和状态维护
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .mvp_base import BaseModel


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 8192
    timeout: int = 600
    interface_format: str = "OpenAI"
    updated_at: Optional[str] = None  # 添加updated_at字段以兼容配置文件
    id: Optional[str] = None  # 添加id字段以兼容配置文件
    created_at: Optional[str] = None  # 添加created_at字段以兼容配置文件


@dataclass
class EmbeddingConfig:
    """Embedding配置数据类"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model_name: str = "text-embedding-ada-002"
    retrieval_k: int = 4
    interface_format: str = "OpenAI"
    id: Optional[str] = None  # 添加id字段以兼容配置文件
    created_at: Optional[str] = None  # 添加created_at字段以兼容配置文件


@dataclass
class NovelParams:
    """小说参数数据类"""
    topic: str = ""
    genre: str = "玄幻"
    num_chapters: int = 10
    word_number: int = 3000
    filepath: str = ""
    chapter_num: int = 1
    characters_involved: str = ""
    key_items: str = ""
    scene_location: str = ""
    time_constraint: str = ""
    user_guidance: str = ""
    webdav_url: str = ""
    webdav_username: str = ""
    webdav_password: str = ""


@dataclass
class ProxySettings:
    """代理设置数据类"""
    enabled: bool = False
    proxy_url: str = ""
    proxy_port: str = ""


@dataclass
class ChooseConfigs:
    """选择配置数据类"""
    architecture_llm: str = "DeepSeek"
    chapter_outline_llm: str = "DeepSeek"
    final_chapter_llm: str = "DeepSeek"
    consistency_review_llm: str = "DeepSeek"
    prompt_draft_llm: str = "DeepSeek"


class ConfigurationManager(BaseModel):
    """
    配置管理器
    负责统一管理所有配置数据和状态
    """
    
    def __init__(self, config_file: str = "config.json"):
        super().__init__()
        self.config_file = config_file
        self._llm_configs: Dict[str, LLMConfig] = {}
        self._embedding_configs: Dict[str, EmbeddingConfig] = {}
        self._novel_params = NovelParams()
        self._proxy_settings = ProxySettings()
        self._choose_configs = ChooseConfigs()
        self._current_llm_config = ""
        self._current_embedding_interface = "OpenAI"
        
        # 加载配置
        self.load_configuration()
    
    def load_configuration(self) -> bool:
        """加载配置文件"""
        from config_manager import load_config
        
        try:
            loaded_config = load_config(self.config_file)
            if not loaded_config:
                self._initialize_default_config()
                self.notify_observers("config_loaded", self._get_current_config())
                return True
            
            # 解析LLM配置
            if "llm_configs" in loaded_config:
                for name, config in loaded_config["llm_configs"].items():
                    self._llm_configs[name] = LLMConfig(**config)
                
                # 设置当前LLM配置
                if self._llm_configs:
                    self._current_llm_config = next(iter(self._llm_configs.keys()))
            
            # 解析Embedding配置
            if "embedding_configs" in loaded_config:
                for interface, config in loaded_config["embedding_configs"].items():
                    self._embedding_configs[interface] = EmbeddingConfig(**config)
            
            # 解析小说参数
            if "other_params" in loaded_config:
                params = loaded_config["other_params"]
                self._novel_params = NovelParams(
                    topic=params.get("topic", ""),
                    genre=params.get("genre", "玄幻"),
                    num_chapters=params.get("num_chapters", 10),
                    word_number=params.get("word_number", 3000),
                    filepath=params.get("filepath", ""),
                    chapter_num=params.get("chapter_num", 1),
                    characters_involved=params.get("characters_involved", ""),
                    key_items=params.get("key_items", ""),
                    scene_location=params.get("scene_location", ""),
                    time_constraint=params.get("time_constraint", ""),
                    user_guidance=params.get("user_guidance", ""),
                    webdav_url=params.get("webdav_url", ""),
                    webdav_username=params.get("webdav_username", ""),
                    webdav_password=params.get("webdav_password", "")
                )
            
            # 解析代理设置
            if "proxy_setting" in loaded_config:
                proxy = loaded_config["proxy_setting"]
                self._proxy_settings = ProxySettings(
                    enabled=proxy.get("enabled", False),
                    proxy_url=proxy.get("proxy_url", ""),
                    proxy_port=proxy.get("proxy_port", "")
                )
                self._apply_proxy_settings()
            
            # 解析选择配置
            if "choose_configs" in loaded_config:
                choose = loaded_config["choose_configs"]
                self._choose_configs = ChooseConfigs(
                    architecture_llm=choose.get("architecture_llm", "DeepSeek"),
                    chapter_outline_llm=choose.get("chapter_outline_llm", "DeepSeek"),
                    final_chapter_llm=choose.get("final_chapter_llm", "DeepSeek"),
                    consistency_review_llm=choose.get("consistency_review_llm", "DeepSeek"),
                    prompt_draft_llm=choose.get("prompt_draft_llm", "DeepSeek")
                )
            
            # 获取当前Embedding接口
            self._current_embedding_interface = loaded_config.get("last_embedding_interface_format", "OpenAI")
            
            self.notify_observers("config_loaded", self._get_current_config())
            return True
            
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            self._initialize_default_config()
            self.notify_observers("config_load_error", str(e))
            return False
    
    def save_configuration(self) -> bool:
        """保存配置文件"""
        from config_manager import save_config
        
        try:
            config_data = self._get_current_config()
            success = save_config(self.config_file, config_data)
            
            if success:
                self.notify_observers("config_saved", config_data)
            else:
                self.notify_observers("config_save_failed", None)
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            self.notify_observers("config_save_error", str(e))
            return False
    
    def _initialize_default_config(self):
        """初始化默认配置"""
        # 默认LLM配置
        self._llm_configs["DeepSeek"] = LLMConfig()
        self._current_llm_config = "DeepSeek"
        
        # 默认Embedding配置
        self._embedding_configs["OpenAI"] = EmbeddingConfig()
        self._current_embedding_interface = "OpenAI"
        
        # 其他默认值已在dataclass中定义
    
    def _get_current_config(self) -> Dict[str, Any]:
        """获取当前完整配置"""
        return {
            "llm_configs": {
                name: {
                    "api_key": config.api_key,
                    "base_url": config.base_url,
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "timeout": config.timeout,
                    "interface_format": config.interface_format
                }
                for name, config in self._llm_configs.items()
            },
            "embedding_configs": {
                interface: {
                    "api_key": config.api_key,
                    "base_url": config.base_url,
                    "model_name": config.model_name,
                    "retrieval_k": config.retrieval_k
                }
                for interface, config in self._embedding_configs.items()
            },
            "other_params": {
                "topic": self._novel_params.topic,
                "genre": self._novel_params.genre,
                "num_chapters": self._novel_params.num_chapters,
                "word_number": self._novel_params.word_number,
                "filepath": self._novel_params.filepath,
                "chapter_num": self._novel_params.chapter_num,
                "characters_involved": self._novel_params.characters_involved,
                "key_items": self._novel_params.key_items,
                "scene_location": self._novel_params.scene_location,
                "time_constraint": self._novel_params.time_constraint,
                "user_guidance": self._novel_params.user_guidance,
                "webdav_url": self._novel_params.webdav_url,
                "webdav_username": self._novel_params.webdav_username,
                "webdav_password": self._novel_params.webdav_password
            },
            "proxy_setting": {
                "enabled": self._proxy_settings.enabled,
                "proxy_url": self._proxy_settings.proxy_url,
                "proxy_port": self._proxy_settings.proxy_port
            },
            "choose_configs": {
                "architecture_llm": self._choose_configs.architecture_llm,
                "chapter_outline_llm": self._choose_configs.chapter_outline_llm,
                "final_chapter_llm": self._choose_configs.final_chapter_llm,
                "consistency_review_llm": self._choose_configs.consistency_review_llm,
                "prompt_draft_llm": self._choose_configs.prompt_draft_llm
            },
            "last_embedding_interface_format": self._current_embedding_interface
        }
    
    def _apply_proxy_settings(self):
        """应用代理设置"""
        if self._proxy_settings.enabled:
            proxy_url = f"http://{self._proxy_settings.proxy_url}:{self._proxy_settings.proxy_port}"
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
        else:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
    
    # 属性访问器
    @property
    def current_llm_config(self) -> LLMConfig:
        """获取当前LLM配置"""
        if self._current_llm_config in self._llm_configs:
            return self._llm_configs[self._current_llm_config]
        return LLMConfig()
    
    @property
    def current_embedding_config(self) -> EmbeddingConfig:
        """获取当前Embedding配置"""
        if self._current_embedding_interface in self._embedding_configs:
            return self._embedding_configs[self._current_embedding_interface]
        return EmbeddingConfig()
    
    @property
    def novel_params(self) -> NovelParams:
        """获取小说参数"""
        return self._novel_params
    
    @property
    def proxy_settings(self) -> ProxySettings:
        """获取代理设置"""
        return self._proxy_settings
    
    @property
    def choose_configs(self) -> ChooseConfigs:
        """获取选择配置"""
        return self._choose_configs
    
    @property
    def llm_config_names(self) -> list:
        """获取所有LLM配置名称"""
        return list(self._llm_configs.keys())
    
    @property
    def embedding_interfaces(self) -> list:
        """获取所有Embedding接口"""
        return list(self._embedding_configs.keys())
    
    # 配置更新方法
    def update_llm_config(self, config_name: str, config: LLMConfig):
        """更新LLM配置"""
        self._llm_configs[config_name] = config
        self.notify_observers("llm_config_updated", {"name": config_name, "config": config})
    
    def update_embedding_config(self, interface: str, config: EmbeddingConfig):
        """更新Embedding配置"""
        self._embedding_configs[interface] = config
        self.notify_observers("embedding_config_updated", {"interface": interface, "config": config})
    
    def update_novel_params(self, params: NovelParams):
        """更新小说参数"""
        self._novel_params = params
        self.notify_observers("novel_params_updated", params)
    
    def update_proxy_settings(self, settings: ProxySettings):
        """更新代理设置"""
        self._proxy_settings = settings
        self._apply_proxy_settings()
        self.notify_observers("proxy_settings_updated", settings)
    
    def update_choose_configs(self, configs: ChooseConfigs):
        """更新选择配置"""
        self._choose_configs = configs
        self.notify_observers("choose_configs_updated", configs)
    
    def set_current_llm_config(self, config_name: str):
        """设置当前LLM配置"""
        if config_name in self._llm_configs:
            self._current_llm_config = config_name
            self.notify_observers("current_llm_config_changed", config_name)
    
    def set_current_embedding_interface(self, interface: str):
        """设置当前Embedding接口"""
        if interface in self._embedding_configs:
            self._current_embedding_interface = interface
            self.notify_observers("current_embedding_interface_changed", interface)