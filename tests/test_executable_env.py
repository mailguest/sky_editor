#!/usr/bin/env python3
"""
通过可执行文件测试打包环境
"""

import sys
import os

def main():
    print("=== Sky Editor 可执行文件环境测试 ===")
    
    # 检查是否在打包环境中
    if getattr(sys, 'frozen', False):
        print("✅ 检测到打包环境 (PyInstaller)")
        bundle_dir = sys._MEIPASS
        print(f"Bundle目录: {bundle_dir}")
    else:
        print("❌ 当前不在打包环境中")
        return
    
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"可执行文件: {sys.executable}")
    
    # 测试关键依赖
    dependencies = ['numpy', 'rawpy', 'matplotlib', 'cv2', 'scipy']
    print("\n=== 测试关键依赖 ===")
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: 可用")
        except ImportError as e:
            print(f"❌ {dep}: 不可用 - {e}")
    
    # 测试主模块
    print("\n=== 测试主模块 ===")
    try:
        import src.main_window as main_window
        print("✅ src.main_window: 导入成功")
        
        # 检查延迟导入状态
        print(f"STACKING_SUPPORT: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        print(f"CAMERA_RAW_SUPPORT: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        
        # 测试延迟导入函数
        try:
            main_window._import_camera_raw_module()
            print(f"Camera Raw导入后: {getattr(main_window, 'CAMERA_RAW_SUPPORT', 'undefined')}")
        except Exception as e:
            print(f"❌ Camera Raw导入失败: {e}")
        
        try:
            main_window._import_stacking_module()
            print(f"星空堆叠导入后: {getattr(main_window, 'STACKING_SUPPORT', 'undefined')}")
        except Exception as e:
            print(f"❌ 星空堆叠导入失败: {e}")
            
    except Exception as e:
        print(f"❌ 主模块导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()