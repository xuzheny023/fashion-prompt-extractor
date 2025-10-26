# -*- coding: utf-8 -*-
import streamlit as st
from typing import Any, Dict, List, Optional
from PIL import Image
import io
from datetime import datetime

_HISTORY_KEY = "history_items"

def _ensure_state():
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []

def save_to_history(image_bytes: bytes, result: Dict[str, Any]):
    _ensure_state()
    st.session_state[_HISTORY_KEY].append({
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image": image_bytes,
        "result": result or {},
    })

def render_history_panel():
    _ensure_state()
    items: List[Dict[str, Any]] = st.session_state[_HISTORY_KEY]
    st.subheader("历史记录")
    if not items:
        st.info("暂无历史记录")
        return
    for i, item in enumerate(reversed(items), 1):
        with st.expander(f"[{i}] {item['ts']}"):
            img = Image.open(io.BytesIO(item["image"]))
            st.image(img, caption=f"历史图片 {i}", use_column_width=True)
            st.json(item["result"])
