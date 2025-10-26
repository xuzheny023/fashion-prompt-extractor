# -*- coding: utf-8 -*-
"""
AI Fashion Fabric Analyst - 重构版

使用组件化 UI 设计
"""
import streamlit as st
from PIL import Image
import io

# 页面配置
st.set_page_config(
    page_title="AI Fashion Fabric Analyst",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入 UI 组件
from ui.components import (
    render_analysis_panel,
    render_recommend_panel,
    render_confidence_panel,
    render_actions_panel,
    render_history_panel
)
from ui.components.history_panel import save_to_history

# 导入核心功能
from src.utils.logger import get_logger
from src.ui.icons import E

log = get_logger("app")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title(f"👔 面料分析器")
    st.caption("AI-Powered Fabric Recognition")
    
    # 上传图片
    uploaded_file = st.file_uploader(
        "📤 上传面料图片",
        type=["jpg", "jpeg", "png"],
        help="支持 JPG、PNG 格式"
    )
    
    st.divider()
    
    # 参数设置
    with st.expander(f"{E('actions')} 参数设置", expanded=False):
        top_k = st.slider("候选数量 Top-K", 5, 50, 12)
        enable_zoom = st.checkbox("启用预览放大", value=True)
        save_hist = st.checkbox("保存到历史", value=True)

# ==================== 主区域 ====================
left, right = st.columns([1.1, 1])

with left:
    st.subheader(f"{E('upload')} 上传与预览")
    if uploaded_file is None:
        st.info("请在左侧上传一张面料或服装图片")
    else:
        bytes_data = uploaded_file.read()
        image = Image.open(io.BytesIO(bytes_data)).convert("RGB")
        st.image(image, caption=uploaded_file.name, use_column_width=True)
        st.session_state["last_upload"] = bytes_data

with right:
    st.subheader(f"{E('analysis')} 分析与推荐")
    if uploaded_file is None:
        st.caption("等待上传...")
    else:
        # 1) 分析面板（颜色/光泽/纹理等特征提取）
        analysis = render_analysis_panel(image)

        # 2) 推荐面板（调用云端服务）
        result = render_recommend_panel(
            image=image,
            analysis=analysis,
            top_k=top_k,
            enable_zoom=enable_zoom
        )

        # 3) 置信度/解释面板
        if result:
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
