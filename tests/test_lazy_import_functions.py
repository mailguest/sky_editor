#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试延迟导入函数的实际调用
"""

import sys
import os

# 添加src目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_lazy_import_functions():
    """测试延迟导入函数"""
    print("=== 延迟导入函数测试 ===")
    print(f"Python路径: {sys.path[:3]}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 导入main_window模块
    try:
        print("导入main_window模块...")
        from src.main_window import _import_stacking_module, _import_camera_raw_module
        print("✅ main_window模块导入成功")
    except ImportError as e:
        print(f"❌ main_window模块导入失败: {e}")
        return
    
    # 测试星空堆叠模块延迟导入
    print("\n=== 测试星空堆叠模块延迟导入 ===")
    try:
        result = _import_stacking_module()
        print(f"星空堆叠模块导入结果: {'✅ 成功' if result else '❌ 失败'}")
        
        if result:
            # 测试模块是否真的可用
            from src.main_window import StackingWindow, STACKING_SUPPORT
            print(f"STACKING_SUPPORT: {STACKING_SUPPORT}")
            print(f"StackingWindow: {StackingWindow}")
        
    except Exception as e:
        print(f"❌ 星空堆叠模块延迟导入异常: {e}")
    
    # 测试Camera Raw模块延迟导入
    print("\n=== 测试Camera Raw模块延迟导入 ===")
    try:
        result = _import_camera_raw_module()
        print(f"Camera Raw模块导入结果: {'✅ 成功' if result else '❌ 失败'}")
        
        if result:
            # 测试模块是否真的可用
            from src.main_window import CameraRawWindow, CAMERA_RAW_SUPPORT
            print(f"CAMERA_RAW_SUPPORT: {CAMERA_RAW_SUPPORT}")
            print(f"CameraRawWindow: {CameraRawWindow}")
        
    except Exception as e:
        print(f"❌ Camera Raw模块延迟导入异常: {e}")

if __name__ == "__main__":
    test_lazy_import_functions()