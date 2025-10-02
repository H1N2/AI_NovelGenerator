# 🛠️ 开发者指南

## 📋 概述

欢迎参与AI小说生成器的开发！本文档将帮助你了解项目的代码结构、开发规范和扩展方法。

## 🏗️ 项目结构

### 核心目录结构
```
AI_NovelGenerator/
├── main.py                    # 应用程序入口
├── config_manager.py          # 配置管理模块
├── utils.py                   # 通用工具函数
├── llm_adapters.py           # LLM适配器实现
├── embedding_adapters.py     # 嵌入模型适配器
├── prompt_definitions.py     # 提示词定义
├── consistency_checker.py    # 一致性检查器
├── requirements.txt          # 项目依赖
├── main.spec                 # PyInstaller配置
├── novel_generator/          # 核心生成模块
│   ├── __init__.py
│   ├── architecture.py       # 小说架构生成
│   ├── blueprint.py          # 章节蓝图生成
│   ├── drafting.py          # 章节草稿生成
│   ├── finalization.py      # 章节定稿
│   ├── knowledge.py         # 知识库管理
│   ├── vectorstore_utils.py # 向量存储工具
│   └── common.py            # 通用重试和清洗工具
├── ui/                      # 用户界面模块
│   ├── main_window.py       # 主窗口
│   ├── main_tab.py          # 主标签页
│   ├── generation_handlers.py # 生成处理器
│   └── role_library.py      # 角色库管理
└── docs/                    # 项目文档
    ├── README.md
    ├── architecture.md
    ├── api-reference.md
    ├── user-guide.md
    ├── configuration.md
    └── developer-guide.md
```

### 模块职责划分

#### 🎯 核心生成模块 (`novel_generator/`)
- **`architecture.py`**: 小说整体架构生成
- **`blueprint.py`**: 章节蓝图和大纲生成
- **`drafting.py`**: 章节内容草稿生成
- **`finalization.py`**: 章节内容定稿和优化
- **`knowledge.py`**: 知识库导入和管理
- **`vectorstore_utils.py`**: 向量存储操作
- **`common.py`**: 重试机制、文本清洗等通用功能

#### 🖥️ 用户界面模块 (`ui/`)
- **`main_window.py`**: 主窗口框架和配置管理
- **`main_tab.py`**: 主要功能标签页布局
- **`generation_handlers.py`**: 生成任务的UI处理逻辑
- **`role_library.py`**: 角色库管理界面

#### 🔌 适配器模块
- **`llm_adapters.py`**: 各种LLM服务的统一接口
- **`embedding_adapters.py`**: 各种嵌入模型的统一接口

#### ⚙️ 基础设施模块
- **`config_manager.py`**: 配置文件管理
- **`utils.py`**: 文件操作等基础工具
- **`prompt_definitions.py`**: 所有提示词模板
- **`consistency_checker.py`**: 内容一致性检查

## 📝 代码规范

### 1. 文件编码和头部
```python
# filename.py
# -*- coding: utf-8 -*-
"""
模块功能描述
"""
```

### 2. 导入规范
```python
# 标准库导入
import os
import json
import logging
import traceback

# 第三方库导入
import customtkinter as ctk
from langchain_chroma import Chroma

# 本地模块导入
from utils import read_file, save_string_to_txt
from novel_generator.common import invoke_with_cleaning
```

### 3. 日志配置
```python
logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### 4. 函数定义规范
```python
def function_name(param1: str, param2: int = 0) -> str:
    """
    函数功能描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述，默认值为0
        
    Returns:
        返回值描述
        
    Raises:
        Exception: 异常情况描述
    """
    pass
```

### 5. 类定义规范
```python
class BaseAdapter:
    """
    适配器基类，定义统一接口
    """
    
    def __init__(self, api_key: str, base_url: str):
        """初始化适配器"""
        self.api_key = api_key
        self.base_url = base_url
    
    def invoke(self, prompt: str) -> str:
        """调用接口生成内容"""
        raise NotImplementedError("子类必须实现invoke方法")
```

### 6. 错误处理规范
```python
def safe_operation():
    """安全操作示例"""
    try:
        # 主要逻辑
        result = risky_operation()
        return result
    except SpecificException as e:
        logging.error(f"特定错误: {e}")
        return default_value
    except Exception as e:
        logging.error(f"未知错误: {e}")
        logging.error(traceback.format_exc())
        return None
```

### 7. 配置管理规范
```python
# 使用配置管理器
from config_manager import load_config, save_config

config = load_config()
api_key = config.get("llm_configs", {}).get("OpenAI", {}).get("api_key", "")
```

## 🔧 开发环境设置

### 1. 环境要求
- **Python**: 3.9+ (推荐 3.10-3.12)
- **操作系统**: Windows/macOS/Linux
- **内存**: 最低4GB，推荐8GB+
- **存储**: 至少2GB可用空间

### 2. 开发工具推荐
```bash
# IDE推荐
- PyCharm Professional
- Visual Studio Code + Python扩展
- Sublime Text + Python插件

# 代码质量工具
pip install black          # 代码格式化
pip install flake8         # 代码检查
pip install mypy           # 类型检查
pip install pytest         # 单元测试
```

### 3. 开发环境配置
```bash
# 1. 克隆项目
git clone https://github.com/YILING0013/AI_NovelGenerator
cd AI_NovelGenerator

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装开发依赖
pip install black flake8 mypy pytest

# 5. 运行项目
python main.py
```

### 4. 代码质量检查
```bash
# 代码格式化
black . --line-length 88

# 代码风格检查
flake8 . --max-line-length=88 --ignore=E203,W503

# 类型检查
mypy . --ignore-missing-imports

# 运行测试
pytest tests/
```

## 🚀 扩展开发指南

### 1. 添加新的LLM适配器

#### 步骤1: 创建适配器类
```python
# 在 llm_adapters.py 中添加
class NewLLMAdapter(BaseLLMAdapter):
    """新LLM服务适配器"""
    
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 temperature: float = 0.7, max_tokens: int = 4096, 
                 timeout: int = 600):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
    
    def invoke(self, prompt: str) -> str:
        """实现具体的调用逻辑"""
        try:
            # 实现API调用逻辑
            response = self._call_api(prompt)
            return response
        except Exception as e:
            logging.error(f"NewLLM调用失败: {e}")
            raise
    
    def _call_api(self, prompt: str) -> str:
        """具体的API调用实现"""
        # 实现HTTP请求逻辑
        pass
```

#### 步骤2: 更新工厂函数
```python
# 在 create_llm_adapter 函数中添加
def create_llm_adapter(interface_format: str, api_key: str, 
                      base_url: str, model_name: str, **kwargs):
    if interface_format == "NewLLM":
        return NewLLMAdapter(api_key, base_url, model_name, **kwargs)
    # ... 其他适配器
```

#### 步骤3: 更新配置模板
```python
# 在 config_manager.py 的 DEFAULT_CONFIG 中添加
"NewLLM": {
    "api_key": "",
    "base_url": "https://api.newllm.com/v1",
    "model_name": "newllm-chat",
    "temperature": 0.7,
    "max_tokens": 4096,
    "timeout": 600,
    "interface_format": "NewLLM"
}
```

### 2. 添加新的Embedding适配器

#### 步骤1: 创建适配器类
```python
# 在 embedding_adapters.py 中添加
class NewEmbeddingAdapter(BaseEmbeddingAdapter):
    """新嵌入服务适配器"""
    
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        # 实现批量嵌入逻辑
        pass
    
    def embed_query(self, query: str) -> List[float]:
        """嵌入查询文本"""
        # 实现单个嵌入逻辑
        pass
```

#### 步骤2: 更新工厂函数
```python
# 在 create_embedding_adapter 函数中添加
def create_embedding_adapter(interface_format: str, **kwargs):
    if interface_format == "NewEmbedding":
        return NewEmbeddingAdapter(**kwargs)
    # ... 其他适配器
```

### 3. 添加新的生成功能

#### 步骤1: 在核心模块中实现
```python
# 在 novel_generator/ 中创建新模块
# new_feature.py
def new_generation_function(
    input_data: str,
    api_key: str,
    base_url: str,
    model_name: str,
    **kwargs
) -> str:
    """新的生成功能"""
    try:
        # 实现生成逻辑
        adapter = create_llm_adapter(...)
        result = adapter.invoke(prompt)
        return result
    except Exception as e:
        logging.error(f"新功能生成失败: {e}")
        raise
```

#### 步骤2: 添加UI处理器
```python
# 在 ui/generation_handlers.py 中添加
def new_feature_handler(self):
    """新功能的UI处理器"""
    def task():
        try:
            self.disable_button_safe(self.btn_new_feature)
            
            # 获取参数
            input_data = self.get_input_data()
            
            # 调用生成函数
            result = new_generation_function(
                input_data=input_data,
                api_key=self.get_api_key(),
                # ... 其他参数
            )
            
            # 显示结果
            self.safe_log(f"新功能结果: {result}")
            
        except Exception:
            self.handle_exception("新功能执行失败")
        finally:
            self.enable_button_safe(self.btn_new_feature)
    
    threading.Thread(target=task, daemon=True).start()
```

#### 步骤3: 添加UI控件
```python
# 在 ui/main_tab.py 中添加按钮
self.btn_new_feature = ctk.CTkButton(
    parent_frame,
    text="新功能",
    command=self.new_feature_handler
)
self.btn_new_feature.pack(pady=5)
```

### 4. 扩展提示词系统

#### 添加新提示词
```python
# 在 prompt_definitions.py 中添加
NEW_FEATURE_PROMPT = """\
你是一个专业的{role}，请根据以下要求完成任务：

输入内容：
{input_content}

任务要求：
{requirements}

输出格式：
{output_format}

请严格按照要求完成任务，不要添加额外解释。
"""

# 使用示例
def use_new_prompt(input_content: str, requirements: str):
    prompt = NEW_FEATURE_PROMPT.format(
        role="小说编辑",
        input_content=input_content,
        requirements=requirements,
        output_format="纯文本格式"
    )
    return prompt
```

## 🧪 测试指南

### 1. 单元测试结构
```python
# tests/test_adapters.py
import pytest
from llm_adapters import create_llm_adapter

class TestLLMAdapters:
    """LLM适配器测试"""
    
    def test_openai_adapter_creation(self):
        """测试OpenAI适配器创建"""
        adapter = create_llm_adapter(
            interface_format="OpenAI",
            api_key="test-key",
            base_url="https://api.openai.com/v1",
            model_name="gpt-3.5-turbo"
        )
        assert adapter is not None
        assert hasattr(adapter, 'invoke')
    
    @pytest.mark.integration
    def test_adapter_invoke(self):
        """集成测试：测试适配器调用"""
        # 需要真实API密钥的集成测试
        pass
```

### 2. 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_adapters.py

# 运行特定测试方法
pytest tests/test_adapters.py::TestLLMAdapters::test_openai_adapter_creation

# 跳过集成测试
pytest -m "not integration"

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 3. Mock测试示例
```python
# tests/test_generation.py
from unittest.mock import Mock, patch
from novel_generator.architecture import Novel_architecture_generate

class TestGeneration:
    """生成功能测试"""
    
    @patch('novel_generator.architecture.create_llm_adapter')
    def test_architecture_generation(self, mock_create_adapter):
        """测试架构生成"""
        # 设置Mock
        mock_adapter = Mock()
        mock_adapter.invoke.return_value = "测试架构内容"
        mock_create_adapter.return_value = mock_adapter
        
        # 调用函数
        result = Novel_architecture_generate(
            interface_format="OpenAI",
            api_key="test-key",
            # ... 其他参数
        )
        
        # 验证结果
        assert "测试架构内容" in result
        mock_adapter.invoke.assert_called_once()
```

## 📦 打包和发布

### 1. 使用PyInstaller打包
```bash
# 安装PyInstaller
pip install pyinstaller

# 使用现有配置打包
pyinstaller main.spec

# 或者重新生成配置
pyinstaller --onefile --windowed --name="AI小说生成器" main.py
```

### 2. 打包配置优化
```python
# main.spec 配置示例
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('novel_generator', 'novel_generator'),
        ('docs', 'docs')
    ],
    hiddenimports=[
        'customtkinter',
        'langchain_chroma',
        'sentence_transformers'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

### 3. 发布检查清单
- [ ] 代码质量检查通过
- [ ] 所有测试通过
- [ ] 文档更新完整
- [ ] 版本号更新
- [ ] 依赖项检查
- [ ] 打包测试成功
- [ ] 功能验证完成

## 🤝 贡献指南

### 1. 贡献流程
```bash
# 1. Fork项目到你的GitHub账户

# 2. 克隆你的Fork
git clone https://github.com/你的用户名/AI_NovelGenerator
cd AI_NovelGenerator

# 3. 创建功能分支
git checkout -b feature/新功能名称

# 4. 进行开发
# ... 编写代码 ...

# 5. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 6. 推送到你的Fork
git push origin feature/新功能名称

# 7. 创建Pull Request
```

### 2. 提交信息规范
```
类型(范围): 简短描述

详细描述（可选）

相关Issue: #123
```

**提交类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 3. Pull Request规范
- **标题**: 简洁描述更改内容
- **描述**: 详细说明更改原因和内容
- **测试**: 说明如何测试更改
- **文档**: 更新相关文档
- **向后兼容**: 说明是否影响现有功能

### 4. 代码审查要点
- **功能正确性**: 代码是否实现预期功能
- **代码质量**: 是否遵循项目规范
- **性能影响**: 是否影响系统性能
- **安全性**: 是否存在安全隐患
- **测试覆盖**: 是否有足够的测试
- **文档完整**: 是否更新相关文档

## 🔍 调试技巧

### 1. 日志调试
```python
import logging

# 设置详细日志级别
logging.basicConfig(level=logging.DEBUG)

# 在关键位置添加日志
logging.debug(f"函数参数: {param}")
logging.info(f"处理进度: {progress}")
logging.warning(f"潜在问题: {issue}")
logging.error(f"错误信息: {error}")
```

### 2. 异常处理调试
```python
import traceback

try:
    risky_operation()
except Exception as e:
    # 打印完整堆栈信息
    logging.error(f"异常详情: {e}")
    logging.error(traceback.format_exc())
    
    # 在开发环境中重新抛出异常
    if DEBUG_MODE:
        raise
```

### 3. 性能调试
```python
import time
from functools import wraps

def timing_decorator(func):
    """性能计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} 执行时间: {end_time - start_time:.2f}秒")
        return result
    return wrapper

@timing_decorator
def slow_function():
    # 需要性能监控的函数
    pass
```

### 4. 内存调试
```python
import psutil
import os

def log_memory_usage(func_name: str):
    """记录内存使用情况"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{func_name} 内存使用: {memory_info.rss / 1024 / 1024:.2f} MB")
```

## 📚 学习资源

### 1. 技术文档
- [CustomTkinter文档](https://customtkinter.tomschimansky.com/)
- [LangChain文档](https://python.langchain.com/)
- [ChromaDB文档](https://docs.trychroma.com/)
- [Sentence Transformers文档](https://www.sbert.net/)

### 2. 相关技术
- **GUI开发**: Tkinter, CustomTkinter
- **LLM集成**: OpenAI API, LangChain
- **向量数据库**: ChromaDB, Faiss
- **文本处理**: NLTK, spaCy
- **机器学习**: Transformers, Sentence Transformers

### 3. 最佳实践
- **设计模式**: 适配器模式、工厂模式、观察者模式
- **代码质量**: Clean Code, SOLID原则
- **测试驱动**: TDD, BDD
- **版本控制**: Git Flow, GitHub Flow

## ❓ 常见问题

### Q: 如何添加新的LLM服务支持？
A: 参考"扩展开发指南"中的LLM适配器添加步骤，主要需要实现`BaseLLMAdapter`接口。

### Q: 如何调试生成质量问题？
A: 1) 检查提示词模板 2) 调整模型参数 3) 查看日志输出 4) 使用一致性检查功能

### Q: 如何优化生成速度？
A: 1) 选择更快的模型 2) 调整max_tokens参数 3) 使用本地模型 4) 优化提示词长度

### Q: 如何处理API限流问题？
A: 项目已内置重试机制，可在`common.py`中调整重试参数和延迟时间。

### Q: 如何贡献代码？
A: 遵循贡献指南，创建功能分支，编写测试，提交Pull Request。

---

**感谢你对AI小说生成器项目的贡献！** 🎉

如有任何问题，欢迎在GitHub Issues中提出或联系项目维护者。