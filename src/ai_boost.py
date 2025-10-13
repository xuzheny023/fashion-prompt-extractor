# -*- coding: utf-8 -*-
"""
AI 复核模块

使用多模态大模型对低置信度或边界模糊的面料识别结果进行复核。

支持的后端：
- OpenAI (gpt-4o-mini / gpt-4-vision-preview)
- Ollama (llava / llava:13b)
- None (跳过复核)

用法：
    from src.ai_boost import LMMReranker
    
    reranker = LMMReranker()
    if reranker.should_rerank(top_scores=[0.45, 0.42]):
        refined = reranker.rerank(image, candidates)
"""
from __future__ import annotations
from typing import List, Tuple
from PIL import Image
import io
import base64

from src.config import cfg
from src.utils.logger import get_logger

log = get_logger("ai_boost")


class LMMReranker:
    """
    多模态大模型复核器
    
    职责：
    1. 判断是否需要复核（低置信度或分数接近）
    2. 调用多模态大模型进行视觉分析
    3. 返回调整后的排名
    """
    
    def __init__(self):
        self.backend = cfg.AI_BACKEND
        self.enabled = self.backend != "none"
        
        if self.enabled:
            log.info(f"AI 复核已启用，后端: {self.backend}")
        else:
            log.debug("AI 复核已禁用")
    
    def should_rerank(
        self,
        top_scores: List[float],
        low_conf_threshold: float | None = None,
        close_gap_threshold: float | None = None
    ) -> bool:
        """
        判断是否需要 AI 复核
        
        触发条件：
        1. 最高分 < LOW_CONF（低置信度）
        2. 前两名分数差 < CLOSE_GAP（边界模糊）
        
        Args:
            top_scores: 前几名的分数列表
            low_conf_threshold: 低置信度阈值（默认从 cfg 读取）
            close_gap_threshold: 分数差阈值（默认从 cfg 读取）
        
        Returns:
            True 如果需要复核
        """
        if not self.enabled:
            return False
        
        if not top_scores:
            return False
        
        low_conf = low_conf_threshold or cfg.LOW_CONF
        close_gap = close_gap_threshold or cfg.CLOSE_GAP
        
        # 条件1: 最高分过低
        if top_scores[0] < low_conf:
            log.info(f"触发 AI 复核：最高分 {top_scores[0]:.2f} < {low_conf}")
            return True
        
        # 条件2: 前两名接近
        if len(top_scores) >= 2:
            gap = top_scores[0] - top_scores[1]
            if gap < close_gap:
                log.info(f"触发 AI 复核：前两名差距 {gap:.2f} < {close_gap}")
                return True
        
        return False
    
    def rerank(
        self,
        image: Image.Image,
        candidates: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """
        使用 AI 复核并调整排名
        
        Args:
            image: 待识别的面料图片
            candidates: 候选列表 [(label, score), ...]
        
        Returns:
            调整后的候选列表
        """
        if not self.enabled:
            log.warning("AI 复核未启用，返回原始排名")
            return candidates
        
        try:
            if self.backend == "openai":
                return self._rerank_openai(image, candidates)
            elif self.backend == "ollama":
                return self._rerank_ollama(image, candidates)
            else:
                log.error(f"不支持的后端: {self.backend}")
                return candidates
        except Exception as e:
            log.exception(f"AI 复核失败: {e}")
            return candidates
    
    def _rerank_openai(
        self,
        image: Image.Image,
        candidates: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """使用 OpenAI 进行复核"""
        try:
            import openai
        except ImportError:
            log.error("未安装 openai 库，请运行: pip install openai")
            return candidates
        
        # 将图片转为 base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 构建候选列表文本
        candidates_text = "\n".join([
            f"{i+1}. {label} (初始置信度: {score:.2f})"
            for i, (label, score) in enumerate(candidates)
        ])
        
        # 构建提示词
        prompt = f"""你是一位专业的纺织品专家。请仔细观察这张面料图片，并根据纹理、光泽、质感等特征，对以下候选面料进行排序。

候选面料（按初始置信度排序）：
{candidates_text}

请直接返回你认为最可能的面料名称（只返回英文 label，不要解释）。
如果初始排名合理，返回第一个候选项即可。
"""
        
        try:
            client = openai.OpenAI(api_key=cfg.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=cfg.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50,
                temperature=0.3,
            )
            
            ai_choice = response.choices[0].message.content.strip().lower()
            log.info(f"AI 选择: {ai_choice}")
            
            # 如果 AI 选择了不同的候选项，将其提升到第一位
            for i, (label, score) in enumerate(candidates):
                if label.lower() == ai_choice:
                    if i > 0:
                        log.info(f"AI 复核：将 {label} 从第 {i+1} 名提升到第 1 名")
                        # 调整排名（给 AI 选择的结果加权）
                        new_candidates = candidates.copy()
                        new_candidates[0], new_candidates[i] = new_candidates[i], new_candidates[0]
                        return new_candidates
                    break
            
            return candidates
            
        except Exception as e:
            log.exception(f"OpenAI API 调用失败: {e}")
            return candidates
    
    def _rerank_ollama(
        self,
        image: Image.Image,
        candidates: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """使用 Ollama 进行复核"""
        try:
            import requests
        except ImportError:
            log.error("未安装 requests 库，请运行: pip install requests")
            return candidates
        
        # 将图片转为 base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # 构建候选列表文本
        candidates_text = "\n".join([
            f"{i+1}. {label} (score: {score:.2f})"
            for i, (label, score) in enumerate(candidates)
        ])
        
        prompt = f"""You are a textile expert. Please analyze this fabric image and choose the most likely fabric type from these candidates:

{candidates_text}

Reply with only the fabric label (English name), no explanation."""
        
        try:
            response = requests.post(
                f"{cfg.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": cfg.OLLAMA_MODEL,
                    "prompt": prompt,
                    "images": [img_base64],
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            
            ai_choice = response.json().get("response", "").strip().lower()
            log.info(f"AI 选择: {ai_choice}")
            
            # 调整排名逻辑同 OpenAI
            for i, (label, score) in enumerate(candidates):
                if label.lower() == ai_choice:
                    if i > 0:
                        log.info(f"AI 复核：将 {label} 从第 {i+1} 名提升到第 1 名")
                        new_candidates = candidates.copy()
                        new_candidates[0], new_candidates[i] = new_candidates[i], new_candidates[0]
                        return new_candidates
                    break
            
            return candidates
            
        except Exception as e:
            log.exception(f"Ollama API 调用失败: {e}")
            return candidates


# 便捷函数
def create_reranker() -> LMMReranker:
    """创建复核器实例"""
    return LMMReranker()


__all__ = [
    'LMMReranker',
    'create_reranker',
]

