#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星空图像堆叠用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
from pathlib import Path
import time
from typing import List, Optional
import json

from .processor import AstroStacker, validate_images_for_stacking, estimate_processing_time
from ..camera_raw import CameraRawWindow

class StackingWindow:
    """星空堆叠窗口"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Sky Editor - 星空图像堆叠")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # 堆叠器实例
        self.stacker = AstroStacker()
        self.processing_thread = None
        self.result_image = None
        
        # 图像列表
        self.image_paths = []
        
        # 设置UI
        self.setup_ui()
        self.load_settings()
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 1. 图像选择标签页
        self.setup_image_tab(notebook)
        
        # 2. 参数设置标签页
        self.setup_params_tab(notebook)
        
        # 3. 处理结果标签页
        self.setup_result_tab(notebook)
        
        # 底部控制栏
        self.setup_control_bar(main_frame)
    
    def setup_image_tab(self, notebook):
        """设置图像选择标签页"""
        image_frame = ttk.Frame(notebook)
        notebook.add(image_frame, text="图像选择")
        
        # 顶部按钮栏
        button_frame = ttk.Frame(image_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="添加图像", command=self.add_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加文件夹", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空列表", command=self.clear_images).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Button(button_frame, text="移除选中", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Camera Raw", command=self.open_camera_raw).pack(side=tk.LEFT, padx=(20, 5))
        
        # 图像列表
        list_frame = ttk.Frame(image_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('序号', '文件名', '尺寸', '大小', '状态')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.image_tree.heading(col, text=col)
        
        # 设置列宽
        self.image_tree.column('序号', width=50)
        self.image_tree.column('文件名', width=300)
        self.image_tree.column('尺寸', width=100)
        self.image_tree.column('大小', width=80)
        self.image_tree.column('状态', width=100)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 信息标签
        info_frame = ttk.Frame(image_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.image_info_label = ttk.Label(info_frame, text="请选择要堆叠的星空图像")
        self.image_info_label.pack(side=tk.LEFT)
        
        self.estimate_label = ttk.Label(info_frame, text="")
        self.estimate_label.pack(side=tk.RIGHT)
    
    def create_help_button(self, parent, title, content):
        """创建帮助按钮"""
        help_label = ttk.Label(parent, text="?", foreground="blue", cursor="hand2", font=('Arial', 10, 'bold'))
        help_label.pack(side=tk.LEFT, padx=(3, 0))
        
        def show_help(event=None):
            help_window = tk.Toplevel(self.window)
            help_window.title(title)
            help_window.geometry("400x300")
            help_window.resizable(True, True)
            
            # 创建文本框显示帮助内容
            text_frame = ttk.Frame(help_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.insert(1.0, content)
            text_widget.configure(state=tk.DISABLED)
            
            # 关闭按钮
            button_frame = ttk.Frame(help_window)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            ttk.Button(button_frame, text="关闭", command=help_window.destroy).pack(side=tk.RIGHT)
            
            # 居中显示
            help_window.transient(self.window)
            help_window.grab_set()
        
        help_label.bind("<Button-1>", show_help)
        return help_label
    
    def setup_params_tab(self, notebook):
        """设置参数配置标签页"""
        params_frame = ttk.Frame(notebook)
        notebook.add(params_frame, text="参数设置")
        
        # 创建滚动区域
        canvas = tk.Canvas(params_frame)
        scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 1. 星点检测参数
        star_group = ttk.LabelFrame(scrollable_frame, text="星点检测参数", padding=10)
        star_group.pack(fill=tk.X, pady=(0, 10))
        
        # 检测阈值
        ttk.Label(star_group, text="检测阈值:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.threshold_var = tk.IntVar(value=50)
        threshold_scale = ttk.Scale(star_group, from_=10, to=200, variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.grid(row=0, column=1, sticky=tk.EW, padx=(10, 5), pady=2)
        self.threshold_label = ttk.Label(star_group, text="50")
        self.threshold_label.grid(row=0, column=2, pady=2)
        threshold_scale.configure(command=lambda v: self.threshold_label.configure(text=f"{int(float(v))}"))
        
        threshold_help_frame = ttk.Frame(star_group)
        threshold_help_frame.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(threshold_help_frame, "检测阈值", 
            "用于星点检测的二值化阈值。\n\n"
            "• 较低值(10-30)：检测更多暗星，但可能包含噪点\n"
            "• 中等值(40-80)：平衡检测效果，推荐用于大多数情况\n"
            "• 较高值(90-200)：只检测明亮星点，减少误检\n\n"
            "建议：从50开始调整，根据图像亮度和噪点情况微调")
        
        # 最小星点面积
        ttk.Label(star_group, text="最小面积:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.min_area_var = tk.IntVar(value=3)
        min_area_spinbox = ttk.Spinbox(star_group, from_=1, to=20, textvariable=self.min_area_var, width=10)
        min_area_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        min_area_help_frame = ttk.Frame(star_group)
        min_area_help_frame.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(min_area_help_frame, "最小星点面积",
            "检测到的星点的最小像素面积。\n\n"
            "• 1-3像素：检测极小的星点，可能包含噪点\n"
            "• 3-8像素：适合大多数星空图像\n"
            "• 8-20像素：只检测较大的星点\n\n"
            "建议：使用3-5像素，可以过滤掉大部分噪点")
        
        # 最大星点面积
        ttk.Label(star_group, text="最大面积:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_area_var = tk.IntVar(value=100)
        max_area_spinbox = ttk.Spinbox(star_group, from_=20, to=500, textvariable=self.max_area_var, width=10)
        max_area_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        max_area_help_frame = ttk.Frame(star_group)
        max_area_help_frame.grid(row=2, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(max_area_help_frame, "最大星点面积",
            "检测到的星点的最大像素面积。\n\n"
            "• 50-100像素：适合普通星点\n"
            "• 100-300像素：包含较大的亮星\n"
            "• 300-500像素：包含过曝的亮星或星云\n\n"
            "建议：使用100像素，避免将星云或过曝区域误认为星点")
        
        # 高斯模糊
        ttk.Label(star_group, text="高斯模糊:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.blur_var = tk.DoubleVar(value=1.5)
        blur_spinbox = ttk.Spinbox(star_group, from_=0.5, to=5.0, increment=0.1, textvariable=self.blur_var, width=10)
        blur_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        blur_help_frame = ttk.Frame(star_group)
        blur_help_frame.grid(row=3, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(blur_help_frame, "高斯模糊半径",
            "在星点检测前应用的高斯模糊强度。\n\n"
            "• 0.5-1.0：轻微模糊，保持星点锐度\n"
            "• 1.0-2.0：中等模糊，平衡噪点抑制和星点检测\n"
            "• 2.0-5.0：强模糊，有效抑制噪点但可能丢失小星点\n\n"
            "建议：使用1.5，在噪点抑制和星点保持之间取得平衡")
        
        star_group.columnconfigure(1, weight=1)
        
        # 2. 对齐参数
        align_group = ttk.LabelFrame(scrollable_frame, text="图像对齐参数", padding=10)
        align_group.pack(fill=tk.X, pady=(0, 10))
        
        # 最大特征点数
        ttk.Label(align_group, text="最大特征点:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.max_features_var = tk.IntVar(value=500)
        max_features_spinbox = ttk.Spinbox(align_group, from_=100, to=2000, increment=50, textvariable=self.max_features_var, width=10)
        max_features_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        max_features_help_frame = ttk.Frame(align_group)
        max_features_help_frame.grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(max_features_help_frame, "最大特征点数",
            "用于图像对齐的最大特征点数量。\n\n"
            "• 100-300：快速处理，适合简单场景\n"
            "• 300-800：平衡速度和精度，推荐设置\n"
            "• 800-2000：高精度对齐，处理时间较长\n\n"
            "建议：使用500个特征点，在大多数情况下能提供良好的对齐效果")
        
        # RANSAC阈值
        ttk.Label(align_group, text="RANSAC阈值:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ransac_var = tk.DoubleVar(value=5.0)
        ransac_spinbox = ttk.Spinbox(align_group, from_=1.0, to=20.0, increment=0.5, textvariable=self.ransac_var, width=10)
        ransac_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ransac_help_frame = ttk.Frame(align_group)
        ransac_help_frame.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(ransac_help_frame, "RANSAC阈值",
            "RANSAC算法的像素误差阈值。\n\n"
            "• 1.0-3.0：严格匹配，可能丢失一些有效匹配\n"
            "• 3.0-8.0：平衡精度和匹配数量，推荐范围\n"
            "• 8.0-20.0：宽松匹配，可能包含错误匹配\n\n"
            "建议：使用5.0像素，在精度和鲁棒性之间取得平衡")
        
        align_group.columnconfigure(1, weight=1)
        
        # 3. 堆叠参数
        stack_group = ttk.LabelFrame(scrollable_frame, text="堆叠参数", padding=10)
        stack_group.pack(fill=tk.X, pady=(0, 10))
        
        # 堆叠方法
        ttk.Label(stack_group, text="堆叠方法:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.method_var = tk.StringVar(value="average")
        method_combo = ttk.Combobox(stack_group, textvariable=self.method_var, 
                                   values=["average", "median", "maximum", "sigma_clip"], 
                                   state="readonly", width=15)
        method_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        method_help_frame = ttk.Frame(stack_group)
        method_help_frame.grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(method_help_frame, "堆叠方法",
            "选择图像堆叠的算法。\n\n"
            "• Average（平均）：计算所有像素的平均值，适合大多数情况\n"
            "• Median（中位数）：使用中位数，能有效去除异常值和噪点\n"
            "• Maximum（最大值）：保留最亮的像素，适合星轨摄影\n"
            "• Sigma Clip（西格玛裁剪）：去除异常值后平均，最佳降噪效果\n\n"
            "建议：一般使用Average，噪点较多时选择Sigma Clip")
        
        # Sigma裁剪参数（仅在选择sigma_clip时显示）
        self.sigma_frame = ttk.Frame(stack_group)
        self.sigma_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))
        
        ttk.Label(self.sigma_frame, text="Sigma下限:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sigma_low_var = tk.DoubleVar(value=2.0)
        sigma_low_spinbox = ttk.Spinbox(self.sigma_frame, from_=0.5, to=5.0, increment=0.1, textvariable=self.sigma_low_var, width=8)
        sigma_low_spinbox.grid(row=0, column=1, padx=(5, 10), pady=2)
        
        sigma_low_help_frame = ttk.Frame(self.sigma_frame)
        sigma_low_help_frame.grid(row=0, column=2, sticky=tk.W, padx=(0, 10), pady=2)
        self.create_help_button(sigma_low_help_frame, "Sigma下限",
            "Sigma裁剪的下限阈值。\n\n"
            "• 0.5-1.5：保守裁剪，保留更多数据\n"
            "• 1.5-3.0：标准裁剪，平衡效果\n"
            "• 3.0-5.0：激进裁剪，去除更多异常值\n\n"
            "建议：使用2.0，能有效去除暗噪点和热像素")
        
        ttk.Label(self.sigma_frame, text="Sigma上限:").grid(row=0, column=3, sticky=tk.W, pady=2)
        self.sigma_high_var = tk.DoubleVar(value=2.0)
        sigma_high_spinbox = ttk.Spinbox(self.sigma_frame, from_=0.5, to=5.0, increment=0.1, textvariable=self.sigma_high_var, width=8)
        sigma_high_spinbox.grid(row=0, column=4, padx=(5, 0), pady=2)
        
        sigma_high_help_frame = ttk.Frame(self.sigma_frame)
        sigma_high_help_frame.grid(row=0, column=5, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(sigma_high_help_frame, "Sigma上限",
            "Sigma裁剪的上限阈值。\n\n"
            "• 0.5-1.5：保守裁剪，保留更多亮点\n"
            "• 1.5-3.0：标准裁剪，平衡效果\n"
            "• 3.0-5.0：激进裁剪，去除飞机轨迹等\n\n"
            "建议：使用2.0，能去除飞机轨迹和卫星轨迹")
        
        # 绑定方法选择事件
        method_combo.bind('<<ComboboxSelected>>', self.on_method_change)
        self.on_method_change()  # 初始化显示
        
        stack_group.columnconfigure(1, weight=1)
        
        # 4. 输出设置
        output_group = ttk.LabelFrame(scrollable_frame, text="输出设置", padding=10)
        output_group.pack(fill=tk.X, pady=(0, 10))
        
        # 输出路径
        ttk.Label(output_group, text="输出路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.output_path_var = tk.StringVar(value="")
        output_frame = ttk.Frame(output_group)
        output_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        ttk.Entry(output_frame, textvariable=self.output_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览", command=self.browse_output_path, width=8).pack(side=tk.RIGHT, padx=(5, 0))
        
        output_path_help_frame = ttk.Frame(output_group)
        output_path_help_frame.grid(row=0, column=2, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(output_path_help_frame, "输出路径",
            "指定堆叠结果的保存位置。\n\n"
            "• 如果不指定，将保存到第一张图片的目录\n"
            "• 支持的格式：JPEG、PNG、TIFF\n"
            "• 文件名会自动添加时间戳避免覆盖\n\n"
            "建议：选择有足够空间的目录，堆叠结果通常较大")
        
        # 图像质量
        ttk.Label(output_group, text="JPEG质量:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(output_group, from_=50, to=100, variable=self.quality_var, orient=tk.HORIZONTAL)
        quality_scale.grid(row=1, column=1, sticky=tk.EW, padx=(10, 5), pady=2)
        self.quality_label = ttk.Label(output_group, text="95")
        self.quality_label.grid(row=1, column=2, pady=2)
        quality_scale.configure(command=lambda v: self.quality_label.configure(text=f"{int(float(v))}"))
        
        quality_help_frame = ttk.Frame(output_group)
        quality_help_frame.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        self.create_help_button(quality_help_frame, "JPEG质量",
            "JPEG格式的压缩质量设置。\n\n"
            "• 50-70：高压缩，文件小但质量较低\n"
            "• 70-90：平衡压缩，适合网络分享\n"
            "• 90-100：低压缩，高质量，文件较大\n\n"
            "建议：使用95，在质量和文件大小间取得平衡")
        
        output_group.columnconfigure(1, weight=1)
        
        # 预设按钮
        preset_frame = ttk.Frame(scrollable_frame)
        preset_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(preset_frame, text="快速模式", command=lambda: self.load_preset("fast")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="平衡模式", command=lambda: self.load_preset("balanced")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="高质量模式", command=lambda: self.load_preset("quality")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="保存设置", command=self.save_settings).pack(side=tk.RIGHT)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_result_tab(self, notebook):
        """设置结果显示标签页"""
        result_frame = ttk.Frame(notebook)
        notebook.add(result_frame, text="处理结果")
        
        # 顶部工具栏
        toolbar = ttk.Frame(result_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="保存结果", command=self.save_result).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="另存为", command=self.save_result_as).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="在主窗口中打开", command=self.open_in_main).pack(side=tk.LEFT, padx=(0, 20))
        
        # 缩放控制
        ttk.Label(toolbar, text="缩放:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="-", width=3, command=self.zoom_out_result).pack(side=tk.LEFT, padx=(0, 2))
        
        self.result_zoom_label = ttk.Label(toolbar, text="100%", width=6, anchor=tk.CENTER)
        self.result_zoom_label.pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(toolbar, text="+", width=3, command=self.zoom_in_result).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="适应", command=self.zoom_fit_result).pack(side=tk.LEFT, padx=(0, 5))
        
        # 结果显示区域
        display_frame = ttk.Frame(result_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas用于显示结果
        self.result_canvas = tk.Canvas(display_frame, bg='white', highlightthickness=0)
        result_v_scroll = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.result_canvas.yview)
        result_h_scroll = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.result_canvas.xview)
        
        self.result_canvas.configure(yscrollcommand=result_v_scroll.set, xscrollcommand=result_h_scroll.set)
        
        result_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        result_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 初始化显示
        self.result_canvas_image_id = None
        self.result_zoom_factor = 1.0
        self.result_canvas.create_text(
            200, 150, text="处理完成后将在此显示结果", 
            font=('Arial', 14), fill='gray', tags='placeholder'
        )
        
        # 信息面板
        info_panel = ttk.Frame(result_frame)
        info_panel.pack(fill=tk.X, pady=(10, 0))
        
        self.result_info_text = tk.Text(info_panel, height=4, wrap=tk.WORD, state=tk.DISABLED)
        info_scroll = ttk.Scrollbar(info_panel, orient=tk.VERTICAL, command=self.result_info_text.yview)
        self.result_info_text.configure(yscrollcommand=info_scroll.set)
        
        self.result_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_control_bar(self, parent):
        """设置底部控制栏"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 左侧：进度信息
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # 右侧：控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="开始堆叠", command=self.start_stacking)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_stacking, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="关闭", command=self.on_closing).pack(side=tk.LEFT)
    
    def add_images(self):
        """添加图像文件"""
        filetypes = [
            ("图像文件", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.arw *.cr2 *.nef *.dng"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("TIFF文件", "*.tiff *.tif"),
            ("RAW文件", "*.arw *.cr2 *.nef *.dng"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择星空图像",
            filetypes=filetypes
        )
        
        if files:
            self.add_image_files(files)
    
    def add_folder(self):
        """添加文件夹中的图像"""
        folder = filedialog.askdirectory(title="选择包含星空图像的文件夹")
        
        if folder:
            # 支持的图像格式
            extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.arw', '.cr2', '.nef', '.dng'}
            
            image_files = []
            for file_path in Path(folder).rglob('*'):
                if file_path.suffix.lower() in extensions:
                    image_files.append(str(file_path))
            
            if image_files:
                self.add_image_files(image_files)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图像文件")
    
    def add_image_files(self, files):
        """添加图像文件到列表"""
        for file_path in files:
            if file_path not in self.image_paths:
                try:
                    # 获取图像信息
                    img = Image.open(file_path)
                    size_str = f"{img.width}x{img.height}"
                    img.close()
                    
                    # 获取文件大小
                    file_size = os.path.getsize(file_path)
                    size_mb = file_size / (1024 * 1024)
                    size_str_mb = f"{size_mb:.1f}MB"
                    
                    # 添加到列表
                    self.image_paths.append(file_path)
                    
                    # 添加到树形控件
                    item_id = self.image_tree.insert('', 'end', values=(
                        len(self.image_paths),
                        Path(file_path).name,
                        size_str,
                        size_str_mb,
                        "就绪"
                    ))
                    
                except Exception as e:
                    messagebox.showerror("错误", f"无法加载图像 {Path(file_path).name}: {str(e)}")
        
        self.update_image_info()
    
    def clear_images(self):
        """清空图像列表"""
        self.image_paths.clear()
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        self.update_image_info()
    
    def remove_selected(self):
        """移除选中的图像"""
        selected_items = self.image_tree.selection()
        if not selected_items:
            return
        
        # 获取要删除的索引
        indices_to_remove = []
        for item in selected_items:
            values = self.image_tree.item(item)['values']
            if values:
                indices_to_remove.append(int(values[0]) - 1)  # 序号从1开始
        
        # 按降序排序，从后往前删除
        indices_to_remove.sort(reverse=True)
        
        for index in indices_to_remove:
            if 0 <= index < len(self.image_paths):
                del self.image_paths[index]
        
        # 重新构建树形控件
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        for i, file_path in enumerate(self.image_paths):
            try:
                img = Image.open(file_path)
                size_str = f"{img.width}x{img.height}"
                img.close()
                
                file_size = os.path.getsize(file_path)
                size_mb = file_size / (1024 * 1024)
                size_str_mb = f"{size_mb:.1f}MB"
                
                self.image_tree.insert('', 'end', values=(
                    i + 1,
                    Path(file_path).name,
                    size_str,
                    size_str_mb,
                    "就绪"
                ))
            except:
                pass
        
        self.update_image_info()
    
    def update_image_info(self):
        """更新图像信息显示"""
        count = len(self.image_paths)
        if count == 0:
            self.image_info_label.configure(text="请选择要堆叠的星空图像")
            self.estimate_label.configure(text="")
        else:
            self.image_info_label.configure(text=f"已选择 {count} 张图像")
            
            # 估算处理时间
            if count >= 2:
                try:
                    img = Image.open(self.image_paths[0])
                    estimated_time = estimate_processing_time(count, img.size)
                    img.close()
                    
                    if estimated_time < 60:
                        time_str = f"约 {estimated_time:.0f} 秒"
                    else:
                        time_str = f"约 {estimated_time/60:.1f} 分钟"
                    
                    self.estimate_label.configure(text=f"预计处理时间: {time_str}")
                except:
                    self.estimate_label.configure(text="")
            else:
                self.estimate_label.configure(text="至少需要2张图像")
    
    def on_method_change(self, event=None):
        """堆叠方法改变时的处理"""
        method = self.method_var.get()
        if method == "sigma_clip":
            # 显示Sigma参数
            for widget in self.sigma_frame.winfo_children():
                widget.grid()
        else:
            # 隐藏Sigma参数
            for widget in self.sigma_frame.winfo_children():
                widget.grid_remove()
    
    def browse_output_path(self):
        """浏览输出路径"""
        filename = filedialog.asksaveasfilename(
            title="保存堆叠结果",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG文件", "*.jpg"),
                ("PNG文件", "*.png"),
                ("TIFF文件", "*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            self.output_path_var.set(filename)
    
    def load_preset(self, preset_name):
        """加载预设参数"""
        presets = {
            "fast": {
                "threshold": 60,
                "min_area": 5,
                "max_area": 80,
                "blur": 2.0,
                "max_features": 300,
                "ransac": 8.0,
                "method": "average"
            },
            "balanced": {
                "threshold": 50,
                "min_area": 3,
                "max_area": 100,
                "blur": 1.5,
                "max_features": 500,
                "ransac": 5.0,
                "method": "median"
            },
            "quality": {
                "threshold": 40,
                "min_area": 2,
                "max_area": 150,
                "blur": 1.0,
                "max_features": 800,
                "ransac": 3.0,
                "method": "sigma_clip"
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.threshold_var.set(preset["threshold"])
            self.min_area_var.set(preset["min_area"])
            self.max_area_var.set(preset["max_area"])
            self.blur_var.set(preset["blur"])
            self.max_features_var.set(preset["max_features"])
            self.ransac_var.set(preset["ransac"])
            self.method_var.set(preset["method"])
            
            # 更新显示
            self.threshold_label.configure(text=str(preset["threshold"]))
            self.on_method_change()
    
    def save_settings(self):
        """保存当前设置"""
        settings = {
            "star_detection": {
                "threshold": self.threshold_var.get(),
                "min_area": self.min_area_var.get(),
                "max_area": self.max_area_var.get(),
                "gaussian_blur": self.blur_var.get()
            },
            "alignment": {
                "max_features": self.max_features_var.get(),
                "ransac_threshold": self.ransac_var.get()
            },
            "stacking": {
                "method": self.method_var.get(),
                "sigma_low": self.sigma_low_var.get(),
                "sigma_high": self.sigma_high_var.get()
            },
            "output": {
                "quality": self.quality_var.get()
            }
        }
        
        try:
            settings_path = Path.home() / ".sky_editor_stacking.json"
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("成功", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def load_settings(self):
        """加载保存的设置"""
        try:
            settings_path = Path.home() / ".sky_editor_stacking.json"
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 应用设置
                star = settings.get("star_detection", {})
                self.threshold_var.set(star.get("threshold", 50))
                self.min_area_var.set(star.get("min_area", 3))
                self.max_area_var.set(star.get("max_area", 100))
                self.blur_var.set(star.get("gaussian_blur", 1.5))
                
                align = settings.get("alignment", {})
                self.max_features_var.set(align.get("max_features", 500))
                self.ransac_var.set(align.get("ransac_threshold", 5.0))
                
                stack = settings.get("stacking", {})
                self.method_var.set(stack.get("method", "average"))
                self.sigma_low_var.set(stack.get("sigma_low", 2.0))
                self.sigma_high_var.set(stack.get("sigma_high", 2.0))
                
                output = settings.get("output", {})
                self.quality_var.set(output.get("quality", 95))
                
                # 更新显示
                self.threshold_label.configure(text=str(self.threshold_var.get()))
                self.quality_label.configure(text=str(self.quality_var.get()))
                self.on_method_change()
                
        except Exception as e:
            # 如果加载失败，使用默认设置
            pass
    
    def start_stacking(self):
        """开始堆叠处理"""
        if len(self.image_paths) < 2:
            messagebox.showerror("错误", "至少需要2张图像进行堆叠")
            return
        
        # 验证图像
        valid, message = validate_images_for_stacking(self.image_paths)
        if not valid:
            messagebox.showerror("错误", message)
            return
        
        # 检查输出路径
        if not self.output_path_var.get():
            # 自动生成输出路径
            first_image_path = Path(self.image_paths[0])
            output_path = first_image_path.parent / f"stacked_{int(time.time())}.jpg"
            self.output_path_var.set(str(output_path))
        
        # 更新堆叠器参数
        self.update_stacker_params()
        
        # 禁用开始按钮，启用取消按钮
        self.start_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.NORMAL)
        
        # 重置进度
        self.progress_bar['value'] = 0
        self.progress_label.configure(text="准备开始...")
        
        # 在新线程中开始处理
        self.processing_thread = threading.Thread(target=self.process_stacking)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def update_stacker_params(self):
        """更新堆叠器参数"""
        # 星点检测参数
        self.stacker.star_detection_params.update({
            'threshold': self.threshold_var.get(),
            'min_area': self.min_area_var.get(),
            'max_area': self.max_area_var.get(),
            'gaussian_blur': self.blur_var.get()
        })
        
        # 对齐参数
        self.stacker.alignment_params.update({
            'max_features': self.max_features_var.get(),
            'ransac_threshold': self.ransac_var.get()
        })
        
        # 堆叠参数
        self.stacker.stacking_params.update({
            'method': self.method_var.get(),
            'sigma_low': self.sigma_low_var.get(),
            'sigma_high': self.sigma_high_var.get()
        })
    
    def process_stacking(self):
        """处理堆叠（在后台线程中运行）"""
        try:
            # 处理堆叠
            result = self.stacker.process_stack(
                self.image_paths,
                progress_callback=self.update_progress
            )
            
            if result is not None and not self.stacker.cancel_flag:
                # 保存结果
                success = self.stacker.save_result(
                    result, 
                    self.output_path_var.get(),
                    quality=self.quality_var.get()
                )
                
                if success:
                    # 在主线程中更新UI
                    self.window.after(0, self.on_stacking_complete, result)
                else:
                    self.window.after(0, self.on_stacking_error, "保存结果失败")
            elif self.stacker.cancel_flag:
                self.window.after(0, self.on_stacking_cancelled)
            else:
                self.window.after(0, self.on_stacking_error, "堆叠处理失败")
                
        except Exception as e:
            self.window.after(0, self.on_stacking_error, str(e))
    
    def update_progress(self, message, progress):
        """更新进度（线程安全）"""
        self.window.after(0, self._update_progress_ui, message, progress)
    
    def _update_progress_ui(self, message, progress):
        """更新进度UI"""
        self.progress_label.configure(text=message)
        self.progress_bar['value'] = progress
        self.window.update_idletasks()
    
    def cancel_stacking(self):
        """取消堆叠处理"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.stacker.cancel_processing()
            self.progress_label.configure(text="正在取消...")
    
    def on_stacking_complete(self, result):
        """堆叠完成的处理"""
        self.result_image = result
        
        # 重置按钮状态
        self.start_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        
        # 更新进度
        self.progress_label.configure(text="堆叠完成")
        self.progress_bar['value'] = 100
        
        # 显示结果
        self.display_result(result)
        
        # 切换到结果标签页
        notebook = self.window.nametowidget(self.window.winfo_children()[0].winfo_children()[0])
        notebook.select(2)  # 选择第三个标签页（结果）
        
        # 显示堆叠信息
        self.show_stacking_info()
        
        messagebox.showinfo("成功", f"星空图像堆叠完成！\n结果已保存到: {self.output_path_var.get()}")
    
    def on_stacking_error(self, error_message):
        """堆叠出错的处理"""
        # 重置按钮状态
        self.start_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        
        # 更新进度
        self.progress_label.configure(text="处理失败")
        
        messagebox.showerror("错误", f"堆叠处理失败: {error_message}")
    
    def on_stacking_cancelled(self):
        """堆叠取消的处理"""
        # 重置按钮状态
        self.start_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        
        # 更新进度
        self.progress_label.configure(text="已取消")
        self.progress_bar['value'] = 0
        
        messagebox.showinfo("提示", "堆叠处理已取消")
    
    def display_result(self, result):
        """显示堆叠结果"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(result)
            
            # 计算适合的显示尺寸
            canvas_width = self.result_canvas.winfo_width()
            canvas_height = self.result_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas还没有正确初始化，延迟显示
                self.window.after(100, lambda: self.display_result(result))
                return
            
            # 计算缩放比例
            img_width, img_height = pil_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            self.result_zoom_factor = min(scale_x, scale_y, 1.0)  # 不放大
            
            # 缩放图像
            new_width = int(img_width * self.result_zoom_factor)
            new_height = int(img_height * self.result_zoom_factor)
            
            if new_width > 0 and new_height > 0:
                display_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为Tkinter图像
                self.result_tk_image = ImageTk.PhotoImage(display_image)
                
                # 清除旧内容
                self.result_canvas.delete("all")
                
                # 显示图像
                self.result_canvas_image_id = self.result_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=self.result_tk_image,
                    anchor=tk.CENTER
                )
                
                # 更新缩放标签
                zoom_percent = int(self.result_zoom_factor * 100)
                self.result_zoom_label.configure(text=f"{zoom_percent}%")
                
                # 更新滚动区域
                self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
        
        except Exception as e:
            messagebox.showerror("错误", f"显示结果失败: {str(e)}")
    
    def show_stacking_info(self):
        """显示堆叠信息"""
        try:
            info = self.stacker.get_stacking_info()
            
            info_text = f"""堆叠处理信息:
• 总图像数量: {info['total_images']} 张
• 成功对齐: {info['aligned_images']} 张
• 堆叠方法: {info['stacking_params']['method']}
• 星点检测阈值: {info['star_detection_params']['threshold']}
• 最大特征点: {info['alignment_params']['max_features']}
• 输出文件: {Path(self.output_path_var.get()).name}
• 处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            self.result_info_text.configure(state=tk.NORMAL)
            self.result_info_text.delete(1.0, tk.END)
            self.result_info_text.insert(1.0, info_text)
            self.result_info_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            pass
    
    def zoom_in_result(self):
        """放大结果图像"""
        if self.result_image is not None:
            self.result_zoom_factor *= 1.2
            self.update_result_display()
    
    def zoom_out_result(self):
        """缩小结果图像"""
        if self.result_image is not None:
            self.result_zoom_factor /= 1.2
            self.update_result_display()
    
    def zoom_fit_result(self):
        """适应窗口显示结果"""
        if self.result_image is not None:
            canvas_width = self.result_canvas.winfo_width()
            canvas_height = self.result_canvas.winfo_height()
            
            pil_image = Image.fromarray(self.result_image)
            img_width, img_height = pil_image.size
            
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            self.result_zoom_factor = min(scale_x, scale_y)
            
            self.update_result_display()
    
    def update_result_display(self):
        """更新结果显示"""
        if self.result_image is None:
            return
        
        try:
            pil_image = Image.fromarray(self.result_image)
            img_width, img_height = pil_image.size
            
            # 计算新尺寸
            new_width = int(img_width * self.result_zoom_factor)
            new_height = int(img_height * self.result_zoom_factor)
            
            if new_width > 0 and new_height > 0:
                # 缩放图像
                display_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为Tkinter图像
                self.result_tk_image = ImageTk.PhotoImage(display_image)
                
                # 更新Canvas中的图像
                if self.result_canvas_image_id:
                    self.result_canvas.itemconfig(self.result_canvas_image_id, image=self.result_tk_image)
                else:
                    canvas_width = self.result_canvas.winfo_width()
                    canvas_height = self.result_canvas.winfo_height()
                    self.result_canvas_image_id = self.result_canvas.create_image(
                        canvas_width // 2, canvas_height // 2,
                        image=self.result_tk_image,
                        anchor=tk.CENTER
                    )
                
                # 更新缩放标签
                zoom_percent = int(self.result_zoom_factor * 100)
                self.result_zoom_label.configure(text=f"{zoom_percent}%")
                
                # 更新滚动区域
                self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
        
        except Exception as e:
            pass
    
    def save_result(self):
        """保存结果到当前路径"""
        if self.result_image is None:
            messagebox.showerror("错误", "没有可保存的结果")
            return
        
        try:
            output_path = self.output_path_var.get()
            if output_path:
                success = self.stacker.save_result(
                    self.result_image, 
                    output_path,
                    quality=self.quality_var.get()
                )
                
                if success:
                    messagebox.showinfo("成功", f"结果已保存到: {output_path}")
                else:
                    messagebox.showerror("错误", "保存失败")
            else:
                self.save_result_as()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_result_as(self):
        """另存为结果"""
        if self.result_image is None:
            messagebox.showerror("错误", "没有可保存的结果")
            return
        
        filename = filedialog.asksaveasfilename(
            title="保存堆叠结果",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG文件", "*.jpg"),
                ("PNG文件", "*.png"),
                ("TIFF文件", "*.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                success = self.stacker.save_result(
                    self.result_image, 
                    filename,
                    quality=self.quality_var.get()
                )
                
                if success:
                    self.output_path_var.set(filename)
                    messagebox.showinfo("成功", f"结果已保存到: {filename}")
                else:
                    messagebox.showerror("错误", "保存失败")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def open_in_main(self):
        """在主窗口中打开结果"""
        if self.result_image is None:
            messagebox.showerror("错误", "没有可打开的结果")
            return
        
        output_path = self.output_path_var.get()
        if output_path and os.path.exists(output_path) and self.parent:
            try:
                # 如果父窗口有add_image_files方法，调用它
                if hasattr(self.parent, 'add_image_files'):
                    self.parent.add_image_files([output_path])
                    messagebox.showinfo("成功", "结果已在主窗口中打开")
                else:
                    messagebox.showinfo("提示", f"请在主窗口中手动打开: {output_path}")
            except Exception as e:
                messagebox.showerror("错误", f"打开失败: {str(e)}")
        else:
            messagebox.showerror("错误", "请先保存结果")
    
    def open_camera_raw(self):
        """打开Camera Raw处理窗口"""
        try:
            # 检查是否有选中的图像
            selection = self.image_tree.selection()
            if selection:
                # 获取选中图像的路径
                item = self.image_tree.item(selection[0])
                image_index = int(item['values'][0]) - 1  # 序号从1开始，索引从0开始
                if 0 <= image_index < len(self.image_paths):
                    image_path = self.image_paths[image_index]
                    # 打开Camera Raw窗口并加载选中的图像
                    camera_raw_window = CameraRawWindow(self.window, image_path)
                else:
                    # 没有选中图像，打开空的Camera Raw窗口
                    camera_raw_window = CameraRawWindow(self.window)
            else:
                # 没有选中图像，打开空的Camera Raw窗口
                camera_raw_window = CameraRawWindow(self.window)
                
        except Exception as e:
            messagebox.showerror("错误", f"打开Camera Raw失败：{e}")
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.processing_thread and self.processing_thread.is_alive():
            if messagebox.askokcancel("确认", "正在处理中，确定要关闭吗？"):
                self.stacker.cancel_processing()
                self.window.destroy()
        else:
            self.window.destroy()

def main():
    """独立运行星空堆叠工具"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    app = StackingWindow()
    app.window.mainloop()

if __name__ == "__main__":
    main()