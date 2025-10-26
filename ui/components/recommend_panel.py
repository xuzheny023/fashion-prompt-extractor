# -*- coding: utf-8 -*-
"""推荐面板 - 极简版"""
import streamlit as st
from PIL import Image
import time, hashlib, io, os
from pathlib import Path
from src.utils.logger import get_logger
from src.fabric_api_infer import analyze_image, NoAPIKeyError

log = get_logger("ui.recommend")

@st.cache_data(show_spinner=False, ttl=3600)
def _cached_analyze_image(path, engine, lang):
    return analyze_image(path, engine=engine, lang=lang)

def _has_api_key():
    try:
        return bool(st.secrets.get("DASHSCOPE_API_KEY")) or bool(os.getenv("DASHSCOPE_API_KEY"))
    except:
        return bool(os.getenv("DASHSCOPE_API_KEY"))

def render_recommend_panel(image=None, crop_size=160, zoom=1.5, top_k=5, lang="zh"):
    if not image:
        st.info("📤 请上传图片开始分析")
        return
    if not _has_api_key():
        st.error("未配置 DASHSCOPE_API_KEY，请在 Secrets 中添加后重试。")
        st.info("""
        **配置步骤：**
        1. 创建 `.streamlit/secrets.toml`
        2. 添加：`DASHSCOPE_API_KEY = "sk-your-key-here"`
        3. 重启应用
        """)
        st.stop()
    col_img, col_info = st.columns([2, 1])
    with col_img:
        try:
            from streamlit_cropper import st_cropper
            cropped_img = st_cropper(image, realtime_update=True, box_color="#66CCFF", aspect_ratio=(1,1), return_type="image")
        except ImportError:
            st.error("请安装 streamlit-cropper")
            st.stop()
    with col_info:
        if cropped_img:
            preview_size = int(crop_size * zoom)
            preview = cropped_img.resize((preview_size, preview_size), Image.Resampling.LANCZOS)
            st.image(preview, caption="预览区域", use_container_width=True)
            st.caption(f"裁剪: {cropped_img.width}×{cropped_img.height} px")
            st.caption(f"预览: {preview_size}×{preview_size} px (×{zoom})")
            st.divider()
            if st.button("🚀 识别该区域", type="primary", use_container_width=True):
                with st.spinner("☁️ 调用云端识别中..."):
                    cache_dir = Path(".cache/crops")
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    img_bytes = io.BytesIO()
                    cropped_img.save(img_bytes, format="PNG")
                    img_hash = hashlib.md5(img_bytes.getvalue()).hexdigest()
                    patch_path = cache_dir / f"{img_hash}.png"
                    cropped_img.save(patch_path, format="PNG")
                    try:
                        t0 = time.perf_counter()
                        res = analyze_image(str(patch_path), engine="cloud_qwen", lang=lang)
                        elapsed_ms = int((time.perf_counter() - t0) * 1000)
                        st.session_state.last_fabric_result = {
                            "materials": res.get("materials", [])[:top_k],
                            "confidences": res.get("confidence", [])[:top_k],
                            "description": res.get("description", ""),
                            "engine": res.get("engine", "cloud_qwen"),
                            "elapsed_ms": elapsed_ms,
                            "crop_path": str(patch_path),
                            "cache_key": img_hash
                        }
                        st.success("✅ 识别完成！")
                        st.rerun()
                    except NoAPIKeyError:
                        st.error("未配置 DASHSCOPE_API_KEY，请在 Secrets 中添加后重试。")
                        st.stop()
                    except Exception as e:
                        error_msg = str(e).lower()
                        st.error(f"❌ 识别失败: {str(e)}")
                        
                        # 提供具体的错误提示
                        if "timeout" in error_msg or "timed out" in error_msg:
                            st.warning("⏱️ **网络超时** - 请检查网络连接或稍后重试")
                        elif "connection" in error_msg or "network" in error_msg:
                            st.warning("🌐 **网络连接问题** - 请检查网络设置")
                        elif "rate limit" in error_msg or "quota" in error_msg or "throttle" in error_msg:
                            st.warning("📊 **API 配额不足** - 请稍后再试或检查账户余额")
                        elif "invalid" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg:
                            st.warning("🔑 **API Key 无效** - 请检查 Secrets 配置")
                        elif "not found" in error_msg or "404" in error_msg:
                            st.warning("🔍 **资源未找到** - 请联系技术支持")
                        else:
                            st.warning("💡 **建议**：检查网络连接、API Key 配置或稍后重试")
                        
                        log.exception("Recognition failed")
                        st.stop()
        else:
            st.info("👈 拖动调整裁剪框")
    st.divider()
    if "last_fabric_result" in st.session_state:
        r = st.session_state.last_fabric_result
        st.caption(f"Engine: {r.get('engine', 'cloud_qwen')}")
        st.divider()
        mats = r.get("materials", [])
        confs = r.get("confidences", [])
        if mats:
            for i, m in enumerate(mats[:3], 1):
                c = confs[i-1] if i-1 < len(confs) else 0.5
                st.markdown(f"**#{i} {m.upper()}** - {c:.0%}")
                st.progress(c, text=f"{m}: {c:.1%}")
        else:
            st.info("未识别到材料")
        st.divider()
        desc = r.get("description", "")
        if desc:
            with st.expander("💡 解释 / Reasoning", expanded=False):
                st.write(desc)
                st.caption("由云端大模型生成")

__all__ = ["render_recommend_panel"]

