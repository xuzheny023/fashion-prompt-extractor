# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, Any, Iterable, Optional, Tuple

import numpy as np
import cv2

_GABOR_CACHE = {}

def _get_gabor_kernel(ksize=(11, 11), sigma=4.0, theta=0.0, lambd=8.0, gamma=0.5, psi=0):
    key = (ksize, float(sigma), float(theta), float(lambd), float(gamma), int(psi))
    k = _GABOR_CACHE.get(key)
    if k is None:
        k = cv2.getGaborKernel(ksize, sigma, theta, lambd, gamma, psi, ktype=cv2.CV_32F)
        _GABOR_CACHE[key] = k
    return k


def _ensure_mask(mask: Optional[np.ndarray], shape: Tuple[int, int]) -> np.ndarray:
    if mask is None:
        return np.ones(shape, dtype=np.uint8) * 255
    if mask.dtype != np.uint8:
        m = (mask > 0).astype(np.uint8) * 255
    else:
        m = mask
    if m.max() == 1:
        m = (m * 255).astype(np.uint8)
    if m.shape[:2] != shape:
        m = cv2.resize(m, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
    return m


def _masked(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return cv2.bitwise_and(img, mask)
    m3 = cv2.merge([mask, mask, mask])
    return cv2.bitwise_and(img, m3)


def _feat_specular_ratio(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    v_masked = _masked(v, mask)
    thr = max(200, int(np.percentile(v_masked[v_masked > 0], 90)) if np.count_nonzero(v_masked) else 200)
    high = np.count_nonzero(v_masked >= thr)
    total = np.count_nonzero(mask)
    return float(high) / float(total + 1e-6)


def _feat_highlight_blobs(img_bgr: np.ndarray, mask: np.ndarray) -> Tuple[int, float]:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(gray, mask)
    thr = max(200, int(np.percentile(g[g > 0], 85)) if np.count_nonzero(g) else 200)
    _, binv = cv2.threshold(g, thr, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(binv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_high = sum(int(cv2.contourArea(c)) for c in cnts)
    area_total = int(np.count_nonzero(mask))
    return len(cnts), float(area_high) / float(area_total + 1e-6)


def _feat_laplacian_var(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    lap = cv2.Laplacian(g, cv2.CV_32F)
    return float(np.var(lap))


def _feat_lbp_distance(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    # Simplified 8-neighbor LBP and chi2 distance to a uniform reference
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    h, w = g.shape
    if h < 3 or w < 3:
        return 0.0
    lbp = np.zeros((h - 2, w - 2), dtype=np.uint8)
    c = g[1:-1, 1:-1]
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    for i, (dy, dx) in enumerate(offsets):
        nb = g[1 + dy:h - 1 + dy, 1 + dx:w - 1 + dx]
        lbp |= ((nb >= c).astype(np.uint8) << i)
    hist = cv2.calcHist([lbp], [0], None, [256], [0, 256]).astype(np.float32).flatten()
    s = float(hist.sum() + 1e-6)
    hist /= s
    ref = np.full(256, 1.0 / 256.0, dtype=np.float32)
    chi2 = 0.5 * float(np.sum(((hist - ref) ** 2) / (hist + ref + 1e-6)))
    return chi2


def _feat_gabor_anisotropy(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    thetas = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]
    acc = []
    for th in thetas:
        k = _get_gabor_kernel((11, 11), 4.0, th, 8.0, 0.5, 0)
        r = cv2.filter2D(g, cv2.CV_32F, k)
        acc.append(float(np.mean(np.abs(r))))
    if not acc:
        return 0.0
    vmin, vmax = float(min(acc)), float(max(acc))
    return float(0.0 if vmax <= 1e-6 else (vmax - vmin) / (vmax + 1e-6))


def _feat_fft_main_dir(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    g = cv2.GaussianBlur(g, (0, 0), 1.0)
    f = np.fft.fftshift(np.fft.fft2(g))
    mag = np.log1p(np.abs(f))
    # Simple orientation proxy: compare vertical vs horizontal energy
    v = float(np.sum(mag, axis=0).mean())
    h = float(np.sum(mag, axis=1).mean())
    # Return angle proxy (0 for horizontal dominance, 90 for vertical)
    return 90.0 * float(h >= v)


def _feat_color_hue(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0]
    hh = _masked(h, mask)
    if np.count_nonzero(mask) == 0:
        return 0.0
    return float(np.sum(hh) / float(np.count_nonzero(mask)))


def _feat_fft_peak(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    f = np.fft.fftshift(np.fft.fft2(g))
    mag = np.abs(f)
    h, w = mag.shape
    # Zero-out a small DC window
    c0, c1 = h // 2, w // 2
    dc = 5
    mag[c0 - dc:c0 + dc + 1, c1 - dc:c1 + dc + 1] = 0
    peak = float(np.max(mag)) if mag.size else 0.0
    mean = float(np.mean(mag)) if mag.size else 0.0
    if mean <= 1e-6:
        return 0.0
    return float(peak / (mean + 1e-6))


def _feat_transparency(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    # Approximate as hole ratio inside bounding rect
    h, w = mask.shape[:2]
    ys, xs = np.where(mask > 0)
    if ys.size == 0:
        return 0.0
    y0, y1 = int(ys.min()), int(ys.max())
    x0, x1 = int(xs.min()), int(xs.max())
    roi = mask[y0:y1 + 1, x0:x1 + 1]
    zeros = int(np.count_nonzero(roi == 0))
    total = int(roi.size)
    return float(zeros) / float(total + 1e-6)


def _feat_edge_sharp(img_bgr: np.ndarray, mask: np.ndarray) -> float:
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = _masked(g, mask)
    sx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(sx * sx + sy * sy)
    return float(np.mean(np.abs(mag)))


def extract_features(
    img_bgr: np.ndarray,
    mask: Optional[np.ndarray] = None,
    *,
    feature_list: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    feature_list=None 鈫?璁＄畻榛樿鍏ㄩ噺锛涗紶鍒楄〃 鈫?鍙畻闇€瑕佺殑锛堢敤浜庡眬閮ㄧ粏鍖栵級銆?
    杩斿洖 dict 鐨?key 鍥哄畾锛?
    ["color_hue","spec_ratio","hl_blob_area","lap_var","lbp_dist",
     "gabor_aniso","fft_dir_deg","fft_peak","transparency","edge_sharp"]
    """
    H, W = img_bgr.shape[:2]
    m = _ensure_mask(mask, (H, W))
    # Shared grayscale and FFT magnitude cache within this call
    g_base = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g_base = _masked(g_base, m)
    _cache: Dict[str, Any] = {}

    def _fft_abs():
        if "fft_abs" in _cache:
            return _cache["fft_abs"]
        g = cv2.GaussianBlur(g_base, (0, 0), 1.0)
        f = np.fft.fftshift(np.fft.fft2(g))
        mag = np.abs(f)
        _cache["fft_abs"] = mag
        return mag
    # Compute highlight metrics once
    def _hl_area():
        _, ar = _feat_highlight_blobs(img_bgr, m)
        return ar

    feats_all = {
        "color_hue": lambda: _feat_color_hue(img_bgr, m),
        "spec_ratio": lambda: _feat_specular_ratio(img_bgr, m),
        "hl_blob_area": _hl_area,
        "lap_var": lambda: _feat_laplacian_var(img_bgr, m),
        "lbp_dist": lambda: _feat_lbp_distance(img_bgr, m),
        "gabor_aniso": lambda: _feat_gabor_anisotropy(img_bgr, m),
        # Use shared FFT magnitude for both features
        "fft_dir_deg": lambda: (lambda mag: (
            90.0 * float(np.sum(np.log1p(mag), axis=1).mean() >= np.sum(np.log1p(mag), axis=0).mean())
        ))(_fft_abs()),
        "fft_peak": lambda: (lambda mag: (
            0.0 if float(np.mean(mag)) <= 1e-6 else float(
                (np.max((lambda mm: (
                    # zero out DC window
                    lambda c0, c1, dc: (mm.__setitem__((slice(c0-dc, c0+dc+1), slice(c1-dc, c1+dc+1)), 0) or mm)
                )(int(mm.shape[0]/2), int(mm.shape[1]/2), 5)) or mm)(mag))
            ) / (float(np.mean(mag)) + 1e-6)
        ))(_fft_abs()),
        "transparency": lambda: _feat_transparency(img_bgr, m),
        "edge_sharp": lambda: _feat_edge_sharp(img_bgr, m),
    }
    keys = list(feats_all.keys()) if feature_list is None else [k for k in feature_list if k in feats_all]
    out: Dict[str, Any] = {}
    for k in keys:
        try:
            out[k] = feats_all[k]()
        except Exception:
            # Robust defaults
            out[k] = 0.0
    return out


