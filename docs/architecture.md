# 🏗️ 系统架构文档

## 📋 概述

**AI小说生成器**是一个基于大语言模型的智能小说创作工具，采用**模块化架构**设计，支持多种LLM接口，具备完整的小说生成流水线和一致性检查机制。

## 🛠️ 技术栈

### 核心技术
- **Python 3.9+** - 主要开发语言
- **CustomTkinter** - 现代化GUI框架
- **LangChain** - LLM应用开发框架
- **ChromaDB** - 向量数据库，用于语义检索
- **Sentence Transformers** - 文本嵌入模型

### LLM支持
- **OpenAI GPT系列** (GPT-4, GPT-3.5等)
- **DeepSeek** - 国产大模型
- **Google Gemini** - 谷歌多模态模型
- **本地模型** - 支持Ollama等本地部署方案

### 依赖库
```
langchain>=0.3.27          # LLM应用框架
chromadb>=1.0.20           # 向量数据库
sentence-transformers>=5.1.0  # 文本嵌入
customtkinter>=5.2.2       # GUI框架
openai>=1.106.1            # OpenAI接口
google-generativeai>=0.8.5 # Google AI接口
```

## 🏛️ 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    AI小说生成器                              │
├─────────────────────────────────────────────────────────────┤
│  GUI层 (CustomTkinter)                                      │
│  ├── 主界面 (main_window.py)                                │
│  ├── 配置管理 (config_tab.py)                               │
│  ├── 生成控制 (generation_handlers.py)                      │
│  └── 各功能标签页 (setting_tab, character_tab等)            │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层                                                  │
│  ├── 小说生成器 (novel_generator/)                          │
│  │   ├── 架构生成 (architecture.py)                        │
│  │   ├── 章节蓝图 (blueprint.py)                           │
│  │   ├── 章节生成 (chapter.py)                             │
│  │   └── 最终化处理 (finalization.py)                      │
│  ├── 一致性检查 (consistency_checker.py)                    │
│  └── 知识库管理 (knowledge.py)                              │
├─────────────────────────────────────────────────────────────┤
│  适配器层                                                    │
│  ├── LLM适配器 (llm_adapters.py)                           │
│  └── 嵌入适配器 (embedding_adapters.py)                     │
├─────────────────────────────────────────────────────────────┤
│  基础设施层                                                  │
│  ├── 配置管理 (config_manager.py)                          │
│  ├── 工具函数 (utils.py)                                   │
│  ├── 提示词定义 (prompt_definitions.py)                     │
│  └── 向量存储 (vectorstore_utils.py)                       │
└─────────────────────────────────────────────────────────────┘
```

## 📦 核心模块详解

### 1. GUI层 (`ui/`)
**职责**: 用户界面交互和事件处理

- `main_window.py` - 主窗口管理，整合所有功能模块
- `config_tab.py` - LLM配置界面，支持多种模型配置
- `generation_handlers.py` - 生成任务的UI控制逻辑
- `setting_tab.py` - 小说设定管理界面
- `character_tab.py` - 角色状态追踪界面
- `summary_tab.py` - 全局摘要管理界面

### 2. 小说生成器 (`novel_generator/`)
**职责**: 核心的小说生成逻辑

#### 2.1 架构生成 (`architecture.py`)
```python
def Novel_architecture_generate(
    interface_format: str,    # LLM接口格式
    api_key: str,            # API密钥
    base_url: str,           # 接口地址
    llm_model: str,          # 模型名称
    topic: str,              # 小说主题
    genre: str,              # 小说类型
    number_of_chapters: int, # 章节数量
    word_number: int,        # 字数要求
    filepath: str,           # 输出路径
    user_guidance: str = "", # 用户指导
    **kwargs
) -> None
```

**功能**: 
- 生成小说的整体架构和世界观设定
- 创建主要角色和关系网络
- 规划主要剧情线和冲突设置

#### 2.2 章节蓝图 (`blueprint.py`)
```python
def Chapter_blueprint_generate(
    chapter_num: int,        # 章节编号
    filepath: str,           # 项目路径
    llm_config: dict,        # LLM配置
    **kwargs
) -> None
```

**功能**:
- 基于整体架构生成具体章节大纲
- 确定章节的关键情节点和角色发展
- 维护剧情的连贯性和逻辑性

#### 2.3 章节生成 (`chapter.py`)
**核心函数**:
- `get_last_n_chapters_text()` - 获取前N章内容用于上下文
- `summarize_recent_chapters()` - 总结近期章节要点
- `get_filtered_knowledge_context()` - 从知识库检索相关信息
- `build_chapter_prompt()` - 构建章节生成提示词
- `generate_chapter_draft()` - 生成章节草稿

### 3. 适配器层
**职责**: 统一不同LLM和嵌入模型的接口

#### 3.1 LLM适配器 (`llm_adapters.py`)
```python
def create_llm_adapter(
    interface_format: str,   # 接口格式 (OpenAI/Google/Azure等)
    api_key: str,
    base_url: str,
    model_name: str,
    **kwargs
) -> BaseLLM
```

**支持的接口**:
- OpenAI兼容接口 (OpenAI, DeepSeek, 本地Ollama等)
- Google Generative AI
- Azure OpenAI Service
- 自定义HTTP接口

#### 3.2 嵌入适配器 (`embedding_adapters.py`)
```python
def create_embedding_adapter(
    interface_format: str,
    api_key: str,
    base_url: str,
    model_name: str
) -> BaseEmbeddings
```

### 4. 基础设施层

#### 4.1 配置管理 (`config_manager.py`)
**配置结构**:
```json
{
  "llm_configs": {
    "DeepSeek V3": {
      "api_key": "sk-xxx",
      "base_url": "https://api.deepseek.com/v1",
      "model_name": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 8192,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  },
  "embedding_configs": {...},
  "other_params": {...},
  "choose_configs": {...}
}
```

#### 4.2 向量存储 (`vectorstore_utils.py`)
- 基于ChromaDB实现语义检索
- 支持知识库文档的向量化存储
- 提供相似度搜索和上下文检索

## 🔄 数据流设计

### 小说生成流程
```
用户输入主题 → 架构生成 → 章节蓝图 → 章节生成 → 一致性检查 → 最终化处理
     ↓              ↓           ↓           ↓            ↓            ↓
   参数配置      世界观设定   章节大纲    章节草稿     矛盾检测     成品章节
```

### 数据存储结构
```
项目目录/
├── novel_architecture.txt    # 小说架构
├── chapter_blueprint.txt     # 章节蓝图  
├── character_state.txt       # 角色状态
├── global_summary.txt        # 全局摘要
├── chapters/                 # 章节目录
│   ├── chapter_1.txt
│   ├── chapter_2.txt
│   └── ...
├── knowledge/                # 知识库
└── vectorstore/              # 向量数据库
```

## 🔧 扩展性设计

### 1. LLM接口扩展
通过适配器模式，可轻松添加新的LLM接口：
```python
# 在llm_adapters.py中添加新的适配器
def create_custom_llm_adapter(config):
    # 实现自定义LLM接口
    pass
```

### 2. 生成策略扩展
可在`novel_generator/`目录下添加新的生成策略模块

### 3. UI组件扩展
可在`ui/`目录下添加新的功能标签页

## 🛡️ 安全性考虑

1. **API密钥保护**: 配置文件不包含在版本控制中
2. **输入验证**: 对用户输入进行严格验证
3. **错误处理**: 完善的异常处理和日志记录
4. **代理支持**: 支持HTTP代理配置

## 📊 性能优化

1. **异步处理**: GUI操作与LLM调用分离，避免界面卡顿
2. **缓存机制**: 向量检索结果缓存，减少重复计算
3. **分批处理**: 支持批量章节生成，提高效率
4. **内存管理**: 及时清理大文本对象，控制内存使用

---

*本文档描述了AI小说生成器的核心架构设计，为开发者提供系统性的技术参考。*