# src/attr_extract.py
# -*- coding: utf-8 -*-
"""
基础视觉属性提取（基于原图 + mask）
- 输入 PIL.Image 和与原图等尺寸对齐的 mask（uint8, 0/255）
- 仅输出颜色信息（RGB/HEX + 简单色名）
"""

from typing import Dict, Tuple
import numpy as np
import cv2
from PIL import Image


# -----------------------------
# 工具函数
# -----------------------------
def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def _apply_mask(img_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """把背景置零，保留前景像素"""
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)
    if mask.max() == 1:  # 兼容 0/1 mask
        mask = (mask * 255).astype(np.uint8)
    # broadcast 到三通道
    m3 = cv2.merge([mask, mask, mask])
    out = cv2.bitwise_and(img_bgr, m3)
    return out

def _dominant_color_bgr(img_bgr: np.ndarray, mask: np.ndarray) -> Tuple[int, int, int]:
    """
    8x8x8 直方图找主色桶中心，返回 (R,G,B)
    """
    if img_bgr.size == 0:
        return (128, 128, 128)
    # 只统计前景
    hist = cv2.calcHist([img_bgr], [0, 1, 2], mask, [8, 8, 8],
                        [0, 256, 0, 256, 0, 256])
    idx = np.unravel_index(np.argmax(hist), hist.shape)
    b = int((idx[0] + 0.5) * 32)
    g = int((idx[1] + 0.5) * 32)
    r = int((idx[2] + 0.5) * 32)
    return (r, g, b)

def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def _simple_color_name(rgb: Tuple[int, int, int]) -> str:
    """
    非严格色名映射：把 RGB 转 HSV，基于 hue/饱和度/明度给出粗略色名。
    """
    r, g, b = rgb
    hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0, 0]
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

    if v < 40:
        return "black"
    if v > 220 and s < 30:
        return "white"
    if s < 30:
        return "gray"

    # hue 区间（OpenCV: 0-179）
    if h < 10 or h >= 170:
        return "red"
    if 10 <= h < 20:
        return "orange"
    if 20 <= h < 35:
        return "yellow"
    if 35 <= h < 85:
        return "green"
    if 85 <= h < 110:
        return "cyan"
    if 110 <= h < 140:
        return "blue"
    if 140 <= h < 170:
        return "purple"

    return "unknown"

def _mask_area_ratio(mask: np.ndarray) -> float:
    H, W = mask.shape[:2]
    return float(np.count_nonzero(mask)) / float(H * W + 1e-6)


# -----------------------------
# 主函数（对外）
# -----------------------------
def extract_attributes(image: Image.Image, mask: np.ndarray) -> Dict:
    """
    入口：原图 PIL + 与原图对齐的二值 mask（0/255）
    返回：仅颜色相关的属性字典
    """
    img_bgr = _pil_to_bgr(image)

    dom_rgb = _dominant_color_bgr(img_bgr, mask)  # (R,G,B)
    color_name = _simple_color_name(dom_rgb)
    color_hex = _rgb_to_hex(dom_rgb)

    coverage = _mask_area_ratio(mask)

    return {
        "visual": {
            "dominant_color_name": color_name,
            "dominant_color_hex": color_hex,
            "coverage_ratio": round(coverage, 4),
        }
    }
