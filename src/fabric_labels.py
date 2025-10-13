# -*- coding: utf-8 -*-
"""
面料标签和别名管理
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List

_LABELS_FILE = Path("data/fabric_labels.json")
_ALIASES_FILE = Path("data/fabric_aliases.json")

_labels_cache: Dict[str, str] | None = None
_aliases_cache: Dict[str, List[str]] | None = None


def load_labels() -> Dict[str, str]:
    """加载面料中文标签"""
    global _labels_cache
    if _labels_cache is None:
        if _LABELS_FILE.exists():
            _labels_cache = json.loads(_LABELS_FILE.read_text(encoding="utf-8"))
        else:
            _labels_cache = {}
    return _labels_cache


def load_aliases() -> Dict[str, List[str]]:
    """加载面料别名"""
    global _aliases_cache
    if _aliases_cache is None:
        if _ALIASES_FILE.exists():
            _aliases_cache = json.loads(_ALIASES_FILE.read_text(encoding="utf-8"))
        else:
            _aliases_cache = {}
    return _aliases_cache


def get_label(fabric_id: str, fallback: str | None = None) -> str:
    """
    获取面料的中文标签
    
    Args:
        fabric_id: 面料ID（英文）
        fallback: 如果找不到标签时的默认值，默认返回 fabric_id
    
    Returns:
        中文标签或默认值
    """
    labels = load_labels()
    if fallback is None:
        fallback = fabric_id
    return labels.get(fabric_id, fallback)


def get_aliases(fabric_id: str) -> List[str]:
    """
    获取面料的别名列表
    
    Args:
        fabric_id: 面料ID（英文）
    
    Returns:
        别名列表，如果没有则返回空列表
    """
    aliases = load_aliases()
    return aliases.get(fabric_id, [])


def search_by_keyword(keyword: str) -> List[str]:
    """
    根据关键词搜索面料（支持中文名和别名）
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        匹配的面料ID列表
    """
    keyword = keyword.lower().strip()
    labels = load_labels()
    aliases = load_aliases()
    results = []
    
    for fabric_id, label in labels.items():
        # 匹配中文标签
        if keyword in label.lower():
            results.append(fabric_id)
            continue
        # 匹配英文ID
        if keyword in fabric_id.lower():
            results.append(fabric_id)
            continue
        # 匹配别名
        fabric_aliases = aliases.get(fabric_id, [])
        if any(keyword in alias.lower() for alias in fabric_aliases):
            results.append(fabric_id)
    
    return results
