# plugins/registry.py
"""
插件注册表
管理插件元数据和依赖关系
"""

from typing import Dict, List, Optional, Set
from .base import PluginMetadata


class PluginRegistry:
    """插件注册表"""
    
    def __init__(self):
        self._plugins: Dict[str, PluginMetadata] = {}
        self._dependencies: Dict[str, Set[str]] = {}
        
    def register_plugin(self, metadata: PluginMetadata):
        """注册插件"""
        self._plugins[metadata.name] = metadata
        self._dependencies[metadata.name] = set(metadata.dependencies)
        
    def unregister_plugin(self, plugin_name: str):
        """注销插件"""
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
        if plugin_name in self._dependencies:
            del self._dependencies[plugin_name]
            
    def get_plugin(self, plugin_name: str) -> Optional[PluginMetadata]:
        """获取插件元数据"""
        return self._plugins.get(plugin_name)
        
    def get_all_plugins(self) -> Dict[str, PluginMetadata]:
        """获取所有插件"""
        return self._plugins.copy()
        
    def get_dependencies(self, plugin_name: str) -> Set[str]:
        """获取插件依赖"""
        return self._dependencies.get(plugin_name, set())
        
    def get_dependents(self, plugin_name: str) -> Set[str]:
        """获取依赖此插件的其他插件"""
        dependents = set()
        for name, deps in self._dependencies.items():
            if plugin_name in deps:
                dependents.add(name)
        return dependents
        
    def resolve_load_order(self, plugin_names: List[str]) -> List[str]:
        """解析插件加载顺序（拓扑排序）"""
        # 简单的拓扑排序实现
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(name: str):
            if name in temp_visited:
                raise ValueError(f"检测到循环依赖: {name}")
            if name in visited:
                return
                
            temp_visited.add(name)
            
            # 先访问依赖
            for dep in self.get_dependencies(name):
                if dep in plugin_names:
                    visit(dep)
                    
            temp_visited.remove(name)
            visited.add(name)
            result.append(name)
            
        for name in plugin_names:
            if name not in visited:
                visit(name)
                
        return result
        
    def check_dependencies(self, plugin_name: str) -> List[str]:
        """检查插件依赖是否满足"""
        missing = []
        for dep in self.get_dependencies(plugin_name):
            if dep not in self._plugins:
                missing.append(dep)
        return missing