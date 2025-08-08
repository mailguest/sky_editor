#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包后应用程序的导入问题
模拟打包后的环境
"""

import sys
import os

# 模拟打包后的Python路径
packaged_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app/Contents/Frameworks"
sys.path.insert(0, packaged_path)

def test_stacking_import():
    """测试星空堆叠模块导入"""
    print("测试星空堆叠模块导入...")
    
    # 测试1: 直接导入处理器
    try:
        from src.modules.stacking.processor import AstroStacker
        print("✅ 直接导入 AstroStacker 成功")
    except Exception as e:
        print(f"❌ 直接导入 AstroStacker 失败: {e}")
    
    # 测试2: 直接导入UI
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✅ 直接导入 StackingWindow 成功")
    except Exception as e:
        print(f"❌ 直接导入 StackingWindow 失败: {e}")
    
    # 测试3: 通过__init__.py导入
    try:
        from src.modules.stacking import StackingWindow
        print("✅ 通过 __init__.py 导入 StackingWindow 成功")
    except Exception as e:
        print(f"❌ 通过 __init__.py 导入 StackingWindow 失败: {e}")
    
    # 测试4: 模拟主窗口的导入方式
    try:
        from .modules.stacking import StackingWindow
        print("✅ 相对导入 StackingWindow 成功")
    except Exception as e:
        print(f"❌ 相对导入 StackingWindow 失败: {e}")

def test_camera_raw_import():
    """测试Camera Raw模块导入"""
    print("\n测试Camera Raw模块导入...")
    
    # 测试rawpy
    try:
        import rawpy
        print("✅ rawpy 导入成功")
    except Exception as e:
        print(f"❌ rawpy 导入失败: {e}")
    
    # 测试Camera Raw处理器
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        print("✅ CameraRawProcessor 导入成功")
    except Exception as e:
        print(f"❌ CameraRawProcessor 导入失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("打包后应用程序导入测试")
    print("=" * 50)
    print(f"Python 路径: {sys.path[:3]}...")
    
    test_camera_raw_import()
    test_stacking_import()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()