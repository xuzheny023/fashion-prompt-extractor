# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Dict, List, Tuple, Any

from src.fabric_ranker import recommend_fabrics, _load_rules
from pathlib import Path
try:
    from src.calibrator import load_logreg
except Exception:
    def load_logreg():
        return lambda _feat: {}


def recommend_for_region(
    region_id: int,
    features_or_index: Dict[str, Any] | Dict[int, Dict[str, Any]],
    *args,
    **kwargs,
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Two-liner wrapper: pick feat_dict by region_id then score via score_by_features.
    Returns [(key, score, explain_dict)].
    """
    # Backward-compatible args parsing
    rules = kwargs.get("rules")
    weights = kwargs.get("weights") or kwargs.get("weights_override") or {}
    topk = int(kwargs.get("topk", 5))

    if isinstance(features_or_index, dict) and "attrs" in features_or_index:
        feat_dict = features_or_index
    else:
        feat_dict = (features_or_index or {}).get(int(region_id), {})

    scored = score_by_features(feat_dict, rules, weights)
    items = sorted(scored.items(), key=lambda kv: kv[1].get("total", 0.0), reverse=True)[:max(0, int(topk))]
    return [(k, v.get("total", 0.0), {"sig_hits": v.get("sig_hits", []), "cont_parts": v.get("parts", {})}) for k, v in items]


def score_by_features(
    feat_dict: Dict[str, Any],
    rules: List[Dict[str, Any]] | None,
    weights: Dict[str, float],
) -> Dict[str, Dict[str, Any]]:
    """
    Internal scorer: robust defaults, min-max normalization, and simple explain.
    Returns {fabric: {"total": float, "parts": {color, gloss, texture}, "sig_hits": []}}
    """
    attrs = feat_dict.get("attrs", {}) if isinstance(feat_dict, dict) else {}
    # Reuse existing recommend_fabrics to get base totals (robust to missing fields)
    try:
        res = recommend_fabrics(attrs, top_k=64, weights_override=weights, rules_source="coarse")
    except Exception:
        res = []
    # Min-max normalize
    vals = [float(x[1]) for x in res] if res else []
    vmin = min(vals) if vals else 0.0
    vmax = max(vals) if vals else 1.0
    rng = (vmax - vmin) if (vmax - vmin) > 1e-9 else 1.0
    # Continuous parts summary from attrs (robust defaults)
    vis = attrs.get("visual", {}) if isinstance(attrs, dict) else {}
    parts = {
        "color": 0.5,
        "gloss": float(vis.get("coverage_ratio", 0.5)),
        "texture": float(vis.get("texture_proxy", 0.5)),
    }
    out: Dict[str, Dict[str, Any]] = {}
    for it in res:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            name = str(it[0])
            total_raw = float(it[1])
            total = (total_raw - vmin) / rng
            out[name] = {"total": float(total), "parts": dict(parts), "sig_hits": []}

    # Blend with calibrator probabilities if model exists
    try:
        project_root = Path(__file__).resolve().parents[1]
        model_path = project_root / "models" / "logreg.pkl"
        if model_path.exists():
            predict_proba = load_logreg()
            # choose feature vector source: prefer low-level features if present
            feat_low = feat_dict.get("features", {}) if isinstance(feat_dict, dict) else {}
            probs = predict_proba(feat_low)
            if probs:
                for k, v in out.items():
                    p = float(probs.get(k, 0.0))
                    v["prob"] = p
                    v["total"] = float(0.6 * float(v.get("total", 0.0)) + 0.4 * p)
    except Exception:
        pass
    return out


def recommend_from_features(
    feat_dict: Dict[str, Any],
    rules: List[Dict[str, Any]] | None,
    weights: Dict[str, float],
    topk: int = 5,
) -> List[Tuple[str, float, Dict[str, Any]]]:
    scored = score_by_features(feat_dict, rules, weights)
    items = sorted(scored.items(), key=lambda kv: kv[1].get("total", 0.0), reverse=True)[:max(0, int(topk))]
    return [(k, v.get("total", 0.0), {"sig_hits": v.get("sig_hits", []), "cont_parts": v.get("parts", {})}) for k, v in items]


def fuse_region_and_local_scores(
    region_scores: Dict[str, Dict[str, Any]] | List[Tuple[str, float]] | None,
    local_scores: Dict[str, Dict[str, Any]] | List[Tuple[str, float]] | List[Tuple[str, float, Dict[str, Any]]] | None,
    alpha: float,
) -> Dict[str, Dict[str, Any]]:
    """
    Fuse two sources with weighted total and merged explain, tagging entries.
    Returns dict {fabric: {"total": float, "explain": [str,...]}}
    """
    def to_dict(obj) -> Dict[str, Dict[str, Any]]:
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        out: Dict[str, Dict[str, Any]] = {}
        if isinstance(obj, list):
            for it in obj:
                if isinstance(it, (list, tuple)) and len(it) >= 2:
                    name = str(it[0])
                    total = float(it[1])
                    out[name] = {"total": total, "explain": []}
        return out

    R = to_dict(region_scores)
    L = to_dict(local_scores)

    def _normalize(d: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        if not d:
            return {}
        vals = [float(v.get("total", 0.0)) for v in d.values()]
        vmin = min(vals)
        vmax = max(vals)
        rng = vmax - vmin
        out: Dict[str, Dict[str, Any]] = {}
        for k, v in d.items():
            if rng <= 1e-9:
                nv = 0.5
            else:
                nv = (float(v.get("total", 0.0)) - vmin) / rng
            out[k] = {**v, "total": float(nv)}
        return out

    # Min-max normalize both sides to avoid scale mismatch
    Rn = _normalize(R)
    Ln = _normalize(L)
    a = float(max(0.0, min(1.0, alpha)))
    b = 1.0 - a
    keys = set(Rn.keys()) | set(Ln.keys())
    fused: Dict[str, Dict[str, Any]] = {}
    for k in keys:
        tr = float(Rn.get(k, {}).get("total", 0.0))
        tl = float(Ln.get(k, {}).get("total", 0.0))
        ex = []
        if Rn.get(k) is not None:
            ex.append("[region]")
        if Ln.get(k) is not None:
            ex.append("[local]")
        fused[k] = {"total": a * tr + b * tl, "explain": ex}
    return fused


