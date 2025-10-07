"""
生成控制器
负责处理小说生成相关的业务逻辑，包括架构生成、章节生成等
"""
import asyncio
import threading
from typing import Dict, Any, Optional, Callable
from .base_controller import BaseController, ControllerState, ControllerEvent
from novel_generator.architecture import Novel_architecture_generate
from novel_generator.blueprint import Chapter_blueprint_generate
from novel_generator.chapter import generate_chapter_draft
from novel_generator.finalization import finalize_chapter


class GenerationController(BaseController):
    """
    生成控制器
    处理小说生成的各个阶段
    """
    
    def __init__(self):
        super().__init__("GenerationController")
        self._current_task = None
        self._task_progress = 0.0
        self._generation_callbacks = {}
    
    async def initialize(self) -> bool:
        """初始化生成控制器"""
        try:
            if not self.validate_dependencies():
                return False
            
            self.set_state(ControllerState.IDLE)
            return True
            
        except Exception as e:
            self._handle_error(e, "生成控制器初始化")
            return False
    
    async def cleanup(self):
        """清理资源"""
        if self._current_task:
            self._current_task = None
        self._generation_callbacks.clear()
        self.logger.info("生成控制器已清理")
    
    def add_generation_callback(self, task_type: str, callback: Callable):
        """添加生成任务回调"""
        if task_type not in self._generation_callbacks:
            self._generation_callbacks[task_type] = []
        self._generation_callbacks[task_type].append(callback)
    
    def remove_generation_callback(self, task_type: str, callback: Callable):
        """移除生成任务回调"""
        if task_type in self._generation_callbacks:
            try:
                self._generation_callbacks[task_type].remove(callback)
            except ValueError:
                pass
    
    async def generate_novel_architecture(self, params: Dict[str, Any]) -> bool:
        """生成小说架构"""
        try:
            self.set_state(ControllerState.PROCESSING)
            self._current_task = "architecture_generation"
            
            # 验证参数
            if not self._validate_architecture_params(params):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 获取LLM配置
            llm_config = self._get_llm_config_for_task("architecture")
            if not llm_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到架构生成的LLM配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 更新UI状态
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("**正在生成小说架构...**")
            
            # 发出开始事件
            start_event = ControllerEvent(
                event_type="architecture_generation_started",
                source=self.name,
                data=params
            )
            self.emit_event(start_event)
            
            # 执行生成任务
            success = await self._run_architecture_generation(llm_config, params)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success("**小说架构生成完成**")
                
                # 发出完成事件
                complete_event = ControllerEvent(
                    event_type="architecture_generation_completed",
                    source=self.name,
                    data=params
                )
                self.emit_event(complete_event)
                
                # 调用回调函数
                self._call_generation_callbacks("architecture", True, params)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**小说架构生成失败**")
                
                # 调用回调函数
                self._call_generation_callbacks("architecture", False, params)
                
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "生成小说架构")
            self._call_generation_callbacks("architecture", False, params)
            return False
        finally:
            self._current_task = None
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("")
    
    async def generate_chapter_blueprint(self, params: Dict[str, Any]) -> bool:
        """生成章节蓝图"""
        try:
            self.set_state(ControllerState.PROCESSING)
            self._current_task = "blueprint_generation"
            
            # 验证参数
            if not self._validate_blueprint_params(params):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 获取LLM配置
            llm_config = self._get_llm_config_for_task("blueprint")
            if not llm_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到章节蓝图生成的LLM配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 更新UI状态
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status(f"**正在生成第{params.get('chapter_num', '?')}章蓝图...**")
            
            # 发出开始事件
            start_event = ControllerEvent(
                event_type="blueprint_generation_started",
                source=self.name,
                data=params
            )
            self.emit_event(start_event)
            
            # 执行生成任务
            success = await self._run_blueprint_generation(llm_config, params)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success(f"**第{params.get('chapter_num', '?')}章蓝图生成完成**")
                
                # 发出完成事件
                complete_event = ControllerEvent(
                    event_type="blueprint_generation_completed",
                    source=self.name,
                    data=params
                )
                self.emit_event(complete_event)
                
                # 调用回调函数
                self._call_generation_callbacks("blueprint", True, params)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**第{params.get('chapter_num', '?')}章蓝图生成失败**")
                
                # 调用回调函数
                self._call_generation_callbacks("blueprint", False, params)
                
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "生成章节蓝图")
            self._call_generation_callbacks("blueprint", False, params)
            return False
        finally:
            self._current_task = None
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("")
    
    async def generate_chapter_draft(self, params: Dict[str, Any]) -> bool:
        """生成章节草稿"""
        try:
            self.set_state(ControllerState.PROCESSING)
            self._current_task = "draft_generation"
            
            # 验证参数
            if not self._validate_draft_params(params):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 获取LLM配置
            llm_config = self._get_llm_config_for_task("draft")
            if not llm_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到章节草稿生成的LLM配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 更新UI状态
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status(f"**正在生成第{params.get('chapter_num', '?')}章草稿...**")
            
            # 发出开始事件
            start_event = ControllerEvent(
                event_type="draft_generation_started",
                source=self.name,
                data=params
            )
            self.emit_event(start_event)
            
            # 执行生成任务
            success = await self._run_draft_generation(llm_config, params)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success(f"**第{params.get('chapter_num', '?')}章草稿生成完成**")
                
                # 发出完成事件
                complete_event = ControllerEvent(
                    event_type="draft_generation_completed",
                    source=self.name,
                    data=params
                )
                self.emit_event(complete_event)
                
                # 调用回调函数
                self._call_generation_callbacks("draft", True, params)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**第{params.get('chapter_num', '?')}章草稿生成失败**")
                
                # 调用回调函数
                self._call_generation_callbacks("draft", False, params)
                
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "生成章节草稿")
            self._call_generation_callbacks("draft", False, params)
            return False
        finally:
            self._current_task = None
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("")
    
    async def finalize_chapter(self, params: Dict[str, Any]) -> bool:
        """定稿章节"""
        try:
            self.set_state(ControllerState.PROCESSING)
            self._current_task = "chapter_finalization"
            
            # 验证参数
            if not self._validate_finalization_params(params):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 获取LLM配置
            llm_config = self._get_llm_config_for_task("finalization")
            if not llm_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**未找到章节定稿的LLM配置**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 更新UI状态
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status(f"**正在定稿第{params.get('chapter_num', '?')}章...**")
            
            # 发出开始事件
            start_event = ControllerEvent(
                event_type="finalization_started",
                source=self.name,
                data=params
            )
            self.emit_event(start_event)
            
            # 执行定稿任务
            success = await self._run_finalization(llm_config, params)
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success(f"**第{params.get('chapter_num', '?')}章定稿完成**")
                
                # 发出完成事件
                complete_event = ControllerEvent(
                    event_type="finalization_completed",
                    source=self.name,
                    data=params
                )
                self.emit_event(complete_event)
                
                # 调用回调函数
                self._call_generation_callbacks("finalization", True, params)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**第{params.get('chapter_num', '?')}章定稿失败**")
                
                # 调用回调函数
                self._call_generation_callbacks("finalization", False, params)
                
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "定稿章节")
            self._call_generation_callbacks("finalization", False, params)
            return False
        finally:
            self._current_task = None
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("")
    
    def get_current_task(self) -> Optional[str]:
        """获取当前任务"""
        return self._current_task
    
    def get_task_progress(self) -> float:
        """获取任务进度"""
        return self._task_progress
    
    def cancel_current_task(self):
        """取消当前任务"""
        if self._current_task:
            self.logger.info(f"取消任务: {self._current_task}")
            self._current_task = None
            self.set_state(ControllerState.IDLE)
            
            if hasattr(self.view, 'set_generation_status'):
                self.view.set_generation_status("**任务已取消**")
    
    async def _run_architecture_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行架构生成任务"""
        try:
            # 在线程中执行生成任务
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_architecture_generation,
                llm_config,
                params
            )
            return success
        except Exception as e:
            self.logger.error(f"架构生成执行失败: {e}")
            return False
    
    def _execute_architecture_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行架构生成（在线程中运行）"""
        try:
            Novel_architecture_generate(
                interface_format=llm_config.get("interface_format", "OpenAI"),
                api_key=llm_config["api_key"],
                base_url=llm_config["base_url"],
                llm_model=llm_config["model_name"],
                topic=params["topic"],
                genre=params["genre"],
                number_of_chapters=params["num_chapters"],
                word_number=params["word_number"],
                filepath=params["filepath"],
                user_guidance=params.get("user_guidance", ""),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 8192),
                timeout=llm_config.get("timeout", 600)
            )
            return True
        except Exception as e:
            self.logger.error(f"架构生成执行异常: {e}")
            return False
    
    async def _run_blueprint_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行蓝图生成任务"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_blueprint_generation,
                llm_config,
                params
            )
            return success
        except Exception as e:
            self.logger.error(f"蓝图生成执行失败: {e}")
            return False
    
    def _execute_blueprint_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行蓝图生成（在线程中运行）"""
        try:
            Chapter_blueprint_generate(
                chapter_num=params["chapter_num"],
                filepath=params["filepath"],
                llm_config=llm_config
            )
            return True
        except Exception as e:
            self.logger.error(f"蓝图生成执行异常: {e}")
            return False
    
    async def _run_draft_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行草稿生成任务"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_draft_generation,
                llm_config,
                params
            )
            return success
        except Exception as e:
            self.logger.error(f"草稿生成执行失败: {e}")
            return False
    
    def _execute_draft_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行草稿生成（在线程中运行）"""
        try:
            generate_chapter_draft(
                api_key=llm_config["api_key"],
                base_url=llm_config["base_url"],
                model_name=llm_config["model_name"],
                filepath=params["filepath"],
                novel_number=params["chapter_num"],
                word_number=params.get("word_number", 2000),
                temperature=llm_config.get("temperature", 0.7),
                user_guidance=params.get("user_guidance", ""),
                characters_involved=params.get("characters_involved", ""),
                key_items=params.get("key_items", ""),
                scene_location=params.get("scene_location", ""),
                time_constraint=params.get("time_constraint", ""),
                embedding_api_key=llm_config.get("embedding_api_key"),
                embedding_url=llm_config.get("embedding_url"),
                embedding_interface_format=llm_config.get("embedding_interface_format"),
                embedding_model_name=llm_config.get("embedding_model_name"),
                interface_format=llm_config.get("interface_format", "OpenAI"),
                max_tokens=llm_config.get("max_tokens", 8192),
                timeout=llm_config.get("timeout", 600)
            )
            return True
        except Exception as e:
            self.logger.error(f"草稿生成执行异常: {e}")
            return False
    
    async def _run_finalization(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行定稿任务"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_finalization,
                llm_config,
                params
            )
            return success
        except Exception as e:
            self.logger.error(f"定稿执行失败: {e}")
            return False
    
    def _execute_finalization(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行定稿（在线程中运行）"""
        try:
            finalize_chapter(
                chapter_num=params["chapter_num"],
                filepath=params["filepath"],
                llm_config=llm_config
            )
            return True
        except Exception as e:
            self.logger.error(f"定稿执行异常: {e}")
            return False
    
    def _get_llm_config_for_task(self, task_type: str) -> Optional[Dict[str, Any]]:
        """获取指定任务类型的LLM配置"""
        if not self.model or not hasattr(self.model, 'get_data'):
            return None
        
        # 获取选择的配置
        choose_configs = self.model.get_data("choose_configs", {})
        
        # 根据任务类型获取对应的LLM配置名称
        config_key_map = {
            "architecture": "architecture_llm",
            "blueprint": "chapter_outline_llm", 
            "draft": "prompt_draft_llm",
            "finalization": "final_chapter_llm"
        }
        
        config_key = config_key_map.get(task_type)
        if not config_key:
            return None
        
        config_name = choose_configs.get(config_key)
        if not config_name:
            # 如果没有指定配置，使用默认配置
            llm_configs = self.model.get_data("llm_configs", {})
            if llm_configs:
                return next(iter(llm_configs.values()))
            return None
        
        # 获取指定的配置
        llm_configs = self.model.get_data("llm_configs", {})
        return llm_configs.get(config_name)
    
    def _validate_architecture_params(self, params: Dict[str, Any]) -> bool:
        """验证架构生成参数"""
        required_fields = ["topic", "genre", "num_chapters", "word_number", "filepath"]
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"架构生成参数缺少必要字段: {field}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**参数错误**: 缺少{field}")
                return False
        return True
    
    def _validate_blueprint_params(self, params: Dict[str, Any]) -> bool:
        """验证蓝图生成参数"""
        required_fields = ["chapter_num", "filepath"]
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"蓝图生成参数缺少必要字段: {field}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**参数错误**: 缺少{field}")
                return False
        return True
    
    def _validate_draft_params(self, params: Dict[str, Any]) -> bool:
        """验证草稿生成参数"""
        required_fields = ["chapter_num", "filepath"]
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"草稿生成参数缺少必要字段: {field}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**参数错误**: 缺少{field}")
                return False
        return True
    
    def _validate_finalization_params(self, params: Dict[str, Any]) -> bool:
        """验证定稿参数"""
        required_fields = ["chapter_num", "filepath"]
        for field in required_fields:
            if field not in params or not params[field]:
                self.logger.error(f"定稿参数缺少必要字段: {field}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**参数错误**: 缺少{field}")
                return False
        return True
    
    def _call_generation_callbacks(self, task_type: str, success: bool, params: Dict[str, Any]):
        """调用生成任务回调函数"""
        callbacks = self._generation_callbacks.get(task_type, [])
        for callback in callbacks:
            try:
                callback(success, params)
            except Exception as e:
                self.logger.error(f"生成回调函数执行失败: {e}")