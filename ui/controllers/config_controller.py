"""
配置控制器
负责处理所有配置相关的业务逻辑，包括LLM配置、嵌入模型配置等
"""
import asyncio
from typing import Dict, Any, Optional
from .base_controller import BaseController, ControllerState, ControllerEvent
from config_manager import test_llm_config, test_embedding_config


class ConfigController(BaseController):
    """
    配置控制器
    处理配置的加载、保存、验证等操作
    """
    
    def __init__(self):
        super().__init__("ConfigController")
        self._current_llm_config = None
        self._current_embedding_config = None
        self._config_cache = {}
    
    async def initialize(self) -> bool:
        """初始化配置控制器"""
        try:
            if not self.validate_dependencies():
                return False
            
            # 加载配置
            await self.load_configuration()
            
            self.set_state(ControllerState.IDLE)
            return True
            
        except Exception as e:
            self._handle_error(e, "配置控制器初始化")
            return False
    
    async def cleanup(self):
        """清理资源"""
        self._config_cache.clear()
        self.logger.info("配置控制器已清理")
    
    async def load_configuration(self) -> bool:
        """加载配置文件"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 从Model加载配置
            if hasattr(self.model, 'load_config'):
                config_data = await asyncio.to_thread(self.model.load_config)
                
                if config_data:
                    self._config_cache = config_data
                    self._extract_current_configs(config_data)
                    
                    # 通知View更新
                    if hasattr(self.view, 'update_config_display'):
                        self.view.update_config_display(config_data)
                    
                    # 发出配置加载完成事件
                    event = ControllerEvent(
                        event_type="config_loaded",
                        source=self.name,
                        data=config_data
                    )
                    self.emit_event(event)
                    
                    self.set_state(ControllerState.COMPLETED)
                    return True
                else:
                    self.logger.warning("配置文件为空或不存在")
                    self.set_state(ControllerState.IDLE)
                    return False
            else:
                self.logger.error("Model不支持配置加载")
                return False
                
        except Exception as e:
            self._handle_error(e, "加载配置")
            return False
    
    async def save_configuration(self, config_data: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 验证配置数据
            if not self._validate_config_data(config_data):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 保存到Model
            if hasattr(self.model, 'save_config'):
                success = await asyncio.to_thread(self.model.save_config, config_data)
                
                if success:
                    self._config_cache = config_data
                    self._extract_current_configs(config_data)
                    
                    # 通知View更新
                    if hasattr(self.view, 'show_success'):
                        self.view.show_success("**配置保存成功**")
                    
                    # 发出配置保存完成事件
                    event = ControllerEvent(
                        event_type="config_saved",
                        source=self.name,
                        data=config_data
                    )
                    self.emit_event(event)
                    
                    self.set_state(ControllerState.COMPLETED)
                    return True
                else:
                    if hasattr(self.view, 'show_error'):
                        self.view.show_error("**配置保存失败**")
                    self.set_state(ControllerState.ERROR)
                    return False
            else:
                self.logger.error("Model不支持配置保存")
                return False
                
        except Exception as e:
            self._handle_error(e, "保存配置")
            return False
    
    async def test_llm_configuration(self, config_name: str = None) -> bool:
        """测试LLM配置"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 获取要测试的配置
            if config_name:
                llm_config = self._get_llm_config_by_name(config_name)
            else:
                llm_config = self._current_llm_config
            
            if not llm_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到LLM配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 执行测试
            success = await asyncio.to_thread(test_llm_config, llm_config)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success("**LLM配置测试成功**")
                
                # 发出测试成功事件
                event = ControllerEvent(
                    event_type="llm_test_success",
                    source=self.name,
                    data=llm_config
                )
                self.emit_event(event)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**LLM配置测试失败**")
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "测试LLM配置")
            return False
    
    async def test_embedding_configuration(self, interface_format: str = "OpenAI") -> bool:
        """测试嵌入模型配置"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 获取嵌入模型配置
            embedding_config = self._get_embedding_config_by_format(interface_format)
            
            if not embedding_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到嵌入模型配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 执行测试
            success = await asyncio.to_thread(test_embedding_config, embedding_config)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success("**嵌入模型配置测试成功**")
                
                # 发出测试成功事件
                event = ControllerEvent(
                    event_type="embedding_test_success",
                    source=self.name,
                    data=embedding_config
                )
                self.emit_event(event)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**嵌入模型配置测试失败**")
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "测试嵌入模型配置")
            return False
    
    def get_current_llm_config(self) -> Optional[Dict[str, Any]]:
        """获取当前LLM配置"""
        return self._current_llm_config
    
    def get_current_embedding_config(self) -> Optional[Dict[str, Any]]:
        """获取当前嵌入模型配置"""
        return self._current_embedding_config
    
    async def add_llm_config(self, name: str, config: dict) -> bool:
        """添加LLM配置"""
        try:
            if not self._validate_llm_config(config):
                self.handle_error(ValueError("无效的LLM配置"), "配置验证失败")
                return False
            
            llm_configs = self._config_cache.get("llm_configs", {})
            llm_configs[name] = config
            self._config_cache["llm_configs"] = llm_configs
            
            event = ControllerEvent(
                event_type="llm_config_added",
                source=self.name,
                data={"name": name, "config": config}
            )
            self.emit_event(event)
            return True
            
        except Exception as e:
            self._handle_error(e, "添加LLM配置失败")
            return False
    
    async def remove_llm_config(self, name: str) -> bool:
        """移除LLM配置"""
        try:
            llm_configs = self._config_cache.get("llm_configs", {})
            if name in llm_configs:
                del llm_configs[name]
                event = ControllerEvent(
                    event_type="llm_config_removed",
                    source=self.name,
                    data={"name": name}
                )
                self.emit_event(event)
                return True
            return False
            
        except Exception as e:
            self._handle_error(e, "移除LLM配置失败")
            return False
    
    def _validate_llm_config(self, config: dict) -> bool:
        """验证LLM配置的有效性"""
        required_fields = ["api_key", "base_url", "model_name"]
        return all(field in config and config[field] for field in required_fields)
    
    def get_all_llm_configs(self) -> Dict[str, Any]:
        """获取所有LLM配置"""
        return self._config_cache.get("llm_configs", {})
    
    def get_all_embedding_configs(self) -> Dict[str, Any]:
        """获取所有嵌入模型配置"""
        return self._config_cache.get("embedding_configs", {})
    
    def _extract_current_configs(self, config_data: Dict[str, Any]):
        """从配置数据中提取当前配置"""
        # 提取LLM配置
        llm_configs = config_data.get("llm_configs", {})
        if llm_configs:
            # 获取第一个LLM配置作为当前配置
            self._current_llm_config = next(iter(llm_configs.values()))
        
        # 提取嵌入模型配置
        embedding_configs = config_data.get("embedding_configs", {})
        last_embedding_format = config_data.get("last_embedding_interface_format", "OpenAI")
        if last_embedding_format in embedding_configs:
            self._current_embedding_config = embedding_configs[last_embedding_format]
        elif embedding_configs:
            self._current_embedding_config = next(iter(embedding_configs.values()))
    
    def _get_llm_config_by_name(self, config_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取LLM配置"""
        llm_configs = self._config_cache.get("llm_configs", {})
        return llm_configs.get(config_name)
    
    def _get_embedding_config_by_format(self, interface_format: str) -> Optional[Dict[str, Any]]:
        """根据接口格式获取嵌入模型配置"""
        embedding_configs = self._config_cache.get("embedding_configs", {})
        return embedding_configs.get(interface_format)
    
    def _validate_config_data(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据的有效性"""
        try:
            # 验证必要的字段
            required_fields = ["llm_configs", "embedding_configs"]
            for field in required_fields:
                if field not in config_data:
                    self.logger.error(f"配置数据缺少必要字段: {field}")
                    return False
            
            # 验证LLM配置
            llm_configs = config_data["llm_configs"]
            if not isinstance(llm_configs, dict) or not llm_configs:
                self.logger.error("LLM配置格式错误或为空")
                return False
            
            # 验证嵌入模型配置
            embedding_configs = config_data["embedding_configs"]
            if not isinstance(embedding_configs, dict) or not embedding_configs:
                self.logger.error("嵌入模型配置格式错误或为空")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置数据验证失败: {e}")
            return False