"""
运行时 hook 用于修复 macOS .app 包中的 cv2 导入问题
"""
import sys
import os

# 检查是否在 macOS .app 包中运行
if hasattr(sys, 'frozen') and sys.frozen:
    if sys.platform == 'darwin' and '.app/Contents/' in sys.executable:
        # 在 .app 包中运行
        bundle_dir = os.path.dirname(sys.executable)
        frameworks_dir = os.path.join(bundle_dir, '..', 'Frameworks')
        resources_dir = os.path.join(bundle_dir, '..', 'Resources')
        
        # 确保 Resources/cv2 在 Frameworks/cv2 之前
        cv2_resources = os.path.join(resources_dir, 'cv2')
        cv2_frameworks = os.path.join(frameworks_dir, 'cv2')
        
        if os.path.exists(cv2_resources) and os.path.exists(cv2_frameworks):
            # 临时重命名 Frameworks 中的 cv2 目录以避免冲突
            cv2_frameworks_backup = cv2_frameworks + '_backup'
            try:
                if not os.path.exists(cv2_frameworks_backup):
                    os.rename(cv2_frameworks, cv2_frameworks_backup)
            except OSError:
                pass  # 如果重命名失败，继续执行
            
            # 确保 Resources 目录在 sys.path 中
            resources_abs = os.path.abspath(resources_dir)
            if resources_abs not in sys.path:
                sys.path.insert(0, resources_abs)
            
            # 确保 Frameworks 目录在 sys.path 中（用于其他依赖）
            frameworks_abs = os.path.abspath(frameworks_dir)
            if frameworks_abs not in sys.path:
                sys.path.append(frameworks_abs)