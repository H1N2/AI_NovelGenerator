# 🔧 故障排除指南

## 📋 概述

本文档提供AI小说生成器常见问题的诊断和解决方案，帮助用户快速定位和解决使用过程中遇到的问题。

## 🚨 紧急问题处理

### 程序无法启动
```bash
# 1. 检查Python环境
python --version
# 应该显示 3.9+ 版本

# 2. 检查依赖安装
pip list | grep -E "(customtkinter|langchain|openai|chromadb)"

# 3. 查看错误日志
cat app.log | tail -20

# 4. 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 程序崩溃
```bash
# 1. 查看崩溃日志
tail -f app.log

# 2. 检查系统资源
# Windows
tasklist | findstr python

# Linux/macOS
ps aux | grep python
top -p $(pgrep python)

# 3. 重启程序
python main.py
```

### API调用失败
```bash
# 1. 测试网络连接
ping api.openai.com
curl -I https://api.openai.com

# 2. 验证API密钥
# 检查config.json中的API密钥是否正确

# 3. 查看API调用日志
grep "API" app.log | tail -10
```

## 🔍 安装问题

### Python版本问题

**问题**: `Python版本过低或不兼容`
```bash
# 症状
SyntaxError: invalid syntax
ModuleNotFoundError: No module named 'typing_extensions'

# 解决方案
# 1. 检查当前版本
python --version

# 2. 安装正确版本
# Windows
choco install python --version=3.11.0

# macOS
brew install python@3.11

# Linux
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 依赖安装问题

**问题1**: `chromadb安装失败`
```bash
# 症状
error: Microsoft Visual C++ 14.0 is required
Building wheel for chroma-hnswlib failed

# 解决方案
# Windows:
# 1. 安装Visual Studio Build Tools
# 2. 或使用预编译版本
pip install --only-binary=all chromadb

# Linux:
sudo apt install build-essential python3-dev

# macOS:
xcode-select --install
```

**问题2**: `sentence-transformers安装慢`
```bash
# 症状
安装过程卡在downloading模型文件

# 解决方案
# 1. 使用国内镜像
pip install sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 2. 手动下载模型
export HF_ENDPOINT=https://hf-mirror.com
pip install sentence-transformers

# 3. 离线安装
# 下载wheel文件后本地安装
pip install sentence_transformers-*.whl
```

**问题3**: `内存不足导致安装失败`
```bash
# 症状
MemoryError during installation
pip install killed

# 解决方案
# 1. 限制pip内存使用
pip install --no-cache-dir -r requirements.txt

# 2. 分批安装
pip install customtkinter langchain
pip install openai chromadb
pip install sentence-transformers

# 3. 增加虚拟内存
# Windows: 系统设置 -> 高级 -> 虚拟内存
# Linux: 
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 虚拟环境问题

**问题**: `虚拟环境创建或激活失败`
```bash
# 症状
venv\Scripts\activate 不是内部或外部命令
source: command not found

# 解决方案
# Windows PowerShell
python -m venv venv
venv\Scripts\Activate.ps1

# Windows CMD
python -m venv venv
venv\Scripts\activate.bat

# 如果执行策略限制
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

## ⚙️ 配置问题

### API配置错误

**问题1**: `OpenAI API密钥无效`
```json
// 症状
{
  "error": "Invalid API key provided"
}

// 解决方案
// 1. 检查config.json中的API密钥格式
{
  "llm_config": {
    "openai": {
      "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "base_url": "https://api.openai.com/v1"
    }
  }
}

// 2. 验证API密钥
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.openai.com/v1/models

// 3. 检查API密钥权限和余额
```

**问题2**: `DeepSeek API配置错误`
```json
// 症状
Connection timeout
SSL certificate verify failed

// 解决方案
{
  "llm_config": {
    "deepseek": {
      "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "base_url": "https://api.deepseek.com/v1",
      "timeout": 60
    }
  }
}

// 如果有网络问题，配置代理
{
  "network": {
    "proxy": {
      "http": "http://127.0.0.1:7890",
      "https": "http://127.0.0.1:7890"
    }
  }
}
```

**问题3**: `Embedding配置错误`
```json
// 症状
Embedding model not found
Rate limit exceeded

// 解决方案
{
  "embedding_config": {
    "openai": {
      "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "model_name": "text-embedding-3-small",
      "base_url": "https://api.openai.com/v1"
    }
  }
}

// 或使用本地模型
{
  "embedding_config": {
    "ollama": {
      "model_name": "nomic-embed-text",
      "base_url": "http://localhost:11434"
    }
  }
}
```

### 配置文件问题

**问题**: `配置文件格式错误`
```bash
# 症状
JSONDecodeError: Expecting ',' delimiter
Config file not found

# 解决方案
# 1. 验证JSON格式
python -m json.tool config.json

# 2. 使用模板重新创建
cp config_template.json config.json

# 3. 检查文件编码
file config.json
# 应该是UTF-8编码

# 4. 修复权限问题
chmod 644 config.json
```

## 🖥️ 界面问题

### CustomTkinter界面问题

**问题1**: `界面显示异常`
```python
# 症状
tkinter.TclError: couldn't connect to display
界面元素重叠或显示不全

# 解决方案
# 1. 检查显示环境变量 (Linux)
export DISPLAY=:0

# 2. 安装X11转发 (SSH连接)
ssh -X username@hostname

# 3. 更新CustomTkinter
pip install --upgrade customtkinter

# 4. 重置界面缓存
import customtkinter
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")
```

**问题2**: `字体显示问题`
```python
# 症状
中文字符显示为方块
字体大小异常

# 解决方案
# 1. 安装中文字体
# Windows: 系统自带
# Linux:
sudo apt install fonts-noto-cjk

# macOS:
brew install font-noto-sans-cjk

# 2. 在代码中指定字体
import customtkinter
customtkinter.set_appearance_mode("system")
font = customtkinter.CTkFont(family="Microsoft YaHei", size=12)
```

**问题3**: `界面卡顿或无响应`
```python
# 症状
点击按钮无反应
界面冻结

# 解决方案
# 1. 检查是否在主线程中更新UI
import threading
from tkinter import messagebox

def long_running_task():
    # 在后台线程中执行
    result = some_heavy_computation()
    # 使用after方法更新UI
    root.after(0, update_ui, result)

# 2. 添加进度指示
progress_bar = customtkinter.CTkProgressBar(root)
progress_bar.set(0.5)

# 3. 优化界面更新频率
root.update_idletasks()  # 而不是 root.update()
```

## 🤖 LLM调用问题

### API调用失败

**问题1**: `连接超时`
```python
# 症状
requests.exceptions.ConnectTimeout
ReadTimeout: HTTPSConnectionPool

# 解决方案
# 1. 增加超时时间
{
  "llm_config": {
    "openai": {
      "timeout": 120  // 增加到120秒
    }
  }
}

# 2. 配置重试机制
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# 3. 检查网络连接
ping api.openai.com
traceroute api.openai.com
```

**问题2**: `速率限制`
```python
# 症状
Rate limit exceeded
Too many requests

# 解决方案
# 1. 降低请求频率
import time
time.sleep(1)  # 请求间隔1秒

# 2. 使用指数退避
def exponential_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** i
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")

# 3. 升级API计划或使用多个API密钥
```

**问题3**: `模型不可用`
```python
# 症状
Model not found
Invalid model specified

# 解决方案
# 1. 检查可用模型列表
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.openai.com/v1/models

# 2. 更新配置中的模型名称
{
  "llm_config": {
    "openai": {
      "model_name": "gpt-3.5-turbo"  // 使用正确的模型名
    }
  }
}

# 3. 检查模型权限
# 确保API密钥有访问指定模型的权限
```

### 生成质量问题

**问题1**: `生成内容质量差`
```python
# 症状
生成的小说逻辑混乱
人物性格不一致
情节重复

# 解决方案
# 1. 调整温度参数
{
  "llm_config": {
    "openai": {
      "temperature": 0.7  // 降低随机性
    }
  }
}

# 2. 优化提示词
# 在prompt_definitions.py中改进提示词
CHAPTER_GENERATION_PROMPT = """
请根据以下信息生成小说章节：
- 严格遵循人物设定
- 保持情节连贯性
- 避免重复内容
...
"""

# 3. 增加一致性检查
# 启用consistency_checker功能
```

**问题2**: `生成速度慢`
```python
# 症状
每章生成时间过长
界面长时间无响应

# 解决方案
# 1. 减少max_tokens
{
  "llm_config": {
    "openai": {
      "max_tokens": 2000  // 减少生成长度
    }
  }
}

# 2. 使用更快的模型
{
  "llm_config": {
    "openai": {
      "model_name": "gpt-3.5-turbo"  // 而不是gpt-4
    }
  }
}

# 3. 并行处理
import asyncio
async def generate_multiple_chapters():
    tasks = [generate_chapter(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    return results
```

## 💾 数据存储问题

### ChromaDB问题

**问题1**: `向量数据库初始化失败`
```python
# 症状
chromadb.errors.InvalidDimensionException
Database lock error

# 解决方案
# 1. 清理数据库文件
rm -rf chroma_db/
# 重新启动程序会自动创建

# 2. 检查磁盘空间
df -h  # Linux/macOS
dir   # Windows

# 3. 修复权限问题
chmod -R 755 chroma_db/

# 4. 使用内存模式（临时解决）
import chromadb
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=None  # 内存模式
))
```

**问题2**: `向量检索异常`
```python
# 症状
No results found
Embedding dimension mismatch

# 解决方案
# 1. 检查embedding模型一致性
# 确保存储和查询使用相同的embedding模型

# 2. 重建向量索引
def rebuild_vector_store():
    # 删除现有数据库
    shutil.rmtree("chroma_db", ignore_errors=True)
    # 重新导入知识库
    import_knowledge_base()

# 3. 验证向量维度
embeddings = embedding_model.embed_query("test")
print(f"Embedding dimension: {len(embeddings)}")
```

### 文件存储问题

**问题**: `文件读写错误`
```python
# 症状
PermissionError: [Errno 13] Permission denied
FileNotFoundError: [Errno 2] No such file or directory
UnicodeDecodeError: 'utf-8' codec can't decode

# 解决方案
# 1. 修复文件权限
chmod 644 output/*.txt
chmod 755 output/

# 2. 创建缺失目录
import os
os.makedirs("output", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# 3. 处理编码问题
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 4. 检查磁盘空间
import shutil
free_space = shutil.disk_usage('.').free
if free_space < 1024 * 1024 * 100:  # 100MB
    print("磁盘空间不足")
```

## 🔧 性能问题

### 内存使用过高

**问题**: `程序占用内存过多`
```python
# 症状
MemoryError
系统变慢
程序被系统杀死

# 解决方案
# 1. 监控内存使用
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")

# 2. 及时释放内存
def cleanup_memory():
    gc.collect()  # 强制垃圾回收
    
# 3. 优化数据结构
# 使用生成器而不是列表
def process_large_data():
    for item in large_dataset:
        yield process(item)
        
# 4. 分批处理
def process_in_batches(data, batch_size=100):
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        process_batch(batch)
        gc.collect()
```

### CPU使用率高

**问题**: `CPU占用过高`
```python
# 症状
风扇狂转
系统响应慢
程序卡顿

# 解决方案
# 1. 优化算法复杂度
# 避免嵌套循环
# 使用更高效的数据结构

# 2. 添加适当延时
import time
time.sleep(0.1)  # 在循环中添加短暂延时

# 3. 使用多线程
import threading
from concurrent.futures import ThreadPoolExecutor

def cpu_intensive_task():
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_item, item) for item in items]
        results = [future.result() for future in futures]

# 4. 监控CPU使用
import psutil
cpu_percent = psutil.cpu_percent(interval=1)
if cpu_percent > 80:
    print("CPU使用率过高，考虑优化")
```

## 🌐 网络问题

### 代理配置

**问题**: `网络连接失败`
```python
# 症状
Connection refused
SSL certificate verify failed
Proxy connection failed

# 解决方案
# 1. 配置HTTP代理
{
  "network": {
    "proxy": {
      "http": "http://127.0.0.1:7890",
      "https": "http://127.0.0.1:7890"
    }
  }
}

# 2. 配置SOCKS代理
import requests
proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}
response = requests.get(url, proxies=proxies)

# 3. 跳过SSL验证（不推荐用于生产环境）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# 4. 测试网络连接
import socket
def test_connection(host, port):
    try:
        socket.create_connection((host, port), timeout=5)
        return True
    except:
        return False
```

### DNS解析问题

**问题**: `域名解析失败`
```bash
# 症状
Name or service not known
DNS resolution failed

# 解决方案
# 1. 更换DNS服务器
# Windows
netsh interface ip set dns "本地连接" static 8.8.8.8
netsh interface ip add dns "本地连接" 8.8.4.4 index=2

# Linux
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf

# 2. 清理DNS缓存
# Windows
ipconfig /flushdns

# Linux
sudo systemctl restart systemd-resolved

# 3. 使用IP地址直接连接
# 在hosts文件中添加映射
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/macOS: /etc/hosts
140.82.112.3 api.openai.com
```

## 📱 平台特定问题

### Windows问题

**问题1**: `PowerShell执行策略限制`
```powershell
# 症状
无法加载文件，因为在此系统上禁止运行脚本

# 解决方案
# 1. 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. 或者使用CMD
cmd /c "venv\Scripts\activate.bat && python main.py"

# 3. 直接运行Python
venv\Scripts\python.exe main.py
```

**问题2**: `路径问题`
```python
# 症状
FileNotFoundError: [WinError 3] 系统找不到指定的路径

# 解决方案
import os
# 使用绝对路径
config_path = os.path.abspath("config.json")

# 或使用pathlib
from pathlib import Path
config_path = Path(__file__).parent / "config.json"

# 处理中文路径
import locale
locale.setlocale(locale.LC_ALL, 'Chinese (Simplified)_China.936')
```

### macOS问题

**问题1**: `SSL证书问题`
```bash
# 症状
SSL: CERTIFICATE_VERIFY_FAILED

# 解决方案
# 1. 更新证书
/Applications/Python\ 3.11/Install\ Certificates.command

# 2. 或手动安装证书
pip install --upgrade certifi

# 3. 使用系统证书
import ssl
import certifi
ssl_context = ssl.create_default_context(cafile=certifi.where())
```

**问题2**: `权限问题`
```bash
# 症状
Operation not permitted

# 解决方案
# 1. 给予完全磁盘访问权限
# 系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限

# 2. 使用sudo（谨慎）
sudo python main.py

# 3. 修改文件权限
chmod +x main.py
```

### Linux问题

**问题1**: `显示问题`
```bash
# 症状
tkinter.TclError: no display name and no $DISPLAY environment variable

# 解决方案
# 1. 设置DISPLAY变量
export DISPLAY=:0

# 2. 安装X11
sudo apt install xorg

# 3. 使用Xvfb（虚拟显示）
sudo apt install xvfb
xvfb-run -a python main.py

# 4. SSH X11转发
ssh -X username@hostname
```

**问题2**: `依赖库问题`
```bash
# 症状
ImportError: libGL.so.1: cannot open shared object file

# 解决方案
# Ubuntu/Debian
sudo apt install libgl1-mesa-glx libglib2.0-0

# CentOS/RHEL
sudo yum install mesa-libGL glib2

# 或使用conda
conda install -c conda-forge libgl
```

## 🔍 调试技巧

### 日志分析

**启用详细日志**
```python
import logging

# 设置日志级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# 在关键位置添加日志
logger = logging.getLogger(__name__)
logger.debug("开始处理请求")
logger.info("API调用成功")
logger.warning("配置文件缺少某些参数")
logger.error("处理失败", exc_info=True)
```

**分析常见日志模式**
```bash
# 查找错误
grep -i error app.log

# 查找API调用
grep "API" app.log | tail -20

# 查找内存问题
grep -i "memory\|oom" app.log

# 统计错误频率
grep -i error app.log | cut -d' ' -f1-2 | sort | uniq -c
```

### 性能分析

**使用cProfile**
```python
import cProfile
import pstats

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 运行代码
your_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前10个最耗时的函数
```

**内存分析**
```python
import tracemalloc

# 开始内存跟踪
tracemalloc.start()

# 运行代码
your_function()

# 获取内存使用情况
current, peak = tracemalloc.get_traced_memory()
print(f"当前内存使用: {current / 1024 / 1024:.1f} MB")
print(f"峰值内存使用: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

## 📞 获取帮助

### 自助诊断

**运行诊断脚本**
```python
# diagnosis.py
import sys
import platform
import pkg_resources
import requests
import json

def system_info():
    print("=== 系统信息 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"架构: {platform.machine()}")

def check_dependencies():
    print("\n=== 依赖检查 ===")
    required_packages = [
        'customtkinter', 'langchain', 'openai', 
        'chromadb', 'sentence-transformers'
    ]
    
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✓ {package}: {version}")
        except:
            print(f"✗ {package}: 未安装")

def test_api_connection():
    print("\n=== API连接测试 ===")
    try:
        response = requests.get("https://api.openai.com", timeout=5)
        print("✓ OpenAI API可访问")
    except:
        print("✗ OpenAI API不可访问")

def check_config():
    print("\n=== 配置检查 ===")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ 配置文件格式正确")
        
        if 'llm_config' in config:
            print("✓ LLM配置存在")
        else:
            print("✗ LLM配置缺失")
            
    except FileNotFoundError:
        print("✗ 配置文件不存在")
    except json.JSONDecodeError:
        print("✗ 配置文件格式错误")

if __name__ == "__main__":
    system_info()
    check_dependencies()
    test_api_connection()
    check_config()
```

### 社区支持

**GitHub Issues**
- 搜索现有问题: https://github.com/YILING0013/AI_NovelGenerator/issues
- 提交新问题时请包含:
  - 系统信息
  - 错误日志
  - 复现步骤
  - 配置文件（隐藏敏感信息）

**问题报告模板**
```markdown
## 问题描述
简要描述遇到的问题

## 环境信息
- 操作系统: 
- Python版本: 
- 程序版本: 

## 复现步骤
1. 
2. 
3. 

## 期望行为
描述期望的正常行为

## 实际行为
描述实际发生的情况

## 错误日志
```
粘贴相关的错误日志
```

## 配置信息
```json
{
  "llm_config": {
    // 隐藏API密钥
  }
}
```

## 已尝试的解决方案
列出已经尝试过的解决方法
```

---

**记住**: 大多数问题都有解决方案，保持耐心，仔细阅读错误信息，按步骤排查问题。如果自助解决不了，不要犹豫寻求社区帮助！ 🤝