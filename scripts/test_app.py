#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sky Editor 应用程序功能测试脚本
用于验证打包后的应用程序是否正常工作
"""

import sys
import subprocess
import time
import os
from pathlib import Path

def test_app_launch():
    """测试应用程序启动"""
    print("🚀 测试应用程序启动...")
    
    app_path = Path("dist/Sky Editor.app")
    if not app_path.exists():
        print("❌ 应用程序不存在")
        return False
    
    try:
        # 启动应用程序
        process = subprocess.Popen(
            ["open", str(app_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待启动
        time.sleep(3)
        
        # 检查是否有错误
        if process.poll() is None or process.returncode == 0:
            print("✅ 应用程序启动成功")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 应用程序启动失败: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖库是否正确包含"""
    print("🔍 测试依赖库...")
    
    # 检查关键文件是否存在
    critical_files = [
        "dist/SkyEditor/_internal/rawpy",
        "dist/SkyEditor/_internal/numpy",
        "dist/SkyEditor/_internal/scipy",
        "dist/SkyEditor/_internal/matplotlib",
        "dist/SkyEditor/_internal/skimage",
        "dist/SkyEditor/_internal/cv2",
        "dist/SkyEditor/_internal/src",
        "dist/SkyEditor/_internal/assets",
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少关键文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ 所有关键依赖文件都存在")
        return True

def test_app_size():
    """检查应用程序大小"""
    print("📊 检查应用程序大小...")
    
    try:
        # 获取应用程序大小
        result = subprocess.run(
            ["du", "-sh", "dist/Sky Editor.app"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            size = result.stdout.split()[0]
            print(f"📦 应用程序大小: {size}")
            
            # 检查大小是否合理（应该在200M-400M之间）
            if "M" in size:
                size_num = float(size.replace("M", ""))
                if 200 <= size_num <= 400:
                    print("✅ 应用程序大小正常")
                    return True
                else:
                    print(f"⚠️ 应用程序大小异常: {size}")
                    return False
            else:
                print(f"⚠️ 无法解析应用程序大小: {size}")
                return False
        else:
            print("❌ 无法获取应用程序大小")
            return False
            
    except Exception as e:
        print(f"❌ 大小检查失败: {e}")
        return False

def test_app_structure():
    """检查应用程序结构"""
    print("🏗️ 检查应用程序结构...")
    
    required_structure = [
        "dist/Sky Editor.app/Contents",
        "dist/Sky Editor.app/Contents/Info.plist",
        "dist/Sky Editor.app/Contents/MacOS",
        "dist/Sky Editor.app/Contents/Resources",
        "dist/SkyEditor/SkyEditor",
        "dist/SkyEditor/_internal",
    ]
    
    missing_structure = []
    for path in required_structure:
        if not Path(path).exists():
            missing_structure.append(path)
    
    if missing_structure:
        print("❌ 应用程序结构不完整:")
        for path in missing_structure:
            print(f"   - {path}")
        return False
    else:
        print("✅ 应用程序结构完整")
        return True

def run_comprehensive_test():
    """运行综合测试"""
    print("=" * 60)
    print("Sky Editor 应用程序测试")
    print("=" * 60)
    
    tests = [
        ("应用程序结构", test_app_structure),
        ("依赖库检查", test_dependencies),
        ("应用程序大小", test_app_size),
        ("应用程序启动", test_app_launch),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}测试:")
        print("-" * 40)
        
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"❌ {test_name}测试失败")
        except Exception as e:
            print(f"❌ {test_name}测试出错: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed_tests}/{total_tests} 项通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！Sky Editor 应用程序可以正常使用。")
        print("\n📋 使用说明:")
        print("1. 双击 'Sky Editor.app' 启动应用程序")
        print("2. 或者将应用程序拖拽到 /Applications 文件夹")
        print("3. 首次运行可能需要在系统偏好设置中允许运行")
        return True
    else:
        print("⚠️ 部分测试失败，应用程序可能存在问题。")
        print("\n🔧 建议:")
        print("1. 检查打包过程是否有错误")
        print("2. 重新运行打包脚本")
        print("3. 检查依赖库是否正确安装")
        return False

def main():
    """主函数"""
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()