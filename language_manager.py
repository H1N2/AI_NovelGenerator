# language_manager.py
"""
多语言管理器
负责应用程序的多语言配置和翻译功能
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class LanguageManager:
    """多语言管理器"""
    
    def __init__(self, languages_dir: str = "languages", default_language: str = "zh_CN"):
        """
        初始化语言管理器
        
        Args:
            languages_dir: 语言文件目录
            default_language: 默认语言代码
        """
        self.languages_dir = Path(languages_dir)
        self.default_language = default_language
        self.current_language = default_language
        
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_languages: Dict[str, str] = {
            "zh_CN": "简体中文",
            "en_US": "English"
        }
        
        # 确保语言目录存在
        self.languages_dir.mkdir(exist_ok=True)
        
        # 加载所有可用语言
        self._load_all_languages()
    
    def _load_all_languages(self):
        """加载所有可用的语言文件"""
        for lang_code in self.available_languages.keys():
            self._load_language(lang_code)
    
    def _load_language(self, language_code: str) -> bool:
        """
        加载指定语言的翻译文件
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否加载成功
        """
        try:
            lang_file = self.languages_dir / f"{language_code}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[language_code] = json.load(f)
                return True
            else:
                # 如果文件不存在，创建空的翻译字典
                self.translations[language_code] = {}
                return False
        except Exception as e:
            print(f"加载语言文件失败 {language_code}: {e}")
            self.translations[language_code] = {}
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        设置当前语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否设置成功
        """
        if language_code in self.available_languages:
            self.current_language = language_code
            return True
        return False
    
    def get_current_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取所有可用语言"""
        return self.available_languages.copy()
    
    def translate(self, key: str, **kwargs) -> str:
        """
        翻译指定的键
        
        Args:
            key: 翻译键，支持点分隔的嵌套键如 'ui.buttons.save'
            **kwargs: 用于格式化字符串的参数
            
        Returns:
            str: 翻译后的文本
        """
        # 获取当前语言的翻译
        current_translations = self.translations.get(self.current_language, {})
        
        # 支持嵌套键
        keys = key.split('.')
        value = current_translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 如果当前语言没有翻译，尝试使用默认语言
                if self.current_language != self.default_language:
                    default_translations = self.translations.get(self.default_language, {})
                    value = default_translations
                    for k in keys:
                        if isinstance(value, dict) and k in value:
                            value = value[k]
                        else:
                            # 如果默认语言也没有，返回键本身
                            return key
                else:
                    return key
                break
        
        # 如果找到了翻译文本
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        
        return key
    
    def t(self, key: str, **kwargs) -> str:
        """translate方法的简写"""
        return self.translate(key, **kwargs)
    
    def add_translation(self, language_code: str, key: str, value: str):
        """
        添加翻译
        
        Args:
            language_code: 语言代码
            key: 翻译键
            value: 翻译值
        """
        if language_code not in self.translations:
            self.translations[language_code] = {}
        
        # 支持嵌套键
        keys = key.split('.')
        current_dict = self.translations[language_code]
        
        for k in keys[:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]
        
        current_dict[keys[-1]] = value
    
    def save_language_file(self, language_code: str) -> bool:
        """
        保存语言文件
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否保存成功
        """
        try:
            lang_file = self.languages_dir / f"{language_code}.json"
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.translations.get(language_code, {}), 
                    f, 
                    ensure_ascii=False, 
                    indent=2
                )
            return True
        except Exception as e:
            print(f"保存语言文件失败 {language_code}: {e}")
            return False
    
    def reload_language(self, language_code: str) -> bool:
        """
        重新加载语言文件
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否重新加载成功
        """
        return self._load_language(language_code)


# 全局语言管理器实例
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """获取全局语言管理器实例"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def t(key: str, **kwargs) -> str:
    """全局翻译函数"""
    return get_language_manager().translate(key, **kwargs)


def set_language(language_code: str) -> bool:
    """设置全局语言"""
    return get_language_manager().set_language(language_code)


def get_current_language() -> str:
    """获取当前语言"""
    return get_language_manager().get_current_language()


def get_available_languages() -> Dict[str, str]:
    """获取可用语言列表"""
    return get_language_manager().get_available_languages()