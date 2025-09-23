# -*- coding: utf-8 -*-
# ui/i18n.py
import streamlit as st

# New canonical keys (from clean table)
zh = {
    # App
    "app.title": "AI面料识别推荐助手",
    "app.subtitle": "上传服装图片，智能分析推荐合适面料",

    # Sidebar - language
    "sidebar.language.label": "语言",
    "sidebar.language.zh": "简体中文",
    "sidebar.language.en": "English",

    # Sidebar - weights
    "sidebar.weights.title": "权重设置",
    "sidebar.weights.color": "颜色权重",
    "sidebar.weights.gloss": "光泽权重",
    "sidebar.weights.texture": "纹理权重",
    "sidebar.weights.advanced": "高级权重配置",

    # Sidebar - actions & flags
    "sidebar.save_default": "保存为默认",
    "sidebar.use_fine_rules": "使用精细规则",
    "sidebar.use_rule_packs": "使用规则包（合并）",

    # Sidebar - hybrid/local refine
    "sidebar.hybrid.title": "混合推荐",
    "sidebar.local_refine.enable": "启用局部细化",
    "sidebar.local_refine.radius": "局部半径",

    # Main
    "main.upload.title": "上传图片",
    "main.click_hint": "点击图片任意位置获取面料推荐",

    # Panel
    "panel.analysis.title": "分析结果",
    "panel.coord.label": "坐标",
    "panel.time.label": "时间",
    "panel.topk.title": "推荐面料",
    "panel.confidence.low": "置信度低，建议采样并标注提升",
    "panel.coarse_suggestion.label": "粗粒度建议",
    "panel.actions.save_sample": "保存为训练样本",
    "panel.actions.add_vote": "加入多点投票",
    "panel.recent_clicks.title": "最近点击",
    "panel.region_info.unavailable": "区域信息不可用",

    # Additional commonly used keys kept from previous set (aliases)
    "layout.upload_title": "上传图片",
    "layout.click_hint": "点击图片任意位置获取面料推荐",
    "layout.lang_english": "English",

    # Previous sidebar keys mapped to new text
    "sidebar.language": "语言",  # alias of sidebar.language.label
    "sidebar.weight_header": "权重设置",  # alias of sidebar.weights.title
    "sidebar.color_weight": "颜色权重",
    "sidebar.sheen_weight": "光泽权重",
    "sidebar.texture_weight": "纹理权重",
    "sidebar.exp_weight": "高级权重配置",
    "sidebar.saved_msg": "已保存！",
    "sidebar.fabric_preview": "面料预览",
    "sidebar.search_placeholder": "搜索面料...",
    "sidebar.col_name": "名称",
    "sidebar.col_alias": "别名",
    "sidebar.col_sheen": "光泽",
    "sidebar.col_edge": "边缘",
    "sidebar.col_notes": "说明",
    "sidebar.no_entries": "暂无条目",

    # Hybrid (kept for compatibility)
    "ui.hybrid.title": "混合推荐",  # alias of sidebar.hybrid.title
    "ui.hybrid.enabled": "启用局部细化",  # alias of sidebar.local_refine.enable
    "ui.hybrid.radius": "局部半径",  # alias of sidebar.local_refine.radius
    "ui.hybrid.alpha": "融合比例",
    "ui.hybrid.tip_cached": "使用区域缓存",
    "ui.hybrid.tip_refined": "已局部细化",

    # Upload & attributes (compatibility)
    "main.uploader": "上传图片",
    "main.file_size_warning": "文件过大",
    "main.attributes_title": "检测属性",

    # Status & click (compatibility)
    "ui.status.loading": "处理中",
    "ui.status.ready": "就绪",
    "ui.click.fallback": "无法捕获点击",
    "ui.click.not_in_region": "点击区域无效",

    # Region info (compatibility)
    "region.unavailable": "区域信息不可用",  # alias of panel.region_info.unavailable
    "region.coords_label": "坐标：({x}, {y})",
    "region.explain": "颜色: {color}, 覆盖: {coverage}",

    # Candidates
    "candidates.score": "评分",
    "candidates.description": "说明",

    # Families
    "family.sheen": "高光平滑类",
    "family.twill": "斜纹类",
    "family.sheer": "透纱类",
    "family.pile": "绒类",
    "family.knit": "针织类",

    # Messages
    "ui.save_success": "已保存（或已存在）",
    "msg.validation_failed": "配置校验失败",
    "msg.rules_fallback": "已回退到粗粒度规则",
    "msg.mask_generation_failed": "掩膜生成失败",
    "msg.attribute_extraction_failed": "属性提取失败",
}

en = {
    # App
    "app.title": "AI Fabric Recognition & Recommendation",
    "app.subtitle": "Upload a garment image to get smart fabric recommendations",

    # Sidebar - language
    "sidebar.language.label": "Language",
    "sidebar.language.zh": "简体中文",
    "sidebar.language.en": "English",

    # Sidebar - weights
    "sidebar.weights.title": "Weights",
    "sidebar.weights.color": "Color weight",
    "sidebar.weights.gloss": "Gloss weight",
    "sidebar.weights.texture": "Texture weight",
    "sidebar.weights.advanced": "Advanced settings",

    # Sidebar - actions & flags
    "sidebar.save_default": "Save as default",
    "sidebar.use_fine_rules": "Use fine rules",
    "sidebar.use_rule_packs": "Use rule packs (merged)",

    # Sidebar - hybrid/local refine
    "sidebar.hybrid.title": "Hybrid recommendation",
    "sidebar.local_refine.enable": "Enable local refinement",
    "sidebar.local_refine.radius": "Patch radius",

    # Main
    "main.upload.title": "Upload image",
    "main.click_hint": "Click anywhere on the image to get fabric suggestions",

    # Panel
    "panel.analysis.title": "Analysis",
    "panel.coord.label": "Coord",
    "panel.time.label": "Time",
    "panel.topk.title": "Top-K Fabrics",
    "panel.confidence.low": "Low confidence. Please sample and annotate to improve.",
    "panel.coarse_suggestion.label": "Coarse suggestion",
    "panel.actions.save_sample": "Save as training sample",
    "panel.actions.add_vote": "Add to multi-point voting",
    "panel.recent_clicks.title": "Recent clicks",
    "panel.region_info.unavailable": "Region info unavailable",

    # Aliases for compatibility with existing code
    "layout.upload_title": "Upload Image",
    "layout.click_hint": "Click anywhere on the image to get fabric recommendations",
    "layout.lang_english": "English",

    "sidebar.language": "Language",  # alias of sidebar.language.label
    "sidebar.weight_header": "Weights",  # alias of sidebar.weights.title
    "sidebar.color_weight": "Color weight",
    "sidebar.sheen_weight": "Gloss weight",
    "sidebar.texture_weight": "Texture weight",
    "sidebar.exp_weight": "Advanced settings",
    "sidebar.saved_msg": "Saved!",
    "sidebar.fabric_preview": "Fabric Preview",
    "sidebar.search_placeholder": "Search fabrics...",
    "sidebar.col_name": "Name",
    "sidebar.col_alias": "Alias",
    "sidebar.col_sheen": "Sheen",
    "sidebar.col_edge": "Edge",
    "sidebar.col_notes": "Notes",
    "sidebar.no_entries": "No entries",

    "ui.hybrid.title": "Hybrid recommendation",
    "ui.hybrid.enabled": "Enable local refinement",
    "ui.hybrid.radius": "Patch radius",
    "ui.hybrid.alpha": "Fusion Ratio",
    "ui.hybrid.tip_cached": "Using region cache",
    "ui.hybrid.tip_refined": "Locally refined",

    "main.uploader": "Upload Image",
    "main.file_size_warning": "File too large",
    "main.attributes_title": "Detected Attributes",

    "ui.status.loading": "Processing",
    "ui.status.ready": "Ready",
    "ui.click.fallback": "Cannot capture clicks",
    "ui.click.not_in_region": "Invalid click region",

    "region.unavailable": "Region info unavailable",
    "region.coords_label": "Coordinates: ({x}, {y})",
    "region.explain": "Color: {color}, Coverage: {coverage}",

    "candidates.score": "Score",
    "candidates.description": "Description",

    "family.sheen": "Glossy Smooth",
    "family.twill": "Twill",
    "family.sheer": "Sheer",
    "family.pile": "Pile",
    "family.knit": "Knit",

    "ui.save_success": "Saved (or already exists)",
    "msg.validation_failed": "Configuration validation failed",
    "msg.rules_fallback": "Fallback to coarse rules",
    "msg.mask_generation_failed": "Mask generation failed",
    "msg.attribute_extraction_failed": "Attribute extraction failed",
}


def t(key: str, lang: str = None) -> str:
    """Get localized string by key. Falls back to key if missing."""
    if lang is None:
        lang = st.session_state.get("lang", "zh")
    locale_dict = zh if lang == "zh" else en
    return locale_dict.get(key, key)
