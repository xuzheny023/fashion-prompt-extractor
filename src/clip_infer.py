# -*- coding: utf-8 -*-
"""
CLIP-based fabric retrieval inference module.
基于 CLIP 的面料检索推理模块
"""
from __future__ import annotations
import os
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image

_model = None
_processor = None

def _load_model():
    global _model, _processor
    if _model is not None:
        return _model, _processor

    # 彻底禁用 CUDA，排除驱动卡住
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # 禁用 tensorflow 警告
    device = "cpu"

    # 使用 transformers 库加载您已下载的 HuggingFace 格式模型
    from transformers import CLIPModel, CLIPProcessor
    import traceback
    
    print("[CLIP] Loading from local cache...", flush=True)
    local_model_path = str(Path.home() / ".cache" / "open_clip" / "ViT-B-32" / "openai")
    
    try:
        # 尝试从本地加载
        print(f"[CLIP] Model path: {local_model_path}", flush=True)
        _processor = CLIPProcessor.from_pretrained(local_model_path, local_files_only=True)
        _model = CLIPModel.from_pretrained(local_model_path, local_files_only=True)
        print(f"[CLIP] ✓ Loaded successfully from local cache!", flush=True)
    except Exception as e:
        print(f"[CLIP] ✗ Local load failed: {str(e)[:200]}", flush=True)
        print(f"[CLIP] Downloading from HuggingFace (using mirror)...", flush=True)
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        print("[CLIP] ✓ Downloaded and loaded", flush=True)
    
    _model.to(device).eval()
    return _model, _processor

def image_to_emb(img: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to CLIP embedding vector.
    将 PIL 图像转换为 CLIP 嵌入向量
    """
    model, processor = _load_model()
    with torch.no_grad():
        inputs = processor(images=img, return_tensors="pt")
        e = model.get_image_features(**inputs)
        e = e / e.norm(dim=-1, keepdim=True)
    return e.squeeze(0).cpu().numpy()

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

