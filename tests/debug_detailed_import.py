#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试延迟导入的具体行为
"""

import sys
import os
import traceback

def debug_detailed_import():
    """详细调试延迟导入"""
    print("=== 详细延迟导入调试 ===")
    print(f"Python路径: {sys.path[:3]}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 测试每一步的导入过程
    print("\n=== 步骤1: 导入main_window模块 ===")
    try:
        import src.main_window as main_window
        print("✅ main_window模块导入成功")
        
        # 检查初始状态
        print(f"初始STACKING_SUPPORT: {main_window.STACKING_SUPPORT}")
        print(f"初始CAMERA_RAW_SUPPORT: {main_window.CAMERA_RAW_SUPPORT}")
        print(f"初始StackingWindow: {main_window.StackingWindow}")
        print(f"初始CameraRawWindow: {main_window.CameraRawWindow}")
        
    except Exception as e:
        print(f"❌ main_window模块导入失败: {e}")
        traceback.print_exc()
        return
    
    # 测试星空堆叠模块延迟导入的详细过程
    print("\n=== 步骤2: 详细测试星空堆叠模块延迟导入 ===")
    try:
        print("调用_import_stacking_module()...")
        result = main_window._import_stacking_module()
        print(f"返回结果: {result}")
        
        if result:
            print(f"导入后STACKING_SUPPORT: {main_window.STACKING_SUPPORT}")
            print(f"导入后StackingWindow: {main_window.StackingWindow}")
        else:
            print("❌ 延迟导入返回False")
            
            # 手动测试导入
            print("手动测试绝对导入...")
            try:
                from src.modules.stacking import StackingWindow
                print("✅ 手动绝对导入成功")
            except ImportError as e:
                print(f"❌ 手动绝对导入失败: {e}")
                
                print("手动测试相对导入...")
                try:
                    # 这在脚本中不会工作，但我们可以尝试
                    exec("from .modules.stacking import StackingWindow")
                    print("✅ 手动相对导入成功")
                except Exception as e:
                    print(f"❌ 手动相对导入失败: {e}")
        
    except Exception as e:
        print(f"❌ 星空堆叠模块延迟导入异常: {e}")
        traceback.print_exc()
    
    # 测试Camera Raw模块延迟导入的详细过程
    print("\n=== 步骤3: 详细测试Camera Raw模块延迟导入 ===")
    try:
        print("调用_import_camera_raw_module()...")
        result = main_window._import_camera_raw_module()
        print(f"返回结果: {result}")
        
        if result:
            print(f"导入后CAMERA_RAW_SUPPORT: {main_window.CAMERA_RAW_SUPPORT}")
            print(f"导入后CameraRawWindow: {main_window.CameraRawWindow}")
        else:
            print("❌ 延迟导入返回False")
            
            # 手动测试导入
            print("手动测试绝对导入...")
            try:
                from src.modules.camera_raw import CameraRawWindow
                print("✅ 手动绝对导入成功")
            except ImportError as e:
                print(f"❌ 手动绝对导入失败: {e}")
                
                print("手动测试相对导入...")
                try:
                    # 这在脚本中不会工作，但我们可以尝试
                    exec("from .modules.camera_raw import CameraRawWindow")
                    print("✅ 手动相对导入成功")
                except Exception as e:
                    print(f"❌ 手动相对导入失败: {e}")
        
    except Exception as e:
        print(f"❌ Camera Raw模块延迟导入异常: {e}")
        traceback.print_exc()
    
    # 测试模块内部的依赖
    print("\n=== 步骤4: 测试模块内部依赖 ===")
    
    print("测试Camera Raw处理器的rawpy依赖...")
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        processor = CameraRawProcessor()
        print("✅ CameraRawProcessor创建成功")
        
        # 检查rawpy支持
        import src.modules.camera_raw.processor as crp
        print(f"RAW_SUPPORT: {crp.RAW_SUPPORT}")
        
    except Exception as e:
        print(f"❌ CameraRawProcessor测试失败: {e}")
        traceback.print_exc()
    
    print("测试星空堆叠处理器的依赖...")
    try:
        from src.modules.stacking.processor import AstroStacker
        stacker = AstroStacker()
        print("✅ AstroStacker创建成功")
        
    except Exception as e:
        print(f"❌ AstroStacker测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_detailed_import()