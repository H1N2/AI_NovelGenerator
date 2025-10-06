"""
插件模板 - 复制此模板开始开发你的插件

这个模板展示了插件开发的基本结构和最佳实践。
"""

import os
import json
from typing import Dict, Any, Optional
from plugins.base import BasePlugin
from plugins import LogLevel, EventPriority
from plugins.events import AppEvents


class TemplatePlugin(BasePlugin):
    """模板插件类 - 展示插件开发的基本结构"""
    
    def __init__(self):
        super().__init__()
        self.name = "template_plugin"
        self.version = "1.0.0"
        self.description = "插件模板 - 复制此模板开始开发你的插件"
        self.author = "你的名字"
        
        # 插件特定的属性
        self.config = {}
        self.is_running = False
        self.processed_count = 0
        
    def initialize(self) -> bool:
        """
        插件初始化方法
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 加载配置
            self.load_config()
            
            # 注册事件处理器
            self.register_event_handlers()
            
            # 执行初始化逻辑
            self.is_running = True
            self.logger.info(f"插件 {self.name} v{self.version} 初始化成功")
            
            # 发送插件状态变更事件
            self.emit_event(AppEvents.PLUGIN_STATUS_CHANGED, {
                'plugin_name': self.name,
                'status': 'initialized',
                'timestamp': self.get_current_timestamp()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """插件清理方法"""
        try:
            # 清理资源
            self.is_running = False
            
            # 保存状态（如果需要）
            self.save_state()
            
            self.logger.info(f"插件 {self.name} 清理完成")
            
            # 发送插件状态变更事件
            self.emit_event(AppEvents.PLUGIN_STATUS_CHANGED, {
                'plugin_name': self.name,
                'status': 'cleaned_up',
                'processed_count': self.processed_count,
                'timestamp': self.get_current_timestamp()
            })
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
    
    def get_services(self) -> Dict[str, callable]:
        """
        返回插件提供的服务
        
        Returns:
            Dict[str, callable]: 服务名称到方法的映射
        """
        return {
            'process_text': self.process_text,
            'get_status': self.get_status,
            'get_statistics': self.get_statistics,
            'configure': self.configure
        }
    
    def load_config(self):
        """加载插件配置"""
        config_path = os.path.join(self.plugin_dir, 'config.json')
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.debug("配置加载成功")
            except Exception as e:
                self.logger.warning(f"配置加载失败，使用默认配置: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """返回默认配置"""
        return {
            'enabled': True,
            'debug_mode': False,
            'max_retries': 3,
            'timeout': 30,
            'batch_size': 100,
            'custom_settings': {
                'feature_a': True,
                'feature_b': False,
                'threshold': 0.8
            }
        }
    
    def save_config(self):
        """保存配置"""
        config_path = os.path.join(self.plugin_dir, 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.debug("配置保存成功")
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
    
    def register_event_handlers(self):
        """注册事件处理器"""
        # 注册应用启动事件
        self.register_event_handler(
            AppEvents.APPLICATION_STARTED,
            self.on_application_started,
            priority=EventPriority.NORMAL
        )
        
        # 注册小说生成事件
        self.register_event_handler(
            AppEvents.NOVEL_GENERATION_START,
            self.on_novel_generation_start,
            priority=EventPriority.NORMAL
        )
        
        # 注册配置变更事件
        self.register_event_handler(
            AppEvents.CONFIG_UPDATED,
            self.on_config_updated,
            priority=EventPriority.HIGH
        )
    
    # 事件处理器
    def on_application_started(self, event):
        """应用启动事件处理器"""
        self.logger.info("应用已启动，插件准备就绪")
    
    def on_novel_generation_start(self, event):
        """小说生成开始事件处理器"""
        self.logger.info(f"小说生成开始: {event.data}")
        # 可以在这里执行相关逻辑
    
    def on_config_updated(self, event):
        """配置更新事件处理器"""
        self.logger.info("检测到配置更新，重新加载配置")
        self.load_config()
    
    # 服务方法
    def process_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        文本处理服务
        
        Args:
            text: 要处理的文本
            options: 处理选项
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        if not self.is_running:
            raise RuntimeError("插件未运行")
        
        try:
            self.logger.debug(f"处理文本，长度: {len(text)}")
            
            # 示例处理逻辑
            processed_text = text.strip().upper()  # 简单的处理示例
            word_count = len(text.split())
            
            self.processed_count += 1
            
            result = {
                'original_text': text,
                'processed_text': processed_text,
                'word_count': word_count,
                'processing_time': self.get_current_timestamp(),
                'success': True
            }
            
            self.logger.debug(f"文本处理完成，字数: {word_count}")
            return result
            
        except Exception as e:
            self.logger.error(f"文本处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': self.get_current_timestamp()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            'name': self.name,
            'version': self.version,
            'is_running': self.is_running,
            'processed_count': self.processed_count,
            'config': self.config,
            'timestamp': self.get_current_timestamp()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        return {
            'processed_count': self.processed_count,
            'uptime': self.get_uptime(),
            'memory_usage': self.get_memory_usage(),
            'last_activity': self.get_current_timestamp()
        }
    
    def configure(self, new_config: Dict[str, Any]) -> bool:
        """
        配置插件
        
        Args:
            new_config: 新的配置
            
        Returns:
            bool: 配置是否成功
        """
        try:
            # 验证配置
            if not self.validate_config(new_config):
                return False
            
            # 更新配置
            self.config.update(new_config)
            self.save_config()
            
            self.logger.info("插件配置更新成功")
            
            # 发送配置更新事件
            self.emit_event(AppEvents.CONFIG_UPDATED, {
                'plugin_name': self.name,
                'config': self.config,
                'timestamp': self.get_current_timestamp()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置更新失败: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 示例验证逻辑
        required_keys = ['enabled']
        for key in required_keys:
            if key not in config:
                self.logger.error(f"配置缺少必需的键: {key}")
                return False
        
        return True
    
    def save_state(self):
        """保存插件状态"""
        state_path = os.path.join(self.plugin_dir, 'state.json')
        state = {
            'processed_count': self.processed_count,
            'last_save': self.get_current_timestamp()
        }
        
        try:
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            self.logger.debug("状态保存成功")
        except Exception as e:
            self.logger.error(f"状态保存失败: {e}")
    
    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        # 这里应该记录启动时间并计算差值
        return 0.0  # 示例返回值
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except Exception:
            return {'error': 'Unable to get memory info'}


# 插件入口点
def create_plugin():
    """创建插件实例"""
    return TemplatePlugin()


# 如果直接运行此文件，可以进行简单测试
if __name__ == "__main__":
    plugin = create_plugin()
    print(f"插件 {plugin.name} v{plugin.version} 创建成功")
    print(f"描述: {plugin.description}")
    print(f"作者: {plugin.author}")