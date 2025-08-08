#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sky Editor 测试启动脚本 - 用于调试打包后的导入问题
"""

import sys
import os

# 强制输出到文件
debug_log = open('/tmp/sky_editor_debug.log', 'w')
sys.stdout = debug_log
sys.stderr = debug_log

print("=== Sky Editor 测试启动 ===")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"当前脚本目录: {current_dir}")

# 检查是否在打包环境中运行
if getattr(sys, 'frozen', False):
    print("检测到打包环境")
    # 在打包环境中，确保_internal目录在路径中
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        bundle_dir = sys._MEIPASS
        print(f"PyInstaller环境，_MEIPASS: {bundle_dir}")
    else:
        # 其他打包环境
        bundle_dir = os.path.dirname(sys.executable)
        print(f"其他打包环境，bundle目录: {bundle_dir}")
    
    # 确保bundle_dir在Python路径的最前面
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
        print(f"已添加bundle目录到Python路径")
    
    print(f"Python路径前5个: {sys.path[:5]}")

def main():
    """启动Sky Editor主程序"""
    print("\n=== 开始导入模块 ===")
    
    try:
        print("导入tkinter...")
        import tkinter as tk
        print("✅ tkinter导入成功")
        
        print("导入src.main_window...")
        from src.main_window import ImageViewer
        print("✅ src.main_window导入成功")
        
        print("创建主窗口...")
        # 创建主窗口
        root = tk.Tk()
        root.title("Sky Editor - 星空图像处理工具")
        root.geometry("1200x800")
        root.withdraw()  # 隐藏窗口，只测试导入
        
        print("创建ImageViewer实例...")
        # 创建应用程序
        app = ImageViewer(root)
        print("✅ ImageViewer创建成功")
        
        print("Sky Editor 测试启动成功")
        print("功能包括：")
        print("- 图像浏览和预览")
        print("- Camera Raw 图像处理")
        print("- 星空图像堆叠")
        print("- 多种图像格式支持")
        
        # 测试模块功能
        print("\n=== 测试模块功能 ===")
        
        # 测试星空堆叠模块
        try:
            from src.modules.stacking import StackingWindow
            print("✅ 星空堆叠模块导入成功")
        except Exception as e:
            print(f"❌ 星空堆叠模块导入失败: {e}")
        
        # 测试Camera Raw模块
        try:
            from src.modules.camera_raw import CameraRawWindow
            print("✅ Camera Raw模块导入成功")
        except Exception as e:
            print(f"❌ Camera Raw模块导入失败: {e}")
        
        # 清理
        root.destroy()
        print("\n=== 测试完成 ===")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所需的依赖库：")
        print("pip install pillow opencv-python numpy rawpy matplotlib")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    debug_log.close()
    
    # 将调试信息复制到标准输出
    with open('/tmp/sky_editor_debug.log', 'r') as f:
        content = f.read()
        print(content)
    
    sys.exit(0 if success else 1)