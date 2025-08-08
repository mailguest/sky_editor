#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天体摄影图像堆叠模块
支持星空图像的自动对齐和堆叠合并
"""

import numpy as np
from PIL import Image, ImageEnhance
import cv2
import threading
import time
from pathlib import Path
import json
from typing import List, Tuple, Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstroStacker:
    """天体摄影图像堆叠器"""
    
    def __init__(self):
        self.images = []  # 原始图像列表
        self.aligned_images = []  # 对齐后的图像列表
        self.reference_image = None  # 参考图像
        self.star_points = []  # 检测到的星点
        self.progress_callback = None  # 进度回调函数
        self.cancel_flag = False  # 取消标志
        
        # 星点检测参数
        self.star_detection_params = {
            'threshold': 50,  # 星点检测阈值
            'min_area': 3,    # 最小星点面积
            'max_area': 100,  # 最大星点面积
            'gaussian_blur': 1.5,  # 高斯模糊半径
        }
        
        # 图像对齐参数
        self.alignment_params = {
            'max_features': 500,  # 最大特征点数量
            'match_threshold': 0.7,  # 特征匹配阈值
            'ransac_threshold': 5.0,  # RANSAC阈值
        }
        
        # 堆叠参数
        self.stacking_params = {
            'method': 'average',  # 堆叠方法: average, median, maximum, sigma_clip
            'sigma_low': 2.0,     # Sigma裁剪下限
            'sigma_high': 2.0,    # Sigma裁剪上限
            'rejection_ratio': 0.1,  # 拒绝比例
        }
    
    def set_star_detection_params(self, threshold=None, min_area=None, max_area=None, gaussian_blur=None):
        """设置星点检测参数"""
        if threshold is not None:
            self.star_detection_params['threshold'] = threshold
        if min_area is not None:
            self.star_detection_params['min_area'] = min_area
        if max_area is not None:
            self.star_detection_params['max_area'] = max_area
        if gaussian_blur is not None:
            self.star_detection_params['gaussian_blur'] = gaussian_blur
    
    def set_alignment_params(self, max_features=None, match_threshold=None):
        """设置图像对齐参数"""
        if max_features is not None:
            self.alignment_params['max_features'] = max_features
        if match_threshold is not None:
            self.alignment_params['match_threshold'] = match_threshold
    
    def set_stacking_params(self, method=None, sigma_clip=None, sigma_lower=None, sigma_upper=None, rejection_ratio=None):
        """设置图像堆叠参数"""
        if method is not None:
            self.stacking_params['method'] = method
        if sigma_clip is not None:
            self.stacking_params['sigma_clip'] = sigma_clip
        if sigma_lower is not None:
            self.stacking_params['sigma_low'] = sigma_lower
        if sigma_upper is not None:
            self.stacking_params['sigma_high'] = sigma_upper
        if rejection_ratio is not None:
            self.stacking_params['rejection_ratio'] = rejection_ratio
    
    def load_images(self, image_paths: List[str]) -> bool:
        """加载图像文件"""
        try:
            self.images = []
            total = len(image_paths)
            
            for i, path in enumerate(image_paths):
                if self.cancel_flag:
                    return False
                    
                try:
                    # 加载图像
                    img = Image.open(path)
                    
                    # 转换为RGB模式
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 转换为numpy数组
                    img_array = np.array(img)
                    
                    self.images.append({
                        'path': path,
                        'image': img_array,
                        'original': img
                    })
                    
                    if self.progress_callback:
                        self.progress_callback(f"加载图像: {Path(path).name}", (i + 1) / total * 20)
                        
                except Exception as e:
                    logger.error(f"加载图像失败 {path}: {e}")
                    continue
            
            if len(self.images) < 2:
                raise ValueError("至少需要2张图像进行堆叠")
                
            # 设置第一张图像为参考图像
            self.reference_image = self.images[0]['image']
            logger.info(f"成功加载 {len(self.images)} 张图像")
            return True
            
        except Exception as e:
            logger.error(f"加载图像时出错: {e}")
            return False
    
    def detect_stars(self, image: np.ndarray) -> List[Tuple[float, float]]:
        """检测图像中的星点"""
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()
            
            # 高斯模糊减少噪点
            blurred = cv2.GaussianBlur(gray, (0, 0), self.star_detection_params['gaussian_blur'])
            
            # 自适应阈值处理
            _, thresh = cv2.threshold(blurred, self.star_detection_params['threshold'], 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            star_points = []
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 过滤面积不合适的轮廓
                if (self.star_detection_params['min_area'] <= area <= 
                    self.star_detection_params['max_area']):
                    
                    # 计算质心
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = M["m10"] / M["m00"]
                        cy = M["m01"] / M["m00"]
                        star_points.append((cx, cy))
            
            # 按亮度排序，选择最亮的星点
            if len(star_points) > self.alignment_params['max_features']:
                # 计算每个星点的亮度
                star_brightness = []
                for x, y in star_points:
                    x, y = int(x), int(y)
                    if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
                        brightness = float(gray[y, x])
                        star_brightness.append((brightness, (x, y)))
                
                # 按亮度排序并选择前N个
                star_brightness.sort(reverse=True)
                star_points = [point for _, point in star_brightness[:self.alignment_params['max_features']]]
            
            logger.info(f"检测到 {len(star_points)} 个星点")
            return star_points
            
        except Exception as e:
            logger.error(f"星点检测失败: {e}")
            return []
    
    def align_images(self) -> bool:
        """对齐所有图像到参考图像"""
        try:
            if not self.images or self.reference_image is None:
                return False
            
            self.aligned_images = []
            total = len(self.images)
            
            # 检测参考图像的星点
            ref_stars = self.detect_stars(self.reference_image)
            if len(ref_stars) < 10:
                raise ValueError("参考图像中检测到的星点太少，无法进行对齐")
            
            if self.progress_callback:
                self.progress_callback("检测参考图像星点", 25)
            
            for i, img_data in enumerate(self.images):
                if self.cancel_flag:
                    return False
                
                try:
                    current_image = img_data['image']
                    
                    if i == 0:
                        # 参考图像直接添加
                        self.aligned_images.append(current_image)
                        if self.progress_callback:
                            self.progress_callback(f"处理参考图像", 30 + (i / total) * 40)
                        continue
                    
                    # 检测当前图像的星点
                    current_stars = self.detect_stars(current_image)
                    
                    if len(current_stars) < 10:
                        logger.warning(f"图像 {i} 中检测到的星点太少，跳过")
                        continue
                    
                    # 星点匹配
                    transformation_matrix = self.match_stars(ref_stars, current_stars)
                    
                    if transformation_matrix is not None:
                        # 应用变换
                        h, w = self.reference_image.shape[:2]
                        aligned = cv2.warpAffine(current_image, transformation_matrix, (w, h))
                        self.aligned_images.append(aligned)
                        logger.info(f"成功对齐图像 {i}")
                    else:
                        logger.warning(f"图像 {i} 对齐失败，跳过")
                    
                    if self.progress_callback:
                        self.progress_callback(f"对齐图像 {i+1}/{total}", 30 + ((i + 1) / total) * 40)
                        
                except Exception as e:
                    logger.error(f"对齐图像 {i} 时出错: {e}")
                    continue
            
            logger.info(f"成功对齐 {len(self.aligned_images)} 张图像")
            return len(self.aligned_images) >= 2
            
        except Exception as e:
            logger.error(f"图像对齐失败: {e}")
            return False
    
    def match_stars(self, ref_stars: List[Tuple[float, float]], 
                   current_stars: List[Tuple[float, float]]) -> Optional[np.ndarray]:
        """匹配两组星点并计算变换矩阵"""
        try:
            if len(ref_stars) < 3 or len(current_stars) < 3:
                return None
            
            # 转换为numpy数组
            ref_points = np.array(ref_stars, dtype=np.float32)
            cur_points = np.array(current_stars, dtype=np.float32)
            
            # 使用最近邻匹配
            matches = []
            for i, ref_point in enumerate(ref_points):
                min_dist = float('inf')
                best_match = -1
                
                for j, cur_point in enumerate(cur_points):
                    dist = np.linalg.norm(ref_point - cur_point)
                    if dist < min_dist:
                        min_dist = dist
                        best_match = j
                
                # 只保留距离合理的匹配
                if min_dist < 100:  # 像素距离阈值
                    matches.append((i, best_match))
            
            if len(matches) < 3:
                return None
            
            # 提取匹配的点对
            src_pts = np.array([cur_points[m[1]] for m in matches], dtype=np.float32)
            dst_pts = np.array([ref_points[m[0]] for m in matches], dtype=np.float32)
            
            # 计算仿射变换矩阵
            transformation_matrix = cv2.estimateAffinePartial2D(
                src_pts, dst_pts,
                method=cv2.RANSAC,
                ransacReprojThreshold=self.alignment_params['ransac_threshold']
            )[0]
            
            return transformation_matrix
            
        except Exception as e:
            logger.error(f"星点匹配失败: {e}")
            return None
    
    def stack_images(self) -> Optional[np.ndarray]:
        """堆叠对齐后的图像"""
        try:
            if not self.aligned_images:
                return None
            
            if self.progress_callback:
                self.progress_callback("开始图像堆叠", 75)
            
            # 转换为浮点数组以避免溢出
            images_array = np.array(self.aligned_images, dtype=np.float64)
            
            method = self.stacking_params['method']
            
            if method == 'average':
                # 平均堆叠
                result = np.mean(images_array, axis=0)
                
            elif method == 'median':
                # 中位数堆叠
                result = np.median(images_array, axis=0)
                
            elif method == 'maximum':
                # 最大值堆叠
                result = np.max(images_array, axis=0)
                
            elif method == 'sigma_clip':
                # Sigma裁剪堆叠
                result = self.sigma_clip_stack(images_array)
                
            else:
                # 默认使用平均堆叠
                result = np.mean(images_array, axis=0)
            
            # 确保结果在有效范围内
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            if self.progress_callback:
                self.progress_callback("堆叠完成", 95)
            
            logger.info(f"使用 {method} 方法成功堆叠 {len(self.aligned_images)} 张图像")
            return result
            
        except Exception as e:
            logger.error(f"图像堆叠失败: {e}")
            return None
    
    def sigma_clip_stack(self, images_array: np.ndarray) -> np.ndarray:
        """Sigma裁剪堆叠算法"""
        try:
            # 计算初始平均值和标准差
            mean = np.mean(images_array, axis=0)
            std = np.std(images_array, axis=0)
            
            # 创建掩码，排除异常值
            sigma_low = self.stacking_params['sigma_low']
            sigma_high = self.stacking_params['sigma_high']
            
            lower_bound = mean - sigma_low * std
            upper_bound = mean + sigma_high * std
            
            # 扩展维度以便广播
            lower_bound = np.expand_dims(lower_bound, axis=0)
            upper_bound = np.expand_dims(upper_bound, axis=0)
            
            # 创建有效像素掩码
            valid_mask = (images_array >= lower_bound) & (images_array <= upper_bound)
            
            # 计算加权平均
            masked_images = np.where(valid_mask, images_array, 0)
            valid_count = np.sum(valid_mask, axis=0)
            
            # 避免除零
            valid_count = np.where(valid_count == 0, 1, valid_count)
            
            result = np.sum(masked_images, axis=0) / valid_count
            
            return result
            
        except Exception as e:
            logger.error(f"Sigma裁剪堆叠失败: {e}")
            return np.mean(images_array, axis=0)
    
    def enhance_result(self, image: np.ndarray) -> np.ndarray:
        """增强堆叠结果"""
        try:
            # 转换为PIL图像进行增强
            pil_image = Image.fromarray(image)
            
            # 轻微增强对比度
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(1.1)
            
            # 轻微增强锐度
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.05)
            
            return np.array(enhanced)
            
        except Exception as e:
            logger.error(f"图像增强失败: {e}")
            return image
    
    def process_stack(self, image_paths: List[str], 
                     progress_callback=None) -> Optional[np.ndarray]:
        """完整的堆叠处理流程"""
        try:
            self.progress_callback = progress_callback
            self.cancel_flag = False
            
            if self.progress_callback:
                self.progress_callback("开始处理", 0)
            
            # 1. 加载图像
            if not self.load_images(image_paths):
                return None
            
            # 2. 对齐图像
            if not self.align_images():
                return None
            
            # 3. 堆叠图像
            result = self.stack_images()
            if result is None:
                return None
            
            # 4. 增强结果
            enhanced_result = self.enhance_result(result)
            
            if self.progress_callback:
                self.progress_callback("处理完成", 100)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"堆叠处理失败: {e}")
            return None
    
    def cancel_processing(self):
        """取消处理"""
        self.cancel_flag = True
    
    def get_stacking_info(self) -> Dict[str, Any]:
        """获取堆叠信息"""
        return {
            'total_images': len(self.images),
            'aligned_images': len(self.aligned_images),
            'star_detection_params': self.star_detection_params,
            'alignment_params': self.alignment_params,
            'stacking_params': self.stacking_params,
        }
    
    def save_result(self, result: np.ndarray, output_path: str, 
                   quality: int = 95) -> bool:
        """保存堆叠结果"""
        try:
            # 转换为PIL图像
            pil_image = Image.fromarray(result)
            
            # 保存图像
            if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                pil_image.save(output_path, 'JPEG', quality=quality, optimize=True)
            else:
                pil_image.save(output_path, quality=quality, optimize=True)
            
            logger.info(f"堆叠结果已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存结果失败: {e}")
            return False

# 工具函数
def estimate_processing_time(num_images: int, image_size: Tuple[int, int]) -> float:
    """估算处理时间（秒）"""
    # 基于图像数量和尺寸的简单估算
    base_time = num_images * 2  # 每张图像基础处理时间
    size_factor = (image_size[0] * image_size[1]) / (1920 * 1080)  # 相对于1080p的尺寸因子
    return base_time * size_factor

def validate_images_for_stacking(image_paths: List[str]) -> Tuple[bool, str]:
    """验证图像是否适合堆叠"""
    try:
        if len(image_paths) < 2:
            return False, "至少需要2张图像进行堆叠"
        
        # 检查第一张图像获取基准尺寸
        first_img = Image.open(image_paths[0])
        base_size = first_img.size
        first_img.close()
        
        # 检查所有图像尺寸是否一致
        for path in image_paths[1:]:
            try:
                img = Image.open(path)
                if img.size != base_size:
                    img.close()
                    return False, f"图像尺寸不一致: {Path(path).name}"
                img.close()
            except Exception as e:
                return False, f"无法打开图像: {Path(path).name}"
        
        return True, "图像验证通过"
        
    except Exception as e:
        return False, f"验证失败: {str(e)}"

# 主程序入口
if __name__ == "__main__":
    import tkinter as tk
    from image_viewer import ImageViewer
    
    # 创建主窗口
    root = tk.Tk()
    root.title("Sky Editor - 星空图像处理工具")
    root.geometry("1200x800")
    
    # 创建应用程序
    app = ImageViewer(root)
    
    # 启动主循环
    root.mainloop()