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

# 导入MVP基础类和配置模型
from .mvp_base import BaseView, BasePresenter
from .config_models import ConfigurationManager, LLMConfig, EmbeddingConfig, NovelParams
from .role_library import RoleLibrary
from llm_adapters import create_llm_adapter

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


class NovelGeneratorView(BaseView):
    """
    小说生成器视图类
    负责UI显示和用户交互，继承自BaseView
    """
    
    def __init__(self, master):
        super().__init__()
        self.master = master
        self._setup_window()
        self._create_ui_variables()
        self._bind_generation_methods()
        self._build_ui()
        
        # 初始化插件系统
        self.plugin_manager = PluginManager()
        self.plugin_ui = PluginManagerUI(self.master, self.plugin_manager)
    
    def _bind_generation_methods(self):
        """绑定生成相关的方法"""
        # 绑定所有生成相关的方法到View实例
        self.generate_novel_architecture_ui = generate_novel_architecture_ui
        self.generate_chapter_blueprint_ui = generate_chapter_blueprint_ui
        self.generate_chapter_draft_ui = generate_chapter_draft_ui
        self.finalize_chapter_ui = finalize_chapter_ui
        self.do_consistency_check = do_consistency_check
        self.generate_batch_ui = generate_batch_ui
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
        self.browse_folder = self.browse_folder  # 绑定自身的browse_folder方法
        
        # **添加测试方法的占位符**
        self.test_llm_config = None
        self.test_embedding_config = None
        
        # **添加config_file属性**
        self.config_file = "config.json"
        
        # 添加loaded_config属性（需要在配置管理器初始化后设置）
        # 这里先设置为空字典，避免NoneType错误
        self.loaded_config = {}
    
    def _setup_window(self):
        """设置主窗口"""
        self.master.title("Novel Generator GUI")
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
        menubar.add_cascade(label="插件系统", menu=plugin_menu)
        
        plugin_menu.add_command(label="插件管理器", command=self._show_plugin_manager)
        plugin_menu.add_separator()
        plugin_menu.add_command(label="重新加载所有插件", command=self._reload_all_plugins)
        plugin_menu.add_command(label="插件开发文档", command=self._show_plugin_docs)
        
    def _show_plugin_manager(self):
        """显示插件管理器"""
        try:
            self.plugin_ui.show_manager_window()
        except Exception as e:
            self.show_error(f"打开插件管理器失败: {e}")
            
    def _reload_all_plugins(self):
        """重新加载所有插件"""
        try:
            self.plugin_manager.reload_all_plugins()
            self.show_success("所有插件重新加载完成")
        except Exception as e:
            self.show_error(f"重新加载插件失败: {e}")
            
    def _show_plugin_docs(self):
        """显示插件开发文档"""
        try:
            import webbrowser
            import os
            docs_path = os.path.join("docs", "plugin_development.md")
            if os.path.exists(docs_path):
                webbrowser.open(f"file://{os.path.abspath(docs_path)}")
            else:
                self.show_error("插件开发文档不存在")
        except Exception as e:
            self.show_error(f"打开文档失败: {e}")
    
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
    
    # 保持向后兼容的方法
    def show_tooltip(self, key: str):
        """显示工具提示"""
        if key in tooltips:
            messagebox.showinfo("提示", tooltips[key])
    
    def safe_get_int(self, var, default=1):
        """安全获取整数值"""
        try:
            return int(var.get())
        except (ValueError, tk.TclError):
            return default
    
    def log(self, message: str):
        """记录日志"""
        logging.info(message)
    
    def safe_log(self, message: str):
        """安全记录日志"""
        try:
            self.log(message)
        except Exception as e:
            print(f"Logging failed: {e}")
    
    def disable_button_safe(self, btn):
        """安全禁用按钮"""
        try:
            btn.configure(state="disabled")
        except Exception:
            pass
    
    def enable_button_safe(self, btn):
        """安全启用按钮"""
        try:
            btn.configure(state="normal")
        except Exception:
            pass
    
    def handle_exception(self, context: str):
        """处理异常"""
        error_msg = f"{context}: {traceback.format_exc()}"
        logging.error(error_msg)
        self.show_error(f"操作失败: {context}")
    
    def show_chapter_in_textbox(self, text: str):
        """在文本框中显示章节内容"""
        # 这个方法需要根据具体的UI组件实现
        pass
    
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.filepath_var.set(folder_path)
    
    def show_character_import_window(self):
        """显示角色导入窗口"""
        # 保持原有实现
        pass
    
    def show_role_library(self):
        """显示角色库"""
        if hasattr(self, '_role_lib'):
            self._role_lib.show()


class NovelGeneratorPresenter(BasePresenter):
    """
    小说生成器Presenter类
    负责协调Model和View之间的交互
    """
    
    def __init__(self, config_manager: ConfigurationManager, view: NovelGeneratorView):
        super().__init__(config_manager, view)
        self._setup_role_library()
    
    def _setup_role_library(self):
        """设置角色库"""
        try:
            save_path = self.model.novel_params.filepath or "."
            llm_adapter = create_llm_adapter(self.model.current_llm_config.__dict__)
            self.view._role_lib = RoleLibrary(self.view.master, save_path, llm_adapter)
        except Exception as e:
            logging.error(f"Failed to setup role library: {e}")
    
    def handle_model_change(self, event: str, data: Any):
        """处理Model变化"""
        if event == "config_loaded":
            self.view.update_view({"config_loaded": self.model})
        elif event == "config_saved":
            self.view.update_view({"config_saved": data})
        elif event.startswith("config_") and event.endswith("_error"):
            self.view.update_view({event: data})
        elif event == "llm_config_updated":
            self._update_role_library()
        elif event == "novel_params_updated":
            self._update_role_library()
    
    def _update_role_library(self):
        """更新角色库"""
        try:
            if hasattr(self.view, '_role_lib'):
                save_path = self.model.novel_params.filepath or "."
                llm_adapter = create_llm_adapter(self.model.current_llm_config.__dict__)
                self.view._role_lib = RoleLibrary(self.view.master, save_path, llm_adapter)
        except Exception as e:
            logging.error(f"Failed to update role library: {e}")
    
    # 测试配置方法
    def test_llm_config(self):
        """测试LLM配置"""
        # 获取当前LLM配置
        current_config = self.config_manager.current_llm_config
        
        return test_llm_config(
            interface_format=current_config.interface_format,
            api_key=current_config.api_key,
            base_url=current_config.base_url,
            model_name=current_config.model_name,
            temperature=current_config.temperature,
            max_tokens=current_config.max_tokens,
            timeout=current_config.timeout,
            log_func=self.view.safe_log,
            handle_exception_func=self.view.handle_exception
        )
    
    def test_embedding_config(self):
        """测试Embedding配置"""
        # 获取当前Embedding配置
        current_config = self.config_manager.current_embedding_config
        
        return test_embedding_config(
            api_key=current_config.api_key,
            base_url=current_config.base_url,
            model_name=current_config.model_name,
            log_func=self.view.safe_log,
            handle_exception_func=self.view.handle_exception
        )


class NovelGeneratorGUI:
    """
    重构后的主GUI类，保持向后兼容性
    内部使用MVP架构，但对外接口保持不变
    """
    
    def __init__(self, master):
        # 创建配置管理器
        self.config_manager = ConfigurationManager()
        
        # 创建View
        self.view = NovelGeneratorView(master)
        
        # 创建Presenter
        self.presenter = NovelGeneratorPresenter(self.config_manager, self.view)
        
        # 保持向后兼容的属性访问
        self._setup_compatibility_attributes()
        
        # 绑定原有的方法（保持向后兼容）
        self._bind_legacy_methods()
        
        # 加载配置
        self.config_manager.load_configuration()
        
        # **设置loaded_config属性**
        self.loaded_config = self.config_manager._get_current_config()
        self.view.loaded_config = self.loaded_config
        
        # 设置观察者模式
        self.config_manager.add_observer(self.presenter)
    
    def _setup_compatibility_attributes(self):
        """设置向后兼容的属性"""
        # 将View的属性暴露到主类中（保持兼容性）
        self.master = self.view.master
        self.tabview = self.view.tabview
        
        # UI变量
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
        
        self.topic_default = self.view.topic_default
        self.user_guidance_default = self.view.user_guidance_default
        
        # 配置相关属性
        self.config_file = self.config_manager.config_file
        self.loaded_config = self.config_manager._get_current_config()
        
        # 角色库
        if hasattr(self.view, '_role_lib'):
            self._role_lib = self.view._role_lib
    
    def _bind_legacy_methods(self):
        """绑定原有的方法（保持向后兼容）"""
        # 将导入的各模块函数直接赋给类方法
        self.generate_novel_architecture_ui = generate_novel_architecture_ui
        self.generate_chapter_blueprint_ui = generate_chapter_blueprint_ui
        self.generate_chapter_draft_ui = generate_chapter_draft_ui
        self.finalize_chapter_ui = finalize_chapter_ui
        self.do_consistency_check = do_consistency_check
        self.generate_batch_ui = generate_batch_ui
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
        self.browse_folder = self.view.browse_folder
        
        # 绑定View的方法
        self.show_tooltip = self.view.show_tooltip
        self.safe_get_int = self.view.safe_get_int
        self.log = self.view.log
        self.safe_log = self.view.safe_log
        self.disable_button_safe = self.view.disable_button_safe
        self.enable_button_safe = self.view.enable_button_safe
        self.handle_exception = self.view.handle_exception
        self.show_chapter_in_textbox = self.view.show_chapter_in_textbox
        self.show_character_import_window = self.view.show_character_import_window
        self.show_role_library = self.view.show_role_library
        
        # 绑定Presenter的方法
        self.test_llm_config = self.presenter.test_llm_config
        self.test_embedding_config = self.presenter.test_embedding_config
        
        # 同时将这些方法也绑定到View上（确保完全兼容）
        self.view.loaded_config = self.loaded_config
        self.view.generate_novel_architecture_ui = generate_novel_architecture_ui
        self.view.generate_chapter_blueprint_ui = generate_chapter_blueprint_ui
        self.view.generate_chapter_draft_ui = generate_chapter_draft_ui
        self.view.finalize_chapter_ui = finalize_chapter_ui
        self.view.do_consistency_check = do_consistency_check
        self.view.generate_batch_ui = generate_batch_ui
        self.view.import_knowledge_handler = import_knowledge_handler
        self.view.clear_vectorstore_handler = clear_vectorstore_handler
        self.view.show_plot_arcs_ui = show_plot_arcs_ui
        self.view.load_config_btn = load_config_btn
        self.view.save_config_btn = save_config_btn
        self.view.load_novel_architecture = load_novel_architecture
        self.view.save_novel_architecture = save_novel_architecture
        self.view.load_chapter_blueprint = load_chapter_blueprint
        self.view.save_chapter_blueprint = save_chapter_blueprint
        self.view.load_character_state = load_character_state
        self.view.save_character_state = save_character_state
        self.view.load_global_summary = load_global_summary
        self.view.save_global_summary = save_global_summary
        self.view.refresh_chapters_list = refresh_chapters_list
        self.view.on_chapter_selected = on_chapter_selected
        self.view.save_current_chapter = save_current_chapter
        self.view.prev_chapter = prev_chapter
        self.view.next_chapter = next_chapter
        
        # 绑定到view对象
        self.view.test_llm_config = self.presenter.test_llm_config
        self.view.test_embedding_config = self.presenter.test_embedding_config