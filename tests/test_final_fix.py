#!/usr/bin/env python3
"""
测试打包后应用程序的导入修复效果
"""

import sys
import os

def test_imports():
    """测试所有关键模块的导入"""
    print("=== 测试打包后应用程序的导入修复效果 ===\n")
    
    # 测试基础库
    print("1. 测试基础库导入...")
    try:
        import tkinter as tk
        import PIL
        import numpy as np
        print("✅ 基础库导入成功")
    except Exception as e:
        print(f"❌ 基础库导入失败: {e}")
        return False
    
    # 测试OpenCV
    print("\n2. 测试OpenCV导入...")
    try:
        import cv2
        print(f"✅ OpenCV导入成功，版本: {cv2.__version__}")
    except Exception as e:
        print(f"❌ OpenCV导入失败: {e}")
        return False
    
    # 测试主窗口模块
    print("\n3. 测试主窗口模块导入...")
    try:
        from src.main_window import ImageViewer
        print("✅ 主窗口模块导入成功")
    except Exception as e:
        print(f"❌ 主窗口模块导入失败: {e}")
        return False
    
    # 测试星空堆叠模块 - 使用绝对导入
    print("\n4. 测试星空堆叠模块导入（绝对导入）...")
    try:
        from src.modules.stacking import StackingWindow
        print("✅ 星空堆叠模块（绝对导入）导入成功")
    except Exception as e:
        print(f"❌ 星空堆叠模块（绝对导入）导入失败: {e}")
    
    # 测试星空堆叠模块 - 直接导入
    print("\n5. 测试星空堆叠模块导入（直接导入）...")
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✅ 星空堆叠模块（直接导入）导入成功")
    except Exception as e:
        print(f"❌ 星空堆叠模块（直接导入）导入失败: {e}")
    
    # 测试Camera Raw模块 - 使用绝对导入
    print("\n6. 测试Camera Raw模块导入（绝对导入）...")
    try:
        from src.modules.camera_raw import CameraRawWindow
        print("✅ Camera Raw模块（绝对导入）导入成功")
    except Exception as e:
        print(f"❌ Camera Raw模块（绝对导入）导入失败: {e}")
    
    # 测试Camera Raw模块 - 直接导入
    print("\n7. 测试Camera Raw模块导入（直接导入）...")
    try:
        from src.modules.camera_raw.ui import CameraRawWindow
        print("✅ Camera Raw模块（直接导入）导入成功")
    except Exception as e:
        print(f"❌ Camera Raw模块（直接导入）导入失败: {e}")
    
    # 测试主程序启动逻辑
    print("\n8. 测试主程序启动逻辑...")
    try:
        # 模拟主程序的导入逻辑
        import tkinter as tk
        from src.main_window import ImageViewer
        
        # 创建一个测试窗口（不显示）
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 尝试创建ImageViewer实例
        app = ImageViewer(root)
        print("✅ 主程序启动逻辑测试成功")
        
        # 清理
        root.destroy()
        
    except Exception as e:
        print(f"❌ 主程序启动逻辑测试失败: {e}")
        return False
    
    print("\n=== 所有测试完成 ===")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 所有关键模块导入测试通过！应用程序应该可以正常运行。")
    else:
        print("\n⚠️  部分模块导入测试失败，可能需要进一步调试。")
    
    sys.exit(0 if success else 1)