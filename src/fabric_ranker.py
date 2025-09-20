# src/fabric_ranker.py
# -*- coding: utf-8 -*-
"""
3D fabric scoring framework: Color + Sheen + Texture
三维面料打分框架：颜色 + 光泽度 + 纹理
- Read data/fabric_rules.json (use built-in defaults if not exists)
- 读取 data/fabric_rules.json（若不存在使用内置默认）
- Score based on color similarity, sheen characteristics, and texture features
- 基于颜色相似度、光泽特征和纹理特征打分
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Union
import json
import numpy as np
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
    # Fallback defaults / 兜底
    return {
        "weights": {"color": 0.5, "sheen": 0.3, "texture": 0.2},
        "color_groups": {
            "light": ["white", "gray", "yellow", "cyan"],
            "mid": ["green", "blue", "purple", "orange"],
            "dark": ["black", "red", "unknown"]
        },
        "rules": [
            {"fabric": "Chiffon", "base": 0.6, "preferred_colors": ["light", "mid"], "sheen_range": [0.3, 0.7], "texture_complexity": 0.4},
            {"fabric": "Satin", "base": 0.6, "preferred_colors": ["mid", "dark"], "sheen_range": [0.7, 0.95], "texture_complexity": 0.2},
            {"fabric": "Tulle", "base": 0.55, "preferred_colors": ["light"], "sheen_range": [0.2, 0.5], "texture_complexity": 0.8}
        ]
    }


@lru_cache(maxsize=1)
def _load_rules_fine() -> List[Dict]:
    if not FINE_RULES_PATH.exists():
        raise FileNotFoundError("Fine rules file not found")
    try:
        with open(FINE_RULES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Fine rules must be a JSON array of objects")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in fine rules: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load fine rules: {e}")


def _map_color_to_group(color_name: str, color_groups: Dict[str, List[str]]) -> str:
    cname = (color_name or "unknown").lower()
    for group, names in color_groups.items():
        if cname in names:
            return group
    return "dark"


def _color_score(attrs: Dict, rule: Dict) -> float:
    """Calculate color similarity score / 计算颜色相似度得分"""
    try:
        vis = attrs.get("visual", {})
        color_name = vis.get("dominant_color_name", "unknown")
        color_groups = {
            "light": ["white", "gray", "yellow", "cyan"],
            "mid": ["green", "blue", "purple", "orange"],
            "dark": ["black", "red", "unknown"]
        }
        
        # Map color to group
        color_group = "dark"
        for group, names in color_groups.items():
            if color_name in names:
                color_group = group
                break
        
        # Check preferred colors
        preferred = rule.get("preferred_colors", [])
        if color_group in preferred:
            return 1.0
        elif preferred:
            return 0.3
        else:
            return 0.5
    except:
        return 0.5


def _sheen_score(attrs: Dict, rule: Dict) -> float:
    """Calculate sheen characteristics score / 计算光泽特征得分"""
    try:
        # For now, use coverage ratio as a proxy for sheen (higher coverage = more reflective)
        # 暂时用覆盖度作为光泽度的代理指标（覆盖度越高越反光）
        coverage = attrs.get("visual", {}).get("coverage_ratio", 0.5)
        
        # Check if coverage falls within expected sheen range
        sheen_range = rule.get("sheen_range", [0.0, 1.0])
        if len(sheen_range) == 2:
            min_sheen, max_sheen = sheen_range
            if min_sheen <= coverage <= max_sheen:
                return 1.0
            else:
                # Distance-based penalty
                dist = min(abs(coverage - min_sheen), abs(coverage - max_sheen))
                return max(0.0, 1.0 - dist * 2)
        
        return 0.5
    except:
        return 0.5


def _texture_score(attrs: Dict, rule: Dict) -> float:
    """Calculate texture complexity score / 计算纹理复杂度得分"""
    try:
        # Use texture complexity from rule if available
        texture_complexity = rule.get("texture_complexity", 0.5)
        
        # For coarse rules, use edge_range as texture indicator
        edge_range = rule.get("edge_range", [0.1, 0.5])
        if len(edge_range) == 2:
            # Use coverage as texture proxy (higher coverage = more texture)
            coverage = attrs.get("visual", {}).get("coverage_ratio", 0.5)
            min_edge, max_edge = edge_range
            
            if min_edge <= coverage <= max_edge:
                return 1.0
            else:
                dist = min(abs(coverage - min_edge), abs(coverage - max_edge))
                return max(0.0, 1.0 - dist * 2)
        
        return texture_complexity
    except:
        return 0.5


def _score_one_3d(rule: Dict, attrs: Dict, weights: Dict[str, float]) -> float:
    """3D scoring: color + sheen + texture / 三维打分：颜色+光泽+纹理"""
    base_score = rule.get("base", 0.5)
    
    color_score = _color_score(attrs, rule)
    sheen_score = _sheen_score(attrs, rule)
    texture_score = _texture_score(attrs, rule)
    
    w_color = weights.get("color", 0.5)
    w_sheen = weights.get("sheen", 0.3)
    w_texture = weights.get("texture", 0.2)
    
    total_score = base_score + w_color * color_score + w_sheen * sheen_score + w_texture * texture_score
    return float(total_score)


def recommend_fabrics(attrs: Dict, top_k: int = 5, weights_override: Dict[str, float] | None = None,
                      rules_source: str = "coarse") -> List[Tuple[str, float] | Tuple[str, float, str]]:
    """
    3D scoring output: [(fabric_name, score), ...] or [(fabric_name, score, notes), ...] in descending order
    三维打分输出：[(fabric_name, score), ...] 或 [(fabric_name, score, notes), ...] 降序
    weights_override: {"color": 0.5, "sheen": 0.3, "texture": 0.2}, overrides weights in JSON if provided
    weights_override: {"color": 0.5, "sheen": 0.3, "texture": 0.2}，若提供则覆盖 JSON 中的权重
    """
    rules_obj = _load_rules()

    # Use provided weights or defaults
    if weights_override:
        weights = {
            "color": float(weights_override.get("color", 0.5)),
            "sheen": float(weights_override.get("sheen", 0.3)),
            "texture": float(weights_override.get("texture", 0.2)),
        }
    else:
        weights_json = rules_obj.get("weights", {})
        weights = {
            "color": float(weights_json.get("color", 0.5)),
            "sheen": float(weights_json.get("sheen", 0.3)),
            "texture": float(weights_json.get("texture", 0.2)),
        }

    if rules_source == "coarse":
        scored: List[Tuple[str, float]] = []
        for rule in rules_obj.get("rules", []):
            s = _score_one_3d(rule, attrs, weights)
            scored.append((rule.get("fabric", "Unknown"), round(s, 4)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    else:
        # Fine source: read from fine rules, use 3D scoring
        fine_items = _load_rules_fine()
        out: List[Tuple[str, float, str]] = []
        for it in fine_items:
            # Map fine schema to scoring rule for 3D scoring
            # Use sheen_range and edge_range from fine rules
            rule = {
                "base": float(it.get("base", 0.5)),
                "preferred_colors": [],  # Fine rules don't have color preferences yet
                "sheen_range": it.get("sheen_range", [0.0, 1.0]),
                "edge_range": it.get("edge_range", [0.1, 0.5]),
                "texture_complexity": 0.5  # Default texture complexity
            }
            s = _score_one_3d(rule, attrs, weights)
            out.append((str(it.get("name", "Unknown")), round(float(s), 4), str(it.get("notes", ""))))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:top_k]



def save_rules_weights(new_weights: Dict[str, float]) -> None:
    """
    Write weights back to data/fabric_rules.json and clear cache (3D weights)
    将权重写回 data/fabric_rules.json，并清空缓存。（三维权重）
    """
    rules_obj = _load_rules().copy()
    rules_obj["weights"] = {
        "color": float(new_weights.get("color", 0.5)),
        "sheen": float(new_weights.get("sheen", 0.3)),
        "texture": float(new_weights.get("texture", 0.2)),
    }
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules_obj, f, ensure_ascii=False, indent=2)
    _load_rules.cache_clear()


def localize_fabric(rule_or_name: Union[Dict, str], lang: str) -> Tuple[str, str]:
    """
    Get localized display name and notes for a fabric rule or name
    获取面料规则或名称的本地化显示名称和说明
    
    Args:
        rule_or_name: Either a fabric rule dict or fabric name string / 面料规则字典或面料名称字符串
        lang: Language code ('en' or 'zh') / 语言代码（'en' 或 'zh'）
    
    Returns:
        Tuple of (display_name, notes) / 返回（显示名称，说明）元组
    """
    try:
        if isinstance(rule_or_name, str):
            # Try to find the rule by name
            fabric_name = rule_or_name
            
            # Try fine rules first
            try:
                fine_rules = _load_rules_fine()
                for rule in fine_rules:
                    if rule.get("name") == fabric_name:
                        return _extract_localized_fields(rule, lang)
            except:
                pass
            
            # Try coarse rules
            coarse_rules = _load_rules()
            for rule in coarse_rules.get("rules", []):
                if rule.get("fabric") == fabric_name:
                    return _extract_localized_fields(rule, lang)
            
            # Fallback: return the name itself
            return fabric_name, ""
        
        else:
            # Direct rule object
            return _extract_localized_fields(rule_or_name, lang)
    
    except Exception:
        # Ultimate fallback
        name = rule_or_name.get("name", rule_or_name.get("fabric", "Unknown")) if isinstance(rule_or_name, dict) else str(rule_or_name)
        return name, ""


def _extract_localized_fields(rule: Dict, lang: str) -> Tuple[str, str]:
    """
    Extract localized display_name and notes from a rule
    从规则中提取本地化的显示名称和说明
    
    Args:
        rule: Fabric rule dictionary / 面料规则字典
        lang: Language code / 语言代码
    
    Returns:
        Tuple of (display_name, notes) / 返回（显示名称，说明）元组
    """
    # Extract display name
    display_name = _get_localized_field(rule, "display_name", lang)
    if not display_name:
        # Fallback: try to find matching alias
        aliases = rule.get("alias", [])
        if aliases:
            # Look for language-appropriate alias
            if lang == "zh":
                # Look for Chinese characters
                for alias in aliases:
                    if any('\u4e00' <= char <= '\u9fff' for char in alias):
                        display_name = alias
                        break
            else:
                # Look for English alias (no Chinese characters)
                for alias in aliases:
                    if not any('\u4e00' <= char <= '\u9fff' for char in alias):
                        display_name = alias
                        break
        
        # Final fallback: use name or fabric field
        if not display_name:
            display_name = rule.get("name", rule.get("fabric", "Unknown"))
    
    # Extract notes
    notes = _get_localized_field(rule, "notes", lang)
    if not notes and isinstance(rule.get("notes"), str):
        # Fallback to string notes
        notes = rule.get("notes", "")
    
    return display_name, notes


def _get_localized_field(rule: Dict, field: str, lang: str) -> str:
    """
    Get localized field value from rule
    从规则中获取本地化字段值
    
    Args:
        rule: Fabric rule dictionary / 面料规则字典
        field: Field name ('display_name' or 'notes') / 字段名称
        lang: Language code / 语言代码
    
    Returns:
        Localized field value or empty string / 本地化字段值或空字符串
    """
    field_data = rule.get(field, {})
    
    if isinstance(field_data, dict):
        # New localized format: {"en": "...", "zh": "..."}
        return field_data.get(lang, "")
    elif isinstance(field_data, str):
        # Old string format: keep for backward compatibility
        return field_data
    
    return ""


def recommend_fabrics_localized(attrs: Dict, lang: str = "en", top_k: int = 5, 
                               weights_override: Dict[str, float] | None = None,
                               rules_source: str = "coarse") -> List[Tuple[str, float, str, str]]:
    """
    Enhanced recommend_fabrics with localization support
    增强的面料推荐函数，支持本地化
    
    Args:
        attrs: Extracted attributes / 提取的属性
        lang: Language code for localization / 本地化语言代码
        top_k: Number of top results / 返回结果数量
        weights_override: Custom weights / 自定义权重
        rules_source: "coarse" or "fine" / 规则源："coarse" 或 "fine"
    
    Returns:
        List of (fabric_name, score, display_name, notes) tuples / 返回（面料名称，得分，显示名称，说明）元组列表
    """
    # Get original recommendations
    original_results = recommend_fabrics(attrs, top_k, weights_override, rules_source)
    
    localized_results = []
    for item in original_results:
        if len(item) == 3:
            name, score, notes = item
            display_name, localized_notes = localize_fabric(name, lang)
            localized_results.append((name, score, display_name, localized_notes))
        else:
            name, score = item
            display_name, localized_notes = localize_fabric(name, lang)
            localized_results.append((name, score, display_name, localized_notes))
    
    return localized_results
