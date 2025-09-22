from __future__ import annotations

from typing import Tuple

import numpy as np
import cv2

try:
    from src.xutils.lazy import optional_import
except Exception:
    from src.utils.lazy import optional_import  # type: ignore


def _mediapipe_selfie_seg(img_bgr: np.ndarray) -> np.ndarray | None:
    mp = optional_import("mediapipe")
    if mp is None:
        return None
    try:
        RGB = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as seg:
            res = seg.process(RGB)
            if not hasattr(res, "segmentation_mask") or res.segmentation_mask is None:
                return None
            mask_prob = res.segmentation_mask.astype(np.float32)
            mask = (mask_prob >= 0.5).astype(np.uint8) * 255
            return mask
    except Exception:
        return None


def _grabcut_fallback(img_bgr: np.ndarray) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    rect = (1, 1, w - 2, h - 2)
    gc_mask = np.zeros((h, w), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(img_bgr, gc_mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        return mask
    except Exception:
        # ultimate fallback: full foreground
        return np.ones((h, w), dtype=np.uint8) * 255


def get_person_mask(img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Return (person_mask_uint8, method):
    - Try mediapipe SelfieSeg
    - Fallback to GrabCut with full-image rectangle
    """
    if img_bgr is None or not isinstance(img_bgr, np.ndarray):
        raise ValueError("img_bgr must be numpy array")
    m = _mediapipe_selfie_seg(img_bgr)
    if m is not None:
        return m, "mediapipe"
    return _grabcut_fallback(img_bgr), "grabcut"


