# -*- coding: utf-8 -*-
"""
AI Fashion Fabric Analyst - 新 UI（带降级容错 + 阿里云适配）
"""
import os, io, json, base64, requests
import streamlit as st
from PIL import Image

from src.utils.logger import get_logger
from src.ui.icons import E
from ui.components.history_panel import save_to_history, render_history_panel as _render_history_panel_builtin

log = get_logger("app_new")

# ==================== 组件导入（带降级） ====================
try:
    from ui.components import (
        render_analysis_panel,
        render_recommend_panel,
        render_confidence_panel,
        render_actions_panel,
        render_history_panel,
    )
    _HAS_FULL_COMPONENTS = True
except Exception as e:
    log.warning(f"ui.components 未完整可用，使用最小实现。原因: {e}")
    _HAS_FULL_COMPONENTS = False

    def render_analysis_panel(image: Image.Image):
        w, h = image.size
        return {"width": w, "height": h}

    def _call_cloud_api(image: Image.Image, top_k: int):
        url = os.getenv("FABRIC_API_URL")
        if not url:
            return {"error": "FABRIC_API_URL 未设置"}
        provider = os.getenv("FABRIC_PROVIDER", "aliyun_api_key")
        api_key = os.getenv("FABRIC_API_KEY")

        # 准备图片（base64）
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        headers = {"Content-Type": "application/json"}
        if provider == "aliyun_api_key" and api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        elif api_key:  # 通用 Bearer
            headers["Authorization"] = f"Bearer {api_key}"

        # 选择兼容/原生
        is_compatible = ("/compatible-mode/" in url) or url.endswith("/chat/completions")

        if is_compatible:
            payload = {
                "model": os.getenv("FABRIC_MODEL", "qwen3-vl-flash"),
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "你是纺织面料专家。请识别面料并仅输出 JSON:{material,texture,color,gloss,notes}"},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{img_b64}"}
                    ]
                }],
                "temperature": 0.2
            }
        else:
            payload = {
                "model": os.getenv("FABRIC_MODEL", "qwen3-vl-flash"),
                "input": {
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "你是纺织面料专家。请识别面料并仅输出 JSON:{material,texture,color,gloss,notes}"},
                            {"type": "input_image", "image_url": f"data:image/png;base64,{img_b64}"}
                        ]
                    }]
                },
                "parameters": {"temperature": 0.2}
            }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
        except Exception as e:
            return {"error": f"request failed: {e}"}

        if resp.status_code != 200:
            return {"error": f"cloud status {resp.status_code}", "detail": resp.text[:1000]}

        try:
            data = resp.json()
        except Exception:
            return {"raw": resp.text}

        # 解析输出文本
        text = None
        if is_compatible:
            try:
                text = data["choices"][0]["message"]["content"]
            except Exception:
                text = None
        else:
            out = data.get("output") or {}
            text = out.get("text") or ((out.get("choices") or [{}])[0].get("message") or {}).get("content")

        result = {"raw": data}
        if text:
            result["text"] = text
            # 如果模型严格按照 JSON 输出，转成对象供下游使用
            try:
                result["json"] = json.loads(text)
            except Exception:
                pass
        return result

    def render_recommend_panel(image: Image.Image, analysis, top_k: int = 12, enable_zoom: bool = True):
        st.markdown("**云端结果**")
        data = _call_cloud_api(image, top_k=top_k)
        if "error" in data:
            st.error(f"云端请求失败：{data['error']}")
            if "detail" in data:
                st.code(data["detail"][:800])
            return None
        items = data.get("items") or data.get("results") or []
        if items:
            cols = st.columns(4)
            for i, it in enumerate(items[:top_k]):
                with cols[i % 4]:
                    st.image(it.get("image_url") or it.get("thumb"), use_column_width=True)
                    st.caption(f"score: {it.get('score')}")
        elif data.get("json"):
            st.json(data["json"])
        elif data.get("text"):
            st.markdown(data["text"])
        else:
            st.info("云端无结构化结果返回")
        return data

    def render_confidence_panel(result):
        st.markdown("**置信度 / 原始返回**")
        st.json(result.get("raw", result))

    def render_actions_panel():
        st.markdown("**操作**")
        st.download_button(
            label="导出当前会话JSON",
            file_name="session.json",
            mime="application/json",
            data=json.dumps(st.session_state.get("session_export", {}), ensure_ascii=False).encode("utf-8")
        )

    def render_history_panel():
        return _render_history_panel_builtin()

# ==================== 页面配置 ====================
st.set_page_config(page_title="AI Fashion Fabric Analyst", page_icon="👔", layout="wide", initial_sidebar_state="expanded")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("👔 面料分析器 (Cloud)")
    st.caption("AI-Powered Fabric Recognition")
    uploaded_file = st.file_uploader("📤 上传面料图片", type=["jpg", "jpeg", "png"])
    st.divider()
    with st.expander(f"{E('actions')} 参数设置", expanded=False):
        top_k = st.slider("候选数量 Top-K", 5, 50, 12)
        enable_zoom = st.checkbox("启用预览放大", value=True)
        save_hist = st.checkbox("保存到历史", value=True)

# ==================== 主区域 ====================
left, right = st.columns([1.1, 1])

with left:
    st.subheader(f"{E('upload')} 上传与预览")
    if not uploaded_file:
        st.info("请在左侧上传一张面料或服装图片")
        image = None
    else:
        data = uploaded_file.read()
        image = Image.open(io.BytesIO(data)).convert("RGB")
        st.image(image, caption=uploaded_file.name, use_column_width=True)
        st.session_state["last_upload"] = data

with right:
    st.subheader(f"{E('analysis')} 分析与推荐")
    if image is None:
        st.caption("等待上传...")
    else:
        analysis = render_analysis_panel(image)
        result = render_recommend_panel(image=image, analysis=analysis, top_k=top_k, enable_zoom=enable_zoom)
        if result is not None:
            st.session_state["session_export"] = {
                "analysis": analysis,
                "result": result,
            }
            render_confidence_panel(result)
            if save_hist and "last_upload" in st.session_state:
                save_to_history(st.session_state["last_upload"], result)

# ==================== 底部操作与历史 ====================
st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    render_actions_panel()
with col2:
    render_history_panel()
