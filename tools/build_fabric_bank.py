# tools/build_fabric_bank.py
from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
import sys, traceback

# Bootstrap robustness (faulthandler, AVIF, sys.path)
try:
    from tools._bootstrap import run_main_safely  # type: ignore
except Exception:
    run_main_safely = None

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dual_clip import image_to_emb

ROOT = Path("data/fabrics")
OUT = Path("data/fabric_bank.npz")

def collect_images():
    if not ROOT.exists():
        print(f"[ERR] {ROOT} not found", flush=True)
        return {}
    fabrics = [p for p in ROOT.iterdir() if p.is_dir()]
    if not fabrics:
        print(f"[WARN] no subfolders under {ROOT}", flush=True)
        return {}
    bank = {}
    for d in fabrics:
        print(f"[{d.name}] scanning...", flush=True)
        embs = []
        # Recursively find images in subfolders as well
        patterns = ("**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.JPG", "**/*.PNG", "**/*.JPEG")
        imgs = []
        for pat in patterns:
            imgs.extend(d.glob(pat))
        if not imgs:
            print(f"  (no images)", flush=True)
            continue
        for i, img_p in enumerate(sorted(imgs), 1):
            try:
                print(f"  ({i}/{len(imgs)}) loading {img_p.name} ...", flush=True)
                img = Image.open(img_p).convert("RGB")
                emb = image_to_emb(img)
                embs.append(emb)
                print(f"    ✓ encoded", flush=True)
            except Exception:
                traceback.print_exc()
                print(f"    ✗ skip {img_p}", flush=True)
        if embs:
            arr = np.stack(embs, axis=0)
            bank[d.name] = arr
            print(f"  → collected {len(embs)} embeddings", flush=True)
            print(f"[{d.name}] {len(embs)} samples -> {arr.shape}", flush=True)
    return bank

def save_npz(bank: dict):
    if not bank:
        print("[ERR] empty bank, nothing to save.", flush=True)
        return
    
    # A. 最少样本过滤统计
    print("\n[STATS] 样本统计:", flush=True)
    valid_classes = []
    for k, v in bank.items():
        count = v.shape[0]
        status = "✓" if count >= 3 else "⚠"
        print(f"  {status} {k:<15}: {count:2d} samples", flush=True)
        if count >= 3:
            valid_classes.append(k)
    
    print(f"\n[FILTER] 有效类别: {len(valid_classes)}/{len(bank)} (≥3 samples)", flush=True)
    
    # B. 生成类中心向量
    centroids = {}
    for k in valid_classes:
        centroids[k] = bank[k].mean(axis=0, keepdims=True).astype("float32")
    
    OUT.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存完整bank
    np.savez_compressed(OUT, **bank)
    print(f"[OK] saved → {OUT.resolve()}", flush=True)
    
    # 保存类中心向量
    if centroids:
        centroids_out = Path("data/fabric_centroids.npz")
        np.savez_compressed(centroids_out, **centroids)
        print(f"[OK] saved → {centroids_out.resolve()}", flush=True)
        print(f"[INFO] centroids: {len(centroids)} classes", flush=True)

def _cli():
    print("[1/2] building fabric bank ...", flush=True)
    bank = collect_images()
    print("[2/2] saving ...", flush=True)
    save_npz(bank)

if __name__ == "__main__":
    if run_main_safely:
        raise SystemExit(run_main_safely(_cli))
    _cli()
