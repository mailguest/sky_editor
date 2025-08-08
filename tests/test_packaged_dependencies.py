#!/usr/bin/env python3
"""
测试打包环境中的依赖和模块导入问题
"""

import sys
import os
import traceback

def test_basic_imports():
    """测试基础依赖导入"""
    print("=== 测试基础依赖导入 ===")
    
    dependencies = [
        'numpy',
        'rawpy', 
        'matplotlib',
        'cv2',
        'scipy',
        'skimage'
    ]
    
    results = {}
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: 导入成功")
            results[dep] = True
        except ImportError as e:
            print(f"❌ {dep}: 导入失败 - {e}")
            results[dep] = False
        except Exception as e:
            print(f"⚠️ {dep}: 导入异常 - {e}")
            results[dep] = False
    
    return results

def test_module_paths():
    """测试模块路径"""
    print("\n=== 测试模块路径 ===")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

def test_src_module_import():
    """测试src模块导入"""
    print("\n=== 测试src模块导入 ===")
    
    try:
        # 测试主模块导入
        import src.main_window as main_window
        print("✅ src.main_window: 导入成功")
        
        # 检查延迟导入状态
        print(f"STACKING_SUPPORT: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        print(f"CAMERA_RAW_SUPPORT: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        
        # 测试创建ImageViewer
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        viewer = main_window.ImageViewer(root)
        print("✅ ImageViewer: 创建成功")
        
        # 再次检查延迟导入状态
        print(f"初始化后 STACKING_SUPPORT: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        print(f"初始化后 CAMERA_RAW_SUPPORT: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        
        # 测试延迟导入函数
        try:
            main_window._import_camera_raw_module()
            print("✅ _import_camera_raw_module: 执行成功")
            print(f"执行后 CAMERA_RAW_SUPPORT: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        except Exception as e:
            print(f"❌ _import_camera_raw_module: 执行失败 - {e}")
            traceback.print_exc()
        
        try:
            main_window._import_stacking_module()
            print("✅ _import_stacking_module: 执行成功")
            print(f"执行后 STACKING_SUPPORT: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        except Exception as e:
            print(f"❌ _import_stacking_module: 执行失败 - {e}")
            traceback.print_exc()
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ src模块导入失败: {e}")
        traceback.print_exc()

def test_direct_module_import():
    """直接测试功能模块导入"""
    print("\n=== 直接测试功能模块导入 ===")
    
    try:
        from src.modules.camera_raw.ui import CameraRawWindow
        print("✅ CameraRawWindow: 导入成功")
    except Exception as e:
        print(f"❌ CameraRawWindow: 导入失败 - {e}")
        traceback.print_exc()
    
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✅ StackingWindow: 导入成功")
    except Exception as e:
        print(f"❌ StackingWindow: 导入失败 - {e}")
        traceback.print_exc()

def test_camera_raw_processor():
    """测试Camera Raw处理器"""
    print("\n=== 测试Camera Raw处理器 ===")
    
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        processor = CameraRawProcessor()
        print("✅ CameraRawProcessor: 创建成功")
        
        # 测试rawpy导入
        import rawpy
        print("✅ rawpy: 在processor中可用")
        
    except Exception as e:
        print(f"❌ CameraRawProcessor: 创建失败 - {e}")
        traceback.print_exc()

def main():
    print("Sky Editor 打包环境依赖测试")
    print("=" * 50)
    
    # 检查是否在打包环境中
    if getattr(sys, 'frozen', False):
        print("✅ 检测到打包环境 (PyInstaller)")
        bundle_dir = sys._MEIPASS
        print(f"Bundle目录: {bundle_dir}")
    else:
        print("⚠️ 当前不在打包环境中")
    
    test_module_paths()
    deps = test_basic_imports()
    test_src_module_import()
    test_direct_module_import()
    test_camera_raw_processor()
    
    print("\n=== 测试总结 ===")
    failed_deps = [dep for dep, success in deps.items() if not success]
    if failed_deps:
        print(f"❌ 失败的依赖: {', '.join(failed_deps)}")
    else:
        print("✅ 所有基础依赖导入成功")

if __name__ == "__main__":
    main()