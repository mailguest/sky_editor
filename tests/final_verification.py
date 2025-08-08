#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 确认延迟导入问题已解决
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def final_verification():
    """最终验证延迟导入功能"""
    print("=== Sky Editor 最终功能验证 ===")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 创建隐藏的根窗口
    root = tk.Tk()
    root.withdraw()
    
    try:
        # 导入并创建ImageViewer
        print("\n1. 导入main_window模块...")
        import src.main_window as main_window
        print("✅ 模块导入成功")
        
        print("\n2. 创建ImageViewer实例...")
        viewer = main_window.ImageViewer(root)
        print("✅ ImageViewer创建成功")
        
        # 检查延迟导入状态
        print(f"\n3. 检查功能模块状态:")
        print(f"   星空堆叠支持: {main_window.STACKING_SUPPORT}")
        print(f"   Camera Raw支持: {main_window.CAMERA_RAW_SUPPORT}")
        print(f"   StackingWindow类: {main_window.StackingWindow}")
        print(f"   CameraRawWindow类: {main_window.CameraRawWindow}")
        
        # 模拟菜单功能调用
        print(f"\n4. 测试菜单功能:")
        
        # 模拟错误消息收集
        error_messages = []
        original_showerror = messagebox.showerror
        
        def mock_showerror(title, message):
            error_messages.append((title, message))
            print(f"   错误对话框: {title} - {message}")
        
        messagebox.showerror = mock_showerror
        
        # 测试Camera Raw功能
        print("   测试Camera Raw功能...")
        try:
            viewer.open_camera_raw()
            if error_messages:
                print(f"   ❌ Camera Raw功能报错: {error_messages[-1][1]}")
            else:
                print("   ✅ Camera Raw功能正常")
        except Exception as e:
            print(f"   ❌ Camera Raw功能异常: {e}")
        
        # 清空错误消息
        error_messages.clear()
        
        # 测试星空堆叠功能
        print("   测试星空堆叠功能...")
        try:
            viewer.open_stacking_tool()
            if error_messages:
                print(f"   ❌ 星空堆叠功能报错: {error_messages[-1][1]}")
            else:
                print("   ✅ 星空堆叠功能正常")
        except Exception as e:
            print(f"   ❌ 星空堆叠功能异常: {e}")
        
        # 恢复原始函数
        messagebox.showerror = original_showerror
        
        # 测试依赖库
        print(f"\n5. 测试关键依赖库:")
        
        dependencies = [
            ('numpy', 'import numpy'),
            ('rawpy', 'import rawpy'),
            ('cv2', 'import cv2'),
            ('matplotlib', 'import matplotlib'),
            ('skimage', 'import skimage'),
            ('scipy', 'import scipy')
        ]
        
        for name, import_cmd in dependencies:
            try:
                exec(import_cmd)
                print(f"   ✅ {name}: 可用")
            except ImportError as e:
                print(f"   ❌ {name}: 不可用 - {e}")
        
        print(f"\n=== 验证完成 ===")
        
        # 检查是否所有功能都正常
        if (main_window.STACKING_SUPPORT and 
            main_window.CAMERA_RAW_SUPPORT and 
            len(error_messages) == 0):
            print("🎉 所有功能验证通过！Sky Editor已准备就绪。")
            return True
        else:
            print("⚠️  部分功能可能存在问题，请检查上述输出。")
            return False
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        root.destroy()

if __name__ == "__main__":
    success = final_verification()
    sys.exit(0 if success else 1)