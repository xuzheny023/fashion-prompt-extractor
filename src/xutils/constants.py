from __future__ import annotations

PREVIEW_WIDTH = 720               # 预览图固定宽度（点击坐标来源）
DEFAULT_MAX_SIDE = 1024           # 分析图最长边（提速）
DEFAULT_SLIC = {"n_segments": 180, "compactness": 10.0}
DEFAULT_HYBRID = {"enabled": True, "radius": 21, "alpha": 0.7}
SMALL_COMPONENT_AREA = 256        # 小连通域剔除阈值

__all__ = [
    "PREVIEW_WIDTH",
    "DEFAULT_MAX_SIDE",
    "DEFAULT_SLIC",
    "DEFAULT_HYBRID",
    "SMALL_COMPONENT_AREA",
]

