from __future__ import annotations

import math
from typing import Dict, Tuple, Any, Optional

import numpy as np
import cv2
try:
    from src.xutils.constants import SMALL_COMPONENT_AREA
except Exception:
    from src.utils.constants import SMALL_COMPONENT_AREA  # type: ignore


def _ensure_uint8_gray(img_bgr: np.ndarray) -> np.ndarray:
    if img_bgr is None:
        raise ValueError("img_bgr is None")
    if img_bgr.dtype != np.uint8:
        img = np.clip(img_bgr, 0, 255).astype(np.uint8)
    else:
        img = img_bgr
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _apply_fg_weight(img_bgr: np.ndarray, fg_mask: Optional[np.ndarray]) -> np.ndarray:
    """
    If foreground mask provided, softly darken background to bias segmentation toward FG.
    """
    if fg_mask is None or not isinstance(fg_mask, np.ndarray) or fg_mask.size == 0:
        return img_bgr
    if fg_mask.dtype != np.uint8:
        mask = (fg_mask > 0).astype(np.uint8) * 255
    else:
        mask = (fg_mask > 0).astype(np.uint8) * 255
    mask3 = cv2.merge([mask, mask, mask])
    blurred = cv2.GaussianBlur(img_bgr, (0, 0), 3)
    # Keep FG as is; darken BG
    out = np.where(mask3 > 0, img_bgr, (blurred * 0.5).astype(np.uint8))
    return out


def _slic_labels(img_bgr: np.ndarray, n_segments: int, compactness: float) -> Optional[np.ndarray]:
    try:
        from skimage.segmentation import slic
    except Exception:
        return None
    try:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        labels = slic(img_rgb, n_segments=int(n_segments), compactness=float(compactness), start_label=0)
        if labels is None:
            return None
        return labels.astype(np.int32)
    except Exception:
        return None


def _grid_labels(h: int, w: int, rows: int, cols: int) -> np.ndarray:
    rows = max(1, int(rows))
    cols = max(1, int(cols))
    labels = -np.ones((h, w), dtype=np.int32)
    idx = 0
    ys = np.linspace(0, h, rows + 1, dtype=np.int32)
    xs = np.linspace(0, w, cols + 1, dtype=np.int32)
    for i in range(rows):
        for j in range(cols):
            y0, y1 = ys[i], ys[i + 1]
            x0, x1 = xs[j], xs[j + 1]
            labels[y0:y1, x0:x1] = idx
            idx += 1
    return labels


def _labels_to_regions(labels: np.ndarray, min_area: int = 0) -> Dict[int, Dict[str, Any]]:
    h, w = labels.shape
    regions: Dict[int, Dict[str, Any]] = {}
    unique_ids = np.unique(labels)
    for rid in unique_ids:
        if rid < 0:
            continue
        mask = (labels == rid).astype(np.uint8) * 255
        area = int(np.count_nonzero(mask))
        if area == 0:
            continue
        x, y, bw, bh = cv2.boundingRect(mask)
        if min_area and area < min_area:
            # Small region is still created; merging handled outside.
            pass
        regions[int(rid)] = {"mask": mask, "bbox": (x, y, bw, bh), "area": area}
    return regions


def _merge_small_regions(labels: np.ndarray, min_area: int = SMALL_COMPONENT_AREA) -> np.ndarray:
    if min_area <= 0:
        return labels
    h, w = labels.shape
    regions = _labels_to_regions(labels)
    # Build neighbors by 4-connectivity
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    for rid, info in list(regions.items()):
        if info["area"] >= min_area:
            continue
        mask = info["mask"] // 255
        dil = cv2.dilate(mask.astype(np.uint8), kernel, iterations=1)
        # Neighbor labels around small region
        ys, xs = np.where(dil > 0)
        neighbor_ids = set()
        for y, x in zip(ys, xs):
            ly = max(0, min(h - 1, y))
            lx = max(0, min(w - 1, x))
            nid = labels[ly, lx]
            if nid >= 0 and nid != rid and regions.get(int(nid), {}).get("area", 0) >= min_area:
                neighbor_ids.add(int(nid))
        if not neighbor_ids:
            # Fallback: choose any different neighbor
            ys2, xs2 = np.where(cv2.dilate(mask.astype(np.uint8), np.ones((3, 3), np.uint8), 1) > 0)
            for y2, x2 in zip(ys2, xs2):
                nid = labels[y2, x2]
                if nid >= 0 and nid != rid:
                    neighbor_ids.add(int(nid))
                    break
        if neighbor_ids:
            # Merge into the largest neighbor
            target = max(neighbor_ids, key=lambda k: regions.get(k, {}).get("area", 0))
            labels[labels == rid] = target
    return labels


def build_regions(
    img_bgr: np.ndarray,
    method: str = "slic",
    slic_n_segments: int = 150,
    slic_compactness: float = 10.0,
    grid_rows: int = 9,
    grid_cols: int = 9,
    fg_mask: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Build region labels using SLIC (preferred) or grid (fallback). Optionally bias by fg_mask.

    Returns dict:
    {
      "method": "slic|grid",
      "labels": int32 label map (same HxW as input; -1 means background if you pre-apply it),
      "regions": {id: {"mask": uint8, "bbox": (x,y,w,h), "area": int}},
      "meta": {"slic_params": {...}, "grid_params": {...}}
    }
    """
    if img_bgr is None or not isinstance(img_bgr, np.ndarray):
        raise ValueError("img_bgr must be a numpy array")

    h, w = img_bgr.shape[:2]
    img_in = img_bgr
    if fg_mask is not None:
        img_in = _apply_fg_weight(img_bgr, fg_mask)

    chosen = method
    labels: Optional[np.ndarray] = None

    # Dynamic fallback: if foreground coverage too low, use grid directly
    fg_coverage = None
    if fg_mask is not None and isinstance(fg_mask, np.ndarray) and fg_mask.size == (h * w):
        if fg_mask.dtype != np.uint8:
            m = (fg_mask > 0).astype(np.uint8)
        else:
            m = (fg_mask > 0).astype(np.uint8)
        fg_coverage = float(np.count_nonzero(m)) / float(h * w)

    if method == "slic" and (fg_coverage is not None and fg_coverage < 0.15):
        labels = _grid_labels(h, w, grid_rows, grid_cols)
        chosen = "grid"
    elif method == "slic":
        labels = _slic_labels(img_in, slic_n_segments, slic_compactness)
        if labels is None:
            chosen = "grid"

    if labels is None:
        labels = _grid_labels(h, w, grid_rows, grid_cols)
        chosen = "grid"

    # If fg_mask provided, set background to -1 to mark as no-foreground
    if fg_mask is not None and isinstance(fg_mask, np.ndarray) and fg_mask.size == labels.size:
        bg = (fg_mask <= 0)
        labels = labels.copy()
        labels[bg] = -1

    # Merge very small regions to neighbors to stabilize downstream features
    labels_merged = _merge_small_regions(labels.copy(), min_area=64)
    regions = _labels_to_regions(labels_merged)

    return {
        "method": chosen,
        "labels": labels_merged,
        "regions": regions,
        "meta": {
            "slic_params": {"n_segments": int(slic_n_segments), "compactness": float(slic_compactness)},
            "grid_params": {"rows": int(grid_rows), "cols": int(grid_cols)},
        },
    }


def locate_region(labels: np.ndarray, x: int, y: int) -> Optional[int]:
    """
    Given a label map and an (x,y) coordinate (image-space), return region id or None.
    """
    if labels is None or not isinstance(labels, np.ndarray):
        return None
    h, w = labels.shape[:2]
    if not (0 <= x < w and 0 <= y < h):
        return None
    rid = int(labels[y, x])
    return None if rid < 0 else rid


