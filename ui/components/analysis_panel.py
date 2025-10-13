# -*- coding: utf-8 -*-
"""
分析面板组件

显示图片分析信息：
- 坐标信息
- 处理时间
- 图片尺寸
- 其他元数据
"""
import streamlit as st
from typing import Dict, Any, Optional


def render_analysis_panel(
    image_info: Optional[Dict[str, Any]] = None,
    click_coords: Optional[tuple] = None,
    processing_time: Optional[float] = None
):
    """
    渲染分析面板
    
    Args:
        image_info: 图片信息字典 {"width": int, "height": int, "format": str, ...}
        click_coords: 点击坐标 (x, y)
        processing_time: 处理时间（秒）
    """
    st.subheader("📊 分析信息")
    
    if image_info:
        # 图片基本信息
        with st.expander("🖼️ 图片信息", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("宽度", f"{image_info.get('width', 0)} px")
                st.metric("格式", image_info.get('format', 'Unknown'))
            with col2:
                st.metric("高度", f"{image_info.get('height', 0)} px")
                if 'size_kb' in image_info:
                    st.metric("大小", f"{image_info['size_kb']:.1f} KB")
    
    # 点击坐标
    if click_coords:
        with st.expander("📍 点击坐标", expanded=True):
            x, y = click_coords
            st.write(f"**X:** {x} px")
            st.write(f"**Y:** {y} px")
            st.caption(f"坐标: ({x}, {y})")
    
    # 处理时间
    if processing_time is not None:
        with st.expander("⏱️ 性能指标", expanded=True):
            st.metric("处理时间", f"{processing_time*1000:.0f} ms")
            
            if processing_time < 0.2:
                st.success("✨ 性能优秀")
            elif processing_time < 0.5:
                st.info("✓ 性能良好")
            else:
                st.warning("⚠️ 处理较慢")
    
    # 如果没有任何信息
    if not image_info and not click_coords and processing_time is None:
        st.info("📤 上传图片开始分析")


def render_metadata_panel(metadata: Dict[str, Any]):
    """
    渲染元数据面板
    
    Args:
        metadata: 元数据字典
    """
    with st.expander("🔍 详细元数据", expanded=False):
        for key, value in metadata.items():
            st.write(f"**{key}:** {value}")

