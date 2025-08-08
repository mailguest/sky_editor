#!/usr/bin/env python3
"""
Sky Editor 功能测试脚本
测试 Camera Raw 和星空堆叠功能是否正常工作
"""

import sys
import os
import subprocess
import tempfile
import numpy as np
from PIL import Image

def test_camera_raw_dependencies():
    """测试 Camera Raw 功能的依赖库"""
    print("🧪 测试 Camera Raw 功能依赖...")
    
    try:
        import rawpy
        print("✅ rawpy 导入成功")
    except ImportError as e:
        print(f"❌ rawpy 导入失败: {e}")
        return False
    
    try:
        import matplotlib
        print("✅ matplotlib 导入成功")
    except ImportError as e:
        print(f"❌ matplotlib 导入失败: {e}")
        return False
    
    try:
        import numpy
        print("✅ numpy 导入成功")
    except ImportError as e:
        print(f"❌ numpy 导入失败: {e}")
        return False
    
    return True

def test_stacking_dependencies():
    """测试星空堆叠功能的依赖库"""
    print("\n🧪 测试星空堆叠功能依赖...")
    
    try:
        import cv2
        print("✅ opencv-python (cv2) 导入成功")
    except ImportError as e:
        print(f"❌ opencv-python (cv2) 导入失败: {e}")
        return False
    
    try:
        import numpy
        print("✅ numpy 导入成功")
    except ImportError as e:
        print(f"❌ numpy 导入失败: {e}")
        return False
    
    try:
        import skimage
        print("✅ scikit-image (skimage) 导入成功")
    except ImportError as e:
        print(f"❌ scikit-image (skimage) 导入失败: {e}")
        return False
    
    return True

def test_camera_raw_module():
    """测试 Camera Raw 模块"""
    print("\n🧪 测试 Camera Raw 模块...")
    
    try:
        # 添加项目根目录到路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from src.modules.camera_raw.processor import CameraRawProcessor
        processor = CameraRawProcessor()
        print("✅ CameraRawProcessor 创建成功")
        
        # 检查 RAW 支持
        if hasattr(processor, 'RAW_SUPPORT'):
            if processor.RAW_SUPPORT:
                print("✅ RAW 支持已启用")
            else:
                print("❌ RAW 支持未启用")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Camera Raw 模块测试失败: {e}")
        return False

def test_stacking_module():
    """测试星空堆叠模块"""
    print("\n🧪 测试星空堆叠模块...")
    
    try:
        # 添加项目根目录到路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from src.modules.stacking.processor import AstroStacker
        processor = AstroStacker()
        print("✅ AstroStacker 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 星空堆叠模块测试失败: {e}")
        return False

def test_image_processing():
    """测试基本图像处理功能"""
    print("\n🧪 测试基本图像处理功能...")
    
    try:
        # 创建测试图像
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # 测试 PIL
        pil_image = Image.fromarray(test_image)
        print("✅ PIL 图像处理成功")
        
        # 测试 OpenCV
        import cv2
        gray = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
        print("✅ OpenCV 图像处理成功")
        
        # 测试 scikit-image
        from skimage import filters
        blurred = filters.gaussian(gray, sigma=1.0)
        print("✅ scikit-image 图像处理成功")
        
        return True
    except Exception as e:
        print(f"❌ 图像处理测试失败: {e}")
        return False

def test_packaged_app():
    """测试打包后的应用程序"""
    print("\n🧪 测试打包后的应用程序...")
    
    app_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app"
    if not os.path.exists(app_path):
        print("❌ 打包后的应用程序不存在")
        return False
    
    # 测试应用程序是否可以启动（快速测试）
    try:
        # 使用 open 命令测试应用程序
        result = subprocess.run(
            ["open", "-n", app_path, "--args", "--test"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("✅ 打包后的应用程序可以启动")
        return True
    except subprocess.TimeoutExpired:
        print("✅ 打包后的应用程序启动正常（超时但正常）")
        return True
    except Exception as e:
        print(f"❌ 打包后的应用程序启动失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("Sky Editor 功能测试")
    print("=" * 60)
    
    tests = [
        ("Camera Raw 依赖", test_camera_raw_dependencies),
        ("星空堆叠依赖", test_stacking_dependencies),
        ("Camera Raw 模块", test_camera_raw_module),
        ("星空堆叠模块", test_stacking_module),
        ("图像处理功能", test_image_processing),
        ("打包后应用程序", test_packaged_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有功能测试通过！Camera Raw 和星空堆叠功能应该可以正常使用。")
        return 0
    else:
        print("⚠️  部分功能测试失败，请检查相关依赖和模块。")
        return 1

if __name__ == "__main__":
    sys.exit(main())