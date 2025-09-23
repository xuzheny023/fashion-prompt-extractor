# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np


def load_logreg():
    """
    Load trained multinomial logistic regression if available, and return a
    callable predict_proba(feat_dict) -> {fabric_key: prob}.
    If model not found, return a dummy that yields empty dict.
    """
    project_root = Path(__file__).resolve().parents[1]
    model_path = project_root / "models" / "logreg.pkl"
    meta_path = project_root / "models" / "logreg_meta.json"
    if not model_path.exists() or not meta_path.exists():
        def _noop(_feat: Dict[str, float]):
            return {}
        return _noop
    try:
        import joblib
        import json
        clf = joblib.load(model_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        classes = [str(x) for x in meta.get("classes", [])]
        feat_keys = meta.get("feature_keys", [])

        def _predict_proba(feat: Dict[str, float]):
            if not classes or not feat_keys:
                return {}
            dir_deg = float(feat.get("fft_dir_deg", 0.0))
            fft_dir_sin = np.sin(np.deg2rad(dir_deg))
            fft_dir_cos = np.cos(np.deg2rad(dir_deg))
            feat_map = {
                "spec_ratio": float(feat.get("spec_ratio", 0.0)),
                "hl_blob_area": float(feat.get("hl_blob_area", 0.0)),
                "lap_var": float(feat.get("lap_var", 0.0)),
                "lbp_dist": float(feat.get("lbp_dist", 0.0)),
                "gabor_aniso": float(feat.get("gabor_aniso", 0.0)),
                "fft_peak": float(feat.get("fft_peak", 0.0)),
                "fft_dir_sin": float(fft_dir_sin),
                "fft_dir_cos": float(fft_dir_cos),
                "transparency": float(feat.get("transparency", 0.0)),
                "edge_sharp": float(feat.get("edge_sharp", 0.0)),
            }
            x = np.asarray([[float(feat_map.get(k, 0.0)) for k in feat_keys]], dtype=np.float32)
            prob = clf.predict_proba(x)[0]
            return {classes[i]: float(prob[i]) for i in range(len(classes))}

        return _predict_proba
    except Exception:
        def _noop(_feat: Dict[str, float]):
            return {}
        return _noop


