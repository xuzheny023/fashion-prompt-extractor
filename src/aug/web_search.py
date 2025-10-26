# -*- coding: utf-8 -*-
"""
Web 搜索和内容提取模块（多引擎回退）
用于开放集面料识别的联网验证
"""

from __future__ import annotations
import re
import streamlit as st
from typing import List, Dict

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

try:
    import requests
    import lxml.html
    from readability import Document
except ImportError:
    requests = None
    lxml = None
    Document = None

# User-Agent for web requests
UA = {"User-Agent": "Mozilla/5.0"}


@st.cache_data(show_spinner=False, ttl=3600)
def ddg_text(query: str, k: int = 5, region: str = "wt-wt") -> List[Dict[str, str]]:
    """
    使用 DuckDuckGo 搜索并返回文本结果。
    
    Args:
        query: 搜索查询词
        k: 返回结果数量
        region: 搜索区域（"wt-wt" for worldwide, "cn" for China, etc.）
    
    Returns:
        [{"title": "...", "url": "...", "snippet": "..."}, ...]
    """
    if DDGS is None:
        return []
    
    out = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, region=region, safesearch="off", max_results=k):
                out.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
    except Exception:
        pass
    
    return out


@st.cache_data(show_spinner=False, ttl=3600)
def wiki_search(q: str, lang: str = "zh") -> List[Dict[str, str]]:
    """
    Wikipedia API 搜索并获取首页摘要。
    
    Args:
        q: 搜索查询词
        lang: 语言代码（"zh" for Chinese, "en" for English）
    
    Returns:
        [{"title": "...", "url": "...", "snippet": "..."}, ...]
    """
    if requests is None:
        return []
    
    try:
        # Search API
        api = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": q,
            "utf8": "1",
            "format": "json",
            "srlimit": "5"
        }
        r = requests.get(api, params=params, timeout=8, headers=UA).json()
        hits = r.get("query", {}).get("search", [])
        
        res = []
        for h in hits[:3]:
            title = h["title"]
            
            # Get page extract
            page_api = f"https://{lang}.wikipedia.org/w/api.php"
            p = requests.get(
                page_api,
                params={
                    "action": "query",
                    "prop": "extracts",
                    "explaintext": 1,
                    "titles": title,
                    "format": "json",
                    "utf8": "1"
                },
                timeout=8,
                headers=UA
            ).json()
            
            # Extract text
            pages = p.get("query", {}).get("pages", {})
            if pages:
                text = list(pages.values())[0].get("extract", "")[:2000]
                url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
                res.append({
                    "title": title,
                    "url": url,
                    "snippet": text
                })
        
        return res
    
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def baike_read(q: str) -> List[Dict[str, str]]:
    """
    百度百科回退方案：抓取 HTML 并提取可读文本。
    
    Args:
        q: 查询词
    
    Returns:
        [{"title": "...", "url": "...", "snippet": "..."}, ...]
    """
    if requests is None or Document is None or lxml is None:
        return []
    
    try:
        url = f"https://baike.baidu.com/item/{q}"
        html = requests.get(url, timeout=8, headers=UA).text
        
        # Extract readable text using readability
        text = Document(html).summary()
        text = lxml.html.fromstring(text).text_content()
        text = re.sub(r"\s+", " ", text).strip()[:2000]
        
        return [{
            "title": q,
            "url": url,
            "snippet": text
        }]
    
    except Exception:
        return []


def web_evidence(label: str, lang: str = "zh", k: int = 4) -> List[Dict[str, str]]:
    """
    多引擎回退搜索：DuckDuckGo → Wikipedia → Baidu Baike。
    
    Args:
        label: 面料名称
        lang: 语言代码（"zh" 或 "en"）
        k: 返回结果数量
    
    Returns:
        [{"title": "...", "url": "...", "snippet": "..."}, ...]
    
    Fallback strategy:
        1. Try DuckDuckGo first (fastest, worldwide)
        2. If no results, try Wikipedia API (reliable, structured)
        3. If still no results and lang=zh, try Baidu Baike (Chinese specific)
    """
    # Build search query
    if lang.startswith("zh"):
        query = f"{label} 面料 特性 纤维 织法"
    else:
        query = f"{label} fabric properties fiber weave"
    
    # Try 1: DuckDuckGo
    items = ddg_text(query, k=k, region="wt-wt")
    
    # Try 2: Wikipedia (if DDG failed)
    if not items:
        wiki_lang = "zh" if lang.startswith("zh") else "en"
        items = wiki_search(label, wiki_lang)
    
    # Try 3: Baidu Baike (if Wikipedia failed and lang is Chinese)
    if not items and lang.startswith("zh"):
        items = baike_read(label)
    
    return items[:k]


# Legacy compatibility - keep old function name
@st.cache_data(show_spinner=False, ttl=3600)
def search_snippets(query: str, k: int = 4, region: str = "cn") -> List[Dict[str, str]]:
    """
    Legacy compatibility wrapper for ddg_text.
    Maps to the new multi-strategy search with region handling.
    """
    # Map region codes
    region_map = {
        "cn": "wt-wt",  # Use worldwide for better results
        "us": "us-en",
        "us-en": "us-en",
        "wt-wt": "wt-wt"
    }
    mapped_region = region_map.get(region, "wt-wt")
    
    # Try multiple strategies
    strategies = [
        {"region": mapped_region, "safesearch": "off"},
        {"region": "wt-wt", "safesearch": "off"},
        {"region": "us-en", "safesearch": "off"},
    ]
    
    for strategy in strategies:
        results = ddg_text(query, k=k * 2, region=strategy["region"])
        if results:
            # Normalize keys: url → href for backward compatibility
            normalized = []
            for r in results[:k]:
                normalized.append({
                    "title": r.get("title", ""),
                    "href": r.get("url", ""),  # Map url → href
                    "snippet": r.get("snippet", "")
                })
            return normalized
    
    return []


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_readable(url: str, timeout: int = 8) -> str:
    """
    获取 URL 的可读文本内容。
    
    Args:
        url: 目标 URL
        timeout: 请求超时时间（秒）
    
    Returns:
        提取的文本内容（最多 3000 字符）
    """
    if requests is None or lxml is None or Document is None:
        return ""
    
    try:
        # 获取 HTML 内容
        resp = requests.get(url, timeout=timeout, headers=UA)
        resp.raise_for_status()
        
        # 使用 readability 提取主要内容
        doc = Document(resp.text)
        html_text = doc.summary(html_partial=True)
        
        # 转换为纯文本
        text = lxml.html.fromstring(html_text).text_content()
        
        # 清理空白字符
        text = re.sub(r"\s+", " ", text).strip()
        
        # 限制长度
        return text[:3000]
    
    except Exception:
        return ""
