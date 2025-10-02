# ⚙️ 配置说明文档

## 📋 概述

本文档详细说明AI小说生成器的所有配置参数，帮助你优化生成效果和系统性能。

## 📁 配置文件结构

配置信息保存在 `config.json` 文件中，主要包含以下几个部分：

```json
{
  "last_interface_format": "OpenAI",
  "last_embedding_interface_format": "OpenAI", 
  "llm_configs": {...},
  "embedding_configs": {...},
  "other_params": {...},
  "choose_configs": {...},
  "proxy_setting": {...},
  "webdav_config": {...}
}
```

## 🤖 LLM配置 (llm_configs)

### 配置结构
```json
{
  "llm_configs": {
    "配置名称": {
      "api_key": "API密钥",
      "base_url": "接口地址", 
      "model_name": "模型名称",
      "temperature": 0.7,
      "max_tokens": 8192,
      "timeout": 600,
      "interface_format": "接口格式"
    }
  }
}
```

### 参数详解

#### api_key (API密钥)
- **作用**: 访问LLM服务的认证密钥
- **格式**: 字符串，通常以 `sk-` 开头
- **获取方式**:
  - OpenAI: https://platform.openai.com/api-keys
  - DeepSeek: https://platform.deepseek.com/api_keys
  - Google AI: https://aistudio.google.com/app/apikey

#### base_url (接口地址)
- **作用**: LLM服务的API端点地址
- **常用地址**:
  ```
  OpenAI官方: https://api.openai.com/v1
  DeepSeek: https://api.deepseek.com/v1
  Google Gemini: https://generativelanguage.googleapis.com/v1beta/openai
  本地Ollama: http://localhost:11434/v1
  ```

#### model_name (模型名称)
- **作用**: 指定要使用的具体模型
- **常用模型**:
  ```
  OpenAI: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
  DeepSeek: deepseek-chat, deepseek-coder
  Gemini: gemini-2.5-pro, gemini-1.5-flash
  本地: llama2, qwen, chatglm等
  ```

#### temperature (温度参数)
- **作用**: 控制生成文本的随机性和创造性
- **取值范围**: 0.0 - 2.0
- **推荐设置**:
  ```
  0.1-0.3: 逻辑性强，适合推理、分析
  0.5-0.7: 平衡创意和逻辑，适合一般写作
  0.8-1.2: 创意性强，适合描写、对话
  1.3-2.0: 高度随机，适合头脑风暴
  ```

#### max_tokens (最大输出长度)
- **作用**: 限制单次生成的最大token数量
- **推荐设置**:
  ```
  2048: 短篇内容，快速生成
  4096: 中等长度，平衡质量和速度
  8192: 长篇内容，高质量生成
  16384+: 超长内容，需要强大模型支持
  ```

#### timeout (超时时间)
- **作用**: API调用的最大等待时间（秒）
- **推荐设置**:
  ```
  300: 快速生成，适合短内容
  600: 标准设置，适合大多数情况
  1200: 长时间生成，适合复杂内容
  ```

### 预设配置示例

#### DeepSeek配置（推荐）
```json
{
  "DeepSeek V3": {
    "api_key": "sk-xxxxxxxx",
    "base_url": "https://api.deepseek.com/v1",
    "model_name": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 8192,
    "timeout": 600,
    "interface_format": "OpenAI"
  }
}
```

#### OpenAI配置
```json
{
  "GPT-4o": {
    "api_key": "sk-xxxxxxxx", 
    "base_url": "https://api.openai.com/v1",
    "model_name": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 8192,
    "timeout": 600,
    "interface_format": "OpenAI"
  }
}
```

#### 本地Ollama配置
```json
{
  "本地Llama": {
    "api_key": "",
    "base_url": "http://localhost:11434/v1",
    "model_name": "llama2",
    "temperature": 0.8,
    "max_tokens": 4096,
    "timeout": 1200,
    "interface_format": "Ollama"
  }
}
```

## 🔍 Embedding配置 (embedding_configs)

### 配置结构
```json
{
  "embedding_configs": {
    "OpenAI": {
      "api_key": "API密钥",
      "base_url": "接口地址",
      "model_name": "模型名称", 
      "retrieval_k": 4,
      "interface_format": "OpenAI"
    }
  }
}
```

### 参数详解

#### retrieval_k (检索数量)
- **作用**: 从知识库检索的相关文档数量
- **取值范围**: 1-10
- **推荐设置**:
  ```
  2-3: 精确检索，减少噪音
  4-5: 标准设置，平衡相关性
  6-8: 广泛检索，增加上下文
  ```

### 常用Embedding模型
```
OpenAI: text-embedding-ada-002, text-embedding-3-small
本地: nomic-embed-text, bge-large-zh
多语言: multilingual-e5-large
```

## 📝 小说参数配置 (other_params)

### 配置结构
```json
{
  "other_params": {
    "topic": "小说主题",
    "genre": "小说类型", 
    "num_chapters": 50,
    "word_number": 3000,
    "filepath": "输出路径",
    "chapter_num": "120",
    "user_guidance": "内容指导",
    "characters_involved": "涉及角色",
    "key_items": "关键物品",
    "scene_location": "场景地点", 
    "time_constraint": "时间限制"
  }
}
```

### 参数详解

#### topic (小说主题)
- **作用**: 小说的核心主题和故事概念
- **示例**:
  ```
  "一个程序员穿越到修仙世界的冒险故事"
  "现代都市中隐藏的超能力者组织"
  "星际殖民时代的政治阴谋"
  ```

#### genre (小说类型)
- **作用**: 小说的文学类型，影响写作风格
- **常用类型**:
  ```
  玄幻: 修仙、魔法、异世界
  科幻: 未来科技、太空、AI
  都市: 现代生活、职场、情感
  历史: 古代背景、历史人物
  悬疑: 推理、犯罪、惊悚
  ```

#### num_chapters (章节数量)
- **作用**: 计划的总章节数
- **建议**:
  ```
  短篇: 10-30章
  中篇: 50-100章  
  长篇: 100-300章
  超长篇: 300+章
  ```

#### word_number (单章字数)
- **作用**: 每章的目标字数
- **建议**:
  ```
  1500-2000: 快节奏，适合网文
  2500-3500: 标准长度，平衡节奏
  4000-6000: 详细描写，传统小说
  ```

#### user_guidance (内容指导)
- **作用**: 对AI生成内容的具体要求
- **示例**:
  ```
  "注重角色心理描写，避免过于血腥的场面"
  "增加幽默元素，保持轻松的氛围"
  "重点描写战斗技巧，体现主角成长"
  ```

## 🎯 生成配置选择 (choose_configs)

### 配置结构
```json
{
  "choose_configs": {
    "architecture_llm": "架构生成使用的LLM",
    "chapter_outline_llm": "章节大纲使用的LLM", 
    "final_chapter_llm": "最终章节使用的LLM",
    "consistency_review_llm": "一致性检查使用的LLM",
    "prompt_draft_llm": "草稿生成使用的LLM"
  }
}
```

### 推荐配置策略

#### 高质量配置
```json
{
  "architecture_llm": "GPT-4o",
  "chapter_outline_llm": "GPT-4o", 
  "final_chapter_llm": "GPT-4o",
  "consistency_review_llm": "DeepSeek V3",
  "prompt_draft_llm": "DeepSeek V3"
}
```

#### 性价比配置
```json
{
  "architecture_llm": "Gemini 2.5 Pro",
  "chapter_outline_llm": "DeepSeek V3",
  "final_chapter_llm": "DeepSeek V3", 
  "consistency_review_llm": "DeepSeek V3",
  "prompt_draft_llm": "DeepSeek V3"
}
```

#### 本地化配置
```json
{
  "architecture_llm": "本地Llama",
  "chapter_outline_llm": "本地Llama",
  "final_chapter_llm": "本地Llama",
  "consistency_review_llm": "本地Llama", 
  "prompt_draft_llm": "本地Llama"
}
```

## 🌐 网络配置

### 代理设置 (proxy_setting)
```json
{
  "proxy_setting": {
    "proxy_url": "127.0.0.1",
    "proxy_port": "7890", 
    "enabled": false
  }
}
```

#### 使用场景
- 国内访问OpenAI等海外服务
- 企业网络环境
- 提高连接稳定性

### WebDAV配置 (webdav_config)
```json
{
  "webdav_config": {
    "webdav_url": "https://dav.jianguoyun.com/dav/",
    "webdav_username": "用户名",
    "webdav_password": "密码"
  }
}
```

#### 用途
- 云端同步配置文件
- 多设备协作创作
- 自动备份小说内容

## 🔧 高级配置技巧

### 1. 多模型协作策略
```
架构设计: 使用逻辑性强的模型 (GPT-4)
内容生成: 使用创意性强的模型 (Claude/Gemini)
一致性检查: 使用成本较低的模型 (DeepSeek)
```

### 2. 参数动态调整
```python
# 不同类型内容使用不同温度
对话场景: temperature = 0.8-1.0
动作场景: temperature = 0.6-0.8  
心理描写: temperature = 0.7-0.9
逻辑推理: temperature = 0.3-0.5
```

### 3. 性能优化配置
```
并发控制: 避免同时调用多个高成本模型
缓存策略: 重复内容使用本地缓存
批量处理: 合并相似的生成任务
```

### 4. 成本控制策略
```
预算分配: 70%用于内容生成，30%用于优化
模型选择: 核心内容用高端模型，辅助内容用经济模型
token管理: 设置合理的max_tokens避免浪费
```

## ⚠️ 配置注意事项

### 1. 安全性
- **API密钥保护**: 不要在公共场所展示config.json
- **定期更换**: 建议定期更换API密钥
- **权限控制**: 使用最小权限原则

### 2. 兼容性
- **模型版本**: 注意模型的更新和废弃
- **接口变更**: 关注服务商的API变更通知
- **格式标准**: 严格按照JSON格式编写配置

### 3. 性能监控
- **响应时间**: 监控API调用的响应时间
- **成功率**: 记录API调用的成功率
- **成本统计**: 跟踪API使用成本

### 4. 备份恢复
- **配置备份**: 定期备份config.json文件
- **版本管理**: 为不同版本的配置做好标记
- **快速恢复**: 准备默认配置模板

## 📊 配置模板

### 新手推荐配置
```json
{
  "last_interface_format": "DeepSeek",
  "llm_configs": {
    "DeepSeek": {
      "api_key": "你的API密钥",
      "base_url": "https://api.deepseek.com/v1",
      "model_name": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 4096,
      "timeout": 600,
      "interface_format": "OpenAI"
    }
  },
  "other_params": {
    "num_chapters": 30,
    "word_number": 2500
  }
}
```

### 专业作者配置
```json
{
  "choose_configs": {
    "architecture_llm": "GPT-4o",
    "chapter_outline_llm": "GPT-4o",
    "final_chapter_llm": "Claude-3.5",
    "consistency_review_llm": "DeepSeek V3",
    "prompt_draft_llm": "Gemini 2.5 Pro"
  }
}
```

---

*通过合理的配置，你可以显著提升AI小说生成的质量和效率！*