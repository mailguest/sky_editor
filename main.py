#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sky Editor 启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 检查是否在打包环境中运行
if getattr(sys, 'frozen', False):
    # 在打包环境中，确保_internal目录在路径中
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        bundle_dir = sys._MEIPASS
    else:
        # 其他打包环境
        bundle_dir = os.path.dirname(sys.executable)
    
    # 确保bundle_dir在Python路径的最前面
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    
    print(f"检测到打包环境，bundle目录: {bundle_dir}")
    print(f"Python路径: {sys.path[:3]}...")  # 只显示前3个路径

def test_mode():
    """测试模式 - 检查打包环境中的依赖和模块"""
    print("=== Sky Editor 测试模式 ===")
    
    # 检查是否在打包环境中
    if getattr(sys, 'frozen', False):
        print("✅ 检测到打包环境 (PyInstaller)")
        bundle_dir = sys._MEIPASS
        print(f"Bundle目录: {bundle_dir}")
    else:
        print("❌ 当前不在打包环境中")
    
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"可执行文件: {sys.executable}")
    
    # 测试关键依赖
    dependencies = ['numpy', 'rawpy', 'matplotlib', 'cv2', 'scipy']
    print("\n=== 测试关键依赖 ===")
    
    failed_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: 可用")
        except ImportError as e:
            print(f"❌ {dep}: 不可用 - {e}")
            failed_deps.append(dep)
    
    # 测试主模块
    print("\n=== 测试主模块 ===")
    try:
        import src.main_window as main_window
        print("✅ src.main_window: 导入成功")
        
        # 检查延迟导入状态
        print(f"初始 STACKING_SUPPORT: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        print(f"初始 CAMERA_RAW_SUPPORT: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        
        # 测试延迟导入函数
        try:
            main_window._import_camera_raw_module()
            camera_raw_support = getattr(main_window, 'CAMERA_RAW_SUPPORT', False)
            print(f"✅ Camera Raw导入: {camera_raw_support}")
        except Exception as e:
            print(f"❌ Camera Raw导入失败: {e}")
            import traceback
            traceback.print_exc()
        
        try:
            main_window._import_stacking_module()
            stacking_support = getattr(main_window, 'STACKING_SUPPORT', False)
            print(f"✅ 星空堆叠导入: {stacking_support}")
        except Exception as e:
            print(f"❌ 星空堆叠导入失败: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 主模块导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试总结 ===")
    if failed_deps:
        print(f"❌ 失败的依赖: {', '.join(failed_deps)}")
    else:
        print("✅ 所有依赖测试通过")

def main():
    """启动Sky Editor主程序"""
    # 检查是否是测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mode()
        return
    
    try:
        import tkinter as tk
        from src.main_window import ImageViewer
        
        # 创建主窗口
        root = tk.Tk()
        root.title("Sky Editor - 星空图像处理工具")
        root.geometry("1200x800")
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用程序图标
            pass
        except:
            pass
        
        # 创建应用程序
        app = ImageViewer(root)
        
        print("Sky Editor 已启动")
        print("功能包括：")
        print("- 图像浏览和预览")
        print("- Camera Raw 图像处理")
        print("- 星空图像堆叠")
        print("- 多种图像格式支持")
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所需的依赖库：")
        print("pip install pillow opencv-python numpy rawpy matplotlib")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()