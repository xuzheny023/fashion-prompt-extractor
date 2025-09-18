# app.py
import streamlit as st
from PIL import Image
import numpy as np
import cv2

from src.bg_remove import get_foreground_mask
from src.attr_extract import extract_attributes
from src.fabric_ranker import recommend_fabrics, save_rules_weights

# ================= 页面配置 =================
st.set_page_config(page_title="AI Fashion Analyzer", layout="centered")

st.title("👗 AI Fashion Analyzer")
st.caption("Upload a fashion image → internal background mask → extract attributes → fabric suggestions")

# ================= 侧边栏：权重调节 =================
st.sidebar.header("⚙️ Scoring Weights")
w_color = st.sidebar.slider("Color weight", 0.0, 1.0, 0.40, 0.01)
w_sil   = st.sidebar.slider("Silhouette weight", 0.0, 1.0, 0.35, 0.01)
w_len   = st.sidebar.slider("Length weight", 0.0, 1.0, 0.25, 0.01)

# 归一化，确保三者之和 = 1
total_w = max(w_color + w_sil + w_len, 1e-6)
weights = {
    "color": w_color / total_w,
    "silhouette": w_sil / total_w,
    "length": w_len / total_w,
}

with st.sidebar.expander("Current weights (normalized)"):
    st.write(weights)

# 保存按钮
if st.sidebar.button("Save as default (write to fabric_rules.json)"):
    save_rules_weights(weights)
    st.sidebar.success("Saved! New default weights applied.")

# ================= 主功能区 =================
uploaded_file = st.file_uploader("Upload a fashion image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 原图展示
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # 生成 mask（内部使用，不展示）
    with st.spinner("Generating mask..."):
        mask, _ = get_foreground_mask(image)

    # 属性提取
    attrs = extract_attributes(image, mask)
    st.markdown("### 🔍 Detected Attributes")
    st.json(attrs)

    # 面料推荐（传入侧边栏权重）
    candidates = recommend_fabrics(attrs, top_k=5, weights_override=weights)
    st.markdown("### 🧵 Candidate Fabrics")
    for i, (name, score) in enumerate(candidates, 1):
        st.write(f"{i}. {name} — **{score:.2f}**")

    # 可选：调试开关，叠加 mask 预览
    if st.toggle("Show mask overlay (debug)"):
        overlay = np.array(image).copy()
        over = overlay.copy()
        over[mask > 0] = (255, 0, 0)  # 红色标记前景
        preview = cv2.addWeighted(overlay, 0.7, over, 0.3, 0)
        st.image(preview, caption="Mask Overlay", use_container_width=True)

else:
    st.info("Drag & drop a JPG/PNG above to start.")
