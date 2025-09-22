from __future__ import annotations

import numpy as np
import cv2

try:
    from src.xutils.constants import SMALL_COMPONENT_AREA
except Exception:
    from src.utils.constants import SMALL_COMPONENT_AREA  # type: ignore


def _skin_mask(img_bgr: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    # HSV skin range (rough)
    lower_hsv = np.array([0, 30, 60], dtype=np.uint8)
    upper_hsv = np.array([20, 180, 255], dtype=np.uint8)
    m1 = cv2.inRange(hsv, lower_hsv, upper_hsv)
    # YCrCb skin range (rough)
    lower_y = np.array([0, 133, 77], dtype=np.uint8)
    upper_y = np.array([255, 173, 127], dtype=np.uint8)
    m2 = cv2.inRange(ycrcb, lower_y, upper_y)
    skin = cv2.bitwise_and(m1, m2)
    return skin


def _hair_mask(img_bgr: np.ndarray, skin_mask: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    dark = (v < 60).astype(np.uint8) * 255
    low_sat = (s < 50).astype(np.uint8) * 255
    cand = cv2.bitwise_and(dark, low_sat)
    cand = cv2.bitwise_and(cand, cv2.bitwise_not(skin_mask))
    # Keep larger connected components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats((cand > 0).astype(np.uint8), 8)
    out = np.zeros_like(cand)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= SMALL_COMPONENT_AREA:
            out[labels == i] = 255
    return out


def _remove_small(mask: np.ndarray, min_area: int = SMALL_COMPONENT_AREA) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8), 8)
    out = np.zeros_like(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            out[labels == i] = 255
    return out


def build_clothing_mask(img_bgr: np.ndarray, person_mask: np.ndarray | None) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    if person_mask is None or not isinstance(person_mask, np.ndarray) or person_mask.size == 0:
        pm = np.ones((h, w), dtype=np.uint8) * 255
    else:
        pm = person_mask
        if pm.dtype != np.uint8:
            pm = (pm > 0).astype(np.uint8) * 255
        if pm.shape[:2] != (h, w):
            pm = cv2.resize(pm, (w, h), interpolation=cv2.INTER_NEAREST)

    skin = _skin_mask(img_bgr)
    hair = _hair_mask(img_bgr, skin)

    # Start from person, subtract skin & hair, then close and clean small regions
    cloth = cv2.bitwise_and(pm, cv2.bitwise_not(skin))
    cloth = cv2.bitwise_and(cloth, cv2.bitwise_not(hair))
    cloth = cv2.morphologyEx(cloth, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
    cloth = _remove_small(cloth, SMALL_COMPONENT_AREA)
    return cloth


