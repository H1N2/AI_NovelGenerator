# 多语言支持系统

## 快速使用

### 1. 导入翻译函数
```python
from language_manager import t
```

### 2. 使用翻译
```python
# 替换硬编码文本
button = ctk.CTkButton(parent, text=t("buttons.save"))
window.title(t("app.title"))
```

### 3. 添加新翻译

在 `languages/zh_CN.json` 中添加：
```json
{
  "buttons": {
    "new_button": "新按钮"
  }
}
```

在 `languages/en_US.json` 中添加：
```json
{
  "buttons": {
    "new_button": "New Button"
  }
}
```

## 翻译键规范

- 使用点号分隔：`category.subcategory.key`
- 小写字母和下划线：`buttons.save_changes`
- 语义清晰：`messages.error.file_not_found`

## 常用分类

- `app.*` - 应用程序
- `menus.*` - 菜单
- `tabs.*` - 选项卡
- `buttons.*` - 按钮
- `labels.*` - 标签
- `messages.*` - 消息
- `config.*` - 配置
- `character.*` - 角色
- `plugin.*` - 插件

## 语言切换

通过菜单栏：**设置 → 语言** 进行切换

## 详细文档

完整开发指南请参考：[docs/multi-language-development-guide.md](docs/multi-language-development-guide.md)