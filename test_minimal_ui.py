#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小化UI测试程序
用于验证CustomTkinter是否正常工作
"""

import customtkinter as ctk
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def test_minimal_ui():
    """测试最小化UI"""
    try:
        logging.info("开始创建最小化UI测试...")
        
        # 创建主窗口
        root = ctk.CTk()
        root.title("最小化UI测试")
        root.geometry("400x300")
        
        # 设置外观模式
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # 创建一个简单的标签
        label = ctk.CTkLabel(root, text="CustomTkinter 测试窗口", font=("Arial", 16))
        label.pack(pady=20)
        
        # 创建一个按钮
        def button_callback():
            logging.info("按钮被点击了！")
            label.configure(text="按钮已点击！")
        
        button = ctk.CTkButton(root, text="点击测试", command=button_callback)
        button.pack(pady=10)
        
        # 创建一个文本框
        textbox = ctk.CTkTextbox(root, width=300, height=100)
        textbox.pack(pady=10)
        textbox.insert("0.0", "这是一个测试文本框\n可以输入文字...")
        
        logging.info("UI组件创建完成，准备显示窗口...")
        
        # 强制显示窗口
        root.deiconify()  # 确保窗口可见
        root.lift()       # 提升窗口到前台
        root.focus_force() # 强制获取焦点
        
        logging.info("窗口应该已经显示，开始主循环...")
        
        # 启动主循环
        root.mainloop()
        
        logging.info("主循环结束")
        return True
        
    except Exception as e:
        logging.error(f"最小化UI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.info("启动最小化UI测试程序...")
    success = test_minimal_ui()
    if success:
        logging.info("测试完成")
        sys.exit(0)
    else:
        logging.error("测试失败")
        sys.exit(1)