# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('src', 'src'),
    ],
    hiddenimports=[
        # Tkinter 相关
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'tkinter.font',
        
        # PIL/Pillow 相关
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
        'PIL.ImageOps',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL._tkinter_finder',
        
        # 核心科学计算库
        'numpy',
        'numpy.core',
        'numpy.core.multiarray',
        'numpy.core.umath',
        'numpy.linalg',
        'numpy.random',
        'numpy.fft',
        
        # RAW 处理
        'rawpy',
        'rawpy._rawpy',
        
        # OpenCV - 修复递归加载问题
        'cv2',
        'cv2.cv2',
        'cv2.data',
        'cv2.gapi',
        'cv2.utils',
        'cv2.mat_wrapper',
        
        # Matplotlib
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'matplotlib.axes',
        
        # 科学图像处理
        'skimage',
        'skimage.filters',
        'skimage.transform',
        'skimage.measure',
        'skimage.morphology',
        'skimage.exposure',
        'skimage.restoration',
        
        # SciPy
        'scipy',
        'scipy.ndimage',
        'scipy.signal',
        'scipy.optimize',
        'scipy.interpolate',
        
        # 标准库
        'json',
        'pathlib',
        'threading',
        'logging',
        'time',
        'os',
        'sys',
        'typing',
        
        # 项目模块
        'src.main_window',
        'src.modules.camera_raw',
        'src.modules.camera_raw.processor',
        'src.modules.camera_raw.ui',
        'src.modules.stacking',
        'src.modules.stacking.processor',
        'src.modules.stacking.ui',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_cv2.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SkyEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SkyEditor',
)

app = BUNDLE(
    coll,
    name='Sky Editor.app',
    icon=None,
    bundle_identifier='com.skyeditor.app',
    version='2.1.0',
    info_plist={
        'CFBundleName': 'Sky Editor',
        'CFBundleDisplayName': 'Sky Editor - 天体摄影图像处理工具',
        'CFBundleVersion': '2.1.0',
        'CFBundleShortVersionString': '2.1.0',
        'CFBundleIdentifier': 'com.skyeditor.app',
        'CFBundleExecutable': 'SkyEditor',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'SKYE',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Image Files',
                'CFBundleTypeRole': 'Editor',
                'CFBundleTypeExtensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'ico', 'arw', 'cr2', 'nef', 'dng', 'raw'],
                'CFBundleTypeIconFile': 'AppIcon',
                'CFBundleTypeMIMETypes': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'],
            }
        ],
    },
)