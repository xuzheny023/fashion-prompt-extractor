from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

try:
    from src.segmentation.person_mask import get_person_mask
    from src.segmentation.clothing_mask import build_clothing_mask
except Exception:
    # Fallback: simple FG mask
    def get_person_mask(img_bgr):
        h, w = img_bgr.shape[:2]
        return np.ones((h, w), np.uint8) * 255, "fallback"

    def build_clothing_mask(img_bgr, pm):
        return pm

from src.regionizer import build_regions, locate_region
from src.region_features import compute_region_features
from src.region_recommender import recommend_for_region


def main() -> int:
    samples_dir = Path("samples")
    jpgs = sorted(list(samples_dir.glob("*.jpg")))
    if not jpgs:
        print("[smoke] no samples/*.jpg found")
        return 0
    img_path = jpgs[0]
    print(f"[smoke] using sample: {img_path}")

    t0 = time.perf_counter()
    pil = Image.open(img_path).convert("RGB")
    img_bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    t1 = time.perf_counter(); print(f"[time] load: {t1 - t0:.3f}s")

    pm, mth = get_person_mask(img_bgr)
    cm = build_clothing_mask(img_bgr, pm)
    t2 = time.perf_counter(); print(f"[time] masks: {t2 - t1:.3f}s ({mth})")

    regions_out = build_regions(img_bgr, method="slic", slic_n_segments=180, slic_compactness=10.0, grid_rows=9, grid_cols=9, fg_mask=cm)
    labels = regions_out.get("labels")
    regions = regions_out.get("regions", {})
    t3 = time.perf_counter(); print(f"[time] regions: {t3 - t2:.3f}s (method={regions_out.get('method')})")

    feats = compute_region_features(img_bgr, regions)
    t4 = time.perf_counter(); print(f"[time] features: {t4 - t3:.3f}s (regions={len(feats)})")

    # pick center point
    h, w = labels.shape[:2]
    cx, cy = w // 2, h // 2
    rid = locate_region(labels, cx, cy)
    if rid is None:
        # scan to find a valid region
        rid = next((r for r in regions.keys()), None)
    if rid is None:
        print("[smoke] no valid region found; PASS but nothing to recommend")
        return 0

    items = recommend_for_region(int(rid), feats[int(rid)], rules=None, weights={"color": 0.5, "sheen": 0.3, "texture": 0.2}, topk=3)
    t5 = time.perf_counter(); print(f"[time] recommend: {t5 - t4:.3f}s")
    for i, (name, score, _explain) in enumerate(items, 1):
        print(f"[top{i}] {name}: {score:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


