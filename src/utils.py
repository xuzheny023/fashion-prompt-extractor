# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _ensure_type(name: str, value: Any, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be {expected_type.__name__}, got {type(value).__name__}")


def _ensure_len(name: str, value: List[Any], length: int) -> None:
    if len(value) != length:
        raise ValueError(f"{name} must have length {length}, got {len(value)}")


def _ensure_range(name: str, value: List[float]) -> None:
    if len(value) != 2:
        raise ValueError(f"{name} must be [min, max] with length 2, got {len(value)}")
    lo, hi = float(value[0]), float(value[1])
    if not (0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0 and lo <= hi):
        raise ValueError(f"{name} values must satisfy 0<=min<=max<=1, got {value}")


def validate_fabric_rules(path: str) -> Tuple[bool, List[str]]:
    """
    Validate fine-grained fabric rules JSON schema.
    Each entry must include fields with correct types. LBP len in {0,256};
    gabor_mu/gabor_sigma len in {0,8}. Returns (ok, errors).
    """
    errors: List[str] = []
    try:
        p = Path(path)
        if not p.exists():
            errors.append("Rules file not found")
            return False, errors
        with open(p, "r", encoding="utf-8") as f:
            fabrics: List[Dict[str, Any]] = json.load(f)
        if not isinstance(fabrics, list):
            errors.append("Root must be an array of fabric entries")
            return False, errors

        names_seen: set[str] = set()
        # Also track optional 'key' for packs-merged schemas; warn on duplicates
        keys_seen: Dict[str, int] = {}
        for idx, item in enumerate(fabrics):
            ctx = f"[{idx}]"
            if not isinstance(item, dict):
                errors.append(f"{ctx} must be an object")
                continue

            # required keys
            required_keys = [
                "name", "alias", "base", "weights", "lbp",
                "gabor_mu", "gabor_sigma", "sheen_range", "edge_range", "notes", "display_name", "suitable_structures"
            ]
            for k in required_keys:
                if k not in item:
                    errors.append(f"{ctx} missing key: {k}")

            name = item.get("name")
            if not isinstance(name, str) or not name:
                errors.append(f"{ctx}.name must be non-empty str")
            else:
                if name in names_seen:
                    errors.append(f"duplicate name: {name}")
                names_seen.add(name)

            # Packs schema: prefer 'key' as unique id when present; warn if duplicates
            k = str(item.get("key") or item.get("name") or "").strip()
            if k:
                if k in keys_seen:
                    import warnings
                    warnings.warn(f"duplicate key '{k}' detected between entries {keys_seen[k]} and {idx}; later one will override when merging")
                else:
                    keys_seen[k] = idx

            alias = item.get("alias")
            if not isinstance(alias, list) or not all(isinstance(a, str) for a in alias):
                errors.append(f"{ctx}.alias must be list[str]")

            base = item.get("base")
            if not isinstance(base, (int, float)) or not (0.0 <= float(base) <= 1.0):
                errors.append(f"{ctx}.base must be number in [0,1]")

            weights = item.get("weights")
            if not isinstance(weights, dict):
                errors.append(f"{ctx}.weights must be object with lbp,gabor,sheen,edges")
            else:
                for k in ("lbp", "gabor", "sheen", "edges"):
                    if k not in weights:
                        errors.append(f"{ctx}.weights missing '{k}'")
                    else:
                        v = weights[k]
                        if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                            errors.append(f"{ctx}.weights['{k}'] must be number in [0,1]")

            lbp = item.get("lbp")
            if not isinstance(lbp, list):
                errors.append(f"{ctx}.lbp must be list")
            else:
                if len(lbp) not in (0, 256):
                    errors.append(f"{ctx}.lbp length must be 0 or 256 (got {len(lbp)})")
                for i, v in enumerate(lbp):
                    if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                        errors.append(f"{ctx}.lbp[{i}] must be number in [0,1]")

            gmu = item.get("gabor_mu")
            if not isinstance(gmu, list):
                errors.append(f"{ctx}.gabor_mu must be list")
            else:
                if len(gmu) not in (0, 8):
                    errors.append(f"{ctx}.gabor_mu length must be 0 or 8 (got {len(gmu)})")
                for i, v in enumerate(gmu):
                    if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                        errors.append(f"{ctx}.gabor_mu[{i}] must be number in [0,1]")

            gsg = item.get("gabor_sigma")
            if not isinstance(gsg, list):
                errors.append(f"{ctx}.gabor_sigma must be list")
            else:
                if len(gsg) not in (0, 8):
                    errors.append(f"{ctx}.gabor_sigma length must be 0 or 8 (got {len(gsg)})")
                for i, v in enumerate(gsg):
                    if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                        errors.append(f"{ctx}.gabor_sigma[{i}] must be number in [0,1]")

            def _check_range(key: str) -> None:
                val = item.get(key)
                if not isinstance(val, list) or len(val) != 2:
                    errors.append(f"{ctx}.{key} must be [min,max]")
                    return
                lo, hi = val[0], val[1]
                if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
                    errors.append(f"{ctx}.{key} values must be numbers")
                elif not (0.0 <= float(lo) <= float(hi) <= 1.0):
                    errors.append(f"{ctx}.{key} must satisfy 0<=min<=max<=1")

            _check_range("sheen_range")
            _check_range("edge_range")

            # Validate display_name field
            display_name = item.get("display_name")
            if isinstance(display_name, dict):
                # New localized format: {"en": "...", "zh": "..."}
                if not display_name.get("en") or not display_name.get("zh"):
                    errors.append(f"{ctx}.display_name must have both 'en' and 'zh' keys with non-empty values")
                elif not isinstance(display_name.get("en"), str) or not isinstance(display_name.get("zh"), str):
                    errors.append(f"{ctx}.display_name values must be strings")
            elif isinstance(display_name, str):
                # Legacy string format - still valid for backward compatibility
                if not display_name:
                    errors.append(f"{ctx}.display_name must be non-empty str")
            else:
                errors.append(f"{ctx}.display_name must be either a string or localized object with 'en' and 'zh' keys")

            notes = item.get("notes")
            if isinstance(notes, dict):
                # New localized format: {"en": "...", "zh": "..."}
                if not notes.get("en") or not notes.get("zh"):
                    errors.append(f"{ctx}.notes must have both 'en' and 'zh' keys with non-empty values")
                elif not isinstance(notes.get("en"), str) or not isinstance(notes.get("zh"), str):
                    errors.append(f"{ctx}.notes values must be strings")
            elif isinstance(notes, str):
                # Legacy string format - still valid for backward compatibility
                if not notes:
                    errors.append(f"{ctx}.notes must be non-empty str")
            else:
                errors.append(f"{ctx}.notes must be either a string or localized object with 'en' and 'zh' keys")

            # Validate suitable_structures field
            valid_structures = {"collar", "sleeve", "buttons", "pants", "skirt", "pocket", "belt", "bodice", "coat"}
            suitable_structures = item.get("suitable_structures")
            if isinstance(suitable_structures, list):
                for struct in suitable_structures:
                    if not isinstance(struct, str):
                        errors.append(f"{ctx}.suitable_structures must contain only strings")
                        break
                    elif struct not in valid_structures:
                        # Warning for unknown values, don't interrupt validation
                        import warnings
                        warnings.warn(f"Unknown structure '{struct}' in {ctx}.suitable_structures. Valid values: {valid_structures}")
            elif suitable_structures is None:
                # Default to all suitable if missing (backward compatibility)
                pass
            else:
                errors.append(f"{ctx}.suitable_structures must be a list of strings or null")

        ok = len(errors) == 0
        return ok, errors
    except Exception as e:
        errors.append(f"exception: {e}")
        return False, errors


def get_note_text(item: Dict[str, Any], lang: str) -> str:
    """
    Get localized note text from a fabric item.
    Supports both legacy string and localized dict formats.
    """
    notes = item.get("notes", "")
    if isinstance(notes, dict):
        return str(notes.get(lang, "") or notes.get("en", "") or notes.get("zh", ""))
    if isinstance(notes, str):
        return notes
    return ""

if __name__ == "__main__":
    # CLI: python -m src.utils validate_rules / CLI: python -m src.utils validate_rules
    if len(sys.argv) >= 2 and sys.argv[1] == "validate_rules":
        project_root = Path(__file__).resolve().parents[1]
        rules_path = project_root / "data" / "fabric_fine_rules.json"
        ok, errs = validate_fabric_rules(str(rules_path))
        if ok:
            print(f"OK: {rules_path}")
            sys.exit(0)
        else:
            print(f"FAILED: {rules_path}")
            for msg in errs:
                print(f"- {msg}")
            sys.exit(1)

