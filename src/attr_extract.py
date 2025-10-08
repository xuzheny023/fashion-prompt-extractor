# -*- coding: utf-8 -*-
# src/attr_extract.py
# -*- coding: utf-8 -*-
"""
Basic visual attribute extraction (based on original image + mask)
鍩虹瑙嗚灞炴€ф彁鍙栵紙鍩轰簬鍘熷浘 + mask锛?- Input: PIL.Image and mask aligned to original size (uint8, 0/255)
- 杈撳叆 PIL.Image 鍜屼笌鍘熷浘绛夊昂瀵稿榻愮殑 mask锛坲int8, 0/255锛?- Output: Only color information (RGB/HEX + simple color names)
- 浠呰緭鍑洪鑹蹭俊鎭紙RGB/HEX + 绠€鍗曡壊鍚嶏級
"""

from typing import Dict, Tuple, Any
import numpy as np
import cv2
from PIL import Image


# -----------------------------
# Utility functions / 宸ュ叿鍑芥暟
# -----------------------------
def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def _apply_mask(img_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Set background to zero, keep foreground pixels / 鎶婅儗鏅疆闆讹紝淇濈暀鍓嶆櫙鍍忕礌"""
    if mask.dtype != np.uint8:
        mask = mask.astype(np.uint8)
    if mask.max() == 1:  # Compatible with 0/1 mask / 鍏煎 0/1 mask
        mask = (mask * 255).astype(np.uint8)
    # Broadcast to three channels / broadcast 鍒颁笁閫氶亾
    m3 = cv2.merge([mask, mask, mask])
    out = cv2.bitwise_and(img_bgr, m3)
    return out

def _dominant_color_bgr(img_bgr: np.ndarray, mask: np.ndarray) -> Tuple[int, int, int]:
    """
    Find dominant color bucket center from 8x8x8 histogram, return (R,G,B)
    8x8x8 鐩存柟鍥炬壘涓昏壊妗朵腑蹇冿紝杩斿洖 (R,G,B)
    """
    if img_bgr.size == 0:
        return (128, 128, 128)
    # Only count foreground / 鍙粺璁′′墠鏅?
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
    闈炰弗鏍艰壊鍚嶆槧灏勶細鎶?RGB 杞?HSV锛屽熀浜?hue/楗卞拰搴?鏄庡害缁欏嚭绮楃暐鑹插悕
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

    # Hue range (OpenCV: 0-179) / hue 鍖洪棿锛圤penCV: 0-179锛?
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
# Main function (public interface) / 涓诲嚱鏁帮紙瀵瑰锛?# -----------------------------
def extract_attributes(image: Image.Image, mask: np.ndarray) -> Dict:
    """
    Entry point: Original PIL image + binary mask aligned to original (0/255)
    鍏ュ彛锛氬師鍥?PIL + 涓庡師鍥惧榻愮殑浜屽€?mask锛?/255锛?    Returns: Dictionary with color-related attributes only
    杩斿洖锛氫粎棰滆壊鐩稿叧鐨勫睘鎬у瓧鍏?    """
    img_bgr = _pil_to_bgr(image)

    dom_rgb = _dominant_color_bgr(img_bgr, mask)  # (R,G,B)
    color_name = _simple_color_name(dom_rgb)
    color_hex = _rgb_to_hex(dom_rgb)

    coverage = _mask_area_ratio(mask)
    # Robust defaults for sheen/texture related placeholders
    # 鎻愪緵绋冲仴鐨勫厜娉?绾圭悊鍗犱綅锛岄伩鍏嶄负0寮曞彂鍒嗘暟鐣稿彉
    sheen_proxy = max(0.1, min(0.9, coverage))
    texture_proxy = 1.0 - abs(coverage - 0.5) * 2.0  # peak at 0.5
    texture_proxy = float(max(0.1, min(0.9, texture_proxy)))

    return {
        "visual": {
            "dominant_color_name": color_name,
            "dominant_color_hex": color_hex,
            "coverage_ratio": round(coverage, 4),
            # Placeholders that downstream scorers may use
            # 渚涗笅娓告墦鍒嗕娇鐢ㄧ殑鍗犱綅鐗瑰緛
            "sheen_proxy": round(float(sheen_proxy), 4),
            "texture_proxy": round(float(texture_proxy), 4),
        }
    }


# -----------------------------
# Localization support / 鏈湴鍖栨敮鎸?# -----------------------------

# Attribute key mappings for localization / 灞炴€ч敭鐨勬湰鍦板寲鏄犲皠
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
        "zh": "颜色代码"
    },
    "coverage_ratio": {
        "en": "Coverage Ratio",
        "zh": "覆盖率"
    }
}

# Color name mappings / 棰滆壊鍚嶇О鏄犲皠
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
    鏈湴鍖栧睘鎬у瓧鍏哥敤浜庢樉绀?
    Args:
        attrs: Original attributes dictionary / 鍘熷灞炴€у瓧鍏?        lang: Language code ('en' or 'zh') / 璇█浠g爜锛?en' 鎴?'zh'锛?
    Returns:
        Localized dictionary with translated keys and color names / 杩斿洖鏈湴鍖栧瓧鍏革紝鍖呭惈缈昏瘧鐨勯敭鍚嶅拰棰滆壊鍚?    """
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
    Get localized color name / 鑾峰彇鏈湴鍖栭鑹插悕绉?
    Args:
        color_name: English color name / 鑻辨枃棰滆壊鍚嶇О
        lang: Language code / 璇█浠g爜

    Returns:
        Localized color name / 鏈湴鍖栭鑹插悕绉?    """
    return COLOR_NAMES.get(color_name, {}).get(lang, color_name)
