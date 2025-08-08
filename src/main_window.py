#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sky Editor - 图片批量预览器
支持多种图片格式的批量预览工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path
import math
import json
import time

# 尝试导入rawpy用于处理RAW格式
RAW_SUPPORT = False

def _check_raw_support():
    """检查RAW格式支持"""
    global RAW_SUPPORT
    if RAW_SUPPORT:
        return True
    
    try:
        import rawpy
        import numpy as np
        RAW_SUPPORT = True
        return True
    except ImportError:
        return False

# 导入星空堆叠功能
STACKING_SUPPORT = False
StackingWindow = None

def _import_stacking_module():
    """延迟导入星空堆叠模块"""
    global STACKING_SUPPORT, StackingWindow
    if STACKING_SUPPORT:
        return True
    
    try:
        from src.modules.stacking import StackingWindow as SW
        StackingWindow = SW
        STACKING_SUPPORT = True
        return True
    except ImportError:
        try:
            # 尝试相对导入作为备选
            from .modules.stacking import StackingWindow as SW
            StackingWindow = SW
            STACKING_SUPPORT = True
            return True
        except ImportError:
            return False

# 导入Camera Raw功能
CAMERA_RAW_SUPPORT = False
CameraRawWindow = None

def _import_camera_raw_module():
    """延迟导入Camera Raw模块"""
    global CAMERA_RAW_SUPPORT, CameraRawWindow
    if CAMERA_RAW_SUPPORT:
        return True
    
    try:
        from src.modules.camera_raw import CameraRawWindow as CRW
        CameraRawWindow = CRW
        CAMERA_RAW_SUPPORT = True
        return True
    except ImportError:
        try:
            # 尝试相对导入作为备选
            from .modules.camera_raw import CameraRawWindow as CRW
            CameraRawWindow = CRW
            CAMERA_RAW_SUPPORT = True
            return True
        except ImportError:
            return False

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sky Editor - 图片批量预览器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.expanduser("~"), ".sky_editor_config.json")
        
        # 支持的图片格式
        self.supported_formats = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.ico', '.ppm', '.pgm', '.pbm', '.pnm', '.arw'
        }
        
        # 加载配置
        self.config = self.load_config()
        
        # 存储图片信息
        self.images = []
        self.current_index = 0
        self.thumbnail_size = (150, 150)
        self.view_mode = 'grid'  # 'grid' 或 'list'
        
        # 预览缩放相关
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_step = 0.1
        self.original_image = None
        self.preview_canvas = None
        
        # 旋转相关
        self.rotation_angle = 0  # 旋转角度，0, 90, 180, 270
        
        # 拖拽相关
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        # 信息窗口显示状态
        self.show_info = False  # 默认关闭状态
        
        # 尝试延迟导入功能模块
        self._initialize_modules()
        
        self.setup_ui()
        self.setup_bindings()
    
    def _initialize_modules(self):
        """初始化功能模块"""
        # 尝试导入星空堆叠模块
        _import_stacking_module()
        # 尝试导入Camera Raw模块
        _import_camera_raw_module()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择文件...", command=self.select_files, accelerator="Ctrl+O")
        file_menu.add_command(label="选择文件夹...", command=self.select_folder, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="在文件夹中显示", command=self.show_in_folder, accelerator="Ctrl+Shift+R")
        file_menu.add_separator()
        file_menu.add_command(label="清空列表", command=self.clear_images, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        
        # 缩放子菜单
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="缩放", menu=zoom_menu)
        zoom_menu.add_command(label="放大", command=self.zoom_in, accelerator="Ctrl++")
        zoom_menu.add_command(label="缩小", command=self.zoom_out, accelerator="Ctrl+-")
        zoom_menu.add_command(label="适应窗口", command=self.zoom_fit, accelerator="Ctrl+9")
        zoom_menu.add_command(label="实际大小", command=self.zoom_actual, accelerator="Ctrl+0")
        
        # 旋转子菜单
        rotate_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="旋转", menu=rotate_menu)
        rotate_menu.add_command(label="向左旋转", command=self.rotate_left, accelerator="Ctrl+L")
        rotate_menu.add_command(label="向右旋转", command=self.rotate_right, accelerator="Ctrl+R")
        rotate_menu.add_command(label="重置旋转", command=self.reset_rotation, accelerator="Ctrl+T")
        
        view_menu.add_separator()
        
        # 视图模式子菜单
        viewmode_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="视图模式", menu=viewmode_menu)
        viewmode_menu.add_command(label="网格视图", command=lambda: self.set_view_mode('grid'))
        viewmode_menu.add_command(label="列表视图", command=lambda: self.set_view_mode('list'))
        
        view_menu.add_separator()
        view_menu.add_command(label="全屏预览", command=self.fullscreen_preview, accelerator="F11")
        view_menu.add_command(label="显示/隐藏信息面板", command=self.toggle_info_panel, accelerator="Ctrl+I")
        
        # 导航菜单
        nav_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="导航", menu=nav_menu)
        nav_menu.add_command(label="上一张", command=self.previous_image, accelerator="Page Up")
        nav_menu.add_command(label="下一张", command=self.next_image, accelerator="Page Down")
        nav_menu.add_separator()
        nav_menu.add_command(label="第一张", command=self.first_image, accelerator="Home")
        nav_menu.add_command(label="最后一张", command=self.last_image, accelerator="End")
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        
        # 缩略图大小子菜单
        thumbnail_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="缩略图大小", menu=thumbnail_menu)
        thumbnail_menu.add_command(label="小 (100px)", command=lambda: self.set_thumbnail_size(100))
        thumbnail_menu.add_command(label="中 (150px)", command=lambda: self.set_thumbnail_size(150))
        thumbnail_menu.add_command(label="大 (200px)", command=lambda: self.set_thumbnail_size(200))
        thumbnail_menu.add_command(label="特大 (250px)", command=lambda: self.set_thumbnail_size(250))
        
        tools_menu.add_separator()
        tools_menu.add_command(label="Camera Raw", command=self.open_camera_raw)
        tools_menu.add_command(label="星空图像堆叠", command=self.open_stacking_tool)
        tools_menu.add_separator()
        tools_menu.add_command(label="刷新", command=self.refresh_display, accelerator="F5")
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="快捷键", command=self.show_shortcuts)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建菜单栏
        self.create_menu()
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 文件操作按钮
        ttk.Button(toolbar, text="选择文件", command=self.select_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="选择文件夹", command=self.select_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="清空列表", command=self.clear_images).pack(side=tk.LEFT, padx=(0, 20))
        
        # 缩放控制
        ttk.Label(toolbar, text="缩放:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="-", width=3, command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 2))
        
        self.zoom_label = ttk.Label(toolbar, text="100%", width=6, anchor=tk.CENTER)
        self.zoom_label.pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(toolbar, text="+", width=3, command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="适应", command=self.zoom_fit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="1:1", command=self.zoom_actual).pack(side=tk.LEFT, padx=(0, 20))
        
        # 旋转控制
        ttk.Label(toolbar, text="旋转:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="↶", width=3, command=self.rotate_left).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="↷", width=3, command=self.rotate_right).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="重置", command=self.reset_rotation).pack(side=tk.LEFT, padx=(0, 20))
        
        # 信息窗口控制
        self.info_button = ttk.Button(toolbar, text="显示信息", command=self.toggle_info_panel)
        self.info_button.pack(side=tk.LEFT)
        
        # 主内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：图片列表/网格 (缩小宽度)
        left_frame = ttk.Frame(content_frame, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 图片计数标签
        self.count_label = ttk.Label(left_frame, text="已加载 0 张图片", font=('Arial', 10))
        self.count_label.pack(fill=tk.X, pady=(0, 10))
        
        # 左侧底部：视图模式控制 - 先创建底部控件
        left_bottom_frame = ttk.Frame(left_frame)
        left_bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # 视图模式按钮
        ttk.Label(left_bottom_frame, text="视图模式:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_bottom_frame, text="网格视图", command=lambda: self.set_view_mode('grid')).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_bottom_frame, text="列表视图", command=lambda: self.set_view_mode('list')).pack(side=tk.LEFT)
        
        # 缩略图大小控制
        size_frame = ttk.Frame(left_frame)
        size_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        ttk.Label(size_frame, text="缩略图大小:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value="150")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, values=["100", "150", "200", "250"], width=8)
        size_combo.pack(side=tk.LEFT, padx=(0, 5))
        size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        
        # 创建滚动区域 - 在底部控件之后创建
        self.canvas = tk.Canvas(left_frame, bg='white')
        scrollbar_v = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_h = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 移除自动配置滚动区域的绑定，改为手动控制
        # self.scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 设置Canvas可以获得焦点，确保滚轮事件能正确处理
        self.canvas.configure(highlightthickness=0)
        self.canvas.focus_set()
        
        # 正确的布局顺序：先放置滚动条，再放置Canvas
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧：预览区域 (扩大宽度)
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 预览控制工具栏（现在为空，可以移除或保留用于未来扩展）
        
        # 预览图片容器
        preview_container = ttk.Frame(right_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        # 创建带滚动条的Canvas用于显示可缩放的图片
        self.preview_canvas = tk.Canvas(preview_container, bg='white', highlightthickness=0)
        preview_v_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        preview_h_scrollbar = ttk.Scrollbar(preview_container, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=preview_v_scrollbar.set, xscrollcommand=preview_h_scrollbar.set)
        
        # 正确的布局顺序：先放置水平滚动条，再放置垂直滚动条，最后放置Canvas
        preview_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        preview_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 初始化Canvas图片ID
        self.canvas_image_id = None
        
        # 显示初始提示文本
        self.preview_canvas.create_text(
            200, 150, text="选择图片进行预览", 
            font=('Arial', 14), fill='gray', tags='placeholder'
        )
        
        # 图片信息 - 默认隐藏
        self.info_frame = ttk.Frame(right_frame)
        # 不立即pack，等待用户点击显示
        
        self.info_text = tk.Text(self.info_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        info_scrollbar = ttk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 预览控制按钮
        self.preview_controls = ttk.Frame(right_frame)
        self.preview_controls.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        ttk.Button(self.preview_controls, text="上一张", command=self.previous_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.preview_controls, text="下一张", command=self.next_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.preview_controls, text="全屏预览", command=self.fullscreen_preview).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(self.preview_controls, text="在文件夹中显示", command=self.show_in_folder).pack(side=tk.LEFT)
        
    def setup_bindings(self):
        """设置键盘绑定"""
        # 图片切换快捷键 - 改为Page键
        self.root.bind('<Prior>', lambda e: self.previous_image())  # Page Up - 上一张
        self.root.bind('<Next>', lambda e: self.next_image())       # Page Down - 下一张
        self.root.bind('<Delete>', lambda e: self.remove_current_image())
        self.root.bind('<F11>', lambda e: self.fullscreen_preview())
        
        # 预览区域滚动快捷键 - 方向键
        self.root.bind('<Up>', lambda e: self.scroll_preview('up'))
        self.root.bind('<Down>', lambda e: self.scroll_preview('down'))
        self.root.bind('<Left>', lambda e: self.scroll_preview('left'))
        self.root.bind('<Right>', lambda e: self.scroll_preview('right'))
        
        # 缩放快捷键
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # 兼容不同键盘
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_actual())
        self.root.bind('<Control-9>', lambda e: self.zoom_fit())
        
        # 旋转快捷键
        self.root.bind('<Control-l>', lambda e: self.rotate_left())   # Ctrl+L 向左旋转
        self.root.bind('<Control-r>', lambda e: self.rotate_right())  # Ctrl+R 向右旋转
        self.root.bind('<Control-t>', lambda e: self.reset_rotation()) # Ctrl+T 重置旋转
        
        # 文件操作快捷键
        self.root.bind('<Control-o>', lambda e: self.select_files())  # Ctrl+O 选择文件
        self.root.bind('<Control-Shift-O>', lambda e: self.select_folder())  # Ctrl+Shift+O 选择文件夹
        self.root.bind('<Control-n>', lambda e: self.clear_images())  # Ctrl+N 清空列表
        self.root.bind('<Control-Shift-R>', lambda e: self.show_in_folder())  # Ctrl+Shift+R 在文件夹中显示
        self.root.bind('<Control-q>', lambda e: self.root.quit())  # Ctrl+Q 退出
        
        # 导航快捷键
        self.root.bind('<Home>', lambda e: self.first_image())  # Home 第一张
        self.root.bind('<End>', lambda e: self.last_image())    # End 最后一张
        
        # 其他快捷键
        self.root.bind('<Control-i>', lambda e: self.toggle_info_panel())  # Ctrl+I 信息面板
        self.root.bind('<F5>', lambda e: self.refresh_display())  # F5 刷新
        
        # 鼠标滚轮绑定 - 绑定到多个控件确保滚动功能正常
        # 为主要控件绑定多种滚轮事件以确保跨平台兼容性
        for widget in [self.canvas, self.scrollable_frame]:
            widget.bind("<MouseWheel>", self.on_mousewheel)  # Windows和macOS
            widget.bind("<Button-4>", self.on_mousewheel)    # Linux向上滚动
            widget.bind("<Button-5>", self.on_mousewheel)    # Linux向下滚动
        
        # 绑定滚轮事件到所有子控件
        self.bind_mousewheel_to_children(self.scrollable_frame)
        
        # 绑定鼠标进入事件，确保焦点正确
        self.canvas.bind("<Enter>", self.on_left_canvas_enter)
        self.scrollable_frame.bind("<Enter>", self.on_left_canvas_enter)
        
        # 预览区域的鼠标滚轮事件 - 统一处理所有滚轮事件
        self.preview_canvas.bind("<MouseWheel>", self.on_preview_mousewheel)
        
        # Linux系统的滚轮事件
        self.preview_canvas.bind("<Button-4>", self.on_preview_mousewheel)  # 向上滚动
        self.preview_canvas.bind("<Button-5>", self.on_preview_mousewheel)  # 向下滚动
        
        # macOS和Windows的水平滚轮事件
        self.preview_canvas.bind("<Shift-MouseWheel>", self.on_preview_mousewheel)
        
        # 确保预览Canvas可以获得焦点以接收事件
        self.preview_canvas.configure(takefocus=True)
        
        # 预览区域的鼠标拖拽 - 支持左键和中键拖拽
        self.preview_canvas.bind("<Button-1>", self.on_drag_start)
        self.preview_canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        
        # 中键拖拽支持
        self.preview_canvas.bind("<Button-2>", self.on_drag_start)  # 中键按下
        self.preview_canvas.bind("<B2-Motion>", self.on_drag_motion)  # 中键拖拽
        self.preview_canvas.bind("<ButtonRelease-2>", self.on_drag_end)  # 中键释放
        
        # 改变鼠标光标
        self.preview_canvas.bind("<Enter>", self.on_canvas_enter)
        self.preview_canvas.bind("<Leave>", self.on_canvas_leave)
        
    def on_left_canvas_enter(self, event):
        """鼠标进入左侧Canvas区域时设置焦点"""
        self.canvas.focus_set()
    
    def bind_mousewheel_to_children(self, parent):
        """递归绑定鼠标滚轮事件到所有子控件"""
        for child in parent.winfo_children():
            # 绑定多种滚轮事件以确保跨平台兼容性
            child.bind("<MouseWheel>", self.on_mousewheel)  # Windows和macOS
            child.bind("<Button-4>", self.on_mousewheel)    # Linux向上滚动
            child.bind("<Button-5>", self.on_mousewheel)    # Linux向下滚动
            # 也绑定鼠标进入事件
            child.bind("<Enter>", self.on_left_canvas_enter)
            # 递归绑定子控件的子控件
            if hasattr(child, 'winfo_children'):
                self.bind_mousewheel_to_children(child)
    
    def on_mousewheel(self, event):
        """处理鼠标滚轮事件 - 改进的跨平台兼容性"""
        # 检查是否真的需要滚动
        if not self.can_scroll():
            return
        
        # 检测操作系统和事件类型
        if event.num == 4 or event.delta > 0:
            # 向上滚动
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            # 向下滚动
            self.canvas.yview_scroll(1, "units")
        else:
            # 使用delta值进行滚动（主要用于Windows和macOS）
            try:
                delta = event.delta
                if delta != 0:
                    # macOS和Windows的delta值处理
                    if abs(delta) >= 120:
                        # Windows风格
                        scroll_amount = int(-1 * (delta / 120))
                    else:
                        # macOS风格
                        scroll_amount = int(-1 * delta)
                    self.canvas.yview_scroll(scroll_amount, "units")
            except AttributeError:
                # 如果没有delta属性，使用默认滚动
                self.canvas.yview_scroll(-1, "units")
        
    def on_preview_mousewheel(self, event):
        """处理预览区域鼠标滚轮事件"""
        if not self.original_image:
            return
            
        # 检查修饰键
        ctrl_pressed = event.state & 0x4   # Ctrl键
        shift_pressed = event.state & 0x1  # Shift键
        
        # 如果按住Ctrl键，进行缩放
        if ctrl_pressed:
            # 处理缩放
            if hasattr(event, 'num'):
                if event.num == 4:  # 向上滚动 - 放大
                    self.zoom_in()
                elif event.num == 5:  # 向下滚动 - 缩小
                    self.zoom_out()
            else:
                # Windows和macOS的滚轮事件
                try:
                    if event.delta > 0:
                        self.zoom_in()
                    elif event.delta < 0:
                        self.zoom_out()
                except AttributeError:
                    pass
            return
        
        # 确定滚动方向和量
        scroll_amount = 0
        is_horizontal = False
        
        # 处理Linux系统的滚轮事件
        if hasattr(event, 'num'):
            if event.num == 4:  # 向上滚动
                scroll_amount = -1
                is_horizontal = False
            elif event.num == 5:  # 向下滚动
                scroll_amount = 1
                is_horizontal = False
        else:
            # 处理Windows和macOS的滚轮事件
            try:
                delta = event.delta
                if delta != 0:
                    # 检查是否是水平滚动（Shift+滚轮）
                    if shift_pressed:
                        is_horizontal = True
                    else:
                        is_horizontal = False
                    
                    # 简化delta值处理
                    if delta > 0:
                        scroll_amount = -1
                    else:
                        scroll_amount = 1
            except AttributeError:
                # 如果没有delta属性，使用默认滚动
                scroll_amount = -1
                is_horizontal = False
        
        # 执行滚动
        if scroll_amount != 0:
            if is_horizontal:
                # 水平滚动
                self.preview_canvas.xview_scroll(scroll_amount, "units")
            else:
                # 垂直滚动
                self.preview_canvas.yview_scroll(scroll_amount, "units")
        
    def on_drag_start(self, event):
        """开始拖拽"""
        # 设置焦点以确保滚轮事件能正常工作
        self.preview_canvas.focus_set()
        
        if self.original_image:
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = True
            self.preview_canvas.configure(cursor="fleur")  # 改变光标为移动光标
            # 开始scan操作
            self.preview_canvas.scan_mark(event.x, event.y)
        
    def on_drag_motion(self, event):
        """拖拽移动"""
        if self.is_dragging and self.original_image:
            # 使用scan_dragto进行拖拽
            self.preview_canvas.scan_dragto(event.x, event.y, gain=1)
            
    def on_drag_end(self, event):
        """结束拖拽"""
        self.is_dragging = False
        self.update_canvas_cursor()
        
    def on_canvas_enter(self, event):
        """鼠标进入Canvas"""
        self.update_canvas_cursor()
        
    def on_canvas_leave(self, event):
        """鼠标离开Canvas"""
        self.preview_canvas.configure(cursor="")
        
    def update_canvas_cursor(self):
        """更新Canvas光标"""
        if self.original_image:
            # 如果有图片，显示手型光标表示可以拖拽
            self.preview_canvas.configure(cursor="hand2")
        else:
            # 否则显示默认光标
            self.preview_canvas.configure(cursor="")
        
    def select_files(self):
        """选择图片文件"""
        # 取消之前的加载
        self.cancel_loading()
        
        # macOS和其他系统的文件类型格式不同
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            filetypes = [
                ("所有支持的图片", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tif *.webp *.ico *.ppm *.pgm *.pbm *.pnm *.arw"),
                ("JPEG图片", "*.jpg *.jpeg"),
                ("PNG图片", "*.png"),
                ("GIF图片", "*.gif"),
                ("BMP图片", "*.bmp"),
                ("TIFF图片", "*.tiff *.tif"),
                ("WebP图片", "*.webp"),
                ("RAW图片", "*.arw"),
                ("所有文件", "*.*")
            ]
        else:  # Windows和Linux
            filetypes = [
                ("所有支持的图片", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.tif;*.webp;*.ico;*.ppm;*.pgm;*.pbm;*.pnm;*.arw"),
                ("JPEG图片", "*.jpg;*.jpeg"),
                ("PNG图片", "*.png"),
                ("GIF图片", "*.gif"),
                ("BMP图片", "*.bmp"),
                ("TIFF图片", "*.tiff;*.tif"),
                ("WebP图片", "*.webp"),
                ("RAW图片", "*.arw"),
                ("所有文件", "*.*")
            ]
        
        # 使用上次打开的文件目录
        initial_dir = self.config.get("last_file_directory", os.path.expanduser("~"))
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if files:
            # 更新最后使用的文件目录
            self.update_last_directory("last_file_directory", files[0])
            self.load_images(files)
            
    def select_folder(self):
        """选择文件夹"""
        # 取消之前的加载
        self.cancel_loading()
        
        # 使用上次打开的文件夹目录
        initial_dir = self.config.get("last_folder_directory", os.path.expanduser("~"))
        
        folder = filedialog.askdirectory(
            title="选择包含图片的文件夹",
            initialdir=initial_dir
        )
        
        if folder:
            # 更新最后使用的文件夹目录
            self.update_last_directory("last_folder_directory", folder)
            
            # 递归查找所有图片文件
            image_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if Path(file).suffix.lower() in self.supported_formats:
                        image_files.append(os.path.join(root, file))
            
            if image_files:
                self.load_images(image_files)
            else:
                messagebox.showinfo("提示", "在选择的文件夹中没有找到支持的图片文件")
    
    def load_raw_image(self, file_path):
        """加载RAW格式图片（ARW等）"""
        if not RAW_SUPPORT:
            raise Exception("未安装rawpy库，无法处理RAW格式")
        
        try:
            with rawpy.imread(file_path) as raw:
                # 使用默认参数处理RAW图片
                rgb = raw.postprocess(
                    use_camera_wb=True,  # 使用相机白平衡
                    half_size=False,     # 不使用半尺寸
                    no_auto_bright=True, # 不自动调整亮度
                    output_bps=8         # 8位输出
                )
                
                # 转换为PIL Image
                image = Image.fromarray(rgb)
                return image
                
        except Exception as e:
            raise Exception(f"处理RAW文件失败: {e}")
    
    def load_raw_thumbnail_fast(self, file_path, thumbnail_size=(150, 150)):
        """快速加载RAW文件的缩略图（优化版本）"""
        if not RAW_SUPPORT:
            raise Exception("未安装rawpy库，无法处理RAW格式")
        
        try:
            with rawpy.imread(file_path) as raw:
                # 尝试提取嵌入的缩略图
                try:
                    # 首先尝试提取JPEG缩略图（最快）
                    thumb = raw.extract_thumb()
                    if thumb.format == rawpy.ThumbFormat.JPEG:
                        # 直接从JPEG数据创建PIL图像
                        from io import BytesIO
                        thumb_image = Image.open(BytesIO(thumb.data))
                        # 调整到目标尺寸
                        thumb_image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                        return thumb_image, raw.sizes.raw_width, raw.sizes.raw_height
                except:
                    # 如果提取缩略图失败，继续使用半尺寸处理
                    pass
                
                # 如果没有嵌入缩略图，使用半尺寸快速处理
                rgb = raw.postprocess(
                    use_camera_wb=True,   # 使用相机白平衡
                    half_size=True,       # 使用半尺寸（4倍速度提升）
                    no_auto_bright=True,  # 不自动调整亮度
                    output_bps=8,         # 8位输出
                    user_qual=0           # 最快质量设置
                )
                
                # 转换为PIL Image并创建缩略图
                image = Image.fromarray(rgb)
                original_size = (raw.sizes.raw_width, raw.sizes.raw_height)
                
                # 创建缩略图
                image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                return image, original_size[0], original_size[1]
                
        except Exception as e:
            raise Exception(f"快速处理RAW缩略图失败: {e}")
                
    def load_images(self, file_paths):
        """快速加载图片列表，异步加载缩略图"""
        # 清空现有图片
        self.clear_images()
        
        # 第一步：快速创建图片信息列表（不加载缩略图）
        for file_path in file_paths:
            try:
                if Path(file_path).suffix.lower() in self.supported_formats:
                    # 快速获取基本信息
                    file_size = os.path.getsize(file_path)
                    file_name = os.path.basename(file_path)
                    
                    # 创建占位符图片信息
                    image_info = {
                        'path': file_path,
                        'name': file_name,
                        'size': file_size,
                        'dimensions': None,  # 稍后异步加载
                        'format': None,      # 稍后异步加载
                        'mode': None,        # 稍后异步加载
                        'thumbnail': None,   # 稍后异步加载
                        'loading': True      # 标记为正在加载
                    }
                    
                    self.images.append(image_info)
                    
            except Exception as e:
                print(f"获取文件信息失败 {file_path}: {e}")
        
        # 立即更新显示（显示占位符）
        self.update_display()
        self.update_count_label()
        
        if self.images:
            self.current_index = 0
            # 立即显示第一张图片的预览（即使缩略图还没加载）
            self.show_preview(0)
        
        # 第二步：异步加载缩略图（简化版本）
        self.start_simple_async_loading()
        
    def start_simple_async_loading(self):
        """基于队列的异步加载方法"""
        self.loading_cancelled = False
        self.queue_size = 20  # 队列大小
        self.active_workers = 0  # 当前活跃的工作线程数
        self.completed_count = 0  # 已完成的加载数量
        
        # 创建按文件大小排序的加载队列（从小到大）
        self.loading_queue = self.create_sorted_loading_queue()
        self.queue_index = 0  # 当前队列索引
        
        print(f"开始队列加载，共 {len(self.loading_queue)} 张图片，队列大小: {self.queue_size}")
        
        # 更新计数标签显示初始进度
        self.update_count_label()
        
        # 启动初始队列
        self.start_initial_queue()
    
    def create_sorted_loading_queue(self):
        """创建按文件大小排序的加载队列"""
        # 创建包含索引和文件大小的列表
        queue_items = []
        for i, image_info in enumerate(self.images):
            queue_items.append({
                'index': i,
                'size': image_info.get('size', 0),
                'path': image_info.get('path', ''),
                'loaded': False
            })
        
        # 按文件大小从小到大排序
        queue_items.sort(key=lambda x: x['size'])
        
        print(f"队列排序完成，最小文件: {queue_items[0]['size']} bytes, 最大文件: {queue_items[-1]['size']} bytes")
        return queue_items
    
    def start_initial_queue(self):
        """启动初始队列"""
        initial_count = min(self.queue_size, len(self.loading_queue))
        
        for i in range(initial_count):
            if not self.loading_cancelled:
                self.start_single_worker(i)
    
    def start_single_worker(self, queue_pos):
        """启动单个工作线程"""
        if (self.loading_cancelled or 
            queue_pos >= len(self.loading_queue) or 
            self.loading_queue[queue_pos]['loaded']):
            return
            
        self.active_workers += 1
        queue_item = self.loading_queue[queue_pos]
        
        def worker():
            try:
                index = queue_item['index']
                image_info = self.images[index]
                
                # 加载缩略图
                self.load_single_thumbnail(index, image_info)
                queue_item['loaded'] = True
                
                # 在主线程中更新UI和启动下一个任务
                self.root.after(0, lambda: self.on_worker_completed(queue_pos, True))
                
            except Exception as e:
                print(f"队列加载失败 {queue_item['path']}: {e}")
                queue_item['loaded'] = True  # 标记为已处理（即使失败）
                self.root.after(0, lambda: self.on_worker_completed(queue_pos, False))
        
        # 在后台线程中执行
        threading.Thread(target=worker, daemon=True).start()
    
    def on_worker_completed(self, completed_queue_pos, success):
        """工作线程完成回调"""
        if self.loading_cancelled:
            return
            
        self.active_workers -= 1
        self.completed_count += 1
        
        # 启动下一个任务
        self.start_next_worker()
        
        # 增量更新单个缩略图UI（不重建整个界面）
        self.root.after(0, lambda: self.update_single_thumbnail(completed_queue_pos))
        
        # 更新计数标签显示进度
        self.root.after(0, self.update_count_label)
        
        # 打印进度
        progress = (self.completed_count / len(self.loading_queue)) * 100
        print(f"加载进度: {self.completed_count}/{len(self.loading_queue)} ({progress:.1f}%)")
    
    def start_next_worker(self):
        """启动下一个工作线程"""
        if self.loading_cancelled:
            return
            
        # 找到下一个未加载的任务
        while self.queue_index < len(self.loading_queue):
            if not self.loading_queue[self.queue_index]['loaded']:
                self.start_single_worker(self.queue_index)
                self.queue_index += 1
                break
            self.queue_index += 1
    
        
    def update_single_thumbnail(self, queue_pos):
        """增量更新单个缩略图UI"""
        if self.loading_cancelled or queue_pos >= len(self.loading_queue):
            return
            
        queue_item = self.loading_queue[queue_pos]
        image_index = queue_item['index']
        
        if image_index >= len(self.images):
            return
            
        image_info = self.images[image_index]
        
        # 查找对应的UI控件并更新
        if hasattr(self, 'thumbnail_widgets') and image_index in self.thumbnail_widgets:
            widget_info = self.thumbnail_widgets[image_index]
            
            # 检查控件是否仍然存在
            try:
                frame = widget_info['frame']
                if not frame.winfo_exists():
                    # 控件已被销毁，从字典中移除
                    del self.thumbnail_widgets[image_index]
                    return
            except tk.TclError:
                # 控件已被销毁
                del self.thumbnail_widgets[image_index]
                return
            
            try:
                if self.view_mode == 'grid':
                    self.update_grid_thumbnail(widget_info, image_info, image_index)
                else:
                    self.update_list_thumbnail(widget_info, image_info, image_index)
            except tk.TclError as e:
                # Tkinter控件错误，通常是控件已被销毁
                print(f"控件已销毁，跳过更新 {image_index}: {e}")
                if image_index in self.thumbnail_widgets:
                    del self.thumbnail_widgets[image_index]
            except Exception as e:
                print(f"更新缩略图UI失败 {image_index}: {e}")
        else:
            # 如果thumbnail_widgets中没有对应的索引，说明可能视图已切换或控件尚未创建
            # 这种情况下，缩略图已经加载完成，但UI控件不存在
            print(f"缩略图已加载但UI控件不存在，索引 {image_index}: {image_info['name']}")
            
            # 不立即重建视图，因为这可能导致频繁的UI重建
            # 缩略图数据已经保存在image_info中，下次显示视图时会自动使用
    
    def update_grid_thumbnail(self, widget_info, image_info, image_index):
        """更新网格视图中的单个缩略图"""
        frame = widget_info['frame']
        
        try:
            if not frame.winfo_exists():
                return
        except tk.TclError:
            return
            
        # 查找并移除旧的缩略图控件（包括占位符）
        thumbnail_widget = None
        try:
            children = list(frame.winfo_children())
            
            for child in children:
                try:
                    # 查找缩略图控件：可能是Label（图片）或tk.Label（占位符）
                    if (hasattr(child, 'image') or  # ttk.Label with image
                        (hasattr(child, 'cget') and 
                         hasattr(child, 'winfo_class') and 
                         child.winfo_class() == 'Label')):  # tk.Label placeholder
                        thumbnail_widget = child
                        break
                except tk.TclError:
                    # 子控件已被销毁，跳过
                    continue
            
            # 移除旧的缩略图控件
            if thumbnail_widget:
                try:
                    thumbnail_widget.destroy()
                except tk.TclError:
                    pass
        except tk.TclError:
            # frame已被销毁
            return
        
        # 创建新的缩略图控件
        try:
            if image_info.get('thumbnail') is not None:
                try:
                    photo = ImageTk.PhotoImage(image_info['thumbnail'])
                    label = ttk.Label(frame, image=photo)
                    label.image = photo  # 保持引用
                    
                    # 获取当前的子控件列表，插入到第一个位置
                    current_children = frame.winfo_children()
                    if current_children:
                        label.pack(padx=5, pady=5, before=current_children[0])
                    else:
                        label.pack(padx=5, pady=5)
                    
                    label.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                    print(f"成功替换网格缩略图: {image_info['name']}")
                except tk.TclError:
                    # frame已被销毁，无法创建新控件
                    pass
                except Exception as e:
                    print(f"创建网格缩略图失败 {image_index}: {e}")
                    try:
                        error_label = tk.Label(frame, text="[错误]", width=10, height=6, 
                                             relief=tk.SUNKEN, background='lightgray')
                        current_children = frame.winfo_children()
                        if current_children:
                            error_label.pack(padx=5, pady=5, before=current_children[0])
                        else:
                            error_label.pack(padx=5, pady=5)
                        error_label.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                    except tk.TclError:
                        pass
            elif image_info.get('load_error', False):
                try:
                    error_label = tk.Label(frame, text="[加载失败]", width=10, height=6, 
                                         relief=tk.SUNKEN, background='lightcoral')
                    current_children = frame.winfo_children()
                    if current_children:
                        error_label.pack(padx=5, pady=5, before=current_children[0])
                    else:
                        error_label.pack(padx=5, pady=5)
                    error_label.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                except tk.TclError:
                    pass
        except tk.TclError:
            # frame已被销毁
            pass
    
    def update_list_thumbnail(self, widget_info, image_info, image_index):
        """更新列表视图中的单个缩略图"""
        frame = widget_info['frame']
        
        try:
            if not frame.winfo_exists():
                return
        except tk.TclError:
            return
            
        # 查找并移除旧的缩略图控件（包括占位符）
        thumbnail_widget = None
        
        try:
            for child in frame.winfo_children():
                try:
                    # 查找缩略图控件：可能是ttk.Label（图片）或tk.Label（占位符）
                    if (hasattr(child, 'image') or  # ttk.Label with image
                        (hasattr(child, 'cget') and 
                         hasattr(child, 'winfo_class') and 
                         child.winfo_class() == 'Label')):  # tk.Label placeholder
                        thumbnail_widget = child
                        break
                except tk.TclError:
                    # 子控件已被销毁，跳过
                    continue
            
            # 移除旧的缩略图控件
            if thumbnail_widget:
                try:
                    thumbnail_widget.destroy()
                except tk.TclError:
                    pass
        except tk.TclError:
            # frame已被销毁
            return
        
        # 创建新的缩略图控件
        try:
            if image_info.get('thumbnail') is not None:
                try:
                    small_thumbnail = image_info['thumbnail'].copy()
                    small_thumbnail.thumbnail((50, 50), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(small_thumbnail)
                    
                    img_label = ttk.Label(frame, image=photo)
                    img_label.image = photo
                    img_label.pack(side=tk.LEFT, padx=(5, 10))
                    img_label.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                    print(f"成功替换列表缩略图: {image_info['name']}")
                except tk.TclError:
                    # frame已被销毁，无法创建新控件
                    pass
                except Exception as e:
                    print(f"创建列表缩略图失败 {image_index}: {e}")
                    try:
                        placeholder = tk.Label(frame, text="[错误]", width=8, background='lightgray')
                        placeholder.pack(side=tk.LEFT, padx=(5, 10))
                        placeholder.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                    except tk.TclError:
                        pass
            elif image_info.get('load_error', False):
                try:
                    placeholder = tk.Label(frame, text="[失败]", width=8, background='lightcoral')
                    placeholder.pack(side=tk.LEFT, padx=(5, 10))
                    placeholder.bind("<Button-1>", lambda e, idx=image_index: self.show_preview(idx))
                except tk.TclError:
                    pass
        except tk.TclError:
            # frame已被销毁
            pass
    
    def cancel_loading(self):
        """取消异步加载"""
        self.loading_cancelled = True
        self.active_workers = 0
        self.completed_count = 0
        self.queue_index = 0
        print("已取消缩略图加载")
    
    def load_single_thumbnail(self, index, image_info):
        """加载单个图片的缩略图"""
        try:
            file_path = image_info['path']
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.arw':
                # 处理ARW格式 - 使用优化的快速方法
                if not RAW_SUPPORT:
                    print(f"跳过ARW文件 {file_path}: 未安装rawpy库")
                    return
                
                print(f"开始快速加载ARW缩略图: {image_info['name']}")
                start_time = time.time()
                
                # 使用快速缩略图提取方法
                thumbnail, width, height = self.load_raw_thumbnail_fast(file_path, self.thumbnail_size)
                
                load_time = time.time() - start_time
                print(f"ARW缩略图加载完成: {image_info['name']} ({load_time:.2f}秒)")
                
                # 更新图片信息
                self.images[index].update({
                    'dimensions': (width, height),
                    'format': 'ARW',
                    'mode': thumbnail.mode,
                    'thumbnail': thumbnail,
                    'loading': False
                })
            else:
                # 处理常规格式
                with Image.open(file_path) as img:
                    # 创建缩略图
                    thumbnail = img.copy()
                    thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    
                    # 更新图片信息
                    self.images[index].update({
                        'dimensions': img.size,
                        'format': img.format,
                        'mode': img.mode,
                        'thumbnail': thumbnail,
                        'loading': False
                    })
                    
        except Exception as e:
            print(f"加载缩略图失败 {file_path}: {e}")
            # 标记加载失败
            self.images[index].update({
                'loading': False,
                'load_error': True
            })
    

        
    def clear_images(self):
        """清空图片列表"""
        # 取消当前的异步加载
        self.cancel_loading()
        
        self.images.clear()
        self.current_index = 0
        self.update_display()
        self.update_count_label()
        self.clear_preview()
        
    def update_display(self):
        """更新图片显示"""
        # 清空现有显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # 清理控件引用
        if hasattr(self, 'thumbnail_widgets'):
            self.thumbnail_widgets.clear()
            
        # 立即重置滚动区域为最小值
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        
        # 重置滚动位置到顶部
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)
            
        if not self.images:
            ttk.Label(self.scrollable_frame, text="没有加载图片\n点击'选择文件'或'选择文件夹'来加载图片").pack(pady=50)
            # 更新滚动区域
            self.canvas.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            return
            
        if self.view_mode == 'grid':
            self.display_grid_view()
        else:
            self.display_list_view()
            
        # 强制更新布局
        self.canvas.update_idletasks()
        
        # 手动计算并设置滚动区域
        self.update_scroll_region()
        
        # 如果不需要滚动，确保滚动位置在顶部
        if not self.can_scroll():
            self.canvas.yview_moveto(0)
            self.canvas.xview_moveto(0)
        
        # 重新绑定滚轮事件到新创建的控件
        self.bind_mousewheel_to_children(self.scrollable_frame)
            
    def display_grid_view(self):
        """网格视图显示"""
        # 初始化控件引用字典
        self.thumbnail_widgets = {}
        
        # 计算每行显示的图片数量
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 280  # 调整默认宽度适应新的左侧宽度
            
        cols = max(1, canvas_width // (self.thumbnail_size[0] + 20))
        
        for i, image_info in enumerate(self.images):
            row = i // cols
            col = i % cols
            
            # 创建图片框架
            frame = ttk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # 存储控件引用
            self.thumbnail_widgets[i] = {'frame': frame, 'type': 'grid'}
            
            # 显示缩略图或占位符
            if image_info.get('thumbnail') is not None:
                # 显示实际缩略图
                try:
                    photo = ImageTk.PhotoImage(image_info['thumbnail'])
                    label = ttk.Label(frame, image=photo)
                    label.image = photo  # 保持引用
                    label.pack(padx=5, pady=5)
                    
                    # 绑定点击事件
                    label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
                    
                except Exception as e:
                    # 缩略图显示失败，显示错误占位符
                    error_label = tk.Label(frame, text="[错误]", width=10, height=6, 
                                         relief=tk.SUNKEN, background='lightgray')
                    error_label.pack(padx=5, pady=5)
                    error_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            elif image_info.get('load_error', False):
                # 加载失败的占位符
                error_label = tk.Label(frame, text="[加载失败]", width=10, height=6, 
                                     relief=tk.SUNKEN, background='lightcoral')
                error_label.pack(padx=5, pady=5)
                error_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            else:
                # 正在加载的占位符
                loading_label = tk.Label(frame, text="[加载中...]", width=10, height=6, 
                                       relief=tk.SUNKEN, background='lightblue')
                loading_label.pack(padx=5, pady=5)
                loading_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            
            # 显示文件名
            name_label = ttk.Label(frame, text=image_info['name'], wraplength=self.thumbnail_size[0])
            name_label.pack(padx=5, pady=(0, 5))
            name_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            
            # 显示文件信息（如果已加载）
            if image_info.get('dimensions'):
                info_text = f"{image_info['dimensions'][0]}×{image_info['dimensions'][1]}"
                info_label = ttk.Label(frame, text=info_text, font=('Arial', 8))
                info_label.pack(padx=5, pady=(0, 5))
                info_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
        
        # 更新滚动区域
        self.root.after_idle(self.update_scroll_region)
                
    def display_list_view(self):
        """列表视图显示"""
        # 初始化控件引用字典
        self.thumbnail_widgets = {}
        
        for i, image_info in enumerate(self.images):
            # 创建行框架
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 存储控件引用
            self.thumbnail_widgets[i] = {'frame': frame, 'type': 'list'}
            
            # 小缩略图
            if image_info.get('thumbnail') is not None:
                try:
                    small_thumbnail = image_info['thumbnail'].copy()
                    small_thumbnail.thumbnail((50, 50), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(small_thumbnail)
                    
                    img_label = ttk.Label(frame, image=photo)
                    img_label.image = photo
                    img_label.pack(side=tk.LEFT, padx=(5, 10))
                    img_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
                    
                except Exception:
                    # 缩略图显示失败
                    placeholder = tk.Label(frame, text="[错误]", width=8, background='lightgray')
                    placeholder.pack(side=tk.LEFT, padx=(5, 10))
                    placeholder.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            elif image_info.get('load_error', False):
                # 加载失败的占位符
                placeholder = tk.Label(frame, text="[失败]", width=8, background='lightcoral')
                placeholder.pack(side=tk.LEFT, padx=(5, 10))
                placeholder.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            else:
                # 正在加载的占位符
                placeholder = tk.Label(frame, text="[加载中]", width=8, background='lightblue')
                placeholder.pack(side=tk.LEFT, padx=(5, 10))
                placeholder.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
                
            # 文件信息
            info_frame = ttk.Frame(frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            name_label = ttk.Label(info_frame, text=image_info['name'], font=('Arial', 10, 'bold'))
            name_label.pack(anchor=tk.W)
            name_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            
            # 显示尺寸信息（如果已加载）
            if image_info.get('dimensions'):
                size_text = f"{image_info['dimensions'][0]}×{image_info['dimensions'][1]} | {self.format_file_size(image_info['size'])}"
                size_label = ttk.Label(info_frame, text=size_text, font=('Arial', 8))
                size_label.pack(anchor=tk.W)
                size_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
            else:
                # 显示简单的文件大小信息
                size_text = f"大小: {self.format_file_size(image_info['size'])}"
                size_label = ttk.Label(info_frame, text=size_text, font=('Arial', 8))
                size_label.pack(anchor=tk.W)
                size_label.bind("<Button-1>", lambda e, idx=i: self.show_preview(idx))
        
        # 更新滚动区域
        self.root.after_idle(self.update_scroll_region)
            
    def show_preview(self, index):
        """显示图片预览"""
        if 0 <= index < len(self.images):
            self.current_index = index
            image_info = self.images[index]
            
            # 立即显示loading状态
            self.show_loading_state(image_info['name'])
            
            # 使用线程异步加载图片，避免界面卡顿
            def load_image_async():
                try:
                    start_time = time.time()
                    
                    # 加载原图
                    file_ext = Path(image_info['path']).suffix.lower()
                    if file_ext == '.arw':
                        # 处理ARW格式
                        img = self.load_raw_image(image_info['path'])
                        self.original_image = img.copy()
                    else:
                        # 处理常规格式
                        with Image.open(image_info['path']) as img:
                            self.original_image = img.copy()
                    
                    load_time = time.time() - start_time
                    print(f"图片加载完成: {image_info['name']} ({load_time:.2f}秒)")
                    
                    # 在主线程中更新UI
                    self.root.after(0, self.on_image_loaded, image_info)
                    
                except Exception as e:
                    print(f"图片加载失败: {image_info['name']} - {str(e)}")
                    # 在主线程中显示错误
                    self.root.after(0, self.on_image_load_error, str(e))
            
            # 启动加载线程
            loading_thread = threading.Thread(target=load_image_async, daemon=True)
            loading_thread.start()
    
    def show_loading_state(self, filename):
        """显示loading状态"""
        # 清除之前的内容
        self.preview_canvas.delete('all')
        
        # 获取Canvas尺寸
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1:  # Canvas还未初始化
            canvas_width = 400
            canvas_height = 300
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # 创建loading动画元素
        # 1. 背景圆圈
        self.preview_canvas.create_oval(
            center_x - 30, center_y - 30, center_x + 30, center_y + 30,
            outline='#e0e0e0', width=2, tags='loading'
        )
        
        # 2. 旋转的加载圆弧
        self.loading_arc = self.preview_canvas.create_arc(
            center_x - 25, center_y - 25, center_x + 25, center_y + 25,
            start=0, extent=90, outline='#4CAF50', width=3, 
            style='arc', tags='loading'
        )
        
        # 3. Loading文本
        self.preview_canvas.create_text(
            center_x, center_y + 50, text="正在加载图片...", 
            font=('Arial', 12), fill='#666666', tags='loading'
        )
        
        # 4. 文件名
        self.preview_canvas.create_text(
            center_x, center_y + 70, text=filename, 
            font=('Arial', 10), fill='#999999', tags='loading'
        )
        
        # 启动loading动画
        self.loading_angle = 0
        self.animate_loading()
    
    def animate_loading(self):
        """loading动画"""
        if hasattr(self, 'loading_arc') and self.preview_canvas.find_withtag('loading'):
            # 更新旋转角度
            self.loading_angle = (self.loading_angle + 10) % 360
            
            # 更新圆弧位置
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1:  # Canvas已初始化
                center_x = canvas_width // 2
                center_y = canvas_height // 2
                
                # 删除旧的圆弧
                self.preview_canvas.delete(self.loading_arc)
                
                # 创建新的圆弧
                self.loading_arc = self.preview_canvas.create_arc(
                    center_x - 25, center_y - 25, center_x + 25, center_y + 25,
                    start=self.loading_angle, extent=90, outline='#4CAF50', width=3, 
                    style='arc', tags='loading'
                )
            
            # 继续动画
            self.root.after(50, self.animate_loading)
    
    def on_image_loaded(self, image_info):
        """图片加载完成的回调"""
        # 清除loading状态
        self.preview_canvas.delete('loading')
        
        # 重置缩放和旋转并适应窗口
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.zoom_fit()
            
        # 更新图片信息
        self.update_image_info(image_info)
    
    def on_image_load_error(self, error_message):
        """图片加载失败的回调"""
        # 清除loading状态
        self.preview_canvas.delete('loading')
        
        # 显示错误信息
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 400
            canvas_height = 300
        
        self.preview_canvas.create_text(
            canvas_width // 2, canvas_height // 2, 
            text=f"预览失败\n{error_message}", 
            font=('Arial', 12), fill='red', tags='error', justify='center'
        )
        self.original_image = None
                
    def update_image_info(self, image_info):
        """更新图片信息显示"""
        # 基本信息
        info_lines = [
            f"文件名: {image_info['name']}",
            f"路径: {image_info['path']}",
            f"文件大小: {self.format_file_size(image_info['size'])}"
        ]
        
        # 如果图片信息已加载，显示详细信息
        if image_info.get('dimensions'):
            info_lines.extend([
                f"图片尺寸: {image_info['dimensions'][0]} × {image_info['dimensions'][1]}",
                f"图片格式: {image_info.get('format', '未知')}",
                f"颜色模式: {image_info.get('mode', '未知')}"
            ])
        else:
            # 如果还在加载中，显示占位信息
            if self.original_image:
                info_lines.extend([
                    f"图片尺寸: {self.original_image.width} × {self.original_image.height}",
                    f"图片格式: {self.original_image.format or '未知'}",
                    f"颜色模式: {self.original_image.mode or '未知'}"
                ])
            else:
                info_lines.append("图片信息: 加载中...")
        
        info_lines.append(f"索引: {self.current_index + 1} / {len(self.images)}")
        
        info_text = "\n".join(info_lines)

        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.configure(state=tk.DISABLED)
        
    def clear_preview(self):
        """清空预览"""
        # 删除Canvas上的图片
        if self.canvas_image_id:
            self.preview_canvas.delete(self.canvas_image_id)
            self.canvas_image_id = None
        
        # 清除图片引用
        self.preview_canvas.image = None
        self.original_image = None
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.update_zoom_label()
        
        # 重置滚动区域
        self.preview_canvas.configure(scrollregion=(0, 0, 0, 0))
        
        # 显示占位符文本
        self.preview_canvas.delete('placeholder')
        self.preview_canvas.create_text(
            200, 150, text="选择图片进行预览", 
            font=('Arial', 14), fill='gray', tags='placeholder'
        )
        
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.configure(state=tk.DISABLED)
        
    def previous_image(self):
        """上一张图片"""
        if self.images and self.current_index > 0:
            self.show_preview(self.current_index - 1)
            
    def next_image(self):
        """下一张图片"""
        if self.images and self.current_index < len(self.images) - 1:
            self.show_preview(self.current_index + 1)
            
    def remove_current_image(self):
        """移除当前图片"""
        if self.images and 0 <= self.current_index < len(self.images):
            self.images.pop(self.current_index)
            
            if self.current_index >= len(self.images):
                self.current_index = len(self.images) - 1
                
            self.update_display()
            self.update_count_label()
            
            if self.images:
                self.show_preview(self.current_index)
            else:
                self.clear_preview()
                
    def fullscreen_preview(self):
        """全屏预览当前图片"""
        if self.images and 0 <= self.current_index < len(self.images):
            image_info = self.images[self.current_index]
            
            # 创建全屏窗口
            fullscreen_window = tk.Toplevel(self.root)
            fullscreen_window.title(f"全屏预览 - {image_info['name']}")
            fullscreen_window.attributes('-fullscreen', True)
            fullscreen_window.configure(bg='black')
            
            try:
                # 加载图片
                file_ext = Path(image_info['path']).suffix.lower()
                if file_ext == '.arw':
                    img = self.load_raw_image(image_info['path'])
                else:
                    img = Image.open(image_info['path'])
                
                # 获取屏幕尺寸
                screen_width = fullscreen_window.winfo_screenwidth()
                screen_height = fullscreen_window.winfo_screenheight()
                
                # 计算缩放比例
                img_ratio = img.width / img.height
                screen_ratio = screen_width / screen_height
                
                if img_ratio > screen_ratio:
                    new_width = screen_width
                    new_height = int(screen_width / img_ratio)
                else:
                    new_height = screen_height
                    new_width = int(screen_height * img_ratio)
                
                # 调整图片大小
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img)
                
                label = tk.Label(fullscreen_window, image=photo, bg='black')
                label.image = photo
                label.pack(expand=True)
                    
            except Exception as e:
                error_label = tk.Label(fullscreen_window, text=f"加载失败: {str(e)}", 
                                     fg='white', bg='black', font=('Arial', 16))
                error_label.pack(expand=True)
            
            # 绑定退出事件
            fullscreen_window.bind('<Escape>', lambda e: fullscreen_window.destroy())
            fullscreen_window.bind('<Button-1>', lambda e: fullscreen_window.destroy())
            fullscreen_window.focus_set()
            
    def show_in_folder(self):
        """在文件夹中显示当前图片"""
        if self.images and 0 <= self.current_index < len(self.images):
            file_path = self.images[self.current_index]['path']
            
            # macOS
            if os.name == 'posix':
                os.system(f'open -R "{file_path}"')
            # Windows
            elif os.name == 'nt':
                os.system(f'explorer /select,"{file_path}"')
            # Linux
            else:
                folder_path = os.path.dirname(file_path)
                os.system(f'xdg-open "{folder_path}"')
                
    def set_view_mode(self, mode):
        """设置视图模式"""
        self.view_mode = mode
        self.update_display()
        
    def on_size_change(self, event=None):
        """缩略图大小改变"""
        try:
            new_size = int(self.size_var.get())
            self.thumbnail_size = (new_size, new_size)
            
            # 重新生成缩略图
            for image_info in self.images:
                try:
                    with Image.open(image_info['path']) as img:
                        thumbnail = img.copy()
                        thumbnail.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                        image_info['thumbnail'] = thumbnail
                except Exception:
                    pass
                    
            # 立即重置滚动区域
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            self.update_display()
            
        except ValueError:
            pass
            
    def update_count_label(self):
        """更新图片计数标签"""
        count = len(self.images)
        
        # 计算已完成缩略图的数量
        loaded_count = sum(1 for img in self.images if img.get('thumbnail') is not None or img.get('load_error', False))
        
        # 如果正在加载且有进度信息，显示加载进度
        if hasattr(self, 'loading_queue') and self.loading_queue and not self.loading_cancelled:
            progress_percent = (loaded_count / count) * 100 if count > 0 else 0
            self.count_label.config(text=f"已加载 {count} 张图片 (缩略图: {loaded_count}/{count} {progress_percent:.1f}%)")
        else:
            # 没有正在加载时，只显示总数
            self.count_label.config(text=f"已加载 {count} 张图片")
        
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    def can_scroll(self):
        """检查是否需要滚动"""
        try:
            # 获取Canvas的当前大小
            canvas_height = self.canvas.winfo_height()
            canvas_width = self.canvas.winfo_width()
            
            # 获取滚动区域
            scrollregion = self.canvas.cget("scrollregion")
            if not scrollregion:
                return False
            
            # 解析滚动区域
            try:
                x1, y1, x2, y2 = map(float, scrollregion.split())
                content_height = y2 - y1
                content_width = x2 - x1
            except (ValueError, AttributeError):
                return False
            
            # 如果内容高度小于等于Canvas高度，则不需要滚动
            return content_height > canvas_height or content_width > canvas_width
            
        except Exception:
            # 如果出现任何错误，默认允许滚动
            return True
    
    def update_scroll_region(self):
        """更新滚动区域"""
        # 强制更新所有子控件的布局
        self.scrollable_frame.update_idletasks()
        
        # 获取scrollable_frame的实际大小
        self.scrollable_frame.update()
        
        # 计算所需的滚动区域
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)
        else:
            # 如果bbox为空，使用scrollable_frame的实际大小
            width = self.scrollable_frame.winfo_reqwidth()
            height = self.scrollable_frame.winfo_reqheight()
            self.canvas.configure(scrollregion=(0, 0, width, height))
        
    def zoom_in(self):
        """放大图片"""
        if self.original_image and self.zoom_factor < self.max_zoom:
            self.zoom_factor = min(self.zoom_factor + self.zoom_step, self.max_zoom)
            self.update_preview_image()
            
    def zoom_out(self):
        """缩小图片"""
        if self.original_image and self.zoom_factor > self.min_zoom:
            self.zoom_factor = max(self.zoom_factor - self.zoom_step, self.min_zoom)
            self.update_preview_image()
            
    def zoom_fit(self):
        """适应窗口大小"""
        if not self.original_image:
            return
            
        # 获取预览区域大小
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # 如果Canvas还没有正确初始化，使用默认大小
            canvas_width = 350
            canvas_height = 300
            
        # 获取旋转后的图片尺寸
        working_image = self.original_image
        if self.rotation_angle != 0:
            working_image = self.original_image.rotate(-self.rotation_angle, expand=True)
            
        # 计算适应窗口的缩放比例
        img_width, img_height = working_image.size
        scale_x = (canvas_width - 20) / img_width  # 留一些边距
        scale_y = (canvas_height - 20) / img_height
        
        self.zoom_factor = min(scale_x, scale_y, 1.0)  # 不超过原始大小
        self.zoom_factor = max(self.zoom_factor, self.min_zoom)
        
        self.update_preview_image()
        
    def zoom_actual(self):
        """显示实际大小(1:1)"""
        if self.original_image:
            self.zoom_factor = 1.0
            self.update_preview_image()
            
    def toggle_info_panel(self):
        """切换信息面板的显示/隐藏状态"""
        self.show_info = not self.show_info
        
        if self.show_info:
            # 显示信息面板
            self.info_frame.pack(fill=tk.X, padx=10, pady=(0, 5), before=self.preview_controls)
            self.info_button.config(text="隐藏信息")
        else:
            # 隐藏信息面板
            self.info_frame.pack_forget()
            self.info_button.config(text="显示信息")
            
    def rotate_left(self):
        """向左旋转90度"""
        if self.original_image:
            self.rotation_angle = (self.rotation_angle - 90) % 360
            self.update_preview_image()
            
    def rotate_right(self):
        """向右旋转90度"""
        if self.original_image:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.update_preview_image()
            
    def reset_rotation(self):
        """重置旋转角度"""
        if self.original_image:
            self.rotation_angle = 0
            self.update_preview_image()
            
    def update_preview_image(self):
        """更新预览图片显示"""
        if not self.original_image:
            return
            
        try:
            # 先应用旋转
            working_image = self.original_image
            if self.rotation_angle != 0:
                working_image = self.original_image.rotate(-self.rotation_angle, expand=True)
            
            # 计算缩放后的尺寸
            img_width, img_height = working_image.size
            new_width = int(img_width * self.zoom_factor)
            new_height = int(img_height * self.zoom_factor)
            
            # 缩放图片
            if new_width > 0 and new_height > 0:
                resized_img = working_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img)
                
                # 获取Canvas尺寸
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                # 计算图片位置（居中显示）
                if new_width < canvas_width:
                    x = canvas_width // 2
                else:
                    x = new_width // 2
                    
                if new_height < canvas_height:
                    y = canvas_height // 2
                else:
                    y = new_height // 2
                
                # 删除旧的图片
                if self.canvas_image_id:
                    self.preview_canvas.delete(self.canvas_image_id)
                
                # 在Canvas上创建新图片
                self.canvas_image_id = self.preview_canvas.create_image(x, y, image=photo, anchor="center")
                
                # 保存图片引用，防止被垃圾回收
                self.preview_canvas.image = photo
                
                # 设置滚动区域 - 确保滚动区域足够大以支持拖拽
                # 滚动区域应该比图片稍大，这样即使图片适应窗口也能拖拽
                scroll_width = max(new_width + 200, canvas_width + 100)
                scroll_height = max(new_height + 200, canvas_height + 100)
                
                # 设置滚动区域，以图片中心为基准
                left = max(0, x - scroll_width // 2)
                top = max(0, y - scroll_height // 2)
                right = left + scroll_width
                bottom = top + scroll_height
                
                self.preview_canvas.configure(scrollregion=(left, top, right, bottom))
                
                # 如果图片比Canvas大，自动滚动到图片中心
                if new_width > canvas_width or new_height > canvas_height:
                    # 计算滚动位置，使图片居中显示
                    center_x = x / scroll_width
                    center_y = y / scroll_height
                    
                    # 设置滚动位置
                    self.preview_canvas.xview_moveto(max(0, center_x - 0.5))
                    self.preview_canvas.yview_moveto(max(0, center_y - 0.5))
                
            # 更新缩放标签
            self.update_zoom_label()
            
            # 更新光标
            self.update_canvas_cursor()
            
        except Exception as e:
            print(f"更新预览图片失败: {e}")
            
    def update_zoom_label(self):
        """更新缩放比例标签"""
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")
        
    def scroll_preview(self, direction):
        """键盘滚动预览区域"""
        if not self.original_image:
            return
            
        # 滚动步长
        scroll_step = 0.1
        
        if direction == 'up':
            # 向上滚动
            current_y = self.preview_canvas.canvasy(0)
            self.preview_canvas.yview_scroll(-1, "units")
        elif direction == 'down':
            # 向下滚动
            current_y = self.preview_canvas.canvasy(0)
            self.preview_canvas.yview_scroll(1, "units")
        elif direction == 'left':
            # 向左滚动
            current_x = self.preview_canvas.canvasx(0)
            self.preview_canvas.xview_scroll(-1, "units")
        elif direction == 'right':
            # 向右滚动
            current_x = self.preview_canvas.canvasx(0)
            self.preview_canvas.xview_scroll(1, "units")
            
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "last_file_directory": os.path.expanduser("~"),
            "last_folder_directory": os.path.expanduser("~")
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有必要的键都存在
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return default_config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return default_config
            
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            
    def update_last_directory(self, directory_type, path):
        """更新最后使用的目录"""
        if directory_type in ["last_file_directory", "last_folder_directory"]:
            # 如果是文件路径，获取其目录
            if os.path.isfile(path):
                path = os.path.dirname(path)
            
            # 确保目录存在
            if os.path.isdir(path):
                self.config[directory_type] = path
                self.save_config()
                
    def first_image(self):
        """跳转到第一张图片"""
        if self.images:
            self.current_index = 0
            self.show_preview(0)
            
    def last_image(self):
        """跳转到最后一张图片"""
        if self.images:
            self.current_index = len(self.images) - 1
            self.show_preview(self.current_index)
            
    def set_thumbnail_size(self, size):
        """设置缩略图大小"""
        self.size_var.set(str(size))
        self.on_size_change()
        
    def refresh_display(self):
        """刷新显示"""
        self.update_display()
        if self.images and 0 <= self.current_index < len(self.images):
            self.show_preview(self.current_index)
            
    def remove_current_image(self):
        """从列表中移除当前图片"""
        if self.images and 0 <= self.current_index < len(self.images):
            # 确认删除
            from tkinter import messagebox
            current_image = self.images[self.current_index]
            result = messagebox.askyesno("确认", f"确定要从列表中移除图片 '{current_image['name']}'？\n\n注意：这只会从当前列表中移除，不会删除文件。")
            
            if result:
                # 从列表中移除
                self.images.pop(self.current_index)
                
                # 调整当前索引
                if self.images:
                    if self.current_index >= len(self.images):
                        self.current_index = len(self.images) - 1
                    self.show_preview(self.current_index)
                else:
                    self.current_index = 0
                    self.clear_preview()
                
                # 更新显示
                self.update_display()
                self.update_count_label()
            
    def show_shortcuts(self):
        """显示快捷键帮助"""
        shortcuts_text = """
快捷键说明：

文件操作：
  Ctrl+O          选择文件
  Ctrl+Shift+O    选择文件夹
  Ctrl+N          清空列表
  Ctrl+Shift+R    在文件夹中显示
  Ctrl+Q          退出程序

图片导航：
  Page Up         上一张图片
  Page Down       下一张图片
  Home            第一张图片
  End             最后一张图片

图片查看：
  Ctrl++          放大
  Ctrl+-          缩小
  Ctrl+0          实际大小
  Ctrl+9          适应窗口
  F11             全屏预览
  Ctrl+I          显示/隐藏信息面板

图片旋转：
  Ctrl+L          向左旋转
  Ctrl+R          向右旋转
  Ctrl+T          重置旋转

预览区域滚动：
  方向键          滚动预览区域

其他：
  F5              刷新显示
  Delete          删除当前图片
        """
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("快捷键说明")
        help_window.geometry("400x600")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # 创建文本框显示快捷键
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # 插入快捷键文本
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 关闭按钮
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(button_frame, text="关闭", command=help_window.destroy).pack(side=tk.RIGHT)
        
    def show_about(self):
        """显示关于对话框"""
        about_text = """
图片查看器 v1.0

一个功能丰富的图片查看器，支持多种图片格式包括：
• 常规格式：JPEG, PNG, GIF, BMP, TIFF, WebP
• RAW格式：ARW (索尼相机)

主要功能：
• 图片浏览和预览
• 缩放、旋转、全屏查看
• 网格和列表视图模式
• 图片信息显示
• 快捷键支持
• 文件夹批量浏览

开发者：图片查看器团队
版本：1.0.0
        """
        
        # 创建关于窗口
        about_window = tk.Toplevel(self.root)
        about_window.title("关于图片查看器")
        about_window.geometry("350x400")
        about_window.transient(self.root)
        about_window.grab_set()
        about_window.resizable(False, False)
        
        # 主框架
        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图片查看器", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 版本信息
        version_label = ttk.Label(main_frame, text="版本 1.0.0", font=('Arial', 12))
        version_label.pack(pady=(0, 20))
        
        # 描述文本
        text_widget = tk.Text(main_frame, wrap=tk.WORD, state=tk.DISABLED, 
                             height=12, font=('Arial', 10), relief=tk.FLAT)
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 关闭按钮
        ttk.Button(main_frame, text="关闭", command=about_window.destroy).pack()
        
    def open_camera_raw(self):
        """打开Camera Raw处理工具"""
        # 尝试延迟导入Camera Raw模块
        if not _import_camera_raw_module():
            messagebox.showerror("错误", "Camera Raw功能不可用。\n请确保已安装所需的依赖库：\n- rawpy\n- matplotlib\n- numpy")
            return
            
        try:
            # 检查是否有当前选中的图像
            current_image_path = None
            if self.images and 0 <= self.current_index < len(self.images):
                current_image_path = self.images[self.current_index]['path']
            
            # 创建Camera Raw窗口
            if current_image_path:
                camera_raw_window = CameraRawWindow(self.root, current_image_path)
            else:
                camera_raw_window = CameraRawWindow(self.root)
                
        except Exception as e:
            messagebox.showerror("错误", f"无法打开Camera Raw工具：\n{str(e)}")
    
    def open_stacking_tool(self):
        """打开星空图像堆叠工具"""
        # 尝试延迟导入星空堆叠模块
        if not _import_stacking_module():
            messagebox.showerror("错误", "星空堆叠功能不可用。\n请确保已安装所需的依赖库：\n- opencv-python\n- numpy\n- scikit-image")
            return
            
        try:
            # 创建星空堆叠窗口 - 只传递parent参数
            stacking_window = StackingWindow(self.root)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开星空堆叠工具：\n{str(e)}")

def main():
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()