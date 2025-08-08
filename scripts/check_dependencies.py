#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查脚本
用于验证Sky Editor所需的所有依赖库是否正确安装和可用
"""

import sys
import importlib
from typing import Dict, List, Tuple

def check_import(module_name: str, description: str = "") -> Tuple[bool, str]:
    """检查单个模块的导入情况"""
    try:
        importlib.import_module(module_name)
        return True, f"✓ {module_name} - {description}"
    except ImportError as e:
        return False, f"✗ {module_name} - {description} (错误: {str(e)})"
    except Exception as e:
        return False, f"✗ {module_name} - {description} (未知错误: {str(e)})"

def check_dependencies() -> Dict[str, List[Tuple[bool, str]]]:
    """检查所有依赖项"""
    results = {
        "核心GUI库": [],
        "图像处理库": [],
        "科学计算库": [],
        "RAW处理库": [],
        "计算机视觉库": [],
        "绘图库": [],
        "项目模块": []
    }
    
    # 核心GUI库
    gui_deps = [
        ("tkinter", "GUI框架"),
        ("tkinter.ttk", "现代GUI组件"),
        ("tkinter.filedialog", "文件对话框"),
        ("tkinter.messagebox", "消息框"),
        ("tkinter.simpledialog", "简单对话框"),
        ("tkinter.colorchooser", "颜色选择器"),
    ]
    
    for module, desc in gui_deps:
        success, msg = check_import(module, desc)
        results["核心GUI库"].append((success, msg))
    
    # 图像处理库
    image_deps = [
        ("PIL", "Python图像库"),
        ("PIL.Image", "图像处理核心"),
        ("PIL.ImageTk", "Tkinter图像支持"),
        ("PIL.ImageEnhance", "图像增强"),
        ("PIL.ImageFilter", "图像滤镜"),
        ("PIL.ImageOps", "图像操作"),
        ("PIL.ImageDraw", "图像绘制"),
    ]
    
    for module, desc in image_deps:
        success, msg = check_import(module, desc)
        results["图像处理库"].append((success, msg))
    
    # 科学计算库
    science_deps = [
        ("numpy", "数值计算库"),
        ("numpy.core", "NumPy核心"),
        ("numpy.linalg", "线性代数"),
        ("numpy.fft", "快速傅里叶变换"),
        ("scipy", "科学计算库"),
        ("scipy.ndimage", "多维图像处理"),
        ("scipy.signal", "信号处理"),
    ]
    
    for module, desc in science_deps:
        success, msg = check_import(module, desc)
        results["科学计算库"].append((success, msg))
    
    # RAW处理库
    raw_deps = [
        ("rawpy", "RAW图像处理"),
    ]
    
    for module, desc in raw_deps:
        success, msg = check_import(module, desc)
        results["RAW处理库"].append((success, msg))
    
    # 计算机视觉库
    cv_deps = [
        ("cv2", "OpenCV计算机视觉库"),
        ("skimage", "科学图像处理"),
        ("skimage.filters", "图像滤波"),
        ("skimage.transform", "图像变换"),
        ("skimage.exposure", "曝光调整"),
    ]
    
    for module, desc in cv_deps:
        success, msg = check_import(module, desc)
        results["计算机视觉库"].append((success, msg))
    
    # 绘图库
    plot_deps = [
        ("matplotlib", "绘图库"),
        ("matplotlib.pyplot", "绘图接口"),
        ("matplotlib.backends.backend_tkagg", "Tkinter后端"),
    ]
    
    for module, desc in plot_deps:
        success, msg = check_import(module, desc)
        results["绘图库"].append((success, msg))
    
    # 项目模块（如果在项目目录中运行）
    try:
        import os
        if os.path.exists("src"):
            sys.path.insert(0, ".")
            project_deps = [
                ("src.main_window", "主窗口模块"),
                ("src.modules.camera_raw", "Camera Raw模块"),
                ("src.modules.camera_raw.processor", "RAW处理器"),
                ("src.modules.camera_raw.ui", "RAW界面"),
                ("src.modules.stacking", "图像堆叠模块"),
                ("src.modules.stacking.processor", "堆叠处理器"),
                ("src.modules.stacking.ui", "堆叠界面"),
            ]
            
            for module, desc in project_deps:
                success, msg = check_import(module, desc)
                results["项目模块"].append((success, msg))
    except:
        results["项目模块"].append((False, "项目模块检查跳过（不在项目目录中）"))
    
    return results

def print_results(results: Dict[str, List[Tuple[bool, str]]]):
    """打印检查结果"""
    print("=" * 60)
    print("Sky Editor 依赖检查报告")
    print("=" * 60)
    
    total_checks = 0
    total_success = 0
    
    for category, checks in results.items():
        print(f"\n【{category}】")
        print("-" * 40)
        
        for success, message in checks:
            print(f"  {message}")
            total_checks += 1
            if success:
                total_success += 1
    
    print("\n" + "=" * 60)
    print(f"检查完成: {total_success}/{total_checks} 项通过")
    
    if total_success == total_checks:
        print("✓ 所有依赖项检查通过！Sky Editor应该能正常运行。")
        return True
    else:
        print("✗ 部分依赖项缺失或有问题，可能影响Sky Editor的功能。")
        print("\n建议解决方案：")
        print("1. 安装缺失的依赖: pip install -r requirements.txt")
        print("2. 检查Python环境配置")
        print("3. 重新打包应用程序")
        return False

def main():
    """主函数"""
    print("正在检查Sky Editor依赖项...")
    results = check_dependencies()
    success = print_results(results)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()