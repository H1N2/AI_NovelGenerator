"""
配置控制器
负责处理所有配置相关的业务逻辑，包括LLM配置、嵌入模型配置等
"""
import asyncio
from typing import Dict, Any, Optional, List
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
            self.set_state(ControllerState.PROCESSING)
            
            # 验证Model依赖项（View可选）
            if self._model is None:
                self.logger.error("Model not set")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 加载配置
            success = await self.load_configuration()
            
            if success:
                self.set_state(ControllerState.COMPLETED)
                self.logger.info("配置控制器初始化完成")
                return True
            else:
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "初始化配置控制器")
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
            if hasattr(self.model, 'load_configuration'):
                # ConfigurationManager的方法是load_configuration，不是load_config
                success = await asyncio.to_thread(self.model.load_configuration)
                
                if success:
                    # 获取配置数据
                    config_data = await asyncio.to_thread(self.model._get_current_config)
                    
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
                        self.logger.warning("配置数据获取失败")
                        self.set_state(ControllerState.IDLE)
                        return False
                else:
                    self.logger.warning("配置文件加载失败")
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
                error_msg = "**未找到LLM配置**"
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(error_msg)
                self.logger.error(error_msg)
                self.set_state(ControllerState.ERROR)
                return False
            
            # 检查必要的配置参数
            api_key = llm_config.get("api_key", "").strip()
            if not api_key:
                error_msg = "**API Key未配置** - 请在配置中填入有效的API Key"
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(error_msg)
                self.logger.error(error_msg)
                self.set_state(ControllerState.ERROR)
                return False
            
            base_url = llm_config.get("base_url", "").strip()
            if not base_url:
                error_msg = "**Base URL未配置** - 请在配置中填入有效的API地址"
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(error_msg)
                self.logger.error(error_msg)
                self.set_state(ControllerState.ERROR)
                return False
            
            model_name = llm_config.get("model_name", "").strip()
            if not model_name:
                error_msg = "**模型名称未配置** - 请在配置中填入有效的模型名称"
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(error_msg)
                self.logger.error(error_msg)
                self.set_state(ControllerState.ERROR)
                return False
            
            # 执行测试 - 需要传递正确的参数
            success = await asyncio.to_thread(
                test_llm_config,
                interface_format=llm_config.get("interface_format"),
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 8192),
                timeout=llm_config.get("timeout", 600),
                log_func=self.view.safe_log if hasattr(self.view, 'safe_log') else print,
                handle_exception_func=self.view.handle_exception if hasattr(self.view, 'handle_exception') else lambda x: None
            )
            
            if success:
                success_msg = "**LLM配置测试成功** ✅"
                if hasattr(self.view, 'show_success'):
                    self.view.show_success(success_msg)
                self.logger.info(success_msg)
                
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
                error_msg = "**LLM配置测试失败** ❌ - 请检查网络连接和配置参数"
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(error_msg)
                self.logger.error(error_msg)
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            # 根据异常类型提供更具体的错误信息
            error_str = str(e)
            
            if "api_key" in error_str.lower():
                friendly_msg = "**API Key错误** - 请检查API Key是否正确配置"
            elif "connection" in error_str.lower() or "timeout" in error_str.lower():
                friendly_msg = "**网络连接错误** - 请检查网络连接和Base URL是否正确"
            elif "unauthorized" in error_str.lower() or "401" in error_str:
                friendly_msg = "**认证失败** - 请检查API Key是否有效"
            elif "not found" in error_str.lower() or "404" in error_str:
                friendly_msg = "**API地址错误** - 请检查Base URL是否正确"
            elif "model" in error_str.lower():
                friendly_msg = "**模型错误** - 请检查模型名称是否正确"
            else:
                friendly_msg = f"**LLM配置测试异常** - {error_str}"
            
            if hasattr(self.view, 'show_error'):
                self.view.show_error(friendly_msg)
            
            self.logger.error(f"测试LLM配置异常: {error_str}")
            self.set_state(ControllerState.ERROR)
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
            
            # 执行测试 - 需要传递正确的参数
            success = await asyncio.to_thread(
                test_embedding_config,
                api_key=embedding_config.get("api_key"),
                base_url=embedding_config.get("base_url"),
                interface_format=embedding_config.get("interface_format"),
                model_name=embedding_config.get("model_name"),
                log_func=self.view.safe_log if hasattr(self.view, 'safe_log') else print,
                handle_exception_func=self.view.handle_exception if hasattr(self.view, 'handle_exception') else lambda x: None
            )
            
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

    def get_llm_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """获取指定名称的LLM配置"""
        return self._get_llm_config_by_name(config_name)

    def set_current_llm_config(self, config_name: str) -> bool:
        """设置当前LLM配置"""
        try:
            # **验证配置是否存在**
            config = self._get_llm_config_by_name(config_name)
            if not config:
                self.logger.warning(f"LLM配置 '{config_name}' 不存在")
                return False
            
            # **更新当前配置**
            self._current_llm_config = config
            self._current_llm_config_name = config_name
            
            # **发出配置变更事件**
            event = ControllerEvent(
                event_type="llm_config_changed",
                source=self.name,
                data={
                    "config_name": config_name,
                    "config": config
                }
            )
            self.emit_event(event)
            
            self.logger.info(f"当前LLM配置已设置为: {config_name}")
            return True
            
        except Exception as e:
            self._handle_error(e, f"设置当前LLM配置失败: {config_name}")
            return False

    def add_llm_config(self, name: str, config: dict) -> bool:
        """添加LLM配置"""
        try:
            if not self._validate_llm_config(config):
                self.handle_error(ValueError("无效的LLM配置"), "配置验证失败")
                return False
            
            # 检查配置是否已存在
            llm_configs = self._config_cache.get("llm_configs", {})
            if name in llm_configs:
                self.logger.warning(f"LLM配置 '{name}' 已存在")
                return False
            
            llm_configs[name] = config
            self._config_cache["llm_configs"] = llm_configs
            
            # 同步到Model层（如果可用）
            if hasattr(self, 'model') and self.model and hasattr(self.model, 'add_llm_config'):
                self.model.add_llm_config(name, config)
            
            event = ControllerEvent(
                event_type="llm_config_added",
                source=self.name,
                data={"name": name, "config": config}
            )
            self.emit_event(event)
            self.logger.info(f"LLM配置已添加: {name}")
            return True
            
        except Exception as e:
            self._handle_error(e, "添加LLM配置失败")
            return False
    
    def remove_llm_config(self, name: str) -> bool:
        """移除LLM配置"""
        try:
            llm_configs = self._config_cache.get("llm_configs", {})
            if name in llm_configs:
                del llm_configs[name]
                
                # 同步到Model层（如果可用）
                if hasattr(self, 'model') and self.model and hasattr(self.model, 'remove_llm_config'):
                    self.model.remove_llm_config(name)
                
                event = ControllerEvent(
                    event_type="llm_config_removed",
                    source=self.name,
                    data={"name": name}
                )
                self.emit_event(event)
                self.logger.info(f"LLM配置已移除: {name}")
                return True
            return False
            
        except Exception as e:
            self._handle_error(e, "移除LLM配置失败")
            return False
    
    def update_llm_config(self, config_name: str, config_data: dict) -> bool:
        """
        更新LLM配置
        
        Args:
            config_name: 配置名称
            config_data: 配置数据字典
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证配置数据
            if not self._validate_llm_config(config_data):
                self.logger.error(f"无效的LLM配置数据: {config_name}")
                return False
            
            # 更新缓存中的配置
            if "llm_configs" not in self._config_cache:
                self._config_cache["llm_configs"] = {}
            
            self._config_cache["llm_configs"][config_name] = config_data
            
            # 如果有Model层，同步更新
            self.logger.debug(f"检查model是否存在update_llm_config方法: model={self.model}, type={type(self.model)}")
            self.logger.debug(f"hasattr(self.model, 'update_llm_config'): {hasattr(self.model, 'update_llm_config') if self.model else 'model is None'}")
            
            if hasattr(self.model, 'update_llm_config'):
                self.logger.debug(f"进入model同步更新分支，配置名称: {config_name}")
                from ui.config_models import LLMConfig
                llm_config = LLMConfig(**config_data)
                self.logger.debug(f"创建LLMConfig对象: {llm_config}")
                self.model.update_llm_config(config_name, llm_config)
                self.logger.debug(f"model.update_llm_config调用完成")
            else:
                self.logger.warning(f"跳过model同步更新: model={self.model}, hasattr结果={hasattr(self.model, 'update_llm_config') if self.model else 'model is None'}")
            
            # 自动保存配置到文件
            try:
                if hasattr(self.model, 'save_configuration'):
                    save_success = self.model.save_configuration()
                    if save_success:
                        self.logger.info(f"LLM配置已保存到文件: {config_name}")
                    else:
                        self.logger.warning(f"LLM配置保存到文件失败: {config_name}")
                else:
                    self.logger.warning("Model层不支持save_configuration方法")
            except Exception as save_error:
                self.logger.error(f"保存配置文件时出错: {save_error}")
            
            # 发出配置更新事件
            event = ControllerEvent(
                event_type="llm_config_updated",
                source=self.name,
                data={"name": config_name, "config": config_data}
            )
            self.emit_event(event)
            
            self.logger.info(f"LLM配置已更新: {config_name}")
            return True
            
        except Exception as e:
            self._handle_error(e, f"更新LLM配置失败: {config_name}")
            return False
    
    def _validate_llm_config(self, config: dict) -> bool:
        """验证LLM配置的有效性"""
        if not isinstance(config, dict):
            self.logger.error(f"LLM配置必须是字典类型，当前类型: {type(config)}")
            return False
            
        required_fields = ["api_key", "base_url", "model_name", "interface_format"]
        optional_fields = ["temperature", "max_tokens", "timeout"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in config:
                self.logger.error(f"LLM配置缺少必需字段: {field}")
                return False
            # api_key可以为空，其他字段不能为空
            if field != "api_key" and not config[field]:
                self.logger.error(f"LLM配置字段 '{field}' 不能为空")
                return False
        
        # 验证数值类型字段
        if "temperature" in config:
            try:
                temp = float(config["temperature"])
                if not (0 <= temp <= 2):
                    self.logger.error(f"temperature必须在0-2之间，当前值: {temp}")
                    return False
            except (ValueError, TypeError):
                self.logger.error(f"temperature必须是数值类型，当前值: {config['temperature']}")
                return False
        
        if "max_tokens" in config:
            try:
                tokens = int(config["max_tokens"])
                if tokens <= 0:
                    self.logger.error(f"max_tokens必须大于0，当前值: {tokens}")
                    return False
            except (ValueError, TypeError):
                self.logger.error(f"max_tokens必须是整数类型，当前值: {config['max_tokens']}")
                return False
        
        if "timeout" in config:
            try:
                timeout = int(config["timeout"])
                if timeout <= 0:
                    self.logger.error(f"timeout必须大于0，当前值: {timeout}")
                    return False
            except (ValueError, TypeError):
                self.logger.error(f"timeout必须是整数类型，当前值: {config['timeout']}")
                return False
        
        return True
    
    def get_llm_config_names(self) -> List[str]:
        """获取所有LLM配置名称"""
        llm_configs = self._config_cache.get("llm_configs", {})
        return list(llm_configs.keys())
    
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
            # 优先使用last_llm_config_name指定的配置
            last_llm_config = config_data.get("last_llm_config_name")
            if last_llm_config and last_llm_config in llm_configs:
                self._current_llm_config = llm_configs[last_llm_config]
            else:
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