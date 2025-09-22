from __future__ import annotations

import sys
import glob
from pathlib import Path

from src.utils.io import _detect_encoding


def convert_file(p: Path) -> None:
    b = p.read_bytes()
    enc = _detect_encoding(b)
    enc_low = (enc or "").lower()
    if enc_low in ("utf-8", "utf_8", "utf-8-sig", "utf_8_sig"):
        print(f"[convert] skip utf8: {p}")
        return
    try:
        text = b.decode(enc, errors="replace")
    except Exception as e:
        print(f"[convert] decode failed {p} with {enc}: {e}")
        return
    bak = p.with_suffix(p.suffix + ".bak")
    try:
        if not bak.exists():
            bak.write_bytes(b)
        p.write_text(text, encoding="utf-8", errors="ignore")
        print(f"[convert] {p} {enc} -> utf-8 (backup: {bak.name})")
    except Exception as e:
        print(f"[convert] write failed {p}: {e}")


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python scripts/convert_to_utf8.py \"locales/*.json\" \"data/**/*.json\"")
        return 1
    root = Path.cwd()
    matched = set()
    for pat in argv:
        for s in glob.glob(pat, recursive=True):
            p = Path(s)
            if p.is_file():
                matched.add(p.resolve())
    for p in sorted(matched):
        convert_file(Path(p))
    print(f"[convert] processed {len(matched)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


