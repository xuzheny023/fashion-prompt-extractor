from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


TEMPLATES: Dict[str, Dict] = {
    "sheens": {
        "signature_rules": [
            {"feat": "spec_ratio", "op": ">", "val": 0.6, "score": 1.5},
            {"feat": "hl_blob_area", "op": "<", "val": 0.15, "score": 0.8},
            {"feat": "lap_var", "op": "<", "val": 0.35, "score": 0.8},
        ],
        "cont_weights": {"color": 0.2, "gloss": 0.45, "texture": 0.2, "direction": 0.05, "transparency": 0.1},
    },
    "piles": {
        "signature_rules": [
            {"feat": "gabor_aniso", "op": ">", "val": 0.5, "score": 1.2},
            {"feat": "lap_var", "op": ">", "val": 0.4, "score": 0.8},
            {"feat": "spec_ratio", "op": "<", "val": 0.5, "score": 0.6},
        ],
        "cont_weights": {"color": 0.2, "gloss": 0.2, "texture": 0.35, "direction": 0.15, "transparency": 0.1},
    },
    "twills": {
        "signature_rules": [
            {"feat": "fft_dir_deg", "op": "in", "val": [35, 55], "score": 1.2},
            {"feat": "fft_peak", "op": ">", "val": 1.2, "score": 1.0},
        ],
        "cont_weights": {"color": 0.2, "gloss": 0.15, "texture": 0.3, "direction": 0.25, "transparency": 0.1},
    },
    "sheers": {
        "signature_rules": [
            {"feat": "transparency", "op": ">", "val": 0.18, "score": 1.2},
            {"feat": "edge_sharp", "op": ">", "val": 2.0, "score": 0.6},
        ],
        "cont_weights": {"color": 0.2, "gloss": 0.2, "texture": 0.25, "direction": 0.05, "transparency": 0.3},
    },
}


def make_entries(keys: List[str], family: str) -> List[Dict]:
    tpl = TEMPLATES.get(family, TEMPLATES["sheers"])  # default fallback
    out: List[Dict] = []
    for k in keys:
        out.append({
            "key": k,
            "display_name": {"zh": "", "en": ""},
            "notes": {"zh": "待补", "en": "TBD"},
            "suitable_structures": [],
            "signature_rules": tpl["signature_rules"],
            "cont_weights": tpl["cont_weights"],
            "base": 0.5,
            "sheen_range": [0.0, 1.0],
            "edge_range": [0.1, 0.5],
        })
    return out


def read_keys_from_packs(packs_dir: Path) -> List[str]:
    keys: List[str] = []
    for js in sorted(packs_dir.glob("*.json")):
        try:
            data = json.loads(js.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for it in data:
                    k = str((it.get("key") or it.get("name") or "").strip())
                    if k:
                        keys.append(k)
        except Exception:
            pass
    # dedupe, keep order
    seen = set()
    uniq = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return uniq


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Make rule skeleton pack")
    parser.add_argument("--keys", nargs="*", help="fabric keys (if empty, read from packs)")
    parser.add_argument("--family", default="sheers", choices=list(TEMPLATES.keys()), help="template family")
    parser.add_argument("--out", default="_auto.json", help="output pack filename (under rules/packs)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    packs_dir = project_root / "rules" / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)

    keys = args.keys if args.keys else read_keys_from_packs(packs_dir)
    if not keys:
        print("no keys provided or found in packs; nothing to do")
        return
    entries = make_entries(keys, args.family)
    out_path = packs_dir / args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"wrote {len(entries)} entries to {out_path}")


if __name__ == "__main__":
    main()


