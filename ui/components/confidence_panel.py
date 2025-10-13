# -*- coding: utf-8 -*-
"""
置信度面板组件

显示：
- 置信度分布
- 分数统计
- 质量评估
"""
import streamlit as st
from typing import List, Optional
from src.types import RankedResult, ScoreItem


def render_confidence_panel(result: Optional[RankedResult] = None):
    """
    渲染置信度面板
    
    Args:
        result: 推荐结果
    """
    st.subheader("📈 置信度分析")
    
    if result is None or not result.items:
        st.info("暂无推荐结果")
        return
    
    # 统计信息
    scores = [item.score for item in result.items]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("最高分", f"{max(scores):.2%}")
    with col2:
        st.metric("平均分", f"{sum(scores)/len(scores):.2%}")
    with col3:
        st.metric("最低分", f"{min(scores):.2%}")
    
    # 置信度分布
    with st.expander("📊 置信度分布", expanded=True):
        _render_distribution(result.items)
    
    # 质量评估
    with st.expander("🎯 质量评估", expanded=True):
        _render_quality_assessment(result)


def _render_distribution(items: List[ScoreItem]):
    """渲染置信度分布"""
    
    # 分级统计
    high = sum(1 for item in items if item.score >= 0.70)
    medium = sum(1 for item in items if 0.50 <= item.score < 0.70)
    low = sum(1 for item in items if 0.30 <= item.score < 0.50)
    very_low = sum(1 for item in items if item.score < 0.30)
    
    st.write("**分级统计：**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if high > 0:
            st.progress(high / len(items), text=f"🟢 高置信度 (≥70%)")
        if medium > 0:
            st.progress(medium / len(items), text=f"🟡 中等置信度 (50-70%)")
        if low > 0:
            st.progress(low / len(items), text=f"🟠 低置信度 (30-50%)")
        if very_low > 0:
            st.progress(very_low / len(items), text=f"🔴 极低置信度 (<30%)")
    
    with col2:
        st.write(f"{high} 个")
        if medium > 0:
            st.write(f"{medium} 个")
        if low > 0:
            st.write(f"{low} 个")
        if very_low > 0:
            st.write(f"{very_low} 个")
    
    # 详细列表
    st.divider()
    st.write("**详细分数：**")
    for i, item in enumerate(items, 1):
        score_bar = "█" * int(item.score * 20)
        st.text(f"{i}. {item.label:<15} {item.score:.2%} {score_bar}")


def _render_quality_assessment(result: RankedResult):
    """渲染质量评估"""
    
    if not result.top1:
        st.warning("无结果")
        return
    
    top1_score = result.top1.score
    
    # 整体评估
    if top1_score >= 0.80:
        st.success("✅ **优秀** - 识别结果可信度高")
        quality = "excellent"
    elif top1_score >= 0.60:
        st.info("✓ **良好** - 识别结果较为可靠")
        quality = "good"
    elif top1_score >= 0.40:
        st.warning("⚠️ **一般** - 建议结合人工判断")
        quality = "fair"
    else:
        st.error("❌ **较差** - 建议重新拍摄或人工确认")
        quality = "poor"
    
    # 建议
    st.divider()
    st.write("**改进建议：**")
    
    if quality in ["fair", "poor"]:
        st.write("- 📸 确保图片清晰、光线充足")
        st.write("- ✂️ 裁剪到面料主体区域")
        st.write("- 🔄 尝试不同角度拍摄")
        st.write("- 📚 补充更多训练样本")
    
    if quality == "poor":
        st.write("- 🤖 启用 AI 复核（设置 AI_BACKEND）")
    
    # 分数差距分析
    if len(result.items) >= 2:
        gap = result.items[0].score - result.items[1].score
        st.divider()
        st.write("**分数差距分析：**")
        
        if gap >= 0.10:
            st.success(f"✓ 第一名领先明显 (差距 {gap:.2%})")
        elif gap >= 0.05:
            st.info(f"○ 第一名略有优势 (差距 {gap:.2%})")
        else:
            st.warning(f"⚠️ 前两名接近 (差距 {gap:.2%}) - 建议 AI 复核")


def render_score_chart(items: List[ScoreItem]):
    """
    渲染分数图表（使用 Streamlit 原生图表）
    
    Args:
        items: ScoreItem 列表
    """
    import pandas as pd
    
    if not items:
        return
    
    # 准备数据
    data = {
        "面料": [item.label for item in items],
        "置信度": [item.score for item in items]
    }
    df = pd.DataFrame(data)
    
    # 条形图
    st.bar_chart(df.set_index("面料"))

