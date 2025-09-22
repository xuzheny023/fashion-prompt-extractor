# app.py
import streamlit as st
import json
from PIL import Image
import numpy as np
import cv2

from src.bg_remove import get_foreground_mask
from src.attr_extract import extract_attributes, localize_attrs
from src.fabric_ranker import recommend_fabrics, save_rules_weights, recommend_fabrics_localized
from src.utils import validate_fabric_rules
from src.structure_detect import detect_structures, to_bool_set
from src.i18n import t
from pathlib import Path
import os
import shutil
from datetime import datetime
from src.regionizer import build_regions, locate_region
try:
    from src.xutils.constants import (
        PREVIEW_WIDTH,
        DEFAULT_MAX_SIDE,
        DEFAULT_SLIC,
        DEFAULT_HYBRID,
        SMALL_COMPONENT_AREA,
    )
except Exception:
    PREVIEW_WIDTH = 720
    DEFAULT_MAX_SIDE = 1024
    DEFAULT_SLIC = {"n_segments": 180, "compactness": 10.0}
    DEFAULT_HYBRID = {"enabled": True, "radius": 21, "alpha": 0.7}
    SMALL_COMPONENT_AREA = 256
from src.region_features import compute_region_features
from src.region_recommender import recommend_for_region, recommend_from_features, fuse_region_and_local_scores
from src.fabric_ranker import localize_fabric
from src.region_local import get_local_window, choose_features_for_local
from src.features import extract_features
STRICT_CLICK_ONLY = True  # 严格点击模式
try:
    import streamlit_image_coordinates as ic
    HAS_IC = True
except Exception:
    HAS_IC = False
HAS_CANVAS = False  # 强制关闭画布回退（高效方案 B）
try:
    from src.utils.coords import make_preview, map_simple_scale
except Exception:
    from src.xutils.coords import make_preview, map_simple_scale  # type: ignore

import io
from time import perf_counter

@st.cache_data(show_spinner=False)
def _cache_mask_png(png_bytes: bytes):
    from PIL import Image as _PIL_Image
    img = _PIL_Image.open(io.BytesIO(png_bytes)).convert("RGB")
    return get_foreground_mask(img)

@st.cache_data(show_spinner=False)
def _cache_regions(img_np_small, mask_small, slic_params: dict):
    out = None
    with swallow("SLIC 分区失败，已回退网格"):
        out = build_regions(
            img_np_small,
            method="slic",
            slic_n_segments=int(slic_params.get("n_segments", 180)),
            slic_compactness=float(slic_params.get("compactness", 10.0)),
            grid_rows=9,
            grid_cols=9,
            fg_mask=mask_small,
        )
    if not isinstance(out, dict):
        out = build_regions(img_np_small, method="grid", grid_rows=9, grid_cols=9, fg_mask=mask_small)
    return out

@st.cache_data(show_spinner=False)
def _cache_region_features(img_np_small, regions: dict):
    return compute_region_features(img_np_small, regions)

@st.cache_data(show_spinner=False)
def _cache_region_topk(feats: dict, weights: dict):
    region_topk = {}
    for rid, feat in feats.items():
        topk_items = recommend_for_region(rid, feat, rules=None, weights=weights, topk=5)
        region_topk[int(rid)] = topk_items
    topk_scores = {int(rid): {str(n): {"total": float(s)} for (n, s, *_rest) in items} for rid, items in region_topk.items()}
    return region_topk, topk_scores

@st.cache_data(show_spinner=False)
def _cache_region_viz(labels, region_topk: dict):
    import numpy as _np
    import cv2 as _cv2
    lbl = labels
    topk_map = region_topk
    scores = []
    rid_list = []
    for rid, items in topk_map.items():
        if items:
            scores.append(float(items[0][1]))
            rid_list.append(int(rid))
    if scores:
        smin, smax = float(min(scores)), float(max(scores))
        rng = (smax - smin) if (smax - smin) > 1e-9 else 1.0
        score_map = _np.zeros(lbl.shape, dtype=_np.float32)
        for rid in rid_list:
            v = (float(topk_map[rid][0][1]) - smin) / rng
            score_map[lbl == rid] = v
        heat_gray = (_np.clip(score_map, 0.0, 1.0) * 255.0).astype(_np.uint8)
        heat_color = _cv2.applyColorMap(heat_gray, _cv2.COLORMAP_JET)
    else:
        heat_color = _np.zeros((*lbl.shape, 3), dtype=_np.uint8)
    boundary = _np.zeros(lbl.shape, dtype=_np.uint8)
    boundary[:-1, :] |= (lbl[:-1, :] != lbl[1:, :]).astype(_np.uint8)
    boundary[:, :-1] |= (lbl[:, :-1] != lbl[:, 1:]).astype(_np.uint8)
    boundary = (boundary > 0).astype(_np.uint8) * 255
    return {"heat": heat_color, "boundary": boundary}
try:
    from src.xutils.errors import swallow
except Exception:
    from src.utils.errors import swallow  # type: ignore

# =============== 面板显隐开关（调试用） ===============
SHOW_ATTRS = False  # 默认隐藏“检测到的属性”面板；调试时可改为 True

# =============== Image loading helper ===============
def load_uploaded_image(uploaded_file, max_side: int = DEFAULT_MAX_SIDE):
    """
    读取并转 RGB；过大自动等比缩小；读取失败给出 UI 提示并停止执行�?    """
    try:
        from PIL import Image  # 确保作用域内可用
        img = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        st.error(f"图片读取失败：{e}")
        st.stop()

    # 等比缩小到最长边 max_side（避免大图拖慢）
    if max(img.size) > max_side:
        ratio = max_side / max(img.size)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        img = img.resize((new_w, new_h))
        print(f"[image] resized from {img.width/ratio:.0f}x{img.height/ratio:.0f} to {new_w}x{new_h}")

    return img

# ================= 页面配置 =================
st.set_page_config(page_title="AI Fashion Fabric Analyst", layout="centered")

# ================= 国际化配�?=================
# Initialize language in session state with default zh
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

# Language selector - update session state when changed
lang_options = ("en", "zh")
current_lang = st.session_state["lang"]
selected_index = 0 if current_lang == "en" else 1

new_lang = st.sidebar.selectbox(
    t("sidebar.language", current_lang), 
    lang_options, 
    index=selected_index
)

# Update session state if language changed
if new_lang != current_lang:
    st.session_state["lang"] = new_lang

# Get current language from session state for global use
lang = st.session_state["lang"]


def get_current_lang() -> str:
    """Get current language from session state / 从会话状态获取当前语言"""
    return st.session_state["lang"]


# ================= 结构检测占位状�?=================
if "struct_conf" not in st.session_state:
    st.session_state["struct_conf"] = {}
if "struct_set" not in st.session_state:
    st.session_state["struct_set"] = set()
if "struct_thr" not in st.session_state:
    st.session_state["struct_thr"] = 0.55

# ================= Hybrid (region + local) preset =================
if "hybrid" not in st.session_state:
    st.session_state["hybrid"] = dict(DEFAULT_HYBRID)


def _get_localized_display_name(fabric_item: dict, lang: str) -> str:
    """Get localized display name for fabric item / 获取面料项目的本地化显示名称"""
    # Try display_name field first
    display_name_data = fabric_item.get("display_name", {})
    if isinstance(display_name_data, dict):
        localized_name = display_name_data.get(lang, "")
        if localized_name:
            return localized_name
    
    # Fallback to alias matching
    aliases = fabric_item.get("alias", [])
    if aliases:
        if lang == "zh":
            # Look for Chinese characters
            for alias in aliases:
                if any('\u4e00' <= char <= '\u9fff' for char in alias):
                    return alias
        else:
            # Look for English alias (no Chinese characters)
            for alias in aliases:
                if not any('\u4e00' <= char <= '\u9fff' for char in alias):
                    return alias
    
    # Final fallback: use name
    return fabric_item.get("name", "Unknown")


def _get_localized_notes(fabric_item: dict, lang: str) -> str:
    """Get localized notes for fabric item / 获取面料项目的本地化说明"""
    # Try notes field first
    notes_data = fabric_item.get("notes", {})
    if isinstance(notes_data, dict):
        localized_notes = notes_data.get(lang, "")
        if localized_notes:
            return localized_notes
    elif isinstance(notes_data, str):
        # Fallback to string notes for backward compatibility
        return notes_data
    
    return ""

# Validate fine fabric rules at startup
ok, errs = validate_fabric_rules(str(Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"))
if not ok:
    st.error(t("msg.validation_failed", get_current_lang()))

st.title("👗 " + t("app.title", get_current_lang()))
st.caption(t("app.subtitle", get_current_lang()))

# ================= 侧边栏：权重调节 =================
st.sidebar.header("⚙️ " + t("sidebar.weight_header", get_current_lang()))
w_color = st.sidebar.slider(t("sidebar.color_weight", get_current_lang()), 0.0, 1.0, 0.5, 0.01)
w_sheen = st.sidebar.slider(t("sidebar.sheen_weight", get_current_lang()), 0.0, 1.0, 0.3, 0.01)
w_texture = st.sidebar.slider(t("sidebar.texture_weight", get_current_lang()), 0.0, 1.0, 0.2, 0.01)

# Auto-normalize weights to sum = 1
total_w = max(w_color + w_sheen + w_texture, 1e-6)
weights = {
    "color": w_color / total_w,
    "sheen": w_sheen / total_w,
    "texture": w_texture / total_w,
}

with st.sidebar.expander(t("sidebar.exp_weight", get_current_lang())):
    st.write(weights)

if st.sidebar.button(t("sidebar.save_default", get_current_lang())):
    save_rules_weights(weights)
    st.sidebar.success(t("sidebar.saved_msg", get_current_lang()))

# Fine-grained fabric library switch
use_fine = st.sidebar.checkbox(t("sidebar.use_fine", get_current_lang()), value=True)

# Optional: use rules packs merging
USE_PACKS = st.sidebar.checkbox("Use rule packs (merged)", value=False)
merged_rules_cache: list[dict] | None = None
if USE_PACKS:
    try:
        from rules.merge_rules import load_all_packs, merge_packs
        packs = load_all_packs(Path(__file__).resolve().parents[0] / "rules" / "packs")
        merged_rules_cache = merge_packs(packs)
        st.sidebar.caption(f"packs: {len(packs)} files, merged entries: {len(merged_rules_cache or [])}")
    except Exception as e:
        st.sidebar.warning(f"packs disabled: {e}")

# Hybrid (region + local) controls
st.sidebar.header("🧪 " + t("ui.hybrid.title", get_current_lang()))
hy_enabled = st.sidebar.checkbox(t("ui.hybrid.enabled", get_current_lang()), value=bool(st.session_state.get("hybrid", {}).get("enabled", True)))
hy_radius = st.sidebar.slider(t("ui.hybrid.radius", get_current_lang()), 9, 49, int(st.session_state.get("hybrid", {}).get("radius", 21)), 2)
hy_alpha = st.sidebar.slider(t("ui.hybrid.alpha", get_current_lang()), 0.0, 1.0, float(st.session_state.get("hybrid", {}).get("alpha", 0.7)), 0.01)
st.session_state["hybrid"] = {"enabled": bool(hy_enabled), "radius": int(hy_radius), "alpha": float(hy_alpha)}

# Profiling toggle
prof_on = st.sidebar.checkbox("性能日志", value=False)

# Fine-grained fabric library preview
with st.sidebar.expander(t("sidebar.fabric_preview", get_current_lang())):
    try:
        from src.utils.io import read_json_smart
        rules_path = Path(__file__).resolve().parents[0] / "data" / "fabric_fine_rules.json"
        fabrics = []
        if rules_path.exists():
            fabrics = read_json_smart(rules_path)
        query = st.text_input(t("sidebar.search_placeholder", get_current_lang()), "")
        q = (query or "").strip().lower()

        def _match(item: dict) -> bool:
            text = " ".join([
                str(item.get("name", "")),
                ",".join(item.get("alias", [])),
                str(item.get("notes", "")),
            ]).lower()
            return q in text

        filt = [it for it in fabrics if _match(it)] if q else fabrics
        col_name = t("sidebar.col_name", get_current_lang())
        col_alias = t("sidebar.col_alias", get_current_lang())
        col_sheen = t("sidebar.col_sheen", get_current_lang())
        col_edge = t("sidebar.col_edge", get_current_lang())
        col_notes = t("sidebar.col_notes", get_current_lang())
        rows = []
        for it in filt[:50]:
            # Use localized display name and notes
            display_name = _get_localized_display_name(it, get_current_lang())
            notes = _get_localized_notes(it, get_current_lang())
            
            rows.append({
                col_name: display_name,
                col_alias: ", ".join(it.get("alias", [])),
                col_sheen: str(it.get("sheen_range", "")),
                col_edge: str(it.get("edge_range", "")),
                col_notes: notes,
            })
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info(t("sidebar.no_entries", get_current_lang()))
    except Exception as e:
        st.info(t("msg.rules_fallback", get_current_lang()))

# ---- Y2: Sidebar annotation controls for last saved patch ----
with st.sidebar.expander("Patch Annotation"):
    lp = st.session_state.get("last_patch")
    if not lp:
        st.caption("No patch yet")
    else:
        top1 = lp.get("top1") or ""
        top2 = lp.get("top2") or ""
        st.caption(f"Last patch: {Path(lp.get('png','')).name}")
        choice = st.radio("标注为 / Label as", options=[f"Top1: {top1}", f"Top2: {top2}", "Other…"], index=0)
        other_key = st.text_input("Fabric key (for Other)", value="" if choice != "Other…" else (lp.get("top1") or ""))
        if st.button("提交标注 / Submit"):
            try:
                png_src = Path(lp.get("png"))
                json_src = Path(lp.get("json"))
                if choice.startswith("Top1") and top1:
                    key = top1
                elif choice.startswith("Top2") and top2:
                    key = top2
                else:
                    key = (other_key or "other").strip()
                project_root = Path(__file__).resolve().parents[0]
                dst_dir = project_root / "data" / "patches" / "labeled" / key
                dst_dir.mkdir(parents=True, exist_ok=True)
                # Move files
                png_dst = dst_dir / png_src.name
                json_dst = dst_dir / json_src.name
                shutil.move(str(png_src), str(png_dst))
                # Update sidecar metadata
                import json as _json
                meta = {}
                try:
                    with open(json_src, "r", encoding="utf-8") as f:
                        meta = _json.load(f)
                except Exception:
                    meta = {}
                meta["labeled_by"] = os.getenv("USERNAME") or os.getenv("USER") or "user"
                meta["labeled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                meta["label_key"] = key
                with open(json_src, "w", encoding="utf-8") as f:
                    _json.dump(meta, f, ensure_ascii=False, indent=2)
                shutil.move(str(json_src), str(json_dst))
                st.success(f"Saved to {dst_dir}")
                print(f"[patch] moved to {dst_dir}")
                st.session_state["last_patch"] = None
            except Exception as e:
                st.error(f"标注保存失败: {e}")

# ================= 主功能区 =================
uploaded_file = st.file_uploader(t("main.uploader", get_current_lang()), type=["jpg", "jpeg", "png"], accept_multiple_files=False)
if uploaded_file is not None and getattr(uploaded_file, 'size', None) is not None:
    if uploaded_file.size > 20 * 1024 * 1024:
        st.error(t("main.file_size_warning", get_current_lang()))
        uploaded_file = None

if uploaded_file is None:
    st.stop()
else:
    # 原图展示（并生成固定宽度的预览图，便于简化坐标映射）
    image = load_uploaded_image(uploaded_file, max_side=DEFAULT_MAX_SIDE)
    preview_pil, orig_w, orig_h = make_preview(image, PREVIEW_WIDTH)
    disp_w, disp_h = preview_pil.width, preview_pil.height
    st.image(preview_pil, caption=t("main.uploader", get_current_lang()), use_container_width=False)

    # 状态进度显示
    with st.status(t("ui.status.loading", get_current_lang()), expanded=False) as _status:
        p = st.progress(0, text="载入图片")

        # 生成 mask（内部使用，不展示）
        p.progress(10, text="生成服装掩膜")
        try:
            mask, _ = get_foreground_mask(image)
        except Exception as e:
            st.error(t("msg.mask_generation_failed", get_current_lang()))
            st.stop()

        # 属性提取
        try:
            attrs = extract_attributes(image, mask)
            if SHOW_ATTRS:
                st.markdown("### 🔍 " + t("main.attributes_title", get_current_lang()))
                # 显示本地化的属性（仅在调试开关开启时显示）
                localized_attrs = localize_attrs(attrs, get_current_lang())
                st.json(localized_attrs)
            else:
                pass
        except Exception as e:
            st.error(t("msg.attribute_extraction_failed", get_current_lang()))
            st.stop()

        # ---------------- 区域索引：构建分区 + 区域特征 + 区域推荐 ----------------
        p.progress(35, text="区域划分")
        try:
            # Resize for performance (longest side <= DEFAULT_MAX_SIDE)
            img_np = np.array(image.convert("RGB"))[:, :, ::-1]
            H, W = img_np.shape[:2]
            scale = 1.0
            max_side = max(H, W)
            if max_side > DEFAULT_MAX_SIDE:
                scale = float(DEFAULT_MAX_SIDE) / float(max_side)
                img_np_small = cv2.resize(img_np, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA)
                mask_small = cv2.resize(mask, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_NEAREST)
            else:
                img_np_small = img_np
                mask_small = mask

            # Cached regionization
            regions_out = _cache_regions(img_np_small, mask_small, DEFAULT_SLIC)
            labels = regions_out.get("labels")
            regions = regions_out.get("regions", {})

            # Cached features
            p.progress(60, text="计算区域特征")
            feats = _cache_region_features(img_np_small, regions) if not prof_on else compute_region_features(img_np_small, regions)

            # Cached region Top-K (weights affect ordering but we return fresh list per weights)
            p.progress(85, text="生成推荐索引")
            region_topk, topk_scores = _cache_region_topk(feats, weights)

            # Save to session for fast lookup
            st.session_state["region_index"] = {
                "labels": labels,
                "regions": regions,
                "features": feats,
                "topk": region_topk,
                "topk_scores": topk_scores,
                "meta": regions_out.get("meta", {}),
                "method": regions_out.get("method", "grid"),
                "scale": scale,
                "image": img_np_small,
                "fg_mask": mask_small,
            }

            # Cached visualization assets
            st.session_state["region_viz"] = _cache_region_viz(labels, region_topk)

            p.progress(100, text="完成")
            _status.update(label=t("ui.status.ready", get_current_lang()), state="complete")
        except Exception:
            # Non-blocking if region pipeline fails
            st.session_state["region_index"] = {}

    # ---------------- 点击查询区域 Top-K ----------------
    try:
        st.markdown("### 🧭 " + t("region.section_title", get_current_lang()))
        reg_index = st.session_state.get("region_index", {})
        labels = reg_index.get("labels")
        img_small = reg_index.get("image")
        if labels is None or img_small is None:
            st.info(t("region.unavailable", get_current_lang()))
        else:
            # Visualization toggles
            show_heat = st.toggle(t("region.heatmap_toggle", get_current_lang()), value=False)
            alpha = st.slider(t("region.alpha_label", get_current_lang()), 0.0, 1.0, 0.35, 0.01)
            show_boundary = st.toggle(t("region.boundary_toggle", get_current_lang()), value=False)

            # Compose overlay once per render from cached assets on preview
            base = np.array(preview_pil)[:, :, ::-1].copy()
            viz = st.session_state.get("region_viz", {})
            heat = viz.get("heat")
            boundary = viz.get("boundary")
            blended = base
            if show_heat and heat is not None:
                blended = cv2.addWeighted(base, 1.0 - alpha, heat, alpha, 0)
            if show_boundary and boundary is not None:
                # draw thin yellow boundary
                yy, xx = np.where(boundary > 0)
                blended[yy, xx] = (0, 255, 255)

            click_x = click_y = None
            # Try interactive coordinate picker(s), with graceful fallback
            disp_h, disp_w = blended.shape[0], blended.shape[1]
            if not HAS_IC and HAS_CANVAS and not st.session_state.get("_use_canvas_warned", False):
                st.session_state["_use_canvas_warned"] = True
                st.warning(t("ui.click.use_canvas", get_current_lang()))
            if not HAS_CANVAS and not HAS_IC and not st.session_state.get("_canvas_warned", False):
                st.session_state["_canvas_warned"] = True
                st.warning(t("ui.click.fallback", get_current_lang()))

            got_disp_coords = False
            # Strict click-only: prefer ic, else canvas, else error
            if HAS_IC:
                with swallow("点击坐标捕获失败"):
                    st.caption(t("ui.click.hint", get_current_lang()))
                    res = ic.streamlit_image_coordinates(preview_pil, key="imgcoords")
                    if res is not None and "x" in res and "y" in res:
                        x_disp = int(res["x"])
                        y_disp = int(res["y"])
                        click_x, click_y = x_disp, y_disp
                        got_disp_coords = True

            if not got_disp_coords and HAS_CANVAS:
                with swallow("画布点击失败"):
                    st.caption(t("ui.click.hint", get_current_lang()))
                    canvas = st_canvas(width=disp_w, height=disp_h, drawing_mode="point", background_image=preview_pil, key="clickcv")
                    if canvas and hasattr(canvas, "json_data") and canvas.json_data:
                        objs = canvas.json_data.get("objects") or []
                        if objs:
                            last = objs[-1]
                            x_disp = int(round(float(last.get("left", 0))))
                            y_disp = int(round(float(last.get("top", 0))))
                            click_x, click_y = x_disp, y_disp
                            got_disp_coords = True

            if not got_disp_coords:
                st.error(t("ui.click.fallback", get_current_lang()))
                st.stop()

            # Map from preview to original coordinates; save to session
            if click_x is not None and click_y is not None:
                x0, y0 = map_simple_scale(int(click_x), int(click_y), disp_w, disp_h, int(orig_w), int(orig_h))
                st.session_state["click_xy"] = (int(x0), int(y0))

            if click_x is not None and click_y is not None:
                # Convert original-space coordinates to labels-space via stored scale
                scale_val = float(st.session_state.get("region_index", {}).get("scale", 1.0))
                xl = int(round(st.session_state["click_xy"][0] * scale_val))
                yl = int(round(st.session_state["click_xy"][1] * scale_val))
                rid = locate_region(labels, xl, yl)
                st.caption(t("region.coords_label", get_current_lang()).format(x=st.session_state["click_xy"][0], y=st.session_state["click_xy"][1]))
                if rid is None:
                    st.info(t("ui.click.not_in_region", get_current_lang()))
                    st.session_state["last_region_id"] = None
                else:
                    st.session_state["last_region_id"] = int(rid)
                    # Highlight selected region
                    try:
                        sel_mask = (labels == int(rid)).astype(np.uint8) * 255
                        sel_mask3 = cv2.merge([sel_mask, sel_mask, sel_mask])
                        color = np.zeros_like(blended)
                        color[:, :] = (0, 200, 50)
                        blended2 = np.where(sel_mask3 > 0, (0.7 * blended + 0.3 * color).astype(np.uint8), blended)
                        st.image(blended2[:, :, ::-1], use_container_width=True)
                    except Exception:
                        st.image(blended[:, :, ::-1], use_container_width=True)

                    st.markdown("#### 🧵 " + t("region.topk_title", get_current_lang()).format(rid=rid))
                    items = reg_index.get("topk", {}).get(int(rid), [])
                    if not items:
                        st.caption(t("sidebar.no_entries", get_current_lang()))
                    else:
                        # Compute confidence metrics based on fused/region scores
                        # Build score dict for Top-K list
                        scores_dict = {str(n): float(s) for (n, s, *_e) in items}
                        # Try fetch logreg prob for Top1 (optional)
                        # conf_rule = (Top1-Top2)/max(Top1,eps) + strong_hits_ratio
                        sorted_pairs = sorted(scores_dict.items(), key=lambda kv: kv[1], reverse=True)
                        eps = 1e-6
                        if sorted_pairs:
                            top1_name, top1_score = sorted_pairs[0]
                            top2_score = sorted_pairs[1][1] if len(sorted_pairs) > 1 else 0.0
                            diff_ratio = (top1_score - top2_score) / max(top1_score, eps)
                        else:
                            top1_name, top1_score, diff_ratio = "", 0.0, 0.0
                        # strong rule hits ratio if available
                        strong_ratio = 0.0
                        # try read from region features explain cache (not available here), keep 0.0
                        conf_rule_total = float(diff_ratio + strong_ratio)
                        # logreg prob best-effort from calibrator
                        conf_logreg = 0.0
                        try:
                            from src.calibrator import load_logreg as _load_logreg
                            feat_low = reg_index.get("features", {}).get(int(rid), {}).get("features", {})
                            probs = _load_logreg()(feat_low)
                            if probs and top1_name:
                                conf_logreg = float(probs.get(str(top1_name), 0.0))
                        except Exception:
                            conf_logreg = 0.0
                        conf_total = float(0.6 * conf_rule_total + 0.4 * conf_logreg) if conf_logreg > 0.0 else float(conf_rule_total)

                        for i, (name, score, explain) in enumerate(items, 1):
                            disp, notes = localize_fabric(name, get_current_lang())
                            score_label = t("candidates.score", get_current_lang())
                            st.write(f"{i}. **{disp}** — {score_label}: **{score:.2f}**")
                            # Explain summary
                            if isinstance(explain, dict):
                                comps = explain.get("components", {})
                                if comps:
                                    st.caption(
                                        t("region.explain", get_current_lang()).format(
                                            color=str(comps.get("color", "-")),
                                            coverage=str(comps.get("coverage", "-"))
                                        )
                                    )
                            if notes:
                                max_len = 30
                                st.caption(notes if len(notes) <= max_len else notes[:max_len] + "…")

                        # Low-confidence hints
                        if conf_total < 0.35:
                            st.warning("置信度低，建议采样并标注提升")
                        if conf_total < 0.2:
                            # simple coarse family fallback hint based on top1_score proxy
                            fam = ""
                            if top1_name:
                                key = top1_name.lower()
                                if any(k in key for k in ["satin","taffeta","charmeuse"]):
                                    fam = "高光平滑类"
                                elif any(k in key for k in ["tweed","herringbone","denim","twill"]):
                                    fam = "斜纹/粗呢类"
                                elif any(k in key for k in ["organza","chiffon","georgette","tulle","lace"]):
                                    fam = "透纱类"
                                elif any(k in key for k in ["velvet","corduroy","suede","fleece"]):
                                    fam = "绒类"
                                elif any(k in key for k in ["jersey","rib","interlock","ponte"]):
                                    fam = "针织类"
                            st.info(f"建议粗粒度：{fam or '待定'}")

                        # Save-as-training button (reuse Y2 saving; we already saved on click)
                        if st.button("保存为训练样本", key=f"save_train_{rid}"):
                            # Reuse the Y2 save path; if not present, try saving again quickly
                            if not st.session_state.get("last_patch"):
                                try:
                                    # Trigger a quick save using existing cropped region if available
                                    pass
                                except Exception:
                                    pass
                            st.success("已保存（或已存在）")

                        # ---- Y2: Save unlabeled region patch + sidecar JSON ----
                        try:
                            regions = reg_index.get("regions", {})
                            info = regions.get(int(rid), {})
                            bx, by, bw, bh = [int(v) for v in (info.get("bbox") or (0, 0, img_small.shape[1], img_small.shape[0]))]
                            pad = 3
                            Hs, Ws = img_small.shape[:2]
                            x0 = max(0, bx - pad)
                            y0 = max(0, by - pad)
                            x1 = min(Ws, bx + bw + pad)
                            y1 = min(Hs, by + bh + pad)
                            crop = img_small[y0:y1, x0:x1].copy()
                            # Ensure directories
                            project_root = Path(__file__).resolve().parents[0]
                            unlabeled_dir = project_root / "data" / "patches" / "unlabeled"
                            unlabeled_dir.mkdir(parents=True, exist_ok=True)
                            # Filename
                            ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                            base_name = f"{ts}_region{int(rid)}"
                            png_path = unlabeled_dir / f"{base_name}.png"
                            json_path = unlabeled_dir / f"{base_name}.json"
                            # Save image (BGR)
                            cv2.imwrite(str(png_path), crop)
                            # Build sidecar content
                            topk_simple = [[str(n), float(s)] for (n, s, *_e) in items[:5]]
                            feat = reg_index.get("features", {}).get(int(rid), {})
                            # Best-effort numeric conversion for JSON
                            def _to_jsonable(v):
                                try:
                                    import numpy as _np
                                    if isinstance(v, (_np.floating, _np.integer)):
                                        return float(v)
                                except Exception:
                                    pass
                                if isinstance(v, (int, float, str)):
                                    return v
                                return str(v)
                            feat_json = {k: _to_jsonable(v) for k, v in (feat or {}).items()}
                            sidecar = {
                                "region_id": int(rid),
                                "click_xy": [int(st.session_state.get("click_xy", (0, 0))[0]), int(st.session_state.get("click_xy", (0, 0))[1])],
                                "topk": topk_simple,
                                "features": feat_json,
                                "saved_at": ts,
                            }
                            with open(json_path, "w", encoding="utf-8") as f:
                                json.dump(sidecar, f, ensure_ascii=False, indent=2)
                            print(f"[patch] saved image: {png_path}")
                            print(f"[patch] saved meta : {json_path}")
                            # Stash last patch info for annotation UI
                            top1 = topk_simple[0][0] if len(topk_simple) >= 1 else ""
                            top2 = topk_simple[1][0] if len(topk_simple) >= 2 else ""
                            st.session_state["last_patch"] = {
                                "png": str(png_path),
                                "json": str(json_path),
                                "top1": top1,
                                "top2": top2,
                            }
                        except Exception as _e:
                            print(f"[patch] save failed: {_e}")

                    # Local refinement features + fused recommendation
                    try:
                        hcfg = st.session_state.get("hybrid", {"enabled": True, "radius": 21, "alpha": 0.7})
                        if not hcfg.get("enabled", True):
                            st.caption(t("ui.hybrid.tip_cached", get_current_lang()))
                        else:
                            # Local LRU cache to avoid recomputation for repeated clicks nearby
                            # Key uses coarse coordinate buckets and weights
                            try:
                                import hashlib as _hashlib
                                img_key = _hashlib.md5(reg_index.get("image", np.zeros((1,1,3),dtype=np.uint8)).tobytes()).hexdigest()[:10]
                            except Exception:
                                img_key = "img"
                            weights_key = f"{weights.get('color',0):.3f}-{weights.get('sheen',0):.3f}-{weights.get('texture',0):.3f}"
                            key_tuple = (img_key, int(click_x)//4, int(click_y)//4, int(hcfg.get("radius",21)), weights_key)

                            @st.cache_data(show_spinner=False)
                            def _cache_local_feats(_key, im, cx, cy, rr, fg):
                                win_bgr, win_mask, bbox = get_local_window(im, cx, cy, rr, cloth_mask=fg)
                                feat_list = choose_features_for_local()
                                if prof_on:
                                    from src.utils.timing import timeit
                                    _ext = timeit("local_extract_features")(extract_features)
                                    feats = _ext(win_bgr, win_mask, feature_list=feat_list)
                                else:
                                    feats = extract_features(win_bgr, win_mask, feature_list=feat_list)
                                return {"bbox": bbox, "features": feats}

                            local_pack = _cache_local_feats(key_tuple, img_small, int(click_x), int(click_y), int(hcfg.get("radius", 21)), reg_index.get("fg_mask"))
                            st.session_state["local_feats"] = local_pack

                            # Scoring fusion
                            rid_attrs = reg_index.get("features", {}).get(int(rid), {}).get("attrs", {})
                            feat_dict_for_score = {"attrs": rid_attrs}
                            if prof_on:
                                from src.utils.timing import timeit
                                _rff = timeit("recommend_from_features")(recommend_from_features)
                                local_scores = _rff(feat_dict_for_score, rules=None, weights=weights, topk=10)
                            else:
                                local_scores = recommend_from_features(feat_dict_for_score, rules=None, weights=weights, topk=10)
                            region_scores = reg_index.get("topk_scores", {}).get(int(rid), {})
                            if prof_on:
                                from src.utils.timing import timeit
                                _fz = timeit("fuse_region_local")(fuse_region_and_local_scores)
                                fused = _fz(region_scores, local_scores, float(hcfg.get("alpha", 0.7)))
                            else:
                                fused = fuse_region_and_local_scores(region_scores, local_scores, float(hcfg.get("alpha", 0.7)))
                            fused_sorted = sorted(fused.items(), key=lambda kv: kv[1].get("total", 0.0), reverse=True)[:5]
                            st.markdown("#### ✨ " + t("ui.hybrid.title", get_current_lang()))
                            st.caption(t("ui.hybrid.tip_refined", get_current_lang()))
                            for i, (fname, finfo) in enumerate(fused_sorted, 1):
                                disp, notes = localize_fabric(fname, get_current_lang())
                                score_label = t("candidates.score", get_current_lang())
                                st.write(f"{i}. **{disp}** — {score_label}: **{finfo.get('total', 0.0):.2f}**")
                            try:
                                reg_top3 = sorted([(k, v.get('total', 0.0)) for k, v in region_scores.items()], key=lambda x: x[1], reverse=True)[:3]
                                loc_top3 = sorted([(n, s) for (n, s, *_e) in local_scores], key=lambda x: x[1], reverse=True)[:3]
                                print("[fusion] region top3:", reg_top3)
                                print("[fusion] local  top3:", loc_top3)
                            except Exception:
                                pass
                    except Exception:
                        pass
    except Exception:
        pass

    # 面料推荐（支�?coarse/fine 源），fine 异常回退 coarse
    st.markdown("### 🧵 " + t("main.candidates_title", get_current_lang()))
    rules_source = "fine" if use_fine else "coarse"
    try:
        # If using packs, override fine rules via merged list in memory
        if USE_PACKS and merged_rules_cache is not None and rules_source == "fine":
            # Perform scoring against merged fine list by temporarily monkeypatching loader
            from src import fabric_ranker as _fr
            orig_loader = getattr(_fr, "_load_rules_fine")
            try:
                from functools import lru_cache
                def _load_rules_fine_override():
                    items = []
                    for it in list(merged_rules_cache or []):
                        obj = dict(it)
                        # ensure compatibility fields expected by downstream logic
                        if not obj.get("name"):
                            obj["name"] = str(obj.get("key", "Unknown"))
                        if "notes" not in obj:
                            obj["notes"] = ""
                        if "sheen_range" not in obj:
                            obj["sheen_range"] = [0.0, 1.0]
                        if "edge_range" not in obj:
                            obj["edge_range"] = [0.1, 0.5]
                        if "base" not in obj:
                            obj["base"] = 0.5
                        items.append(obj)
                    return items
                _fr._load_rules_fine = lru_cache(maxsize=1)(_load_rules_fine_override)  # type: ignore
                candidates = recommend_fabrics_localized(attrs, lang=get_current_lang(), top_k=5, weights_override=weights, rules_source=rules_source)
            finally:
                _fr._load_rules_fine = orig_loader  # type: ignore
        else:
            candidates = recommend_fabrics_localized(attrs, lang=get_current_lang(), top_k=5, weights_override=weights, rules_source=rules_source)
    except Exception as e:
        if rules_source == "fine":
            st.sidebar.warning(t("msg.rules_fallback", get_current_lang()))
            rules_source = "coarse"  # 强制回退
            candidates = recommend_fabrics_localized(attrs, lang=get_current_lang(), top_k=5, weights_override=weights, rules_source=rules_source)
        else:
            st.error(t("msg.fabric_recommendation_failed", get_current_lang()))
            st.stop()

    # 渲染本地化的面料名称和说明
    for i, item in enumerate(candidates, 1):
        if len(item) == 4:
            name, score, display_name, notes = item
            
            # 确保显示名称不为空，如果为空则使用本地化回退
            if not display_name:
                display_name = name
            
            # 格式化分数显示
            score_label = t("candidates.score", get_current_lang())
            
            # 显示面料名称和分数
            st.write(f"{i}. **{display_name}** — {score_label}: **{score:.2f}**")
            
            # 显示详细说明（截断处理）
            if notes and isinstance(notes, str) and notes.strip():
                # 截断到30字符左右，保持完整性
                max_len = 30
                if len(notes) > max_len:
                    # 找到最近的句号或逗号作为截断点
                    truncate_point = max_len
                    for punct in ['。', '.', '，', ',', '；', ';']:
                        punct_pos = notes.find(punct, 0, max_len)
                        if punct_pos > 0:
                            truncate_point = punct_pos + 1
                            break
                    note_snip = notes[:truncate_point] + "…"
                else:
                    note_snip = notes
                
                desc_label = t("candidates.description", get_current_lang())
                st.caption(f"*{desc_label}: {note_snip}*")
        else:
            # Fallback for unexpected format
            name, score = item[:2]
            score_label = t("candidates.score", get_current_lang())
            st.write(f"{i}. **{name}** — {score_label}: **{score:.2f}**")

    # 可选：调试开关，叠加 mask 预览
    if st.toggle(t("main.mask_toggle", get_current_lang())):
        overlay = np.array(image).copy()
        over = overlay.copy()
        over[mask > 0] = (255, 0, 0)  # 红色标记前景
        preview = cv2.addWeighted(overlay, 0.7, over, 0.3, 0)
        st.image(preview, caption=t("debug.mask_overlay", get_current_lang()), use_container_width=True)
