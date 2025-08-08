#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包环境中的依赖库导入
"""

import sys
import os

def test_dependencies():
    """测试所有依赖库的导入"""
    print("=== 依赖库导入测试 ===")
    print(f"Python路径: {sys.path[:3]}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 测试基础库
    print("\n=== 基础库测试 ===")
    
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ numpy 导入失败: {e}")
    
    try:
        import matplotlib
        print(f"✅ matplotlib {matplotlib.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ matplotlib 导入失败: {e}")
    
    try:
        import cv2
        print(f"✅ cv2 {cv2.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ cv2 导入失败: {e}")
    
    try:
        import rawpy
        print(f"✅ rawpy {rawpy.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ rawpy 导入失败: {e}")
    
    try:
        import skimage
        print(f"✅ skimage {skimage.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ skimage 导入失败: {e}")
    
    try:
        import scipy
        print(f"✅ scipy {scipy.__version__} 导入成功")
    except ImportError as e:
        print(f"❌ scipy 导入失败: {e}")
    
    # 测试模块导入
    print("\n=== 模块导入测试 ===")
    
    try:
        print("测试: from src.modules.camera_raw.processor import CameraRawProcessor")
        from src.modules.camera_raw.processor import CameraRawProcessor
        print("✅ CameraRawProcessor 导入成功")
        
        # 测试实例化
        processor = CameraRawProcessor()
        print("✅ CameraRawProcessor 实例化成功")
    except ImportError as e:
        print(f"❌ CameraRawProcessor 导入失败: {e}")
    except Exception as e:
        print(f"❌ CameraRawProcessor 实例化失败: {e}")
    
    try:
        print("测试: from src.modules.camera_raw.ui import CameraRawWindow")
        from src.modules.camera_raw.ui import CameraRawWindow
        print("✅ CameraRawWindow 导入成功")
    except ImportError as e:
        print(f"❌ CameraRawWindow 导入失败: {e}")
    except Exception as e:
        print(f"❌ CameraRawWindow 导入异常: {e}")
    
    try:
        print("测试: from src.modules.stacking.processor import AstroStacker")
        from src.modules.stacking.processor import AstroStacker
        print("✅ AstroStacker 导入成功")
        
        # 测试实例化
        stacker = AstroStacker()
        print("✅ AstroStacker 实例化成功")
    except ImportError as e:
        print(f"❌ AstroStacker 导入失败: {e}")
    except Exception as e:
        print(f"❌ AstroStacker 实例化失败: {e}")
    
    try:
        print("测试: from src.modules.stacking.ui import StackingWindow")
        from src.modules.stacking.ui import StackingWindow
        print("✅ StackingWindow 导入成功")
    except ImportError as e:
        print(f"❌ StackingWindow 导入失败: {e}")
    except Exception as e:
        print(f"❌ StackingWindow 导入异常: {e}")
    
    # 测试完整模块导入
    print("\n=== 完整模块导入测试 ===")
    
    try:
        print("测试: from src.modules.camera_raw import CameraRawWindow")
        from src.modules.camera_raw import CameraRawWindow
        print("✅ 完整Camera Raw模块导入成功")
    except ImportError as e:
        print(f"❌ 完整Camera Raw模块导入失败: {e}")
    except Exception as e:
        print(f"❌ 完整Camera Raw模块导入异常: {e}")
    
    try:
        print("测试: from src.modules.stacking import StackingWindow")
        from src.modules.stacking import StackingWindow
        print("✅ 完整星空堆叠模块导入成功")
    except ImportError as e:
        print(f"❌ 完整星空堆叠模块导入失败: {e}")
    except Exception as e:
        print(f"❌ 完整星空堆叠模块导入异常: {e}")

if __name__ == "__main__":
    test_dependencies()