# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import streamlit as st
import cv2

from src.features import extract_features
from src.region_recommender import score_by_features
try:
    from src.calibrator import load_logreg
except Exception:
    def load_logreg():
        return lambda _feat: {}


st.set_page_config(page_title="Evaluate Labeled Patches", layout="wide")
st.title("棣冩惓 Evaluate Labeled Patches")

# Sidebar controls
use_logreg = st.sidebar.checkbox("Use logreg fusion", value=True)
alpha = st.sidebar.slider("Rule weight 浼?, 0.0, 1.0, 0.6, 0.05)


@st.cache_data(show_spinner=False)
def _load_labeled_samples(root: Path) -> List[Tuple[str, Path, Dict]]:
    items: List[Tuple[str, Path, Dict]] = []
    for cls_dir in sorted(root.glob("*/")):
        if not cls_dir.is_dir():
            continue
        y_true = cls_dir.name
        for js in sorted(cls_dir.glob("*.json")):
            try:
                data = json.loads(js.read_text(encoding="utf-8"))
                items.append((y_true, js, data))
            except Exception:
                continue
    return items


def _score_one(sidecar: Dict, alpha_rule: float, use_cal: bool) -> Tuple[Dict[str, float], List[Tuple[str, float]]]:
    # Prepare feat_dict as region_recommender expects
    feat_low = sidecar.get("features", {}) or {}
    feat_dict = {"attrs": {"visual": {}}, "features": feat_low}
    # Rule-based scores
    rule_scored = score_by_features(feat_dict, rules=None, weights={})
    # Flatten to list
    names = list(rule_scored.keys())
    base = [(k, float(rule_scored[k].get("total", 0.0))) for k in names]
    # Optional logreg
    if use_cal:
        predict_proba = load_logreg()
        probs = predict_proba(feat_low)
    else:
        probs = {}
    fused: Dict[str, float] = {}
    for k, s in base:
        p = float(probs.get(k, 0.0))
        fused[k] = float(alpha_rule * s + (1.0 - alpha_rule) * p)
    ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)
    return fused, ranked


def _confusion_matrix(classes: List[str], y_true: List[int], y_pred: List[int]) -> np.ndarray:
    n = len(classes)
    M = np.zeros((n, n), dtype=np.int32)
    for t, p in zip(y_true, y_pred):
        if 0 <= t < n and 0 <= p < n:
            M[t, p] += 1
    return M


def main():
    project_root = Path(__file__).resolve().parents[1]
    labeled_root = project_root / "data" / "patches" / "labeled"
    samples = _load_labeled_samples(labeled_root)
    if not samples:
        st.info("No labeled patches found.")
        return

    # Collect class list
    classes = sorted(list({y for (y, _p, _d) in samples}))
    class_to_idx = {c: i for i, c in enumerate(classes)}

    y_true_idx: List[int] = []
    y_pred_idx: List[int] = []
    top1_hits = 0
    top3_hits = 0
    hard_samples: List[Tuple[str, float, float]] = []  # (json_path, s1, s2)

    detailed_rows = []

    for (y_true, js_path, data) in samples:
        fused, ranked = _score_one(data, alpha, use_logreg)
        if not ranked:
            continue
        pred, s1 = ranked[0]
        s2 = ranked[1][1] if len(ranked) > 1 else 0.0
        y_true_idx.append(class_to_idx.get(y_true, -1))
        y_pred_idx.append(class_to_idx.get(pred, -1))
        if pred == y_true:
            top1_hits += 1
        top3 = [k for (k, _v) in ranked[:3]]
        if y_true in top3:
            top3_hits += 1
        if abs(s1 - s2) < 0.05:
            hard_samples.append((str(js_path), float(s1), float(s2)))
        detailed_rows.append({
            "truth": y_true,
            "pred": pred,
            "s1": float(s1),
            "s2": float(s2),
            "in_top3": y_true in top3,
            "json": str(js_path),
        })

    n = len(y_true_idx)
    acc1 = float(top1_hits) / float(n) if n else 0.0
    acc3 = float(top3_hits) / float(n) if n else 0.0
    st.subheader("Overall Metrics")
    st.write({"overall@1": round(acc1, 4), "overall@3": round(acc3, 4), "count": n})

    # Per-class precision/recall
    M = _confusion_matrix(classes, y_true_idx, y_pred_idx)
    precision = []
    recall = []
    for i, c in enumerate(classes):
        tp = int(M[i, i])
        fp = int(M[:, i].sum() - tp)
        fn = int(M[i, :].sum() - tp)
        p = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
        r = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
        precision.append(p)
        recall.append(r)
    st.subheader("Per-class Precision / Recall")
    table_rows = []
    for i, c in enumerate(classes):
        table_rows.append({"class": c, "precision": round(precision[i], 4), "recall": round(recall[i], 4), "support": int(M[i, :].sum())})
    st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.subheader("Confusion Matrix (rows=true, cols=pred)")
    st.dataframe(M.tolist(), use_container_width=True)

    # Most confused pairs (off-diagonal highest)
    confused: List[Tuple[str, str, int]] = []
    for i, a in enumerate(classes):
        for j, b in enumerate(classes):
            if i == j:
                continue
            cnt = int(M[i, j])
            if cnt > 0:
                confused.append((a, b, cnt))
    confused.sort(key=lambda x: x[2], reverse=True)
    st.subheader("Most Confused Pairs (Top 10)")
    st.dataframe([{"true": a, "pred": b, "count": n} for (a, b, n) in confused[:10]], use_container_width=True, hide_index=True)

    st.subheader("Hard Samples (|s1 - s2| < 0.05)")
    if hard_samples:
        st.dataframe([{"json": p, "s1": s1, "s2": s2} for (p, s1, s2) in hard_samples], use_container_width=True, hide_index=True)
    else:
        st.caption("None")

    with st.expander("Details"):
        st.dataframe(detailed_rows, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()


