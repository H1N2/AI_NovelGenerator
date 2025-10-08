#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证测试脚本
用于验证LLM配置和测试功能的完整性
"""

import sys
import json
from typing import Dict, Any
from config_manager import load_config, test_llm_config


def test_config_loading() -> bool:
    """测试配置加载功能"""
    print("=== 测试配置加载 ===")
    try:
        config = load_config('config.json')
        if config:
            print("✅ 配置加载成功")
            print(f"LLM配置数量: {len(config.get('llm_configs', {}))}")
            print(f"嵌入模型配置数量: {len(config.get('embedding_configs', {}))}")
            return True
        else:
            print("❌ 配置加载失败")
            return False
    except Exception as e:
        print(f"❌ 配置加载异常: {e}")
        return False


def test_llm_config_validation(config: Dict[str, Any]) -> bool:
    """测试LLM配置验证"""
    print("\n=== 测试LLM配置验证 ===")
    if not config or 'llm_configs' not in config:
        print("❌ 没有找到LLM配置")
        return False
    
    all_valid = True
    required_fields = ['api_key', 'base_url', 'model_name', 'interface_format']
    
    for name, llm_config in config['llm_configs'].items():
        print(f"配置名称: {name}")
        missing_fields = [field for field in required_fields if not llm_config.get(field)]
        
        if missing_fields:
            print(f"❌ 缺少必要字段: {missing_fields}")
            all_valid = False
        else:
            print("✅ 配置字段完整")
        
        # 检查字段值是否为空
        empty_fields = [field for field in required_fields 
                       if field in llm_config and not str(llm_config[field]).strip()]
        if empty_fields:
            print(f"⚠️  字段值为空: {empty_fields}")
            all_valid = False
        
        print()
    
    return all_valid


def test_config_structure(config: Dict[str, Any]) -> bool:
    """测试配置结构完整性"""
    print("=== 测试配置结构 ===")
    required_sections = ['llm_configs', 'embedding_configs', 'other_params']
    missing_sections = [section for section in required_sections if section not in config]
    
    if missing_sections:
        print(f"❌ 缺少配置节: {missing_sections}")
        return False
    else:
        print("✅ 配置结构完整")
        return True


def test_mock_llm_function():
    """测试LLM测试函数的基本功能（模拟测试）"""
    print("\n=== 测试LLM测试函数 ===")
    
    def mock_log(msg):
        print(f"[LOG] {msg}")
    
    def mock_exception_handler(msg):
        print(f"[EXCEPTION] {msg}")
    
    # 测试无效配置
    try:
        result = test_llm_config(
            interface_format="",
            api_key="",
            base_url="",
            model_name="",
            temperature=0.7,
            max_tokens=1000,
            timeout=30,
            log_func=mock_log,
            handle_exception_func=mock_exception_handler
        )
        print(f"无效配置测试结果: {result}")
        return result is False  # 应该返回False
    except Exception as e:
        print(f"测试函数异常: {e}")
        return True  # 异常处理正常


def main():
    """主测试函数"""
    print("开始配置验证测试...\n")
    
    # 测试配置加载
    config = load_config('config.json')
    config_loaded = test_config_loading()
    
    if not config_loaded or not config:
        print("\n❌ 配置加载失败，无法继续测试")
        return False
    
    # 测试配置结构
    structure_valid = test_config_structure(config)
    
    # 测试LLM配置验证
    llm_valid = test_llm_config_validation(config)
    
    # 测试LLM测试函数
    function_valid = test_mock_llm_function()
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"配置加载: {'✅' if config_loaded else '❌'}")
    print(f"配置结构: {'✅' if structure_valid else '❌'}")
    print(f"LLM配置验证: {'✅' if llm_valid else '❌'}")
    print(f"测试函数: {'✅' if function_valid else '❌'}")
    
    all_passed = all([config_loaded, structure_valid, llm_valid, function_valid])
    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)