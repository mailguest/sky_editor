#!/bin/bash

# Sky Editor - 图片批量预览器启动脚本

echo "=== Sky Editor - 图片批量预览器 ==="
echo "正在检查Python环境..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7或更高版本"
    exit 1
fi

# 显示Python版本
python3 --version

# 检查并安装依赖
echo "正在检查依赖包..."
if ! python3 -c "import PIL" &> /dev/null; then
    echo "正在安装Pillow..."
    pip3 install Pillow>=10.0.0
fi

# 启动程序
echo "启动图片预览器..."
python3 image_viewer.py