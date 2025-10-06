# 插件模板

这是一个完整的插件开发模板，展示了AI小说生成器插件系统的所有核心功能。

## 功能特性

- **完整的插件生命周期管理**
- **配置管理和验证**
- **事件系统集成**
- **日志记录**
- **服务提供**
- **错误处理和崩溃恢复**
- **性能监控**

## 使用方法

### 1. 复制模板

```bash
cp -r plugins/template plugins/your_plugin_name
```

### 2. 修改配置

编辑 `plugin.json` 文件：

```json
{
    "name": "your_plugin_name",
    "version": "1.0.0",
    "description": "你的插件描述",
    "author": "你的名字"
}
```

### 3. 实现功能

在 `main.py` 中实现你的插件逻辑：

```python
class YourPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "your_plugin_name"
        # 其他初始化代码
```

### 4. 配置服务

实现 `get_services()` 方法：

```python
def get_services(self):
    return {
        'your_service': self.your_service_method
    }
```

## 模板结构

```
template/
├── plugin.json      # 插件配置
├── main.py         # 主插件文件
├── config.json     # 默认配置
├── README.md       # 说明文档
└── tests/          # 测试文件（可选）
```

## 核心方法

### 必需方法

- `initialize()`: 插件初始化
- `cleanup()`: 插件清理
- `get_services()`: 返回提供的服务

### 可选方法

- `load_config()`: 加载配置
- `save_config()`: 保存配置
- `validate_config()`: 验证配置
- `register_event_handlers()`: 注册事件处理器

## 事件处理

```python
def register_event_handlers(self):
    self.register_event_handler(
        AppEvents.NOVEL_GENERATION_START,
        self.on_novel_generation_start,
        priority=EventPriority.NORMAL
    )

def on_novel_generation_start(self, event):
    self.logger.info(f"小说生成开始: {event.data}")
```

## 服务实现

```python
def process_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
    try:
        # 处理逻辑
        result = self.do_processing(text, options)
        return {'success': True, 'result': result}
    except Exception as e:
        self.logger.error(f"处理失败: {e}")
        return {'success': False, 'error': str(e)}
```

## 配置管理

插件支持动态配置更新：

```python
def configure(self, new_config: Dict[str, Any]) -> bool:
    if self.validate_config(new_config):
        self.config.update(new_config)
        self.save_config()
        return True
    return False
```

## 日志记录

使用插件专用日志器：

```python
self.logger.info("信息日志")
self.logger.warning("警告日志")
self.logger.error("错误日志")
self.logger.debug("调试日志")
```

## 错误处理

插件系统提供自动崩溃恢复：

```python
def risky_operation(self):
    try:
        # 可能出错的操作
        return self.do_something()
    except Exception as e:
        self.logger.error(f"操作失败: {e}")
        raise  # 让系统处理崩溃
```

## 测试

创建测试文件 `tests/test_plugin.py`：

```python
import unittest
from unittest.mock import Mock
from main import TemplatePlugin

class TestTemplatePlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = TemplatePlugin()
        self.plugin.logger = Mock()
        
    def test_initialization(self):
        result = self.plugin.initialize()
        self.assertTrue(result)
```

## 部署

1. 将插件文件夹放入 `plugins/` 目录
2. 重启应用或重新加载插件
3. 检查插件状态和日志

## 最佳实践

1. **错误处理**: 总是处理可能的异常
2. **日志记录**: 记录重要操作和错误
3. **配置验证**: 验证用户配置的有效性
4. **资源清理**: 在 `cleanup()` 中释放资源
5. **性能优化**: 使用缓存和批处理
6. **文档完善**: 提供清晰的使用说明

## 支持

如有问题，请查看：
- 插件开发指南
- 系统日志
- 示例插件