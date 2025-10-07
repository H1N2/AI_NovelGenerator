"""
小说控制器
负责处理小说项目管理相关的业务逻辑，包括项目创建、加载、保存等
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_controller import BaseController, ControllerState, ControllerEvent


class NovelController(BaseController):
    """
    小说控制器
    处理小说项目的创建、加载、保存等操作
    """
    
    def __init__(self):
        super().__init__("NovelController")
        self._current_project = None
        self._project_history = []
        self._auto_save_enabled = True
        self._auto_save_interval = 300  # 5分钟
    
    async def initialize(self) -> bool:
        """初始化小说控制器"""
        try:
            if not self.validate_dependencies():
                return False
            
            # 加载项目历史
            self._load_project_history()
            
            self.set_state(ControllerState.IDLE)
            return True
            
        except Exception as e:
            self._handle_error(e, "小说控制器初始化")
            return False
    
    async def cleanup(self):
        """清理资源"""
        # 保存当前项目
        if self._current_project:
            await self.save_current_project()
        
        # 保存项目历史
        self._save_project_history()
        
        self.logger.info("小说控制器已清理")
    
    async def create_new_project(self, project_data: Dict[str, Any]) -> bool:
        """创建新的小说项目"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 验证项目数据
            if not self._validate_project_data(project_data):
                self.set_state(ControllerState.ERROR)
                return False
            
            # 创建项目目录结构
            project_path = project_data["filepath"]
            if not self._create_project_structure(project_path):
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**项目目录创建失败**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 创建项目配置文件
            project_config = {
                "project_name": project_data["project_name"],
                "topic": project_data["topic"],
                "genre": project_data["genre"],
                "num_chapters": project_data["num_chapters"],
                "word_number": project_data["word_number"],
                "user_guidance": project_data.get("user_guidance", ""),
                "created_time": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "status": "created"
            }
            
            config_path = os.path.join(project_path, "project_config.json")
            if not self._save_project_config(config_path, project_config):
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**项目配置保存失败**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 设置当前项目
            self._current_project = {
                "path": project_path,
                "config": project_config
            }
            
            # 添加到项目历史
            self._add_to_project_history(project_path, project_config["project_name"])
            
            # 更新UI
            if hasattr(self.view, 'update_project_info'):
                self.view.update_project_info(project_config)
            
            if hasattr(self.view, 'show_success'):
                self.view.show_success(f"**项目 '{project_config['project_name']}' 创建成功**")
            
            # 发出项目创建事件
            event = ControllerEvent(
                event_type="project_created",
                source=self.name,
                data={"project_path": project_path, "config": project_config}
            )
            self.emit_event(event)
            
            self.set_state(ControllerState.COMPLETED)
            return True
            
        except Exception as e:
            self._handle_error(e, "创建新项目")
            return False
    
    async def load_project(self, project_path: str) -> bool:
        """加载现有项目"""
        try:
            self.set_state(ControllerState.PROCESSING)
            
            # 验证项目路径
            if not os.path.exists(project_path):
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**项目路径不存在**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 加载项目配置
            config_path = os.path.join(project_path, "project_config.json")
            project_config = self._load_project_config(config_path)
            
            if not project_config:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**项目配置文件无效**")
                self.set_state(ControllerState.ERROR)
                return False
            
            # 保存当前项目（如果有）
            if self._current_project:
                await self.save_current_project()
            
            # 设置当前项目
            self._current_project = {
                "path": project_path,
                "config": project_config
            }
            
            # 添加到项目历史
            self._add_to_project_history(project_path, project_config.get("project_name", "未命名项目"))
            
            # 更新UI
            if hasattr(self.view, 'update_project_info'):
                self.view.update_project_info(project_config)
            
            if hasattr(self.view, 'load_project_files'):
                self.view.load_project_files(project_path)
            
            if hasattr(self.view, 'show_success'):
                self.view.show_success(f"**项目 '{project_config.get('project_name', '未命名')}' 加载成功**")
            
            # 发出项目加载事件
            event = ControllerEvent(
                event_type="project_loaded",
                source=self.name,
                data={"project_path": project_path, "config": project_config}
            )
            self.emit_event(event)
            
            self.set_state(ControllerState.COMPLETED)
            return True
            
        except Exception as e:
            self._handle_error(e, "加载项目")
            return False
    
    async def save_current_project(self) -> bool:
        """保存当前项目"""
        try:
            if not self._current_project:
                return True
            
            self.set_state(ControllerState.PROCESSING)
            
            # 更新最后修改时间
            self._current_project["config"]["last_modified"] = datetime.now().isoformat()
            
            # 保存项目配置
            config_path = os.path.join(self._current_project["path"], "project_config.json")
            success = self._save_project_config(config_path, self._current_project["config"])
            
            if success:
                if hasattr(self.view, 'show_success'):
                    self.view.show_success("**项目保存成功**")
                
                # 发出项目保存事件
                event = ControllerEvent(
                    event_type="project_saved",
                    source=self.name,
                    data={"project_path": self._current_project["path"]}
                )
                self.emit_event(event)
                
                self.set_state(ControllerState.COMPLETED)
                return True
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("**项目保存失败**")
                self.set_state(ControllerState.ERROR)
                return False
                
        except Exception as e:
            self._handle_error(e, "保存项目")
            return False
    
    async def close_current_project(self) -> bool:
        """关闭当前项目"""
        try:
            if not self._current_project:
                return True
            
            # 保存当前项目
            await self.save_current_project()
            
            # 清除当前项目
            project_name = self._current_project["config"].get("project_name", "未命名")
            self._current_project = None
            
            # 更新UI
            if hasattr(self.view, 'clear_project_info'):
                self.view.clear_project_info()
            
            if hasattr(self.view, 'show_success'):
                self.view.show_success(f"**项目 '{project_name}' 已关闭**")
            
            # 发出项目关闭事件
            event = ControllerEvent(
                event_type="project_closed",
                source=self.name,
                data={"project_name": project_name}
            )
            self.emit_event(event)
            
            self.set_state(ControllerState.IDLE)
            return True
            
        except Exception as e:
            self._handle_error(e, "关闭项目")
            return False
    
    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """获取当前项目信息"""
        return self._current_project
    
    def get_project_history(self) -> List[Dict[str, Any]]:
        """获取项目历史"""
        return self._project_history.copy()
    
    def update_project_config(self, updates: Dict[str, Any]) -> bool:
        """更新项目配置"""
        try:
            if not self._current_project:
                return False
            
            # 更新配置
            self._current_project["config"].update(updates)
            self._current_project["config"]["last_modified"] = datetime.now().isoformat()
            
            # 更新UI
            if hasattr(self.view, 'update_project_info'):
                self.view.update_project_info(self._current_project["config"])
            
            # 发出配置更新事件
            event = ControllerEvent(
                event_type="project_config_updated",
                source=self.name,
                data={"updates": updates}
            )
            self.emit_event(event)
            
            return True
            
        except Exception as e:
            self._handle_error(e, "更新项目配置")
            return False
    
    def get_project_files(self) -> List[str]:
        """获取项目文件列表"""
        if not self._current_project:
            return []
        
        try:
            project_path = self._current_project["path"]
            files = []
            
            # 遍历项目目录
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    if filename.endswith(('.txt', '.md', '.json')):
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, project_path)
                        files.append(rel_path)
            
            return files
            
        except Exception as e:
            self.logger.error(f"获取项目文件列表失败: {e}")
            return []
    
    def _validate_project_data(self, project_data: Dict[str, Any]) -> bool:
        """验证项目数据"""
        required_fields = ["project_name", "topic", "genre", "num_chapters", "word_number", "filepath"]
        
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                self.logger.error(f"项目数据缺少必要字段: {field}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(f"**参数错误**: 缺少{field}")
                return False
        
        # 验证数值字段
        try:
            int(project_data["num_chapters"])
            int(project_data["word_number"])
        except ValueError:
            self.logger.error("章节数或字数必须为数字")
            if hasattr(self.view, 'show_error'):
                self.view.show_error("**参数错误**: 章节数或字数必须为数字")
            return False
        
        return True
    
    def _create_project_structure(self, project_path: str) -> bool:
        """创建项目目录结构"""
        try:
            # 创建主目录
            os.makedirs(project_path, exist_ok=True)
            
            # 创建子目录
            subdirs = [
                "architecture",      # 架构文件
                "blueprints",       # 章节蓝图
                "drafts",          # 章节草稿
                "final_chapters",  # 最终章节
                "characters",      # 角色信息
                "settings",        # 设定信息
                "resources"        # 资源文件
            ]
            
            for subdir in subdirs:
                subdir_path = os.path.join(project_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建项目目录结构失败: {e}")
            return False
    
    def _save_project_config(self, config_path: str, config: Dict[str, Any]) -> bool:
        """保存项目配置"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存项目配置失败: {e}")
            return False
    
    def _load_project_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """加载项目配置"""
        try:
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            self.logger.error(f"加载项目配置失败: {e}")
            return None
    
    def _load_project_history(self):
        """加载项目历史"""
        try:
            history_path = os.path.join(os.path.expanduser("~"), ".novel_generator", "project_history.json")
            
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    self._project_history = json.load(f)
            else:
                self._project_history = []
                
        except Exception as e:
            self.logger.error(f"加载项目历史失败: {e}")
            self._project_history = []
    
    def _save_project_history(self):
        """保存项目历史"""
        try:
            history_dir = os.path.join(os.path.expanduser("~"), ".novel_generator")
            os.makedirs(history_dir, exist_ok=True)
            
            history_path = os.path.join(history_dir, "project_history.json")
            
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self._project_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存项目历史失败: {e}")
    
    def _add_to_project_history(self, project_path: str, project_name: str):
        """添加到项目历史"""
        try:
            # 移除重复项
            self._project_history = [
                item for item in self._project_history 
                if item.get("path") != project_path
            ]
            
            # 添加新项到开头
            self._project_history.insert(0, {
                "path": project_path,
                "name": project_name,
                "last_opened": datetime.now().isoformat()
            })
            
            # 限制历史记录数量
            if len(self._project_history) > 10:
                self._project_history = self._project_history[:10]
                
        except Exception as e:
            self.logger.error(f"添加项目历史失败: {e}")