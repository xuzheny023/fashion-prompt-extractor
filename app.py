# app.py
import streamlit as st
import json
from PIL import Image
import numpy as np
import cv2

from src.bg_remove import get_foreground_mask
from src.attr_extract import extract_attributes
from src.fabric_ranker import recommend_fabrics, save_rules_weights
from src.utils import validate_fabric_rules
from pathlib import Path

# ================= 页面配置 =================
st.set_page_config(page_title="AI Fashion Fabric Analyst", layout="centered")

# ================= i18n =================
i18n = {
    "en": {
        "app_title": "AI Fashion Fabric Analyst",
        "caption": "Upload a fashion image → background mask → extract attributes → fabric suggestions",
        "sidebar_weight_header": "Scoring Weight",
        "color_weight": "Color weight",
        "exp_weight": "Current weight",
        "save_default": "Save default (fabric_rules.json)",
        "saved_msg": "Saved! Default color weight updated.",
        "exp_fine_preview": "Fabric library (fine-grained) preview",
        "search": "Search",
        "no_entries": "No entries to display.",
        "rules_failed": "Fabric fine rules validation failed:",
        "uploader": "Upload a fashion image",
        "gen_mask": "Generating mask...",
        "detected_attrs": "Detected Attributes",
        "candidates": "Candidate Fabrics",
        "use_fine": "Use fine-grained fabric list",
        "fine_unavailable": "Fine rules unavailable: {err}. Falling back to coarse list.",
        "show_mask": "Show mask overlay (debug)",
        "drop_to_start": "Drag & drop a JPG/PNG above to start.",
        "col_name": "name",
        "col_alias": "alias",
        "col_sheen": "sheen_range",
        "col_edge": "edge_range",
        "col_notes": "notes",
    },
    "zh": {
        "app_title": "AI 服装面料分析师",
        "caption": "上传时装图片 → 背景分割 → 提取属性 → 面料推荐",
        "sidebar_weight_header": "打分权重",
        "color_weight": "颜色权重",
        "exp_weight": "当前权重",
        "save_default": "保存默认（fabric_rules.json）",
        "saved_msg": "已保存！默认颜色权重已更新。",
        "exp_fine_preview": "面料库（细粒度）预览",
        "search": "搜索",
        "no_entries": "没有可展示的条目。",
        "rules_failed": "细粒度面料规则校验失败：",
        "uploader": "上传时装图片",
        "gen_mask": "生成掩膜中...",
        "detected_attrs": "检测到的属性",
        "candidates": "候选面料",
        "use_fine": "使用细粒度面料清单",
        "fine_unavailable": "细粒度规则不可用：{err}，已回退到粗粒度列表。",
        "show_mask": "显示掩膜覆盖（调试）",
        "drop_to_start": "拖拽 JPG/PNG 到上方开始。",
        "col_name": "名称",
        "col_alias": "别名",
        "col_sheen": "高光范围",
        "col_edge": "边缘密度范围",
        "col_notes": "备注",
    },
}

if "lang" not in st.session_state:
    st.session_state.lang = "zh"

lang = st.sidebar.selectbox("Language / 语言", ("en", "zh"), index=(0 if st.session_state.lang == "en" else 1))
st.session_state.lang = lang
T = i18n[lang]

# Validate fine fabric rules at startup
ok, errs = validate_fabric_rules(str(Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"))
if not ok:
    st.error(T["rules_failed"] + "\n" + "\n".join(errs))

st.title("👗 " + T["app_title"])
st.caption(T["caption"])

# ================= 侧边栏：权重调节 =================
st.sidebar.header("⚙️ " + T["sidebar_weight_header"])
w_color = st.sidebar.slider(T["color_weight"], 0.0, 1.0, 1.00, 0.01)
weights = {"color": w_color}

with st.sidebar.expander(T["exp_weight"]):
    st.write(weights)

if st.sidebar.button(T["save_default"]):
    save_rules_weights(weights)
    st.sidebar.success(T["saved_msg"])

# Fine-grained fabric library preview
with st.sidebar.expander(T["exp_fine_preview"]):
    try:
        rules_path = Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"
        fabrics = []
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                fabrics = json.load(f)
        query = st.text_input(T["search"], "")
        q = (query or "").strip().lower()

        def _match(item: dict) -> bool:
            text = " ".join([
                str(item.get("name", "")),
                ",".join(item.get("alias", [])),
                str(item.get("notes", "")),
            ]).lower()
            return q in text

        filt = [it for it in fabrics if _match(it)] if q else fabrics
        col_name = T["col_name"]
        col_alias = T["col_alias"]
        col_sheen = T["col_sheen"]
        col_edge = T["col_edge"]
        col_notes = T["col_notes"]
        rows = []
        for it in filt[:50]:
            rows.append({
                col_name: it.get("name", ""),
                col_alias: ", ".join(it.get("alias", [])),
                col_sheen: str(it.get("sheen_range", "")),
                col_edge: str(it.get("edge_range", "")),
                col_notes: it.get("notes", ""),
            })
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info(T["no_entries"])
    except Exception as e:
        st.info(f"Unable to load fabric library: {e}")

# ================= 主功能区 =================
uploaded_file = st.file_uploader(T["uploader"], type=["jpg", "jpeg", "png"], accept_multiple_files=False)
if uploaded_file is not None and getattr(uploaded_file, 'size', None) is not None:
    if uploaded_file.size > 20 * 1024 * 1024:
        st.error("File too large. Max 20MB.")
        uploaded_file = None

if uploaded_file:
    # 原图展示
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption=T["uploader"], use_container_width=True)

    # 生成 mask（内部使用，不展示）
    with st.spinner(T["gen_mask"]):
        mask, _ = get_foreground_mask(image)

    # 属性提取
    attrs = extract_attributes(image, mask)
    st.markdown("### 🔍 " + T["detected_attrs"])
    st.json(attrs)

    use_fine = st.checkbox(T["use_fine"], value=True)
    # 面料推荐（支持 coarse/fine 源），fine 异常回退 coarse
    st.markdown("### 🧵 " + T["candidates"])
    rules_source = "fine" if use_fine else "coarse"
    try:
        candidates = recommend_fabrics(attrs, top_k=5, weights_override=weights, rules_source=rules_source)
    except Exception as e:
        if rules_source == "fine":
            st.warning(T["fine_unavailable"].format(err=e))
            candidates = recommend_fabrics(attrs, top_k=5, weights_override=weights, rules_source="coarse")
        else:
            raise

    # 渲染，若含 notes 则显示灰字摘要
    for i, item in enumerate(candidates, 1):
        if len(item) == 3:
            name, score, notes = item
            note_snip = (notes[:30] + "…") if isinstance(notes, str) and len(notes) > 30 else notes
            st.write(f"{i}. {name} — **{score:.2f}**  ")
            if note_snip:
                st.caption(str(note_snip))
        else:
            name, score = item
            st.write(f"{i}. {name} — **{score:.2f}**")

    # 可选：调试开关，叠加 mask 预览
    if st.toggle(T["show_mask"]):
        overlay = np.array(image).copy()
        over = overlay.copy()
        over[mask > 0] = (255, 0, 0)  # 红色标记前景
        preview = cv2.addWeighted(overlay, 0.7, over, 0.3, 0)
        st.image(preview, caption="Mask Overlay", use_container_width=True)

else:
    st.info(T["drop_to_start"])
