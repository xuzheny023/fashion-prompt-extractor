# -*- coding: utf-8 -*-
# src/bg_remove.py
import io, numpy as np, cv2
from PIL import Image
from rembg import remove, new_session

def get_foreground_mask(pil_img: Image.Image, target_long=1024, model='isnet-general'):
    """
    Return:
      mask (H,W) uint8 in {0,255}, aligned to ORIGINAL size
      meta: {'scale': float, 'pad': (top,left), 'bbox': (x1,y1,x2,y2)} if you did cropping; otherwise empty
      meta: {'scale': float, 'pad': (top,left), 'bbox': (x1,y1,x2,y2)} if浣犲仛浜嗚鍓? 鍚﹀垯涓虹┖
    """
    W, H = pil_img.size
    # Keep original size alignment simplest: only scale proportionally to shorter side for inference, then scale back
    # 鈥斺€?淇濇寔鍘熷昂瀵稿榻愭渶绠€鍗曪細鍙仛绛夋瘮缂╂斁鍒拌緝鐭竟鎺ㄧ悊锛屽啀缂╁洖 鈥斺€?    scale = target_long / max(W, H)
    if scale < 1.0:
        resized = pil_img.resize((int(W*scale), int(H*scale)), Image.BICUBIC)
    else:
        resized = pil_img

    session = None
    try:
        session = new_session(model)
    except Exception:
        pass

    buf = io.BytesIO()
    resized.save(buf, format='PNG'); data = buf.getvalue()
    out = remove(
        data, session=session,
        alpha_matting=True,
        post_process_mask=True
    )
    rgba = np.array(Image.open(io.BytesIO(out)).convert('RGBA'))
    a_small = rgba[:, :, 3]  # 0-255

    # Scale back to original size / 缂╁洖鍘熷昂瀵?    if scale < 1.0:
        mask = cv2.resize(a_small, (W, H), interpolation=cv2.INTER_LINEAR)
    else:
        # Original image smaller: pad to original size / 鍘熷浘鏇村皬锛歱ad鍒板師灏哄
        canvas = np.zeros((H, W), np.uint8)
        h, w = a_small.shape[:2]
        canvas[:h, :w] = a_small
        mask = canvas

    # Light post-processing: closing operation + light smoothing / 杞诲悗澶勭悊锛氶棴杩愮畻 + 杞诲钩婊?    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    mask = cv2.medianBlur(mask, 3)

    # Binarization (more stable for analysis/speed) / 浜屽€煎寲锛堝垎鏋?鍔犻€熸洿绋筹級
    _, mask = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
    return mask, {}
