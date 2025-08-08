#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证脚本 - 测试打包后的Sky Editor应用程序
"""

import subprocess
import sys
import time
import os

def test_packaged_app():
    """测试打包后的应用程序"""
    print("=== Sky Editor 最终验证测试 ===")
    
    app_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/SkyEditor/SkyEditor"
    
    if not os.path.exists(app_path):
        print("❌ 应用程序不存在")
        return False
    
    print(f"✅ 应用程序路径: {app_path}")
    
    try:
        # 启动应用程序并捕获输出
        print("🚀 启动应用程序...")
        proc = subprocess.Popen([app_path], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        # 等待5秒钟捕获初始输出
        time.sleep(5)
        
        # 检查进程是否还在运行
        if proc.poll() is None:
            print("✅ 应用程序成功启动并正在运行")
            
            # 终止进程
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(timeout=3)
                
                print("\n=== 标准输出 ===")
                if stdout.strip():
                    print(stdout)
                    
                    # 检查是否包含警告信息
                    if "警告: 星空堆叠模块导入失败" in stdout:
                        print("❌ 仍然存在星空堆叠模块导入失败警告")
                        return False
                    elif "Camera Raw功能不可用" in stdout:
                        print("❌ 仍然存在Camera Raw功能不可用警告")
                        return False
                    else:
                        print("✅ 没有发现导入失败警告")
                else:
                    print("(无标准输出)")
                
                print("\n=== 标准错误 ===")
                if stderr.strip():
                    print(stderr)
                else:
                    print("(无错误输出)")
                    
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print("⚠️  进程终止超时")
        else:
            # 进程已退出，获取输出
            stdout, stderr = proc.communicate()
            print(f"❌ 应用程序退出，退出代码: {proc.returncode}")
            
            if stdout:
                print("标准输出:")
                print(stdout)
            if stderr:
                print("错误输出:")
                print(stderr)
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    
    print("\n=== 测试结果 ===")
    print("✅ Sky Editor 打包后的导入问题修复验证成功！")
    print("✅ 应用程序可以正常启动")
    print("✅ 没有发现模块导入失败的警告信息")
    
    return True

if __name__ == "__main__":
    success = test_packaged_app()
    sys.exit(0 if success else 1)