#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Raw 用户界面
类似Adobe Camera Raw的图像处理界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import threading
import os
from pathlib import Path
import json
import time
from typing import Optional, Dict, Any

from .processor import CameraRawProcessor

class CameraRawWindow:
    """Camera Raw 处理窗口"""
    
    def __init__(self, parent=None, image_path: str = None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Sky Editor - Camera Raw")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # Camera Raw 处理器
        self.processor = CameraRawProcessor()
        
        # UI 变量
        self.preview_image = None
        self.preview_label = None
        self.histogram_canvas = None
        self.auto_preview = tk.BooleanVar(value=True)
        self.zoom_factor = 1.0
        self.preview_size = (400, 300)
        
        # 性能优化变量
        self.update_timer = None
        self.update_delay = 300  # 延迟300ms更新
        self.is_dragging = False
        self.last_update_time = 0
        self.processing_thread = None
        self.preview_quality = 'high'  # 'high' 或 'low'
        self.low_quality_size = (200, 150)  # 拖动时的低质量预览尺寸
        
        # 参数变量
        self.setup_parameter_variables()
        
        # 设置UI
        self.setup_ui()
        
        # 如果提供了图像路径，则加载图像
        if image_path:
            self.load_image(image_path)
        
        # 绑定关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_parameter_variables(self):
        """设置参数变量"""
        # 基础调整变量
        self.exposure_var = tk.DoubleVar(value=0.0)
        self.highlights_var = tk.IntVar(value=0)
        self.shadows_var = tk.IntVar(value=0)
        self.whites_var = tk.IntVar(value=0)
        self.blacks_var = tk.IntVar(value=0)
        self.contrast_var = tk.IntVar(value=0)
        self.clarity_var = tk.IntVar(value=0)
        self.vibrance_var = tk.IntVar(value=0)
        self.saturation_var = tk.IntVar(value=0)
        
        # 色彩调整变量
        self.temperature_var = tk.IntVar(value=0)
        self.tint_var = tk.IntVar(value=0)
        self.hue_var = tk.IntVar(value=0)
        
        # 细节调整变量
        self.sharpening_var = tk.IntVar(value=0)
        self.noise_reduction_var = tk.IntVar(value=0)
        self.color_noise_reduction_var = tk.IntVar(value=0)
        
        # 天体摄影专用变量
        self.star_enhancement_var = tk.IntVar(value=0)
        self.background_smoothing_var = tk.IntVar(value=0)
        self.light_pollution_removal_var = tk.IntVar(value=0)
        self.nebula_enhancement_var = tk.IntVar(value=0)
        
        # 绑定变量变化事件
        self.bind_variable_changes()
    
    def bind_variable_changes(self):
        """绑定变量变化事件"""
        variables = [
            self.exposure_var, self.highlights_var, self.shadows_var,
            self.whites_var, self.blacks_var, self.contrast_var,
            self.clarity_var, self.vibrance_var, self.saturation_var,
            self.temperature_var, self.tint_var, self.hue_var,
            self.sharpening_var, self.noise_reduction_var, self.color_noise_reduction_var,
            self.star_enhancement_var, self.background_smoothing_var,
            self.light_pollution_removal_var, self.nebula_enhancement_var
        ]
        
        for var in variables:
            var.trace('w', self.on_parameter_change)
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左右分割
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：图像预览和直方图
        self.setup_preview_panel(paned_window)
        
        # 右侧：调整面板
        self.setup_adjustment_panel(paned_window)
        
        # 底部：控制栏
        self.setup_control_bar(main_frame)
    
    def setup_preview_panel(self, parent):
        """设置预览面板"""
        preview_frame = ttk.Frame(parent)
        parent.add(preview_frame, weight=2)
        
        # 工具栏
        toolbar = ttk.Frame(preview_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="打开图像", command=self.open_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="重置", command=self.reset_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(toolbar, text="自动预览", variable=self.auto_preview).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(toolbar, text="更新预览", command=self.update_preview_async).pack(side=tk.LEFT, padx=(0, 5))
        
        # 性能设置
        perf_frame = ttk.Frame(toolbar)
        perf_frame.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(perf_frame, text="响应速度:").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="平衡")
        delay_combo = ttk.Combobox(perf_frame, textvariable=self.delay_var, 
                                  values=["快速", "平衡", "流畅"], width=8, state="readonly")
        delay_combo.pack(side=tk.LEFT, padx=(5, 0))
        delay_combo.bind("<<ComboboxSelected>>", self.on_delay_change)
        
        # 缩放控制
        zoom_frame = ttk.Frame(toolbar)
        zoom_frame.pack(side=tk.RIGHT)
        ttk.Label(zoom_frame, text="缩放:").pack(side=tk.LEFT)
        zoom_scale = ttk.Scale(zoom_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, 
                              command=self.on_zoom_change, length=100)
        zoom_scale.set(1.0)
        zoom_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        # 图像预览区域
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动区域
        canvas = tk.Canvas(preview_container, bg='gray20')
        h_scrollbar = ttk.Scrollbar(preview_container, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=canvas.yview)
        
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # 预览标签
        self.preview_label = ttk.Label(canvas, text="请打开一张图像", anchor=tk.CENTER)
        canvas.create_window(0, 0, window=self.preview_label, anchor=tk.NW)
        
        # 布局滚动区域
        canvas.grid(row=0, column=0, sticky=tk.NSEW)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # 直方图区域
        histogram_frame = ttk.LabelFrame(preview_frame, text="直方图", padding=5)
        histogram_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.histogram_canvas = tk.Canvas(histogram_frame, height=100, bg='black')
        self.histogram_canvas.pack(fill=tk.X)
    
    def setup_adjustment_panel(self, parent):
        """设置调整面板"""
        adjustment_frame = ttk.Frame(parent)
        parent.add(adjustment_frame, weight=1)
        
        # 创建笔记本控件
        notebook = ttk.Notebook(adjustment_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基础调整标签页
        self.setup_basic_tab(notebook)
        
        # 色彩调整标签页
        self.setup_color_tab(notebook)
        
        # 细节调整标签页
        self.setup_detail_tab(notebook)
        
        # 天体摄影标签页
        self.setup_astro_tab(notebook)
        
        # 预设管理标签页
        self.setup_preset_tab(notebook)
    
    def setup_basic_tab(self, notebook):
        """设置基础调整标签页"""
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基础")
        
        # 创建滚动区域
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 曝光组
        exposure_group = ttk.LabelFrame(scrollable_frame, text="曝光", padding=10)
        exposure_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(exposure_group, "曝光", self.exposure_var, -5.0, 5.0, 0.1, 0)
        self.create_slider(exposure_group, "高光", self.highlights_var, -100, 100, 1, 1)
        self.create_slider(exposure_group, "阴影", self.shadows_var, -100, 100, 1, 2)
        self.create_slider(exposure_group, "白色", self.whites_var, -100, 100, 1, 3)
        self.create_slider(exposure_group, "黑色", self.blacks_var, -100, 100, 1, 4)
        
        # 色调组
        tone_group = ttk.LabelFrame(scrollable_frame, text="色调", padding=10)
        tone_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(tone_group, "对比度", self.contrast_var, -100, 100, 1, 0)
        self.create_slider(tone_group, "清晰度", self.clarity_var, -100, 100, 1, 1)
        self.create_slider(tone_group, "自然饱和度", self.vibrance_var, -100, 100, 1, 2)
        self.create_slider(tone_group, "饱和度", self.saturation_var, -100, 100, 1, 3)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_color_tab(self, notebook):
        """设置色彩调整标签页"""
        color_frame = ttk.Frame(notebook)
        notebook.add(color_frame, text="色彩")
        
        # 白平衡组
        wb_group = ttk.LabelFrame(color_frame, text="白平衡", padding=10)
        wb_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(wb_group, "色温", self.temperature_var, -2000, 2000, 10, 0)
        self.create_slider(wb_group, "色调", self.tint_var, -100, 100, 1, 1)
        
        # 色彩组
        color_group = ttk.LabelFrame(color_frame, text="色彩调整", padding=10)
        color_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(color_group, "色相", self.hue_var, -180, 180, 1, 0)
    
    def setup_detail_tab(self, notebook):
        """设置细节调整标签页"""
        detail_frame = ttk.Frame(notebook)
        notebook.add(detail_frame, text="细节")
        
        # 锐化组
        sharp_group = ttk.LabelFrame(detail_frame, text="锐化", padding=10)
        sharp_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(sharp_group, "锐化", self.sharpening_var, 0, 100, 1, 0)
        
        # 降噪组
        noise_group = ttk.LabelFrame(detail_frame, text="降噪", padding=10)
        noise_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(noise_group, "明度降噪", self.noise_reduction_var, 0, 100, 1, 0)
        self.create_slider(noise_group, "颜色降噪", self.color_noise_reduction_var, 0, 100, 1, 1)
    
    def setup_astro_tab(self, notebook):
        """设置天体摄影标签页"""
        astro_frame = ttk.Frame(notebook)
        notebook.add(astro_frame, text="天体摄影")
        
        # 星点增强组
        star_group = ttk.LabelFrame(astro_frame, text="星点处理", padding=10)
        star_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(star_group, "星点增强", self.star_enhancement_var, 0, 100, 1, 0)
        
        # 背景处理组
        bg_group = ttk.LabelFrame(astro_frame, text="背景处理", padding=10)
        bg_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(bg_group, "背景平滑", self.background_smoothing_var, 0, 100, 1, 0)
        self.create_slider(bg_group, "光污染去除", self.light_pollution_removal_var, 0, 100, 1, 1)
        
        # 星云增强组
        nebula_group = ttk.LabelFrame(astro_frame, text="星云处理", padding=10)
        nebula_group.pack(fill=tk.X, pady=(0, 10))
        
        self.create_slider(nebula_group, "星云增强", self.nebula_enhancement_var, 0, 100, 1, 0)
    
    def setup_preset_tab(self, notebook):
        """设置预设管理标签页"""
        preset_frame = ttk.Frame(notebook)
        notebook.add(preset_frame, text="预设")
        
        # 预设列表
        preset_list_frame = ttk.LabelFrame(preset_frame, text="预设列表", padding=10)
        preset_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 预设列表框
        self.preset_listbox = tk.Listbox(preset_list_frame, height=10)
        preset_scroll = ttk.Scrollbar(preset_list_frame, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        self.preset_listbox.configure(yscrollcommand=preset_scroll.set)
        
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preset_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 预设操作按钮
        preset_buttons = ttk.Frame(preset_frame)
        preset_buttons.pack(fill=tk.X)
        
        ttk.Button(preset_buttons, text="加载预设", command=self.load_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_buttons, text="保存预设", command=self.save_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_buttons, text="删除预设", command=self.delete_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_buttons, text="刷新列表", command=self.refresh_preset_list).pack(side=tk.RIGHT)
        
        # 加载预设列表
        self.refresh_preset_list()
    
    def create_slider(self, parent, label, variable, min_val, max_val, resolution, row):
        """创建滑块控件"""
        ttk.Label(parent, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, pady=2)
        
        scale = ttk.Scale(parent, from_=min_val, to=max_val, variable=variable, 
                         orient=tk.HORIZONTAL, length=200)
        scale.grid(row=row, column=1, sticky=tk.EW, padx=(10, 5), pady=2)
        
        # 绑定拖动事件
        scale.bind("<Button-1>", self.on_drag_start)
        scale.bind("<ButtonRelease-1>", self.on_drag_end)
        scale.bind("<B1-Motion>", self.on_dragging)
        
        # 数值标签
        value_label = ttk.Label(parent, text=str(variable.get()))
        value_label.grid(row=row, column=2, pady=2)
        
        # 更新数值标签
        def update_label(*args):
            if isinstance(variable.get(), float):
                value_label.configure(text=f"{variable.get():.1f}")
            else:
                value_label.configure(text=str(variable.get()))
        
        variable.trace('w', update_label)
        
        # 重置按钮
        reset_btn = ttk.Button(parent, text="↺", width=3, 
                              command=lambda: variable.set(0))
        reset_btn.grid(row=row, column=3, padx=(5, 0), pady=2)
        
        parent.grid_columnconfigure(1, weight=1)
    
    def setup_control_bar(self, parent):
        """设置控制栏"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 左侧：图像信息
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(side=tk.LEFT)
        
        self.info_label = ttk.Label(info_frame, text="未加载图像")
        self.info_label.pack()
        
        # 右侧：操作按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="导出图像", command=self.export_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="应用到堆叠", command=self.apply_to_stacking).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="关闭", command=self.on_closing).pack(side=tk.LEFT)
    
    def open_image(self):
        """打开图像文件"""
        file_types = [
            ("所有支持的格式", "*.jpg *.jpeg *.png *.tiff *.tif *.cr2 *.nef *.arw *.dng"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("TIFF文件", "*.tiff *.tif"),
            ("RAW文件", "*.cr2 *.nef *.arw *.dng"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择图像文件",
            filetypes=file_types
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, image_path: str):
        """加载图像"""
        try:
            if self.processor.load_image(image_path):
                # 更新信息标签
                metadata = self.processor.metadata
                info_text = f"图像: {Path(image_path).name}"
                if 'size' in metadata:
                    info_text += f" | 尺寸: {metadata['size'][0]}x{metadata['size'][1]}"
                if 'camera_model' in metadata:
                    info_text += f" | 相机: {metadata['camera_model']}"
                
                self.info_label.configure(text=info_text)
                
                # 使用异步更新预览
                self.update_preview_async()
                
                messagebox.showinfo("成功", "图像加载成功！")
            else:
                messagebox.showerror("错误", "加载图像失败！")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载图像时出错：{e}")
    
    def on_parameter_change(self, *args):
        """参数变化时的回调 - 使用延迟更新机制"""
        # 更新处理器参数
        self.update_processor_parameters()
        
        # 如果启用自动预览，则使用延迟更新
        if self.auto_preview.get():
            self.schedule_delayed_update()
    
    def update_processor_parameters(self):
        """更新处理器参数"""
        # 基础调整
        self.processor.basic_adjustments.update({
            'exposure': self.exposure_var.get(),
            'highlights': self.highlights_var.get(),
            'shadows': self.shadows_var.get(),
            'whites': self.whites_var.get(),
            'blacks': self.blacks_var.get(),
            'contrast': self.contrast_var.get(),
            'clarity': self.clarity_var.get(),
            'vibrance': self.vibrance_var.get(),
            'saturation': self.saturation_var.get(),
        })
        
        # 色彩调整
        self.processor.color_adjustments.update({
            'temperature': self.temperature_var.get(),
            'tint': self.tint_var.get(),
            'hue': self.hue_var.get(),
        })
        
        # 细节调整
        self.processor.detail_adjustments.update({
            'sharpening': self.sharpening_var.get(),
            'noise_reduction': self.noise_reduction_var.get(),
            'color_noise_reduction': self.color_noise_reduction_var.get(),
        })
        
        # 天体摄影调整
        self.processor.astro_adjustments.update({
            'star_enhancement': self.star_enhancement_var.get(),
            'background_smoothing': self.background_smoothing_var.get(),
            'light_pollution_removal': self.light_pollution_removal_var.get(),
            'nebula_enhancement': self.nebula_enhancement_var.get(),
        })
    
    def on_drag_start(self, event):
        """拖动开始事件"""
        self.is_dragging = True
        self.preview_quality = 'low'  # 切换到低质量预览
    
    def on_dragging(self, event):
        """拖动中事件"""
        # 在拖动过程中，使用更短的延迟
        if self.auto_preview.get():
            # 取消之前的定时器
            if self.update_timer is not None:
                self.window.after_cancel(self.update_timer)
            
            # 设置更短的延迟（100ms）
            self.update_timer = self.window.after(100, self.delayed_update_callback)
    
    def on_drag_end(self, event):
        """拖动结束事件"""
        self.is_dragging = False
        self.preview_quality = 'high'  # 切换回高质量预览
        
        # 拖动结束后立即进行高质量更新
        if self.auto_preview.get():
            # 取消之前的定时器
            if self.update_timer is not None:
                self.window.after_cancel(self.update_timer)
            
            # 立即更新高质量预览
            self.window.after(50, self.delayed_update_callback)
    
    def on_delay_change(self, event=None):
        """响应速度设置变化"""
        delay_setting = self.delay_var.get()
        if delay_setting == "快速":
            self.update_delay = 100  # 100ms延迟，响应快但可能卡顿
        elif delay_setting == "平衡":
            self.update_delay = 300  # 300ms延迟，平衡性能和响应
        elif delay_setting == "流畅":
            self.update_delay = 600  # 600ms延迟，更流畅但响应慢
    
    def schedule_delayed_update(self):
        """安排延迟更新"""
        # 取消之前的定时器
        if self.update_timer is not None:
            self.window.after_cancel(self.update_timer)
        
        # 设置新的定时器
        self.update_timer = self.window.after(self.update_delay, self.delayed_update_callback)
    
    def delayed_update_callback(self):
        """延迟更新回调"""
        self.update_timer = None
        self.update_preview_async()
    
    def update_preview_async(self):
        """异步更新预览"""
        if self.processor.original_image is None:
            return
        
        # 如果已有处理线程在运行，则跳过
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        # 启动新的处理线程
        self.processing_thread = threading.Thread(target=self._process_and_update_preview)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def _process_and_update_preview(self):
        """在后台线程中处理图像并更新预览"""
        try:
            # 处理图像
            processed_image = self.processor.process_image()
            if processed_image is None:
                return
            
            # 根据当前质量设置选择预览尺寸
            if self.preview_quality == 'low':
                preview_size = self.low_quality_size
            else:
                preview_size = self.preview_size
            
            # 调整预览大小
            preview_image = processed_image.copy()
            preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # 应用缩放
            if self.zoom_factor != 1.0:
                new_size = (int(preview_image.width * self.zoom_factor),
                           int(preview_image.height * self.zoom_factor))
                preview_image = preview_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 在主线程中更新UI
            self.window.after(0, lambda: self._update_preview_ui(preview_image))
            
        except Exception as e:
            print(f"后台处理预览失败: {e}")
    
    def _update_preview_ui(self, preview_image):
        """在主线程中更新预览UI"""
        try:
            # 转换为PhotoImage
            self.preview_image = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=self.preview_image, text="")
            
            # 更新直方图
            self.update_histogram()
            
        except Exception as e:
            print(f"更新预览UI失败: {e}")
    
    def update_preview(self):
        """更新图像预览"""
        if self.processor.original_image is None:
            return
        
        try:
            # 处理图像
            processed_image = self.processor.process_image()
            if processed_image is None:
                return
            
            # 调整预览大小
            preview_image = processed_image.copy()
            preview_image.thumbnail(self.preview_size, Image.Resampling.LANCZOS)
            
            # 应用缩放
            if self.zoom_factor != 1.0:
                new_size = (int(preview_image.width * self.zoom_factor),
                           int(preview_image.height * self.zoom_factor))
                preview_image = preview_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            self.preview_image = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=self.preview_image, text="")
            
            # 更新直方图
            self.update_histogram()
            
        except Exception as e:
            print(f"更新预览失败: {e}")
    
    def update_histogram(self):
        """更新直方图"""
        if self.histogram_canvas is None:
            return
        
        try:
            hist_data = self.processor.get_histogram_data()
            if not hist_data:
                return
            
            # 清除画布
            self.histogram_canvas.delete("all")
            
            canvas_width = self.histogram_canvas.winfo_width()
            canvas_height = self.histogram_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # 绘制RGB直方图
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                if color in hist_data:
                    hist = hist_data[color]
                    max_val = np.max(hist) if np.max(hist) > 0 else 1
                    
                    for j in range(len(hist)):
                        x = j * canvas_width / 256
                        height = (hist[j] / max_val) * canvas_height * 0.8
                        y = canvas_height - height
                        
                        self.histogram_canvas.create_line(
                            x, canvas_height, x, y,
                            fill=color, width=1
                        )
            
        except Exception as e:
            print(f"更新直方图失败: {e}")
    
    def on_zoom_change(self, value):
        """缩放变化回调"""
        self.zoom_factor = float(value)
        # 使用延迟更新机制
        if self.auto_preview.get():
            self.schedule_delayed_update()
    
    def reset_all(self):
        """重置所有参数"""
        # 重置所有变量
        variables = [
            (self.exposure_var, 0.0),
            (self.highlights_var, 0),
            (self.shadows_var, 0),
            (self.whites_var, 0),
            (self.blacks_var, 0),
            (self.contrast_var, 0),
            (self.clarity_var, 0),
            (self.vibrance_var, 0),
            (self.saturation_var, 0),
            (self.temperature_var, 0),
            (self.tint_var, 0),
            (self.hue_var, 0),
            (self.sharpening_var, 0),
            (self.noise_reduction_var, 0),
            (self.color_noise_reduction_var, 0),
            (self.star_enhancement_var, 0),
            (self.background_smoothing_var, 0),
            (self.light_pollution_removal_var, 0),
            (self.nebula_enhancement_var, 0),
        ]
        
        for var, default_value in variables:
            var.set(default_value)
        
        # 重置处理器
        self.processor.reset_adjustments()
        
        # 使用异步更新预览
        self.update_preview_async()
    
    def save_preset(self):
        """保存预设"""
        preset_name = tk.simpledialog.askstring("保存预设", "请输入预设名称:")
        if preset_name:
            try:
                preset_path = Path("assets/presets/camera_raw") / f"{preset_name}.json"
                preset_path.parent.mkdir(exist_ok=True)
                
                if self.processor.save_preset(preset_name, str(preset_path)):
                    messagebox.showinfo("成功", f"预设 '{preset_name}' 已保存！")
                    self.refresh_preset_list()
                else:
                    messagebox.showerror("错误", "保存预设失败！")
            except Exception as e:
                messagebox.showerror("错误", f"保存预设时出错：{e}")
    
    def load_preset(self):
        """加载预设"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个预设！")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        preset_path = Path("assets/presets/camera_raw") / f"{preset_name}.json"
        
        try:
            if self.processor.load_preset(str(preset_path)):
                # 更新UI变量
                self.update_ui_from_processor()
                messagebox.showinfo("成功", f"预设 '{preset_name}' 已加载！")
            else:
                messagebox.showerror("错误", "加载预设失败！")
        except Exception as e:
            messagebox.showerror("错误", f"加载预设时出错：{e}")
    
    def delete_preset(self):
        """删除预设"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个预设！")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        
        if messagebox.askyesno("确认", f"确定要删除预设 '{preset_name}' 吗？"):
            try:
                preset_path = Path("assets/presets/camera_raw") / f"{preset_name}.json"
                if preset_path.exists():
                    preset_path.unlink()
                    messagebox.showinfo("成功", f"预设 '{preset_name}' 已删除！")
                    self.refresh_preset_list()
                else:
                    messagebox.showerror("错误", "预设文件不存在！")
            except Exception as e:
                messagebox.showerror("错误", f"删除预设时出错：{e}")
    
    def refresh_preset_list(self):
        """刷新预设列表"""
        self.preset_listbox.delete(0, tk.END)
        
        preset_dir = Path("assets/presets/camera_raw")
        if preset_dir.exists():
            for preset_file in preset_dir.glob("*.json"):
                self.preset_listbox.insert(tk.END, preset_file.stem)
    
    def update_ui_from_processor(self):
        """从处理器更新UI变量"""
        # 基础调整
        basic = self.processor.basic_adjustments
        self.exposure_var.set(basic.get('exposure', 0))
        self.highlights_var.set(basic.get('highlights', 0))
        self.shadows_var.set(basic.get('shadows', 0))
        self.whites_var.set(basic.get('whites', 0))
        self.blacks_var.set(basic.get('blacks', 0))
        self.contrast_var.set(basic.get('contrast', 0))
        self.clarity_var.set(basic.get('clarity', 0))
        self.vibrance_var.set(basic.get('vibrance', 0))
        self.saturation_var.set(basic.get('saturation', 0))
        
        # 色彩调整
        color = self.processor.color_adjustments
        self.temperature_var.set(color.get('temperature', 0))
        self.tint_var.set(color.get('tint', 0))
        self.hue_var.set(color.get('hue', 0))
        
        # 细节调整
        detail = self.processor.detail_adjustments
        self.sharpening_var.set(detail.get('sharpening', 0))
        self.noise_reduction_var.set(detail.get('noise_reduction', 0))
        self.color_noise_reduction_var.set(detail.get('color_noise_reduction', 0))
        
        # 天体摄影调整
        astro = self.processor.astro_adjustments
        self.star_enhancement_var.set(astro.get('star_enhancement', 0))
        self.background_smoothing_var.set(astro.get('background_smoothing', 0))
        self.light_pollution_removal_var.set(astro.get('light_pollution_removal', 0))
        self.nebula_enhancement_var.set(astro.get('nebula_enhancement', 0))
    
    def export_image(self):
        """导出处理后的图像"""
        if self.processor.processed_image is None:
            messagebox.showwarning("警告", "没有可导出的图像！")
            return
        
        file_types = [
            ("JPEG文件", "*.jpg"),
            ("PNG文件", "*.png"),
            ("TIFF文件", "*.tiff"),
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="导出图像",
            filetypes=file_types,
            defaultextension=".jpg"
        )
        
        if file_path:
            try:
                self.processor.processed_image.save(file_path, quality=95)
                messagebox.showinfo("成功", f"图像已导出到：{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出图像失败：{e}")
    
    def apply_to_stacking(self):
        """应用到堆叠工具"""
        if self.processor.processed_image is None:
            messagebox.showwarning("警告", "没有可应用的图像！")
            return
        
        # 这里可以实现将处理后的图像传递给堆叠工具的逻辑
        messagebox.showinfo("提示", "此功能将在后续版本中实现")
    
    def on_closing(self):
        """关闭窗口"""
        # 清理定时器
        if self.update_timer is not None:
            self.window.after_cancel(self.update_timer)
            self.update_timer = None
        
        # 等待处理线程结束
        if self.processing_thread and self.processing_thread.is_alive():
            # 给线程一些时间完成
            self.processing_thread.join(timeout=1.0)
        
        self.window.destroy()

# 导入简化对话框
import tkinter.simpledialog

def main():
    """主函数"""
    app = CameraRawWindow()
    app.window.mainloop()

if __name__ == "__main__":
    main()