# -*- coding: utf-8 -*-
"""
AI Fashion Fabric Analyst - 纯云端版本
Cloud-only architecture with interactive cropping
"""
import streamlit as st
from PIL import Image
import io
import base64
import os
from typing import Optional, Tuple

st.set_page_config(
    page_title="AI Fashion Fabric Analyst",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== API Key 管理 ====================
def get_api_key() -> Optional[str]:
    """统一获取 API Key：优先 secrets，回退到环境变量"""
    try:
        return st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    except Exception:
        return os.getenv("DASHSCOPE_API_KEY")

# ==================== 导入组件 ====================
# 裁剪组件
try:
    from ui.web_cropper import web_cropper
except Exception:
    web_cropper = None

# 推荐面板
try:
    from ui.components.recommend_panel import render_recommend_panel
except Exception:
    def render_recommend_panel(*args, **kwargs):
        st.error("⚠️ 推荐面板不可用")

# 日志和图标
try:
    from src.utils.logger import get_logger
    log = get_logger("app")
except Exception:
    import logging
    log = logging.getLogger("app")

try:
    from src.ui.icons import E
except Exception:
    def E(name): return {"app": "🎯", "recommend": "📊", "clip": "🔍"}.get(name, "•")

# ==================== 辅助函数 ====================
def pil_to_b64(img: Image.Image) -> str:
    """Convert PIL image to base64 string (PNG format, no data: prefix)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def crop_by_rect(img: Image.Image, rect: dict | None, display_width: int) -> Tuple[Image.Image, Optional[dict]]:
    """
    Crop image based on rect from web_cropper component.
    
    Args:
        img: Original PIL image
        rect: {x, y, w, h} in CSS pixels (relative to display size)
        display_width: Width at which the image was displayed in the component
    
    Returns:
        (cropped_image, crop_metadata) or (original_image, None)
    """
    if not rect:
        return img, None
    
    orig_w, orig_h = img.size
    
    # Component displays image at max 800px width, keeping aspect ratio
    if display_width >= orig_w:
        # No scaling, use coordinates directly
        scale = 1.0
    else:
        # Image was scaled down, need to scale coordinates back up
        scale = orig_w / display_width
    
    # Extract rect coordinates (CSS pixels)
    x = float(rect.get("x", 0))
    y = float(rect.get("y", 0))
    w = float(rect.get("w", 0))
    h = float(rect.get("h", 0))
    
    # Convert to original image coordinates
    x0 = int(x * scale)
    y0 = int(y * scale)
    x1 = int((x + w) * scale)
    y1 = int((y + h) * scale)
    
    # Clamp to image bounds
    x0 = max(0, min(x0, orig_w))
    y0 = max(0, min(y0, orig_h))
    x1 = max(0, min(x1, orig_w))
    y1 = max(0, min(y1, orig_h))
    
    # Validate crop area
    if x1 <= x0 or y1 <= y0:
        return img, None
    
    cropped = img.crop((x0, y0, x1, y1))
    metadata = {
        "x0": x0, "y0": y0, "x1": x1, "y1": y1,
        "width": x1 - x0, "height": y1 - y0,
        "scale": scale
    }
    
    return cropped, metadata

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("👔 面料分析器")
    st.caption("AI-Powered Fabric Recognition")

    uploaded_file = st.file_uploader(
        "📤 上传面料图片",
        type=["jpg", "jpeg", "png"],
        help="支持 JPG、PNG 格式"
    )

    st.divider()
    with st.expander(f"{E('recommend')} 参数设置", expanded=False):
        top_k = st.slider("返回结果数", 3, 10, 5)
        lang = st.selectbox("语言", ["zh", "en"], index=0)
        use_crop = st.checkbox("使用交互裁剪区域进行识别", value=True, help="若可用，将优先用裁剪区域做检索")
    
    st.divider()
    with st.expander("🔑 API 配置", expanded=False):
        api_key = get_api_key()
        if api_key:
            st.success("✅ API Key 已配置")
            st.caption(f"来源: {'secrets.toml' if 'DASHSCOPE_API_KEY' in st.secrets else '环境变量'}")
        else:
            st.warning("⚠️ 未配置 API Key")
            st.caption("请在 `.streamlit/secrets.toml` 中设置：")
            st.code('DASHSCOPE_API_KEY = "sk-xxx"', language="toml")
    
    st.divider()
    with st.expander("ℹ️ 关于", expanded=False):
        st.markdown("""
        **版本:** 3.0 (纯云端)  
        - ✅ 云端 API 识别  
        - ✅ 交互式裁剪组件  
        - ✅ 轻量级架构  
        """)

# ==================== 主界面 ====================
st.title(f"{E('app')} AI 面料识别与分析")
st.caption("基于云端 API 的智能面料识别系统")

if uploaded_file is None:
    st.info("👈 请在左侧上传面料图片开始分析")
    st.stop()

# 加载图片
try:
    image = Image.open(uploaded_file).convert("RGB")
    log.info(f"图片已加载: {uploaded_file.name}, 尺寸: {image.size}")
except Exception as e:
    st.error(f"❌ 图片加载失败: {e}")
    st.stop()

# ==================== 布局：左预览 / 右推荐 ====================
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📷 图片预览 / 交互裁剪")

    crop_rect = None
    display_width = 800  # Component max display width
    
    if web_cropper is None:
        # Graceful fallback: show warning and full image
        if use_crop:
            st.warning("⚠️ 裁剪组件不可用，使用完整图片进行识别")
        st.image(image, use_container_width=True, caption=f"原始图片 ({image.width} × {image.height})")
    else:
        # Use web_cropper component
        try:
            b64 = pil_to_b64(image)
            st.caption("💡 拖动矩形移动位置 • 拖动右下角调整大小 • 点击 Confirm 确认")
            
            res = web_cropper(
                key="web_cropper_main",
                image_b64=b64,
                box=None,
                minSize=32
            )
            
            # Check if user confirmed a crop area
            if isinstance(res, dict) and isinstance(res.get("rect"), dict):
                crop_rect = res["rect"]
                st.success(f"✓ 已选择裁剪区域：{int(crop_rect['w'])} × {int(crop_rect['h'])} px")
            else:
                st.info("👆 调整裁剪框后点击 Confirm 按钮")
        except Exception as e:
            log.error(f"Web cropper error: {e}")
            st.warning(f"⚠️ 裁剪组件出错，使用完整图片：{e}")
            st.image(image, use_container_width=True)

    # Process crop if enabled and available
    if use_crop and crop_rect:
        crop_img, crop_meta = crop_by_rect(image, crop_rect, display_width)
        if crop_meta:
            st.divider()
            st.caption(f"📐 裁剪区域：({crop_meta['x0']}, {crop_meta['y0']}) → ({crop_meta['x1']}, {crop_meta['y1']})")
            st.image(crop_img, caption=f"裁剪预览 ({crop_meta['width']} × {crop_meta['height']})", use_container_width=True)
            # Store cropped image for inference
            st.session_state["_active_image_for_infer"] = crop_img
            st.session_state["_active_meta"] = crop_meta
        else:
            # Invalid crop, use full image
            st.session_state["_active_image_for_infer"] = image
            st.session_state["_active_meta"] = None
    else:
        # Use full image
        st.session_state["_active_image_for_infer"] = image
        st.session_state["_active_meta"] = None

with right_col:
    st.subheader(f"{E('recommend')} 推荐结果")
    st.caption(f"{E('clip')} 云端 API 识别")
    
    # 调用推荐面板
    render_recommend_panel(
        image=st.session_state.get("_active_image_for_infer", image),
        top_k=top_k,
        lang=lang
    )
    
    # Display engine info (for verification)
    if 'last_meta' in st.session_state and st.session_state.last_meta:
        engine = st.session_state.last_meta.get('engine', '未知')
        st.caption(f"🔧 引擎: {engine}")
    else:
        st.caption("🔧 引擎: 未返回")

# ==================== 底部信息 ====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("✂️ 交互式裁剪：拖动移动 • 拖角调整大小")
with col2:
    st.caption("☁️ 云端识别：DashScope API")
with col3:
    cropper_status = "✅ 可用" if web_cropper else "⚠️ 不可用"
    st.caption(f"🔧 裁剪组件：{cropper_status}")

def main():
    pass

if __name__ == "__main__":
    main()
