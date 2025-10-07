# main.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import logging
import os
from datetime import datetime
from ui import NovelGeneratorGUI

# 确保logs目录存在
logs_dir = './logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 生成按日期命名的日志文件
log_filename = datetime.now().strftime('app_%Y%m%d.log')
log_filepath = os.path.join(logs_dir, log_filename)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler(log_filepath, encoding='utf-8')  # 输出到按日期命名的文件
    ]
)

def main():
    logging.info("应用程序启动")
    app = ctk.CTk()
    gui = NovelGeneratorGUI(app)
    app.mainloop()
    logging.info("应用程序退出")

if __name__ == "__main__":
    main()
