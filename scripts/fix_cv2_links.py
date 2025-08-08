#!/usr/bin/env python3
"""
修复指向 cv2/.dylibs/ 的链接，将其改为 cv2_backup/.dylibs/
"""
import os
import subprocess
import sys

def fix_cv2_links(app_path):
    """修复指向 cv2/.dylibs/ 的链接"""
    frameworks_dir = os.path.join(app_path, "Contents", "Frameworks")
    
    if not os.path.exists(frameworks_dir):
        print(f"错误: 找不到 Frameworks 目录")
        return False
    
    fixed_count = 0
    
    # 遍历 Frameworks 目录中的所有文件
    for item in os.listdir(frameworks_dir):
        item_path = os.path.join(frameworks_dir, item)
        
        # 检查是否是软链接
        if os.path.islink(item_path):
            link_target = os.readlink(item_path)
            
            # 如果链接指向 cv2/.dylibs/，修复为 cv2_backup/.dylibs/
            if link_target.startswith("cv2/.dylibs/"):
                new_target = link_target.replace("cv2/.dylibs/", "cv2_backup/.dylibs/")
                
                try:
                    os.unlink(item_path)
                    os.symlink(new_target, item_path)
                    print(f"修复链接: {item} -> {new_target}")
                    fixed_count += 1
                except OSError as e:
                    print(f"修复链接失败 {item}: {e}")
    
    print(f"修复了 {fixed_count} 个 cv2 链接")
    return True

if __name__ == "__main__":
    app_path = "/Users/fanglei/source/leo_projects/sky_editor/dist/Sky Editor.app"
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用包 {app_path}")
        sys.exit(1)
    
    print(f"修复应用包中的 cv2 链接: {app_path}")
    if fix_cv2_links(app_path):
        print("修复完成!")
    else:
        print("修复失败!")
        sys.exit(1)