from __future__ import annotations

from typing import Dict


def detect_structures(img_bgr: np.ndarray, fg_mask: np.ndarray | None = None) -> Dict[str, object]:
    """
    Deprecated: use regionizer.py for region-based analysis

    Kept for backward compatibility. Returns a minimal placeholder dict:
    {"conf":{}, "masks":{}, "method":"deprecated"}
    """
    return {"conf": {}, "masks": {}, "method": "deprecated"}


def to_bool_set(conf: Dict[str, float], thr: float = 0.55) -> set[str]:
    """
    Deprecated: use regionizer.py for region-based analysis

    Kept signature for compatibility. Always returns empty set.
    """
    return set()


