#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试延迟导入 - 在打包环境中测试
"""

import sys
import os

def debug_lazy_import():
    """调试延迟导入功能"""
    print("=== 延迟导入调试 ===")
    print(f"Python路径: {sys.path[:5]}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 测试星空堆叠模块延迟导入
    print("\n=== 测试星空堆叠模块延迟导入 ===")
    global STACKING_SUPPORT, StackingWindow
    STACKING_SUPPORT = False
    StackingWindow = None

    def _import_stacking_module():
        """延迟导入星空堆叠模块"""
        global STACKING_SUPPORT, StackingWindow
        if STACKING_SUPPORT:
            return True
        
        print("尝试绝对导入: from src.modules.stacking import StackingWindow")
        try:
            from src.modules.stacking import StackingWindow as SW
            StackingWindow = SW
            STACKING_SUPPORT = True
            print("✅ 绝对导入成功")
            return True
        except ImportError as e:
            print(f"❌ 绝对导入失败: {e}")
            
            print("尝试相对导入: from .modules.stacking import StackingWindow")
            try:
                # 尝试相对导入作为备选
                from .modules.stacking import StackingWindow as SW
                StackingWindow = SW
                STACKING_SUPPORT = True
                print("✅ 相对导入成功")
                return True
            except ImportError as e:
                print(f"❌ 相对导入失败: {e}")
                return False

    # 测试Camera Raw模块延迟导入
    print("\n=== 测试Camera Raw模块延迟导入 ===")
    global CAMERA_RAW_SUPPORT, CameraRawWindow
    CAMERA_RAW_SUPPORT = False
    CameraRawWindow = None

    def _import_camera_raw_module():
        """延迟导入Camera Raw模块"""
        global CAMERA_RAW_SUPPORT, CameraRawWindow
        if CAMERA_RAW_SUPPORT:
            return True
        
        print("尝试绝对导入: from src.modules.camera_raw import CameraRawWindow")
        try:
            from src.modules.camera_raw import CameraRawWindow as CRW
            CameraRawWindow = CRW
            CAMERA_RAW_SUPPORT = True
            print("✅ 绝对导入成功")
            return True
        except ImportError as e:
            print(f"❌ 绝对导入失败: {e}")
            
            print("尝试相对导入: from .modules.camera_raw import CameraRawWindow")
            try:
                # 尝试相对导入作为备选
                from .modules.camera_raw import CameraRawWindow as CRW
                CameraRawWindow = CRW
                CAMERA_RAW_SUPPORT = True
                print("✅ 相对导入成功")
                return True
            except ImportError as e:
                print(f"❌ 相对导入失败: {e}")
                return False

    # 执行测试
    stacking_result = _import_stacking_module()
    camera_raw_result = _import_camera_raw_module()
    
    print(f"\n=== 测试结果 ===")
    print(f"星空堆叠模块导入: {'✅ 成功' if stacking_result else '❌ 失败'}")
    print(f"Camera Raw模块导入: {'✅ 成功' if camera_raw_result else '❌ 失败'}")
    
    # 如果导入失败，尝试其他导入方式
    if not stacking_result:
        print("\n=== 尝试其他导入方式 (星空堆叠) ===")
        try:
            print("尝试: import src.modules.stacking")
            import src.modules.stacking
            print("✅ 模块导入成功")
            
            print("尝试: from src.modules.stacking.ui import StackingWindow")
            from src.modules.stacking.ui import StackingWindow
            print("✅ StackingWindow导入成功")
        except ImportError as e:
            print(f"❌ 其他方式也失败: {e}")
    
    if not camera_raw_result:
        print("\n=== 尝试其他导入方式 (Camera Raw) ===")
        try:
            print("尝试: import src.modules.camera_raw")
            import src.modules.camera_raw
            print("✅ 模块导入成功")
            
            print("尝试: from src.modules.camera_raw.ui import CameraRawWindow")
            from src.modules.camera_raw.ui import CameraRawWindow
            print("✅ CameraRawWindow导入成功")
        except ImportError as e:
            print(f"❌ 其他方式也失败: {e}")

if __name__ == "__main__":
    debug_lazy_import()