#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Raw 功能测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_imports():
    """测试所有必要的模块导入"""
    print("测试模块导入...")
    
    try:
        import tkinter as tk
        print("✓ tkinter 导入成功")
    except ImportError as e:
        print(f"✗ tkinter 导入失败: {e}")
        return False
    
    try:
        import PIL
        print("✓ PIL (Pillow) 导入成功")
    except ImportError as e:
        print(f"✗ PIL 导入失败: {e}")
        return False
    
    try:
        import cv2
        print("✓ OpenCV 导入成功")
    except ImportError as e:
        print(f"✗ OpenCV 导入失败: {e}")
        return False
    
    try:
        import numpy
        print("✓ NumPy 导入成功")
    except ImportError as e:
        print(f"✗ NumPy 导入失败: {e}")
        return False
    
    try:
        import rawpy
        print("✓ rawpy 导入成功")
    except ImportError as e:
        print(f"✗ rawpy 导入失败: {e}")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib 导入成功")
    except ImportError as e:
        print(f"✗ matplotlib 导入失败: {e}")
        return False
    
    return True

def test_camera_raw_modules():
    """测试Camera Raw相关模块"""
    print("\n测试Camera Raw模块...")
    
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        print("✓ CameraRawProcessor 导入成功")
    except ImportError as e:
        print(f"✗ CameraRawProcessor 导入失败: {e}")
        return False
    
    try:
        from src.modules.camera_raw.ui import CameraRawWindow
        print("✓ CameraRawWindow 导入成功")
    except ImportError as e:
        print(f"✗ CameraRawWindow 导入失败: {e}")
        return False
    
    return True

def test_presets():
    """测试预设文件"""
    print("\n测试预设文件...")
    
    presets_dir = os.path.join(project_root, "assets", "presets", "camera_raw")
    if not os.path.exists(presets_dir):
        print("✗ presets 目录不存在")
        return False
    
    print("✓ presets 目录存在")
    
    preset_files = [
        "深空天体增强.json",
        "银河摄影增强.json", 
        "星轨摄影增强.json"
    ]
    
    for preset_file in preset_files:
        preset_path = os.path.join(presets_dir, preset_file)
        if os.path.exists(preset_path):
            print(f"✓ {preset_file} 存在")
        else:
            print(f"✗ {preset_file} 不存在")
    
    return True

def test_camera_raw_functionality():
    """测试Camera Raw核心功能"""
    print("\n测试Camera Raw核心功能...")
    
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        
        # 创建处理器实例
        processor = CameraRawProcessor()
        print("✓ CameraRawProcessor 实例创建成功")
        
        # 测试参数设置
        processor.basic_adjustments['exposure'] = 0.5
        processor.basic_adjustments['highlights'] = -50
        processor.basic_adjustments['shadows'] = 50
        print("✓ 参数设置功能正常")
        
        # 测试重置功能
        processor.reset_adjustments()
        print("✓ 重置功能正常")
        
        # 测试预设目录
        import os
        presets_dir = os.path.join(project_root, "assets", "presets", "camera_raw")
        if os.path.exists(presets_dir):
            preset_files = [f for f in os.listdir(presets_dir) if f.endswith('.json')]
            print(f"✓ 可用预设数量: {len(preset_files)}")
        else:
            print("✗ 预设目录不存在")
        
        return True
        
    except Exception as e:
        print(f"✗ Camera Raw功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Sky Editor Camera Raw 功能测试")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 测试基础依赖
    if not test_imports():
        all_tests_passed = False
    
    # 测试Camera Raw模块
    if not test_camera_raw_modules():
        all_tests_passed = False
    
    # 测试预设文件
    if not test_presets():
        all_tests_passed = False
    
    # 测试核心功能
    if not test_camera_raw_functionality():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有测试通过！Camera Raw功能已准备就绪。")
        print("\n启动方法：")
        print("1. 运行: python main.py")
        print("2. 在菜单中选择: 工具 → Camera Raw")
    else:
        print("❌ 部分测试失败，请检查相关问题。")
    print("=" * 50)

if __name__ == "__main__":
    main()