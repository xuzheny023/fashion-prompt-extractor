# src/attr_extract.py
# -*- coding: utf-8 -*-
"""
基础视觉属性提取（基于原图 + mask）
- 输入 PIL.Image 和与原图等尺寸对齐的 mask（uint8, 0/255）
- 输出包含：
  - 颜色（RGB/HEX + 简单色名）
  - 廓形（straight / A-line / flare / fitted 粗略）
  - 长度（mini / knee-length / midi / maxi 粗略）
并保留你之前的结构字段，作为兼容占位/半自动填充。
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

def _width_profile(mask: np.ndarray, slices: int = 7) -> np.ndarray:
    """
    计算从上到下若干水平切片的前景宽度，得到廓形宽度剖面。
    """
    H, W = mask.shape[:2]
    ys = np.linspace(0, H - 1, slices).astype(int)
    widths = []
    for y in ys:
        row = mask[y, :]
        xs = np.where(row > 0)[0]
        if xs.size == 0:
            widths.append(0)
        else:
            widths.append(int(xs.max() - xs.min() + 1))
    return np.array(widths, dtype=np.float32)

def _silhouette_from_profile(widths: np.ndarray) -> str:
    """
    非学术启发式：
    - bottom 较 top 明显更宽：flare
    - 逐渐变宽：A-line
    - 宽度基本恒定：straight
    - 宽度总体偏窄：fitted（这里用作“贴身”粗判）
    """
    if widths.size < 3 or widths.max() == 0:
        return "unknown"

    w_top = np.mean(widths[: max(1, len(widths)//3)])
    w_mid = np.mean(widths[len(widths)//3: 2*len(widths)//3])
    w_bot = np.mean(widths[2*len(widths)//3:])

    # 避免除零
    w_top = max(w_top, 1.0)

    growth_bot = (w_bot - w_top) / w_top
    growth_mid = (w_mid - w_top) / w_top
    var_norm = np.std(widths) / max(np.mean(widths), 1.0)

    if growth_bot > 0.35:
        return "flare"
    if growth_mid > 0.2 and growth_bot > 0.2:
        return "A-line"
    if var_norm < 0.12:
        return "straight"
    if np.mean(widths) < 0.35 * np.max(widths):
        return "fitted"

    return "straight"

def _length_estimate(mask: np.ndarray) -> str:
    """
    粗略长度：用前景覆盖高度占整图高度的比例估计。
    受构图影响较大，但在同一数据风格下可作为近似。
    """
    H, W = mask.shape[:2]
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return "unknown"
    height = ys.max() - ys.min() + 1
    ratio = height / H

    # 根据你的示例图的常见构图经验给出阈值，可按需要微调
    if ratio < 0.35:
        return "top-only"
    if ratio < 0.55:
        return "mini"
    if ratio < 0.72:
        return "knee-length"
    if ratio < 0.88:
        return "midi"
    return "maxi"

def _mask_area_ratio(mask: np.ndarray) -> float:
    H, W = mask.shape[:2]
    return float(np.count_nonzero(mask)) / float(H * W + 1e-6)


# -----------------------------
# 主函数（对外）
# -----------------------------
def extract_attributes(image: Image.Image, mask: np.ndarray) -> Dict:
    """
    入口：原图 PIL + 与原图对齐的二值 mask（0/255）
    返回：属性字典（含兼容字段）
    """
    img_bgr = _pil_to_bgr(image)

    # 颜色主色
    dom_rgb = _dominant_color_bgr(img_bgr, mask)  # (R,G,B)
    color_name = _simple_color_name(dom_rgb)
    color_hex = _rgb_to_hex(dom_rgb)

    # 廓形（宽度剖面）
    widths = _width_profile(mask, slices=9)
    silhouette = _silhouette_from_profile(widths)

    # 长度估计
    length_est = _length_estimate(mask)

    # 可作为后续规则/排序的参考指标
    coverage = _mask_area_ratio(mask)

    # ---------------------------------------
    # 兼容你现有下游字段（先给默认/半自动）
    # 这些如果之后接入更强的分类器，再替换即可。
    # ---------------------------------------
    neckline = "unknown"     # 暂无稳定启发式，留空或后续用分类器替换
    sleeves = "sleeveless" if "top-only" in length_est or coverage < 0.18 else "unknown"
    waist   = "fitted" if silhouette in ("fitted", "straight") else "relaxed"
    skirt   = "flare" if silhouette in ("flare", "A-line") else "straight"
    # length 字段沿用我们估计
    length  = length_est

    return {
        # 视觉强化后的新字段
        "visual": {
            "dominant_color_name": color_name,
            "dominant_color_hex": color_hex,
            "silhouette": silhouette,
            "coverage_ratio": round(coverage, 4),
        },
        # 兼容原有字段（可被上面推断部分“半自动”填充）
        "neckline": neckline,
        "sleeves": sleeves,
        "waist": waist,
        "skirt": skirt,
        "length": length,
    }
