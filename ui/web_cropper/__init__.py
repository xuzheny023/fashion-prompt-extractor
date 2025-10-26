# ui/web_cropper/__init__.py
# -*- coding: utf-8 -*-
"""Streamlit custom component: web_cropper (auto dev/build fallback)."""
from __future__ import annotations
import os
import socket
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import numpy as np
from io import BytesIO


def _port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _declare_component():
    """
    优先使用环境变量 WEB_CROPPER_DEV_URL 指定的 Dev Server，
    若不可达则回退到本地构建产物（dist 或 build，自动探测）。
    """
    dev_url = os.getenv("WEB_CROPPER_DEV_URL", "").strip()
    if dev_url:
        try:
            from urllib.parse import urlparse
            u = urlparse(dev_url)
            host, port = (u.hostname or "localhost"), (u.port or 5173)
            if _port_open(host, int(port)):
                return components.declare_component("web_cropper", url=dev_url)
        except Exception:
            pass  # 回退到本地产物

    root = Path(__file__).parent / "frontend"
    # 兼容两种常见目录名
    for candidate in ("dist", "build"):
        p = root / candidate
        if p.exists() and (p / "index.html").exists():
            return components.declare_component("web_cropper", path=str(p))

    # 最后兜底（即使目录不存在，也让错误信息更可读）
    return components.declare_component("web_cropper", path=str(root / "dist"))


_web_cropper = _declare_component()

def _pil_to_media_url(img: Image.Image, fmt: str = "PNG", coordinates: str = "web_cropper") -> str:
    """Store image and return a URL.

    Prefers the current Runtime.media_file_mgr.add API:
      add(path_or_data: bytes | str, mimetype: str, coordinates: str, file_name: str | None = None) -> str

    Falls back to older Streamlit APIs if necessary.
    Returns a relative URL (e.g. /media/xxx) when available; otherwise a data URL as a last resort.
    """
    buf = BytesIO()
    fmt = (fmt or "PNG").upper()
    img.convert("RGB").save(buf, format=fmt)
    data = buf.getvalue()
    mime = f"image/{fmt.lower()}"
    filename = f"image.{fmt.lower()}"

    # 1) Preferred: Runtime singleton media_file_mgr
    try:
        from streamlit.runtime import get_instance

        mgr = get_instance().media_file_mgr
        url = mgr.add(data, mime, coordinates, filename)
        return url
    except Exception:
        pass

    # 2) Legacy: module-level media_file_manager instance
    try:
        from streamlit.runtime.media_file_manager import media_file_manager as mfm  # type: ignore

        url = mfm.add(data, mime, coordinates, filename)  # type: ignore[attr-defined]
        return url
    except Exception:
        pass

    # 3) Old add(...) function variants requiring ctx
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        from streamlit.runtime.media_file_manager import add as add_func  # type: ignore

        ctx = get_script_run_ctx()
        try:
            mf = add_func(data=data, mimetype=mime, filename=filename, ctx=ctx)  # type: ignore[call-arg]
            return mf.url if hasattr(mf, "url") else mf  # type: ignore[no-any-return]
        except TypeError:
            mf = add_func(data, f".{fmt.lower()}", mime, ctx=ctx)  # type: ignore[misc]
            return mf.url if hasattr(mf, "url") else mf  # type: ignore[no-any-return]
    except Exception:
        pass

    # 4) Final fallback: data URL (works in all cases, though not relative)
    import base64

    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"

def ensure_pil(obj) -> Image.Image:
    if isinstance(obj, Image.Image):
        return obj
    if isinstance(obj, np.ndarray):
        return Image.fromarray(obj)
    if isinstance(obj, (bytes, bytearray, BytesIO)):
        b = obj if isinstance(obj, BytesIO) else BytesIO(obj)
        return Image.open(b)
    raise TypeError(f"Unsupported image type: {type(obj)}")

def st_web_cropper(
    image: Image.Image | np.ndarray | bytes,
    init_box: int = 160,
    key: str = "web_cropper",
    container_width: int = 900,
) -> Optional[Tuple[int, int, int, int]]:
    """
    Returns (x, y, w, h) in original image pixel coordinates, or None.
    """
    img = ensure_pil(image).convert("RGB")
    w, h = img.size

    # Show at most container_width; keep aspect
    disp_w = min(container_width, w)
    disp_h = int(h * (disp_w / w))

    coords = f"web_cropper.{key}"
    url = _pil_to_media_url(img, fmt="JPEG", coordinates=coords)  # relative URL when possible
    # Pass to frontend: imageUrl (relative), natural size and display size, initBox
    value = _web_cropper(
        imageUrl=url,
        naturalWidth=w,
        naturalHeight=h,
        displayWidth=disp_w,
        displayHeight=disp_h,
        initBox=init_box,
        key=key,
        default=None,
    )
    # value expected as dict {x,y,w,h} in **original** pixel units
    if isinstance(value, dict):
        try:
            x = int(value.get("x", 0))
            y = int(value.get("y", 0))
            ww = int(value.get("w", 0))
            hh = int(value.get("h", 0))
            if ww > 0 and hh > 0:
                return (x, y, ww, hh)
        except Exception:
            pass
    return None
