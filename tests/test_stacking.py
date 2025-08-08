#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试星空堆叠功能
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_imports():
    """测试所有必要的导入"""
    print("测试导入...")
    
    try:
        import numpy as np
        print("✓ numpy 导入成功")
    except ImportError as e:
        print(f"✗ numpy 导入失败: {e}")
        return False
    
    try:
        import cv2
        print(f"✓ opencv-python 导入成功 (版本: {cv2.__version__})")
    except ImportError as e:
        print(f"✗ opencv-python 导入失败: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL 导入成功")
    except ImportError as e:
        print(f"✗ PIL 导入失败: {e}")
        return False
    
    try:
        from skimage import feature, transform, filters
        print("✓ scikit-image 导入成功")
    except ImportError as e:
        print(f"✗ scikit-image 导入失败: {e}")
        return False
    
    try:
        from src.modules.stacking.processor import AstroStacker
        print("✓ AstroStacker 导入成功")
    except ImportError as e:
        print(f"✗ AstroStacker 导入失败: {e}")
        return False
    
    try:
        from src.modules.stacking.ui import StackingWindow
        print("✓ StackingWindow 导入成功")
    except ImportError as e:
        print(f"✗ StackingWindow 导入失败: {e}")
        return False
    
    return True

def test_astro_stacker():
    """测试AstroStacker类的基本功能"""
    print("\n测试AstroStacker...")
    
    try:
        from src.modules.stacking.processor import AstroStacker
        
        # 创建实例
        stacker = AstroStacker()
        print("✓ AstroStacker 实例创建成功")
        
        # 测试参数设置
        stacker.set_star_detection_params(threshold=0.1, min_area=5, max_area=1000)
        print("✓ 星点检测参数设置成功")
        
        stacker.set_alignment_params(max_features=500, match_threshold=0.7)
        print("✓ 图像对齐参数设置成功")
        
        stacker.set_stacking_params(method='average', sigma_clip=True, sigma_lower=2.0, sigma_upper=2.0)
        print("✓ 图像堆叠参数设置成功")
        
        return True
        
    except Exception as e:
        print(f"✗ AstroStacker 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Sky Editor 星空堆叠功能测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖库安装")
        return False
    
    # 测试AstroStacker
    if not test_astro_stacker():
        print("\n❌ AstroStacker 测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！星空堆叠功能已准备就绪")
    print("=" * 50)
    print("\n使用方法：")
    print("1. 运行 Sky Editor: python main.py")
    print("2. 在菜单栏选择：工具 -> 星空图像堆叠")
    print("3. 添加星空图像文件")
    print("4. 调整参数并开始堆叠")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)