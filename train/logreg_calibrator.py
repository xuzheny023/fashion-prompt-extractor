from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib


FEATURE_KEYS = [
    "spec_ratio",
    "hl_blob_area",
    "lap_var",
    "lbp_dist",
    "gabor_aniso",
    "fft_peak",
    "fft_dir_sin",
    "fft_dir_cos",
    "transparency",
    "edge_sharp",
]


def _collect_samples(patches_dir: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    X: List[List[float]] = []
    y: List[int] = []
    classes: List[str] = []
    class_to_idx: Dict[str, int] = {}
    for sub in sorted(patches_dir.glob("*/")):
        key = sub.name
        if not sub.is_dir():
            continue
        for js in sorted(sub.glob("*.json")):
            try:
                data = json.loads(js.read_text(encoding="utf-8"))
                feats = data.get("features", {}) or {}
                # Build feature vector
                vec: List[float] = []
                # handle derived fft_dir features if available; else fallbacks
                dir_deg = float(feats.get("fft_dir_deg", 0.0))
                fft_dir_sin = np.sin(np.deg2rad(dir_deg))
                fft_dir_cos = np.cos(np.deg2rad(dir_deg))
                feat_map = {
                    "spec_ratio": float(feats.get("spec_ratio", 0.0)),
                    "hl_blob_area": float(feats.get("hl_blob_area", 0.0)),
                    "lap_var": float(feats.get("lap_var", 0.0)),
                    "lbp_dist": float(feats.get("lbp_dist", 0.0)),
                    "gabor_aniso": float(feats.get("gabor_aniso", 0.0)),
                    "fft_peak": float(feats.get("fft_peak", 0.0)),
                    "fft_dir_sin": float(fft_dir_sin),
                    "fft_dir_cos": float(fft_dir_cos),
                    "transparency": float(feats.get("transparency", 0.0)),
                    "edge_sharp": float(feats.get("edge_sharp", 0.0)),
                }
                vec = [float(feat_map.get(k, 0.0)) for k in FEATURE_KEYS]
                # Append
                if key not in class_to_idx:
                    class_to_idx[key] = len(classes)
                    classes.append(key)
                y.append(class_to_idx[key])
                X.append(vec)
            except Exception as e:
                print(f"[train] skip {js}: {e}")
    if not X:
        raise RuntimeError("No training samples found in labeled patches directory")
    Xn = np.asarray(X, dtype=np.float32)
    yn = np.asarray(y, dtype=np.int64)
    return Xn, yn, classes


def train_and_save(labeled_root: Path, models_dir: Path) -> None:
    X, y, classes = _collect_samples(labeled_root)
    print(f"[train] samples={len(y)}, classes={len(classes)} → {classes}")
    clf = LogisticRegression(max_iter=1000, multi_class="multinomial")
    clf.fit(X, y)
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, models_dir / "logreg.pkl")
    # Export weights per class
    meta = {
        "classes": classes,
        "feature_keys": FEATURE_KEYS,
        "coef": clf.coef_.tolist() if hasattr(clf, "coef_") else [],
        "intercept": clf.intercept_.tolist() if hasattr(clf, "intercept_") else [],
    }
    with open(models_dir / "logreg_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[train] saved models to {models_dir}")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    labeled_root = project_root / "data" / "patches" / "labeled"
    models_dir = project_root / "models"
    train_and_save(labeled_root, models_dir)


