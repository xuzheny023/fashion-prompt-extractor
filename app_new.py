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

# ==================== 组件依赖可用性探测 ====================
WEB_CROPPER_AVAILABLE = bool('web_cropper' in globals() and web_cropper)

CROP_CANVAS_AVAILABLE = False
try:
    from streamlit_drawable_canvas import st_canvas  # noqa: F401
    CROP_CANVAS_AVAILABLE = True
except Exception:
    CROP_CANVAS_AVAILABLE = False

DASHSCOPE_AVAILABLE = False
try:
    import dashscope  # noqa: F401
    from dashscope import MultiModalConversation  # noqa: F401
    DASHSCOPE_AVAILABLE = True
except Exception:
    DASHSCOPE_AVAILABLE = False

# ==================== 辅助函数 ====================
def pil_to_b64(img: Image.Image) -> str:
    """Convert PIL image to base64 string (PNG format, no data: prefix)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def ensure_min_size(pil_img: Image.Image, tgt: int = 640) -> Image.Image:
    """保证传云端的图片最短边≥tgt，避免太小导致识别失败。"""
    w, h = pil_img.size
    if min(w, h) >= tgt:
        return pil_img
    scale = tgt / float(min(w, h))
    nw, nh = int(round(w * scale)), int(round(h * scale))
    return pil_img.resize((nw, nh), Image.LANCZOS)

def try_parse_json(text: str):
    """尝试从文本中解析 JSON，兼容 ```json 代码块与首个对象兜底。"""
    import json as _json
    import re as _re
    t = (text or "").strip()
    # 1) 直接解析
    try:
        return _json.loads(t)
    except Exception:
        pass
    # 2) ```json 代码块
    if "```" in t:
        m = _re.search(r"```json\s*(\{[\s\S]*?\})\s*```", t, flags=_re.I)
        if m:
            try:
                return _json.loads(m.group(1))
            except Exception:
                pass
        m = _re.search(r"```\s*(\{[\s\S]*?\})\s*```", t)
        if m:
            try:
                return _json.loads(m.group(1))
            except Exception:
                pass
    # 3) 首个对象兜底
    m = _re.search(r"\{[\s\S]*?\}", t)
    if m:
        try:
            return _json.loads(m.group(0))
        except Exception:
            return None
    return None

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
    st.header("⚙️ 参数设置")
    
    # 裁剪与预览
    crop_size = st.slider("选框大小(px)", 60, 240, 120, 2)
    zoom_ratio = st.slider("预览放大倍数", 1.0, 2.0, 1.5, 0.05)
    
    # 云端模型选择
    engine = st.selectbox("云端模型 / Cloud Engine", ["qwen-vl", "qwen-vl-plus"], index=0)
    # 语言选择
    lang = st.radio("语言 / Language", ["zh", "en"], index=0, horizontal=True)
    
    # 联网检索（先保留，不影响可用性）
    enable_web = st.checkbox("启用联网检索", value=False)
    k_per_query = st.slider("每个候选检索条数", 1, 10, 4)
    top_k = st.slider("返回结果数", 3, 10, 5)
        
    # 裁剪选项
    use_crop = st.checkbox("使用交互裁剪区域进行识别", value=True, help="若可用，将优先用裁剪区域做检索")
    
    # 密钥与 SDK 状态指示
    try:
        _api_key = st.secrets.get("DASHSCOPE_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    except Exception:
        _api_key = os.getenv("DASHSCOPE_API_KEY")
    st.markdown(f"**DashScope SDK**：{'✅' if DASHSCOPE_AVAILABLE else '❌'}")
    st.markdown(f"**API Key**：{'✅ 已读取' if _api_key else '❌ 缺失'}")
    
    st.divider()
    with st.expander("ℹ️ 关于", expanded=False):
        st.markdown("""
        **版本:** 3.0 (纯云端)  
        - ✅ 云端 API 识别  
        - ✅ 交互式裁剪组件  
        - ✅ 轻量级架构  
        """)

st.title(f"{E('app')} AI 面料识别与分析")
st.caption("基于云端 API 的智能面料识别系统")

# 结果展示（统一）
def render_result_block(result: dict, engine_name: str):
    st.caption(f"引擎：{engine_name}")
    if result.get("labels"):
        st.success("已识别")
        labs = result.get("labels", [])
        confs = result.get("confidences", [])
        for i, lab in enumerate(labs):
            c = confs[i] if i < len(confs) else None
            st.markdown(f"**{i+1}. {lab}** " + (f"（{c:.2%}）" if isinstance(c, (float, int)) else ""))
    else:
        st.warning("未识别到明确面料标签")
    with st.expander("🧠 解释 / Reasoning", expanded=True):
        st.write(result.get("reasoning") or result.get("raw") or "（无）")

# ==================== 布局：左预览 / 右推荐 ====================
colL, colR = st.columns([7, 5], gap="large")

with colL:
    st.subheader("图片预览 / 交互裁剪")
    img = None
    uploaded = uploaded_file
    if uploaded:
        try:
            img = Image.open(uploaded).convert("RGB")
        except Exception as _e:
            st.error(f"图片加载失败：{_e}")
            img = None
        if img:
            st.image(img, caption=f"原始图片（{img.size[0]}×{img.size[1]}）", use_container_width=True)

        rect = None
        patch = None

        # 兜底 1：drawable-canvas（首选）
        if img and CROP_CANVAS_AVAILABLE:
            st.caption("🔧 使用 drawable-canvas 裁剪")
            try:
                canvas_res = st_canvas(
                    fill_color="rgba(0, 0, 0, 0)",
                    stroke_width=2,
                    stroke_color="#00BFFF",
                    background_image=img,
                    update_streamlit=True,
                    height=int(img.size[1] * 0.7),
                    drawing_mode="rect",
                    key="crop_canvas",
                )
                try:
                    if canvas_res.json_data and canvas_res.json_data.get("objects"):
                        obj = next((o for o in canvas_res.json_data["objects"] if o.get("type") == "rect"), None)
                        if obj:
                            x, y = int(obj.get("left", 0)), int(obj.get("top", 0))
                            w, h = int(obj.get("width", 0)), int(obj.get("height", 0))
                            rect = (x, y, x + w, y + h)
                except Exception:
                    rect = None
            except AttributeError as ae:
                st.warning("⚠️ 当前 Streamlit 与 drawable-canvas 不兼容，已自动切换到数值裁剪模式。")
                log.warning(f"drawable-canvas AttributeError: {ae}")
                rect = None
            except Exception as e:
                st.warning(f"⚠️ 裁剪组件出错，已自动切换到数值裁剪模式：{e}")
                log.error(f"st_canvas error: {e}")
                rect = None

        # 兜底 2：数值裁剪（无前端依赖）
        if img and rect is None:
            st.caption("🧩 兜底：数值裁剪（无前端依赖）")
            W, H = img.size
            cx = st.slider("中心X", 0, W, W // 2)
            cy = st.slider("中心Y", 0, H, H // 2)
            half = int(crop_size) // 2
            x1, y1 = max(0, cx - half), max(0, cy - half)
            x2, y2 = min(W, cx + half), min(H, cy + half)
            rect = (x1, y1, x2, y2)

        # 生成 patch
        if img and rect:
            x1, y1, x2, y2 = map(int, rect)
            x2, y2 = max(x2, x1 + 4), max(y2, y1 + 4)
            patch = img.crop((x1, y1, x2, y2))
        st.session_state["__patch__"] = patch
    else:
        st.info("请先上传图片")

with colR:
    st.subheader("推荐结果")
    patch = st.session_state.get("__patch__")
    if patch:
        prev_w = int(patch.size[0] * float(zoom_ratio))
        prev_h = int(patch.size[1] * float(zoom_ratio))
        st.image(patch.resize((prev_w, prev_h), Image.LANCZOS), caption="预览区域", use_column_width=False)

    rec_btn = st.button("🔎 识别该区域", use_container_width=True, disabled=not bool(patch))
    if rec_btn:
        if cloud_infer is None:
            st.error("云端推理模块不可用")
        elif not DASHSCOPE_AVAILABLE:
            st.error("DashScope SDK 未安装")
        else:
            api_key_now = get_api_key()
            if not api_key_now:
                st.error("DASHSCOPE_API_KEY 缺失")
            else:
                with st.spinner("云端识别中..."):
                    result = cloud_infer(patch, engine=engine, lang=lang, enable_web=enable_web, k_per_query=k_per_query)
                render_result_block(result, engine)

    # 兜底：整图识别
    if (not patch) and uploaded_file and 'img' in locals() and isinstance(img, Image.Image):
        if st.button("🔎 直接识别整图（兜底）", use_container_width=True):
            if cloud_infer is None:
                st.error("云端推理模块不可用")
            elif not DASHSCOPE_AVAILABLE:
                st.error("DashScope SDK 未安装")
            else:
                api_key_now = get_api_key()
                if not api_key_now:
                    st.error("DASHSCOPE_API_KEY 缺失")
                else:
                    with st.spinner("云端识别中..."):
                        result = cloud_infer(img, engine=engine, lang=lang, enable_web=enable_web, k_per_query=k_per_query)
                    render_result_block(result, engine)

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
