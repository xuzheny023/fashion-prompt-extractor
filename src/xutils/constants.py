# -*- coding: utf-8 -*-
from __future__ import annotations

PREVIEW_WIDTH = 720               # 棰勮鍥惧浐瀹氬搴︼紙鐐瑰嚮鍧愭爣鏉ユ簮锛?DEFAULT_MAX_SIDE = 1024           # 鍒嗘瀽鍥炬渶闀胯竟锛堟彁閫燂級
DEFAULT_SLIC = {"n_segments": 180, "compactness": 10.0}
DEFAULT_HYBRID = {"enabled": True, "radius": 21, "alpha": 0.7}
SMALL_COMPONENT_AREA = 256        # 灏忚繛閫氬煙鍓旈櫎闃堝€?
__all__ = [
    "PREVIEW_WIDTH",
    "DEFAULT_MAX_SIDE",
    "DEFAULT_SLIC",
    "DEFAULT_HYBRID",
    "SMALL_COMPONENT_AREA",
]

