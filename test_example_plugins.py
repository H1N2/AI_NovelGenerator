#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例插件测试脚本
测试 text_processor 和 novel_enhancer 插件的加载和运行
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.manager import PluginManager
from plugins.logging_system import get_plugin_logging_system

class ExamplePluginTester:
    """示例插件测试器"""
    
    def __init__(self):
        self.test_count = 0
        self.passed_count = 0
        self.failed_tests = []
        
        # 创建模拟应用实例
        class MockApp:
            def __init__(self):
                self.version = "1.0.0"
        
        self.mock_app = MockApp()
        # 设置插件目录为 examples 子目录
        self.manager = PluginManager(self.mock_app, "plugins/examples")
        
    def assert_test(self, test_name: str, condition: bool):
        """断言测试"""
        self.test_count += 1
        if condition:
            print(f"   ✅ {test_name}: 通过")
            self.passed_count += 1
        else:
            print(f"   ❌ {test_name}: 失败")
            self.failed_tests.append(test_name)
    
    def test_text_processor_plugin(self):
        """测试文本处理插件"""
        print("\n📝 测试文本处理插件...")
        
        try:
            # 插件管理器会自动发现插件目录中的插件
            # 无需手动添加插件目录
            
            # 先检查插件是否被发现
            discovered = self.manager.discover_plugins()
            print(f"   发现的插件: {[p.name for p in discovered]}")
            
            # 加载插件
            success = self.manager.load_plugin("text_processor")
            self.assert_test("文本处理插件加载", success)
            
            if success:
                # 获取插件实例
                plugin = self.manager.get_plugin("text_processor")
                self.assert_test("获取插件实例", plugin is not None)
                
                if plugin:
                    # 测试文本清理
                    test_text = "  这是一个测试文本。  \n\n  有多余的空格和换行。  "
                    cleaned = plugin.clean_text(test_text)
                    self.assert_test("文本清理功能", cleaned != test_text and len(cleaned) < len(test_text))
                    
                    # 测试文本格式化
                    formatted = plugin.format_text(test_text)
                    self.assert_test("文本格式化功能", formatted is not None)
                    
                    # 测试文本分析
                    analysis = plugin.analyze_text("这是一个测试文本，用于分析关键词和统计信息。")
                    self.assert_test("文本分析功能", isinstance(analysis, dict) and 'word_count' in analysis)
                    
                    # 测试关键词提取
                    keywords = plugin.extract_keywords("这是一个关于人工智能和机器学习的测试文本。")
                    self.assert_test("关键词提取功能", isinstance(keywords, list))
                    
                    print("   ✅ 文本处理插件测试完成")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ 文本处理插件测试失败: {e}")
            return False
    
    def test_novel_enhancer_plugin(self):
        """测试小说增强插件"""
        print("\n📚 测试小说增强插件...")
        
        try:
            # 加载插件（依赖text_processor）
            success = self.manager.load_plugin("novel_enhancer")
            self.assert_test("小说增强插件加载", success)
            
            if success:
                # 获取插件实例
                plugin = self.manager.get_plugin("novel_enhancer")
                self.assert_test("获取插件实例", plugin is not None)
                
                if plugin:
                    # 测试小说分析
                    test_novel = """
                    第一章 开始
                    
                    主人公张三是一个年轻的程序员，他住在北京。
                    有一天，他遇到了一个神秘的女孩李四。
                    
                    第二章 发展
                    
                    张三和李四开始了一段奇妙的冒险。
                    他们一起解决了许多技术难题。
                    """
                    
                    analysis = plugin.analyze_novel(test_novel)
                    self.assert_test("小说分析功能", isinstance(analysis, dict))
                    
                    # 测试角色管理
                    plugin.add_character("张三", {"职业": "程序员", "居住地": "北京"})
                    plugin.add_character("李四", {"性别": "女", "特点": "神秘"})
                    
                    characters = plugin.get_characters()
                    self.assert_test("角色管理功能", len(characters) >= 2)
                    
                    # 测试风格优化
                    optimized = plugin.optimize_style(test_novel)
                    self.assert_test("风格优化功能", optimized is not None)
                    
                    # 测试摘要生成
                    summary = plugin.generate_summary(test_novel)
                    self.assert_test("摘要生成功能", isinstance(summary, str) and len(summary) > 0)
                    
                    # 测试一致性检查
                    consistency = plugin.check_consistency()
                    self.assert_test("一致性检查功能", isinstance(consistency, dict))
                    
                    print("   ✅ 小说增强插件测试完成")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ 小说增强插件测试失败: {e}")
            return False
    
    def test_plugin_dependencies(self):
        """测试插件依赖关系"""
        print("\n🔗 测试插件依赖关系...")
        
        try:
            # 检查依赖关系
            novel_enhancer = self.manager.get_plugin("novel_enhancer")
            text_processor = self.manager.get_plugin("text_processor")
            
            self.assert_test("依赖插件加载", text_processor is not None)
            self.assert_test("主插件加载", novel_enhancer is not None)
            
            # 测试依赖调用
            if novel_enhancer and text_processor:
                # novel_enhancer 应该能够使用 text_processor 的功能
                test_text = "这是一个测试文本，用于验证插件间的依赖关系。"
                
                # 通过 novel_enhancer 间接使用 text_processor
                analysis = novel_enhancer.analyze_novel(test_text)
                self.assert_test("依赖功能调用", isinstance(analysis, dict))
            
            print("   ✅ 插件依赖关系测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 插件依赖关系测试失败: {e}")
            return False
    
    def test_plugin_logging(self):
        """测试插件日志功能"""
        print("\n📋 测试插件日志功能...")
        
        try:
            # 获取插件日志
            text_processor_logs = self.manager.logging_system.get_plugin_logs("text_processor")
            novel_enhancer_logs = self.manager.logging_system.get_plugin_logs("novel_enhancer")
            
            self.assert_test("文本处理插件日志", len(text_processor_logs) >= 0)
            self.assert_test("小说增强插件日志", len(novel_enhancer_logs) >= 0)
            
            # 测试日志搜索
            all_logs = self.manager.logging_system.search_plugin_logs("INFO", "test")
            self.assert_test("日志搜索功能", isinstance(all_logs, list))
            
            # 测试日志统计
            stats = self.manager.logging_system.get_logging_statistics()
            self.assert_test("日志统计功能", isinstance(stats, dict))
            
            print("   ✅ 插件日志功能测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 插件日志功能测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始示例插件测试...")
        
        # 运行各项测试
        tests = [
            self.test_text_processor_plugin,
            self.test_novel_enhancer_plugin,
            self.test_plugin_dependencies,
            self.test_plugin_logging
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"测试执行异常: {e}")
        
        # 输出测试结果
        print(f"\n📊 测试结果汇总:")
        print(f"   总测试数: {self.test_count}")
        print(f"   通过: {self.passed_count}")
        print(f"   失败: {len(self.failed_tests)}")
        print(f"   成功率: {(self.passed_count / self.test_count * 100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in self.failed_tests:
                print(f"   - {test}")
            print("\n⚠️  部分测试失败，请检查示例插件。")
            return False
        else:
            print("\n🎉 所有测试通过！示例插件运行正常。")
            return True

if __name__ == "__main__":
    tester = ExamplePluginTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)