# Sky Editor 安装与打包指南

本文档是 Sky Editor 专业天体摄影图像处理工具的完整安装、打包和异常问题处理说明手册。

## 📋 目录

- [系统要求](#系统要求)
- [开发环境安装](#开发环境安装)
- [依赖管理](#依赖管理)
- [项目打包](#项目打包)
- [安装部署](#安装部署)
- [异常问题处理](#异常问题处理)
- [性能优化](#性能优化)
- [维护指南](#维护指南)

## 🛠️ 系统要求

### 最低要求
- **操作系统**: macOS 10.14 (Mojave) 或更高版本
- **Python**: 3.8+ (推荐 3.9-3.11)
- **内存**: 8GB RAM (推荐 16GB+)
- **存储**: 2GB 可用空间
- **显示**: 支持 Retina 显示屏

### 推荐配置
- **操作系统**: macOS 12.0 (Monterey) 或更高版本
- **Python**: 3.10.x
- **内存**: 16GB+ RAM
- **存储**: 5GB+ 可用空间
- **处理器**: Apple Silicon (M1/M2) 或 Intel Core i5+

## 🔧 开发环境安装

### 1. Python 环境配置

#### 使用 Homebrew 安装 Python (推荐)
```bash
# 安装 Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.10

# 验证安装
python3 --version
pip3 --version
```

#### 使用 pyenv 管理 Python 版本
```bash
# 安装 pyenv
brew install pyenv

# 安装指定 Python 版本
pyenv install 3.10.11
pyenv global 3.10.11

# 添加到 shell 配置
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 虚拟环境设置

#### 创建虚拟环境
```bash
# 进入项目目录
cd /path/to/sky_editor

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

#### 验证环境
```bash
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version

# 检查虚拟环境路径
which python
```

## 📚 依赖管理

### 1. 核心依赖安装

#### 自动安装所有依赖
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt
```

#### 手动安装核心依赖
```bash
# 图像处理核心
pip install Pillow>=9.0.0

# 科学计算
pip install numpy>=1.21.0 scipy>=1.7.0

# RAW 图像处理
pip install rawpy>=0.17.0

# 计算机视觉
pip install opencv-python>=4.5.0 scikit-image>=0.19.0

# 绘图和可视化
pip install matplotlib>=3.5.0

# 打包工具
pip install pyinstaller>=5.0.0
```

### 2. 依赖验证

#### 使用项目提供的检查脚本
```bash
# 运行完整依赖检查
python scripts/check_dependencies.py

# 检查特定模块
python -c "import rawpy; print('rawpy 版本:', rawpy.__version__)"
python -c "import cv2; print('OpenCV 版本:', cv2.__version__)"
python -c "import numpy; print('NumPy 版本:', numpy.__version__)"
```

#### 手动验证关键功能
```bash
# 测试 GUI 框架
python -c "import tkinter; print('Tkinter 可用')"

# 测试图像处理
python -c "from PIL import Image; print('Pillow 可用')"

# 测试 RAW 处理
python -c "import rawpy; print('RAW 处理可用')"

# 测试项目模块
python -c "from src.main_window import ImageViewer; print('主模块可用')"
```

### 3. 常见依赖问题解决

#### rawpy 安装问题
```bash
# 方法1: 使用 conda 安装 (推荐)
conda install -c conda-forge rawpy

# 方法2: 安装编译工具
xcode-select --install
pip install rawpy

# 方法3: 使用预编译版本
pip install --only-binary=rawpy rawpy
```

#### OpenCV 安装问题
```bash
# 卸载可能冲突的版本
pip uninstall opencv-python opencv-contrib-python opencv-python-headless

# 重新安装
pip install opencv-python>=4.5.0

# 验证安装
python -c "import cv2; print('OpenCV 版本:', cv2.__version__)"
```

#### macOS 权限问题
```bash
# 给予 Python 相机权限 (如果需要)
sudo spctl --master-disable

# 重置权限
sudo spctl --master-enable
```

## 📦 项目打包

### 1. 打包前准备

#### 环境检查
```bash
# 确保在项目根目录
cd /path/to/sky_editor

# 激活虚拟环境
source venv/bin/activate

# 验证 Python 版本
python --version  # 应该显示 3.8+

# 检查项目依赖
python scripts/check_dependencies.py
```

#### 清理环境
```bash
# 清理之前的构建文件
rm -rf build/ dist/

# 清理 Python 缓存
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 2. 自动打包（推荐）

#### 使用完整打包脚本
```bash
# 给脚本执行权限
chmod +x scripts/build_app.sh

# 运行自动打包脚本
./scripts/build_app.sh
```

**脚本功能说明：**
- ✅ 自动检查 Python 版本和依赖
- ✅ 验证项目文件完整性
- ✅ 清理之前的构建
- ✅ 使用优化的 spec 配置
- ✅ 创建完整的 Mac 应用程序包
- ✅ 自动验证打包结果
- ✅ 提供测试运行选项

#### 使用简化打包脚本
```bash
# 快速打包（跳过部分检查）
chmod +x scripts/build_simple.sh
./scripts/build_simple.sh
```

### 3. 手动打包

#### 步骤1: 安装打包工具
```bash
# 安装 PyInstaller
pip install pyinstaller>=5.0.0

# 验证安装
pyinstaller --version
```

#### 步骤2: 使用 spec 文件打包
```bash
# 使用项目配置的 spec 文件
pyinstaller sky_editor.spec --clean

# 或使用详细输出模式
pyinstaller sky_editor.spec --clean --log-level=INFO
```

#### 步骤3: 命令行打包（备用方法）
```bash
pyinstaller \
  --onedir \
  --windowed \
  --name="Sky Editor" \
  --icon=assets/icons/app_icon.icns \
  --add-data="assets:assets" \
  --add-data="src:src" \
  --hidden-import=tkinter \
  --hidden-import=PIL \
  --hidden-import=rawpy \
  --hidden-import=cv2 \
  --hidden-import=numpy \
  --hidden-import=scipy \
  --hidden-import=matplotlib \
  --hidden-import=skimage \
  main.py
```

### 4. 打包配置详解

#### spec 文件关键配置
```python
# 应用基本信息
app = BUNDLE(
    name='Sky Editor.app',
    bundle_identifier='com.skyeditor.app',
    version='2.1.0',
    info_plist={
        'CFBundleName': 'Sky Editor',
        'CFBundleDisplayName': 'Sky Editor - 天体摄影图像处理工具',
        'NSHighResolutionCapable': True,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': [
                    'jpg', 'jpeg', 'png', 'gif', 'bmp', 
                    'tiff', 'tif', 'webp', 'ico', 
                    'arw', 'cr2', 'nef', 'dng', 'raw'
                ],
            }
        ],
    }
)
```

#### 隐藏导入配置
```python
hiddenimports=[
    # GUI 框架
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
    
    # 图像处理
    'PIL', 'PIL.Image', 'PIL.ImageTk',
    
    # 科学计算
    'numpy', 'scipy', 'rawpy', 'cv2',
    
    # 项目模块
    'src.main_window',
    'src.modules.camera_raw',
    'src.modules.stacking',
]
```

## 📁 打包结果验证

### 1. 检查打包输出

成功打包后，您会在 `dist/` 目录下找到：

```
dist/
├── Sky Editor.app/          # 完整应用包 (推荐)
│   ├── Contents/
│   │   ├── MacOS/
│   │   │   └── SkyEditor    # 可执行文件
│   │   ├── Resources/       # 资源文件
│   │   ├── Frameworks/      # 依赖库
│   │   └── Info.plist       # 应用信息
└── SkyEditor/               # 程序文件夹 (备用)
    ├── SkyEditor            # 可执行文件
    ├── _internal/           # 依赖文件
    └── ...
```

### 2. 验证应用完整性

```bash
# 检查应用包结构
ls -la "dist/Sky Editor.app/Contents/"

# 验证可执行文件
file "dist/Sky Editor.app/Contents/MacOS/SkyEditor"

# 检查应用信息
plutil -p "dist/Sky Editor.app/Contents/Info.plist"

# 测试应用启动
open "dist/Sky Editor.app"
```

### 3. 应用大小分析

```bash
# 查看应用大小
du -sh "dist/Sky Editor.app"

# 详细大小分析
du -sh "dist/Sky Editor.app/Contents/"*

# 预期大小: 150-250MB
# - Python 运行时: ~50MB
# - 图像处理库: ~80MB
# - 科学计算库: ~60MB
# - 项目代码: ~10MB
```

## 🚀 安装部署

### 1. 本地安装

#### 方法1: 拖拽安装 (推荐)
```bash
# 将应用拖拽到 Applications 文件夹
cp -R "dist/Sky Editor.app" /Applications/

# 验证安装
ls -la "/Applications/Sky Editor.app"
```

#### 方法2: 命令行安装
```bash
# 复制到 Applications
sudo cp -R "dist/Sky Editor.app" /Applications/

# 设置权限
sudo chown -R $(whoami):staff "/Applications/Sky Editor.app"

# 验证权限
ls -la "/Applications/Sky Editor.app"
```

### 2. 创建快捷方式

#### 桌面快捷方式
```bash
# 创建桌面别名
ln -s "/Applications/Sky Editor.app" ~/Desktop/

# 或使用 Finder
# 右键应用 → "制作替身" → 移动到桌面
```

#### Dock 快捷方式
```bash
# 将应用添加到 Dock
# 拖拽应用到 Dock 栏，或右键 Dock → "保留在 Dock 中"
```

### 3. 文件关联设置

#### 自动关联图像文件
```bash
# 设置默认应用程序
# 右键图像文件 → "打开方式" → "其他" → 选择 Sky Editor
# 勾选"始终以此方式打开"
```

#### 手动配置文件关联
```bash
# 使用 duti 工具设置文件关联
brew install duti

# 设置 JPEG 文件关联
duti -s com.skyeditor.app public.jpeg all

# 设置 RAW 文件关联
duti -s com.skyeditor.app com.adobe.raw-image all
```

## 🔧 异常问题处理

### 1. 打包阶段问题

#### 问题: PyInstaller 安装失败
```bash
# 症状: pip install pyinstaller 失败
# 解决方案:

# 方法1: 升级 pip
pip install --upgrade pip setuptools wheel
pip install pyinstaller

# 方法2: 使用 conda
conda install -c conda-forge pyinstaller

# 方法3: 从源码安装
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
```

#### 问题: rawpy 编译错误
```bash
# 症状: Building wheel for rawpy failed
# 解决方案:

# 方法1: 安装 Xcode Command Line Tools
xcode-select --install

# 方法2: 使用 conda 安装
conda install -c conda-forge rawpy

# 方法3: 设置编译环境
export CC=clang
export CXX=clang++
pip install rawpy

# 方法4: 使用预编译版本
pip install --only-binary=rawpy rawpy
```

#### 问题: OpenCV 导入错误
```bash
# 症状: ImportError: No module named 'cv2'
# 解决方案:

# 清理冲突版本
pip uninstall opencv-python opencv-contrib-python opencv-python-headless

# 重新安装
pip install opencv-python==4.8.1.78

# 验证安装
python -c "import cv2; print(cv2.__version__)"
```

#### 问题: 内存不足错误
```bash
# 症状: MemoryError during packaging
# 解决方案:

# 增加虚拟内存
sudo sysctl -w vm.max_map_count=262144

# 使用 --exclude-module 减少打包内容
pyinstaller sky_editor.spec --exclude-module matplotlib.tests

# 分步打包
pyinstaller --onefile --console main.py  # 先测试基本功能
```

### 2. 运行阶段问题

#### 问题: 应用无法启动
```bash
# 症状: 双击应用无响应或闪退
# 诊断方法:

# 方法1: 终端启动查看错误
"/Applications/Sky Editor.app/Contents/MacOS/SkyEditor"

# 方法2: 查看系统日志
log show --predicate 'process == "SkyEditor"' --last 5m

# 方法3: 查看 Console.app
# 打开 Console.app → 搜索 "SkyEditor"
```

#### 问题: 权限被拒绝
```bash
# 症状: "Sky Editor" cannot be opened because the developer cannot be verified
# 解决方案:

# 方法1: 系统偏好设置
# 系统偏好设置 → 安全性与隐私 → 通用 → 点击"仍要打开"

# 方法2: 命令行解除隔离
sudo xattr -rd com.apple.quarantine "/Applications/Sky Editor.app"

# 方法3: 临时禁用 Gatekeeper
sudo spctl --master-disable
# 使用后记得重新启用: sudo spctl --master-enable
```

#### 问题: 文件关联不生效
```bash
# 症状: 双击图像文件不会用 Sky Editor 打开
# 解决方案:

# 方法1: 重建 Launch Services 数据库
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user

# 方法2: 手动设置默认应用
# 右键图像文件 → 显示简介 → 打开方式 → 选择 Sky Editor → 全部更改

# 方法3: 使用 duti 工具
brew install duti
duti -s com.skyeditor.app public.image all
```

### 3. 功能模块问题

#### 问题: RAW 文件处理失败
```bash
# 症状: 无法打开 .arw, .cr2, .nef 等 RAW 文件
# 诊断:

# 检查 rawpy 是否正确打包
python -c "import rawpy; print('rawpy 可用')"

# 检查 RAW 文件支持
python -c "import rawpy; print(rawpy.supported_cameras())"

# 解决方案:
# 1. 重新安装 rawpy: pip install --force-reinstall rawpy
# 2. 检查 RAW 文件格式是否支持
# 3. 更新 rawpy 到最新版本
```

#### 问题: 星空堆叠功能异常
```bash
# 症状: 堆叠处理失败或结果异常
# 诊断:

# 检查科学计算库
python -c "import numpy, scipy, cv2, skimage; print('科学计算库正常')"

# 检查内存使用
# 堆叠大量高分辨率图像需要大量内存

# 解决方案:
# 1. 减少同时处理的图像数量
# 2. 降低图像分辨率
# 3. 增加系统内存
# 4. 使用分块处理算法
```

#### 问题: Camera Raw 调整无效果
```bash
# 症状: 调整参数后图像无变化
# 诊断:

# 检查图像格式
# Camera Raw 功能主要针对 RAW 格式

# 检查处理流程
# 确保点击了"应用"或"更新预览"

# 解决方案:
# 1. 确认使用 RAW 格式文件
# 2. 检查参数调整范围
# 3. 重启应用程序
```

### 4. 性能问题

#### 问题: 应用启动缓慢
```bash
# 症状: 应用启动需要很长时间
# 诊断:

# 检查应用大小
du -sh "/Applications/Sky Editor.app"

# 检查启动日志
log show --predicate 'process == "SkyEditor"' --last 1m

# 解决方案:
# 1. 优化 spec 文件，排除不必要的模块
# 2. 使用 --onefile 模式（但会增加启动时间）
# 3. 减少隐藏导入的模块数量
# 4. 使用 UPX 压缩（可能影响启动速度）
```

#### 问题: 内存占用过高
```bash
# 症状: 应用运行时占用大量内存
# 诊断:

# 监控内存使用
top -pid $(pgrep SkyEditor)

# 使用 Activity Monitor 查看详细信息

# 解决方案:
# 1. 优化图像处理算法
# 2. 实现图像缓存管理
# 3. 使用延迟加载
# 4. 及时释放不用的图像数据
```

### 5. 兼容性问题

#### 问题: macOS 版本兼容性
```bash
# 症状: 在某些 macOS 版本上无法运行
# 解决方案:

# 检查最低系统要求
# macOS 10.14+ (Mojave)

# 更新 spec 文件中的最低版本要求
# LSMinimumSystemVersion: '10.14'

# 使用兼容的 Python 版本
# Python 3.8-3.11 推荐
```

#### 问题: Apple Silicon 兼容性
```bash
# 症状: 在 M1/M2 Mac 上运行异常
# 解决方案:

# 使用 Universal Binary
pyinstaller sky_editor.spec --target-arch universal2

# 或分别为不同架构打包
pyinstaller sky_editor.spec --target-arch x86_64    # Intel
pyinstaller sky_editor.spec --target-arch arm64     # Apple Silicon
```

## ⚡ 性能优化

### 1. 打包优化

#### 减小应用体积
```bash
# 排除不必要的模块
pyinstaller sky_editor.spec \
  --exclude-module matplotlib.tests \
  --exclude-module numpy.tests \
  --exclude-module PIL.tests

# 使用 UPX 压缩
pyinstaller sky_editor.spec --upx-dir=/usr/local/bin

# 清理临时文件
find dist/ -name "*.pyc" -delete
find dist/ -name "__pycache__" -type d -exec rm -rf {} +
```

#### 优化启动速度
```python
# 在 spec 文件中优化导入
hiddenimports=[
    # 只包含必要的模块
    'tkinter',
    'PIL.Image',
    'numpy.core',
    'rawpy',
    # 移除不必要的子模块
]

# 使用运行时钩子优化
runtime_hooks=['hooks/rthook_optimize.py']
```

### 2. 运行时优化

#### 内存管理
```python
# 在代码中实现内存优化
import gc

def optimize_memory():
    """优化内存使用"""
    # 强制垃圾回收
    gc.collect()
    
    # 清理图像缓存
    if hasattr(self, 'image_cache'):
        self.image_cache.clear()
```

#### 多线程优化
```python
# 使用线程池处理图像
from concurrent.futures import ThreadPoolExecutor

def process_images_parallel(image_paths):
    """并行处理图像"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_single_image, image_paths))
    return results
```

### 3. 用户体验优化

#### 启动画面
```python
# 添加启动画面减少等待感
import tkinter as tk
from tkinter import ttk

def show_splash_screen():
    """显示启动画面"""
    splash = tk.Toplevel()
    splash.title("Sky Editor")
    splash.geometry("400x300")
    
    # 添加进度条和状态信息
    progress = ttk.Progressbar(splash, mode='indeterminate')
    progress.pack(pady=20)
    progress.start()
```

## 🔄 维护指南

### 1. 版本更新流程

#### 更新依赖版本
```bash
# 检查过时的依赖
pip list --outdated

# 更新特定依赖
pip install --upgrade numpy scipy matplotlib

# 更新所有依赖（谨慎使用）
pip install --upgrade -r requirements.txt

# 测试兼容性
python scripts/check_dependencies.py
```

#### 更新应用版本
```python
# 更新 spec 文件中的版本信息
app = BUNDLE(
    name='Sky Editor.app',
    version='2.2.0',  # 更新版本号
    info_plist={
        'CFBundleVersion': '2.2.0',
        'CFBundleShortVersionString': '2.2.0',
    }
)
```

### 2. 测试流程

#### 自动化测试
```bash
# 运行单元测试
python -m pytest tests/

# 运行集成测试
python tests/test_packaged_dependencies.py

# 运行功能测试
python scripts/test_features.py
```

#### 手动测试清单
```
□ 应用正常启动
□ 主要功能可用
  □ 图像浏览
  □ RAW 文件处理
  □ 星空堆叠
  □ Camera Raw 调整
□ 文件关联正常
□ 性能表现良好
□ 内存使用合理
□ 无明显 Bug
```

### 3. 发布流程

#### 准备发布
```bash
# 1. 更新版本号
# 2. 更新 CHANGELOG.md
# 3. 运行完整测试
# 4. 清理构建环境
rm -rf build/ dist/

# 5. 重新打包
./scripts/build_app.sh

# 6. 验证打包结果
python scripts/test_app.py
```

#### 分发准备
```bash
# 创建 DMG 安装包
hdiutil create -volname "Sky Editor" \
  -srcfolder "dist/Sky Editor.app" \
  -ov -format UDZO \
  "Sky Editor-2.1.0.dmg"

# 计算校验和
shasum -a 256 "Sky Editor-2.1.0.dmg" > checksums.txt
```

### 4. 备份和恢复

#### 备份重要文件
```bash
# 备份项目配置
tar -czf sky_editor_config_backup.tar.gz \
  sky_editor.spec \
  requirements.txt \
  scripts/ \
  hooks/

# 备份构建环境
pip freeze > requirements_frozen.txt
```

#### 环境恢复
```bash
# 恢复虚拟环境
python3 -m venv venv_restore
source venv_restore/bin/activate
pip install -r requirements_frozen.txt

# 验证环境
python scripts/check_dependencies.py
```

## 📋 最佳实践

### 1. 开发环境
- 使用虚拟环境隔离依赖
- 定期更新依赖版本
- 保持代码和配置的版本控制
- 编写完整的测试用例

### 2. 打包发布
- 在多个 macOS 版本上测试
- 使用自动化脚本确保一致性
- 保留详细的构建日志
- 提供清晰的安装说明

### 3. 用户支持
- 提供详细的错误诊断信息
- 建立问题反馈渠道
- 维护常见问题解答
- 定期发布更新和修复

## 📞 技术支持

### 获取帮助
- **项目文档**: 查看 `docs/` 目录下的相关文档
- **问题诊断**: 运行 `python scripts/check_dependencies.py`
- **日志分析**: 查看 Console.app 或使用 `log show` 命令
- **社区支持**: 参考 PyInstaller 和相关库的官方文档

### 报告问题
提交问题时请包含：
1. 操作系统版本
2. Python 版本
3. 依赖库版本
4. 完整的错误信息
5. 重现步骤

---

**注意**: 
- 首次运行可能需要在"系统偏好设置" → "安全性与隐私"中允许应用运行
- 建议定期备份项目配置和构建环境
- 保持依赖库的版本更新，但要充分测试兼容性