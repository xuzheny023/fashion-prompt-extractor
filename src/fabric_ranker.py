# src/fabric_ranker.py
# -*- coding: utf-8 -*-
"""
基于颜色的面料候选打分排序（去除廓形/长度）：
- 读取 data/fabric_rules.json（若不存在使用内置默认）
- 仅根据 attrs['visual'].dominant_color_name 与规则的颜色偏好打分
"""

from __future__ import annotations
from typing import Dict, List, Tuple
import json
from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = PROJECT_ROOT / "data" / "fabric_rules.json"
FINE_RULES_PATH = PROJECT_ROOT / "data" / "fabric_fine_rules.json"


@lru_cache(maxsize=1)
def _load_rules() -> Dict:
    if RULES_PATH.exists():
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # 兜底
    return {
        "weights": {"color": 1.0},
        "color_groups": {
            "light": ["white", "gray", "yellow", "cyan"],
            "mid": ["green", "blue", "purple", "orange"],
            "dark": ["black", "red", "unknown"]
        },
        "rules": [
            {"fabric": "Chiffon", "base": 0.6, "preferred_colors": ["light", "mid"]},
            {"fabric": "Satin", "base": 0.6, "preferred_colors": ["mid", "dark"]},
            {"fabric": "Tulle", "base": 0.55, "preferred_colors": ["light"]}
        ]
    }


@lru_cache(maxsize=1)
def _load_rules_fine() -> List[Dict]:
    if not FINE_RULES_PATH.exists():
        raise FileNotFoundError(f"Fine rules file not found: {FINE_RULES_PATH}")
    try:
        with open(FINE_RULES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("fabric_fine_rules.json must be a JSON array of objects")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {FINE_RULES_PATH}: {e}")


def _map_color_to_group(color_name: str, color_groups: Dict[str, List[str]]) -> str:
    cname = (color_name or "unknown").lower()
    for group, names in color_groups.items():
        if cname in names:
            return group
    return "dark"


def _score_one(rule: Dict, color_group: str, w_color: float) -> float:
    score = rule.get("base", 0.5)
    if rule.get("preferred_colors"):
        score += w_color * (1.0 if color_group in rule["preferred_colors"] else 0.3)
    return float(score)


def recommend_fabrics(attrs: Dict, top_k: int = 5, weights_override: Dict[str, float] | None = None,
                      rules_source: str = "coarse") -> List[Tuple[str, float] | Tuple[str, float, str]]:
    """
    输出：[(fabric_name, score), ...] 降序
    weights_override: 形如 {"color": 0.4, "silhouette": 0.35, "length": 0.25}，若提供则覆盖 JSON 中的权重
    """
    rules_obj = _load_rules()

    if rules_source == "coarse":
        weights_json = rules_obj.get("weights", {})
        if weights_override:
            w_color = float(weights_override.get("color", weights_json.get("color", 1.0)))
        else:
            w_color = float(weights_json.get("color", 1.0))
    else:
        # fine: use provided override color weight or default 1.0
        if weights_override and "color" in weights_override:
            w_color = float(weights_override["color"]) 
        else:
            w_color = 1.0

    vis = attrs.get("visual", {})
    color_name = vis.get("dominant_color_name", "unknown")

    if rules_source == "coarse":
        color_group = _map_color_to_group(color_name, rules_obj.get("color_groups", {}))
        scored: List[Tuple[str, float]] = []
        for rule in rules_obj.get("rules", []):
            s = _score_one(rule, color_group, w_color)
            scored.append((rule.get("fabric", "Unknown"), round(s, 4)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    else:
        # fine source: read from fine rules, use name/base/weights/notes
        fine_items = _load_rules_fine()
        color_group = _map_color_to_group(color_name, _load_rules().get("color_groups", {}))
        out: List[Tuple[str, float, str]] = []
        for it in fine_items:
            # map fine schema to scoring rule: using base and optional preferred colors via notes not available; use color weight only
            base = float(it.get("base", 0.5))
            s = base + w_color * 0.0  # placeholder: color preference not specified in fine list yet
            out.append((str(it.get("name", "Unknown")), round(float(s), 4), str(it.get("notes", ""))))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:top_k]



def save_rules_weights(new_weights: Dict[str, float]) -> None:
    """
    将权重写回 data/fabric_rules.json，并清空缓存。（仅 color ）
    """
    rules_obj = _load_rules().copy()
    rules_obj["weights"] = {
        "color": float(new_weights.get("color", 1.0)),
    }
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules_obj, f, ensure_ascii=False, indent=2)
    _load_rules.cache_clear()
