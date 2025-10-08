#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实LLM配置测试脚本
使用有效的API密钥测试LLM配置功能
"""

import sys
from config_manager import load_config, test_llm_config


def test_real_llm_config():
    """测试真实的LLM配置"""
    print("=== 测试真实LLM配置 ===")
    
    # 加载配置
    config = load_config('config.json')
    if not config or 'llm_configs' not in config:
        print("❌ 无法加载配置文件")
        return False
    
    # 查找有效的配置（有API密钥的）
    valid_configs = []
    for name, llm_config in config['llm_configs'].items():
        api_key = llm_config.get('api_key', '').strip()
        if api_key and api_key != '':
            valid_configs.append((name, llm_config))
    
    if not valid_configs:
        print("❌ 没有找到有效的LLM配置（需要API密钥）")
        return False
    
    print(f"找到 {len(valid_configs)} 个有效配置")
    
    # 测试每个有效配置
    test_results = []
    for name, llm_config in valid_configs:
        print(f"\n--- 测试配置: {name} ---")
        
        def log_func(msg):
            print(f"[{name}] {msg}")
        
        def exception_func(msg):
            print(f"[{name}] 异常: {msg}")
        
        try:
            result = test_llm_config(
                interface_format=llm_config.get('interface_format', 'OpenAI'),
                api_key=llm_config.get('api_key', ''),
                base_url=llm_config.get('base_url', ''),
                model_name=llm_config.get('model_name', ''),
                temperature=llm_config.get('temperature', 0.7),
                max_tokens=llm_config.get('max_tokens', 1000),
                timeout=llm_config.get('timeout', 30),
                log_func=log_func,
                handle_exception_func=exception_func
            )
            
            test_results.append((name, result))
            print(f"[{name}] 测试结果: {'✅ 成功' if result else '❌ 失败'}")
            
        except Exception as e:
            print(f"[{name}] 测试异常: {e}")
            test_results.append((name, False))
    
    # 总结结果
    print("\n=== 测试总结 ===")
    successful_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for name, result in test_results:
        print(f"{name}: {'✅' if result else '❌'}")
    
    print(f"\n成功: {successful_tests}/{total_tests}")
    print(f"总体结果: {'✅ 测试通过' if successful_tests > 0 else '❌ 所有测试失败'}")
    
    return successful_tests > 0


def test_config_controller_integration():
    """测试配置控制器集成"""
    print("\n=== 测试配置控制器集成 ===")
    
    try:
        from ui.controllers.config_controller import ConfigController
        import asyncio
        
        # 创建配置控制器
        controller = ConfigController()
        
        # 加载配置
        controller.load_config()
        
        # 获取LLM配置名称
        llm_configs = controller.get_llm_config_names()
        print(f"可用LLM配置: {llm_configs}")
        
        # 测试有效配置
        config = load_config('config.json')
        valid_config_name = None
        
        for name in llm_configs:
            llm_config = config['llm_configs'].get(name, {})
            api_key = llm_config.get('api_key', '').strip()
            if api_key and api_key != '':
                valid_config_name = name
                break
        
        if valid_config_name:
            print(f"使用配置进行测试: {valid_config_name}")
            
            # 设置当前配置
            controller.set_current_llm_config(valid_config_name)
            
            # 异步测试配置
            async def async_test():
                try:
                    result = await controller.test_llm_configuration()
                    return result
                except Exception as e:
                    print(f"异步测试异常: {e}")
                    return False
            
            # 运行异步测试
            result = asyncio.run(async_test())
            print(f"配置控制器测试结果: {'✅ 成功' if result else '❌ 失败'}")
            return result
        else:
            print("❌ 没有找到有效的配置进行测试")
            return False
            
    except Exception as e:
        print(f"❌ 配置控制器集成测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("开始真实LLM配置测试...\n")
    
    # 测试基本配置功能
    basic_test_passed = test_real_llm_config()
    
    # 测试配置控制器集成
    integration_test_passed = test_config_controller_integration()
    
    # 总结
    print("\n=== 最终总结 ===")
    print(f"基本配置测试: {'✅' if basic_test_passed else '❌'}")
    print(f"控制器集成测试: {'✅' if integration_test_passed else '❌'}")
    
    overall_success = basic_test_passed and integration_test_passed
    print(f"整体测试结果: {'✅ 所有测试通过' if overall_success else '❌ 部分测试失败'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)