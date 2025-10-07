# 翻译键参考手册

本文档列出了当前系统中所有可用的翻译键，方便开发人员查找和使用。

## 应用程序 (app)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `app.title` | AI小说生成器 | AI Novel Generator | 应用程序标题 |

## 菜单 (menus)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `menus.settings` | 设置 | Settings | 设置菜单 |
| `menus.language` | 语言 | Language | 语言菜单 |
| `menus.chinese` | 中文 | Chinese | 中文选项 |
| `menus.english` | English | English | 英文选项 |

## 选项卡 (tabs)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `tabs.main_functions` | 主要功能 | Main Functions | 主功能选项卡 |
| `tabs.config` | 配置 | Config | 配置选项卡 |
| `tabs.chapters_manage` | 章节管理 | Chapters Manage | 章节管理选项卡 |

## 按钮 (buttons)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `buttons.prev_chapter` | << 上一章 | << Previous | 上一章按钮 |
| `buttons.next_chapter` | 下一章 >> | Next >> | 下一章按钮 |
| `buttons.save_changes` | 保存修改 | Save Changes | 保存修改按钮 |
| `buttons.refresh_chapters` | 刷新章节列表 | Refresh Chapters List | 刷新章节列表按钮 |

## 标签 (labels)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `labels.word_count` | 字数 | Word Count | 字数标签 |
| `labels.parameter_description` | 参数说明 | Parameter Description | 参数说明标签 |

## 消息 (messages)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `messages.no_description` | 暂无说明 | No description | 无说明时的提示 |
| `messages.language_switched` | 语言已切换 | Language switched | 语言切换成功提示 |

## 配置 (config)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `config.llm_model_settings` | LLM Model settings | LLM Model settings | LLM模型设置 |
| `config.embedding_settings` | Embedding settings | Embedding settings | 嵌入设置 |
| `config.config_choose` | Config choose | Config choose | 配置选择 |

## 角色 (character)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `character.library_management` | 角色库管理 | Character Library Management | 角色库管理窗口标题 |

## 插件 (plugin)

| 键 | 中文 | 英文 | 用途 |
|---|---|---|---|
| `plugin.manager_title` | 插件系统管理 | Plugin System Management | 插件管理器标题 |
| `plugin.load` | 加载 | Load | 加载插件 |
| `plugin.unload` | 卸载 | Unload | 卸载插件 |
| `plugin.reload` | 重载 | Reload | 重载插件 |
| `plugin.performance` | 性能 | Performance | 性能监控 |
| `plugin.logs` | 日志 | Logs | 日志查看 |

## 使用示例

```python
from language_manager import t

# 使用现有翻译键
title = t("app.title")
save_btn_text = t("buttons.save_changes")
word_count_label = t("labels.word_count")

# 在UI组件中使用
window.title(t("character.library_management"))
button = ctk.CTkButton(parent, text=t("buttons.refresh_chapters"))
```

## 添加新翻译键

当需要添加新的翻译键时：

1. **选择合适的分类**：根据用途选择 `app`、`buttons`、`labels` 等分类
2. **遵循命名规范**：使用小写字母和下划线，保持语义清晰
3. **同时更新两个文件**：`zh_CN.json` 和 `en_US.json`
4. **更新本文档**：在对应分类中添加新的翻译键

## 注意事项

- 所有翻译键都区分大小写
- 使用不存在的翻译键会返回键名本身
- 建议在添加新UI元素前先检查是否有可复用的翻译键
- 保持中英文翻译的一致性和准确性

---

**更新日期**: 2024年12月
**版本**: 1.0