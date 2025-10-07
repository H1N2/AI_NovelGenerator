# 多语言开发指南

本文档为开发人员提供在AI小说生成器中实现多语言支持的详细指南。

## 目录
- [概述](#概述)
- [语言管理器架构](#语言管理器架构)
- [快速开始](#快速开始)
- [翻译文件管理](#翻译文件管理)
- [UI组件多语言化](#ui组件多语言化)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

## 概述

多语言支持系统基于 `language_manager.py` 模块实现，提供了：
- 动态语言切换
- 嵌套翻译键支持
- 默认语言回退机制
- 全局访问接口

## 语言管理器架构

### 核心组件

```python
# language_manager.py
class LanguageManager:
    def __init__(self, default_language='zh_CN')
    def load_language(self, language_code)
    def set_language(self, language_code)
    def translate(self, key, **kwargs)
    def get_current_language(self)
    def get_available_languages(self)
```

### 全局访问函数

```python
# 获取语言管理器实例
get_language_manager() -> LanguageManager

# 翻译文本（推荐使用）
t(key: str, **kwargs) -> str
```

## 快速开始

### 1. 导入多语言支持

在需要多语言支持的UI文件中导入：

```python
from language_manager import t
```

### 2. 使用翻译函数

```python
# 简单翻译
title = t("app.title")

# 嵌套键翻译
button_text = t("buttons.save_changes")

# 带参数的翻译（未来扩展）
message = t("messages.welcome", name="用户名")
```

### 3. 在UI组件中应用

```python
# 窗口标题
self.window.title(t("character.library_management"))

# 按钮文本
save_btn = ctk.CTkButton(parent, text=t("buttons.save"))

# 标签文本
label = ctk.CTkLabel(parent, text=t("labels.word_count"))
```

## 翻译文件管理

### 文件结构

```
languages/
├── zh_CN.json  # 中文翻译
└── en_US.json  # 英文翻译
```

### 翻译文件格式

```json
{
  "app": {
    "title": "小说生成器"
  },
  "buttons": {
    "save": "保存",
    "cancel": "取消"
  },
  "messages": {
    "success": "成功",
    "error": "错误"
  }
}
```

### 添加新翻译

1. **在中文文件中添加**（`languages/zh_CN.json`）：
```json
{
  "new_feature": {
    "title": "新功能",
    "description": "这是一个新功能"
  }
}
```

2. **在英文文件中添加对应翻译**（`languages/en_US.json`）：
```json
{
  "new_feature": {
    "title": "New Feature",
    "description": "This is a new feature"
  }
}
```

## UI组件多语言化

### 标准流程

1. **导入翻译函数**
```python
from language_manager import t
```

2. **替换硬编码文本**
```python
# 之前
button = ctk.CTkButton(parent, text="保存修改")

# 之后
button = ctk.CTkButton(parent, text=t("buttons.save_changes"))
```

3. **动态更新文本**
```python
def update_word_count(self, count):
    self.word_count_label.configure(text=f"{t('labels.word_count')}: {count}")
```

### 常见UI元素示例

#### 窗口标题
```python
self.window.title(t("plugin.manager_title"))
```

#### 选项卡标题
```python
self.tab = self.tabview.add(t("tabs.main_functions"))
```

#### 按钮文本
```python
prev_btn = ctk.CTkButton(frame, text=t("buttons.prev_chapter"))
next_btn = ctk.CTkButton(frame, text=t("buttons.next_chapter"))
```

#### 标签文本
```python
label = ctk.CTkLabel(frame, text=t("labels.chapter_content"))
```

#### 消息框
```python
messagebox.showinfo(t("messages.success"), t("messages.save_completed"))
```

## 最佳实践

### 1. 翻译键命名规范

- 使用点号分隔的层级结构
- 使用小写字母和下划线
- 保持语义清晰

```python
# 推荐
t("buttons.save_changes")
t("messages.error.file_not_found")
t("config.llm_settings")

# 不推荐
t("SaveButton")
t("error1")
t("llm-config")
```

### 2. 翻译键分类

```json
{
  "app": {},           // 应用程序级别
  "menus": {},         // 菜单项
  "tabs": {},          // 选项卡
  "buttons": {},       // 按钮
  "labels": {},        // 标签
  "messages": {},      // 消息提示
  "tooltips": {},      // 工具提示
  "status": {},        // 状态信息
  "config": {},        // 配置相关
  "generation": {},    // 生成相关
  "novel": {},         // 小说相关
  "character": {},     // 角色相关
  "plugin": {}         // 插件相关
}
```

### 3. 代码组织

```python
class MyUIComponent:
    def __init__(self):
        # 在初始化时导入
        from language_manager import t
        self.t = t
        
    def create_ui(self):
        # 使用实例方法
        button = ctk.CTkButton(parent, text=self.t("buttons.save"))
```

### 4. 语言切换响应

如果UI需要响应语言切换，实现刷新方法：

```python
def refresh_ui_language(self):
    """刷新UI语言显示"""
    self.window.title(t("window.title"))
    self.save_button.configure(text=t("buttons.save"))
    # ... 更新其他UI元素
```

## 常见问题

### Q: 如何添加新的语言？

A: 
1. 在 `languages/` 目录下创建新的JSON文件，如 `ja_JP.json`
2. 复制现有翻译文件的结构，翻译所有文本
3. 语言管理器会自动检测并加载新语言

### Q: 翻译键不存在时会发生什么？

A: 系统会返回翻译键本身，并在控制台输出警告信息。例如：
```python
t("non.existent.key")  # 返回 "non.existent.key"
```

### Q: 如何处理带参数的翻译？

A: 当前版本支持基础的参数传递（预留接口）：
```python
# 翻译文件中
"welcome_message": "欢迎 {name} 使用系统"

# 代码中
message = t("welcome_message", name="张三")
```

### Q: 如何在运行时切换语言？

A: 使用语言管理器的方法：
```python
from language_manager import get_language_manager

manager = get_language_manager()
manager.set_language("en_US")  # 切换到英文
```

### Q: 如何获取当前可用的语言列表？

A: 
```python
from language_manager import get_language_manager

manager = get_language_manager()
languages = manager.get_available_languages()
print(languages)  # ['zh_CN', 'en_US']
```

## 开发检查清单

在为新UI组件添加多语言支持时，请检查：

- [ ] 已导入 `from language_manager import t`
- [ ] 所有硬编码文本已替换为 `t()` 调用
- [ ] 翻译键遵循命名规范
- [ ] 中英文翻译文件都已更新
- [ ] 动态文本更新正确使用翻译函数
- [ ] 测试语言切换功能正常

## 示例代码

完整的UI组件多语言化示例：

```python
# ui/example_tab.py
import customtkinter as ctk
from language_manager import t

def build_example_tab(self):
    # 创建选项卡
    self.example_tab = self.tabview.add(t("tabs.example"))
    
    # 创建按钮
    save_btn = ctk.CTkButton(
        self.example_tab, 
        text=t("buttons.save"),
        command=self.save_data
    )
    
    # 创建标签
    status_label = ctk.CTkLabel(
        self.example_tab,
        text=t("status.ready")
    )
    
    # 动态更新文本
    def update_status(self, new_status):
        self.status_label.configure(text=t(f"status.{new_status}"))
```

---

**注意**: 本文档会随着多语言系统的更新而持续完善。如有疑问，请参考 `language_manager.py` 源码或联系开发团队。