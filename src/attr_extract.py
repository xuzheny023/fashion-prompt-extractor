# src/attr_extract.py
# -*- coding: utf-8 -*-
"""
Basic visual attribute extraction (based on original image + mask)
基础视觉属性提取（基于原图 + mask）
- Input: PIL.Image and mask aligned to original size (uint8, 0/255)
- 输入 PIL.Image 和与原图等尺寸对齐的 mask（uint8, 0/255）
- Output: Only color information (RGB/HEX + simple color names)
- 仅输出颜色信息（RGB/HEX + 简单色名）
"""

from typing import Dict, Tuple, Any
import numpy as np
import cv2
from PIL import Image


# -----------------------------
# Utility functions / 工具函数
# -----------------------------
def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def _apply_mask(img_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Set background to zero, keep foreground pixels / 把背景置零，保留前景像素"""
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)
    if mask.max() == 1:  # Compatible with 0/1 mask / 兼容 0/1 mask
        mask = (mask * 255).astype(np.uint8)
    # Broadcast to three channels / broadcast 到三通道
    m3 = cv2.merge([mask, mask, mask])
    out = cv2.bitwise_and(img_bgr, m3)
    return out

def _dominant_color_bgr(img_bgr: np.ndarray, mask: np.ndarray) -> Tuple[int, int, int]:
    """
    Find dominant color bucket center from 8x8x8 histogram, return (R,G,B)
    8x8x8 直方图找主色桶中心，返回 (R,G,B)
    """
    if img_bgr.size == 0:
        return (128, 128, 128)
    # Only count foreground / 只统计前景
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
    Non-strict color name mapping: Convert RGB to HSV, give rough color names based on hue/saturation/brightness
    非严格色名映射：把 RGB 转 HSV，基于 hue/饱和度/明度给出粗略色名
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

    # Hue range (OpenCV: 0-179) / hue 区间（OpenCV: 0-179）
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
# Main function (public interface) / 主函数（对外）
# -----------------------------
def extract_attributes(image: Image.Image, mask: np.ndarray) -> Dict:
    """
    Entry point: Original PIL image + binary mask aligned to original (0/255)
    入口：原图 PIL + 与原图对齐的二值 mask（0/255）
    Returns: Dictionary with color-related attributes only
    返回：仅颜色相关的属性字典
    """
    img_bgr = _pil_to_bgr(image)

    dom_rgb = _dominant_color_bgr(img_bgr, mask)  # (R,G,B)
    color_name = _simple_color_name(dom_rgb)
    color_hex = _rgb_to_hex(dom_rgb)

    coverage = _mask_area_ratio(mask)
    # Robust defaults for sheen/texture related placeholders
    # 提供稳健的光泽/纹理占位，避免为0引发分数畸变
    sheen_proxy = max(0.1, min(0.9, coverage))
    texture_proxy = 1.0 - abs(coverage - 0.5) * 2.0  # peak at 0.5
    texture_proxy = float(max(0.1, min(0.9, texture_proxy)))

    return {
        "visual": {
            "dominant_color_name": color_name,
            "dominant_color_hex": color_hex,
            "coverage_ratio": round(coverage, 4),
            # Placeholders that downstream scorers may use
            # 供下游打分使用的占位特征
            "sheen_proxy": round(float(sheen_proxy), 4),
            "texture_proxy": round(float(texture_proxy), 4),
        }
    }


# -----------------------------
# Localization support / 本地化支持
# -----------------------------

# Attribute key mappings for localization / 属性键的本地化映射
ATTR_KEYS = {
    "visual": {
        "en": "Visual",
        "zh": "视觉"
    },
    "dominant_color_name": {
        "en": "Dominant Color",
        "zh": "主色调"
    },
    "dominant_color_hex": {
        "en": "Color Code",
        "zh": "色号"
    },
    "coverage_ratio": {
        "en": "Coverage Ratio",
        "zh": "覆盖率"
    }
}

# Color name mappings / 颜色名称映射
COLOR_NAMES = {
    "black": {"en": "Black", "zh": "黑色"},
    "white": {"en": "White", "zh": "白色"},
    "gray": {"en": "Gray", "zh": "灰色"},
    "red": {"en": "Red", "zh": "红色"},
    "orange": {"en": "Orange", "zh": "橙色"},
    "yellow": {"en": "Yellow", "zh": "黄色"},
    "green": {"en": "Green", "zh": "绿色"},
    "cyan": {"en": "Cyan", "zh": "青色"},
    "blue": {"en": "Blue", "zh": "蓝色"},
    "purple": {"en": "Purple", "zh": "紫色"},
    "unknown": {"en": "Unknown", "zh": "未知"}
}


def localize_attrs(attrs: Dict, lang: str = "en") -> Dict[str, Any]:
    """
    Localize attribute dictionary for display purposes
    本地化属性字典用于显示
    
    Args:
        attrs: Original attributes dictionary / 原始属性字典
        lang: Language code ('en' or 'zh') / 语言代码（'en' 或 'zh'）
    
    Returns:
        Localized dictionary with translated keys and color names / 返回本地化字典，包含翻译的键名和颜色名
    """
    localized = {}
    
    for key, value in attrs.items():
        # Get localized key name
        localized_key = ATTR_KEYS.get(key, {}).get(lang, key)
        
        if isinstance(value, dict):
            # Recursively localize nested dictionaries
            localized[localized_key] = localize_attrs(value, lang)
        else:
            # Handle color names specially
            if key == "dominant_color_name" and isinstance(value, str):
                # Translate color name
                color_translation = COLOR_NAMES.get(value, {}).get(lang, value)
                localized[localized_key] = color_translation
            else:
                # Keep other values as-is
                localized[localized_key] = value
    
    return localized


def get_color_name_localized(color_name: str, lang: str = "en") -> str:
    """
    Get localized color name / 获取本地化颜色名称
    
    Args:
        color_name: English color name / 英文颜色名称
        lang: Language code / 语言代码
    
    Returns:
        Localized color name / 本地化颜色名称
    """
    return COLOR_NAMES.get(color_name, {}).get(lang, color_name)
