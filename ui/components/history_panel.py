# -*- coding: utf-8 -*-
"""
历史记录面板组件

显示：
- 分析历史
- 快速回顾
- 历史对比
"""
import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
import json
from pathlib import Path


# 历史记录存储路径
HISTORY_FILE = Path("logs/analysis_history.jsonl")


def render_history_panel(max_items: int = 10):
    """
    渲染历史记录面板
    
    Args:
        max_items: 显示最近 N 条记录
    """
    st.subheader("📜 历史记录")
    
    history = _load_history(max_items)
    
    if not history:
        st.info("暂无历史记录")
        return
    
    # 统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总记录数", len(history))
    with col2:
        avg_time = sum(h.get("time_ms", 0) for h in history) / len(history)
        st.metric("平均耗时", f"{avg_time:.0f}ms")
    with col3:
        avg_score = sum(h.get("top1_score", 0) for h in history) / len(history)
        st.metric("平均置信度", f"{avg_score:.2%}")
    
    st.divider()
    
    # 历史列表
    for i, record in enumerate(history):
        with st.expander(
            f"🕐 {record.get('timestamp', 'Unknown')} - {record.get('top1_label', 'N/A')}",
            expanded=(i == 0)
        ):
            _render_history_item(record)
    
    # 清除历史
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清除历史", use_container_width=True):
            _clear_history()
            st.rerun()
    with col2:
        if st.button("📥 导出历史", use_container_width=True):
            _export_history(history)


def _render_history_item(record: Dict[str, Any]):
    """渲染单条历史记录"""
    
    # 基本信息
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Top 1:** {record.get('top1_label', 'N/A')}")
        st.write(f"**置信度:** {record.get('top1_score', 0):.2%}")
    with col2:
        st.write(f"**耗时:** {record.get('time_ms', 0)}ms")
        st.write(f"**推理:** {record.get('ai_reason', 'CLIP')}")
    
    # 完整结果
    if 'results' in record:
        st.write("**所有结果:**")
        for i, item in enumerate(record['results'][:5], 1):
            st.text(f"{i}. {item['label']}: {item['score']:.2%}")


def save_to_history(
    result,
    meta,
    image_name: str = "unknown"
):
    """
    保存分析结果到历史
    
    Args:
        result: RankedResult 对象
        meta: QueryMeta 对象
        image_name: 图片名称
    """
    from src.types import RankedResult, QueryMeta
    
    if not isinstance(result, RankedResult) or not isinstance(meta, QueryMeta):
        return
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "image_name": image_name,
        "top1_label": result.top1.label if result.top1 else "N/A",
        "top1_score": result.top1.score if result.top1 else 0.0,
        "time_ms": meta.ms,
        "coarse_max": meta.coarse_max,
        "ai_reason": result.ai_reason,
        "results": [
            {"label": item.label, "score": item.score}
            for item in result.items
        ]
    }
    
    # 确保目录存在
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 追加到文件
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def _load_history(max_items: int = 10) -> List[Dict[str, Any]]:
    """加载历史记录"""
    
    if not HISTORY_FILE.exists():
        return []
    
    history = []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
    except Exception:
        return []
    
    # 返回最近的 N 条
    return history[-max_items:][::-1]  # 倒序


def _clear_history():
    """清除历史记录"""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    st.success("✓ 历史记录已清除")


def _export_history(history: List[Dict[str, Any]]):
    """导出历史记录"""
    
    json_str = json.dumps(history, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="⬇️ 下载历史记录",
        data=json_str,
        file_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )


def render_comparison_panel(history: List[Dict[str, Any]]):
    """
    渲染对比面板
    
    Args:
        history: 历史记录列表
    """
    st.subheader("📊 历史对比")
    
    if len(history) < 2:
        st.info("至少需要 2 条记录才能对比")
        return
    
    # 选择要对比的记录
    options = [
        f"{h['timestamp'][:19]} - {h.get('top1_label', 'N/A')}"
        for h in history
    ]
    
    selected = st.multiselect(
        "选择要对比的记录",
        options=options,
        max_selections=3
    )
    
    if len(selected) >= 2:
        selected_indices = [options.index(s) for s in selected]
        selected_records = [history[i] for i in selected_indices]
        
        _render_comparison_table(selected_records)


def _render_comparison_table(records: List[Dict[str, Any]]):
    """渲染对比表格"""
    
    import pandas as pd
    
    data = {
        "时间": [r['timestamp'][:19] for r in records],
        "Top 1": [r.get('top1_label', 'N/A') for r in records],
        "置信度": [f"{r.get('top1_score', 0):.2%}" for r in records],
        "耗时(ms)": [r.get('time_ms', 0) for r in records],
        "推理方式": [r.get('ai_reason', 'CLIP') for r in records],
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # 趋势分析
    st.divider()
    st.write("**趋势分析:**")
    
    scores = [r.get('top1_score', 0) for r in records]
    times = [r.get('time_ms', 0) for r in records]
    
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart({"置信度": scores})
    with col2:
        st.line_chart({"耗时(ms)": times})

