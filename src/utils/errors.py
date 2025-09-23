# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import contextmanager
import traceback
import streamlit as st


@contextmanager
def swallow(msg: str):
    try:
        yield
    except Exception as e:
        try:
            st.warning(f"{msg}: {e}")
        except Exception:
            # If Streamlit not available in context
            print(f"[warn] {msg}: {e}")
        traceback.print_exc()


