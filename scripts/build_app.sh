#!/bin/bash

# Sky Editor Mac App 打包脚本
# 使用PyInstaller将Python程序打包成Mac应用程序

echo "🚀 开始打包 Sky Editor v2.1.0..."
echo "📝 功能包括: Camera Raw处理、星空图像堆叠、图像浏览"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python版本: $python_version"

# 检查是否安装了PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller 未安装，正在安装..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ PyInstaller 安装失败，请手动安装: pip3 install pyinstaller"
        exit 1
    fi
fi

# 检查依赖是否安装
echo "🔍 运行详细依赖检查..."
python3 scripts/check_dependencies.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 依赖检查失败！"
    echo "请解决上述依赖问题后重新运行打包脚本。"
    echo ""
    echo "常见解决方案："
    echo "1. 安装所有依赖: pip3 install -r requirements.txt"
    echo "2. 单独安装缺失的库:"
    echo "   pip3 install rawpy numpy opencv-python matplotlib scipy scikit-image"
    echo "3. 如果使用conda: conda install -c conda-forge rawpy opencv matplotlib"
    exit 1
fi

echo ""
echo "✓ 所有依赖检查通过！"

if [ $? -ne 0 ]; then
    echo "⚠️  部分依赖未安装，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请检查 requirements.txt"
        exit 1
    fi
fi

# 清理之前的构建
echo ""
echo "🧹 清理之前的构建..."
rm -rf build/
rm -rf dist/

# 检查必要文件
echo "📋 检查项目文件..."
if [ ! -f "main.py" ]; then
    echo "❌ 找不到 main.py 文件"
    exit 1
fi

if [ ! -f "sky_editor.spec" ]; then
    echo "❌ 找不到 sky_editor.spec 文件"
    exit 1
fi

if [ ! -d "src" ]; then
    echo "❌ 找不到 src 目录"
    exit 1
fi

echo "✅ 项目文件检查完成"

# 使用PyInstaller打包
echo ""
echo "📱 开始打包应用程序..."
echo "⏳ 这可能需要几分钟时间，请耐心等待..."
pyinstaller sky_editor.spec --clean

# 检查打包结果
if [ -d "dist/Sky Editor.app" ]; then
    echo ""
    echo "🎉 打包成功！"
    echo "📍 应用程序位置: $(pwd)/dist/Sky Editor.app"
    echo ""
    
    # 获取应用程序大小
    app_size=$(du -sh "dist/Sky Editor.app" | cut -f1)
    echo "📊 应用程序信息:"
    echo "   • 大小: $app_size"
    echo "   • 版本: 2.1.0"
    echo "   • 功能: Camera Raw处理、星空图像堆叠、图像浏览"
    echo ""
    
    echo "🎯 使用方法:"
    echo "   1. 直接运行: open 'dist/Sky Editor.app'"
    echo "   2. 拖拽到 /Applications 文件夹"
    echo "   3. 右键创建桌面快捷方式"
    echo ""
    
    # 验证应用程序
    echo "🔍 验证应用程序..."
    if [ -f "dist/Sky Editor.app/Contents/MacOS/SkyEditor" ]; then
        echo "✅ 可执行文件存在"
    else
        echo "⚠️  可执行文件可能有问题"
    fi
    
    # 询问是否立即运行
    read -p "🤔 是否立即运行应用程序进行测试？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 启动 Sky Editor..."
        open "dist/Sky Editor.app"
        echo "✨ 如果应用程序正常启动，说明打包成功！"
    fi
    
    echo ""
    echo "📦 打包完成！应用程序已保存到 dist/ 目录"
else
    echo ""
    echo "❌ 打包失败，请检查上方的错误信息"
    echo "💡 常见问题解决方案:"
    echo "   1. 确保所有依赖都已安装: pip3 install -r requirements.txt"
    echo "   2. 检查Python版本是否兼容"
    echo "   3. 查看详细错误信息并搜索解决方案"
    exit 1
fi