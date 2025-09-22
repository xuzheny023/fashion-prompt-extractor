from __future__ import annotations

from typing import Dict, Any

import numpy as np
import cv2
from src.features import extract_features


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def _dominant_color_bgr(img_bgr: np.ndarray, mask: np.ndarray) -> tuple[int, int, int]:
    if img_bgr.size == 0:
        return (128, 128, 128)
    if mask is None:
        mask = np.ones(img_bgr.shape[:2], dtype=np.uint8) * 255
    if mask.dtype != np.uint8:
        m = mask.astype(np.uint8)
    else:
        m = mask
    if m.max() == 1:
        m = (m * 255).astype(np.uint8)
    hist = cv2.calcHist([img_bgr], [0, 1, 2], m, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    idx = np.unravel_index(np.argmax(hist), hist.shape)
    b = int((idx[0] + 0.5) * 32)
    g = int((idx[1] + 0.5) * 32)
    r = int((idx[2] + 0.5) * 32)
    return (r, g, b)


def _simple_color_name(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0, 0]
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])
    if v < 40:
        return "black"
    if v > 220 and s < 30:
        return "white"
    if s < 30:
        return "gray"
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


def compute_region_features(img_bgr: np.ndarray, regions: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Compute lightweight per-region features compatible with fabric_ranker scoring.
    Returns {region_id: {"attrs": {"visual": {...}}}}
    """
    H, W = img_bgr.shape[:2]
    total = float(H * W + 1e-6)
    out: Dict[int, Dict[str, Any]] = {}
    for rid, info in regions.items():
        mask = info.get("mask")
        if mask is None:
            continue
        if mask.dtype != np.uint8:
            m = mask.astype(np.uint8)
        else:
            m = mask
        if m.max() == 1:
            m = (m * 255).astype(np.uint8)
        # Dominant color & coverage
        rgb = _dominant_color_bgr(img_bgr, m)
        color_hex = _rgb_to_hex(rgb)
        color_name = _simple_color_name(rgb)
        area = int(np.count_nonzero(m))
        coverage = float(area) / total
        sheen_proxy = max(0.1, min(0.9, coverage))
        texture_proxy = 1.0 - abs(coverage - 0.5) * 2.0
        texture_proxy = float(max(0.1, min(0.9, texture_proxy)))
        # Unified feature extraction API (compute default feature set)
        feats = extract_features(img_bgr, m)
        out[int(rid)] = {
            "attrs": {
                "visual": {
                    "dominant_color_name": color_name,
                    "dominant_color_hex": color_hex,
                    "coverage_ratio": round(coverage, 4),
                    "sheen_proxy": round(float(sheen_proxy), 4),
                    "texture_proxy": round(float(texture_proxy), 4),
                }
            },
            "features": feats
        }
    return out


