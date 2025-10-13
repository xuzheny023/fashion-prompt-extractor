# -*- coding: utf-8 -*-
# src/fabric_ranker.py
# -*- coding: utf-8 -*-
"""
3D fabric scoring framework: Color + Sheen + Texture
- Read data/fabric_rules.json (use built-in defaults if not exists)
- Score based on color similarity, sheen characteristics, and texture features
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Union
import numpy as np
from functools import lru_cache
from pathlib import Path
try:
    # Prefer new xutils path; fallback to legacy utils for compatibility
    from src.xutils.io import read_json_smart
except Exception:
    from src.utils.io import read_json_smart  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = PROJECT_ROOT / "data" / "fabric_rules.json"
FINE_RULES_PATH = PROJECT_ROOT / "data" / "fabric_fine_rules.json"


@lru_cache(maxsize=1)
def _load_rules() -> Dict:
    if RULES_PATH.exists():
        return read_json_smart(RULES_PATH)
    # Fallback defaults / 鍏滃簳
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
        data = read_json_smart(FINE_RULES_PATH)
        if not isinstance(data, list):
            raise ValueError("Fine rules must be a JSON array of objects")
        return data
    except Exception as e:
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
    """Calculate color similarity score."""
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
    """Calculate sheen characteristics score."""
    try:
        # For now, use coverage ratio as a proxy for sheen (higher coverage = more reflective)
        # 鏆傛椂鐢ㄨ鐩栧害浣滀负鍏夋辰搴》殑浠g悊鎸囨爣锛堣鐩栧害瓒婇珮瓒婂弽鍏夛級
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
    """Calculate texture complexity score."""
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


def _component_scores(attrs: Dict, rule: Dict) -> Tuple[float, float, float]:
    """Return (color, sheen, texture) component scores."""
    return _color_score(attrs, rule), _sheen_score(attrs, rule), _texture_score(attrs, rule)


def _score_one_3d(rule: Dict, attrs: Dict, weights: Dict[str, float]) -> float:
    """3D scoring: color + sheen + texture / 涓夌淮鎵撳垎锛氶鑹?鍏夋辰+绾圭悊"""
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
    涓夌淮鎵撳垎杈撳嚭锛歔(fabric_name, score), ...] 鎴?[(fabric_name, score, notes), ...] 闄嶅簭
    weights_override: {"color": 0.5, "sheen": 0.3, "texture": 0.2}, overrides weights in JSON if provided
    weights_override: {"color": 0.5, "sheen": 0.3, "texture": 0.2}锛岃嫢鎻愪緵鍒欒鐩?JSON 涓殑鏉冮噸
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
            name = rule.get("fabric", "Unknown")
            try:
                # Log global features if available in session (printed to console)
                import streamlit as _st
                feats = _st.session_state.get("features", {}).get("global", {})
                if feats:
                    # also log per-structure summaries if available
                    struct_set = list(_st.session_state.get("struct_set", []))
                    print(f"[features] {name} global: {feats}")
                    det = _st.session_state.get("struct_detect", {})
                    if det:
                        print(f"[struct] method={det.get('method','heuristic')} thr={float(_st.session_state.get('struct_thr',0.55))} set={struct_set}")
                    masks = _st.session_state.get("struct_masks", {})
                    feat_all = _st.session_state.get("features", {})
                    for sk in struct_set:
                        fsk = feat_all.get(sk, {})
                        if fsk:
                            print(f"[features] {name} {sk}: lap={fsk.get('laplacian_var_norm')}, g_aniso={fsk.get('gabor_anisotropy')}")
            except Exception:
                pass
            scored.append((name, round(s, 4)))
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
            name = str(it.get("name", "Unknown"))
            try:
                import streamlit as _st
                feats = _st.session_state.get("features", {}).get("global", {})
                if feats:
                    struct_set = list(_st.session_state.get("struct_set", []))
                    print(f"[features] {name} global: {feats}")
                    det = _st.session_state.get("struct_detect", {})
                    if det:
                        print(f"[struct] method={det.get('method','heuristic')} thr={float(_st.session_state.get('struct_thr',0.55))} set={struct_set}")
                    masks = _st.session_state.get("struct_masks", {})
                    feat_all = _st.session_state.get("features", {})
                    for sk in struct_set:
                        fsk = feat_all.get(sk, {})
                        if fsk:
                            print(f"[features] {name} {sk}: lap={fsk.get('laplacian_var_norm')}, g_aniso={fsk.get('gabor_anisotropy')}")
            except Exception:
                pass
            out.append((name, round(float(s), 4), str(it.get("notes", ""))))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:top_k]



def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize weights; accept keys {"color","sheen"|"gloss","texture"}.
    Sum-normalize to 1.0; fall back to defaults if invalid.
    """
    w_color = float(weights.get("color", weights.get("colour", 0.5)))
    w_sheen = float(weights.get("sheen", weights.get("gloss", 0.3)))
    w_texture = float(weights.get("texture", 0.2))
    total = max(w_color + w_sheen + w_texture, 1e-6)
    return {
        "color": w_color / total,
        "sheen": w_sheen / total,
        "texture": w_texture / total,
    }


def filter_rules_by_structure(rules: List[Dict], structure: str) -> List[Dict]:
    """
    Filter rules by structure. If a rule lacks 'suitable_structures', it passes.
    Otherwise, keep rules whose 'suitable_structures' contains the structure.
    """
    structure = str(structure or "").strip()
    out: List[Dict] = []
    for r in rules:
        ss = r.get("suitable_structures")
        if not isinstance(ss, list):
            out.append(r)
        else:
            if structure in ss:
                out.append(r)
    return out


def _minmax(values: List[float]) -> List[float]:
    if not values:
        return []
    vmin = float(min(values))
    vmax = float(max(values))
    if not np.isfinite(vmin) or not np.isfinite(vmax):
        return [0.5 for _ in values]
    rng = vmax - vmin
    if rng <= 1e-8:
        return [0.5 for _ in values]
    return [(v - vmin) / rng for v in values]


def _map_fine_to_scoring(rule_item: Dict) -> Dict:
    """Map a fine rule item to a scoring rule dict expected by component scorers."""
    return {
        "base": float(rule_item.get("base", 0.5)),
        "preferred_colors": [],
        "sheen_range": rule_item.get("sheen_range", [0.0, 1.0]),
        "edge_range": rule_item.get("edge_range", [0.1, 0.5]),
        "texture_complexity": 0.5,
    }


def rank_fabrics_by_structures(
    attrs: Dict,
    rules: List[Dict],
    struct_set: List[str] | set[str],
    weights: Dict[str, float],
    topk: int = 5,
) -> Dict[str, List[Tuple[str, float]]]:
    """
    For each structure, filter rules then rank using normalized component scores.
    Returns {structure: [(name, score), ...]}.
    """
    norm_w = normalize_weights(weights)
    result: Dict[str, List[Tuple[str, float]]] = {}

    for struct in struct_set:
        filtered = filter_rules_by_structure(rules, struct)

        # Compute component scores for each candidate
        names: List[str] = []
        comps_color: List[float] = []
        comps_sheen: List[float] = []
        comps_texture: List[float] = []

        for item in filtered:
            # Support both coarse and fine schemas
            if "fabric" in item:  # coarse
                scoring_rule = item
                name = str(item.get("fabric", "Unknown"))
            else:  # fine
                scoring_rule = _map_fine_to_scoring(item)
                name = str(item.get("name", "Unknown"))

            c, s, t = _component_scores(attrs, scoring_rule)
            names.append(name)
            comps_color.append(float(c))
            comps_sheen.append(float(s))
            comps_texture.append(float(t))

        # Normalize components per structure bucket
        nc = _minmax(comps_color)
        ns = _minmax(comps_sheen)
        nt = _minmax(comps_texture)

        combined: List[Tuple[str, float]] = []
        for i, name in enumerate(names):
            score = (
                norm_w["color"] * (nc[i] if i < len(nc) else 0.5) +
                norm_w["sheen"] * (ns[i] if i < len(ns) else 0.5) +
                norm_w["texture"] * (nt[i] if i < len(nt) else 0.5)
            )
            combined.append((name, round(float(score), 4)))

        combined.sort(key=lambda x: x[1], reverse=True)
        result[str(struct)] = combined[: max(0, int(topk))]

    return result


def save_rules_weights(new_weights: Dict[str, float]) -> None:
    """
    Write weights back to data/fabric_rules.json and clear cache (3D weights)
    """
    rules_obj = _load_rules().copy()
    rules_obj["weights"] = {
        "color": float(new_weights.get("color", 0.5)),
        "sheen": float(new_weights.get("sheen", 0.3)),
        "texture": float(new_weights.get("texture", 0.2)),
    }
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Use built-in json but ensure availability
    import json as _json  # localized import avoids top-level dependency for readers
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        _json.dump(rules_obj, f, ensure_ascii=False, indent=2)
    _load_rules.cache_clear()


def localize_fabric(rule_or_name: Union[Dict, str], lang: str) -> Tuple[str, str]:
    """
    Get localized display name and notes for a fabric rule or name
    鑾峰彇闈(二)枡瑙勫垯鎴栧悕绉扮殑鏈湴鍖栨樉绀哄悕绉板拰璇存槑

    Args:
        rule_or_name: Either a fabric rule dict or fabric name string / 闈(二)枡瑙勫垯瀛楀吀鎴栭潰鏂欏悕绉板瓧绗〈覆
        lang: Language code ('en' or 'zh') / 璇█浠g爜锛?en' 鎴?'zh'锛?
    Returns:
        Tuple of (display_name, notes) / 杩斿洖锛堟樉绀哄悕绉帮紝璇存槑锛夊厓缁?    """
    try:
        if isinstance(rule_or_name, str):
            # Try to find the rule by name
            fabric_name = rule_or_name

            # Try loading from new fabric_labels system first
            try:
                from src.fabric_labels import get_label
                if lang == "zh":
                    chinese_label = get_label(fabric_name, fallback_to_id=False)
                    if chinese_label:
                        return chinese_label, ""
            except Exception:
                pass

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
    浠庤鍒欎腑鎻愬彇鏈湴鍖栫殑鏄剧ず鍚嶇О鍜岃鏄?
    Args:
        rule: Fabric rule dictionary / 闈(二)枡瑙勫垯瀛楀吀
        lang: Language code / 璇█浠g爜

    Returns:
        Tuple of (display_name, notes) / 杩斿洖锛堟樉绀哄悕绉帮紝璇存槑锛夊厓缁?    """
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
    浠庤鍒欎腑鑾峰彇鏈湴鍖栧瓧娈靛€?
    Args:
        rule: Fabric rule dictionary / 闈(二)枡瑙勫垯瀛楀吀
        field: Field name ('display_name' or 'notes') / 瀛楁鍚嶇О
        lang: Language code / 璇█浠g爜

    Returns:
        Localized field value or empty string / 鏈湴鍖栧瓧娈靛€兼垨绌哄瓧绗〈覆
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
    澧炲己鐨勯潰鏂欐帹鑽愬嚱鏁帮紝鏀寔鏈湴鍖?
    Args:
        attrs: Extracted attributes / 鎻愬彇鐨勫睘鎬?        lang: Language code for localization / 鏈湴鍖栬瑷€浠g爜
        top_k: Number of top results / 杩斿洖缁撴灉鏁伴噺
        weights_override: Custom weights / 鑷畾涔夋潈閲?        rules_source: "coarse" or "fine" / 瑙勫垯婧愶細"coarse" 鎴?"fine"

    Returns:
        List of (fabric_name, score, display_name, notes) tuples / 杩斿洖锛堥潰鏂欏悕绉帮紝寰楀垎锛屾樉绀哄悕绉帮紝璇存槑锛夊厓缁勫垪琛?    """
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


def load_bank():
    """Load fabric bank and centroids for CLIP retrieval."""
    import numpy as np
    from pathlib import Path
    
    bank_path = Path("data/fabric_bank.npz")
    centroids_path = Path("data/fabric_centroids.npz")
    
    bank = None
    centroids = None
    
    if bank_path.exists():
        bank = np.load(bank_path, allow_pickle=True)
    
    if centroids_path.exists():
        centroids = np.load(centroids_path, allow_pickle=True)
    
    return bank, centroids


def rank_with_centroids(query_emb, bank, centroids, topk=5):
    """
    Rank fabrics using centroids-first approach with fallback to full samples.
    Returns list of (fabric_id, score) tuples sorted by score descending.
    """
    import numpy as np
    from src.clip_infer import cosine_sim
    
    if centroids is None or bank is None:
        return []
    
    # Step 1: Centroids-first retrieval
    centroid_scores = {}
    for k in centroids.files:
        centroid_emb = centroids[k][0]  # [1,512] -> [512]
        centroid_scores[k] = float(cosine_sim(query_emb, centroid_emb))
    
    centroid_top = sorted(centroid_scores.items(), key=lambda x: x[1], reverse=True)[:topk]
    
    # Step 2: Check if we need fallback to full samples
    if len(centroid_top) >= 2:
        score_diff = centroid_top[0][1] - centroid_top[1][1]
        if score_diff < 0.03:
            # Fallback to full samples for close scores
            scores = {}
            for k in bank.files:
                if bank[k].shape[0] >= 3:  # Minimum sample filter
                    embs = bank[k]
                    sims = [cosine_sim(query_emb, e) for e in embs]
                    scores[k] = float(np.max(sims))
            return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:topk]
    
    return centroid_top


def fuse_with_clip(patch_img, base_results: List[Tuple], lang="zh", alpha=0.7, topk=5) -> List[Tuple[str, float, str, str]]:
    """
    Fuse rule-based recommendations with CLIP retrieval scores using centroids-first approach.
    融合基于规则的推荐与 CLIP 检索分数（类中心优先）
    
    Args:
        patch_img: PIL.Image of the fabric patch / 面料区域的 PIL 图像
        base_results: Original results from recommend_fabrics_localized / 原始推荐结果
            Format: [(name, score, display_name, notes), ...]
        lang: Language code / 语言代码
        alpha: Weight for base score (1-alpha for CLIP) / 基础分数权重（1-alpha 为 CLIP 权重）
        topk: Number of results to return / 返回结果数量
    
    Returns:
        Fused results: [(name, score, display_name, notes), ...] / 融合后的结果
    """
    try:
        from PIL import Image
        from src.clip_infer import image_to_emb
        
        # Load bank and centroids
        bank, centroids = load_bank()
        if bank is None:
            return base_results[:topk]
        
        # Get query embedding
        query_emb = image_to_emb(patch_img)
        
        # 1) Extract base scores (0-1 range)
        base = {}
        metadata = {}  # Store display_name and notes
        for item in base_results:
            if len(item) >= 4:
                name, score, display_name, notes = item
                base[name] = float(score)
                metadata[name] = (display_name, notes)
            elif len(item) == 3:
                name, score, notes = item
                base[name] = float(score)
                metadata[name] = (name, notes)
            elif len(item) == 2:
                name, score = item
                base[name] = float(score)
                metadata[name] = (name, "")
        
        # 2) Get CLIP retrieval scores using centroids-first approach
        clip_ranks = rank_with_centroids(query_emb, bank, centroids, topk=topk * 2)
        clip = {}
        for fid, score_raw in clip_ranks:
            # CLIP scores are already in [0, 1] range
            clip[fid] = float(score_raw)
        
        # 3) Fuse scores
        all_ids = set(base) | set(clip)
        fused = []
        
        for fid in all_ids:
            b = base.get(fid, 0.0)
            c = clip.get(fid, 0.0)
            s = alpha * b + (1.0 - alpha) * c
            
            # Get metadata (display_name, notes)
            if fid in metadata:
                display_name, notes = metadata[fid]
            else:
                # New fabric from CLIP not in base results
                display_name, notes = localize_fabric(fid, lang)
            
            fused.append((fid, round(float(s), 4), display_name, notes))
        
        # 4) Sort by fused score descending
        fused.sort(key=lambda x: x[1], reverse=True)
        
        return fused[:topk]
        
    except Exception as e:
        # Fallback to base results if CLIP fails
        import logging
        logging.warning(f"[CLIP fusion] Failed to fuse with CLIP: {e}. Using base results.")
        return base_results[:topk]


def score_with_features(attrs: Dict, features_dict: Dict, structure: str | None = None) -> Dict:
    """
    Placeholder scoring hook using extracted low-level features.
    For now, returns features for the requested structure or global features.
    """
    try:
        if structure and structure in features_dict:
            return dict(features_dict.get(structure, {}))
        return dict(features_dict.get("global", {}))
    except Exception:
        return {}
