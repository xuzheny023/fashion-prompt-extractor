# -*- coding: utf-8 -*-
from __future__ import annotations

def optional_import(name: str):
    try:
        return __import__(name)
    except Exception:
        return None


