#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试菜单函数的直接调用
"""

import sys
import os
import tkinter as tk
from unittest.mock import patch

def test_menu_functions():
    """测试菜单函数"""
    print("=== 菜单函数测试 ===")
    print(f"Python路径: {sys.path[:3]}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 创建一个虚拟的tkinter根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    try:
        # 导入ImageViewer类
        print("导入ImageViewer类...")
        from src.main_window import ImageViewer
        print("✅ ImageViewer类导入成功")
        
        # 创建ImageViewer实例
        print("创建ImageViewer实例...")
        app = ImageViewer(root)
        print("✅ ImageViewer实例创建成功")
        
        # 测试Camera Raw功能
        print("\n=== 测试Camera Raw功能 ===")
        try:
            # 使用patch来模拟messagebox，避免实际弹出对话框
            with patch('tkinter.messagebox.showerror') as mock_error:
                app.open_camera_raw()
                if mock_error.called:
                    # 如果调用了错误对话框，打印错误信息
                    args, kwargs = mock_error.call_args
                    print(f"❌ Camera Raw功能调用失败: {args[1]}")
                else:
                    print("✅ Camera Raw功能调用成功")
        except Exception as e:
            print(f"❌ Camera Raw功能调用异常: {e}")
        
        # 测试星空堆叠功能
        print("\n=== 测试星空堆叠功能 ===")
        try:
            # 使用patch来模拟messagebox，避免实际弹出对话框
            with patch('tkinter.messagebox.showerror') as mock_error:
                app.open_stacking_tool()
                if mock_error.called:
                    # 如果调用了错误对话框，打印错误信息
                    args, kwargs = mock_error.call_args
                    print(f"❌ 星空堆叠功能调用失败: {args[1]}")
                else:
                    print("✅ 星空堆叠功能调用成功")
        except Exception as e:
            print(f"❌ 星空堆叠功能调用异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_menu_functions()