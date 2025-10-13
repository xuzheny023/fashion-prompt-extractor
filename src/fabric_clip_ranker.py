# -*- coding: utf-8 -*-
"""
基于 CLIP 的面料推荐器（优化版）

使用双通道 CLIP 向量相似度进行面料检索，替代传统的规则基推荐
优化策略：
- 预归一化向量库 → 余弦相似度 = 点积
- 矩阵批量计算 → 避免循环
- 智能粗排+精排 → 速度与准确率平衡
- 统一配置与类型 → 易于维护和扩展
"""
from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np
from PIL import Image
from functools import lru_cache

# 统一配置
from src.config import cfg
# 标准类型
from src.types import ScoreItem
# 日志系统
from src.utils.logger import get_logger
# CLIP 编码器
from src.dual_clip import image_to_emb
# 中文标签
from src.fabric_labels import get_label

log = get_logger("fabric_ranker")

# 导出的公共 API
__all__ = [
    'load_centroids',
    'load_bank',
    'retrieve_topk',
    'recommend_fabrics_clip',
    'recommend_from_region_image',
]

# FAISS 可选加速
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    log.debug("FAISS 不可用，将使用 NumPy 矩阵运算")


@lru_cache(maxsize=1)
def load_centroids() -> Tuple[List[str], np.ndarray]:
    """
    加载并归一化类中心向量（带缓存）
    
    Returns:
        labels: 类别名称列表 [Nc]
        C: 类中心矩阵 [Nc, D]，已 L2 归一化
    """
    log.debug(f"加载类中心向量: {cfg.FABRIC_CENTROIDS}")
    
    if not cfg.FABRIC_CENTROIDS.exists():
        log.warning(f"类中心向量不存在: {cfg.FABRIC_CENTROIDS}")
        return [], np.array([])
    
    cz = np.load(cfg.FABRIC_CENTROIDS, allow_pickle=True)
    labels, mats = [], []
    
    for k in cz.files:
        v = cz[k].astype("float32")
        # L2 归一化
        norm = np.linalg.norm(v, axis=1, keepdims=True)
        v = v / (norm + 1e-12)
        labels.append(k)
        mats.append(v[0])  # 取第一行（centroids 只有一行）
    
    if not mats:
        log.warning("类中心向量为空")
        return [], np.array([])
    
    C = np.stack(mats).astype("float32")  # [Nc, D]
    log.info(f"✓ 类中心向量已加载: {len(labels)} 类, 维度 {C.shape[1]}")
    return labels, C


@lru_cache(maxsize=1)
def load_bank() -> Dict[str, np.ndarray]:
    """
    加载并归一化完整向量库（带缓存）
    
    Returns:
        per_class: {类别名: 归一化样本矩阵 [Ni, D]}
    """
    log.debug(f"加载向量库: {cfg.FABRIC_BANK}")
    
    if not cfg.FABRIC_BANK.exists():
        log.error(f"向量库不存在: {cfg.FABRIC_BANK}")
        raise FileNotFoundError(
            f"向量库不存在: {cfg.FABRIC_BANK}\n"
            "请先运行: python tools/build_fabric_bank.py"
        )
    
    bank = np.load(cfg.FABRIC_BANK, allow_pickle=True)
    per_class = {}
    total_samples = 0
    
    for k in bank.files:
        X = bank[k].astype("float32")
        
        # 过滤：维度检查 + 最少样本数
        if X.ndim != 2 or X.shape[0] < cfg.MIN_SAMPLES:
            log.debug(f"跳过类别 {k}: 样本数 {X.shape[0]} < {cfg.MIN_SAMPLES}")
            continue
        
        # L2 归一化（矩阵化操作）
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        X = X / (norms + 1e-12)
        
        per_class[k] = X  # [Ni, D]，已归一化
        total_samples += X.shape[0]
    
    log.info(f"✓ 向量库已加载: {len(per_class)} 类, 共 {total_samples} 个样本")
    return per_class


def retrieve_topk(
    q_emb: np.ndarray,
    topk: int | None = None,
    topc: int | None = None,
    use_faiss: bool | None = None
) -> Tuple[List[ScoreItem], float]:
    """
    核心检索函数：先粗排，再类内精排（全矩阵化操作）
    
    Args:
        q_emb: [D] 查询向量（会自动 L2 归一化）
        topk: 返回 Top-K 结果（默认从 cfg.TOPK 读取）
        topc: 粗排后取前 C 个类做精排（默认从 cfg.TOPC 读取）
        use_faiss: 是否使用 FAISS 加速（默认从 cfg.ENABLE_FAISS 读取）
    
    Returns:
        results: [ScoreItem, ...] Top-K 结果（标准类型）
        max_coarse_score: 粗排最高分（可作置信度参考）
    """
    # 读取配置
    topk = topk or cfg.TOPK
    topc = topc or cfg.TOPC
    use_faiss = cfg.ENABLE_FAISS if use_faiss is None else use_faiss
    
    log.debug(f"开始检索: topk={topk}, topc={topc}, use_faiss={use_faiss}")
    
    # 确保查询向量 L2 归一化
    q = q_emb.astype("float32")
    norm = np.linalg.norm(q)
    if norm > 0:
        q = q / norm
    log.debug(f"查询向量归一化完成: shape={q.shape}, norm={norm:.6f}")
    
    # 1) 类中心粗排（矩阵点积）
    cent_labels, C = load_centroids()
    
    if len(cent_labels) == 0:
        log.warning("无类中心向量，回退到全样本检索")
        return _retrieve_all_samples(q, topk, use_faiss)
    
    log.debug(f"粗排: {len(cent_labels)} 个类中心")
    
    if use_faiss and HAS_FAISS:
        # FAISS 内积检索（快）
        log.debug("使用 FAISS 加速粗排")
        index = faiss.IndexFlatIP(C.shape[1])
        index.add(C)
        scores_c, idx = index.search(q.reshape(1, -1), min(topc, len(cent_labels)))
        scores_c = scores_c[0]  # [topc]
        idx = idx[0]  # [topc]
    else:
        # NumPy 矩阵点积
        log.debug("使用 NumPy 矩阵运算粗排")
        scores_c = C @ q  # [Nc] - 全矩阵化，无循环
        scores_c = np.clip(scores_c, -1.0, 1.0)
        idx = np.argsort(-scores_c)[:topc]  # Top-C 索引
        scores_c = scores_c[idx]
    
    sel_classes = [cent_labels[i] for i in idx]  # 进入精排的类
    max_coarse_score = float(np.max(scores_c))
    log.debug(f"粗排完成: 选出 {len(sel_classes)} 个候选类, 最高分={max_coarse_score:.3f}")
    
    # 2) 类内精排（只对入围类做，矩阵点积）
    bank = load_bank()
    best = []
    
    log.debug(f"精排: 对 {len(sel_classes)} 个类进行类内检索")
    for cls in sel_classes:
        X = bank.get(cls)
        if X is None:
            log.debug(f"跳过类别 {cls}: 向量库中不存在")
            continue
        
        if use_faiss and HAS_FAISS:
            # FAISS 内积检索
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X)
            s, _ = index.search(q.reshape(1, -1), 1)
            max_sim = float(s[0, 0])
        else:
            # NumPy 矩阵点积（矩阵化，无循环）
            s = X @ q  # [Ni] - 一次性计算所有样本相似度
            s = np.clip(s, -1.0, 1.0)
            max_sim = float(np.max(s))
        
        best.append((cls, max_sim))
        log.debug(f"  {cls}: {X.shape[0]} 个样本, 最高分={max_sim:.3f}")
    
    # 3) 排序并转换为标准类型
    best.sort(key=lambda x: -x[1])
    results = [ScoreItem(label=cls, score=score) for cls, score in best[:topk]]
    
    log.debug(f"精排完成: 返回 {len(results)} 个结果")
    if results:
        log.info(f"检索完成: Top 1={results[0].label} ({results[0].score:.3f})")
    
    return results, max_coarse_score


def _retrieve_all_samples(
    q: np.ndarray,
    topk: int,
    use_faiss: bool = False
) -> Tuple[List[ScoreItem], float]:
    """
    全样本检索（无 centroids 时的后备方案）
    
    矩阵化操作，无循环相似度计算
    """
    log.debug("执行全样本检索（后备方案）")
    bank = load_bank()
    all_scores = []
    
    for cls, X in bank.items():
        if use_faiss and HAS_FAISS:
            # FAISS 内积检索
            index = faiss.IndexFlatIP(X.shape[1])
            index.add(X)
            s, _ = index.search(q.reshape(1, -1), 1)
            max_sim = float(s[0, 0])
        else:
            # NumPy 矩阵点积（矩阵化，无循环）
            s = X @ q  # [Ni] - 一次性计算所有样本
            s = np.clip(s, -1.0, 1.0)
            max_sim = float(np.max(s))
        all_scores.append((cls, max_sim))
    
    all_scores.sort(key=lambda x: -x[1])
    max_score = all_scores[0][1] if all_scores else 0.0
    
    # 转换为标准类型
    results = [ScoreItem(label=cls, score=score) for cls, score in all_scores[:topk]]
    log.debug(f"全样本检索完成: {len(results)} 个结果")
    
    return results, max_score


def recommend_fabrics_clip(
    image: Image.Image,
    top_k: int | None = None,
    topc: int | None = None,
    lang: str = "zh"
) -> List[Tuple[str, float, str]]:
    """
    基于 CLIP 向量相似度推荐面料（优化版）
    
    策略：
    1. 类中心粗排（矩阵点积，快）
    2. Top-C 精排（只对前 C 个类做全样本比对）
    
    Args:
        image: PIL Image 对象
        top_k: 返回 Top-K 结果（默认从 cfg.TOPK 读取）
        topc: 粗排后取前 C 个类做精排（默认从 cfg.TOPC 读取）
        lang: 语言代码（'zh' 或 'en'）
    
    Returns:
        [(类别ID, 分数, 显示名称), ...] - 兼容旧接口
    
    Note:
        推荐使用 retrieve_topk() 获取标准 ScoreItem 类型
    """
    log.debug(f"推荐面料: top_k={top_k}, topc={topc}, lang={lang}")
    
    # 1. 编码查询图片（dual_clip 已归一化）
    query_emb = image_to_emb(image)
    
    # 2. 核心检索（返回 ScoreItem 列表）
    score_items, max_coarse = retrieve_topk(query_emb, topk=top_k, topc=topc)
    
    # 3. 转换为旧格式（兼容性）
    final_results = []
    for item in score_items:
        display_name = get_label(item.label) if lang == "zh" else item.label
        final_results.append((item.label, item.score, display_name))
    
    log.debug(f"推荐完成: {len(final_results)} 个结果")
    return final_results


def recommend_from_region_image(
    full_image: np.ndarray,
    region_bbox: Tuple[int, int, int, int],
    top_k: int | None = None,
    lang: str = "zh"
) -> List[Tuple[str, float, str]]:
    """
    从完整图片中裁剪区域并推荐面料
    
    Args:
        full_image: 完整图片 (numpy array, RGB)
        region_bbox: 区域边界框 (x1, y1, x2, y2)
        top_k: 返回 Top-K 结果（默认从 cfg.TOPK 读取）
        lang: 语言代码
    
    Returns:
        [(类别ID, 分数, 显示名称), ...]
    """
    x1, y1, x2, y2 = region_bbox
    log.debug(f"区域推荐: bbox=({x1},{y1},{x2},{y2}), size={x2-x1}x{y2-y1}")
    
    # 裁剪区域
    region_crop = full_image[y1:y2, x1:x2]
    log.debug(f"裁剪完成: shape={region_crop.shape}")
    
    # 转换为 PIL Image
    region_pil = Image.fromarray(region_crop).convert("RGB")
    
    # 推荐
    return recommend_fabrics_clip(region_pil, top_k=top_k, lang=lang)
