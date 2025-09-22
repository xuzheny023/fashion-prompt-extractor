from __future__ import annotations

from PIL import Image


def make_preview(image_pil: Image.Image, preview_width: int = 720):
    w, h = image_pil.width, image_pil.height
    if w == preview_width:
        return image_pil, w, h
    ratio = preview_width / float(w)
    new_size = (preview_width, int(round(h * ratio)))
    return image_pil.resize(new_size), w, h


def map_simple_scale(x_disp: int, y_disp: int, disp_w: int, disp_h: int, orig_w: int, orig_h: int):
    sx = orig_w / float(disp_w)
    sy = orig_h / float(disp_h)
    x0 = int(max(0, min(orig_w - 1, round(x_disp * sx))))
    y0 = int(max(0, min(orig_h - 1, round(y_disp * sy))))
    return x0, y0


