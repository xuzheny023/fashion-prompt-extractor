# -*- coding: utf-8 -*-
from __future__ import annotations

PREVIEW_WIDTH = 720               # Preview image width
DEFAULT_MAX_SIDE = 1024           # Max side for analysis
DEFAULT_SLIC = {"n_segments": 180, "compactness": 10.0}
DEFAULT_HYBRID = {"enabled": True, "radius": 21, "alpha": 0.7}
SMALL_COMPONENT_AREA = 256        # Minimum area for tiny connected components removal
__all__ = [
    "PREVIEW_WIDTH",
    "DEFAULT_MAX_SIDE",
    "DEFAULT_SLIC",
    "DEFAULT_HYBRID",
    "SMALL_COMPONENT_AREA",
]

