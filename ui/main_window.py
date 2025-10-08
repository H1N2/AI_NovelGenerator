"""
重构后的主窗口类
采用MVP架构，保持向后兼容性，确保原有功能不受影响
"""
import os
import threading
import logging
import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict
import types

# 导入MVP基础类和配置模型
from .mvp_base import BaseView, BasePresenter, ConfigurationModel
from .config_models import ConfigurationManager, LLMConfig, EmbeddingConfig, NovelParams
from .role_library import RoleLibrary
from llm_adapters import create_llm_adapter

# 导入新的控制器架构
from .controllers import ControllerRegistry, ConfigController, NovelController, GenerationController

# 导入插件系统
from plugins import PluginManager
from .plugin_manager_ui import PluginManagerUI

# 导入原有的UI构建函数（保持兼容性）
from ui.context_menu import TextWidgetContextMenu
from ui.main_tab import build_main_tab, build_left_layout, build_right_layout
from ui.config_tab import build_config_tabview, load_config_btn, save_config_btn
from ui.novel_params_tab import build_novel_params_area, build_optional_buttons_area
from ui.generation_handlers import (
    generate_novel_architecture_ui,
    generate_chapter_blueprint_ui,
    generate_chapter_draft_ui,
    finalize_chapter_ui,
    do_consistency_check,
    import_knowledge_handler,
    clear_vectorstore_handler,
    show_plot_arcs_ui,
    generate_batch_ui
)
from ui.setting_tab import build_setting_tab, load_novel_architecture, save_novel_architecture
from ui.directory_tab import build_directory_tab, load_chapter_blueprint, save_chapter_blueprint
from ui.character_tab import build_character_tab, load_character_state, save_character_state
from ui.summary_tab import build_summary_tab, load_global_summary, save_global_summary
from ui.chapters_tab import build_chapters_tab, refresh_chapters_list, on_chapter_selected, load_chapter_content, save_current_chapter, prev_chapter, next_chapter
from ui.other_settings import build_other_settings_tab

# 导入原有的工具函数
from config_manager import test_llm_config, test_embedding_config
from utils import read_file, save_string_to_txt, clear_file_content
from tooltips import tooltips

# 导入多语言支持
from language_manager import get_language_manager, t


class NovelGeneratorView(BaseView):
    """
    小说生成器视图类 - 负责UI显示和用户交互
    """
    
    def __init__(self, master):
        super().__init__()
        self.master = master
        self._setup_window()
        self._create_ui_variables()
        self._bind_generation_methods()
        self._build_ui()
        
        # 初始化插件系统
        self.plugin_manager = PluginManager(self)
        self.plugin_ui = PluginManagerUI(self.master, self.plugin_manager)
    
    def _bind_generation_methods(self):
        """绑定生成相关的方法"""
        # 绑定所有生成相关的方法到View实例
        self.generate_novel_architecture_ui = generate_novel_architecture_ui
        self.generate_chapter_blueprint_ui = generate_chapter_blueprint_ui
        self.generate_chapter_draft_ui = generate_chapter_draft_ui
        self.finalize_chapter_ui = finalize_chapter_ui
        self.do_consistency_check = do_consistency_check
        self.generate_batch_ui = lambda: generate_batch_ui(self)
        self.import_knowledge_handler = import_knowledge_handler
        self.clear_vectorstore_handler = clear_vectorstore_handler
        self.show_plot_arcs_ui = show_plot_arcs_ui
        self.load_config_btn = load_config_btn
        self.save_config_btn = save_config_btn
        self.load_novel_architecture = load_novel_architecture
        self.save_novel_architecture = save_novel_architecture
        self.load_chapter_blueprint = load_chapter_blueprint
        self.save_chapter_blueprint = save_chapter_blueprint
        self.load_character_state = load_character_state
        self.save_character_state = save_character_state
        self.load_global_summary = load_global_summary
        self.save_global_summary = save_global_summary
        self.refresh_chapters_list = refresh_chapters_list
        self.on_chapter_selected = on_chapter_selected
        self.save_current_chapter = save_current_chapter
        self.prev_chapter = prev_chapter
        self.next_chapter = next_chapter
        
        # 添加测试方法的占位符
        self.test_llm_config = None
        self.test_embedding_config = None
        
        # 添加config_file属性
        self.config_file = "config.json"
        
        # 添加loaded_config属性（需要在配置管理器初始化后设置）
        self.loaded_config = {}
    
    def _test_llm_config_with_button_state(self, button):
        """
        测试LLM配置并管理按钮状态
        
        Args:
            button: 测试按钮实例，用于状态管理
        """
        def test_in_thread():
            try:
                # 设置按钮为测试中状态
                button.configure(text=t("config.llm.testing"), state="disabled")
                self.master.update()
                
                # 执行测试逻辑
                if hasattr(self, 'config_controller') and self.config_controller:
                    # 使用控制器进行测试
                    result = self.config_controller.test_llm_configuration()
                    if result:
                        self.show_success(t("config.llm.test_success"))
                    else:
                        self.show_error(t("config.llm.test_failed"))
                else:
                    # 使用fallback方法
                    from config_manager import test_llm_config
                    current_config = self._get_current_llm_config()
                    result = test_llm_config(current_config)
                    if result:
                        self.show_success("LLM配置测试成功")
                    else:
                        self.show_error("LLM配置测试失败")
                        
            except Exception as e:
                self.show_error(f"LLM配置测试出错: {e}")
            finally:
                # 恢复按钮状态
                button.configure(text=t("config.llm.test_connection"), state="normal")
                self.master.update()
        
        # 在新线程中执行测试，避免阻塞UI
        threading.Thread(target=test_in_thread, daemon=True).start()
    
    def _get_current_llm_config(self):
        """获取当前LLM配置"""
        try:
            # 从UI变量构建配置对象
            from .config_models import LLMConfig
            return LLMConfig(
                interface_format=self.interface_format_var.get(),
                api_key=self.api_key_var.get(),
                base_url=self.base_url_var.get(),
                model_name=self.model_name_var.get(),
                temperature=self.temperature_var.get(),
                max_tokens=self.max_tokens_var.get(),
                timeout=self.timeout_var.get()
            )
        except Exception as e:
            logging.error(f"获取当前LLM配置失败: {e}")
            return None
    
    def _setup_window(self):
        """设置主窗口"""
        self.master.title(t("app.title"))
        try:
            if os.path.exists("icon.ico"):
                self.master.iconbitmap("icon.ico")
        except Exception:
            pass
        self.master.geometry("1350x840")
    
    def _create_ui_variables(self):
        """创建UI变量（保持向后兼容）"""
        # LLM配置变量
        self.api_key_var = ctk.StringVar()
        self.base_url_var = ctk.StringVar()
        self.interface_format_var = ctk.StringVar()
        self.model_name_var = ctk.StringVar()
        self.temperature_var = ctk.DoubleVar()
        self.max_tokens_var = ctk.IntVar()
        self.timeout_var = ctk.IntVar()
        self.interface_config_var = ctk.StringVar()
        
        # Embedding配置变量
        self.embedding_interface_format_var = ctk.StringVar()
        self.embedding_api_key_var = ctk.StringVar()
        self.embedding_url_var = ctk.StringVar()
        self.embedding_model_name_var = ctk.StringVar()
        self.embedding_retrieval_k_var = ctk.StringVar()
        
        # 生成配置变量
        self.architecture_llm_var = ctk.StringVar()
        self.chapter_outline_llm_var = ctk.StringVar()
        self.final_chapter_llm_var = ctk.StringVar()
        self.consistency_review_llm_var = ctk.StringVar()
        self.prompt_draft_llm_var = ctk.StringVar()
        
        # 小说参数变量
        self.genre_var = ctk.StringVar()
        self.num_chapters_var = ctk.StringVar()
        self.word_number_var = ctk.StringVar()
        self.filepath_var = ctk.StringVar()
        self.chapter_num_var = ctk.StringVar()
        self.characters_involved_var = ctk.StringVar()
        self.key_items_var = ctk.StringVar()
        self.scene_location_var = ctk.StringVar()
        self.time_constraint_var = ctk.StringVar()
        self.webdav_url_var = ctk.StringVar()
        self.webdav_username_var = ctk.StringVar()
        self.webdav_password_var = ctk.StringVar()
        
        # 其他变量
        self.topic_default = ""
        self.user_guidance_default = ""
        
        # 添加全局摘要和角色状态变量
        self.global_summary_var = ctk.StringVar()
        self.character_state_var = ctk.StringVar()
        self.novel_architecture_var = ctk.StringVar()
    
    def _build_ui(self):
        """构建UI界面"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建主要的Tab布局
        self.tabview = ctk.CTkTabview(self.master)
        self.tabview.pack(fill="both", expand=True)
        
        # 使用原有的UI构建函数（保持兼容性）
        build_main_tab(self)
        build_config_tabview(self)
        build_novel_params_area(self, start_row=1)
        build_optional_buttons_area(self, start_row=2)
        build_setting_tab(self)
        build_directory_tab(self)
        build_character_tab(self)
        build_summary_tab(self)
        build_chapters_tab(self)
        build_other_settings_tab(self)
        
    def _create_menu_bar(self):
        """创建菜单栏"""
        # 创建菜单栏
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # 插件系统菜单
        plugin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menus.plugin_system"), menu=plugin_menu)
        
        plugin_menu.add_command(label=t("menus.plugin_manager"), command=self._show_plugin_manager)
        plugin_menu.add_separator()
        plugin_menu.add_command(label=t("menus.reload_plugins"), command=self._reload_all_plugins)
        plugin_menu.add_command(label=t("menus.plugin_docs"), command=self._show_plugin_docs)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=t("menus.settings"), menu=settings_menu)
        
        # 语言设置子菜单
        language_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=t("menus.language"), menu=language_menu)
        
        language_menu.add_command(label="中文", command=lambda: self._change_language("zh_CN"))
        language_menu.add_command(label="English", command=lambda: self._change_language("en_US"))
        
    def _show_plugin_manager(self):
        """显示插件管理器"""
        try:
            self.plugin_ui.show_manager_window()
        except Exception as e:
            self.show_error(f"{t('error.plugin_manager_failed')}: {e}")
            
    def _reload_all_plugins(self):
        """重新加载所有插件"""
        try:
            self.plugin_manager.reload_all_plugins()
            self.show_success(t("success.plugins_reloaded"))
        except Exception as e:
            self.show_error(f"{t('error.plugin_reload_failed')}: {e}")
            
    def _show_plugin_docs(self):
        """显示插件开发文档"""
        try:
            import webbrowser
            import os
            docs_path = os.path.join("docs", "plugin_development.md")
            if os.path.exists(docs_path):
                webbrowser.open(f"file://{os.path.abspath(docs_path)}")
            else:
                self.show_error(t("error.plugin_docs_not_found"))
        except Exception as e:
            self.show_error(f"{t('error.open_docs_failed')}: {e}")
            
    def _change_language(self, language_code):
        """切换语言"""
        try:
            lang_manager = get_language_manager()
            lang_manager.set_language(language_code)
            self.show_success(t("success.language_changed"))
            # 重新创建菜单栏以更新语言
            self._create_menu_bar()
        except Exception as e:
            self.show_error(f"{t('error.language_change_failed')}: {e}")
    
    def update_view(self, data: Dict[str, Any]):
        """更新视图显示"""
        if "config_loaded" in data:
            self._update_ui_from_config(data["config_loaded"])
        elif "config_saved" in data:
            self.show_success("配置保存成功")
        elif "config_load_error" in data:
            self.show_error(f"配置加载失败: {data['config_load_error']}")
        elif "config_save_error" in data:
            self.show_error(f"配置保存失败: {data['config_save_error']}")
    
    def _update_ui_from_config(self, config_manager: ConfigurationManager):
        """从配置管理器更新UI"""
        # 更新LLM配置
        llm_config = config_manager.current_llm_config
        self.api_key_var.set(llm_config.api_key)
        self.base_url_var.set(llm_config.base_url)
        self.interface_format_var.set(llm_config.interface_format)
        self.model_name_var.set(llm_config.model_name)
        self.temperature_var.set(llm_config.temperature)
        self.max_tokens_var.set(llm_config.max_tokens)
        self.timeout_var.set(llm_config.timeout)
        
        # 更新Embedding配置
        emb_config = config_manager.current_embedding_config
        self.embedding_interface_format_var.set(config_manager._current_embedding_interface)
        self.embedding_api_key_var.set(emb_config.api_key)
        self.embedding_url_var.set(emb_config.base_url)
        self.embedding_model_name_var.set(emb_config.model_name)
        self.embedding_retrieval_k_var.set(str(emb_config.retrieval_k))
        
        # 更新生成配置
        choose_configs = config_manager.choose_configs
        self.architecture_llm_var.set(choose_configs.architecture_llm)
        self.chapter_outline_llm_var.set(choose_configs.chapter_outline_llm)
        self.final_chapter_llm_var.set(choose_configs.final_chapter_llm)
        self.consistency_review_llm_var.set(choose_configs.consistency_review_llm)
        self.prompt_draft_llm_var.set(choose_configs.prompt_draft_llm)
        
        # 更新小说参数
        novel_params = config_manager.novel_params
        self.topic_default = novel_params.topic
        self.genre_var.set(novel_params.genre)
        self.num_chapters_var.set(str(novel_params.num_chapters))
        self.word_number_var.set(str(novel_params.word_number))
        self.filepath_var.set(novel_params.filepath)
        self.chapter_num_var.set(str(novel_params.chapter_num))
        self.characters_involved_var.set(novel_params.characters_involved)
        self.key_items_var.set(novel_params.key_items)
        self.scene_location_var.set(novel_params.scene_location)
        self.time_constraint_var.set(novel_params.time_constraint)
        self.user_guidance_default = novel_params.user_guidance
        self.webdav_url_var.set(novel_params.webdav_url)
        self.webdav_username_var.set(novel_params.webdav_username)
        self.webdav_password_var.set(novel_params.webdav_password)
        
        # 设置当前配置名称
        if config_manager.llm_config_names:
            self.interface_config_var.set(config_manager._current_llm_config)
    
    def show_error(self, message: str):
        """显示错误信息"""
        messagebox.showerror("错误", message)
    
    def show_success(self, message: str):
        """显示成功信息"""
        messagebox.showinfo("成功", message)
    
    def safe_get_int(self, var, default=1):
        """安全获取整数值"""
        try:
            return int(var.get())
        except (ValueError, AttributeError):
            return default
    
    def log(self, message: str):
        """记录日志"""
        try:
            if hasattr(self, 'log_text') and self.log_text:
                # 临时启用文本框以便插入内容
                self.log_text.configure(state="normal")
                self.log_text.insert("end", f"{message}\n")
                self.log_text.see("end")
                # 重新禁用文本框
                self.log_text.configure(state="disabled")
        except Exception as e:
            # 如果UI日志失败，至少记录到系统日志
            logging.info(f"UI日志失败，消息: {message}, 错误: {e}")
    
    def safe_log(self, message: str):
        """安全记录日志"""
        try:
            self.log(message)
        except Exception:
            pass
    
    def disable_button_safe(self, btn):
        """安全禁用按钮"""
        try:
            if btn:
                btn.configure(state="disabled")
        except Exception:
            pass
    
    def enable_button_safe(self, btn):
        """安全启用按钮"""
        try:
            if btn:
                btn.configure(state="normal")
        except Exception:
            pass
    
    def handle_exception(self, context: str):
        """处理异常"""
        error_msg = f"在 {context} 中发生错误: {traceback.format_exc()}"
        logging.error(error_msg)
        self.safe_log(f"❌ {error_msg}")
    
    def show_chapter_in_textbox(self, text: str):
        """在文本框中显示章节内容"""
        try:
            if hasattr(self, 'chapter_content_text') and self.chapter_content_text:
                self.chapter_content_text.delete("0.0", "end")
                self.chapter_content_text.insert("0.0", text)
        except Exception:
            pass
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.filepath_var.set(folder_path)
    
    def show_character_import_window(self):
        """显示角色导入窗口"""
        # 这里可以添加角色导入的具体实现
        pass
    
    def show_role_library(self):
        """显示角色库"""
        # 这里可以添加角色库的具体实现
        pass


class NovelGeneratorPresenter(BasePresenter):
    """
    小说生成器展示器类 - 负责业务逻辑处理
    """
    
    def __init__(self, config_manager: ConfigurationManager, view: NovelGeneratorView):
        # 创建一个简单的Model实例用于MVP架构
        model = ConfigurationModel()
        super().__init__(model, view)
        self.config_manager = config_manager
        self._setup_role_library()
        
        # 绑定测试方法到View
        self.view.test_llm_config = self.test_llm_config
        self.view.test_embedding_config = self.test_embedding_config
    
    def _setup_role_library(self):
        """设置角色库"""
        try:
            # 获取保存路径
            save_path = os.path.dirname(self.config_manager.config_file) if hasattr(self.config_manager, 'config_file') else "."
            
            # 创建默认的LLM适配器
            llm_adapter = None
            if self.config_manager.current_llm_config:
                llm_config = self.config_manager.current_llm_config
                llm_adapter = create_llm_adapter(
                    interface_format=llm_config.interface_format,
                    api_key=llm_config.api_key,
                    base_url=llm_config.base_url,
                    model_name=llm_config.model_name,
                    temperature=llm_config.temperature,
                    max_tokens=llm_config.max_tokens,
                    timeout=llm_config.timeout
                )
            
            # 创建角色库实例，传入所需的三个参数
            self.role_library = RoleLibrary(self.view.master, save_path, llm_adapter)
            
            # 设置LLM适配器到角色库
            if llm_adapter:
                self.role_library.set_llm_adapter(llm_adapter)
        except Exception as e:
            logging.error(f"角色库LLM适配器更新失败: {e}")
    
    def handle_model_change(self, event: str, data: Any):
        """处理模型变更事件"""
        if event == "config_changed":
            self._update_role_library()
            # 通知View更新
            self.view.update_view({"config_loaded": self.config_manager})
        elif event == "config_load_error":
            self.view.update_view({"config_load_error": data})
        elif event == "config_save_error":
            self.view.update_view({"config_save_error": data})
    
    def _update_role_library(self):
        """更新角色库的LLM适配器"""
        try:
            if self.config_manager.current_llm_config:
                llm_config = self.config_manager.current_llm_config
                self.llm_adapter = create_llm_adapter(
                    interface_format=llm_config.interface_format,
                    api_key=llm_config.api_key,
                    base_url=llm_config.base_url,
                    model_name=llm_config.model_name,
                    temperature=llm_config.temperature,
                    max_tokens=llm_config.max_tokens,
                    timeout=llm_config.timeout
                )
                self.role_library.set_llm_adapter(self.llm_adapter)
        except Exception as e:
            logging.error(f"角色库LLM适配器更新失败: {e}")
    
    def test_llm_config(self):
        """测试LLM配置"""
        try:
            result = test_llm_config(self.config_manager.current_llm_config)
            if result:
                self.view.show_success("LLM配置测试成功")
            else:
                self.view.show_error("LLM配置测试失败")
        except Exception as e:
            self.view.show_error(f"LLM配置测试出错: {e}")
    
    def test_embedding_config(self):
        """测试Embedding配置"""
        try:
            result = test_embedding_config(self.config_manager.current_embedding_config)
            if result:
                self.view.show_success("Embedding配置测试成功")
            else:
                self.view.show_error("Embedding配置测试失败")
        except Exception as e:
            self.view.show_error(f"Embedding配置测试出错: {e}")


class NovelGeneratorGUI:
    """
    小说生成器主GUI类 - 整合MVP架构和控制器系统
    """
    
    def __init__(self, master):
        self.master = master
        
        # 初始化配置管理器
        self.config_manager = ConfigurationManager()
        
        # 创建View和Presenter
        self.view = NovelGeneratorView(master)
        self.presenter = NovelGeneratorPresenter(self.config_manager, self.view)
        
        # 绑定fallback方法
        self._bind_legacy_methods()
        
        # 设置控制器
        self._setup_controllers()
        
        # 设置控制器事件
        self._setup_controller_events()
        
        # 设置兼容性属性
        self._setup_compatibility_attributes()
    
    def _setup_controllers(self):
        """设置控制器系统"""
        try:
            # 创建控制器注册表
            self.controller_registry = ControllerRegistry()
            
            # 创建各个控制器 - 修复构造函数参数
            self.config_controller = ConfigController()  # 不传参数，使用默认构造函数
            self.novel_controller = NovelController()    # 不传参数，使用默认构造函数
            self.generation_controller = GenerationController()  # 不传参数，使用默认构造函数
            
            # 注册控制器 - 修复register方法调用，只传递控制器对象
            self.controller_registry.register(self.config_controller)
            self.controller_registry.register(self.novel_controller)
            self.controller_registry.register(self.generation_controller)
            
            # 将控制器绑定到View
            self.view.config_controller = self.config_controller
            self.view.novel_controller = self.novel_controller
            self.view.generation_controller = self.generation_controller
            
        except Exception as e:
            logging.error(f"控制器设置失败: {e}")
    
    def _setup_controller_events(self):
        """设置控制器事件监听"""
        try:
            # 配置控制器事件 - 使用正确的方法名
            if hasattr(self.config_controller, 'add_event_listener'):
                self.config_controller.add_event_listener('config_changed', self.presenter.handle_model_change)
                self.config_controller.add_event_listener('config_load_error', self.presenter.handle_model_change)
                self.config_controller.add_event_listener('config_save_error', self.presenter.handle_model_change)
            
        except Exception as e:
            logging.error(f"控制器事件设置失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'controller_registry'):
                self.controller_registry.cleanup()
            if hasattr(self.view, 'plugin_manager'):
                self.view.plugin_manager.cleanup()
        except Exception as e:
            logging.error(f"资源清理失败: {e}")
    
    def _bind_legacy_methods(self):
        """绑定fallback方法到View实例"""
        # 创建fallback方法并绑定到View
        self.view._generate_architecture_fallback = self._create_architecture_fallback()
        self.view._generate_blueprint_fallback = self._create_blueprint_fallback()
        self.view._generate_draft_fallback = self._create_draft_fallback()
        self.view._finalize_chapter_fallback = self._create_finalize_fallback()
    
    def _create_architecture_fallback(self):
        """创建架构生成fallback方法"""
        def _generate_architecture_fallback(filepath):
            """原有架构生成逻辑作为备用"""
            try:
                interface_format = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["interface_format"]
                api_key = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["api_key"]
                base_url = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["base_url"]
                model_name = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["model_name"]
                temperature = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["temperature"]
                max_tokens = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["max_tokens"]
                timeout_val = self.view.loaded_config["llm_configs"][self.view.architecture_llm_var.get()]["timeout"]

                topic = self.view.topic_text.get("0.0", "end").strip()
                genre = self.view.genre_var.get().strip()
                num_chapters = self.view.safe_get_int(self.view.num_chapters_var, 10)
                word_number = self.view.safe_get_int(self.view.word_number_var, 3000)
                user_guidance = self.view.user_guide_text.get("0.0", "end").strip()

                self.view.safe_log("开始生成小说架构...")
                from novel_generator import Novel_architecture_generate
                Novel_architecture_generate(
                    interface_format=interface_format,
                    api_key=api_key,
                    base_url=base_url,
                    llm_model=model_name,
                    topic=topic,
                    genre=genre,
                    number_of_chapters=num_chapters,
                    word_number=word_number,
                    filepath=filepath,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout_val,
                    user_guidance=user_guidance
                )
                self.view.safe_log("✅ 小说架构生成完成。请在 'Novel Architecture' 标签页查看或编辑。")
            except Exception as e:
                self.view.handle_exception("架构生成fallback")
        return _generate_architecture_fallback

    def _create_blueprint_fallback(self):
        """创建章节蓝图fallback方法"""
        def _generate_blueprint_fallback(filepath):
            """原有大纲生成逻辑作为备用"""
            try:
                interface_format = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["interface_format"]
                api_key = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["api_key"]
                base_url = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["base_url"]
                model_name = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["model_name"]
                temperature = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["temperature"]
                max_tokens = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["max_tokens"]
                timeout_val = self.view.loaded_config["llm_configs"][self.view.chapter_outline_llm_var.get()]["timeout"]

                self.view.safe_log("开始生成章节大纲...")
                from novel_generator import Chapter_blueprint_generate
                Chapter_blueprint_generate(
                    interface_format=interface_format,
                    api_key=api_key,
                    base_url=base_url,
                    llm_model=model_name,
                    filepath=filepath,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout_val
                )
                self.view.safe_log("✅ 章节大纲生成完成。请在 'Chapter Blueprint' 标签页查看或编辑。")
            except Exception as e:
                self.view.handle_exception("章节蓝图生成fallback")
        return _generate_blueprint_fallback

    def _create_draft_fallback(self):
        """创建章节草稿fallback方法"""
        def _generate_draft_fallback(filepath):
            """原有章节生成逻辑作为备用"""
            try:
                interface_format = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["interface_format"]
                api_key = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["api_key"]
                base_url = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["base_url"]
                model_name = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["model_name"]
                temperature = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["temperature"]
                max_tokens = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["max_tokens"]
                timeout_val = self.view.loaded_config["llm_configs"][self.view.final_chapter_llm_var.get()]["timeout"]

                chapter_num = self.view.safe_get_int(self.view.chapter_num_var, 1)
                characters_involved = self.view.characters_involved_var.get().strip()
                key_items = self.view.key_items_var.get().strip()
                scene_location = self.view.scene_location_var.get().strip()
                time_constraint = self.view.time_constraint_var.get().strip()
                user_guidance = self.view.user_guide_text.get("0.0", "end").strip()

                self.view.safe_log(f"开始生成第 {chapter_num} 章草稿...")
                from novel_generator import Chapter_draft_generate
                Chapter_draft_generate(
                    interface_format=interface_format,
                    api_key=api_key,
                    base_url=base_url,
                    llm_model=model_name,
                    chapter_num=chapter_num,
                    characters_involved=characters_involved,
                    key_items=key_items,
                    scene_location=scene_location,
                    time_constraint=time_constraint,
                    filepath=filepath,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout_val,
                    user_guidance=user_guidance
                )
                self.view.safe_log(f"✅ 第 {chapter_num} 章草稿生成完成。")
            except Exception as e:
                self.view.handle_exception("章节草稿生成fallback")
        return _generate_draft_fallback

    def _create_finalize_fallback(self):
        """创建章节完善fallback方法"""
        def _finalize_chapter_fallback(filepath):
            """原有章节完善逻辑作为备用"""
            try:
                interface_format = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["interface_format"]
                api_key = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["api_key"]
                base_url = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["base_url"]
                model_name = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["model_name"]
                temperature = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["temperature"]
                max_tokens = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["max_tokens"]
                timeout_val = self.view.loaded_config["llm_configs"][self.view.consistency_review_llm_var.get()]["timeout"]

                chapter_num = self.view.safe_get_int(self.view.chapter_num_var, 1)
                user_guidance = self.view.user_guide_text.get("0.0", "end").strip()

                self.view.safe_log(f"开始完善第 {chapter_num} 章...")
                from novel_generator import Finalize_chapter
                Finalize_chapter(
                    interface_format=interface_format,
                    api_key=api_key,
                    base_url=base_url,
                    llm_model=model_name,
                    chapter_num=chapter_num,
                    filepath=filepath,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout_val,
                    user_guidance=user_guidance
                )
                self.view.safe_log(f"✅ 第 {chapter_num} 章完善完成。")
            except Exception as e:
                self.view.handle_exception("章节完善fallback")
        return _finalize_chapter_fallback
    
    def _setup_compatibility_attributes(self):
        """设置兼容性属性，确保原有代码能正常工作"""
        # 将View的属性映射到GUI实例，保持向后兼容
        self.config_manager = self.config_manager
        self.view = self.view
        self.presenter = self.presenter
        
        # 映射所有UI变量到GUI实例
        self.api_key_var = self.view.api_key_var
        self.base_url_var = self.view.base_url_var
        self.interface_format_var = self.view.interface_format_var
        self.model_name_var = self.view.model_name_var
        self.temperature_var = self.view.temperature_var
        self.max_tokens_var = self.view.max_tokens_var
        self.timeout_var = self.view.timeout_var
        self.interface_config_var = self.view.interface_config_var
        
        self.embedding_interface_format_var = self.view.embedding_interface_format_var
        self.embedding_api_key_var = self.view.embedding_api_key_var
        self.embedding_url_var = self.view.embedding_url_var
        self.embedding_model_name_var = self.view.embedding_model_name_var
        self.embedding_retrieval_k_var = self.view.embedding_retrieval_k_var
        
        self.architecture_llm_var = self.view.architecture_llm_var
        self.chapter_outline_llm_var = self.view.chapter_outline_llm_var
        self.final_chapter_llm_var = self.view.final_chapter_llm_var
        self.consistency_review_llm_var = self.view.consistency_review_llm_var
        self.prompt_draft_llm_var = self.view.prompt_draft_llm_var
        
        self.genre_var = self.view.genre_var
        self.num_chapters_var = self.view.num_chapters_var
        self.word_number_var = self.view.word_number_var
        self.filepath_var = self.view.filepath_var
        self.chapter_num_var = self.view.chapter_num_var
        self.characters_involved_var = self.view.characters_involved_var
        self.key_items_var = self.view.key_items_var
        self.scene_location_var = self.view.scene_location_var
        self.time_constraint_var = self.view.time_constraint_var
        self.webdav_url_var = self.view.webdav_url_var
        self.webdav_username_var = self.view.webdav_username_var
        self.webdav_password_var = self.view.webdav_password_var
        self.global_summary_var = self.view.global_summary_var
        self.character_state_var = self.view.character_state_var
        self.novel_architecture_var = self.view.novel_architecture_var