#!/usr/bin/env python3
"""
LLM测试连接诊断脚本
用于分析LLM模型测试连接无反应的问题
"""

import sys
import asyncio
import traceback
from ui.controllers.config_controller import ConfigController
from ui.config_models import ConfigurationManager


async def test_llm_connection():
    """诊断LLM测试连接问题"""
    print('=== LLM测试连接诊断 ===')
    
    try:
        # 1. 创建ConfigurationManager
        config_manager = ConfigurationManager()
        print(f'✓ ConfigurationManager创建: {config_manager}')
        
        # 2. 加载配置
        load_result = config_manager.load_configuration()
        print(f'✓ 配置加载结果: {load_result}')
        
        # 获取配置数据
        llm_count = len(config_manager.llm_config_names)
        print(f'✓ 配置数据加载: {llm_count} 个LLM配置')
        
        if llm_count == 0:
            print('❌ 错误: 没有找到LLM配置')
            return False
        
        # 3. 创建ConfigController
        controller = ConfigController()
        controller.set_model(config_manager)
        print(f'✓ ConfigController创建: {controller}')
        
        # 4. 初始化控制器
        print('正在初始化控制器...')
        init_result = await controller.initialize()
        print(f'✓ 控制器初始化结果: {init_result}')
        
        if not init_result:
            print('❌ 错误: 控制器初始化失败')
            return False
        
        # 5. 检查当前配置
        current_config = controller.get_current_llm_config()
        has_config = current_config is not None
        print(f'✓ 当前LLM配置存在: {has_config}')
        
        if current_config:
            print(f'  - 接口格式: {current_config.get("interface_format")}')
            print(f'  - 模型名称: {current_config.get("model_name")}')
            print(f'  - API密钥: {"已设置" if current_config.get("api_key") else "未设置"}')
            print(f'  - 基础URL: {current_config.get("base_url")}')
        else:
            print('❌ 错误: 无法获取当前LLM配置')
            return False
        
        # 6. 尝试测试连接
        print('正在测试LLM连接...')
        test_result = await controller.test_llm_configuration()
        print(f'✓ 测试连接结果: {test_result}')
        
        return test_result
        
    except Exception as e:
        print(f'❌ 测试连接异常: {e}')
        print(f'异常详情: {traceback.format_exc()}')
        return False


def main():
    """主函数"""
    try:
        result = asyncio.run(test_llm_connection())
        if result:
            print('\n🎉 LLM测试连接成功!')
        else:
            print('\n💥 LLM测试连接失败!')
    except Exception as e:
        print(f'\n💥 脚本执行失败: {e}')
        print(f'详细错误: {traceback.format_exc()}')


if __name__ == "__main__":
    main()