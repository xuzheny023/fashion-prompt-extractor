# src/fabric_ranker.py
# -*- coding: utf-8 -*-
"""
基于规则的面料候选打分排序：
- 读取 data/fabric_rules.json
- 根据 attrs['visual'] 的 dominant_color_name / silhouette + attrs['length'] 打分
- 支持运行时 weights_override 覆盖权重；支持保存权重到 JSON
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import json
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = PROJECT_ROOT / "data" / "fabric_rules.json"


@lru_cache(maxsize=1)
def _load_rules() -> Dict:
    if RULES_PATH.exists():
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # 兜底
    return {
        "weights": {"color": 0.4, "silhouette": 0.35, "length": 0.25},
        "color_groups": {
            "light": ["white", "gray", "yellow", "cyan"],
            "mid": ["green", "blue", "purple", "orange"],
            "dark": ["black", "red", "unknown"]
        },
        "rules": [
            {"fabric": "Chiffon", "base": 0.6, "silhouettes": ["A-line", "flare", "straight"],
             "lengths": ["mini", "knee-length", "midi", "maxi"], "preferred_colors": ["light", "mid"]},
            {"fabric": "Satin", "base": 0.6, "silhouettes": ["straight", "fitted", "A-line"],
             "lengths": ["mini", "knee-length", "midi", "maxi"], "preferred_colors": ["mid", "dark"]},
            {"fabric": "Tulle", "base": 0.55, "silhouettes": ["flare", "A-line"],
             "lengths": ["mini", "knee-length", "midi"], "preferred_colors": ["light"]}
        ]
    }


def _map_color_to_group(color_name: str, color_groups: Dict[str, List[str]]) -> str:
    cname = (color_name or "unknown").lower()
    for group, names in color_groups.items():
        if cname in names:
            return group
    return "dark"


def _score_one(rule: Dict, color_group: str, silhouette: str, length: str,
               w_color: float, w_sil: float, w_len: float) -> float:
    score = rule.get("base", 0.5)

    # color
    if rule.get("preferred_colors"):
        score += w_color * (1.0 if color_group in rule["preferred_colors"] else 0.3)

    # silhouette
    sils = rule.get("silhouettes", [])
    if silhouette in sils:
        s = 1.0
    elif silhouette == "A-line" and "flare" in sils:
        s = 0.7
    elif silhouette == "straight" and "fitted" in sils:
        s = 0.7
    else:
        s = 0.3
    score += w_sil * s

    # length
    lens = rule.get("lengths", [])
    if length in lens:
        l = 1.0
    else:
        neighbors = {
            "mini": ["knee-length"],
            "knee-length": ["mini", "midi"],
            "midi": ["knee-length", "maxi"],
            "maxi": ["midi"],
            "top-only": ["mini"]
        }
        l = 0.6 if any(n in lens for n in neighbors.get(length, [])) else 0.3
    score += w_len * l

    return float(score)


def recommend_fabrics(attrs: Dict, top_k: int = 5, weights_override: Dict[str, float] | None = None) -> List[Tuple[str, float]]:
    """
    输出：[(fabric_name, score), ...] 降序
    weights_override: 形如 {"color": 0.4, "silhouette": 0.35, "length": 0.25}，若提供则覆盖 JSON 中的权重
    """
    rules_obj = _load_rules()

    weights_json = rules_obj.get("weights", {})
    if weights_override:
        w_color = float(weights_override.get("color", weights_json.get("color", 0.4)))
        w_sil   = float(weights_override.get("silhouette", weights_json.get("silhouette", 0.35)))
        w_len   = float(weights_override.get("length", weights_json.get("length", 0.25)))
    else:
        w_color = float(weights_json.get("color", 0.4))
        w_sil   = float(weights_json.get("silhouette", 0.35))
        w_len   = float(weights_json.get("length", 0.25))

    vis = attrs.get("visual", {})
    color_name = vis.get("dominant_color_name", "unknown")
    silhouette = vis.get("silhouette", attrs.get("skirt", "straight"))
    length = attrs.get("length", "knee-length")

    color_group = _map_color_to_group(color_name, rules_obj.get("color_groups", {}))

    scored: List[Tuple[str, float]] = []
    for rule in rules_obj.get("rules", []):
        s = _score_one(rule, color_group, silhouette, length, w_color, w_sil, w_len)
        scored.append((rule.get("fabric", "Unknown"), round(s, 4)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def save_rules_weights(new_weights: Dict[str, float]) -> None:
    """
    将权重写回 data/fabric_rules.json，并清空缓存。
    """
    rules_obj = _load_rules().copy()
    rules_obj["weights"] = {
        "color": float(new_weights.get("color", 0.4)),
        "silhouette": float(new_weights.get("silhouette", 0.35)),
        "length": float(new_weights.get("length", 0.25)),
    }
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules_obj, f, ensure_ascii=False, indent=2)
    # 让下一次读取拿到最新文件
    _load_rules.cache_clear()
