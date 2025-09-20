# app.py
import streamlit as st
import json
from PIL import Image
import numpy as np
import cv2

from src.bg_remove import get_foreground_mask
from src.attr_extract import extract_attributes, localize_attrs
from src.fabric_ranker import recommend_fabrics, save_rules_weights, recommend_fabrics_localized
from src.utils import validate_fabric_rules
from src.i18n import t
from pathlib import Path

# ================= 页面配置 =================
st.set_page_config(page_title="AI Fashion Fabric Analyst", layout="centered")

# ================= 国际化配置 =================
# Initialize language in session state with default zh
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

# Language selector - update session state when changed
lang_options = ("en", "zh")
current_lang = st.session_state["lang"]
selected_index = 0 if current_lang == "en" else 1

new_lang = st.sidebar.selectbox(
    t("sidebar.language", current_lang), 
    lang_options, 
    index=selected_index
)

# Update session state if language changed
if new_lang != current_lang:
    st.session_state["lang"] = new_lang

# Get current language from session state for global use
lang = st.session_state["lang"]


def get_current_lang() -> str:
    """Get current language from session state / 从会话状态获取当前语言"""
    return st.session_state["lang"]


def _get_localized_display_name(fabric_item: dict, lang: str) -> str:
    """Get localized display name for fabric item / 获取面料项目的本地化显示名称"""
    # Try display_name field first
    display_name_data = fabric_item.get("display_name", {})
    if isinstance(display_name_data, dict):
        localized_name = display_name_data.get(lang, "")
        if localized_name:
            return localized_name
    
    # Fallback to alias matching
    aliases = fabric_item.get("alias", [])
    if aliases:
        if lang == "zh":
            # Look for Chinese characters
            for alias in aliases:
                if any('\u4e00' <= char <= '\u9fff' for char in alias):
                    return alias
        else:
            # Look for English alias (no Chinese characters)
            for alias in aliases:
                if not any('\u4e00' <= char <= '\u9fff' for char in alias):
                    return alias
    
    # Final fallback: use name
    return fabric_item.get("name", "Unknown")


def _get_localized_notes(fabric_item: dict, lang: str) -> str:
    """Get localized notes for fabric item / 获取面料项目的本地化说明"""
    # Try notes field first
    notes_data = fabric_item.get("notes", {})
    if isinstance(notes_data, dict):
        localized_notes = notes_data.get(lang, "")
        if localized_notes:
            return localized_notes
    elif isinstance(notes_data, str):
        # Fallback to string notes for backward compatibility
        return notes_data
    
    return ""

# Validate fine fabric rules at startup
ok, errs = validate_fabric_rules(str(Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"))
if not ok:
    st.error(t("msg.validation_failed", get_current_lang()))

st.title("👗 " + t("app.title", get_current_lang()))
st.caption(t("app.subtitle", get_current_lang()))

# ================= 侧边栏：权重调节 =================
st.sidebar.header("⚙️ " + t("sidebar.weight_header", get_current_lang()))
w_color = st.sidebar.slider(t("sidebar.color_weight", get_current_lang()), 0.0, 1.0, 0.5, 0.01)
w_sheen = st.sidebar.slider(t("sidebar.sheen_weight", get_current_lang()), 0.0, 1.0, 0.3, 0.01)
w_texture = st.sidebar.slider(t("sidebar.texture_weight", get_current_lang()), 0.0, 1.0, 0.2, 0.01)

# Auto-normalize weights to sum = 1
total_w = max(w_color + w_sheen + w_texture, 1e-6)
weights = {
    "color": w_color / total_w,
    "sheen": w_sheen / total_w,
    "texture": w_texture / total_w,
}

with st.sidebar.expander(t("sidebar.exp_weight", get_current_lang())):
    st.write(weights)

if st.sidebar.button(t("sidebar.save_default", get_current_lang())):
    save_rules_weights(weights)
    st.sidebar.success(t("sidebar.saved_msg", get_current_lang()))

# Fine-grained fabric library switch
use_fine = st.sidebar.checkbox(t("sidebar.use_fine", get_current_lang()), value=True)

# Fine-grained fabric library preview
with st.sidebar.expander(t("sidebar.fabric_preview", get_current_lang())):
    try:
        rules_path = Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"
        fabrics = []
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                fabrics = json.load(f)
        query = st.text_input(t("sidebar.search_placeholder", get_current_lang()), "")
        q = (query or "").strip().lower()

        def _match(item: dict) -> bool:
            text = " ".join([
                str(item.get("name", "")),
                ",".join(item.get("alias", [])),
                str(item.get("notes", "")),
            ]).lower()
            return q in text

        filt = [it for it in fabrics if _match(it)] if q else fabrics
        col_name = t("sidebar.col_name", get_current_lang())
        col_alias = t("sidebar.col_alias", get_current_lang())
        col_sheen = t("sidebar.col_sheen", get_current_lang())
        col_edge = t("sidebar.col_edge", get_current_lang())
        col_notes = t("sidebar.col_notes", get_current_lang())
        rows = []
        for it in filt[:50]:
            # Use localized display name and notes
            display_name = _get_localized_display_name(it, get_current_lang())
            notes = _get_localized_notes(it, get_current_lang())
            
            rows.append({
                col_name: display_name,
                col_alias: ", ".join(it.get("alias", [])),
                col_sheen: str(it.get("sheen_range", "")),
                col_edge: str(it.get("edge_range", "")),
                col_notes: notes,
            })
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info(t("sidebar.no_entries", get_current_lang()))
    except Exception as e:
        st.info(t("msg.rules_fallback", get_current_lang()))

# ================= 主功能区 =================
uploaded_file = st.file_uploader(t("main.uploader", get_current_lang()), type=["jpg", "jpeg", "png"], accept_multiple_files=False)
if uploaded_file is not None and getattr(uploaded_file, 'size', None) is not None:
    if uploaded_file.size > 20 * 1024 * 1024:
        st.error(t("main.file_size_warning", get_current_lang()))
        uploaded_file = None

if uploaded_file:
    # 原图展示
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption=t("main.uploader", get_current_lang()), use_container_width=True)
    except Exception as e:
        st.error(t("msg.processing_error", get_current_lang()))
        st.stop()

    # 生成 mask（内部使用，不展示）
    with st.spinner(t("main.processing", get_current_lang())):
        try:
            mask, _ = get_foreground_mask(image)
        except Exception as e:
            st.error(t("msg.mask_generation_failed", get_current_lang()))
            st.stop()

    # 属性提取
    try:
        attrs = extract_attributes(image, mask)
        st.markdown("### 🔍 " + t("main.attributes_title", get_current_lang()))
        
        # 显示本地化的属性
        localized_attrs = localize_attrs(attrs, get_current_lang())
        st.json(localized_attrs)
    except Exception as e:
        st.error(t("msg.attribute_extraction_failed", get_current_lang()))
        st.stop()

    # 面料推荐（支持 coarse/fine 源），fine 异常回退 coarse
    st.markdown("### 🧵 " + t("main.candidates_title", get_current_lang()))
    rules_source = "fine" if use_fine else "coarse"
    try:
        candidates = recommend_fabrics_localized(attrs, lang=get_current_lang(), top_k=5, weights_override=weights, rules_source=rules_source)
    except Exception as e:
        if rules_source == "fine":
            st.sidebar.warning(t("msg.rules_fallback", get_current_lang()))
            rules_source = "coarse"  # 强制回退
            candidates = recommend_fabrics_localized(attrs, lang=get_current_lang(), top_k=5, weights_override=weights, rules_source=rules_source)
        else:
            st.error(t("msg.fabric_recommendation_failed", get_current_lang()))
            st.stop()

    # 渲染本地化的面料名称和说明
    for i, item in enumerate(candidates, 1):
        if len(item) == 4:
            name, score, display_name, notes = item
            
            # 确保显示名称不为空，如果为空则使用本地化回退
            if not display_name:
                display_name = name
            
            # 格式化分数显示
            score_label = t("candidates.score", get_current_lang())
            
            # 显示面料名称和分数
            st.write(f"{i}. **{display_name}** — {score_label}: **{score:.2f}**")
            
            # 显示详细说明（截断处理）
            if notes and isinstance(notes, str) and notes.strip():
                # 截断到30字符左右，保持完整性
                max_len = 30
                if len(notes) > max_len:
                    # 找到最近的句号或逗号作为截断点
                    truncate_point = max_len
                    for punct in ['。', '.', '，', ',', '；', ';']:
                        punct_pos = notes.find(punct, 0, max_len)
                        if punct_pos > 0:
                            truncate_point = punct_pos + 1
                            break
                    note_snip = notes[:truncate_point] + "…"
                else:
                    note_snip = notes
                
                desc_label = t("candidates.description", get_current_lang())
                st.caption(f"*{desc_label}: {note_snip}*")
        else:
            # Fallback for unexpected format
            name, score = item[:2]
            score_label = t("candidates.score", get_current_lang())
            st.write(f"{i}. **{name}** — {score_label}: **{score:.2f}**")

    # 可选：调试开关，叠加 mask 预览
    if st.toggle(t("main.mask_toggle", get_current_lang())):
        overlay = np.array(image).copy()
        over = overlay.copy()
        over[mask > 0] = (255, 0, 0)  # 红色标记前景
        preview = cv2.addWeighted(overlay, 0.7, over, 0.3, 0)
        st.image(preview, caption=t("debug.mask_overlay", get_current_lang()), use_container_width=True)

else:
    st.info(t("main.drop_to_start", get_current_lang()))
