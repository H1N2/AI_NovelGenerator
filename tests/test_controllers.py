"""
控制器测试文档
用于验证MVP架构重构后的控制器功能
"""
import unittest
import asyncio
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# 导入控制器类
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ui.controllers.base_controller import BaseController, ControllerState, ControllerEvent, ControllerRegistry
from ui.controllers.config_controller import ConfigController
from ui.controllers.novel_controller import NovelController
from ui.controllers.generation_controller import GenerationController


class TestController(BaseController):
    """测试用的控制器实现"""
    def __init__(self, name: str):
        super().__init__(name)
    
    async def initialize(self) -> bool:
        """初始化控制器"""
        return True
    
    async def cleanup(self) -> None:
        """清理控制器"""
        pass


class TestBaseController(unittest.TestCase):
    """测试基础控制器类"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = TestController("TestController")
        self.mock_model = Mock()
        self.mock_view = Mock()
    
    def test_controller_initialization(self):
        """测试控制器初始化"""
        self.assertEqual(self.controller.name, "TestController")
        self.assertEqual(self.controller.state, ControllerState.IDLE)
        self.assertIsNone(self.controller.model)
        self.assertIsNone(self.controller.view)
    
    def test_set_model_view(self):
        """测试设置模型和视图"""
        self.controller.set_model(self.mock_model)
        self.controller.set_view(self.mock_view)
        
        self.assertEqual(self.controller.model, self.mock_model)
        self.assertEqual(self.controller.view, self.mock_view)
    
    def test_state_management(self):
        """测试状态管理"""
        # 测试状态变更
        self.controller.set_state(ControllerState.PROCESSING)
        self.assertEqual(self.controller.state, ControllerState.PROCESSING)
        
        # 测试状态事件发出
        events = []
        def capture_event(event):
            events.append(event)
        
        self.controller.add_event_listener("state_changed", capture_event)
        self.controller.set_state(ControllerState.COMPLETED)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "state_changed")
        self.assertEqual(events[0].data["new_state"], ControllerState.COMPLETED)
    
    def test_event_system(self):
        """测试事件系统"""
        events = []
        def event_handler(event):
            events.append(event)
        
        # 添加事件监听器
        self.controller.add_event_listener("test_event", event_handler)
        
        # 发出事件
        test_event = ControllerEvent(
            event_type="test_event",
            source="TestController",
            data={"test": "data"}
        )
        self.controller.emit_event(test_event)
        
        # 验证事件被接收
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "test_event")
        self.assertEqual(events[0].data["test"], "data")
        
        # 移除事件监听器
        self.controller.remove_event_listener("test_event", event_handler)
        self.controller.emit_event(test_event)
        
        # 验证事件不再被接收
        self.assertEqual(len(events), 1)
    
    def test_error_handling(self):
        """测试错误处理"""
        with patch.object(self.controller, 'logger') as mock_logger:
            test_error = Exception("测试错误")
            self.controller._handle_error(test_error, "测试操作")
            
            # 验证错误被记录
            mock_logger.error.assert_called()
            
            # 验证状态被设置为错误
            self.assertEqual(self.controller.state, ControllerState.ERROR)


class TestControllerRegistry(unittest.TestCase):
    """测试控制器注册表"""
    
    def setUp(self):
        """测试前准备"""
        self.registry = ControllerRegistry()
        self.controller1 = TestController("Controller1")
        self.controller2 = TestController("Controller2")
    
    def test_register_controller(self):
        """测试注册控制器"""
        self.registry.register(self.controller1)
        self.assertEqual(self.registry.get("Controller1"), self.controller1)
    
    def test_unregister_controller(self):
        """测试注销控制器"""
        self.registry.register(self.controller1)
        self.registry.unregister("Controller1")
        self.assertIsNone(self.registry.get("Controller1"))
    
    def test_get_all_controllers(self):
        """测试获取所有控制器"""
        self.registry.register(self.controller1)
        self.registry.register(self.controller2)
        
        controllers = self.registry.get_all()
        self.assertEqual(len(controllers), 2)
        self.assertIn(self.controller1, controllers.values())
        self.assertIn(self.controller2, controllers.values())


class TestConfigController(unittest.TestCase):
    """测试配置控制器"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = ConfigController()
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # 设置模拟数据
        self.mock_model.get_data.return_value = {}
        self.mock_model.set_data = Mock()
        
        self.controller.set_model(self.mock_model)
        self.controller.set_view(self.mock_view)
    
    def test_initialization(self):
        """测试初始化"""
        async def run_test():
            result = await self.controller.initialize()
            self.assertTrue(result)
            self.assertEqual(self.controller.state, ControllerState.IDLE)
        
        asyncio.run(run_test())
    
    def test_add_llm_config(self):
        """测试添加LLM配置"""
        config_data = {
            "name": "test_llm",
            "interface_format": "OpenAI",
            "api_key": "test_key",
            "base_url": "https://api.test.com",
            "model_name": "gpt-3.5-turbo"
        }
        
        async def run_test():
            result = await self.controller.add_llm_config("test_llm", config_data)
            self.assertTrue(result)
            
            # 验证模型数据被更新
            self.mock_model.set_data.assert_called()
        
        asyncio.run(run_test())
    
    def test_validate_llm_config(self):
        """测试LLM配置验证"""
        # 有效配置
        valid_config = {
            "name": "test_llm",
            "interface_format": "OpenAI",
            "api_key": "test_key",
            "base_url": "https://api.test.com",
            "model_name": "gpt-3.5-turbo"
        }
        self.assertTrue(self.controller._validate_llm_config(valid_config))
        
        # 无效配置 - 缺少必要字段
        invalid_config = {
            "name": "test_llm",
            "interface_format": "OpenAI"
            # 缺少其他必要字段
        }
        self.assertFalse(self.controller._validate_llm_config(invalid_config))
    
    def test_remove_llm_config(self):
        """测试移除LLM配置"""
        # 设置现有配置
        existing_configs = {
            "test_llm": {
                "name": "test_llm",
                "interface_format": "OpenAI"
            }
        }
        self.mock_model.get_data.return_value = existing_configs
        
        async def run_test():
            result = await self.controller.remove_llm_config("test_llm")
            self.assertTrue(result)
            
            # 验证配置被移除
            self.mock_model.set_data.assert_called()
        
        asyncio.run(run_test())


class TestNovelController(unittest.TestCase):
    """测试小说控制器"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = NovelController()
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        
        self.controller.set_model(self.mock_model)
        self.controller.set_view(self.mock_view)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        async def run_test():
            result = await self.controller.initialize()
            self.assertTrue(result)
            self.assertEqual(self.controller.state, ControllerState.IDLE)
        
        asyncio.run(run_test())
    
    def test_create_new_project(self):
        """测试创建新项目"""
        project_data = {
            "project_name": "测试小说",
            "topic": "科幻冒险",
            "genre": "科幻",
            "num_chapters": 10,
            "word_number": 100000,
            "filepath": os.path.join(self.temp_dir, "test_novel"),
            "user_guidance": "测试指导"
        }
        
        async def run_test():
            result = await self.controller.create_new_project(project_data)
            self.assertTrue(result)
            
            # 验证项目目录被创建
            self.assertTrue(os.path.exists(project_data["filepath"]))
            
            # 验证项目配置文件被创建
            config_path = os.path.join(project_data["filepath"], "project_config.json")
            self.assertTrue(os.path.exists(config_path))
            
            # 验证配置内容
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.assertEqual(config["project_name"], project_data["project_name"])
            self.assertEqual(config["topic"], project_data["topic"])
            self.assertEqual(config["genre"], project_data["genre"])
        
        asyncio.run(run_test())
    
    def test_load_project(self):
        """测试加载项目"""
        # 先创建一个项目
        project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(project_path, exist_ok=True)
        
        # 创建项目配置文件
        config = {
            "project_name": "测试项目",
            "topic": "测试主题",
            "genre": "测试类型",
            "num_chapters": 5,
            "word_number": 50000
        }
        
        config_path = os.path.join(project_path, "project_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        async def run_test():
            result = await self.controller.load_project(project_path)
            self.assertTrue(result)
            
            # 验证当前项目被设置
            current_project = self.controller.get_current_project()
            self.assertIsNotNone(current_project)
            self.assertEqual(current_project["path"], project_path)
            self.assertEqual(current_project["config"]["project_name"], "测试项目")
        
        asyncio.run(run_test())
    
    def test_project_validation(self):
        """测试项目数据验证"""
        # 有效项目数据
        valid_data = {
            "project_name": "测试小说",
            "topic": "科幻冒险",
            "genre": "科幻",
            "num_chapters": 10,
            "word_number": 100000,
            "filepath": "/path/to/project"
        }
        self.assertTrue(self.controller._validate_project_data(valid_data))
        
        # 无效项目数据 - 缺少必要字段
        invalid_data = {
            "project_name": "测试小说",
            "topic": "科幻冒险"
            # 缺少其他必要字段
        }
        self.assertFalse(self.controller._validate_project_data(invalid_data))
        
        # 无效项目数据 - 数值字段不是数字
        invalid_numeric_data = {
            "project_name": "测试小说",
            "topic": "科幻冒险",
            "genre": "科幻",
            "num_chapters": "不是数字",
            "word_number": 100000,
            "filepath": "/path/to/project"
        }
        self.assertFalse(self.controller._validate_project_data(invalid_numeric_data))


class TestGenerationController(unittest.TestCase):
    """测试生成控制器"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = GenerationController()
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # 设置模拟LLM配置
        self.mock_llm_config = {
            "interface_format": "OpenAI",
            "api_key": "test_key",
            "base_url": "https://api.test.com",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600
        }
        
        # 设置模拟数据
        self.mock_model.get_data.side_effect = lambda key, default=None: {
            "choose_configs": {
                "architecture_llm": "test_config"
            },
            "llm_configs": {
                "test_config": self.mock_llm_config
            }
        }.get(key, default)
        
        self.controller.set_model(self.mock_model)
        self.controller.set_view(self.mock_view)
    
    def test_initialization(self):
        """测试初始化"""
        async def run_test():
            result = await self.controller.initialize()
            self.assertTrue(result)
            self.assertEqual(self.controller.state, ControllerState.IDLE)
        
        asyncio.run(run_test())
    
    def test_get_llm_config_for_task(self):
        """测试获取任务LLM配置"""
        config = self.controller._get_llm_config_for_task("architecture")
        self.assertIsNotNone(config)
        self.assertEqual(config["model_name"], "gpt-3.5-turbo")
    
    def test_validate_architecture_params(self):
        """测试架构生成参数验证"""
        # 有效参数
        valid_params = {
            "topic": "科幻小说",
            "genre": "科幻",
            "num_chapters": 10,
            "word_number": 100000,
            "filepath": "/path/to/project"
        }
        self.assertTrue(self.controller._validate_architecture_params(valid_params))
        
        # 无效参数 - 缺少必要字段
        invalid_params = {
            "topic": "科幻小说",
            "genre": "科幻"
            # 缺少其他必要字段
        }
        self.assertFalse(self.controller._validate_architecture_params(invalid_params))
    
    def test_validate_blueprint_params(self):
        """测试蓝图生成参数验证"""
        # 有效参数
        valid_params = {
            "chapter_num": 1,
            "filepath": "/path/to/project"
        }
        self.assertTrue(self.controller._validate_blueprint_params(valid_params))
        
        # 无效参数
        invalid_params = {
            "chapter_num": 1
            # 缺少filepath
        }
        self.assertFalse(self.controller._validate_blueprint_params(invalid_params))
    
    def test_generation_callbacks(self):
        """测试生成回调系统"""
        callback_called = []
        
        def test_callback(success, params):
            callback_called.append((success, params))
        
        # 添加回调
        self.controller.add_generation_callback("architecture", test_callback)
        
        # 调用回调
        test_params = {"test": "data"}
        self.controller._call_generation_callbacks("architecture", True, test_params)
        
        # 验证回调被调用
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0][0], True)
        self.assertEqual(callback_called[0][1], test_params)
        
        # 移除回调
        self.controller.remove_generation_callback("architecture", test_callback)
        self.controller._call_generation_callbacks("architecture", True, test_params)
        
        # 验证回调不再被调用
        self.assertEqual(len(callback_called), 1)
    
    def test_task_management(self):
        """测试任务管理"""
        # 测试获取当前任务
        self.assertIsNone(self.controller.get_current_task())
        
        # 设置当前任务
        self.controller._current_task = "test_task"
        self.assertEqual(self.controller.get_current_task(), "test_task")
        
        # 测试取消任务
        self.controller.cancel_current_task()
        self.assertIsNone(self.controller.get_current_task())
        self.assertEqual(self.controller.state, ControllerState.IDLE)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.registry = ControllerRegistry()
        self.config_controller = ConfigController()
        self.novel_controller = NovelController()
        self.generation_controller = GenerationController()
        
        # 注册控制器
        self.registry.register(self.config_controller)
        self.registry.register(self.novel_controller)
        self.registry.register(self.generation_controller)
        
        # 创建模拟模型和视图
        self.mock_model = Mock()
        self.mock_view = Mock()
        
        # 设置控制器
        for controller in self.registry.get_all().values():
            controller.set_model(self.mock_model)
            controller.set_view(self.mock_view)
    
    def test_controller_registry_integration(self):
        """测试控制器注册表集成"""
        # 验证所有控制器都已注册
        controllers = self.registry.get_all()
        self.assertEqual(len(controllers), 3)
        
        # 验证可以通过名称获取控制器
        config_ctrl = self.registry.get("ConfigController")
        self.assertIsInstance(config_ctrl, ConfigController)
        
        novel_ctrl = self.registry.get("NovelController")
        self.assertIsInstance(novel_ctrl, NovelController)
        
        generation_ctrl = self.registry.get("GenerationController")
        self.assertIsInstance(generation_ctrl, GenerationController)
    
    def test_controller_communication(self):
        """测试控制器间通信"""
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        # 设置事件监听
        self.novel_controller.add_event_listener("project_created", event_handler)
        
        # 模拟项目创建事件
        test_event = ControllerEvent(
            event_type="project_created",
            source="NovelController",
            data={"project_name": "测试项目"}
        )
        
        self.novel_controller.emit_event(test_event)
        
        # 验证事件被接收
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].event_type, "project_created")


def run_controller_tests():
    """运行所有控制器测试"""
    print("**开始运行控制器测试...**")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestBaseController,
        TestControllerRegistry,
        TestConfigController,
        TestNovelController,
        TestGenerationController,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n**测试结果:**")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n**失败的测试:**")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\n**错误的测试:**")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n**测试{'通过' if success else '失败'}**")
    
    return success


if __name__ == "__main__":
    run_controller_tests()