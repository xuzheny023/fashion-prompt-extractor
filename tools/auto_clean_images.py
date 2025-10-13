from __future__ import annotations
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm
import sys

# Optional: keep AVIF by registering HEIF opener if installed
try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass

ROOT = Path("data/fabrics")
MIN_SIDE = 224


def bad(img_path: Path) -> bool:
    try:
        with Image.open(img_path) as im:
            im.verify()
        with Image.open(img_path) as im:
            w, h = im.size
        return min(w, h) < MIN_SIDE
    except (UnidentifiedImageError, OSError):
        return True


def main() -> int:
    if not ROOT.exists():
        print(f"[ERR] {ROOT} not found", flush=True)
        return 2
    imgs = [p for p in ROOT.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}]
    if not imgs:
        print("[WARN] no images found", flush=True)
        return 0

    removed = 0
    for p in tqdm(imgs, desc="Scanning", unit="img"):
        try:
            if bad(p):
                p.unlink(missing_ok=True)
                removed += 1
        except Exception as e:
            print(f"[SKIP] {p}: {e}", flush=True)

    print(f"[OK] cleaned. removed={removed} / total={len(imgs)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

