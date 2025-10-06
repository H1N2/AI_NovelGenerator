#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件系统测试脚本
测试插件管理器、崩溃处理、日志系统和事件系统的功能
"""

import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins import (
    PluginManager, 
    PluginLoggingSystem, 
    get_plugin_logging_system,
    PluginCrashHandler,
    get_crash_handler,
    PluginEventSystem,
    AppEvents,
    LogLevel
)

class PluginSystemTester:
    """插件系统测试器"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        
    def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="plugin_test_")
        print(f"   临时目录: {self.temp_dir}")
        
        # 创建测试插件目录
        test_plugin_dir = Path(self.temp_dir) / "test_plugin"
        test_plugin_dir.mkdir()
        
        # 创建测试插件配置
        plugin_config = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "测试插件",
            "author": "Test",
            "main": "main.py",
            "dependencies": [],
            "permissions": ["read", "write"],
            "config": {
                "enabled": True,
                "auto_start": True,
                "debug_mode": True
            }
        }
        
        with open(test_plugin_dir / "plugin.json", "w", encoding="utf-8") as f:
            json.dump(plugin_config, f, indent=2, ensure_ascii=False)
        
        # 创建测试插件主文件
        plugin_main = '''
from plugins.base import BasePlugin

class TestPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.test_data = []
        
    def initialize(self):
        """初始化插件"""
        self.logger.info("测试插件初始化")
        return True
        
    def cleanup(self):
        """清理插件"""
        self.logger.info("测试插件清理")
        
    def get_info(self):
        """获取插件信息"""
        return {
            "name": "test_plugin",
            "version": "1.0.0",
            "status": "active"
        }
        
    def test_crash(self):
        """测试崩溃"""
        raise Exception("测试崩溃异常")
        
    def test_logging(self):
        """测试日志功能"""
        self.logger.debug("调试信息")
        self.logger.info("信息日志")
        self.logger.warning("警告信息")
        self.logger.error("错误信息")
        
def create_plugin():
    return TestPlugin()
'''
        
        with open(test_plugin_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(plugin_main)
            
        return str(test_plugin_dir)
    
    def test_plugin_manager(self):
        """测试插件管理器"""
        print("\n📦 测试插件管理器...")
        
        try:
            # 创建模拟应用实例
            class MockApp:
                def __init__(self):
                    self.version = "1.0.0"
            
            mock_app = MockApp()
            
            # 创建插件管理器
            manager = PluginManager(mock_app)
            
            # 测试基本功能
            self.assert_test("插件管理器创建", manager is not None)
            self.assert_test("插件目录设置", hasattr(manager, 'plugins_dir'))
            self.assert_test("日志系统集成", hasattr(manager, 'logging_system'))
            self.assert_test("崩溃处理集成", hasattr(manager, 'crash_handler'))
            self.assert_test("事件系统集成", hasattr(manager, 'event_system'))
            
            print("   ✅ 插件管理器测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 插件管理器测试失败: {e}")
            return False
    
    def test_crash_handler(self):
        """测试崩溃处理系统"""
        print("\n💥 测试崩溃处理系统...")
        
        try:
            # 获取崩溃处理器
            crash_handler = get_crash_handler()
            
            # 测试基本功能
            self.assert_test("崩溃处理器创建", crash_handler is not None)
            self.assert_test("崩溃记录存储", hasattr(crash_handler, '_crash_records'))
            
            # 模拟插件崩溃
            test_exception = Exception("测试崩溃")
            crash_handler.handle_crash("test_plugin", test_exception)
            
            # 检查崩溃记录
            records = crash_handler.get_crash_history("test_plugin")
            self.assert_test("崩溃记录", len(records) > 0)
            
            # 测试统计功能
            stats = crash_handler.get_crash_statistics("test_plugin")
            self.assert_test("崩溃统计", isinstance(stats, dict) and 'total_crashes' in stats)
            
            print("   ✅ 崩溃处理系统测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 崩溃处理系统测试失败: {e}")
            return False
    
    def test_logging_system(self):
        """测试日志系统"""
        print("\n📝 测试日志系统...")
        
        try:
            # 获取日志系统
            logging_system = get_plugin_logging_system()
            
            # 测试基本功能
            self.assert_test("日志系统创建", logging_system is not None)
            
            # 创建插件日志器
            logger = logging_system.create_plugin_logger("test_plugin")
            self.assert_test("插件日志器创建", logger is not None)
            
            # 测试日志记录
            logger.info("测试信息日志")
            logger.warning("测试警告日志")
            logger.error("测试错误日志")
            
            # 测试日志搜索
            logs = logging_system.search_plugin_logs("test_plugin", "测试")
            self.assert_test("日志搜索", len(logs) > 0)
            
            # 测试统计功能
            stats = logging_system.get_logging_statistics()
            self.assert_test("日志统计", "test_plugin" in stats)
            
            # 清理日志器
            logging_system.remove_plugin_logger("test_plugin")
            
            print("   ✅ 日志系统测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 日志系统测试失败: {e}")
            return False
    
    def test_event_system(self):
        """测试事件系统"""
        print("\n⚡ 测试事件系统...")
        
        try:
            # 创建事件系统
            event_system = PluginEventSystem()
            
            # 测试基本功能
            self.assert_test("事件系统创建", event_system is not None)
            
            # 测试事件注册
            event_received = []
            
            def test_handler(event):
                event_received.append(event.name)
            
            event_system.register_handler("test.event", test_handler, "test_plugin")
            
            # 测试事件发送
            event_system.emit_event("test.event", {"test": "data"})
            
            # 等待事件处理
            time.sleep(0.1)
            
            self.assert_test("事件处理", len(event_received) > 0)
            
            # 测试事件历史
            history = event_system.get_event_history()
            self.assert_test("事件历史", len(history) > 0)
            
            # 测试性能统计
            stats = event_system.get_statistics()
            self.assert_test("性能统计", len(stats) > 0)
            
            print("   ✅ 事件系统测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 事件系统测试失败: {e}")
            return False
    
    def test_integration(self):
        """测试系统集成"""
        print("\n🔗 测试系统集成...")
        
        try:
            # 创建模拟应用实例
            class MockApp:
                def __init__(self):
                    self.version = "1.0.0"
            
            mock_app = MockApp()
            
            # 创建完整的插件管理器
            manager = PluginManager(mock_app)
            
            # 测试基本集成
            self.assert_test("集成测试-插件管理器创建", manager is not None)
            self.assert_test("集成测试-日志系统", hasattr(manager, 'logging_system'))
            self.assert_test("集成测试-崩溃处理", hasattr(manager, 'crash_handler'))
            self.assert_test("集成测试-事件系统", hasattr(manager, 'event_system'))
            
            # 测试事件发送
            manager.event_system.emit_event("test.integration", {
                "test": "data"
            })
            
            print("   ✅ 系统集成测试完成")
            return True
            
        except Exception as e:
            print(f"   ❌ 系统集成测试失败: {e}")
            return False
    
    def assert_test(self, test_name, condition):
        """断言测试结果"""
        result = bool(condition)
        self.test_results.append((test_name, result))
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}: {'通过' if result else '失败'}")
        return result
    
    def cleanup(self):
        """清理测试环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 清理临时目录: {self.temp_dir}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始插件系统测试...\n")
        
        tests = [
            self.test_plugin_manager,
            self.test_crash_handler,
            self.test_logging_system,
            self.test_event_system,
            self.test_integration
        ]
        
        passed = 0
        total = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                total += 1
            except Exception as e:
                print(f"❌ 测试执行失败: {e}")
                total += 1
        
        # 显示测试结果
        print(f"\n📊 测试结果汇总:")
        print(f"   总测试数: {len(self.test_results)}")
        print(f"   通过: {sum(1 for _, result in self.test_results if result)}")
        print(f"   失败: {sum(1 for _, result in self.test_results if not result)}")
        print(f"   成功率: {sum(1 for _, result in self.test_results if result) / len(self.test_results) * 100:.1f}%")
        
        # 显示失败的测试
        failed_tests = [name for name, result in self.test_results if not result]
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test_name in failed_tests:
                print(f"   - {test_name}")
        
        self.cleanup()
        
        return len(failed_tests) == 0

def main():
    """主函数"""
    tester = PluginSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！插件系统运行正常。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查插件系统。")
        return 1

if __name__ == "__main__":
    sys.exit(main())