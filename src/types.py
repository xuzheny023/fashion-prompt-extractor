# -*- coding: utf-8 -*-
"""
标准化数据类型

定义项目中统一的数据结构，确保函数返回值的一致性和可维护性。

用法:
    from src.types import ScoreItem, RankedResult, QueryMeta
    
    # 创建评分项
    item = ScoreItem(label="cotton", score=0.85)
    
    # 创建排名结果
    result = RankedResult(
        items=[
            ScoreItem("cotton", 0.85),
            ScoreItem("linen", 0.72),
        ],
        ai_reason="基于纹理特征匹配"
    )
    
    # 创建查询元数据
    meta = QueryMeta(ms=150, coarse_max=0.92)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class ScoreItem:
    """
    单个评分项
    
    Attributes:
        label: 标签/类别名称（如面料类型）
        score: 置信度分数 [0.0, 1.0]
    
    Example:
        >>> item = ScoreItem(label="cotton", score=0.85)
        >>> print(f"{item.label}: {item.score:.2%}")
        cotton: 85.00%
    """
    label: str
    score: float
    
    def __post_init__(self):
        """验证数据有效性"""
        if not isinstance(self.label, str):
            raise TypeError(f"label 必须是字符串，当前类型: {type(self.label)}")
        if not isinstance(self.score, (int, float)):
            raise TypeError(f"score 必须是数字，当前类型: {type(self.score)}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"score 必须在 [0.0, 1.0] 范围内，当前值: {self.score}")


@dataclass
class RankedResult:
    """
    排名结果
    
    Attributes:
        items: 评分项列表，按分数降序排列
        ai_reason: AI 推理原因/解释（可选）
    
    Example:
        >>> result = RankedResult(
        ...     items=[
        ...         ScoreItem("cotton", 0.85),
        ...         ScoreItem("linen", 0.72),
        ...     ],
        ...     ai_reason="基于纹理细腻度和光泽度分析"
        ... )
        >>> print(f"Top 1: {result.items[0].label} ({result.items[0].score:.2f})")
        Top 1: cotton (0.85)
    """
    items: List[ScoreItem]
    ai_reason: str = ""
    
    def __post_init__(self):
        """验证数据有效性"""
        if not isinstance(self.items, list):
            raise TypeError(f"items 必须是列表，当前类型: {type(self.items)}")
        for i, item in enumerate(self.items):
            if not isinstance(item, ScoreItem):
                raise TypeError(f"items[{i}] 必须是 ScoreItem，当前类型: {type(item)}")
    
    @property
    def top1(self) -> ScoreItem | None:
        """返回得分最高的项"""
        return self.items[0] if self.items else None
    
    @property
    def top3(self) -> List[ScoreItem]:
        """返回得分前3的项"""
        return self.items[:3]
    
    def get_top_k(self, k: int = 5) -> List[ScoreItem]:
        """
        获取前 K 个结果
        
        Args:
            k: 返回结果数量
        
        Returns:
            前 K 个评分项
        """
        return self.items[:k]
    
    def filter_by_threshold(self, threshold: float = 0.5) -> List[ScoreItem]:
        """
        过滤低于阈值的结果
        
        Args:
            threshold: 最低分数阈值
        
        Returns:
            分数 >= threshold 的评分项
        """
        return [item for item in self.items if item.score >= threshold]


@dataclass
class QueryMeta:
    """
    查询元数据（性能指标）
    
    Attributes:
        ms: 查询耗时（毫秒）
        coarse_max: 粗排阶段最高分
    
    Example:
        >>> meta = QueryMeta(ms=150, coarse_max=0.92)
        >>> print(f"查询耗时: {meta.ms}ms, 粗排最高分: {meta.coarse_max:.2f}")
        查询耗时: 150ms, 粗排最高分: 0.92
    """
    ms: int = 0
    coarse_max: float = 0.0
    
    def __post_init__(self):
        """验证数据有效性"""
        if not isinstance(self.ms, int):
            raise TypeError(f"ms 必须是整数，当前类型: {type(self.ms)}")
        if self.ms < 0:
            raise ValueError(f"ms 必须非负，当前值: {self.ms}")
        if not isinstance(self.coarse_max, (int, float)):
            raise TypeError(f"coarse_max 必须是数字，当前类型: {type(self.coarse_max)}")
    
    @property
    def seconds(self) -> float:
        """返回耗时（秒）"""
        return self.ms / 1000.0
    
    def is_fast(self, threshold_ms: int = 200) -> bool:
        """
        判断查询是否足够快
        
        Args:
            threshold_ms: 速度阈值（毫秒）
        
        Returns:
            True 如果查询时间 <= 阈值
        """
        return self.ms <= threshold_ms


# 导出所有公共类型
__all__ = [
    'ScoreItem',
    'RankedResult',
    'QueryMeta',
]

