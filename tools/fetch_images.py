# -*- coding: utf-8 -*-
"""
Fetch fabric images via Bing, topping up each category to >=5 images.
- Uses chinese labels from data/fabric_labels.json to build robust queries
- Flattens bing_image_downloader nested folders into data/fabrics/<id>/
- Skips categories already having >=5 images
- Accepts optional CLI args to only fetch specified fabric IDs

Usage:
  # Fetch for all categories needing images
  python tools/fetch_images.py

  # Only fetch for specified categories
  python tools/fetch_images.py canvas chiffon corduroy cotton denim knit lace linen organza satin silk woolen

Requires:
  pip install bing-image-downloader pillow-heif
"""
from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from typing import List
from PIL import Image
try:
    from tools._bootstrap import run_main_safely  # type: ignore
except Exception:
    run_main_safely = None

# Enable AVIF/HEIF via pillow-heif if available
try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass

try:
    from bing_image_downloader import downloader
except Exception as e:
    raise SystemExit("bing-image-downloader not installed. Run: pip install bing-image-downloader")

ROOT = Path("data/fabrics")
LABELS_PATH = Path("data/fabric_labels.json")


def count_images(dir_path: Path) -> int:
    exts = ("*.jpg", "*.jpeg", "*.png")
    files: List[Path] = []
    for pat in exts:
        files.extend(dir_path.glob(pat))
    return len(files)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def flatten_downloads(fabric_id: str, out_dir: Path) -> int:
    """Move images from bing-created subfolders into out_dir as JPGs.
    Returns number of images moved.
    """
    moved = 0
    # Find subfolders created by bing_image_downloader under out_dir
    for sub in [d for d in out_dir.iterdir() if d.is_dir()]:
        for fp in sub.rglob("*"):
            if not fp.is_file():
                continue
            try:
                img = Image.open(fp).convert("RGB")
                # Next sequence index
                exist_count = count_images(out_dir)
                save_path = out_dir / f"{fabric_id}_{exist_count+1:03d}.jpg"
                img.save(save_path, "JPEG", quality=92)
                moved += 1
            except Exception:
                # skip unreadable files
                continue
        # remove the subfolder after processing
        try:
            for fp in sub.rglob("*"):
                try:
                    fp.unlink()
                except Exception:
                    pass
            sub.rmdir()
        except Exception:
            pass
    return moved


def fetch_for_fabric(fabric_id: str, chinese_label: str, min_needed: int = 5) -> None:
    out = ROOT / fabric_id
    ensure_dir(out)
    have = count_images(out)
    if have >= min_needed:
        print(f"✓ {fabric_id:<15} already has {have} images (skip)")
        return

    need = min_needed - have
    # Build query (Chinese + English) for close-up texture
    query = f"{chinese_label} 纹理 近景 布料 质地 close up fabric texture"

    print(f"→ {fabric_id:<15} need {need} more (have {have}), querying: {query}")
    try:
        # bing_image_downloader creates a subfolder under output_dir with the query as name
        downloader.download(query,
                            limit=need,
                            output_dir=str(out),
                            adult_filter_off=True,
                            force_replace=False,
                            timeout=30,
                            verbose=True)
    except Exception as e:
        print(f"  ✗ download failed: {e}")

    moved = flatten_downloads(fabric_id, out)
    print(f"  ✓ moved {moved} files into {out}")


def main(args: List[str]) -> int:
    if not LABELS_PATH.exists():
        print(f"labels file not found: {LABELS_PATH}", flush=True)
        return 2

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        labels = json.load(f)

    # Determine target fabrics
    if args:
        target_ids = [a.strip() for a in args if a.strip() in labels]
        unknown = [a for a in args if a.strip() not in labels]
        if unknown:
            print(f"⚠ unknown fabric ids ignored: {', '.join(unknown)}")
    else:
        target_ids = list(labels.keys())

    # Ensure root exists
    ensure_dir(ROOT)

    for fid in target_ids:
        fetch_for_fabric(fid, labels[fid])

    print("done", flush=True)
    return 0


if __name__ == "__main__":
    if run_main_safely:
        raise SystemExit(run_main_safely(lambda: main(sys.argv[1:])))
    sys.exit(main(sys.argv[1:]))