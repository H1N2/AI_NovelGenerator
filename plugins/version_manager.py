# plugins/version_manager.py
"""
插件版本兼容性管理模块
提供版本检查、向后兼容处理、版本迁移等功能
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from packaging import version
import json

logger = logging.getLogger(__name__)

class CompatibilityLevel(Enum):
    """兼容性级别"""
    COMPATIBLE = "compatible"           # 完全兼容
    BACKWARD_COMPATIBLE = "backward"    # 向后兼容
    DEPRECATED = "deprecated"           # 已弃用但可用
    INCOMPATIBLE = "incompatible"       # 不兼容

@dataclass
class VersionInfo:
    """版本信息"""
    major: int
    minor: int
    patch: int
    pre_release: Optional[str] = None
    build: Optional[str] = None
    
    @classmethod
    def from_string(cls, version_str: str) -> 'VersionInfo':
        """从版本字符串创建版本信息"""
        try:
            v = version.parse(version_str)
            return cls(
                major=v.major,
                minor=v.minor,
                patch=v.micro,
                pre_release=v.pre if v.pre else None,
                build=v.local if v.local else None
            )
        except Exception as e:
            logger.error(f"解析版本字符串失败: {version_str}, 错误: {e}")
            raise ValueError(f"无效的版本字符串: {version_str}")
    
    def to_string(self) -> str:
        """转换为版本字符串"""
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version_str += f"-{self.pre_release}"
        if self.build:
            version_str += f"+{self.build}"
        return version_str
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, VersionInfo):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, VersionInfo):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other) -> bool:
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        return not self <= other
    
    def __ge__(self, other) -> bool:
        return not self < other

@dataclass
class CompatibilityRule:
    """兼容性规则"""
    min_version: VersionInfo
    max_version: Optional[VersionInfo]
    compatibility_level: CompatibilityLevel
    migration_handler: Optional[Callable] = None
    deprecation_message: Optional[str] = None
    
class VersionCompatibilityManager:
    """版本兼容性管理器"""
    
    def __init__(self, app_version: str):
        self.app_version = VersionInfo.from_string(app_version)
        self._compatibility_rules: Dict[str, List[CompatibilityRule]] = {}
        self._migration_handlers: Dict[str, Dict[str, Callable]] = {}
        self._deprecated_features: Dict[str, Dict[str, str]] = {}
        
        # 设置默认兼容性规则
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认兼容性规则"""
        # 主版本号相同时完全兼容
        # 次版本号向后兼容
        # 修订版本号完全兼容
        pass
    
    def register_compatibility_rule(self, plugin_name: str, rule: CompatibilityRule):
        """注册兼容性规则"""
        if plugin_name not in self._compatibility_rules:
            self._compatibility_rules[plugin_name] = []
        
        self._compatibility_rules[plugin_name].append(rule)
        logger.info(f"为插件 {plugin_name} 注册兼容性规则: {rule}")
    
    def register_migration_handler(self, plugin_name: str, from_version: str, 
                                 to_version: str, handler: Callable):
        """注册版本迁移处理器"""
        if plugin_name not in self._migration_handlers:
            self._migration_handlers[plugin_name] = {}
        
        key = f"{from_version}->{to_version}"
        self._migration_handlers[plugin_name][key] = handler
        logger.info(f"为插件 {plugin_name} 注册迁移处理器: {key}")
    
    def check_compatibility(self, plugin_name: str, plugin_version: str, 
                          required_app_version: str = None) -> Tuple[CompatibilityLevel, str]:
        """检查插件兼容性"""
        try:
            plugin_ver = VersionInfo.from_string(plugin_version)
            required_ver = VersionInfo.from_string(required_app_version) if required_app_version else None
            
            # 检查应用版本要求
            if required_ver and self.app_version < required_ver:
                return (CompatibilityLevel.INCOMPATIBLE, 
                       f"插件要求应用版本 {required_ver}，当前版本 {self.app_version}")
            
            # 检查自定义兼容性规则
            if plugin_name in self._compatibility_rules:
                for rule in self._compatibility_rules[plugin_name]:
                    if self._version_matches_rule(plugin_ver, rule):
                        message = self._get_compatibility_message(rule, plugin_ver)
                        return rule.compatibility_level, message
            
            # 默认兼容性检查
            return self._default_compatibility_check(plugin_ver)
            
        except Exception as e:
            logger.error(f"检查插件 {plugin_name} 兼容性时出错: {e}")
            return CompatibilityLevel.INCOMPATIBLE, f"版本检查失败: {str(e)}"
    
    def _version_matches_rule(self, plugin_version: VersionInfo, rule: CompatibilityRule) -> bool:
        """检查版本是否匹配规则"""
        if plugin_version < rule.min_version:
            return False
        if rule.max_version and plugin_version > rule.max_version:
            return False
        return True
    
    def _get_compatibility_message(self, rule: CompatibilityRule, plugin_version: VersionInfo) -> str:
        """获取兼容性消息"""
        if rule.compatibility_level == CompatibilityLevel.COMPATIBLE:
            return "完全兼容"
        elif rule.compatibility_level == CompatibilityLevel.BACKWARD_COMPATIBLE:
            return "向后兼容，建议更新到最新版本"
        elif rule.compatibility_level == CompatibilityLevel.DEPRECATED:
            return rule.deprecation_message or f"版本 {plugin_version} 已弃用，请尽快更新"
        else:
            return f"版本 {plugin_version} 不兼容"
    
    def _default_compatibility_check(self, plugin_version: VersionInfo) -> Tuple[CompatibilityLevel, str]:
        """默认兼容性检查"""
        app_ver = self.app_version
        
        # 主版本号不同 - 不兼容
        if plugin_version.major != app_ver.major:
            if plugin_version.major < app_ver.major:
                return (CompatibilityLevel.DEPRECATED, 
                       f"插件主版本 {plugin_version.major} 过旧，当前应用版本 {app_ver.major}")
            else:
                return (CompatibilityLevel.INCOMPATIBLE,
                       f"插件主版本 {plugin_version.major} 过新，当前应用版本 {app_ver.major}")
        
        # 次版本号检查
        if plugin_version.minor < app_ver.minor:
            return (CompatibilityLevel.BACKWARD_COMPATIBLE,
                   f"插件次版本 {plugin_version.minor} 较旧，建议更新")
        elif plugin_version.minor > app_ver.minor:
            return (CompatibilityLevel.INCOMPATIBLE,
                   f"插件次版本 {plugin_version.minor} 过新，当前应用版本 {app_ver.minor}")
        
        # 修订版本号 - 完全兼容
        return CompatibilityLevel.COMPATIBLE, "版本完全兼容"
    
    def migrate_plugin_data(self, plugin_name: str, from_version: str, 
                          to_version: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """迁移插件数据"""
        try:
            # 查找迁移处理器
            if plugin_name in self._migration_handlers:
                key = f"{from_version}->{to_version}"
                if key in self._migration_handlers[plugin_name]:
                    handler = self._migration_handlers[plugin_name][key]
                    migrated_data = handler(data)
                    logger.info(f"成功迁移插件 {plugin_name} 数据从 {from_version} 到 {to_version}")
                    return migrated_data
            
            # 尝试自动迁移
            return self._auto_migrate_data(data, from_version, to_version)
            
        except Exception as e:
            logger.error(f"迁移插件 {plugin_name} 数据失败: {e}")
            return data  # 返回原始数据
    
    def _auto_migrate_data(self, data: Dict[str, Any], from_version: str, 
                          to_version: str) -> Dict[str, Any]:
        """自动数据迁移"""
        # 简单的数据结构保持不变
        # 可以根据需要添加更复杂的自动迁移逻辑
        logger.info(f"执行自动数据迁移从 {from_version} 到 {to_version}")
        return data.copy()
    
    def get_deprecated_features(self, plugin_name: str, plugin_version: str) -> List[str]:
        """获取已弃用的功能列表"""
        deprecated = []
        
        if plugin_name in self._deprecated_features:
            plugin_ver = VersionInfo.from_string(plugin_version)
            
            for feature, version_str in self._deprecated_features[plugin_name].items():
                deprecated_ver = VersionInfo.from_string(version_str)
                if plugin_ver >= deprecated_ver:
                    deprecated.append(feature)
        
        return deprecated
    
    def mark_feature_deprecated(self, plugin_name: str, feature_name: str, 
                              deprecated_since: str):
        """标记功能为已弃用"""
        if plugin_name not in self._deprecated_features:
            self._deprecated_features[plugin_name] = {}
        
        self._deprecated_features[plugin_name][feature_name] = deprecated_since
        logger.info(f"标记插件 {plugin_name} 的功能 {feature_name} 在版本 {deprecated_since} 中弃用")
    
    def is_version_supported(self, plugin_version: str, min_supported: str = None, 
                           max_supported: str = None) -> bool:
        """检查版本是否受支持"""
        try:
            plugin_ver = VersionInfo.from_string(plugin_version)
            
            if min_supported:
                min_ver = VersionInfo.from_string(min_supported)
                if plugin_ver < min_ver:
                    return False
            
            if max_supported:
                max_ver = VersionInfo.from_string(max_supported)
                if plugin_ver > max_ver:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查版本支持时出错: {e}")
            return False
    
    def get_compatibility_report(self, plugins: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """生成兼容性报告"""
        report = {}
        
        for plugin_name, plugin_version in plugins.items():
            try:
                compatibility, message = self.check_compatibility(plugin_name, plugin_version)
                deprecated_features = self.get_deprecated_features(plugin_name, plugin_version)
                
                report[plugin_name] = {
                    "version": plugin_version,
                    "compatibility_level": compatibility.value,
                    "message": message,
                    "deprecated_features": deprecated_features,
                    "supported": compatibility != CompatibilityLevel.INCOMPATIBLE
                }
                
            except Exception as e:
                report[plugin_name] = {
                    "version": plugin_version,
                    "compatibility_level": "error",
                    "message": f"检查失败: {str(e)}",
                    "deprecated_features": [],
                    "supported": False
                }
        
        return report
    
    def suggest_version_update(self, plugin_name: str, current_version: str) -> Optional[str]:
        """建议版本更新"""
        try:
            current_ver = VersionInfo.from_string(current_version)
            compatibility, _ = self.check_compatibility(plugin_name, current_version)
            
            if compatibility in [CompatibilityLevel.DEPRECATED, CompatibilityLevel.BACKWARD_COMPATIBLE]:
                # 建议更新到与应用版本匹配的版本
                suggested = f"{self.app_version.major}.{self.app_version.minor}.x"
                return f"建议更新到版本 {suggested}"
            
            return None
            
        except Exception as e:
            logger.error(f"生成版本更新建议时出错: {e}")
            return None

# 全局版本管理器实例
_version_manager = None

def get_version_manager(app_version: str = "1.0.0") -> VersionCompatibilityManager:
    """获取全局版本管理器实例"""
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionCompatibilityManager(app_version)
    return _version_manager

def setup_default_compatibility_rules(manager: VersionCompatibilityManager):
    """设置默认兼容性规则"""
    # 可以在这里添加通用的兼容性规则
    pass