#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试打包后应用程序的依赖库导入问题
"""

import sys
import os

def test_import(module_name, description=""):
    """测试模块导入"""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - {description}")
        print(f"   错误: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - {description}")
        print(f"   其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Sky Editor 依赖库导入测试")
    print("=" * 60)
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.path}")
    print("=" * 60)
    
    # 基础库测试
    print("\n📦 基础库测试:")
    basic_libs = [
        ("tkinter", "GUI框架"),
        ("PIL", "图像处理库"),
        ("numpy", "数值计算库"),
        ("threading", "多线程支持"),
        ("pathlib", "路径处理"),
        ("json", "JSON处理"),
    ]
    
    basic_success = 0
    for lib, desc in basic_libs:
        if test_import(lib, desc):
            basic_success += 1
    
    # Camera Raw 相关库测试
    print("\n📷 Camera Raw 相关库测试:")
    camera_raw_libs = [
        ("rawpy", "RAW图像处理"),
        ("matplotlib", "图表绘制"),
        ("matplotlib.pyplot", "绘图接口"),
    ]
    
    camera_raw_success = 0
    for lib, desc in camera_raw_libs:
        if test_import(lib, desc):
            camera_raw_success += 1
    
    # 星空堆叠相关库测试
    print("\n🌟 星空堆叠相关库测试:")
    stacking_libs = [
        ("cv2", "OpenCV计算机视觉"),
        ("skimage", "scikit-image图像处理"),
        ("scipy", "科学计算库"),
        ("scipy.ndimage", "图像处理"),
        ("scipy.signal", "信号处理"),
    ]
    
    stacking_success = 0
    for lib, desc in stacking_libs:
        if test_import(lib, desc):
            stacking_success += 1
    
    # 模块导入测试
    print("\n🔧 Sky Editor 模块测试:")
    
    # 测试主模块
    try:
        sys.path.insert(0, '/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app/Contents/Frameworks')
        from src.main_window import ImageViewer
        print("✅ src.main_window.ImageViewer - 主窗口模块")
        main_module_success = True
    except Exception as e:
        print("❌ src.main_window.ImageViewer - 主窗口模块")
        print(f"   错误: {e}")
        main_module_success = False
    
    # 测试Camera Raw模块
    try:
        from src.modules.camera_raw.processor import CameraRawProcessor
        print("✅ src.modules.camera_raw.processor.CameraRawProcessor - Camera Raw处理器")
        camera_raw_module_success = True
    except Exception as e:
        print("❌ src.modules.camera_raw.processor.CameraRawProcessor - Camera Raw处理器")
        print(f"   错误: {e}")
        camera_raw_module_success = False
    
    # 测试星空堆叠模块
    try:
        from src.modules.stacking.processor import AstroStacker
        print("✅ src.modules.stacking.processor.AstroStacker - 星空堆叠处理器")
        stacking_processor_success = True
    except Exception as e:
        print("❌ src.modules.stacking.processor.AstroStacker - 星空堆叠处理器")
        print(f"   错误: {e}")
        stacking_processor_success = False
    
    # 测试星空堆叠UI模块
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✅ src.modules.stacking.ui.StackingWindow - 星空堆叠UI")
        stacking_ui_success = True
    except Exception as e:
        print("❌ src.modules.stacking.ui.StackingWindow - 星空堆叠UI")
        print(f"   错误: {e}")
        stacking_ui_success = False
    
    # 测试星空堆叠模块整体导入
    try:
        from src.modules.stacking import StackingWindow
        print("✅ src.modules.stacking.StackingWindow - 星空堆叠模块整体导入")
        stacking_import_success = True
    except Exception as e:
        print("❌ src.modules.stacking.StackingWindow - 星空堆叠模块整体导入")
        print(f"   错误: {e}")
        stacking_import_success = False
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    print(f"基础库: {basic_success}/{len(basic_libs)} 通过")
    print(f"Camera Raw库: {camera_raw_success}/{len(camera_raw_libs)} 通过")
    print(f"星空堆叠库: {stacking_success}/{len(stacking_libs)} 通过")
    print(f"主模块: {'✅' if main_module_success else '❌'}")
    print(f"Camera Raw模块: {'✅' if camera_raw_module_success else '❌'}")
    print(f"星空堆叠处理器: {'✅' if stacking_processor_success else '❌'}")
    print(f"星空堆叠UI: {'✅' if stacking_ui_success else '❌'}")
    print(f"星空堆叠整体导入: {'✅' if stacking_import_success else '❌'}")
    
    # 问题诊断
    print("\n🔍 问题诊断:")
    if camera_raw_success < len(camera_raw_libs):
        print("⚠️  Camera Raw功能可能不可用，缺少必要的依赖库")
    
    if stacking_success < len(stacking_libs):
        print("⚠️  星空堆叠功能可能不可用，缺少必要的依赖库")
    
    if not stacking_import_success:
        print("⚠️  星空堆叠模块导入失败，这是主要问题")
    
    # 建议
    print("\n💡 建议:")
    if camera_raw_success < len(camera_raw_libs) or stacking_success < len(stacking_libs):
        print("1. 检查PyInstaller的spec文件，确保所有依赖库都被正确包含")
        print("2. 重新打包应用程序，使用更详细的依赖库列表")
        print("3. 检查依赖库的版本兼容性")

if __name__ == "__main__":
    main()