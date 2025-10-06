"""
文本处理示例插件

提供文本清理、格式化、分析等功能的示例插件。
展示了如何处理中文文本、使用第三方库、实现复杂的服务逻辑。
"""

import re
import json
import os
from typing import Dict, Any, List, Optional
from collections import Counter

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

from plugins.base import BasePlugin
from plugins import LogLevel, EventPriority
from plugins.events import AppEvents


class TextProcessorPlugin(BasePlugin):
    """文本处理插件 - 提供各种文本处理功能"""
    
    def __init__(self):
        super().__init__()
        self.name = "text_processor"
        self.version = "1.0.0"
        self.description = "文本处理示例插件 - 提供文本清理、格式化和分析功能"
        self.author = "AI小说生成器团队"
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 插件状态
        self.config = {}
        self.statistics = {
            'processed_texts': 0,
            'total_characters': 0,
            'total_words': 0,
            'cleaned_texts': 0,
            'analyzed_texts': 0
        }
        
        # 文本处理规则
        self.cleaning_rules = []
        self.format_rules = []
        
    def get_metadata(self) -> 'PluginMetadata':
        """返回插件元数据"""
        from plugins.base import PluginMetadata
        return PluginMetadata(
            name="text_processor",
            version="1.0.0",
            description="文本处理示例插件 - 提供文本清理、格式化和分析功能",
            author="AI小说生成器团队",
            entry_point="create_plugin",
            main="main.py"
        )
    
    def initialize(self, context=None) -> bool:
        """初始化插件"""
        try:
            # 加载配置
            self.load_config()
            
            # 初始化jieba（如果可用）
            if JIEBA_AVAILABLE:
                jieba.initialize()
                self.logger.info("jieba分词器初始化成功")
            else:
                self.logger.warning("jieba不可用，部分功能将受限")
            
            # 加载处理规则
            self.load_processing_rules()
            
            # 注册事件处理器
            self.register_event_handlers()
            
            self.logger.info(f"文本处理插件 v{self.version} 初始化成功")
            
            # 发送初始化完成事件
            # self.emit_event(AppEvents.PLUGIN_STATUS_CHANGED, {
            #     'plugin_name': self.name,
            #     'status': 'initialized',
            #     'features': self.get_available_features()
            # })
            
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件"""
        try:
            # 保存统计信息
            self.save_statistics()
            
            self.logger.info(f"文本处理插件清理完成，共处理 {self.statistics['processed_texts']} 个文本")
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
    
    def get_services(self) -> Dict[str, callable]:
        """返回插件提供的服务"""
        return {
            'clean_text': self.clean_text,
            'format_text': self.format_text,
            'analyze_text': self.analyze_text,
            'extract_keywords': self.extract_keywords,
            'count_words': self.count_words,
            'split_sentences': self.split_sentences,
            'get_statistics': self.get_text_statistics,
            'batch_process': self.batch_process_texts
        }
    
    def load_config(self):
        """加载配置"""
        config_path = os.path.join(self.plugin_dir, 'config.json')
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.debug("配置加载成功")
            except Exception as e:
                self.logger.warning(f"配置加载失败: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'enabled': True,
            'debug_mode': False,
            'cleaning': {
                'remove_extra_spaces': True,
                'remove_empty_lines': True,
                'normalize_punctuation': True,
                'remove_special_chars': False
            },
            'formatting': {
                'indent_paragraphs': True,
                'line_length': 80,
                'paragraph_spacing': 1
            },
            'analysis': {
                'enable_keyword_extraction': True,
                'keyword_count': 10,
                'enable_sentiment_analysis': False
            }
        }
    
    def save_config(self):
        """保存配置"""
        config_path = os.path.join(self.plugin_dir, 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"配置保存失败: {e}")
    
    def load_processing_rules(self):
        """加载文本处理规则"""
        # 清理规则
        self.cleaning_rules = [
            (r'\s+', ' '),  # 多个空格替换为单个空格
            (r'\n\s*\n', '\n\n'),  # 多个空行替换为双空行
            (r'["""]', '"'),  # 统一引号
            (r"[''']", "'"),  # 统一单引号
        ]
        
        # 格式化规则
        self.format_rules = [
            ('paragraph_indent', '    '),  # 段落缩进
            ('line_ending', '\n'),  # 行结束符
        ]
        
        self.logger.debug(f"加载了 {len(self.cleaning_rules)} 个清理规则和 {len(self.format_rules)} 个格式化规则")
    
    def register_event_handlers(self):
        """注册事件处理器"""
        # 注册小说生成开始事件
        # self.register_event_handler(
        #     AppEvents.NOVEL_GENERATION_START,
        #     self.on_novel_generation_start
        # )
        
        # 注册章节生成完成事件
        # self.register_event_handler(
        #     AppEvents.CHAPTER_GENERATED,
        #     self.on_chapter_generated
        # )
        pass
    
    def on_novel_generation_start(self, event):
        """小说生成开始事件处理"""
        self.logger.info("小说生成开始，文本处理插件准备就绪")
    
    def on_chapter_generated(self, event):
        """章节生成完成事件处理"""
        if 'chapter_content' in event.data:
            # 自动分析生成的章节
            content = event.data['chapter_content']
            analysis = self.analyze_text(content)
            self.logger.info(f"章节分析完成: {analysis['word_count']} 字，{analysis['sentence_count']} 句")
    
    # 服务方法实现
    def clean_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        清理文本
        
        Args:
            text: 要清理的文本
            options: 清理选项
            
        Returns:
            Dict[str, Any]: 清理结果
        """
        try:
            if not text:
                return {'success': False, 'error': '文本为空'}
            
            original_text = text
            cleaned_text = text
            
            # 应用清理规则
            if self.config['cleaning']['remove_extra_spaces']:
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            if self.config['cleaning']['remove_empty_lines']:
                cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
            
            if self.config['cleaning']['normalize_punctuation']:
                # 统一引号
                cleaned_text = re.sub(r'["""]', '"', cleaned_text)
                cleaned_text = re.sub(r"[''']", "'", cleaned_text)
            
            if self.config['cleaning']['remove_special_chars']:
                cleaned_text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？；：""''（）【】《》]", '', cleaned_text)
            
            # 应用自定义清理规则
            for pattern, replacement in self.cleaning_rules:
                cleaned_text = re.sub(pattern, replacement, cleaned_text)
            
            # 更新统计
            self.statistics['cleaned_texts'] += 1
            self.statistics['total_characters'] += len(cleaned_text)
            
            result = {
                'success': True,
                'original_text': original_text,
                'cleaned_text': cleaned_text.strip(),
                'changes_made': len(original_text) != len(cleaned_text.strip()),
                'original_length': len(original_text),
                'cleaned_length': len(cleaned_text.strip())
            }
            
            self.logger.debug(f"文本清理完成: {len(original_text)} -> {len(cleaned_text.strip())} 字符")
            return result
            
        except Exception as e:
            self.logger.error(f"文本清理失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        格式化文本
        
        Args:
            text: 要格式化的文本
            options: 格式化选项
            
        Returns:
            Dict[str, Any]: 格式化结果
        """
        try:
            if not text:
                return {'success': False, 'error': '文本为空'}
            
            formatted_text = text
            
            # 段落缩进
            if self.config['formatting']['indent_paragraphs']:
                lines = formatted_text.split('\n')
                formatted_lines = []
                for line in lines:
                    if line.strip():  # 非空行
                        formatted_lines.append('    ' + line.strip())
                    else:
                        formatted_lines.append('')
                formatted_text = '\n'.join(formatted_lines)
            
            # 行长度控制
            line_length = self.config['formatting']['line_length']
            if line_length > 0:
                formatted_text = self.wrap_text(formatted_text, line_length)
            
            result = {
                'success': True,
                'original_text': text,
                'formatted_text': formatted_text,
                'formatting_applied': True
            }
            
            self.logger.debug("文本格式化完成")
            return result
            
        except Exception as e:
            self.logger.error(f"文本格式化失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析文本
        
        Args:
            text: 要分析的文本
            options: 分析选项
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            if not text:
                return {'success': False, 'error': '文本为空'}
            
            # 基本统计
            char_count = len(text)
            word_count = len(text.split()) if not JIEBA_AVAILABLE else len(list(jieba.cut(text)))
            sentence_count = len(re.findall(r'[。！？.!?]+', text))
            paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # 字符分布
            char_distribution = Counter(text)
            most_common_chars = char_distribution.most_common(10)
            
            # 词频统计（如果jieba可用）
            word_freq = {}
            if JIEBA_AVAILABLE:
                words = [word for word in jieba.cut(text) if len(word.strip()) > 1]
                word_freq = dict(Counter(words).most_common(20))
            
            # 更新统计
            self.statistics['analyzed_texts'] += 1
            self.statistics['processed_texts'] += 1
            self.statistics['total_characters'] += char_count
            self.statistics['total_words'] += word_count
            
            result = {
                'success': True,
                'word_count': word_count,  # 测试期望的直接字段
                'character_count': char_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'basic_stats': {
                    'character_count': char_count,
                    'word_count': word_count,
                    'sentence_count': sentence_count,
                    'paragraph_count': paragraph_count
                },
                'character_distribution': most_common_chars,
                'word_frequency': word_freq,
                'readability': {
                    'avg_sentence_length': char_count / max(sentence_count, 1),
                    'avg_word_length': char_count / max(word_count, 1)
                }
            }
            
            self.logger.debug(f"文本分析完成: {char_count} 字符，{word_count} 词，{sentence_count} 句")
            return result
            
        except Exception as e:
            self.logger.error(f"文本分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_keywords(self, text: str, count: int = 10):
        """提取关键词"""
        try:
            if not JIEBA_AVAILABLE:
                return []  # 测试期望返回列表
            
            if not text:
                return []  # 测试期望返回列表
            
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=count, withWeight=True)
            
            # 测试期望直接返回关键词列表
            result = [word for word, weight in keywords]
            
            self.logger.debug(f"关键词提取完成: {len(keywords)} 个关键词")
            return result
            
        except Exception as e:
            self.logger.error(f"关键词提取失败: {e}")
            return []  # 测试期望返回列表
    
    def count_words(self, text: str) -> Dict[str, Any]:
        """统计词数"""
        try:
            if not text:
                return {'success': False, 'error': '文本为空'}
            
            if JIEBA_AVAILABLE:
                words = list(jieba.cut(text))
                word_count = len([w for w in words if w.strip()])
            else:
                word_count = len(text.split())
            
            result = {
                'success': True,
                'word_count': word_count,
                'character_count': len(text),
                'character_count_no_spaces': len(text.replace(' ', ''))
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"词数统计失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def split_sentences(self, text: str) -> Dict[str, Any]:
        """分割句子"""
        try:
            if not text:
                return {'success': False, 'error': '文本为空'}
            
            # 中文句子分割
            sentences = re.split(r'[。！？.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            result = {
                'success': True,
                'sentences': sentences,
                'sentence_count': len(sentences)
            }
            
            self.logger.debug(f"句子分割完成: {len(sentences)} 个句子")
            return result
            
        except Exception as e:
            self.logger.error(f"句子分割失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def batch_process_texts(self, texts: List[str], operations: List[str]) -> Dict[str, Any]:
        """批量处理文本"""
        try:
            if not texts:
                return {'success': False, 'error': '文本列表为空'}
            
            results = []
            for i, text in enumerate(texts):
                text_results = {'index': i, 'original_text': text}
                
                for operation in operations:
                    if operation == 'clean':
                        result = self.clean_text(text)
                        if result['success']:
                            text = result['cleaned_text']
                            text_results['cleaned'] = True
                    
                    elif operation == 'analyze':
                        result = self.analyze_text(text)
                        if result['success']:
                            text_results['analysis'] = result['basic_stats']
                    
                    elif operation == 'keywords':
                        result = self.extract_keywords(text)
                        if result['success']:
                            text_results['keywords'] = result['keywords']
                
                text_results['processed_text'] = text
                results.append(text_results)
            
            return {
                'success': True,
                'results': results,
                'processed_count': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"批量处理失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_text_statistics(self) -> Dict[str, Any]:
        """获取文本处理统计信息"""
        return {
            'success': True,
            'statistics': self.statistics.copy(),
            'features': self.get_available_features()
        }
    
    def get_available_features(self) -> List[str]:
        """获取可用功能列表"""
        features = ['clean_text', 'format_text', 'analyze_text', 'count_words', 'split_sentences']
        
        if JIEBA_AVAILABLE:
            features.extend(['extract_keywords', 'advanced_word_count'])
        
        return features
    
    def wrap_text(self, text: str, width: int) -> str:
        """文本换行"""
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                # 简单的换行逻辑
                words = line.split(' ')
                current_line = ''
                for word in words:
                    if len(current_line + word) <= width:
                        current_line += word + ' '
                    else:
                        if current_line:
                            wrapped_lines.append(current_line.strip())
                        current_line = word + ' '
                if current_line:
                    wrapped_lines.append(current_line.strip())
        
        return '\n'.join(wrapped_lines)
    
    def save_statistics(self):
        """保存统计信息"""
        stats_path = os.path.join(self.plugin_dir, 'statistics.json')
        try:
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"统计信息保存失败: {e}")


def create_plugin():
    """创建插件实例"""
    return TextProcessorPlugin()