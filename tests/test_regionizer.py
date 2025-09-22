import sys
from pathlib import Path

import numpy as np
import cv2

# Allow running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.regionizer import build_regions


def _load_demo_img() -> np.ndarray:
    # Try to load a small sample from data/ if exists; else generate synthetic
    candidates = [
        ROOT / "data" / "demo.jpg",
        ROOT / "data" / "demo.png",
    ]
    for p in candidates:
        if p.exists():
            img = cv2.imread(str(p))
            if img is not None:
                return img
    # synthetic gradient + circle
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    for y in range(256):
        img[y, :, 1] = np.uint8(y)  # green gradient
    cv2.circle(img, (128, 128), 60, (0, 0, 255), -1)
    return img


def main():
    img = _load_demo_img()
    print("Image shape:", img.shape)

    for method in ("slic", "grid"):
        out = build_regions(img, method=method, slic_n_segments=120, slic_compactness=8.0, grid_rows=8, grid_cols=8)
        labels = out["labels"]
        regions = out["regions"]
        print(f"method={out['method']}, unique_labels={len(set([int(x) for x in np.unique(labels) if x>=0]))}, regions={len(regions)}")
        first3 = list(regions.items())[:3]
        for rid, info in first3:
            print("  id=", rid, "bbox=", info.get("bbox"), "area=", info.get("area"))


if __name__ == "__main__":
    main()


