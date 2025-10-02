# 🚀 部署文档

## 📋 概述

本文档详细说明AI小说生成器的部署方法，包括环境配置、依赖管理、打包发布等内容。

## 🖥️ 系统要求

### 最低系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python版本**: 3.9+ (推荐 3.10-3.12)
- **内存**: 4GB RAM (推荐 8GB+)
- **存储空间**: 2GB 可用空间
- **网络**: 稳定的互联网连接（用于API调用）

### 推荐系统配置
- **CPU**: 4核心以上
- **内存**: 16GB RAM
- **存储**: SSD硬盘，10GB+ 可用空间
- **GPU**: 可选，用于本地模型推理

## 🔧 环境配置

### 1. Python环境安装

#### Windows系统
```bash
# 方法1: 从官网下载安装
# 访问 https://www.python.org/downloads/
# 下载Python 3.10或3.11版本

# 方法2: 使用Chocolatey
choco install python

# 方法3: 使用Microsoft Store
# 搜索"Python 3.11"并安装
```

#### macOS系统
```bash
# 方法1: 使用Homebrew
brew install python@3.11

# 方法2: 使用pyenv
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### Linux系统
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# CentOS/RHEL
sudo yum install python3.11 python3.11-pip

# Arch Linux
sudo pacman -S python python-pip
```

### 2. 虚拟环境配置

#### 创建虚拟环境
```bash
# 进入项目目录
cd AI_NovelGenerator

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 验证环境
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version

# 升级pip
python -m pip install --upgrade pip
```

## 📦 依赖管理

### 1. 核心依赖安装

#### 标准安装
```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果遇到网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 分步安装（推荐）
```bash
# 1. 安装基础依赖
pip install customtkinter==5.2.2
pip install requests==2.32.5
pip install pydantic==2.11.7

# 2. 安装LLM相关依赖
pip install openai==1.106.1
pip install langchain==0.3.27
pip install langchain-openai==0.3.32
pip install langchain-community==0.3.29

# 3. 安装向量数据库依赖
pip install chromadb==1.0.20
pip install sentence-transformers==5.1.0

# 4. 安装其他依赖
pip install nltk==3.9.1
pip install numpy==2.3.2
pip install scikit-learn==1.7.1
```

### 2. 可选依赖

#### 开发工具
```bash
pip install black flake8 mypy pytest
```

#### 性能优化
```bash
# GPU加速（如果有NVIDIA GPU）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 更快的JSON处理
pip install orjson==3.11.3
```

#### 本地模型支持
```bash
# Ollama支持
pip install ollama

# Transformers支持
pip install transformers==4.56.1
pip install accelerate
```

### 3. 依赖问题解决

#### 常见问题及解决方案

**问题1: 安装chromadb失败**
```bash
# 解决方案1: 安装Visual Studio Build Tools
# Windows: 下载并安装 Visual Studio Build Tools
# 勾选"C++ 桌面开发"选项

# 解决方案2: 使用预编译版本
pip install --only-binary=all chromadb
```

**问题2: sentence-transformers安装慢**
```bash
# 使用国内镜像
pip install sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者使用conda
conda install -c conda-forge sentence-transformers
```

**问题3: 内存不足**
```bash
# 限制pip并发安装
pip install --no-cache-dir -r requirements.txt

# 分批安装
pip install customtkinter langchain openai
pip install chromadb sentence-transformers
pip install nltk numpy scikit-learn
```

## 🏗️ 源码部署

### 1. 获取源码
```bash
# 方法1: Git克隆
git clone https://github.com/YILING0013/AI_NovelGenerator.git
cd AI_NovelGenerator

# 方法2: 下载ZIP
# 从GitHub下载ZIP文件并解压
```

### 2. 配置环境
```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化配置
```bash
# 首次运行会自动创建配置文件
python main.py

# 或者手动创建配置文件
cp config_template.json config.json
```

### 4. 验证安装
```bash
# 运行程序
python main.py

# 检查日志
tail -f app.log  # Linux/macOS
type app.log     # Windows
```

## 📱 打包发布

### 1. PyInstaller打包

#### 安装PyInstaller
```bash
pip install pyinstaller
```

#### 使用现有配置打包
```bash
# 使用项目提供的spec文件
pyinstaller main.spec

# 打包完成后，可执行文件位于 dist/ 目录
```

#### 自定义打包配置
```bash
# 生成基础spec文件
pyinstaller --onefile --windowed --name="AI小说生成器" main.py

# 编辑生成的spec文件，添加必要的数据文件和隐藏导入
```

#### 完整的spec配置示例
```python
# main.spec
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# 收集数据文件
datas = [
    ('ui', 'ui'),
    ('novel_generator', 'novel_generator'),
    ('docs', 'docs'),
    ('README.md', '.'),
    ('requirements.txt', '.')
]

# 收集二进制文件
binaries = []

# 隐藏导入
hiddenimports = [
    'typing_extensions',
    'langchain-openai',
    'openai',
    'google-genai',
    'nltk',
    'sentence_transformers',
    'scikit-learn',
    'langchain-community',
    'pydantic',
    'tiktoken_ext.openai_public',
    'chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2'
]

# 收集chromadb相关文件
tmp_ret = collect_all('chromadb')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 添加customtkinter主题文件
import customtkinter
customtkinter_dir = customtkinter.__path__[0]
datas.append((customtkinter_dir, 'customtkinter'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_NovelGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 如果有图标文件
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_NovelGenerator'
)
```

### 2. 打包优化

#### 减小文件大小
```bash
# 使用UPX压缩
pip install upx-ucl
pyinstaller --upx-dir=/path/to/upx main.spec

# 排除不必要的模块
# 在spec文件中添加excludes参数
excludes=['matplotlib', 'scipy.spatial.cKDTree']
```

#### 提高启动速度
```bash
# 使用--onedir模式而不是--onefile
# 这样可以避免每次启动时解压

# 在spec文件中设置
onefile=False
```

### 3. 多平台打包

#### Windows平台
```bash
# 在Windows系统上打包
pyinstaller main.spec

# 生成的文件：
# dist/AI_NovelGenerator/AI_NovelGenerator.exe
```

#### macOS平台
```bash
# 在macOS系统上打包
pyinstaller main.spec

# 创建DMG安装包
pip install dmgbuild
dmgbuild -s settings.py "AI小说生成器" AI_NovelGenerator.dmg
```

#### Linux平台
```bash
# 在Linux系统上打包
pyinstaller main.spec

# 创建AppImage
pip install python-appimage
python-appimage build main.py
```

## 🐳 Docker部署

### 1. Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（如果有Web界面）
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV DISPLAY=:0

# 启动命令
CMD ["python", "main.py"]
```

### 2. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-novel-generator:
    build: .
    container_name: ai-novel-generator
    volumes:
      - ./config:/app/config
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
    
  # 可选：添加向量数据库服务
  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma/chroma
    restart: unless-stopped

volumes:
  chromadb_data:
```

### 3. 构建和运行
```bash
# 构建镜像
docker build -t ai-novel-generator .

# 运行容器
docker run -d \
  --name ai-novel-generator \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  ai-novel-generator

# 使用Docker Compose
docker-compose up -d
```

## ☁️ 云端部署

### 1. 服务器配置

#### 基础服务器要求
```bash
# 最低配置
CPU: 2核心
内存: 4GB
存储: 20GB SSD
带宽: 5Mbps

# 推荐配置
CPU: 4核心
内存: 8GB
存储: 50GB SSD
带宽: 10Mbps
```

#### 服务器初始化
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y git python3.11 python3.11-pip python3.11-venv nginx

# 创建应用用户
sudo useradd -m -s /bin/bash ainovel
sudo usermod -aG sudo ainovel
```

### 2. 应用部署
```bash
# 切换到应用用户
sudo su - ainovel

# 克隆代码
git clone https://github.com/YILING0013/AI_NovelGenerator.git
cd AI_NovelGenerator

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置应用
cp config_template.json config.json
# 编辑配置文件...
```

### 3. 服务配置

#### Systemd服务
```ini
# /etc/systemd/system/ai-novel-generator.service
[Unit]
Description=AI Novel Generator
After=network.target

[Service]
Type=simple
User=ainovel
WorkingDirectory=/home/ainovel/AI_NovelGenerator
Environment=PATH=/home/ainovel/AI_NovelGenerator/venv/bin
ExecStart=/home/ainovel/AI_NovelGenerator/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ai-novel-generator

# 设置开机自启
sudo systemctl enable ai-novel-generator

# 查看服务状态
sudo systemctl status ai-novel-generator
```

## 🔒 安全配置

### 1. API密钥安全
```bash
# 使用环境变量存储敏感信息
export OPENAI_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"

# 在代码中读取环境变量
import os
api_key = os.getenv('OPENAI_API_KEY')
```

### 2. 文件权限
```bash
# 设置配置文件权限
chmod 600 config.json

# 设置日志文件权限
chmod 644 app.log

# 设置应用目录权限
chmod -R 755 /home/ainovel/AI_NovelGenerator
```

### 3. 网络安全
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# 如果使用Nginx反向代理
sudo ufw allow 'Nginx Full'
```

## 📊 监控和维护

### 1. 日志管理
```bash
# 配置日志轮转
sudo nano /etc/logrotate.d/ai-novel-generator

# 内容：
/home/ainovel/AI_NovelGenerator/app.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

### 2. 性能监控
```bash
# 安装监控工具
pip install psutil

# 监控脚本示例
import psutil
import logging

def monitor_system():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logging.info(f"CPU使用率: {cpu_percent}%")
    logging.info(f"内存使用率: {memory.percent}%")
    logging.info(f"磁盘使用率: {disk.percent}%")
```

### 3. 自动备份
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/ai-novel-generator"
APP_DIR="/home/ainovel/AI_NovelGenerator"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份配置和数据
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz \
    $APP_DIR/config.json \
    $APP_DIR/output/ \
    $APP_DIR/logs/

# 删除30天前的备份
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
```

## 🔧 故障排除

### 1. 常见部署问题

**问题1: Python版本不兼容**
```bash
# 检查Python版本
python --version

# 如果版本过低，升级Python
sudo apt install python3.11
```

**问题2: 依赖安装失败**
```bash
# 清理pip缓存
pip cache purge

# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**问题3: 权限问题**
```bash
# 修复文件权限
sudo chown -R ainovel:ainovel /home/ainovel/AI_NovelGenerator
chmod +x main.py
```

### 2. 运行时问题

**问题1: 内存不足**
```bash
# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**问题2: API调用失败**
```bash
# 检查网络连接
curl -I https://api.openai.com

# 检查API密钥
echo $OPENAI_API_KEY

# 查看详细错误日志
tail -f app.log
```

### 3. 性能优化

**优化1: 减少内存使用**
```python
# 在代码中添加内存清理
import gc
gc.collect()

# 使用生成器而不是列表
def process_large_data():
    for item in large_dataset:
        yield process(item)
```

**优化2: 提高响应速度**
```python
# 使用连接池
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

## 📋 部署检查清单

### 部署前检查
- [ ] Python环境版本正确 (3.9+)
- [ ] 所有依赖安装成功
- [ ] 配置文件正确设置
- [ ] API密钥有效
- [ ] 网络连接正常
- [ ] 存储空间充足

### 部署后验证
- [ ] 应用启动成功
- [ ] 基本功能正常
- [ ] API调用成功
- [ ] 日志记录正常
- [ ] 性能指标正常
- [ ] 安全配置生效

### 生产环境检查
- [ ] 服务自动启动
- [ ] 监控系统运行
- [ ] 备份策略执行
- [ ] 日志轮转配置
- [ ] 安全更新及时
- [ ] 文档更新完整

---

**部署完成！** 🎉

如遇到问题，请参考故障排除部分或在GitHub Issues中寻求帮助。