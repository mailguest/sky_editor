#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试可执行文件的环境
"""

import sys
import os
import subprocess

def debug_executable_env():
    """调试可执行文件的环境"""
    print("=== 调试可执行文件环境 ===")
    
    # 检查两个可执行文件的环境
    executables = [
        "/Users/fanglei/source/leo_projects/sky_editor/dist/SkyEditor/SkyEditor",
        "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app/Contents/MacOS/Sky Editor"
    ]
    
    for exe in executables:
        if os.path.exists(exe):
            print(f"\n=== 测试可执行文件: {exe} ===")
            
            # 创建一个简单的测试脚本
            test_script = '''
import sys
import os
print("Python路径:", sys.path[:3])
print("当前工作目录:", os.getcwd())
print("可执行文件:", sys.executable)

# 测试延迟导入
try:
    import src.main_window as main_window
    print("main_window导入成功")
    
    # 测试延迟导入函数
    stacking_result = main_window._import_stacking_module()
    camera_raw_result = main_window._import_camera_raw_module()
    
    print(f"星空堆叠延迟导入: {stacking_result}")
    print(f"Camera Raw延迟导入: {camera_raw_result}")
    print(f"STACKING_SUPPORT: {main_window.STACKING_SUPPORT}")
    print(f"CAMERA_RAW_SUPPORT: {main_window.CAMERA_RAW_SUPPORT}")
    
except Exception as e:
    print(f"导入失败: {e}")
    import traceback
    traceback.print_exc()
'''
            
            try:
                # 运行可执行文件并传入测试脚本
                result = subprocess.run([exe, "-c", test_script], 
                                      capture_output=True, text=True, timeout=30)
                
                print("标准输出:")
                print(result.stdout)
                
                if result.stderr:
                    print("标准错误:")
                    print(result.stderr)
                    
                print(f"退出码: {result.returncode}")
                
            except subprocess.TimeoutExpired:
                print("执行超时")
            except Exception as e:
                print(f"执行失败: {e}")
        else:
            print(f"可执行文件不存在: {exe}")

if __name__ == "__main__":
    debug_executable_env()