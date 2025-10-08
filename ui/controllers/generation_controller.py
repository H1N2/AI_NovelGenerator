"""
生成控制器
负责处理小说生成相关的业务逻辑，包括架构生成、章节生成等
重构后采用模板方法模式，消除代码重复
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
    生成控制器 - 重构版
    使用模板方法模式统一处理生成任务
    """
    
    def __init__(self):
        super().__init__("GenerationController")
        self._current_task = None
        self._task_progress = 0.0
        self._generation_callbacks = {}
        
        # 任务配置映射 - 消除特殊情况处理
        self._task_configs = {
            "architecture": {
                "display_name": "小说架构",
                "generator_func": self._execute_architecture_generation,
                "validator_func": self._validate_architecture_params,
                "async_runner": self._run_architecture_generation
            },
            "blueprint": {
                "display_name": "章节蓝图", 
                "generator_func": self._execute_blueprint_generation,
                "validator_func": self._validate_blueprint_params,
                "async_runner": self._run_blueprint_generation
            },
            "draft": {
                "display_name": "章节草稿",
                "generator_func": self._execute_draft_generation,
                "validator_func": self._validate_draft_params,
                "async_runner": self._run_draft_generation
            },
            "finalization": {
                "display_name": "章节定稿",
                "generator_func": self._execute_finalization,
                "validator_func": self._validate_finalization_params,
                "async_runner": self._run_finalization
            }
        }
    
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
    
    # ========== 统一的生成任务模板方法 ==========
    
    async def _execute_generation_task(self, task_type: str, params: Dict[str, Any]) -> bool:
        """
        通用生成任务执行模板 - 好品味实现
        消除了四个函数中的重复逻辑
        """
        task_config = self._task_configs.get(task_type)
        if not task_config:
            self._handle_unknown_task_type(task_type)
            return False
        
        try:
            self.set_state(ControllerState.PROCESSING)
            self._current_task = f"{task_type}_generation"
            
            # 统一参数验证
            if not task_config["validator_func"](params):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 统一配置获取
            llm_config = self._get_llm_config_for_task(task_type)
            if not llm_config:
                self._handle_config_error(task_type, task_config["display_name"])
                return False
            
            # 统一UI状态更新
            self._update_generation_status(f"正在生成{task_config['display_name']}...")
            
            # 发出开始事件
            self._emit_start_event(task_type, params)
            
            # 执行具体生成逻辑
            success = await task_config["async_runner"](llm_config, params)
            
            # 统一结果处理
            return self._handle_generation_result(task_type, task_config["display_name"], success, params)
            
        except Exception as e:
            return self._handle_generation_error(task_type, task_config["display_name"], e, params)
        finally:
            self._cleanup_generation_task()
    
    # ========== 公共接口方法 ==========
    
    async def generate_novel_architecture(self, params: Dict[str, Any]) -> bool:
        """生成小说架构"""
        return await self._execute_generation_task("architecture", params)
    
    async def generate_chapter_blueprint(self, params: Dict[str, Any]) -> bool:
        """生成章节蓝图"""
        return await self._execute_generation_task("blueprint", params)
    
    async def generate_chapter_draft(self, params: Dict[str, Any]) -> bool:
        """生成章节草稿"""
        return await self._execute_generation_task("draft", params)
    
    async def finalize_chapter(self, params: Dict[str, Any]) -> bool:
        """完成章节定稿"""
        return await self._execute_generation_task("finalization", params)
    
    # ========== 任务管理方法 ==========
    
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
            self._task_progress = 0.0
            self.set_state(ControllerState.IDLE)
    
    # ========== 回调管理 ==========
    
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
    
    # ========== 私有辅助方法 ==========
    
    def _handle_unknown_task_type(self, task_type: str):
        """处理未知任务类型"""
        error_msg = f"未知的生成任务类型: {task_type}"
        self.logger.error(error_msg)
        if hasattr(self.view, 'show_error'):
            self.view.show_error(f"**{error_msg}**")
        self.set_state(ControllerState.ERROR)
    
    def _handle_config_error(self, task_type: str, display_name: str):
        """处理配置错误"""
        error_msg = f"未找到{display_name}的LLM配置"
        self.logger.error(error_msg)
        if hasattr(self.view, 'show_error'):
            self.view.show_error(f"**{error_msg}**")
        self.set_state(ControllerState.ERROR)
    
    def _update_generation_status(self, status: str):
        """更新生成状态"""
        if hasattr(self.view, 'set_generation_status'):
            self.view.set_generation_status(f"**{status}**")
    
    def _emit_start_event(self, task_type: str, params: Dict[str, Any]):
        """发出开始事件"""
        start_event = ControllerEvent(
            event_type=f"{task_type}_generation_started",
            source=self.name,
            data=params
        )
        self.emit_event(start_event)
    
    def _handle_generation_result(self, task_type: str, display_name: str, success: bool, params: Dict[str, Any]) -> bool:
        """处理生成结果"""
        if success:
            if hasattr(self.view, 'show_success'):
                self.view.show_success(f"**{display_name}生成完成**")
            
            # 发出完成事件
            complete_event = ControllerEvent(
                event_type=f"{task_type}_generation_completed",
                source=self.name,
                data={"success": True, "params": params}
            )
            self.emit_event(complete_event)
            
            # 调用回调函数
            self._call_generation_callbacks(task_type, True, params)
            self.set_state(ControllerState.IDLE)
            return True
        else:
            if hasattr(self.view, 'show_error'):
                self.view.show_error(f"**{display_name}生成失败**")
            
            # 发出失败事件
            error_event = ControllerEvent(
                event_type=f"{task_type}_generation_failed",
                source=self.name,
                data={"success": False, "params": params}
            )
            self.emit_event(error_event)
            
            # 调用回调函数
            self._call_generation_callbacks(task_type, False, params)
            self.set_state(ControllerState.ERROR)
            return False
    
    def _handle_generation_error(self, task_type: str, display_name: str, error: Exception, params: Dict[str, Any]) -> bool:
        """处理生成异常"""
        error_msg = f"{display_name}生成异常: {str(error)}"
        self.logger.error(error_msg)
        if hasattr(self.view, 'show_error'):
            self.view.show_error(f"**{error_msg}**")
        
        # 发出异常事件
        exception_event = ControllerEvent(
            event_type=f"{task_type}_generation_exception",
            source=self.name,
            data={"error": str(error), "params": params}
        )
        self.emit_event(exception_event)
        
        self.set_state(ControllerState.ERROR)
        return False
    
    def _cleanup_generation_task(self):
        """清理生成任务"""
        self._current_task = None
        self._task_progress = 0.0
    
    # ========== 具体生成逻辑执行器 ==========
    
    async def _run_architecture_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """异步执行架构生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._execute_architecture_generation, 
            llm_config, 
            params
        )
    
    def _execute_architecture_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行架构生成"""
        try:
            result = Novel_architecture_generate(
                topic=params.get('topic', ''),
                genre=params.get('genre', ''),
                num_chapters=params.get('num_chapters', 10),
                word_number=params.get('word_number', 2000),
                filepath=params.get('filepath', ''),
                llm_config=llm_config
            )
            return result is not None
        except Exception as e:
            self.logger.error(f"架构生成执行失败: {e}")
            return False
    
    async def _run_blueprint_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """异步执行蓝图生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._execute_blueprint_generation, 
            llm_config, 
            params
        )
    
    def _execute_blueprint_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行蓝图生成"""
        try:
            result = Chapter_blueprint_generate(
                filepath=params.get('filepath', ''),
                llm_config=llm_config
            )
            return result is not None
        except Exception as e:
            self.logger.error(f"蓝图生成执行失败: {e}")
            return False
    
    async def _run_draft_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """异步执行草稿生成"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._execute_draft_generation, 
            llm_config, 
            params
        )
    
    def _execute_draft_generation(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行草稿生成"""
        try:
            result = generate_chapter_draft(
                filepath=params.get('filepath', ''),
                chapter_num=params.get('chapter_num', '1'),
                user_guidance=params.get('user_guidance', ''),
                characters_involved=params.get('characters_involved', ''),
                key_items=params.get('key_items', ''),
                scene_location=params.get('scene_location', ''),
                time_constraint=params.get('time_constraint', ''),
                llm_config=llm_config,
                embedding_config=params.get('embedding_config', {})
            )
            return result is not None
        except Exception as e:
            self.logger.error(f"草稿生成执行失败: {e}")
            return False
    
    async def _run_finalization(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """异步执行定稿"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._execute_finalization, 
            llm_config, 
            params
        )
    
    def _execute_finalization(self, llm_config: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """执行定稿"""
        try:
            result = finalize_chapter(
                filepath=params.get('filepath', ''),
                chapter_num=params.get('chapter_num', '1'),
                llm_config=llm_config
            )
            return result is not None
        except Exception as e:
            self.logger.error(f"定稿执行失败: {e}")
            return False
    
    # ========== 配置和验证方法 ==========
    
    def _get_llm_config_for_task(self, task_type: str) -> Optional[Dict[str, Any]]:
        """获取任务对应的LLM配置"""
        try:
            if hasattr(self, 'config_controller') and self.config_controller:
                return self.config_controller.get_current_llm_config()
            elif hasattr(self.view, 'get_current_llm_config'):
                return self.view.get_current_llm_config()
            else:
                self.logger.warning("无法获取LLM配置")
                return None
        except Exception as e:
            self.logger.error(f"获取LLM配置失败: {e}")
            return None
    
    def _validate_architecture_params(self, params: Dict[str, Any]) -> bool:
        """验证架构生成参数"""
        required_fields = ['topic', 'genre', 'num_chapters', 'word_number', 'filepath']
        return all(params.get(field) for field in required_fields)
    
    def _validate_blueprint_params(self, params: Dict[str, Any]) -> bool:
        """验证蓝图生成参数"""
        return bool(params.get('filepath'))
    
    def _validate_draft_params(self, params: Dict[str, Any]) -> bool:
        """验证草稿生成参数"""
        required_fields = ['filepath', 'chapter_num']
        return all(params.get(field) for field in required_fields)
    
    def _validate_finalization_params(self, params: Dict[str, Any]) -> bool:
        """验证定稿参数"""
        required_fields = ['filepath', 'chapter_num']
        return all(params.get(field) for field in required_fields)
    
    def _call_generation_callbacks(self, task_type: str, success: bool, params: Dict[str, Any]):
        """调用生成回调函数"""
        if task_type in self._generation_callbacks:
            for callback in self._generation_callbacks[task_type]:
                try:
                    callback(success, params)
                except Exception as e:
                    self.logger.error(f"生成回调函数执行失败: {e}")