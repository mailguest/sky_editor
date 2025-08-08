#!/bin/bash

# Sky Editor 简单打包脚本
# 快速打包，不包含复杂配置

echo "🚀 Sky Editor v2.1.0 快速打包..."
echo "📝 简化版本，适合快速测试"

# 安装PyInstaller（如果未安装）
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 安装 PyInstaller..."
    pip3 install pyinstaller
fi

# 清理
echo "🧹 清理旧文件..."
rm -rf build/ dist/

# 简单打包命令
echo "📱 开始打包..."
pyinstaller --onedir \
    --windowed \
    --name="SkyEditor" \
    --add-data="src:src" \
    --add-data="assets:assets" \
    --hidden-import="PIL._tkinter_finder" \
    --hidden-import="rawpy" \
    --hidden-import="numpy" \
    --hidden-import="tkinter" \
    --hidden-import="tkinter.ttk" \
    --hidden-import="tkinter.filedialog" \
    --hidden-import="tkinter.messagebox" \
    --hidden-import="tkinter.simpledialog" \
    --hidden-import="cv2" \
    --hidden-import="matplotlib" \
    --hidden-import="scipy" \
    --hidden-import="skimage" \
    main.py

if [ -d "dist/SkyEditor" ]; then
    echo ""
    echo "✅ 快速打包完成！"
    echo "📍 程序位置: dist/SkyEditor/"
    echo "🚀 运行命令: ./dist/SkyEditor/SkyEditor"
    echo ""
    echo "💡 注意: 这是简化版本，如需完整的Mac应用程序包，请使用:"
    echo "   ./scripts/build_app.sh"
    
    # 获取大小
    app_size=$(du -sh "dist/SkyEditor" | cut -f1)
    echo "📊 程序大小: $app_size"
else
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi