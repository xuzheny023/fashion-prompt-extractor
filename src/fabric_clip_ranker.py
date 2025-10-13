# -*- coding: utf-8 -*-
"""
基于 CLIP 的面料推荐器（优化版）

使用双通道 CLIP 向量相似度进行面料检索，替代传统的规则基推荐
优化策略：
- 预归一化向量库 → 余弦相似度 = 点积
- 矩阵批量计算 → 避免循环
- 智能粗排+精排 → 速度与准确率平衡
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
from PIL import Image
from functools import lru_cache

# CLIP 编码器
from src.dual_clip import image_to_emb
# 中文标签
from src.fabric_labels import get_label

# 导出的公共 API
__all__ = [
    'load_centroids',
    'load_bank',
    'retrieve_topk',
    'recommend_fabrics_clip',
    'recommend_from_region_image',
]

# 向量库路径
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = PROJECT_ROOT / "data" / "fabric_bank.npz"
CENTROIDS_PATH = PROJECT_ROOT / "data" / "fabric_centroids.npz"

# 参数配置
MIN_SAMPLES = 3     # 最少样本数
TOPC = 12          # 粗排取前多少个类做精排

# FAISS 可选加速
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


@lru_cache(maxsize=1)
def load_centroids() -> Tuple[List[str], np.ndarray]:
    """
    加载并归一化类中心向量
    
    Returns:
        labels: 类别名称列表 [Nc]
        C: 类中心矩阵 [Nc, D]，已归一化
    """
    if not CENTROIDS_PATH.exists():
        return [], np.array([])
    
    cz = np.load(CENTROIDS_PATH, allow_pickle=True)
    labels, mats = [], []
    
    for k in cz.files:
        v = cz[k].astype("float32")
        # L2 归一化
        norm = np.linalg.norm(v, axis=1, keepdims=True)
        v = v / (norm + 1e-12)
        labels.append(k)
        mats.append(v[0])  # 取第一行（centroids 只有一行）
    
    if not mats:
        return [], np.array([])
    
    C = np.stack(mats).astype("float32")  # [Nc, D]
    return labels, C


@lru_cache(maxsize=1)
def load_bank() -> Dict[str, np.ndarray]:
    """
    加载并归一化完整向量库
    
    Returns:
        per_class: {类别名: 归一化样本矩阵 [Ni, D]}
    """
    if not BANK_PATH.exists():
        raise FileNotFoundError(
            f"向量库不存在: {BANK_PATH}\n"
            "请先运行: python tools/build_fabric_bank.py"
        )
    
    bank = np.load(BANK_PATH, allow_pickle=True)
    per_class = {}
    
    for k in bank.files:
        X = bank[k].astype("float32")
        
        # 过滤：维度检查 + 最少样本数
        if X.ndim != 2 or X.shape[0] < MIN_SAMPLES:
            continue
        
        # L2 归一化
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        X = X / (norms + 1e-12)
        
        per_class[k] = X  # [Ni, D]，已归一化
    
    return per_class


def retrieve_topk(
    q_emb: np.ndarray,
    topk: int = 5,
    topc: int = TOPC,
    use_faiss: bool = HAS_FAISS
) -> Tuple[List[Tuple[str, float]], float]:
    """
    核心检索函数：先粗排，再类内精排（全部矩阵点积）
    
    Args:
        q_emb: [D] 查询向量（建议预归一化）
        topk: 返回 Top-K 结果
        topc: 粗排后取前多少个类做精排
        use_faiss: 是否使用 FAISS 加速（如果可用）
    
    Returns:
        best: [(类别ID, 分数), ...] Top-K 结果
        max_coarse_score: 粗排最高分（可作置信度参考）
    """
    # 确保查询向量归一化
    q = q_emb.astype("float32")
    q = q / (np.linalg.norm(q) + 1e-12)
    
    # 1) 类中心粗排
    cent_labels, C = load_centroids()
    
    if len(cent_labels) == 0:
        # 无 centroids，回退到全样本
        return _retrieve_all_samples(q, topk, use_faiss)
    
    if use_faiss and HAS_FAISS:
        # FAISS 内积检索
        index = faiss.IndexFlatIP(C.shape[1])
        index.add(C)
        scores_c, idx = index.search(q.reshape(1, -1), topc)
        scores_c = scores_c[0]  # [topc]
        idx = idx[0]  # [topc]
    else:
        # NumPy 矩阵点积
        scores_c = C @ q  # [Nc]
        scores_c = np.clip(scores_c, -1.0, 1.0)
        idx = np.argsort(-scores_c)[:topc]  # Top-C 索引
        scores_c = scores_c[idx]
    
    sel_classes = [cent_labels[i] for i in idx]  # 进入精排的类
    max_coarse_score = float(np.max(scores_c))
    
    # 2) 类内精排（只对入围类做）
    bank = load_bank()
    best = []
    
    for cls in sel_classes:
        X = bank.get(cls)
        if X is None:
            continue
        
        if use_faiss and HAS_FAISS:
            # FAISS 内积检索
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X)
            s, _ = index.search(q.reshape(1, -1), 1)
            max_sim = float(s[0, 0])
        else:
            # NumPy 矩阵点积
            s = X @ q  # [Ni]
            s = np.clip(s, -1.0, 1.0)
            max_sim = float(np.max(s))
        
        best.append((cls, max_sim))
    
    best.sort(key=lambda x: -x[1])
    return best[:topk], max_coarse_score


def _retrieve_all_samples(
    q: np.ndarray,
    topk: int,
    use_faiss: bool = False
) -> Tuple[List[Tuple[str, float]], float]:
    """全样本检索（无 centroids 时的后备方案）"""
    bank = load_bank()
    all_scores = []
    
    for cls, X in bank.items():
        if use_faiss and HAS_FAISS:
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X)
            s, _ = index.search(q.reshape(1, -1), 1)
            max_sim = float(s[0, 0])
        else:
            s = X @ q  # [Ni]
            s = np.clip(s, -1.0, 1.0)
            max_sim = float(np.max(s))
        all_scores.append((cls, max_sim))
    
    all_scores.sort(key=lambda x: -x[1])
    max_score = all_scores[0][1] if all_scores else 0.0
    return all_scores[:topk], max_score


def recommend_fabrics_clip(
    image: Image.Image,
    top_k: int = 5,
    topc: int = TOPC,
    lang: str = "zh"
) -> List[Tuple[str, float, str]]:
    """
    基于 CLIP 向量相似度推荐面料（优化版）
    
    策略：
    1. 类中心粗排（矩阵点积，快）
    2. Top-C 精排（只对前 C 个类做全样本比对）
    
    Args:
        image: PIL Image 对象
        top_k: 返回 Top-K 结果
        topc: 粗排后取前多少个类做精排
        lang: 语言代码（'zh' 或 'en'）
    
    Returns:
        [(类别ID, 分数, 显示名称), ...]
    """
    
    # 1. 编码查询图片（dual_clip 已归一化）
    query_emb = image_to_emb(image)
    
    # 2. 核心检索
    results, max_coarse = retrieve_topk(query_emb, topk=top_k, topc=topc)
    
    # 3. 添加显示名称
    final_results = []
    for cls, score in results:
        display_name = get_label(cls) if lang == "zh" else cls
        final_results.append((cls, score, display_name))
    
    return final_results


def recommend_from_region_image(
    full_image: np.ndarray,
    region_bbox: Tuple[int, int, int, int],
    top_k: int = 5,
    lang: str = "zh"
) -> List[Tuple[str, float, str]]:
    """
    从完整图片中裁剪区域并推荐面料
    
    Args:
        full_image: 完整图片 (numpy array, RGB)
        region_bbox: 区域边界框 (x1, y1, x2, y2)
        top_k: 返回 Top-K 结果
        lang: 语言代码
    
    Returns:
        [(类别ID, 分数, 显示名称), ...]
    """
    x1, y1, x2, y2 = region_bbox
    
    # 裁剪区域
    region_crop = full_image[y1:y2, x1:x2]
    
    # 转换为 PIL Image
    region_pil = Image.fromarray(region_crop).convert("RGB")
    
    # 推荐
    return recommend_fabrics_clip(region_pil, top_k=top_k, lang=lang)
