#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Camera Raw 风格的图像处理模块
专为天体摄影优化的RAW图像处理工具
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from pathlib import Path
import json
from typing import Dict, Any, Optional, Tuple
import logging

# 尝试导入rawpy用于RAW文件支持
try:
    import rawpy
    RAW_SUPPORT = True
except ImportError:
    RAW_SUPPORT = False
    logging.warning("rawpy未安装，无法处理RAW格式文件")

logger = logging.getLogger(__name__)

class CameraRawProcessor:
    """Camera Raw 风格的图像处理器"""
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.raw_image = None  # rawpy对象
        self.image_path = None
        self.metadata = {}
        
        # 基础调整参数
        self.basic_adjustments = {
            'exposure': 0.0,        # 曝光补偿 (-5.0 到 +5.0)
            'highlights': 0,        # 高光 (-100 到 +100)
            'shadows': 0,           # 阴影 (-100 到 +100)
            'whites': 0,            # 白色 (-100 到 +100)
            'blacks': 0,            # 黑色 (-100 到 +100)
            'contrast': 0,          # 对比度 (-100 到 +100)
            'clarity': 0,           # 清晰度 (-100 到 +100)
            'vibrance': 0,          # 自然饱和度 (-100 到 +100)
            'saturation': 0,        # 饱和度 (-100 到 +100)
        }
        
        # 色彩调整参数
        self.color_adjustments = {
            'temperature': 0,       # 色温 (-2000 到 +2000)
            'tint': 0,             # 色调 (-100 到 +100)
            'hue': 0,              # 色相 (-180 到 +180)
        }
        
        # 细节调整参数
        self.detail_adjustments = {
            'sharpening': 0,        # 锐化 (0 到 100)
            'noise_reduction': 0,   # 降噪 (0 到 100)
            'color_noise_reduction': 0,  # 颜色降噪 (0 到 100)
        }
        
        # 天体摄影专用参数
        self.astro_adjustments = {
            'star_enhancement': 0,   # 星点增强 (0 到 100)
            'background_smoothing': 0,  # 背景平滑 (0 到 100)
            'light_pollution_removal': 0,  # 光污染去除 (0 到 100)
            'nebula_enhancement': 0,     # 星云增强 (0 到 100)
        }
        
        # HSL调整参数 (8个颜色通道)
        self.hsl_adjustments = {
            'red': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'orange': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'yellow': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'green': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'aqua': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'blue': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'purple': {'hue': 0, 'saturation': 0, 'luminance': 0},
            'magenta': {'hue': 0, 'saturation': 0, 'luminance': 0},
        }
        
        # 色调曲线参数
        self.tone_curve = {
            'highlights': 255,
            'lights': 191,
            'darks': 64,
            'shadows': 0,
        }
    
    def load_image(self, image_path: str) -> bool:
        """加载图像文件"""
        try:
            self.image_path = Path(image_path)
            
            # 检查是否为RAW文件
            if self.image_path.suffix.lower() in ['.cr2', '.nef', '.arw', '.dng', '.raf', '.orf']:
                return self._load_raw_image(image_path)
            else:
                return self._load_standard_image(image_path)
                
        except Exception as e:
            logger.error(f"加载图像失败: {e}")
            return False
    
    def _load_raw_image(self, image_path: str) -> bool:
        """加载RAW格式图像"""
        if not RAW_SUPPORT:
            logger.error("rawpy未安装，无法处理RAW文件")
            return False
            
        try:
            self.raw_image = rawpy.imread(image_path)
            
            # 使用默认参数处理RAW图像
            rgb_array = self.raw_image.postprocess(
                use_camera_wb=True,
                half_size=False,
                no_auto_bright=True,
                output_bps=16
            )
            
            # 转换为8位
            rgb_array = (rgb_array / 256).astype(np.uint8)
            
            self.original_image = Image.fromarray(rgb_array)
            self.processed_image = self.original_image.copy()
            
            # 提取元数据
            self._extract_metadata()
            
            logger.info(f"成功加载RAW图像: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载RAW图像失败: {e}")
            return False
    
    def _load_standard_image(self, image_path: str) -> bool:
        """加载标准格式图像"""
        try:
            self.original_image = Image.open(image_path)
            
            # 转换为RGB模式
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')
            
            self.processed_image = self.original_image.copy()
            
            # 提取基本信息
            self.metadata = {
                'format': self.original_image.format,
                'size': self.original_image.size,
                'mode': self.original_image.mode,
            }
            
            logger.info(f"成功加载图像: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载标准图像失败: {e}")
            return False
    
    def _extract_metadata(self):
        """提取图像元数据"""
        if self.raw_image:
            try:
                self.metadata = {
                    'camera_make': getattr(self.raw_image, 'camera_make', 'Unknown'),
                    'camera_model': getattr(self.raw_image, 'camera_model', 'Unknown'),
                    'iso': getattr(self.raw_image, 'camera_iso', 0),
                    'shutter_speed': getattr(self.raw_image, 'camera_shutter', 0),
                    'aperture': getattr(self.raw_image, 'camera_aperture', 0),
                    'focal_length': getattr(self.raw_image, 'camera_focal_length', 0),
                    'white_balance': getattr(self.raw_image, 'camera_whitebalance', [1, 1, 1, 1]),
                    'size': (self.raw_image.sizes.width, self.raw_image.sizes.height),
                }
            except Exception as e:
                logger.warning(f"提取元数据失败: {e}")
                self.metadata = {}
    
    def reset_adjustments(self):
        """重置所有调整参数"""
        for param in self.basic_adjustments:
            self.basic_adjustments[param] = 0
        for param in self.color_adjustments:
            self.color_adjustments[param] = 0
        for param in self.detail_adjustments:
            self.detail_adjustments[param] = 0
        for param in self.astro_adjustments:
            self.astro_adjustments[param] = 0
        
        # 重置HSL调整
        for color in self.hsl_adjustments:
            for param in self.hsl_adjustments[color]:
                self.hsl_adjustments[color][param] = 0
        
        # 重置色调曲线
        self.tone_curve = {
            'highlights': 255,
            'lights': 191,
            'darks': 64,
            'shadows': 0,
        }
    
    def apply_basic_adjustments(self, image: Image.Image) -> Image.Image:
        """应用基础调整"""
        result = image.copy()
        
        # 曝光调整
        if self.basic_adjustments['exposure'] != 0:
            exposure_factor = 2 ** self.basic_adjustments['exposure']
            enhancer = ImageEnhance.Brightness(result)
            result = enhancer.enhance(exposure_factor)
        
        # 对比度调整
        if self.basic_adjustments['contrast'] != 0:
            contrast_factor = 1 + (self.basic_adjustments['contrast'] / 100)
            enhancer = ImageEnhance.Contrast(result)
            result = enhancer.enhance(contrast_factor)
        
        # 饱和度调整
        if self.basic_adjustments['saturation'] != 0:
            saturation_factor = 1 + (self.basic_adjustments['saturation'] / 100)
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(saturation_factor)
        
        # 清晰度调整
        if self.basic_adjustments['clarity'] != 0:
            clarity_factor = self.basic_adjustments['clarity'] / 100
            if clarity_factor > 0:
                # 增加清晰度
                result = result.filter(ImageFilter.UnsharpMask(
                    radius=2, percent=int(clarity_factor * 150), threshold=3
                ))
            else:
                # 减少清晰度（轻微模糊）
                result = result.filter(ImageFilter.GaussianBlur(radius=abs(clarity_factor)))
        
        return result
    
    def apply_color_adjustments(self, image: Image.Image) -> Image.Image:
        """应用色彩调整"""
        if all(v == 0 for v in self.color_adjustments.values()):
            return image
        
        # 转换为numpy数组进行处理
        img_array = np.array(image, dtype=np.float32)
        
        # 色温调整
        if self.color_adjustments['temperature'] != 0:
            temp_factor = self.color_adjustments['temperature'] / 1000.0
            if temp_factor > 0:  # 暖色调
                img_array[:, :, 0] *= (1 + temp_factor * 0.3)  # 增加红色
                img_array[:, :, 2] *= (1 - temp_factor * 0.2)  # 减少蓝色
            else:  # 冷色调
                img_array[:, :, 0] *= (1 + temp_factor * 0.2)  # 减少红色
                img_array[:, :, 2] *= (1 - temp_factor * 0.3)  # 增加蓝色
        
        # 色调调整
        if self.color_adjustments['tint'] != 0:
            tint_factor = self.color_adjustments['tint'] / 100.0
            if tint_factor > 0:  # 品红色调
                img_array[:, :, 0] *= (1 + tint_factor * 0.1)  # 增加红色
                img_array[:, :, 2] *= (1 + tint_factor * 0.1)  # 增加蓝色
            else:  # 绿色调
                img_array[:, :, 1] *= (1 - tint_factor * 0.2)  # 增加绿色
        
        # 限制像素值范围
        img_array = np.clip(img_array, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def apply_astro_adjustments(self, image: Image.Image) -> Image.Image:
        """应用天体摄影专用调整"""
        result = image.copy()
        img_array = np.array(result)
        
        # 星点增强
        if self.astro_adjustments['star_enhancement'] > 0:
            result = self._enhance_stars(result)
        
        # 背景平滑
        if self.astro_adjustments['background_smoothing'] > 0:
            result = self._smooth_background(result)
        
        # 光污染去除
        if self.astro_adjustments['light_pollution_removal'] > 0:
            result = self._remove_light_pollution(result)
        
        # 星云增强
        if self.astro_adjustments['nebula_enhancement'] > 0:
            result = self._enhance_nebula(result)
        
        return result
    
    def _enhance_stars(self, image: Image.Image) -> Image.Image:
        """增强星点"""
        enhancement_factor = self.astro_adjustments['star_enhancement'] / 100.0
        
        # 使用非锐化蒙版增强星点
        return image.filter(ImageFilter.UnsharpMask(
            radius=1, 
            percent=int(enhancement_factor * 200), 
            threshold=10
        ))
    
    def _smooth_background(self, image: Image.Image) -> Image.Image:
        """平滑背景"""
        smoothing_factor = self.astro_adjustments['background_smoothing'] / 100.0
        
        if smoothing_factor > 0:
            # 轻微高斯模糊来平滑背景
            return image.filter(ImageFilter.GaussianBlur(radius=smoothing_factor * 2))
        
        return image
    
    def _remove_light_pollution(self, image: Image.Image) -> Image.Image:
        """去除光污染"""
        removal_factor = self.astro_adjustments['light_pollution_removal'] / 100.0
        
        if removal_factor > 0:
            img_array = np.array(image, dtype=np.float32)
            
            # 简单的光污染去除：减少整体亮度，特别是低亮度区域
            pollution_mask = img_array < (128 * (1 - removal_factor))
            img_array[pollution_mask] *= (1 - removal_factor * 0.5)
            
            img_array = np.clip(img_array, 0, 255)
            return Image.fromarray(img_array.astype(np.uint8))
        
        return image
    
    def _enhance_nebula(self, image: Image.Image) -> Image.Image:
        """增强星云"""
        enhancement_factor = self.astro_adjustments['nebula_enhancement'] / 100.0
        
        if enhancement_factor > 0:
            # 增强对比度和饱和度来突出星云
            enhancer = ImageEnhance.Contrast(image)
            result = enhancer.enhance(1 + enhancement_factor * 0.5)
            
            enhancer = ImageEnhance.Color(result)
            result = enhancer.enhance(1 + enhancement_factor * 0.3)
            
            return result
        
        return image
    
    def process_image(self) -> Optional[Image.Image]:
        """处理图像，应用所有调整"""
        if self.original_image is None:
            return None
        
        try:
            # 从原始图像开始
            result = self.original_image.copy()
            
            # 按顺序应用各种调整
            result = self.apply_basic_adjustments(result)
            result = self.apply_color_adjustments(result)
            result = self.apply_astro_adjustments(result)
            
            self.processed_image = result
            return result
            
        except Exception as e:
            logger.error(f"处理图像失败: {e}")
            return None
    
    def save_preset(self, preset_name: str, file_path: str = None) -> bool:
        """保存调整预设"""
        try:
            preset_data = {
                'name': preset_name,
                'basic_adjustments': self.basic_adjustments.copy(),
                'color_adjustments': self.color_adjustments.copy(),
                'detail_adjustments': self.detail_adjustments.copy(),
                'astro_adjustments': self.astro_adjustments.copy(),
                'hsl_adjustments': self.hsl_adjustments.copy(),
                'tone_curve': self.tone_curve.copy(),
            }
            
            if file_path is None:
                file_path = f"{preset_name}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"预设已保存: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存预设失败: {e}")
            return False
    
    def load_preset(self, file_path: str) -> bool:
        """加载调整预设"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            self.basic_adjustments.update(preset_data.get('basic_adjustments', {}))
            self.color_adjustments.update(preset_data.get('color_adjustments', {}))
            self.detail_adjustments.update(preset_data.get('detail_adjustments', {}))
            self.astro_adjustments.update(preset_data.get('astro_adjustments', {}))
            self.hsl_adjustments.update(preset_data.get('hsl_adjustments', {}))
            self.tone_curve.update(preset_data.get('tone_curve', {}))
            
            logger.info(f"预设已加载: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"加载预设失败: {e}")
            return False
    
    def get_histogram_data(self) -> Dict[str, np.ndarray]:
        """获取直方图数据"""
        if self.processed_image is None:
            return {}
        
        img_array = np.array(self.processed_image)
        
        # 计算RGB直方图
        hist_r = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))[0]
        
        # 计算亮度直方图
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        hist_lum = np.histogram(gray, bins=256, range=(0, 256))[0]
        
        return {
            'red': hist_r,
            'green': hist_g,
            'blue': hist_b,
            'luminance': hist_lum
        }