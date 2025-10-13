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

log = get_logger("app")

# ==================== 侧边栏 ====================
with st.sidebar:
    st.title("👔 面料分析器")
    st.caption("AI-Powered Fabric Recognition")
    
    # 上传图片
    uploaded_file = st.file_uploader(
        "📤 上传面料图片",
        type=["jpg", "jpeg", "png"],
        help="支持 JPG、PNG 格式"
    )
    
    st.divider()
    
    # 参数设置
    with st.expander("⚙️ 参数设置", expanded=False):
        top_k = st.slider("返回结果数", 3, 10, 5)
        lang = st.selectbox("语言", ["zh", "en"], index=0)
        
        st.caption("更多设置请编辑 .env 文件")
    
    st.divider()
    
    # 关于
    with st.expander("ℹ️ 关于", expanded=False):
        st.markdown("""
        **版本:** 2.0 (重构版)
        
        **特性:**
        - 🎯 CLIP 双通道识别
        - 🚀 高性能检索 (< 500ms)
        - 🤖 可选 AI 复核
        - 📊 详细分析报告
        
        **技术栈:**
        - Streamlit UI
        - PyTorch + CLIP
        - NumPy 矩阵运算
        """)

# ==================== 主界面 ====================
st.title("🎨 AI 面料识别与分析")
st.caption("基于 CLIP 双通道向量检索的智能面料识别系统")

# 如果没有上传图片
if uploaded_file is None:
    st.info("👈 请在左侧上传面料图片开始分析")
    
    # 显示示例
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Cotton", caption="示例：棉")
    with col2:
        st.image("https://via.placeholder.com/300x200?text=Silk", caption="示例：丝绸")
    with col3:
        st.image("https://via.placeholder.com/300x200?text=Linen", caption="示例：亚麻")
    
    st.stop()

# ==================== 加载图片 ====================
try:
    image = Image.open(uploaded_file).convert("RGB")
    log.info(f"图片已加载: {uploaded_file.name}, 尺寸: {image.size}")
except Exception as e:
    st.error(f"❌ 图片加载失败: {e}")
    log.error(f"图片加载失败: {e}")
    st.stop()

# ==================== 布局 ====================
# 左栏：图片预览
# 右栏：分析面板

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📷 图片预览")
    st.image(image, use_container_width=True)
    
    # 图片信息
    image_info = {
        "width": image.width,
        "height": image.height,
        "format": image.format or "Unknown",
        "size_kb": len(uploaded_file.getvalue()) / 1024
    }

with right_col:
    # 使用 tabs 组织右侧面板
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 推荐",
        "📊 分析",
        "📈 置信度",
        "⚡ 操作",
        "📜 历史"
    ])
    
    with tab1:
        # 推荐面板（包含进度条）
        render_recommend_panel(
            image=image,
            top_k=top_k,
            lang=lang
        )
        
        # 保存到历史（如果推荐成功）
        if 'last_result' in st.session_state and 'last_meta' in st.session_state:
            try:
                save_to_history(
                    st.session_state.last_result,
                    st.session_state.last_meta,
                    uploaded_file.name
                )
            except Exception:
                pass
    
    with tab2:
        # 分析面板
        render_analysis_panel(
            image_info=image_info,
            click_coords=None,  # 可以集成点击坐标
            processing_time=st.session_state.get('last_meta', None).seconds if 'last_meta' in st.session_state else None
        )
    
    with tab3:
        # 置信度面板
        if 'last_result' in st.session_state:
            render_confidence_panel(st.session_state.last_result)
        else:
            st.info("请先进行推荐分析")
    
    with tab4:
        # 操作面板
        if 'last_result' in st.session_state:
            render_actions_panel(
                result=st.session_state.last_result,
                meta=st.session_state.get('last_meta'),
                image=image
            )
        else:
            st.info("请先进行推荐分析")
    
    with tab5:
        # 历史记录面板
        render_history_panel(max_items=10)

# ==================== 页脚 ====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 [配置文档](docs/CONFIG_GUIDE.md)")
with col2:
    st.caption("📚 [API 文档](docs/RECOMMENDER_GUIDE.md)")
with col3:
    st.caption("🐛 [问题反馈](https://github.com/your-repo/issues)")

