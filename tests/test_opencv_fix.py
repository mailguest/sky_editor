#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OpenCV修复后的导入问题
"""

import sys
import os

# 模拟打包后的环境
packaged_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app/Contents/Frameworks"
sys.path.insert(0, packaged_path)

def test_opencv():
    """测试OpenCV导入"""
    print("测试OpenCV导入...")
    
    try:
        import cv2
        print(f"✅ OpenCV导入成功，版本: {cv2.__version__}")
        
        # 测试基本功能
        import numpy as np
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_img, cv2.COLOR_RGB2GRAY)
        print("✅ OpenCV基本功能测试成功")
        
        return True
    except Exception as e:
        print(f"❌ OpenCV导入失败: {e}")
        return False

def test_stacking_dependencies():
    """测试星空堆叠的所有依赖"""
    print("\n测试星空堆叠依赖...")
    
    dependencies = [
        ("numpy", "数值计算"),
        ("PIL", "图像处理"),
        ("cv2", "计算机视觉"),
        ("threading", "多线程"),
        ("time", "时间处理"),
        ("pathlib", "路径处理"),
        ("json", "JSON处理"),
        ("typing", "类型提示"),
        ("logging", "日志记录"),
    ]
    
    success_count = 0
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - {desc}")
            success_count += 1
        except Exception as e:
            print(f"❌ {dep} - {desc}: {e}")
    
    return success_count == len(dependencies)

def test_stacking_processor():
    """测试星空堆叠处理器"""
    print("\n测试星空堆叠处理器...")
    
    try:
        from src.modules.stacking.processor import AstroStacker
        print("✅ AstroStacker导入成功")
        
        # 创建实例
        stacker = AstroStacker()
        print("✅ AstroStacker实例创建成功")
        
        return True
    except Exception as e:
        print(f"❌ AstroStacker导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stacking_ui():
    """测试星空堆叠UI"""
    print("\n测试星空堆叠UI...")
    
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✅ StackingWindow导入成功")
        return True
    except Exception as e:
        print(f"❌ StackingWindow导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stacking_module():
    """测试星空堆叠模块整体导入"""
    print("\n测试星空堆叠模块整体导入...")
    
    try:
        from src.modules.stacking import StackingWindow
        print("✅ 星空堆叠模块整体导入成功")
        return True
    except Exception as e:
        print(f"❌ 星空堆叠模块整体导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("OpenCV修复后的测试")
    print("=" * 60)
    
    # 测试OpenCV
    opencv_ok = test_opencv()
    
    # 测试依赖
    deps_ok = test_stacking_dependencies()
    
    # 测试处理器
    processor_ok = test_stacking_processor()
    
    # 测试UI
    ui_ok = test_stacking_ui()
    
    # 测试模块整体导入
    module_ok = test_stacking_module()
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    print(f"OpenCV: {'✅' if opencv_ok else '❌'}")
    print(f"依赖库: {'✅' if deps_ok else '❌'}")
    print(f"星空堆叠处理器: {'✅' if processor_ok else '❌'}")
    print(f"星空堆叠UI: {'✅' if ui_ok else '❌'}")
    print(f"星空堆叠模块: {'✅' if module_ok else '❌'}")
    
    if all([opencv_ok, deps_ok, processor_ok, ui_ok, module_ok]):
        print("\n🎉 所有测试通过！星空堆叠功能应该可以正常使用了。")
    else:
        print("\n⚠️  仍有问题需要解决。")

if __name__ == "__main__":
    main()