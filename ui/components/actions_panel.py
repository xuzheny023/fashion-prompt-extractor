# -*- coding: utf-8 -*-
"""
操作面板组件

提供：
- 导出结果
- 保存图片
- 复制数据
- 其他操作
"""
import streamlit as st
from typing import Optional
import json
from datetime import datetime
from PIL import Image
import io

from src.types import RankedResult, QueryMeta


def render_actions_panel(
    result: Optional[RankedResult] = None,
    meta: Optional[QueryMeta] = None,
    image: Optional[Image.Image] = None
):
    """
    渲染操作面板
    
    Args:
        result: 推荐结果
        meta: 性能指标
        image: 原始图片
    """
    st.subheader("⚡ 操作")
    
    if result is None:
        st.info("暂无可操作的结果")
        return
    
    # 导出 JSON
    if st.button("📥 导出 JSON", use_container_width=True):
        _export_json(result, meta)
    
    # 导出 CSV
    if st.button("📊 导出 CSV", use_container_width=True):
        _export_csv(result, meta)
    
    # 复制结果
    if st.button("📋 复制结果", use_container_width=True):
        _copy_results(result)
    
    # 保存图片（如果有）
    if image:
        st.divider()
        if st.button("💾 保存分析图片", use_container_width=True):
            _save_image(image, result)
    
    # 重新分析
    st.divider()
    if st.button("🔄 重新分析", use_container_width=True, type="primary"):
        st.rerun()


def _export_json(result: RankedResult, meta: Optional[QueryMeta]):
    """导出为 JSON"""
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "rank": i,
                "label": item.label,
                "score": item.score,
                "confidence": f"{item.score:.2%}"
            }
            for i, item in enumerate(result.items, 1)
        ],
        "ai_reason": result.ai_reason,
    }
    
    if meta:
        data["performance"] = {
            "time_ms": meta.ms,
            "coarse_max": meta.coarse_max,
            "is_fast": meta.is_fast()
        }
    
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="⬇️ 下载 JSON",
        data=json_str,
        file_name=f"fabric_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.success("✓ JSON 已生成")


def _export_csv(result: RankedResult, meta: Optional[QueryMeta]):
    """导出为 CSV"""
    
    import pandas as pd
    
    df = pd.DataFrame([
        {
            "排名": i,
            "面料": item.label,
            "分数": item.score,
            "置信度": f"{item.score:.2%}"
        }
        for i, item in enumerate(result.items, 1)
    ])
    
    csv_str = df.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="⬇️ 下载 CSV",
        data=csv_str,
        file_name=f"fabric_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.success("✓ CSV 已生成")


def _copy_results(result: RankedResult):
    """复制结果到剪贴板"""
    
    text = "面料推荐结果\n" + "=" * 40 + "\n\n"
    
    for i, item in enumerate(result.items, 1):
        text += f"{i}. {item.label}: {item.score:.2%}\n"
    
    if result.ai_reason:
        text += f"\n推理方式: {result.ai_reason}\n"
    
    # 使用 Streamlit 的代码块显示（用户可以手动复制）
    st.code(text, language=None)
    st.info("💡 请手动复制上方文本")


def _save_image(image: Image.Image, result: RankedResult):
    """保存分析后的图片"""
    
    # 转换为字节
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    img_bytes = buf.getvalue()
    
    st.download_button(
        label="⬇️ 下载图片",
        data=img_bytes,
        file_name=f"fabric_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png",
        use_container_width=True
    )
    
    st.success("✓ 图片已准备下载")


def render_batch_actions():
    """渲染批量操作面板"""
    
    st.subheader("📦 批量操作")
    
    uploaded_files = st.file_uploader(
        "上传多张图片",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"已选择 {len(uploaded_files)} 张图片")
        
        if st.button("🚀 批量分析", use_container_width=True, type="primary"):
            _batch_analyze(uploaded_files)


def _batch_analyze(files):
    """批量分析"""
    
    from src.core.recommender import recommend
    
    results = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(files):
        try:
            img = Image.open(file)
            result, meta = recommend(img)
            
            results.append({
                "file": file.name,
                "top1": result.top1.label if result.top1 else "N/A",
                "score": result.top1.score if result.top1 else 0.0,
                "time_ms": meta.ms
            })
            
        except Exception as e:
            results.append({
                "file": file.name,
                "top1": "ERROR",
                "score": 0.0,
                "time_ms": 0
            })
        
        progress_bar.progress((i + 1) / len(files))
    
    # 显示结果
    import pandas as pd
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
    
    # 导出
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        "⬇️ 下载批量结果",
        data=csv,
        file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

