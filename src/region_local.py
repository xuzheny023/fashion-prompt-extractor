# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple, Dict, Any, List, Optional

import numpy as np
import cv2


def get_local_window(
    img_bgr: np.ndarray,
    x: int,
    y: int,
    r: int,
    *,
    cloth_mask: Optional[np.ndarray] = None,
    letterbox: Tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Tuple[np.ndarray, np.ndarray, Tuple[int, int, int, int]]:
    """
    Crop a local window around (x, y) with radius r.
    Returns (win_bgr, win_mask, bbox), bbox=(x0,y0,w,h). Mask is 255 inside the window.
    """
    h, w = img_bgr.shape[:2]
    r = max(0, int(r))
    # Adjust for letterbox offsets (left, top, right, bottom)
    lx, ly, rx, by = [int(v) for v in letterbox]
    xa = int(x) - max(0, lx)
    ya = int(y) - max(0, ly)
    # Clamp to image coordinates
    xa = max(0, min(w - 1, xa))
    ya = max(0, min(h - 1, ya))
    # Iteratively shrink r to fit if needed
    rr = int(r)
    while True:
        x0 = max(0, xa - rr)
        y0 = max(0, ya - rr)
        x1 = min(w, xa + rr + 1)
        y1 = min(h, ya + rr + 1)
        if x1 > x0 and y1 > y0:
            break
        if rr <= 1:
            break
        rr -= 1
    win = img_bgr[y0:y1, x0:x1]
    if win.size == 0:
        return np.zeros((0, 0, 3), dtype=np.uint8), np.zeros((0, 0), dtype=np.uint8), (x0, y0, max(0, x1 - x0), max(0, y1 - y0))
    # Window mask: prefer cloth_mask crop if provided
    if cloth_mask is not None and isinstance(cloth_mask, np.ndarray) and cloth_mask.size:
        cm = cloth_mask
        if cm.dtype != np.uint8:
            cm = (cm > 0).astype(np.uint8) * 255
        if cm.shape[:2] != (h, w):
            # Best-effort resize
            cm = cv2.resize(cm, (w, h), interpolation=cv2.INTER_NEAREST)
        mask = cm[y0:y1, x0:x1]
    else:
        mask = np.ones((y1 - y0, x1 - x0), dtype=np.uint8) * 255
    bbox = (x0, y0, x1 - x0, y1 - y0)
    return win, mask, bbox


def fuse_region_and_local_scores(
    region_score_dict: Dict[str, Dict[str, Any]] | List,
    local_score_dict: Dict[str, Dict[str, Any]] | List,
    alpha: float = 0.7,
) -> Dict[str, Dict[str, Any]]:
    """
    Fuse two score dictionaries with weighted sum on 'total'.
    Inputs can be dicts {fabric:{'total':..,'parts':{..},'explain':[...]}},
    or lists of (name, score[, ...]).
    Returns normalized dict keyed by fabric.
    """
    def to_dict(obj) -> Dict[str, Dict[str, Any]]:
        if isinstance(obj, dict):
            return obj
        out: Dict[str, Dict[str, Any]] = {}
        if isinstance(obj, list):
            for it in obj:
                if isinstance(it, (list, tuple)) and len(it) >= 2:
                    out[str(it[0])] = {"total": float(it[1]), "parts": {}, "explain": []}
        return out

    A = to_dict(region_score_dict)
    B = to_dict(local_score_dict)
    fused: Dict[str, Dict[str, Any]] = {}
    keys = set(A.keys()) | set(B.keys())
    a = float(max(0.0, min(1.0, alpha)))
    b = 1.0 - a
    for k in keys:
        ta = float(A.get(k, {}).get("total", 0.0))
        tb = float(B.get(k, {}).get("total", 0.0))
        parts = {}
        parts.update(A.get(k, {}).get("parts", {}))
        for pk, pv in B.get(k, {}).get("parts", {}).items():
            if pk in parts and isinstance(parts[pk], (int, float)) and isinstance(pv, (int, float)):
                parts[pk] = a * float(parts[pk]) + b * float(pv)
            else:
                parts[pk] = pv
        explain = []
        explain.extend(A.get(k, {}).get("explain", []))
        explain.extend(B.get(k, {}).get("explain", []))
        fused[k] = {"total": a * ta + b * tb, "parts": parts, "explain": explain}
    return fused


def choose_features_for_local() -> List[str]:
    """
    Return a default list of features to recompute on local window.
    """
    return ["specular", "highlight_blobs", "gabor", "fft_dir", "laplacian", "lbp_dist"]


