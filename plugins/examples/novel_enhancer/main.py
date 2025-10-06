"""
小说增强示例插件

提供情节分析、角色管理、风格优化等高级功能的示例插件。
展示了如何依赖其他插件、实现复杂的业务逻辑、管理持久化数据。
"""

import json
import os
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

from plugins.base import BasePlugin
from plugins import LogLevel, EventPriority
from plugins.events import AppEvents


@dataclass
class Character:
    """角色数据类"""
    name: str
    description: str = ""
    personality: List[str] = None
    relationships: Dict[str, str] = None
    appearances: List[int] = None  # 出现的章节
    importance: float = 0.0  # 重要性评分
    
    def __post_init__(self):
        if self.personality is None:
            self.personality = []
        if self.relationships is None:
            self.relationships = {}
        if self.appearances is None:
            self.appearances = []


@dataclass
class PlotPoint:
    """情节点数据类"""
    chapter: int
    description: str
    type: str  # setup, conflict, climax, resolution
    importance: float = 0.0
    characters_involved: List[str] = None
    
    def __post_init__(self):
        if self.characters_involved is None:
            self.characters_involved = []


class NovelEnhancerPlugin(BasePlugin):
    """小说增强插件 - 提供高级分析和优化功能"""
    
    def __init__(self):
        super().__init__()
        self.name = "novel_enhancer"
        self.version = "1.0.0"
        self.description = "小说增强示例插件 - 提供情节分析、角色管理、风格优化等功能"
        self.author = "AI小说生成器团队"
        
        # 插件状态
        self.config = {}
        self.characters: Dict[str, Character] = {}
        self.plot_points: List[PlotPoint] = []
        self.novel_metadata = {}
        self.text_processor = None  # 依赖的文本处理插件
        
        # 统计信息
        self.statistics = {
            'novels_analyzed': 0,
            'characters_managed': 0,
            'plot_points_identified': 0,
            'style_optimizations': 0
        }
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            # 加载配置
            self.load_config()
            
            # 获取依赖的文本处理插件
            self.text_processor = self.get_dependency_service('text_processor')
            if not self.text_processor:
                self.logger.warning("文本处理插件不可用，部分功能将受限")
            
            # 加载持久化数据
            self.load_persistent_data()
            
            # 注册事件处理器
            self.register_event_handlers()
            
            self.logger.info(f"小说增强插件 v{self.version} 初始化成功")
            
            # 发送初始化完成事件
            self.emit_event(AppEvents.PLUGIN_STATUS_CHANGED, {
                'plugin_name': self.name,
                'status': 'initialized',
                'dependencies': ['text_processor'],
                'features': self.get_available_features()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件"""
        try:
            # 保存持久化数据
            self.save_persistent_data()
            
            # 保存统计信息
            self.save_statistics()
            
            self.logger.info(f"小说增强插件清理完成，管理了 {len(self.characters)} 个角色")
            
        except Exception as e:
            self.logger.error(f"插件清理失败: {e}")
    
    def get_services(self) -> Dict[str, callable]:
        """返回插件提供的服务"""
        return {
            'analyze_novel': self.analyze_novel,
            'manage_character': self.manage_character,
            'get_character': self.get_character,
            'list_characters': self.list_characters,
            'analyze_plot': self.analyze_plot,
            'optimize_style': self.optimize_style,
            'generate_summary': self.generate_summary,
            'check_consistency': self.check_consistency,
            'get_recommendations': self.get_recommendations,
            'export_analysis': self.export_analysis
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
            'character_analysis': {
                'auto_detect': True,
                'importance_threshold': 0.3,
                'max_characters': 50
            },
            'plot_analysis': {
                'auto_identify_points': True,
                'chapter_analysis': True,
                'conflict_detection': True
            },
            'style_optimization': {
                'enable_suggestions': True,
                'check_repetition': True,
                'analyze_pacing': True
            },
            'export': {
                'include_statistics': True,
                'include_recommendations': True,
                'format': 'json'
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
    
    def load_persistent_data(self):
        """加载持久化数据"""
        data_path = os.path.join(self.plugin_dir, 'data.json')
        
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 恢复角色数据
                if 'characters' in data:
                    for char_data in data['characters']:
                        char = Character(**char_data)
                        self.characters[char.name] = char
                
                # 恢复情节点数据
                if 'plot_points' in data:
                    self.plot_points = [PlotPoint(**pp) for pp in data['plot_points']]
                
                # 恢复小说元数据
                if 'novel_metadata' in data:
                    self.novel_metadata = data['novel_metadata']
                
                self.logger.debug(f"持久化数据加载成功: {len(self.characters)} 个角色，{len(self.plot_points)} 个情节点")
                
            except Exception as e:
                self.logger.warning(f"持久化数据加载失败: {e}")
    
    def save_persistent_data(self):
        """保存持久化数据"""
        data_path = os.path.join(self.plugin_dir, 'data.json')
        
        try:
            data = {
                'characters': [asdict(char) for char in self.characters.values()],
                'plot_points': [asdict(pp) for pp in self.plot_points],
                'novel_metadata': self.novel_metadata,
                'last_save': datetime.now().isoformat()
            }
            
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("持久化数据保存成功")
            
        except Exception as e:
            self.logger.error(f"持久化数据保存失败: {e}")
    
    def register_event_handlers(self):
        """注册事件处理器"""
        self.register_event_handler(
            AppEvents.CHAPTER_GENERATED,
            self.on_chapter_generated,
            priority=EventPriority.NORMAL
        )
        
        self.register_event_handler(
            AppEvents.NOVEL_GENERATION_COMPLETED,
            self.on_novel_completed,
            priority=EventPriority.NORMAL
        )
    
    def on_chapter_generated(self, event):
        """章节生成完成事件处理"""
        if 'chapter_content' in event.data and 'chapter_number' in event.data:
            content = event.data['chapter_content']
            chapter_num = event.data['chapter_number']
            
            # 自动分析新章节
            self.analyze_chapter(content, chapter_num)
    
    def on_novel_completed(self, event):
        """小说生成完成事件处理"""
        self.logger.info("小说生成完成，开始全面分析")
        
        if 'novel_content' in event.data:
            # 进行完整的小说分析
            analysis_result = self.analyze_novel(event.data['novel_content'])
            
            # 发送分析完成事件
            self.emit_event(AppEvents.NOVEL_ANALYSIS_COMPLETED, {
                'plugin_name': self.name,
                'analysis_result': analysis_result
            })
    
    def get_dependency_service(self, plugin_name: str):
        """获取依赖插件的服务"""
        try:
            # 这里应该通过插件管理器获取其他插件的服务
            # 简化实现，实际应该通过 self.plugin_manager.call_plugin_service
            return None  # 占位符
        except Exception as e:
            self.logger.warning(f"无法获取依赖插件 {plugin_name} 的服务: {e}")
            return None
    
    # 服务方法实现
    def analyze_novel(self, content: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析整部小说
        
        Args:
            content: 小说内容
            options: 分析选项
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            if not content:
                return {'success': False, 'error': '小说内容为空'}
            
            self.logger.info("开始分析小说")
            
            # 基础文本分析（使用文本处理插件）
            basic_analysis = {}
            if self.text_processor:
                basic_analysis = self.text_processor.analyze_text(content)
            
            # 角色分析
            character_analysis = self.analyze_characters(content)
            
            # 情节分析
            plot_analysis = self.analyze_plot_structure(content)
            
            # 风格分析
            style_analysis = self.analyze_writing_style(content)
            
            # 更新统计
            self.statistics['novels_analyzed'] += 1
            
            result = {
                'success': True,
                'basic_analysis': basic_analysis,
                'character_analysis': character_analysis,
                'plot_analysis': plot_analysis,
                'style_analysis': style_analysis,
                'recommendations': self.generate_recommendations_internal(content),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("小说分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"小说分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_characters(self, content: str) -> Dict[str, Any]:
        """分析角色"""
        try:
            # 简单的角色识别（基于姓名模式）
            # 实际实现应该更复杂，可能需要NLP技术
            
            # 中文姓名模式
            name_patterns = [
                r'[王李张刘陈杨黄赵周吴徐孙朱马胡郭林何高梁郑罗宋谢唐韩曹许邓萧冯曾程蔡彭潘袁于董余苏叶吕魏蒋田杜丁沈姜范江傅钟卢汪戴崔任陆廖姚方金邱夏谭韦贾邹石熊孟秦阎薛侯雷白龙段郝孔邵史毛常万顾赖武康贺严尹钱施牛洪龚][一-龯]{1,2}',
                r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*'  # 英文姓名
            ]
            
            detected_names = set()
            for pattern in name_patterns:
                names = re.findall(pattern, content)
                detected_names.update(names)
            
            # 分析每个角色的出现频率和重要性
            character_stats = {}
            for name in detected_names:
                if len(name) >= 2:  # 过滤太短的匹配
                    count = content.count(name)
                    if count >= 2:  # 至少出现2次才认为是角色
                        character_stats[name] = {
                            'appearances': count,
                            'importance': min(count / 10.0, 1.0),  # 简单的重要性计算
                            'first_appearance': content.find(name)
                        }
                        
                        # 创建或更新角色
                        if name not in self.characters:
                            self.characters[name] = Character(
                                name=name,
                                importance=character_stats[name]['importance']
                            )
                        else:
                            self.characters[name].importance = character_stats[name]['importance']
            
            self.statistics['characters_managed'] = len(self.characters)
            
            return {
                'detected_characters': character_stats,
                'total_characters': len(character_stats),
                'main_characters': {name: stats for name, stats in character_stats.items() 
                                 if stats['importance'] > 0.3}
            }
            
        except Exception as e:
            self.logger.error(f"角色分析失败: {e}")
            return {'error': str(e)}
    
    def analyze_plot_structure(self, content: str) -> Dict[str, Any]:
        """分析情节结构"""
        try:
            # 简单的情节分析
            chapters = self.split_into_chapters(content)
            
            plot_points = []
            for i, chapter in enumerate(chapters):
                # 检测情节关键词
                conflict_keywords = ['冲突', '矛盾', '争吵', '战斗', '对抗']
                climax_keywords = ['高潮', '决战', '关键', '转折']
                resolution_keywords = ['解决', '结束', '完成', '和解']
                
                chapter_lower = chapter.lower()
                
                plot_type = 'development'  # 默认类型
                importance = 0.3
                
                if any(keyword in chapter for keyword in conflict_keywords):
                    plot_type = 'conflict'
                    importance = 0.7
                elif any(keyword in chapter for keyword in climax_keywords):
                    plot_type = 'climax'
                    importance = 0.9
                elif any(keyword in chapter for keyword in resolution_keywords):
                    plot_type = 'resolution'
                    importance = 0.6
                
                plot_point = PlotPoint(
                    chapter=i + 1,
                    description=f"第{i+1}章情节点",
                    type=plot_type,
                    importance=importance
                )
                plot_points.append(plot_point)
            
            self.plot_points = plot_points
            self.statistics['plot_points_identified'] = len(plot_points)
            
            return {
                'total_chapters': len(chapters),
                'plot_points': [asdict(pp) for pp in plot_points],
                'structure_analysis': {
                    'setup_chapters': len([pp for pp in plot_points if pp.type == 'setup']),
                    'conflict_chapters': len([pp for pp in plot_points if pp.type == 'conflict']),
                    'climax_chapters': len([pp for pp in plot_points if pp.type == 'climax']),
                    'resolution_chapters': len([pp for pp in plot_points if pp.type == 'resolution'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"情节分析失败: {e}")
            return {'error': str(e)}
    
    def analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """分析写作风格"""
        try:
            # 句子长度分析
            sentences = re.split(r'[。！？.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            sentence_lengths = [len(s) for s in sentences]
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
            
            # 段落分析
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            paragraph_lengths = [len(p) for p in paragraphs]
            avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
            
            # 词汇重复分析
            words = content.split()
            word_freq = {}
            for word in words:
                if len(word) > 1:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 找出重复度高的词汇
            repeated_words = {word: count for word, count in word_freq.items() 
                            if count > len(words) * 0.01}  # 出现频率超过1%
            
            return {
                'sentence_analysis': {
                    'total_sentences': len(sentences),
                    'average_length': avg_sentence_length,
                    'length_distribution': {
                        'short': len([l for l in sentence_lengths if l < 20]),
                        'medium': len([l for l in sentence_lengths if 20 <= l < 50]),
                        'long': len([l for l in sentence_lengths if l >= 50])
                    }
                },
                'paragraph_analysis': {
                    'total_paragraphs': len(paragraphs),
                    'average_length': avg_paragraph_length
                },
                'vocabulary_analysis': {
                    'total_words': len(words),
                    'unique_words': len(word_freq),
                    'vocabulary_richness': len(word_freq) / len(words) if words else 0,
                    'repeated_words': repeated_words
                }
            }
            
        except Exception as e:
            self.logger.error(f"风格分析失败: {e}")
            return {'error': str(e)}
    
    def manage_character(self, name: str, action: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """管理角色"""
        try:
            if action == 'create':
                if name in self.characters:
                    return {'success': False, 'error': '角色已存在'}
                
                character = Character(name=name)
                if data:
                    for key, value in data.items():
                        if hasattr(character, key):
                            setattr(character, key, value)
                
                self.characters[name] = character
                self.logger.info(f"创建角色: {name}")
                return {'success': True, 'character': asdict(character)}
            
            elif action == 'update':
                if name not in self.characters:
                    return {'success': False, 'error': '角色不存在'}
                
                character = self.characters[name]
                if data:
                    for key, value in data.items():
                        if hasattr(character, key):
                            setattr(character, key, value)
                
                self.logger.info(f"更新角色: {name}")
                return {'success': True, 'character': asdict(character)}
            
            elif action == 'delete':
                if name not in self.characters:
                    return {'success': False, 'error': '角色不存在'}
                
                del self.characters[name]
                self.logger.info(f"删除角色: {name}")
                return {'success': True}
            
            else:
                return {'success': False, 'error': f'未知操作: {action}'}
                
        except Exception as e:
            self.logger.error(f"角色管理失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_character(self, name: str) -> Dict[str, Any]:
        """获取角色信息"""
        try:
            if name not in self.characters:
                return {'success': False, 'error': '角色不存在'}
            
            return {
                'success': True,
                'character': asdict(self.characters[name])
            }
            
        except Exception as e:
            self.logger.error(f"获取角色失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_characters(self) -> Dict[str, Any]:
        """列出所有角色"""
        try:
            return {
                'success': True,
                'characters': [asdict(char) for char in self.characters.values()],
                'total_count': len(self.characters)
            }
            
        except Exception as e:
            self.logger.error(f"列出角色失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_plot(self, content: str) -> Dict[str, Any]:
        """分析情节"""
        return self.analyze_plot_structure(content)
    
    def optimize_style(self, content: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """优化写作风格"""
        try:
            suggestions = []
            optimized_content = content
            
            # 检查重复词汇
            words = content.split()
            word_freq = {}
            for word in words:
                if len(word) > 1:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            repeated_words = {word: count for word, count in word_freq.items() 
                            if count > len(words) * 0.02}
            
            if repeated_words:
                suggestions.append({
                    'type': 'repetition',
                    'message': f'检测到重复使用的词汇: {list(repeated_words.keys())[:5]}',
                    'severity': 'medium'
                })
            
            # 检查句子长度
            sentences = re.split(r'[。！？.!?]+', content)
            long_sentences = [s for s in sentences if len(s) > 100]
            
            if long_sentences:
                suggestions.append({
                    'type': 'sentence_length',
                    'message': f'发现 {len(long_sentences)} 个过长的句子，建议分割',
                    'severity': 'low'
                })
            
            # 检查段落长度
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            long_paragraphs = [p for p in paragraphs if len(p) > 500]
            
            if long_paragraphs:
                suggestions.append({
                    'type': 'paragraph_length',
                    'message': f'发现 {len(long_paragraphs)} 个过长的段落，建议分段',
                    'severity': 'low'
                })
            
            self.statistics['style_optimizations'] += 1
            
            return {
                'success': True,
                'suggestions': suggestions,
                'optimized_content': optimized_content,
                'improvement_count': len(suggestions)
            }
            
        except Exception as e:
            self.logger.error(f"风格优化失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_summary(self, content: str, max_length: int = 200) -> Dict[str, Any]:
        """生成摘要"""
        try:
            # 简单的摘要生成（取前几句）
            sentences = re.split(r'[。！？.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            summary_sentences = []
            current_length = 0
            
            for sentence in sentences:
                if current_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            summary = '。'.join(summary_sentences) + '。'
            
            return {
                'success': True,
                'summary': summary,
                'original_length': len(content),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(content) if content else 0
            }
            
        except Exception as e:
            self.logger.error(f"摘要生成失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_consistency(self, content: str) -> Dict[str, Any]:
        """检查一致性"""
        try:
            issues = []
            
            # 检查角色名称一致性
            for char_name in self.characters:
                variations = [char_name, char_name.upper(), char_name.lower()]
                counts = {var: content.count(var) for var in variations}
                
                if sum(counts.values()) > counts.get(char_name, 0):
                    issues.append({
                        'type': 'character_name_inconsistency',
                        'character': char_name,
                        'message': f'角色 {char_name} 的名称使用不一致',
                        'details': counts
                    })
            
            # 检查时间线一致性（简单检查）
            time_indicators = re.findall(r'(昨天|今天|明天|上午|下午|晚上)', content)
            if len(set(time_indicators)) > 5:
                issues.append({
                    'type': 'timeline_complexity',
                    'message': '时间线可能过于复杂，建议检查一致性',
                    'indicators': list(set(time_indicators))
                })
            
            return {
                'success': True,
                'issues': issues,
                'consistency_score': max(0, 1.0 - len(issues) * 0.1)
            }
            
        except Exception as e:
            self.logger.error(f"一致性检查失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_recommendations(self, content: str) -> Dict[str, Any]:
        """获取改进建议"""
        return {'success': True, 'recommendations': self.generate_recommendations_internal(content)}
    
    def generate_recommendations_internal(self, content: str) -> List[Dict[str, Any]]:
        """内部方法：生成改进建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        if len(self.characters) < 3:
            recommendations.append({
                'type': 'character_development',
                'priority': 'medium',
                'message': '考虑增加更多角色来丰富故事情节'
            })
        
        if len(self.plot_points) < 5:
            recommendations.append({
                'type': 'plot_development',
                'priority': 'high',
                'message': '情节点较少，建议增加更多冲突和转折'
            })
        
        # 基于内容长度的建议
        if len(content) < 1000:
            recommendations.append({
                'type': 'content_length',
                'priority': 'low',
                'message': '内容较短，可以考虑扩展描述和对话'
            })
        
        return recommendations
    
    def export_analysis(self, format_type: str = 'json') -> Dict[str, Any]:
        """导出分析结果"""
        try:
            export_data = {
                'characters': [asdict(char) for char in self.characters.values()],
                'plot_points': [asdict(pp) for pp in self.plot_points],
                'novel_metadata': self.novel_metadata,
                'statistics': self.statistics,
                'export_timestamp': datetime.now().isoformat()
            }
            
            if format_type == 'json':
                return {
                    'success': True,
                    'data': export_data,
                    'format': 'json'
                }
            else:
                return {'success': False, 'error': f'不支持的格式: {format_type}'}
                
        except Exception as e:
            self.logger.error(f"导出分析失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def split_into_chapters(self, content: str) -> List[str]:
        """将内容分割为章节"""
        # 简单的章节分割逻辑
        chapter_patterns = [
            r'第[一二三四五六七八九十\d]+章',
            r'Chapter\s+\d+',
            r'章节\s*\d+'
        ]
        
        for pattern in chapter_patterns:
            if re.search(pattern, content):
                chapters = re.split(pattern, content)
                return [chapter.strip() for chapter in chapters if chapter.strip()]
        
        # 如果没有明确的章节标记，按段落分割
        return [p.strip() for p in content.split('\n\n') if p.strip()]
    
    def analyze_chapter(self, content: str, chapter_num: int):
        """分析单个章节"""
        try:
            # 分析章节中的角色
            self.analyze_characters(content)
            
            # 创建章节情节点
            plot_point = PlotPoint(
                chapter=chapter_num,
                description=f"第{chapter_num}章",
                type='development',
                importance=0.5
            )
            
            # 检查是否有特殊情节类型
            if any(keyword in content for keyword in ['冲突', '矛盾', '争吵']):
                plot_point.type = 'conflict'
                plot_point.importance = 0.7
            
            self.plot_points.append(plot_point)
            
            self.logger.debug(f"章节 {chapter_num} 分析完成")
            
        except Exception as e:
            self.logger.error(f"章节分析失败: {e}")
    
    def get_available_features(self) -> List[str]:
        """获取可用功能列表"""
        features = [
            'analyze_novel', 'manage_character', 'analyze_plot',
            'optimize_style', 'generate_summary', 'check_consistency',
            'get_recommendations', 'export_analysis'
        ]
        
        if self.text_processor:
            features.append('advanced_text_analysis')
        
        return features
    
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
    return NovelEnhancerPlugin()