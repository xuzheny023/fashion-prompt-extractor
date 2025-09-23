# -*- coding: utf-8 -*-
from __future__ import annotations

# Unified fabric keys (extend as needed)
FABRIC_KEYS = (
    "name",
    "fabric",
    "alias",
    "base",
    "weights",
    "sheen_range",
    "edge_range",
    "notes",
)

# Global defaults
DEFAULT_MAX_SIDE = 1024
DEFAULT_SLIC = {"n_segments": 180, "compactness": 10.0}
DEFAULT_HYBRID = {"enabled": True, "radius": 21, "alpha": 0.7}
PREVIEW_WIDTH = 720

# Heuristic threshold for very small components (pixels)
SMALL_COMPONENT_AREA = 256


