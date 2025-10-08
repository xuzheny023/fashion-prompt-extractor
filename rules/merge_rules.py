# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

try:
    from src.xutils.io import read_json_smart
except Exception:
    from src.utils.io import read_json_smart  # type: ignore


def load_all_packs(dir: str | Path = "rules/packs") -> List[Tuple[str, List[Dict]]]:
    """
    Load all JSON packs from directory, sorted by filename.
    Returns list of (filename, items) where items is a list[dict].
    """
    d = Path(dir)
    if not d.exists():
        return []
    files = sorted([p for p in d.glob("*.json") if p.is_file()], key=lambda p: p.name)
    out: List[Tuple[str, List[Dict]]] = []
    for p in files:
        try:
            data = read_json_smart(p)
            if isinstance(data, list):
                out.append((p.name, data))
            else:
                print(f"[packs] skip {p} (root is not a list)")
        except Exception as e:
            print(f"[packs] failed to load {p}: {e}")
    return out


def merge_packs(packs: List[Tuple[str, List[Dict]]]) -> List[Dict]:
    """
    Merge packs by unique key. Later packs override earlier ones on the same key.
    Key precedence: item['key'] if present else item['name'] if present.
    Duplicate keys will print a warning including both sources.
    """
    merged: Dict[str, Dict] = {}
    source_of: Dict[str, str] = {}
    for fname, items in packs:
        for it in items:
            k = str(it.get("key") or it.get("name") or "").strip()
            if not k:
                # generate a synthetic key to avoid collisions
                import hashlib
                h = hashlib.md5(repr(sorted(it.items())).encode("utf-8")).hexdigest()[:8]
                k = f"_anon_{h}"
            if k in merged:
                print(f"[packs] duplicate key '{k}' overridden by {fname} (was from {source_of.get(k)})")
            merged[k] = it
            source_of[k] = fname
    return list(merged.values())


def save_merged(out: str | Path = "fabric_fine_rules_merged.json", rules: List[Dict] | None = None) -> Path:
    """
    Save merged rules list to data/out (default data/fabric_fine_rules_merged.json).
    If rules is None, auto-load and merge from rules/packs.
    Returns the output path.
    """
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / Path(out).name
    if rules is None:
        packs = load_all_packs(project_root / "rules" / "packs")
        rules = merge_packs(packs)
    import json
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rules or [], f, ensure_ascii=False, indent=2)
    print(f"[packs] merged rules saved to {out_path}")
    return out_path


if __name__ == "__main__":
    pk = load_all_packs()
    merged = merge_packs(pk)
    save_merged(rules=merged)
    print(f"[packs] loaded={len(pk)} files, merged entries={len(merged)}")


