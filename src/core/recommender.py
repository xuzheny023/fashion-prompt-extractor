# -*- coding: utf-8 -*-
"""
统一推荐引擎

职责：串联整个推荐流程
1. 图片编码 (CLIP)
2. 向量检索 (fabric_clip_ranker)
3. AI 复核 (ai_boost)
4. 返回标准结果 (types)

用法：
    from src.core.recommender import recommend
    
    result, meta = recommend(pil_image)
    print(f"Top 1: {result.top1.label} ({result.top1.score:.2f})")
    print(f"耗时: {meta.ms}ms")
"""
from __future__ import annotations
import time
import numpy as np
from PIL import Image

from src.config import cfg
from src.types import ScoreItem, RankedResult, QueryMeta
from src.utils.logger import get_logger

# CLIP 编码器
from src.dual_clip import get_encoder

# 向量检索
from src.fabric_clip_ranker import retrieve_topk, load_centroids, load_bank

# AI 复核
from src.ai_boost import LMMReranker

# 中文标签
from src.fabric_labels import get_label

log = get_logger("recommender")


class FabricRecommendEngine:
    """
    面料推荐引擎
    
    整合了 CLIP 编码 + 向量检索 + AI 复核的完整流程
    """
    
    def __init__(self):
        """初始化引擎"""
        log.info("初始化面料推荐引擎...")
        
        # 1. 预加载 CLIP 编码器
        try:
            self.encoder = get_encoder()
            log.info("✓ CLIP 编码器已加载")
        except Exception as e:
            log.error(f"✗ CLIP 编码器加载失败: {e}")
            raise
        
        # 2. 预加载向量库
        try:
            self.centroids_labels, self.centroids_matrix = load_centroids()
            self.bank = load_bank()
            log.info(f"✓ 向量库已加载: {len(self.bank)} 类, {len(self.centroids_labels)} 中心点")
        except Exception as e:
            log.error(f"✗ 向量库加载失败: {e}")
            raise
        
        # 3. 初始化 AI 复核器（可选）
        try:
            self.reranker = LMMReranker()
            if self.reranker.enabled:
                log.info(f"✓ AI 复核已启用: {cfg.AI_BACKEND}")
            else:
                log.info("○ AI 复核已禁用")
        except Exception as e:
            log.warning(f"⚠ AI 复核初始化失败: {e}")
            self.reranker = None
        
        log.info("✅ 推荐引擎初始化完成")
    
    def recommend(
        self,
        image: Image.Image,
        top_k: int | None = None,
        topc: int | None = None,
        lang: str = "zh"
    ) -> tuple[RankedResult, QueryMeta]:
        """
        推荐面料
        
        Args:
            image: PIL 图片对象
            top_k: 返回前 K 个结果（默认从 cfg 读取）
            topc: 粗排取前 C 个类（默认从 cfg 读取）
            lang: 语言（"zh" 或 "en"）
        
        Returns:
            (RankedResult, QueryMeta) - 排名结果和性能指标
        """
        t0 = time.perf_counter()
        
        top_k = top_k or cfg.TOPK
        topc = topc or cfg.TOPC
        
        # ==================== 阶段1: 编码 ====================
        log.debug("阶段1: CLIP 编码...")
        try:
            query_emb = self._encode_image(image)
            log.debug(f"✓ 编码完成: {query_emb.shape}")
        except Exception as e:
            log.exception("编码失败")
            raise
        
        # ==================== 阶段2: 检索 ====================
        log.debug(f"阶段2: 向量检索 (top_k={top_k}, topc={topc})...")
        try:
            retrieval_results, coarse_max = retrieve_topk(
                query_emb,
                topk=top_k,
                topc=topc,
                use_faiss=cfg.ENABLE_FAISS
            )
            log.debug(f"✓ 检索完成: {len(retrieval_results)} 个候选, 粗排最高分={coarse_max:.3f}")
        except Exception as e:
            log.exception("检索失败")
            raise
        
        # ==================== 阶段3: AI 复核（可选）====================
        ai_reason = ""
        if self.reranker and self.reranker.enabled:
            log.debug("阶段3: AI 复核判断...")
            
            # 提取前几名的分数（retrieval_results 现在是 List[ScoreItem]）
            top_scores = [item.score for item in retrieval_results[:min(3, len(retrieval_results))]]
            
            if self.reranker.should_rerank(top_scores):
                log.info("→ 触发 AI 复核")
                try:
                    # 转换为 AI 复核需要的格式 [(label, score), ...]
                    candidates = [(item.label, item.score) for item in retrieval_results]
                    reranked = self.reranker.rerank(image, candidates)
                    # 转换回 ScoreItem
                    retrieval_results = [ScoreItem(label=lbl, score=scr) for lbl, scr in reranked]
                    ai_reason = f"AI 复核 ({cfg.AI_BACKEND})"
                    log.info("✓ AI 复核完成")
                except Exception as e:
                    log.warning(f"⚠ AI 复核失败: {e}")
                    ai_reason = ""
            else:
                log.debug("○ 无需 AI 复核")
        else:
            log.debug("○ 跳过 AI 复核（已禁用）")
        
        # ==================== 阶段4: 构建结果 ====================
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        
        # 应用中文标签（如果需要）
        items = []
        for item in retrieval_results:
            display_label = get_label(item.label) if lang == "zh" else item.label
            items.append(ScoreItem(label=display_label, score=item.score))
        
        result = RankedResult(
            items=items,
            ai_reason=ai_reason or "CLIP 双通道向量检索"
        )
        
        meta = QueryMeta(
            ms=elapsed_ms,
            coarse_max=coarse_max
        )
        
        log.info(f"✅ 推荐完成: Top 1={result.top1.label} ({result.top1.score:.2f}), 耗时={meta.ms}ms")
        
        return result, meta
    
    def _encode_image(self, image: Image.Image) -> np.ndarray:
        """
        将图片编码为 1536 维向量并 L2 归一化
        
        Args:
            image: PIL 图片
        
        Returns:
            归一化的 1536 维向量 (float32)
        """
        # 使用 dual_clip 编码（内部已经做了 L2 归一化）
        emb = self.encoder.image_to_emb(image)
        
        # 确保归一化（双保险）
        emb = emb.astype("float32")
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        
        return emb


# ==================== 全局单例 ====================
_engine: FabricRecommendEngine | None = None


def get_engine() -> FabricRecommendEngine:
    """获取引擎单例"""
    global _engine
    if _engine is None:
        _engine = FabricRecommendEngine()
    return _engine


def recommend(
    image: Image.Image,
    top_k: int | None = None,
    topc: int | None = None,
    lang: str = "zh"
) -> tuple[RankedResult, QueryMeta]:
    """
    推荐面料（便捷函数）
    
    Args:
        image: PIL 图片对象
        top_k: 返回前 K 个结果（默认 5）
        topc: 粗排取前 C 个类（默认 12）
        lang: 语言（"zh" 或 "en"）
    
    Returns:
        (RankedResult, QueryMeta) - 排名结果和性能指标
    
    Example:
        >>> from PIL import Image
        >>> from src.core.recommender import recommend
        >>> 
        >>> img = Image.open("fabric.jpg")
        >>> result, meta = recommend(img)
        >>> 
        >>> print(f"Top 1: {result.top1.label} ({result.top1.score:.2%})")
        >>> print(f"耗时: {meta.ms}ms")
    """
    engine = get_engine()
    return engine.recommend(image, top_k=top_k, topc=topc, lang=lang)


__all__ = [
    'FabricRecommendEngine',
    'get_engine',
    'recommend',
]

