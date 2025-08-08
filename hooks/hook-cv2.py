#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller hook for OpenCV (cv2)
解决OpenCV在打包后的递归加载问题
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os
import sys

# 收集cv2的数据文件，但避免重复收集
datas = []

# 收集cv2的动态库
binaries = collect_dynamic_libs('cv2')

# 收集所有cv2子模块
hiddenimports = collect_submodules('cv2')

# 添加额外的隐藏导入
hiddenimports.extend([
    'numpy.core._methods',
    'numpy.lib.format',
    'numpy.core._dtype_ctypes',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.linalg.lapack_lite',
    'numpy.linalg._umath_linalg',
])

# 手动添加cv2的关键配置文件，确保只收集一次
try:
    import cv2
    cv2_path = os.path.dirname(cv2.__file__)
    
    # 收集所有cv2数据文件，但排除二进制文件
    cv2_datas = collect_data_files('cv2')
    for src, dst in cv2_datas:
        # 只收集非二进制文件
        if not src.endswith(('.so', '.dylib', '.dll', '.pyd')):
            datas.append((src, dst))
    
    # 确保关键配置文件被包含
    critical_files = ['__init__.py', 'config.py', 'config-3.py']
    for filename in critical_files:
        file_path = os.path.join(cv2_path, filename)
        if os.path.exists(file_path):
            # 检查是否已经在datas中
            already_added = any(src == file_path for src, dst in datas)
            if not already_added:
                datas.append((file_path, 'cv2'))
        
    # 添加版本特定的配置文件
    version_config = os.path.join(cv2_path, f'config-{sys.version_info.major}.{sys.version_info.minor}.py')
    if os.path.exists(version_config):
        already_added = any(src == version_config for src, dst in datas)
        if not already_added:
            datas.append((version_config, 'cv2'))
        
except ImportError:
    pass

# 排除一些不需要的模块
excludedimports = ['cv2.gapi.wip.draw']