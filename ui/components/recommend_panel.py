# -*- coding: utf-8 -*-
"""
推荐面板组件

调用 core.recommender.recommend 进行面料推荐
包含：
- 4 阶段进度条
- 结果展示（ScoreItem 列表）
- AI 推理说明
"""
import streamlit as st
from PIL import Image
from typing import Optional
import time

from src.core.recommender import recommend
from src.types import RankedResult, QueryMeta
from src.utils.logger import get_logger

log = get_logger("ui.recommend")


def render_recommend_panel(
    image: Optional[Image.Image] = None,
    top_k: int = 5,
    lang: str = "zh"
):
    """
    渲染推荐面板
    
    Args:
        image: PIL 图片对象
        top_k: 返回前 K 个结果
        lang: 语言（"zh" 或 "en"）
    """
    st.subheader("🎯 面料推荐")
    
    if image is None:
        st.info("📤 上传图片开始推荐")
        return
    
    # 创建进度条容器
    progress_container = st.empty()
    status_container = st.empty()
    
    try:
        # 阶段1: 加载数据 (5%)
        with progress_container:
            progress_bar = st.progress(0.05, text="🔄 加载数据...")
        time.sleep(0.1)  # 短暂延迟以显示进度
        
        # 阶段2: 编码查询 (25%)
        progress_bar.progress(0.25, text="🧠 CLIP 编码中...")
        t0 = time.perf_counter()
        
        # 调用推荐引擎
        result, meta = recommend(image, top_k=top_k, lang=lang)
        
        # 阶段3: 粗排 (40%)
        progress_bar.progress(0.40, text="🔍 类中心粗排...")
        time.sleep(0.05)
        
        # 阶段4: 精排 (85%)
        progress_bar.progress(0.85, text="✨ 类内精排...")
        time.sleep(0.05)
        
        # 完成 (100%)
        progress_bar.progress(1.0, text=f"✅ 完成 ({meta.ms}ms)")
        time.sleep(0.3)
        
        # 清除进度条
        progress_container.empty()
        
        # 显示性能指标
        with status_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("耗时", f"{meta.ms} ms")
            with col2:
                st.metric("粗排最高分", f"{meta.coarse_max:.2f}")
            with col3:
                speed_status = "🚀 快速" if meta.is_fast() else "⏱️ 正常"
                st.metric("速度", speed_status)
        
        st.divider()
        
        # 保存到 session_state（供其他面板使用）
        st.session_state.last_result = result
        st.session_state.last_meta = meta
        
        # 显示推荐结果
        _render_results(result, meta)
        
    except FileNotFoundError as e:
        progress_container.empty()
        st.error("❌ 向量库未找到")
        st.info("💡 请先运行：`python tools/build_fabric_bank.py`")
        log.error(f"向量库未找到: {e}")
        
    except Exception as e:
        progress_container.empty()
        st.error(f"❌ 推荐失败：{e}")
        log.exception("推荐失败")
        
        with st.expander("🔍 错误详情"):
            st.code(str(e))


def _render_results(result: RankedResult, meta: QueryMeta):
    """渲染推荐结果"""
    
    # AI 推理说明
    if result.ai_reason:
        if "AI" in result.ai_reason:
            st.info(f"🤖 {result.ai_reason}")
        else:
            st.caption(f"💡 {result.ai_reason}")
    
    # 结果列表
    st.markdown("### 推荐结果")
    
    for i, item in enumerate(result.items, 1):
        with st.container():
            # 标题行
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{i}. {item.label}**")
            with col2:
                st.markdown(f"`{item.score:.2%}`")
            
            # 置信度条
            confidence_pct = min(max(item.score, 0.0), 1.0)
            st.progress(confidence_pct)
            
            # 置信度标签
            if item.score >= 0.70:
                st.success("🟢 高置信度", icon="✅")
            elif item.score >= 0.50:
                st.info("🟡 中等置信度", icon="ℹ️")
            elif item.score >= 0.30:
                st.warning("🟠 低置信度", icon="⚠️")
            else:
                st.error("🔴 极低置信度 - 建议人工确认", icon="❌")
            
            st.divider()
    
    # 高置信度过滤
    high_conf = result.filter_by_threshold(0.60)
    if high_conf:
        with st.expander(f"✨ 高置信度结果 (≥60%)", expanded=False):
            for item in high_conf:
                st.write(f"• **{item.label}**: {item.score:.2%}")
    
    # 低置信度警告
    if result.top1 and result.top1.score < 0.50:
        st.warning("""
        ⚠️ **最高置信度较低，建议：**
        1. 检查图片质量（光线、角度、清晰度）
        2. 尝试裁剪到面料区域
        3. 补充更多训练样本
        4. 启用 AI 复核（在 .env 中设置 AI_BACKEND）
        """)


def render_quick_recommend(image: Image.Image, top_k: int = 3):
    """
    快速推荐（无进度条，用于侧边栏等）
    
    Args:
        image: PIL 图片对象
        top_k: 返回前 K 个结果
    """
    try:
        with st.spinner("🔍 分析中..."):
            result, meta = recommend(image, top_k=top_k)
        
        st.caption(f"⚡ {meta.ms}ms")
        
        for i, item in enumerate(result.items, 1):
            st.write(f"{i}. **{item.label}** - {item.score:.2%}")
            
    except Exception as e:
        st.error(f"推荐失败: {e}")

