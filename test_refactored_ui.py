"""
测试重构后的UI功能完整性
确保重构不会破坏原有功能
"""
import sys
import os
import customtkinter as ctk
from tkinter import messagebox

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_original_ui():
    """测试原始UI"""
    try:
        from ui.main_window import NovelGeneratorGUI as OriginalGUI
        
        root = ctk.CTk()
        root.withdraw()  # 隐藏窗口，只测试初始化
        
        app = OriginalGUI(root)
        
        # 测试基本属性
        assert hasattr(app, 'master'), "缺少master属性"
        assert hasattr(app, 'tabview'), "缺少tabview属性"
        assert hasattr(app, 'api_key_var'), "缺少api_key_var属性"
        assert hasattr(app, 'config_file'), "缺少config_file属性"
        
        # 测试基本方法
        assert hasattr(app, 'show_tooltip'), "缺少show_tooltip方法"
        assert hasattr(app, 'safe_get_int'), "缺少safe_get_int方法"
        assert hasattr(app, 'test_llm_config'), "缺少test_llm_config方法"
        
        # 安全销毁窗口
        try:
            root.quit()
            root.update()
        except:
            pass
        finally:
            try:
                root.destroy()
            except:
                pass
        return True, "原始UI测试通过"
        
    except Exception as e:
        try:
            if 'root' in locals():
                root.quit()
                root.destroy()
        except:
            pass
        return False, f"原始UI测试失败: {str(e)}"

def test_refactored_ui():
    """测试重构后的UI"""
    try:
        from ui.main_window_refactored import NovelGeneratorGUI as RefactoredGUI
        
        root = ctk.CTk()
        root.withdraw()  # 隐藏窗口，只测试初始化
        
        app = RefactoredGUI(root)
        
        # 测试基本属性（向后兼容性）
        assert hasattr(app, 'master'), "缺少master属性"
        assert hasattr(app, 'tabview'), "缺少tabview属性"
        assert hasattr(app, 'api_key_var'), "缺少api_key_var属性"
        assert hasattr(app, 'config_file'), "缺少config_file属性"
        
        # 测试基本方法（向后兼容性）
        assert hasattr(app, 'show_tooltip'), "缺少show_tooltip方法"
        assert hasattr(app, 'safe_get_int'), "缺少safe_get_int方法"
        assert hasattr(app, 'test_llm_config'), "缺少test_llm_config方法"
        
        # 测试MVP架构组件
        assert hasattr(app, 'config_manager'), "缺少config_manager属性"
        assert hasattr(app, 'view'), "缺少view属性"
        assert hasattr(app, 'presenter'), "缺少presenter属性"
        
        # 测试配置管理器
        assert hasattr(app.config_manager, 'current_llm_config'), "配置管理器缺少current_llm_config"
        assert hasattr(app.config_manager, 'novel_params'), "配置管理器缺少novel_params"
        
        # 测试View组件
        assert hasattr(app.view, 'update_view'), "View缺少update_view方法"
        assert hasattr(app.view, 'show_error'), "View缺少show_error方法"
        
        # 测试Presenter组件
        assert hasattr(app.presenter, 'handle_model_change'), "Presenter缺少handle_model_change方法"
        
        # 安全销毁窗口
        try:
            root.quit()
            root.update()
        except:
            pass
        finally:
            try:
                root.destroy()
            except:
                pass
        return True, "重构UI测试通过"
        
    except Exception as e:
        try:
            if 'root' in locals():
                root.quit()
                root.destroy()
        except:
            pass
        return False, f"重构UI测试失败: {str(e)}"

def test_compatibility():
    """测试向后兼容性"""
    try:
        from ui.main_window import NovelGeneratorGUI as OriginalGUI
        from ui.main_window_refactored import NovelGeneratorGUI as RefactoredGUI
        
        # 创建两个实例进行对比
        root1 = ctk.CTk()
        root1.withdraw()
        original_app = OriginalGUI(root1)
        
        root2 = ctk.CTk()
        root2.withdraw()
        refactored_app = RefactoredGUI(root2)
        
        # 比较关键属性
        original_attrs = [attr for attr in dir(original_app) if not attr.startswith('_')]
        refactored_attrs = [attr for attr in dir(refactored_app) if not attr.startswith('_')]
        
        missing_attrs = set(original_attrs) - set(refactored_attrs)
        if missing_attrs:
            # 安全销毁窗口
            try:
                root1.quit()
                root1.destroy()
                root2.quit()
                root2.destroy()
            except:
                pass
            return False, f"重构后缺少属性: {missing_attrs}"
        
        # 测试关键方法的存在性
        key_methods = [
            'show_tooltip', 'safe_get_int', 'log', 'safe_log',
            'disable_button_safe', 'enable_button_safe', 'handle_exception',
            'test_llm_config', 'test_embedding_config', 'browse_folder',
            'generate_novel_architecture_ui', 'generate_chapter_blueprint_ui'
        ]
        
        for method in key_methods:
            if not hasattr(refactored_app, method):
                # 安全销毁窗口
                try:
                    root1.quit()
                    root1.destroy()
                    root2.quit()
                    root2.destroy()
                except:
                    pass
                return False, f"重构后缺少方法: {method}"
            # 同时检查View对象是否也有这些方法（如果是生成相关方法）
            if method.endswith('_ui') or method.startswith('generate_'):
                if not hasattr(refactored_app.view, method):
                    # 安全销毁窗口
                    try:
                        root1.quit()
                        root1.destroy()
                        root2.quit()
                        root2.destroy()
                    except:
                        pass
                    return False, f"重构后View缺少方法: {method}"
        
        # 安全销毁窗口
        try:
            root1.quit()
            root1.destroy()
            root2.quit()
            root2.destroy()
        except:
            pass
        return True, "向后兼容性测试通过"
        
    except Exception as e:
        try:
            if 'root1' in locals():
                root1.quit()
                root1.destroy()
            if 'root2' in locals():
                root2.quit()
                root2.destroy()
        except:
            pass
        return False, f"向后兼容性测试失败: {str(e)}"

def test_config_management():
    """测试配置管理功能"""
    try:
        from ui.config_models import ConfigurationManager, LLMConfig, EmbeddingConfig, NovelParams
        
        # 测试配置管理器初始化
        config_manager = ConfigurationManager()
        
        # 测试基本属性
        assert hasattr(config_manager, 'current_llm_config'), "缺少current_llm_config属性"
        assert hasattr(config_manager, 'current_embedding_config'), "缺少current_embedding_config属性"
        assert hasattr(config_manager, 'novel_params'), "缺少novel_params属性"
        
        # 测试数据类
        llm_config = LLMConfig()
        assert llm_config.model_name == "gpt-4o-mini", "LLMConfig默认值错误"
        
        emb_config = EmbeddingConfig()
        assert emb_config.model_name == "text-embedding-ada-002", "EmbeddingConfig默认值错误"
        
        novel_params = NovelParams()
        assert novel_params.genre == "玄幻", "NovelParams默认值错误"
        
        return True, "配置管理测试通过"
        
    except Exception as e:
        return False, f"配置管理测试失败: {str(e)}"

def run_all_tests():
    """运行所有测试"""
    tests = [
        ("原始UI测试", test_original_ui),
        ("重构UI测试", test_refactored_ui),
        ("向后兼容性测试", test_compatibility),
        ("配置管理测试", test_config_management)
    ]
    
    results = []
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            results.append(f"✓ {test_name}: {message}" if success else f"✗ {test_name}: {message}")
            if not success:
                all_passed = False
        except Exception as e:
            results.append(f"✗ {test_name}: 测试执行异常 - {str(e)}")
            all_passed = False
    
    return all_passed, results

if __name__ == "__main__":
    print("开始UI重构功能完整性测试...")
    print("=" * 50)
    
    try:
        all_passed, results = run_all_tests()
        
        for result in results:
            print(result)
        
        print("=" * 50)
        if all_passed:
            print("🎉 所有测试通过！重构成功，功能完整性得到保证。")
        else:
            print("❌ 部分测试失败，需要修复问题。")
        
    except Exception as e:
        print(f"测试执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("按回车键退出...")