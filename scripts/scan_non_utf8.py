# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from src.utils.io import _detect_encoding


EXTS: Iterable[str] = (".json", ".txt", ".md", ".yaml", ".yml")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    targets = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in EXTS:
            targets.append(p)

    bad = 0
    for p in targets:
        b = p.read_bytes()
        try:
            b.decode("utf-8")
            continue
        except Exception:
            enc = _detect_encoding(b)
            print(f"[non-utf8] {p} -> suggest: {enc}")
            bad += 1

    print(f"[scan] checked {len(targets)} files, non-utf8: {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


