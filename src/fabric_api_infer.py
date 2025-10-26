# -*- coding: utf-8 -*-
"""
Cloud VLM (Qwen-VL) inference for fabric analysis.
Open-Set Recognition + RAG (Retrieval-Augmented Generation).
"""

from __future__ import annotations
import os
import re
import json
import hashlib
from typing import Dict, List
import streamlit as st

try:
    from dashscope import MultiModalConversation
except Exception:
    MultiModalConversation = None


# ---------- Errors ----------
class NoAPIKeyError(RuntimeError):
    pass


# ---------- Helpers ----------
def _need_secret(name: str) -> str:
    """Read secret from st.secrets or env. Raise NoAPIKeyError if missing."""
    v = None
    try:
        v = st.secrets.get(name)
    except Exception:
        v = None
    v = v or os.getenv(name)
    if not v:
        raise NoAPIKeyError(f"Missing secret: {name}")
    return v


def _md5_file(path: str) -> str:
    """Compute MD5 hash of a file."""
    m = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            m.update(chunk)
    return m.hexdigest()


def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM response.
    
    Strategies:
    1. Try markdown code block extraction (```json ... ```)
    2. Try regex to find first JSON object
    3. Try direct json.loads
    
    Returns:
        Parsed dict or empty dict if all strategies fail
    """
    # Strategy 1: Markdown code block
    if "```json" in text:
        try:
            json_text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    if "```" in text:
        try:
            json_text = text.split("```")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    # Strategy 2: Regex to find first JSON object
    try:
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if match:
            json_text = match.group(0)
            return json.loads(json_text)
    except Exception:
        pass
    
    # Strategy 3: Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    
    return {}


# ---------- Prompt Templates ----------
def _build_prompt_pass1(lang: str = "zh") -> str:
    """Build prompt for Pass 1: open-set vision recognition."""
    if lang.startswith("zh"):
        return """你是专业的纺织品分析师。请仅基于给定的图片块，识别面料材质。

**要求：**
返回纯 JSON 格式（不要任何其他文本）：

{
  "candidates": [
    {"label": "面料名称1", "confidence": 0.0-1.0},
    {"label": "面料名称2", "confidence": 0.0-1.0},
    ...最多8个候选
  ],
  "visual_notes": "1-2句话描述视觉特征"
}

**识别指南：**
• 面料名称可以是任何真实材质（不限于常见面料）
• 可使用专业术语（如Harris粗花呢、羊绒、经编针织等）
• 按可能性从高到低排序
• 置信度总和应接近1.0
• visual_notes描述光泽、纹理、质感等"""
    else:
        return """You are a professional textile analyst. Based ONLY on the given image patch, identify the fabric material.

**Requirements:**
Return pure JSON format (no other text):

{
  "candidates": [
    {"label": "fabric_name1", "confidence": 0.0-1.0},
    {"label": "fabric_name2", "confidence": 0.0-1.0},
    ...up to 8 candidates
  ],
  "visual_notes": "1-2 sentences describing visual features"
}

**Recognition Guidelines:**
• Fabric names can be ANY real material (not limited to common fabrics)
• You can use professional terms (e.g., Harris tweed, cashmere, warp knit, etc.)
• Sort by likelihood from high to low
• Confidences should sum to approximately 1.0
• visual_notes should describe sheen, texture, feel, etc."""


def _build_prompt_pass2(candidates_str: str, visual_notes: str, evidence_str: str, lang: str = "zh") -> str:
    """Build prompt for Pass 2: RAG re-ranking with evidence."""
    if lang.startswith("zh"):
        return f"""给定初始候选和联网证据，重新排序并选择最多5个最终标签。输出纯JSON：

{{
  "labels": ["面料1", "面料2", "面料3", "面料4", "面料5"],
  "confidences": [0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0],
  "reasoning": "简短说明重排序理由（2-3句话）",
  "evidence": [{{"label":"面料1", "urls":["url1","url2"]}}, ...]
}}

**指南：**
• 优先选择定义/属性与visual_notes匹配的标签（光泽、纤维类型、编织方式）
• 可包含具体名称（如Harris粗花呢、雪纺、经编针织、羊绒等）
• 如果两个名称是同义词，保留更常见术语
• labels必须从初始候选中选择
• confidences总和应接近1.0

**初始视觉判断：**
{visual_notes}

**初始候选：**
{candidates_str}

**联网证据：**
{evidence_str}"""
    else:
        return f"""Given initial candidates and web evidence, re-rank and select up to 5 final labels. Output pure JSON:

{{
  "labels": ["fabric1", "fabric2", "fabric3", "fabric4", "fabric5"],
  "confidences": [0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0, 0.0-1.0],
  "reasoning": "Brief explanation of re-ranking rationale (2-3 sentences)",
  "evidence": [{{"label":"fabric1", "urls":["url1","url2"]}}, ...]
}}

**Guidelines:**
• Prefer labels whose definitions/properties match visual_notes (sheen, fiber type, weave)
• You may include specific names like Harris tweed, chiffon, warp knit, cashmere, etc.
• If two names are synonyms, keep the more common term
• labels must be selected from initial candidates
• confidences should sum to approximately 1.0

**Initial Visual Judgment:**
{visual_notes}

**Initial Candidates:**
{candidates_str}

**Web Evidence:**
{evidence_str}"""


# ---------- Engine Implementations ----------
def _qwen_pass1(image_path: str, lang: str = "zh") -> Dict:
    """
    Pass 1: Qwen-VL vision recognition (open-set).
    
    Returns:
        {
            "candidates": [{"label": "...", "confidence": 0.0-1.0}, ...],
            "visual_notes": "..."
        }
    """
    if MultiModalConversation is None:
        raise RuntimeError("dashscope not installed. pip install dashscope")
    
    api_key = _need_secret("DASHSCOPE_API_KEY")
    prompt = _build_prompt_pass1(lang)
    
    # Call Qwen-VL
    messages = [{
            "role": "user",
            "content": [
            {"image": f"file://{image_path}"},
                {"text": prompt}
            ]
    }]
    
    resp = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-vl-plus",
            messages=messages
        )
        
    text = (resp.output.get("text") or "").strip()
    
    # Robust JSON extraction
    data = _extract_json(text)
    
    if not data:
        # Fallback: return empty candidates
        return {"candidates": [], "visual_notes": text[:500] if text else ""}

    return {
        "candidates": data.get("candidates", []),
        "visual_notes": data.get("visual_notes", "")
    }


def _qwen_pass2(candidates_str: str, visual_notes: str, evidence_str: str, lang: str = "zh") -> Dict:
    """
    Pass 2: Qwen-VL text re-ranking with RAG evidence.
    
    Returns:
        {
            "labels": ["...", ...],
            "confidences": [0.0-1.0, ...],
            "reasoning": "...",
            "evidence": [{"label": "...", "urls": [...]}, ...]
        }
    """
    if MultiModalConversation is None:
        raise RuntimeError("dashscope not installed. pip install dashscope")
    
    api_key = _need_secret("DASHSCOPE_API_KEY")
    prompt = _build_prompt_pass2(candidates_str, visual_notes, evidence_str, lang)
    
    # Call Qwen-VL (text-only)
    messages = [{
        "role": "user",
        "content": [{"text": prompt}]
    }]
    
    resp = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-vl-plus",
        messages=messages
    )
    
    text = (resp.output.get("text") or "").strip()
    
    # Robust JSON extraction
    data = _extract_json(text)
    
    if not data:
        # Fallback: return empty result
        return {"labels": [], "confidences": [], "reasoning": "", "evidence": []}
        
        return {
        "labels": data.get("labels", []),
        "confidences": data.get("confidences", []),
        "reasoning": data.get("reasoning", ""),
        "evidence": data.get("evidence", [])
    }


def _analyze_qwen(
    image_path: str,
    lang: str = "zh",
    enable_web: bool = False,
    web_k: int = 4,
    web_lang: str = "zh"
) -> Dict:
    """
    Complete Qwen-VL analysis flow (Open-Set + RAG).
    
    Args:
        image_path: Local image path
        lang: Language code
        enable_web: Whether to enable web verification
        web_k: Number of search results per candidate
        web_lang: Search language
    
    Returns:
        {
            "materials": [...],  # Top-5
            "confidence": [...],
            "description": "...",
            "engine": "cloud_qwen",
            "evidence": [{"label": "...", "urls": [...]}, ...]
        }
    """
    # Pass 1: Generate initial candidates
    pass1_result = _qwen_pass1(image_path, lang)
    candidates = pass1_result.get("candidates", [])
    visual_notes = pass1_result.get("visual_notes", "")
    
    # If no candidates, return early
    if not candidates:
        return {
            "materials": [],
            "confidence": [],
            "description": visual_notes or "Unable to identify fabric",
            "engine": "cloud_qwen",
            "evidence": []
        }
    
    # If web search disabled, return Pass 1 results directly
    if not enable_web:
        labels = [c.get("label", "") for c in candidates[:5]]
        confs = [c.get("confidence", 0.0) for c in candidates[:5]]
        
        # Normalize confidences
        total = sum(confs) if sum(confs) > 0 else 1.0
        confs = [c / total for c in confs]
        
        return {
            "materials": labels,
            "confidence": confs,
            "description": visual_notes,
            "engine": "cloud_qwen",
            "evidence": []
        }
    
    # Pass 2: Web search + RAG re-ranking
    try:
        from src.aug.web_search import web_evidence
        
        # Search for top-N candidates (multi-engine fallback)
        top_n = min(5, len(candidates))
        evidence_map = {}  # {label: {"urls": [...], "snippets": [...]}}
        
        for cand in candidates[:top_n]:
            label = cand.get("label", "")
            if not label:
                continue
            
            # Multi-engine search: DuckDuckGo → Wikipedia → Baidu Baike
            results = web_evidence(label, lang=web_lang, k=web_k)
            
            if results:
                urls = [r.get("url", "") for r in results if r.get("url")]
                snippets = [r.get("snippet", "") for r in results]
                evidence_map[label] = {"urls": urls[:3], "snippets": snippets[:2]}
        
        # Build evidence summary string
        evidence_lines = []
        for label, ev in evidence_map.items():
            # Truncate snippets to 400 chars total
            snippets_str = " ".join(ev["snippets"][:2])[:400]
            urls_str = ", ".join(ev["urls"][:2])
            evidence_lines.append(f"• {label}: {snippets_str}\n  URLs: {urls_str}")
        evidence_str = "\n".join(evidence_lines[:5])
        
        # Build candidates string for prompt
        candidates_lines = [
            f"{i+1}. {c.get('label', '')} (confidence: {c.get('confidence', 0.0):.2f})"
            for i, c in enumerate(candidates[:8])
        ]
        candidates_str = "\n".join(candidates_lines)
        
        # Pass 2: Re-rank with evidence
        pass2_result = _qwen_pass2(candidates_str, visual_notes, evidence_str, lang)
        
        labels = pass2_result.get("labels", [])[:5]
        confs = pass2_result.get("confidences", [])[:5]
        reasoning = pass2_result.get("reasoning", visual_notes)
        evidence_list = pass2_result.get("evidence", [])
        
        # Normalize confidences
        if not confs or len(confs) != len(labels):
            # Fallback confidences
            confs = [0.50, 0.20, 0.15, 0.10, 0.05][:len(labels)]
        else:
            total = sum(confs) if sum(confs) > 0 else 1.0
            confs = [c / total for c in confs]
        
        # Build evidence list with URLs from evidence_map
        final_evidence = []
        for ev in evidence_list:
            label = ev.get("label", "")
            if label in evidence_map:
                final_evidence.append({
                    "label": label,
                    "urls": evidence_map[label]["urls"][:3]
                })
        
        return {
            "materials": labels,
            "confidence": confs,
            "description": reasoning,
            "engine": "cloud_qwen",
            "evidence": final_evidence
        }
    
    except Exception as e:
        # Web search or Pass 2 failed, fall back to Pass 1 results
        labels = [c.get("label", "") for c in candidates[:5]]
        confs = [c.get("confidence", 0.0) for c in candidates[:5]]
        
        # Normalize confidences
        total = sum(confs) if sum(confs) > 0 else 1.0
        confs = [c / total for c in confs]
        
        return {
            "materials": labels,
            "confidence": confs,
            "description": visual_notes,
            "engine": "cloud_qwen",
            "evidence": []
        }


# ---------- Public API ----------
@st.cache_data(show_spinner=False, ttl=7200)
def analyze_image(
    image_path: str,
    engine: str = "cloud_qwen",
    lang: str = "zh",
    enable_web: bool = True,
    web_k: int = 4,
    web_lang: str = "zh"
) -> Dict:
    """
    Use cloud VLM to analyze fabric image - Engine router.
    
    Args:
        image_path: Local image path
        engine: Engine name
            - "cloud_qwen": Qwen-VL (implemented)
            - "cloud_gpt4o": GPT-4o-mini (not implemented)
            - "cloud_gemini": Gemini (not implemented)
        lang: Language code "zh" | "en"
        enable_web: Enable web search verification
        web_k: Number of search results per candidate
        web_lang: Search language
    
    Returns:
        {
            "materials": ["fabric1", "fabric2", ...][:5],
            "confidence": [0.6, 0.25, 0.15, ...],
            "description": "LLM short explanation",
            "engine": "cloud_qwen",
            "evidence": [{"label": "...", "urls": [...]}, ...]
        }
    
    Raises:
        ValueError: Unsupported engine
        RuntimeError: Engine not implemented or dependencies not installed
        NoAPIKeyError: Missing API Key
    """
    # Engine router
    if engine == "cloud_qwen":
        return _analyze_qwen(image_path, lang=lang, enable_web=enable_web, web_k=web_k, web_lang=web_lang)
    elif engine == "cloud_gpt4o":
        raise RuntimeError("engine cloud_gpt4o not implemented yet")
    elif engine == "cloud_gemini":
        raise RuntimeError("engine cloud_gemini not implemented yet")
    else:
        raise ValueError(f"Unknown engine: {engine}")
