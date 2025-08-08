#!/usr/bin/env python3
"""
在打包环境中调试导入问题
"""

import sys
import os

def debug_packaged_environment():
    """调试打包环境中的导入问题"""
    print("=== 打包环境导入调试 ===\n")
    
    # 显示Python路径信息
    print("1. Python路径信息:")
    print(f"sys.executable: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径:")
    for i, path in enumerate(sys.path):
        print(f"  [{i}] {path}")
    print()
    
    # 检查src目录是否在路径中
    print("2. 检查src目录:")
    src_in_path = any('src' in path for path in sys.path)
    print(f"src目录在Python路径中: {src_in_path}")
    
    # 查找src目录的实际位置
    possible_src_paths = []
    for path in sys.path:
        src_path = os.path.join(path, 'src')
        if os.path.exists(src_path):
            possible_src_paths.append(src_path)
    
    print(f"找到的src目录: {possible_src_paths}")
    print()
    
    # 测试不同的导入方式
    print("3. 测试不同的导入方式:")
    
    # 方式1: 直接导入src
    print("方式1: 直接导入src")
    try:
        import src
        print(f"✅ src导入成功: {src.__file__}")
    except Exception as e:
        print(f"❌ src导入失败: {e}")
    
    # 方式2: 导入src.main_window
    print("\n方式2: 导入src.main_window")
    try:
        import src.main_window
        print(f"✅ src.main_window导入成功: {src.main_window.__file__}")
    except Exception as e:
        print(f"❌ src.main_window导入失败: {e}")
    
    # 方式3: 导入src.modules.stacking
    print("\n方式3: 导入src.modules.stacking")
    try:
        import src.modules.stacking
        print(f"✅ src.modules.stacking导入成功: {src.modules.stacking.__file__}")
    except Exception as e:
        print(f"❌ src.modules.stacking导入失败: {e}")
    
    # 方式4: 导入src.modules.stacking.ui
    print("\n方式4: 导入src.modules.stacking.ui")
    try:
        import src.modules.stacking.ui
        print(f"✅ src.modules.stacking.ui导入成功: {src.modules.stacking.ui.__file__}")
    except Exception as e:
        print(f"❌ src.modules.stacking.ui导入失败: {e}")
    
    # 方式5: 从src.modules.stacking导入StackingWindow
    print("\n方式5: 从src.modules.stacking导入StackingWindow")
    try:
        from src.modules.stacking import StackingWindow
        print(f"✅ StackingWindow导入成功: {StackingWindow}")
    except Exception as e:
        print(f"❌ StackingWindow导入失败: {e}")
    
    # 方式6: 导入Camera Raw
    print("\n方式6: 导入Camera Raw")
    try:
        from src.modules.camera_raw import CameraRawWindow
        print(f"✅ CameraRawWindow导入成功: {CameraRawWindow}")
    except Exception as e:
        print(f"❌ CameraRawWindow导入失败: {e}")
    
    print("\n4. 检查模块文件是否存在:")
    
    # 检查关键文件是否存在
    for path in sys.path:
        stacking_init = os.path.join(path, 'src', 'modules', 'stacking', '__init__.py')
        stacking_ui = os.path.join(path, 'src', 'modules', 'stacking', 'ui.py')
        camera_init = os.path.join(path, 'src', 'modules', 'camera_raw', '__init__.py')
        camera_ui = os.path.join(path, 'src', 'modules', 'camera_raw', 'ui.py')
        
        if os.path.exists(stacking_init):
            print(f"✅ 找到stacking __init__.py: {stacking_init}")
        if os.path.exists(stacking_ui):
            print(f"✅ 找到stacking ui.py: {stacking_ui}")
        if os.path.exists(camera_init):
            print(f"✅ 找到camera_raw __init__.py: {camera_init}")
        if os.path.exists(camera_ui):
            print(f"✅ 找到camera_raw ui.py: {camera_ui}")
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    debug_packaged_environment()