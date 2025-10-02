# 📚 API接口文档

## 📋 概述

本文档详细描述了AI小说生成器的核心API接口，包括**LLM适配器**和**Embedding适配器**的使用方法和配置规范。

## 🤖 LLM适配器 (llm_adapters.py)

### 基础接口

#### BaseLLMAdapter
所有LLM适配器的基类，定义了统一的接口规范。

```python
class BaseLLMAdapter:
    """LLM适配器基类"""
    
    def invoke(self, prompt: str) -> str:
        """
        调用LLM生成文本
        
        Args:
            prompt (str): 输入提示词
            
        Returns:
            str: 生成的文本内容
        """
        raise NotImplementedError
```

### 创建适配器

#### create_llm_adapter()
工厂函数，根据配置创建对应的LLM适配器实例。

```python
def create_llm_adapter(
    interface_format: str,  # 接口格式
    base_url: str,         # API基础URL
    model_name: str,       # 模型名称
    api_key: str,          # API密钥
    temperature: float,    # 温度参数 (0.0-2.0)
    max_tokens: int,       # 最大输出token数
    timeout: int           # 超时时间(秒)
) -> BaseLLMAdapter:
```

**支持的interface_format值**:
- `"OpenAI"` - OpenAI兼容接口
- `"DeepSeek"` - DeepSeek接口
- `"Gemini"` - Google Gemini接口
- `"AzureOpenAI"` - Azure OpenAI服务
- `"Ollama"` - 本地Ollama服务
- `"MLStudio"` - Azure ML Studio
- `"AzureAI"` - Azure AI服务
- `"VolcanoEngine"` - 火山引擎
- `"SiliconFlow"` - 硅基流动
- `"Grok"` - xAI Grok

### 具体适配器实现

#### 1. OpenAIAdapter
适配OpenAI官方API和兼容接口。

```python
class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 max_tokens: int, temperature: float = 0.7, 
                 timeout: Optional[int] = 600):
        # 使用langchain的ChatOpenAI
        self._client = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout
        )
```

**配置示例**:
```json
{
  "api_key": "sk-xxx",
  "base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 8192,
  "timeout": 600
}
```

#### 2. DeepSeekAdapter
适配DeepSeek API接口。

```python
class DeepSeekAdapter(BaseLLMAdapter):
    # 实现与OpenAI兼容的接口调用
```

**配置示例**:
```json
{
  "api_key": "sk-xxx",
  "base_url": "https://api.deepseek.com/v1",
  "model_name": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 8192,
  "timeout": 600
}
```

#### 3. GeminiAdapter
适配Google Gemini API。

```python
class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 max_tokens: int, temperature: float = 0.7, 
                 timeout: Optional[int] = 600):
        # 配置Google AI
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name=model_name)
        
    def invoke(self, prompt: str) -> str:
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        response = self._model.generate_content(prompt, generation_config=generation_config)
        return response.text if response and response.text else ""
```

**配置示例**:
```json
{
  "api_key": "AIzaSyXXX",
  "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
  "model_name": "gemini-2.5-pro",
  "temperature": 0.7,
  "max_tokens": 32768,
  "timeout": 600
}
```

#### 4. AzureOpenAIAdapter
适配Azure OpenAI服务。

```python
class AzureOpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 max_tokens: int, temperature: float = 0.7, 
                 timeout: Optional[int] = 600):
        # 解析Azure URL格式
        # https://{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={version}
        self._client = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=deployment,
            openai_api_key=api_key,
            api_version=api_version
        )
```

#### 5. OllamaAdapter
适配本地Ollama服务。

```python
class OllamaAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 max_tokens: int, temperature: float = 0.7, 
                 timeout: Optional[int] = 600):
        # 本地服务，通常不需要API密钥
        self.base_url = base_url  # http://localhost:11434
        self.model_name = model_name  # llama2, qwen等
```

**配置示例**:
```json
{
  "api_key": "",
  "base_url": "http://localhost:11434",
  "model_name": "llama2",
  "temperature": 0.7,
  "max_tokens": 4096,
  "timeout": 600
}
```

## 🔍 Embedding适配器 (embedding_adapters.py)

### 基础接口

#### BaseEmbeddingAdapter
所有Embedding适配器的基类。

```python
class BaseEmbeddingAdapter:
    """Embedding适配器基类"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量文档向量化
        
        Args:
            texts (List[str]): 文档文本列表
            
        Returns:
            List[List[float]]: 向量列表
        """
        raise NotImplementedError
        
    def embed_query(self, query: str) -> List[float]:
        """
        查询文本向量化
        
        Args:
            query (str): 查询文本
            
        Returns:
            List[float]: 向量
        """
        raise NotImplementedError
```

### 创建适配器

#### create_embedding_adapter()
工厂函数，创建Embedding适配器实例。

```python
def create_embedding_adapter(
    interface_format: str,  # 接口格式
    api_key: str,          # API密钥
    base_url: str,         # API基础URL
    model_name: str        # 模型名称
) -> BaseEmbeddingAdapter:
```

**支持的interface_format值**:
- `"OpenAI"` - OpenAI Embedding接口
- `"AzureOpenAI"` - Azure OpenAI Embedding
- `"Ollama"` - 本地Ollama Embedding
- `"MLStudio"` - Azure ML Studio
- `"Gemini"` - Google Gemini Embedding
- `"SiliconFlow"` - 硅基流动

### 具体适配器实现

#### 1. OpenAIEmbeddingAdapter
适配OpenAI Embedding API。

```python
class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self._embedding = OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base=ensure_openai_base_url_has_v1(base_url),
            model=model_name
        )
```

**配置示例**:
```json
{
  "api_key": "sk-xxx",
  "base_url": "https://api.openai.com/v1",
  "model_name": "text-embedding-ada-002",
  "retrieval_k": 4
}
```

#### 2. OllamaEmbeddingAdapter
适配本地Ollama Embedding服务。

```python
class OllamaEmbeddingAdapter(BaseEmbeddingAdapter):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name  # nomic-embed-text等
        self.base_url = base_url      # http://localhost:11434
        
    def _embed_single(self, text: str) -> List[float]:
        # 调用 /api/embeddings 接口
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model_name,
            "prompt": text
        }
        response = requests.post(url, json=payload)
        return response.json().get("embedding", [])
```

#### 3. GeminiEmbeddingAdapter
适配Google Gemini Embedding。

```python
class GeminiEmbeddingAdapter(BaseEmbeddingAdapter):
    def __init__(self, api_key: str, model_name: str, base_url: str):
        self.api_key = api_key
        self.model_name = model_name  # text-embedding-004等
        self.base_url = base_url
        
    def _embed_single(self, text: str) -> List[float]:
        # 调用Google AI Embedding API
        url = f"{self.base_url}/models/{self.model_name}:embedContent"
        # 实现具体的API调用逻辑
```

## 🔧 使用示例

### LLM适配器使用

```python
from llm_adapters import create_llm_adapter

# 创建OpenAI适配器
llm = create_llm_adapter(
    interface_format="OpenAI",
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1",
    model_name="gpt-4o-mini",
    temperature=0.7,
    max_tokens=8192,
    timeout=600
)

# 生成文本
response = llm.invoke("请写一个科幻小说的开头")
print(response)
```

### Embedding适配器使用

```python
from embedding_adapters import create_embedding_adapter

# 创建Embedding适配器
embedding = create_embedding_adapter(
    interface_format="OpenAI",
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1",
    model_name="text-embedding-ada-002"
)

# 文档向量化
texts = ["这是第一个文档", "这是第二个文档"]
doc_embeddings = embedding.embed_documents(texts)

# 查询向量化
query_embedding = embedding.embed_query("搜索相关文档")
```

## 🛠️ 扩展新适配器

### 添加新的LLM适配器

1. **继承BaseLLMAdapter**:
```python
class CustomLLMAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, 
                 max_tokens: int, temperature: float = 0.7, 
                 timeout: Optional[int] = 600):
        # 初始化自定义客户端
        pass
        
    def invoke(self, prompt: str) -> str:
        # 实现具体的API调用逻辑
        pass
```

2. **在create_llm_adapter中添加分支**:
```python
def create_llm_adapter(...):
    if interface_format == "Custom":
        return CustomLLMAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    # ... 其他分支
```

### 添加新的Embedding适配器

1. **继承BaseEmbeddingAdapter**:
```python
class CustomEmbeddingAdapter(BaseEmbeddingAdapter):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # 实现批量向量化
        pass
        
    def embed_query(self, query: str) -> List[float]:
        # 实现单个查询向量化
        pass
```

2. **在create_embedding_adapter中添加分支**:
```python
def create_embedding_adapter(...):
    if interface_format == "Custom":
        return CustomEmbeddingAdapter(api_key, base_url, model_name)
    # ... 其他分支
```

## ⚠️ 注意事项

1. **API密钥安全**: 确保API密钥不被泄露，建议使用环境变量
2. **错误处理**: 所有适配器都应包含完善的异常处理
3. **超时设置**: 合理设置timeout参数，避免长时间等待
4. **URL格式**: 不同服务商的URL格式可能不同，需要正确配置
5. **模型兼容性**: 确认模型名称与服务商支持的模型匹配

## 📊 性能优化建议

1. **连接复用**: 适配器内部应复用HTTP连接
2. **批量处理**: Embedding适配器支持批量向量化以提高效率
3. **缓存机制**: 可在上层实现结果缓存
4. **异步调用**: 对于大量请求，考虑使用异步调用

---

*本文档提供了完整的API接口规范，帮助开发者理解和扩展系统功能。*