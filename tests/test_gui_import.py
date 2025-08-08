#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GUI环境中的延迟导入
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def test_gui_import():
    """在GUI环境中测试延迟导入"""
    print("=== GUI环境延迟导入测试 ===")
    
    # 创建一个隐藏的根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        # 导入main_window模块
        import src.main_window as main_window
        print("✅ main_window模块导入成功")
        
        # 创建ImageViewer实例（这会触发延迟导入）
        print("创建ImageViewer实例...")
        viewer = main_window.ImageViewer(root)
        print("✅ ImageViewer创建成功")
        
        # 检查延迟导入状态
        print(f"STACKING_SUPPORT: {main_window.STACKING_SUPPORT}")
        print(f"CAMERA_RAW_SUPPORT: {main_window.CAMERA_RAW_SUPPORT}")
        
        # 模拟点击菜单
        print("\n=== 模拟菜单点击 ===")
        
        # 测试Camera Raw菜单
        print("测试Camera Raw菜单...")
        try:
            # 使用mock来避免实际弹出对话框
            original_showerror = messagebox.showerror
            error_messages = []
            
            def mock_showerror(title, message):
                error_messages.append((title, message))
                print(f"错误对话框: {title} - {message}")
            
            messagebox.showerror = mock_showerror
            
            # 调用open_camera_raw函数
            viewer.open_camera_raw()
            
            if error_messages:
                print(f"❌ Camera Raw功能报错: {error_messages[-1]}")
            else:
                print("✅ Camera Raw功能正常")
            
            # 测试星空堆叠菜单
            print("测试星空堆叠菜单...")
            error_messages.clear()
            
            viewer.open_stacking_tool()
            
            if error_messages:
                print(f"❌ 星空堆叠功能报错: {error_messages[-1]}")
            else:
                print("✅ 星空堆叠功能正常")
            
            # 恢复原始函数
            messagebox.showerror = original_showerror
            
        except Exception as e:
            print(f"❌ 菜单测试异常: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()

if __name__ == "__main__":
    test_gui_import()