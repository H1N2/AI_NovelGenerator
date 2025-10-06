# ui/plugin_manager_ui.py
"""
插件管理器UI界面
提供图形化的插件管理功能
"""

import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
import json
from language_manager import t


class PluginManagerUI:
    """插件管理器UI"""
    
    def __init__(self, parent, plugin_manager):
        self.parent = parent
        self.plugin_manager = plugin_manager
        self.window = None
        self.plugin_listbox = None
        self.detail_text = None
        self.status_label = None
        
    def show_manager_window(self):
        """显示插件管理窗口"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title(t("plugin.manager_title"))
        self.window.geometry("900x600")
        self.window.transient(self.parent)
        
        # 设置窗口图标（如果有的话）
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
            
        self._create_ui()
        self._refresh_plugin_list()
        
    def _create_ui(self):
        """创建UI界面"""
        # 主框架
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧插件列表
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # 插件列表标题
        list_title = ctk.CTkLabel(left_frame, text="**已发现的插件**", font=("Microsoft YaHei", 14, "bold"))
        list_title.pack(pady=(10, 5))
        
        # 插件列表框架
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 使用Treeview显示插件列表
        columns = ("name", "version", "status", "description")
        self.plugin_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        self.plugin_tree.heading("name", text="插件名称")
        self.plugin_tree.heading("version", text="版本")
        self.plugin_tree.heading("status", text="状态")
        self.plugin_tree.heading("description", text="描述")
        
        # 设置列宽
        self.plugin_tree.column("name", width=120)
        self.plugin_tree.column("version", width=80)
        self.plugin_tree.column("status", width=80)
        self.plugin_tree.column("description", width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugin_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定选择事件
        self.plugin_tree.bind("<<TreeviewSelect>>", self._on_plugin_select)
        
        # 操作按钮框架
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # 按钮
        self.load_btn = ctk.CTkButton(button_frame, text="加载插件", command=self._load_plugin)
        self.load_btn.pack(side="left", padx=5)
        
        self.unload_btn = ctk.CTkButton(button_frame, text="卸载插件", command=self._unload_plugin)
        self.unload_btn.pack(side="left", padx=5)
        
        self.reload_btn = ctk.CTkButton(button_frame, text="重新加载", command=self._reload_plugin)
        self.reload_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ctk.CTkButton(button_frame, text="刷新列表", command=self._refresh_plugin_list)
        self.refresh_btn.pack(side="left", padx=5)
        
        # 右侧详情面板
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # 详情标题
        detail_title = ctk.CTkLabel(right_frame, text="**插件详情**", font=("Microsoft YaHei", 14, "bold"))
        detail_title.pack(pady=(10, 5))
        
        # 详情文本框
        self.detail_text = ctk.CTkTextbox(right_frame, wrap="word", font=("Microsoft YaHei", 11))
        self.detail_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 性能监控按钮
        perf_frame = ctk.CTkFrame(right_frame)
        perf_frame.pack(fill="x", padx=10, pady=5)
        
        self.perf_btn = ctk.CTkButton(perf_frame, text="性能监控", command=self._show_performance)
        self.perf_btn.pack(side="left", padx=5)
        
        self.logs_btn = ctk.CTkButton(perf_frame, text="查看日志", command=self._show_logs)
        self.logs_btn.pack(side="left", padx=5)
        
        # 状态栏
        self.status_label = ctk.CTkLabel(self.window, text="就绪", font=("Microsoft YaHei", 10))
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)
        
    def _refresh_plugin_list(self):
        """刷新插件列表"""
        try:
            self._set_status("正在刷新插件列表...")
            
            # 清空现有列表
            for item in self.plugin_tree.get_children():
                self.plugin_tree.delete(item)
                
            # 发现插件
            discovered_plugins = self.plugin_manager.discover_plugins()
            loaded_plugins = self.plugin_manager.get_loaded_plugins()
            
            # 添加到列表
            for metadata in discovered_plugins:
                status = "已加载" if metadata.name in loaded_plugins else "未加载"
                
                # 检查插件状态
                if metadata.name in loaded_plugins:
                    plugin_instance = loaded_plugins[metadata.name]
                    status = plugin_instance.state.value
                    
                self.plugin_tree.insert("", "end", values=(
                    metadata.name,
                    metadata.version,
                    status,
                    metadata.description[:50] + "..." if len(metadata.description) > 50 else metadata.description
                ))
                
            self._set_status(f"发现 {len(discovered_plugins)} 个插件")
            
        except Exception as e:
            self._set_status(f"刷新失败: {e}")
            messagebox.showerror("错误", f"刷新插件列表失败: {e}")
            
    def _on_plugin_select(self, event):
        """插件选择事件"""
        selection = self.plugin_tree.selection()
        if not selection:
            return
            
        item = self.plugin_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        self._show_plugin_details(plugin_name)
        
    def _show_plugin_details(self, plugin_name: str):
        """显示插件详情"""
        try:
            # 获取插件元数据
            metadata = self.plugin_manager.registry.get_plugin(plugin_name)
            if not metadata:
                self.detail_text.delete("0.0", "end")
                self.detail_text.insert("0.0", "未找到插件信息")
                return
                
            # 获取插件实例（如果已加载）
            plugin_instance = self.plugin_manager.get_plugin(plugin_name)
            
            # 构建详情文本
            details = []
            details.append(f"**插件名称**: {metadata.name}")
            details.append(f"**版本**: {metadata.version}")
            details.append(f"**作者**: {metadata.author}")
            details.append(f"**描述**: {metadata.description}")
            details.append(f"**最低应用版本**: {metadata.min_app_version}")
            if metadata.max_app_version:
                details.append(f"**最高应用版本**: {metadata.max_app_version}")
                
            if metadata.dependencies:
                details.append(f"**依赖**: {', '.join(metadata.dependencies)}")
                
            details.append(f"**入口点**: {metadata.entry_point}")
            
            if plugin_instance:
                details.append(f"**当前状态**: {plugin_instance.state.value}")
                
                # 显示提供的服务
                services = plugin_instance.get_services()
                if services:
                    details.append(f"**提供的服务**: {', '.join(services.keys())}")
                    
                # 显示UI组件
                ui_components = plugin_instance.get_ui_components()
                if ui_components:
                    details.append(f"**UI组件**: {', '.join(ui_components.keys())}")
                    
                # 显示设置
                settings = plugin_instance.get_settings()
                if settings:
                    details.append("**当前设置**:")
                    for key, value in settings.items():
                        details.append(f"  - {key}: {value}")
                        
            else:
                details.append("**当前状态**: 未加载")
                
            # 显示详情
            self.detail_text.delete("0.0", "end")
            self.detail_text.insert("0.0", "\n".join(details))
            
        except Exception as e:
            self.detail_text.delete("0.0", "end")
            self.detail_text.insert("0.0", f"显示详情失败: {e}")
            
    def _load_plugin(self):
        """加载插件"""
        plugin_name = self._get_selected_plugin()
        if not plugin_name:
            return
            
        def load_task():
            try:
                self._set_status(f"正在加载插件 {plugin_name}...")
                success = self.plugin_manager.load_plugin(plugin_name)
                
                if success:
                    self._set_status(f"插件 {plugin_name} 加载成功")
                    self.window.after(0, self._refresh_plugin_list)
                else:
                    self._set_status(f"插件 {plugin_name} 加载失败")
                    
            except Exception as e:
                self._set_status(f"加载失败: {e}")
                self.window.after(0, lambda: messagebox.showerror("错误", f"加载插件失败: {e}"))
                
        threading.Thread(target=load_task, daemon=True).start()
        
    def _unload_plugin(self):
        """卸载插件"""
        plugin_name = self._get_selected_plugin()
        if not plugin_name:
            return
            
        if messagebox.askyesno("确认", f"确定要卸载插件 '{plugin_name}' 吗？"):
            def unload_task():
                try:
                    self._set_status(f"正在卸载插件 {plugin_name}...")
                    success = self.plugin_manager.unload_plugin(plugin_name)
                    
                    if success:
                        self._set_status(f"插件 {plugin_name} 卸载成功")
                        self.window.after(0, self._refresh_plugin_list)
                    else:
                        self._set_status(f"插件 {plugin_name} 卸载失败")
                        
                except Exception as e:
                    self._set_status(f"卸载失败: {e}")
                    self.window.after(0, lambda: messagebox.showerror("错误", f"卸载插件失败: {e}"))
                    
            threading.Thread(target=unload_task, daemon=True).start()
            
    def _reload_plugin(self):
        """重新加载插件"""
        plugin_name = self._get_selected_plugin()
        if not plugin_name:
            return
            
        def reload_task():
            try:
                self._set_status(f"正在重新加载插件 {plugin_name}...")
                success = self.plugin_manager.reload_plugin(plugin_name)
                
                if success:
                    self._set_status(f"插件 {plugin_name} 重新加载成功")
                    self.window.after(0, self._refresh_plugin_list)
                else:
                    self._set_status(f"插件 {plugin_name} 重新加载失败")
                    
            except Exception as e:
                self._set_status(f"重新加载失败: {e}")
                self.window.after(0, lambda: messagebox.showerror("错误", f"重新加载插件失败: {e}"))
                
        threading.Thread(target=reload_task, daemon=True).start()
        
    def _show_performance(self):
        """显示性能监控"""
        plugin_name = self._get_selected_plugin()
        if plugin_name:
            PluginPerformanceWindow(self.window, self.plugin_manager, plugin_name)
        else:
            PluginPerformanceWindow(self.window, self.plugin_manager)
            
    def _show_logs(self):
        """显示日志"""
        plugin_name = self._get_selected_plugin()
        PluginLogWindow(self.window, plugin_name)
        
    def _get_selected_plugin(self) -> Optional[str]:
        """获取选中的插件名称"""
        selection = self.plugin_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个插件")
            return None
            
        item = self.plugin_tree.item(selection[0])
        return item['values'][0]
        
    def _set_status(self, message: str):
        """设置状态栏消息"""
        if self.status_label:
            self.status_label.configure(text=message)


class PluginPerformanceWindow:
    """插件性能监控窗口"""
    
    def __init__(self, parent, plugin_manager, plugin_name: Optional[str] = None):
        self.parent = parent
        self.plugin_manager = plugin_manager
        self.plugin_name = plugin_name
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"性能监控 - {plugin_name or '全部插件'}")
        self.window.geometry("800x500")
        self.window.transient(parent)
        
        self._create_ui()
        self._refresh_stats()
        
    def _create_ui(self):
        """创建UI"""
        # 统计文本框
        self.stats_text = ctk.CTkTextbox(self.window, wrap="word", font=("Consolas", 10))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 刷新按钮
        refresh_btn = ctk.CTkButton(self.window, text="刷新", command=self._refresh_stats)
        refresh_btn.pack(pady=5)
        
    def _refresh_stats(self):
        """刷新统计信息"""
        try:
            stats = self.plugin_manager.get_performance_stats()
            
            output = []
            output.append("=== 插件性能统计 ===\n")
            
            if self.plugin_name and self.plugin_name in stats.get('plugins', {}):
                # 显示特定插件的统计
                plugin_stats = stats['plugins'][self.plugin_name]
                output.append(f"插件: {self.plugin_name}")
                output.append(f"总调用次数: {plugin_stats['total_calls']}")
                output.append(f"总执行时间: {plugin_stats['total_time']:.3f}s")
                output.append(f"平均执行时间: {plugin_stats['avg_time']:.3f}s")
                output.append(f"最大执行时间: {plugin_stats['max_time']:.3f}s")
                output.append(f"最小执行时间: {plugin_stats['min_time']:.3f}s")
                if 'avg_memory' in plugin_stats:
                    output.append(f"平均内存使用: {plugin_stats['avg_memory']:.2f}MB")
            else:
                # 显示所有插件的统计
                output.append(f"总记录数: {stats['total_records']}")
                output.append("\n--- 各插件统计 ---")
                
                for plugin_name, plugin_stats in stats.get('plugins', {}).items():
                    output.append(f"\n{plugin_name}:")
                    output.append(f"  调用次数: {plugin_stats['total_calls']}")
                    output.append(f"  平均时间: {plugin_stats['avg_time']:.3f}s")
                    output.append(f"  最大时间: {plugin_stats['max_time']:.3f}s")
                    
            # 服务调用统计
            if stats.get('service_calls'):
                output.append("\n--- 服务调用统计 ---")
                for plugin_name, services in stats['service_calls'].items():
                    if not self.plugin_name or plugin_name == self.plugin_name:
                        output.append(f"\n{plugin_name}:")
                        for service_name, service_stats in services.items():
                            output.append(f"  {service_name}: {service_stats['count']}次, "
                                        f"平均{service_stats['avg_time']:.3f}s")
                            
            self.stats_text.delete("0.0", "end")
            self.stats_text.insert("0.0", "\n".join(output))
            
        except Exception as e:
            self.stats_text.delete("0.0", "end")
            self.stats_text.insert("0.0", f"获取统计信息失败: {e}")


class PluginLogWindow:
    """插件日志查看窗口"""
    
    def __init__(self, parent, plugin_name: Optional[str] = None):
        self.parent = parent
        self.plugin_name = plugin_name
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"插件日志 - {plugin_name or '全部'}")
        self.window.geometry("800x500")
        self.window.transient(parent)
        
        self._create_ui()
        self._load_logs()
        
    def _create_ui(self):
        """创建UI"""
        # 日志文本框
        self.log_text = ctk.CTkTextbox(self.window, wrap="word", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = ctk.CTkButton(button_frame, text="刷新", command=self._load_logs)
        refresh_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(button_frame, text="清空", command=self._clear_logs)
        clear_btn.pack(side="left", padx=5)
        
    def _load_logs(self):
        """加载日志"""
        try:
            import os
            log_dir = "logs/plugins"
            
            if not os.path.exists(log_dir):
                self.log_text.delete("0.0", "end")
                self.log_text.insert("0.0", "日志目录不存在")
                return
                
            # 读取日志文件
            log_files = ["plugin_manager.log", "plugin_errors.log"]
            content = []
            
            for log_file in log_files:
                log_path = os.path.join(log_dir, log_file)
                if os.path.exists(log_path):
                    content.append(f"=== {log_file} ===")
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            # 只显示最后100行
                            content.extend(lines[-100:])
                    except Exception as e:
                        content.append(f"读取失败: {e}")
                    content.append("")
                    
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", "\n".join(content))
            
        except Exception as e:
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", f"加载日志失败: {e}")
            
    def _clear_logs(self):
        """清空日志显示"""
        self.log_text.delete("0.0", "end")