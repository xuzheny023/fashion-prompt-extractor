# -*- coding: utf-8 -*-
"""
Build fabric reference bank by extracting CLIP embeddings from reference images.
构建面料参考库，从参考图像中提取 CLIP 嵌入

Usage:
    python tools/build_fabric_bank.py

Input:
    data/fabrics/<fabric_id>/*.jpg
    
Output:
    data/fabric_bank.npz
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
import sys
import os

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clip_infer import image_to_emb

ROOT = Path("data/fabrics")
OUT = Path("data/fabric_bank.npz")

def collect_images():
    """
    Collect and encode all reference images in data/fabrics/.
    收集并编码 data/fabrics/ 中的所有参考图像
    
    Returns:
        Dict mapping fabric_id -> numpy array of embeddings (N, D)
    """
    if not ROOT.exists():
        print(f"[ERROR] Directory not found: {ROOT.resolve()}")
        print("Please create data/fabrics/<fabric_id>/ and add reference images.")
        return {}
    
    fabric_dirs = [p for p in ROOT.iterdir() if p.is_dir()]
    if not fabric_dirs:
        print(f"[WARN] No subdirectories found in {ROOT.resolve()}")
        print("Expected structure: data/fabrics/<fabric_id>/*.jpg")
        return {}
    
    bank = {}
    for d in fabric_dirs:
        embs = []
        image_files = (
            list(d.glob("*.jpg")) + 
            list(d.glob("*.jpeg")) + 
            list(d.glob("*.png"))
        )
        
        for img_p in sorted(image_files):
            try:
                img = Image.open(img_p).convert("RGB")
                emb = image_to_emb(img)
                embs.append(emb)
                print(f"  [{d.name}] Processed: {img_p.name}")
            except Exception as e:
                print(f"[skip] {img_p}: {e}")
        
        if embs:
            bank[d.name] = np.stack(embs, axis=0)
            print(f"[OK] {d.name}: {len(embs)} images -> shape {bank[d.name].shape}")
        else:
            print(f"[WARN] {d.name}: No valid images found")
    
    return bank

def save_npz(bank: dict):
    """
    Save fabric bank to compressed NPZ file.
    将面料库保存为压缩的 NPZ 文件
    """
    if not bank:
        print("\n[ERROR] No embeddings collected. Make sure data/fabrics/<id> has images.")
        print("Expected structure:")
        print("  data/fabrics/")
        print("    ├── cotton/")
        print("    │   ├── ref1.jpg")
        print("    │   └── ref2.jpg")
        print("    ├── silk/")
        print("    │   └── ref1.jpg")
        print("    └── ...")
        return
    
    # Ensure output directory exists
    OUT.parent.mkdir(parents=True, exist_ok=True)
    
    np.savez_compressed(OUT, **bank)
    total_images = sum(embs.shape[0] for embs in bank.values())
    print(f"\n{'='*60}")
    print(f"✅ Saved fabric bank -> {OUT.resolve()}")
    print(f"   Total fabrics: {len(bank)}")
    print(f"   Total images: {total_images}")
    print(f"   File size: {OUT.stat().st_size / 1024:.1f} KB")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("Building fabric reference bank...\n")
    bank = collect_images()
    save_npz(bank)

