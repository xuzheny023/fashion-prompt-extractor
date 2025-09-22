from __future__ import annotations

from pathlib import Path
from typing import Any
import json

# Optional detectors
try:
    from charset_normalizer import from_bytes as cn_from_bytes  # type: ignore
except Exception:
    cn_from_bytes = None  # type: ignore

try:
    import chardet  # type: ignore
except Exception:
    chardet = None  # type: ignore


def _detect_encoding(b: bytes) -> str:
    # Fast paths
    for enc in ("utf-8", "utf-8-sig"):
        try:
            b.decode(enc)
            return enc
        except Exception:
            pass
    # Probe via charset-normalizer
    if cn_from_bytes is not None:
        try:
            res = cn_from_bytes(b).best()
            if res and getattr(res, "encoding", None):
                return res.encoding  # type: ignore
        except Exception:
            pass
    # Probe via chardet
    if chardet is not None:
        try:
            det = chardet.detect(b)
            if det and det.get("encoding"):
                return str(det["encoding"])
        except Exception:
            pass
    # Fallback trials
    for enc in ("gbk", "cp936", "latin-1"):
        try:
            b.decode(enc)
            return enc
        except Exception:
            pass
    return "latin-1"  # last resort


def read_text_smart(path: str | Path) -> tuple[str, str]:
    p = Path(path)
    data = p.read_bytes()
    enc = _detect_encoding(data)
    text = data.decode(enc, errors="replace")
    print(f"[io] loaded {p} with encoding={enc}")
    return text, enc


def read_json_smart(path: str | Path) -> Any:
    text, _enc = read_text_smart(path)
    # Strip BOM-like/JS-style comments
    import re

    cleaned = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    cleaned = re.sub(r"^\s*//.*?$", "", cleaned, flags=re.M)
    return json.loads(cleaned)


