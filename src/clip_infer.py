# -*- coding: utf-8 -*-
"""
CLIP-based fabric retrieval inference module.
基于 CLIP 的面料检索推理模块
"""
from __future__ import annotations
import os, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from PIL import Image

# lazy import to speed cold start
_model = None
_preprocess = None
_device = "cuda" if torch.cuda.is_available() else "cpu"

def _load_model():
    global _model, _preprocess
    if _model is not None:
        return _model, _preprocess
    # open-clip lazy import
    from open_clip import create_model_and_transforms
    _model, _, _preprocess = create_model_and_transforms("ViT-B-32", pretrained="openai")
    _model.to(_device).eval()
    return _model, _preprocess

def image_to_emb(img: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to CLIP embedding vector.
    将 PIL 图像转换为 CLIP 嵌入向量
    """
    model, preprocess = _load_model()
    with torch.no_grad():
        t = preprocess(img).unsqueeze(0).to(_device)
        e = model.encode_image(t)
        e = e / e.norm(dim=-1, keepdim=True)
    return e.squeeze(0).detach().cpu().numpy()

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    计算两个向量的余弦相似度
    """
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    return float(np.dot(a, b))

def load_fabric_bank(path: str | Path = "data/fabric_bank.npz") -> Dict[str, np.ndarray]:
    """
    Load pre-built fabric reference bank.
    加载预构建的面料参考库
    
    Returns:
        Dict mapping fabric_id -> array of embeddings (N, D)
    """
    p = Path(path)
    if not p.exists():
        return {}
    npz = np.load(p, allow_pickle=True)
    bank = {}
    for k in npz.files:
        bank[k] = npz[k]
    return bank  # {fabric_id: (N, D)}

def rank_by_retrieval(
    patch_img: Image.Image, 
    topk: int = 5, 
    bank_path: str | Path = "data/fabric_bank.npz"
) -> List[Dict[str, any]]:
    """
    Rank fabrics by CLIP retrieval similarity.
    基于 CLIP 检索相似度对面料排序
    
    Args:
        patch_img: PIL Image of the fabric patch
        topk: Number of top results to return
        bank_path: Path to fabric bank NPZ file
        
    Returns:
        List of dicts: [{id, score}] sorted desc by score
    """
    bank = load_fabric_bank(bank_path)
    if not bank:
        return []
    q = image_to_emb(patch_img)
    results = []
    for fid, embs in bank.items():
        # aggregate score by max similarity to any reference embedding
        sims = [cosine_sim(q, e) for e in embs]
        score = float(np.max(sims))
        results.append({"id": fid, "score": round(score, 4)})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:topk]

