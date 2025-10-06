# AI小说生成器插件开发指南

## 概述

本指南将帮助你开发AI小说生成器的插件。插件系统提供了强大的扩展能力，包括崩溃处理、日志记录、事件系统等功能。

## 插件基础结构

### 1. 插件类定义

```python
from plugins.base import BasePlugin
from plugins import LogLevel, EventPriority

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "my_plugin"
        self.version = "1.0.0"
        self.description = "我的示例插件"
        self.author = "开发者姓名"
        
    def initialize(self):
        """插件初始化"""
        self.logger.info("插件初始化完成")
        return True
        
    def cleanup(self):
        """插件清理"""
        self.logger.info("插件清理完成")
        
    def get_services(self):
        """返回插件提供的服务"""
        return {
            'my_service': self.my_service_method
        }
```

### 2. 插件配置文件 (plugin.json)

```json
{
    "name": "my_plugin",
    "version": "1.0.0",
    "description": "我的示例插件",
    "author": "开发者姓名",
    "main": "main.py",
    "dependencies": [],
    "permissions": ["file_access", "network_access"],
    "config": {
        "enabled": true,
        "auto_start": true
    }
}
```

## 核心功能使用

### 1. 日志记录

```python
# 使用插件专用日志器
self.logger.info("信息日志")
self.logger.warning("警告日志")
self.logger.error("错误日志")
self.logger.debug("调试日志")

# 带上下文的日志
self.logger.info("处理文件", extra={
    'file_path': '/path/to/file',
    'operation': 'read'
})
```

### 2. 事件系统

```python
from plugins.events import AppEvents, EventPriority

# 注册事件处理器
def on_novel_generation_start(self, event):
    self.logger.info(f"小说生成开始: {event.data}")

self.register_event_handler(
    AppEvents.NOVEL_GENERATION_START,
    self.on_novel_generation_start,
    priority=EventPriority.NORMAL
)

# 发送事件
self.emit_event(AppEvents.PLUGIN_STATUS_CHANGED, {
    'plugin_name': self.name,
    'status': 'active'
})
```

### 3. 崩溃处理

```python
# 插件会自动处理崩溃，但你可以手动处理
try:
    # 可能出错的代码
    risky_operation()
except Exception as e:
    self.logger.error(f"操作失败: {e}")
    # 系统会自动记录崩溃并决定是否重启
```

## 插件服务

### 定义服务

```python
def get_services(self):
    return {
        'text_processor': self.process_text,
        'file_handler': self.handle_file,
        'data_analyzer': self.analyze_data
    }

def process_text(self, text, options=None):
    """文本处理服务"""
    self.logger.debug(f"处理文本，长度: {len(text)}")
    # 处理逻辑
    return processed_text
```

### 调用其他插件服务

```python
# 通过插件管理器调用服务
result = self.plugin_manager.call_plugin_service(
    'other_plugin', 
    'service_name', 
    arg1, arg2, 
    keyword_arg=value
)
```

## 配置管理

```python
def load_config(self):
    """加载插件配置"""
    config_path = os.path.join(self.plugin_dir, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    else:
        self.config = self.get_default_config()

def get_default_config(self):
    """返回默认配置"""
    return {
        'enabled': True,
        'max_retries': 3,
        'timeout': 30
    }
```

## 最佳实践

### 1. 错误处理

```python
def safe_operation(self):
    try:
        # 主要逻辑
        result = self.do_something()
        return result
    except FileNotFoundError:
        self.logger.warning("文件未找到，使用默认值")
        return self.get_default_value()
    except Exception as e:
        self.logger.error(f"操作失败: {e}")
        raise  # 让系统处理崩溃
```

### 2. 资源管理

```python
def initialize(self):
    # 初始化资源
    self.connection = self.create_connection()
    self.temp_files = []
    return True

def cleanup(self):
    # 清理资源
    if hasattr(self, 'connection'):
        self.connection.close()
    
    for temp_file in getattr(self, 'temp_files', []):
        try:
            os.remove(temp_file)
        except OSError:
            pass
```

### 3. 性能优化

```python
import time
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(self, param):
    """使用缓存优化性能"""
    start_time = time.time()
    result = self.do_expensive_work(param)
    duration = time.time() - start_time
    
    self.logger.debug(f"操作耗时: {duration:.2f}秒")
    return result
```

## 调试和测试

### 1. 启用调试日志

```python
# 在开发时启用调试日志
self.logger.setLevel(LogLevel.DEBUG)
```

### 2. 单元测试

```python
import unittest
from unittest.mock import Mock, patch

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
        self.plugin.logger = Mock()
        
    def test_initialization(self):
        result = self.plugin.initialize()
        self.assertTrue(result)
        self.plugin.logger.info.assert_called()
```

## 部署和分发

### 1. 插件目录结构

```
my_plugin/
├── plugin.json          # 插件配置
├── main.py             # 主插件文件
├── config.json         # 默认配置
├── requirements.txt    # Python依赖
├── README.md          # 插件说明
└── tests/             # 测试文件
    └── test_plugin.py
```

### 2. 安装插件

1. 将插件文件夹复制到 `plugins/` 目录
2. 重启应用或使用插件管理器重新加载
3. 检查插件状态和日志

## 常见问题

### Q: 插件崩溃后如何恢复？
A: 系统会自动尝试重启插件。如果多次崩溃，插件会被自动禁用。

### Q: 如何调试插件？
A: 启用调试日志，查看插件专用日志文件，使用事件系统监控插件状态。

### Q: 插件间如何通信？
A: 通过服务调用和事件系统进行通信。

### Q: 如何处理插件依赖？
A: 在 `plugin.json` 中声明依赖，系统会按依赖顺序加载插件。

## 示例插件

参考 `examples/` 目录中的示例插件了解具体实现。