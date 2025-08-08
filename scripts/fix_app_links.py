#!/usr/bin/env python3
"""
修复 macOS .app 包中的库链接问题
"""
import os
import subprocess
import sys

def fix_app_links(app_path):
    """修复 .app 包中的库链接问题"""
    frameworks_dir = os.path.join(app_path, "Contents", "Frameworks")
    pil_dir = os.path.join(frameworks_dir, "PIL")
    
    if not os.path.exists(frameworks_dir) or not os.path.exists(pil_dir):
        print(f"错误: 找不到必要的目录")
        return False
    
    # 获取所有 .dylib 文件
    dylib_files = []
    for root, dirs, files in os.walk(frameworks_dir):
        for file in files:
            if file.endswith('.dylib') and not os.path.islink(os.path.join(root, file)):
                dylib_files.append(file)
    
    print(f"找到 {len(dylib_files)} 个动态库文件")
    
    # 在 PIL 目录中创建软链接
    fixed_count = 0
    for dylib in dylib_files:
        pil_link = os.path.join(pil_dir, dylib)
        frameworks_target = os.path.join("..", dylib)
        
        # 如果链接不存在或者是坏链接，创建新链接
        if not os.path.exists(pil_link) or (os.path.islink(pil_link) and not os.path.exists(os.readlink(pil_link))):
            try:
                if os.path.islink(pil_link):
                    os.unlink(pil_link)
                elif os.path.exists(pil_link):
                    continue  # 如果是真实文件，跳过
                
                os.symlink(frameworks_target, pil_link)
                print(f"创建链接: {dylib}")
                fixed_count += 1
            except OSError as e:
                print(f"创建链接失败 {dylib}: {e}")
    
    print(f"修复了 {fixed_count} 个库链接")
    return True

if __name__ == "__main__":
    app_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app"
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用包 {app_path}")
        sys.exit(1)
    
    print(f"修复应用包: {app_path}")
    if fix_app_links(app_path):
        print("修复完成!")
    else:
        print("修复失败!")
        sys.exit(1)