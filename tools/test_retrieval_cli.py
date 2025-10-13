# -*- coding: utf-8 -*-
"""
面料检索测试工具（CLI）

使用方法：
    python tools/test_retrieval_cli.py <图片路径> [--top-k 5]

示例：
    python tools/test_retrieval_cli.py data/fabrics/denim/test.jpg
    python tools/test_retrieval_cli.py mytest.jpg --top-k 10
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import numpy as np
from PIL import Image
from src.dual_clip import image_to_emb
from src.fabric_labels import get_label

# 加载向量库
BANK_PATH = Path("data/fabric_bank.npz")
CENTROIDS_PATH = Path("data/fabric_centroids.npz")

if not BANK_PATH.exists():
    print(f"[ERR] 向量库不存在: {BANK_PATH}", flush=True)
    print("请先运行: python tools/build_fabric_bank.py", flush=True)
    sys.exit(1)

BANK = np.load(BANK_PATH)
CENTROIDS = np.load(CENTROIDS_PATH) if CENTROIDS_PATH.exists() else None

# 过滤：只保留样本数 ≥3 的类别
VALID_CLASSES = [k for k in BANK.files if BANK[k].shape[0] >= 3]

print(f"[INFO] 已加载 {len(VALID_CLASSES)}/{len(BANK.files)} 个有效类别", flush=True)
if CENTROIDS:
    print(f"[INFO] 使用类中心向量加速检索", flush=True)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """余弦相似度（限制在 [-1, 1] 范围内）"""
    sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
    # 限制在有效范围内，避免数值精度问题
    return max(-1.0, min(1.0, sim))


def retrieve_topk(query_emb: np.ndarray, k: int = 5, threshold: float = 0.03):
    """
    检索 Top-K 面料
    
    策略：
    1. 优先使用类中心向量做粗排（快）
    2. 如果 Top1 和 Top2 分数差 < threshold，回退到全样本精排（准）
    
    Args:
        query_emb: 查询图片的向量 [1536]
        k: 返回 Top-K 结果
        threshold: 分数差阈值，低于此值触发精排
    
    Returns:
        [(类别ID, 分数, 中文名), ...]
    """
    
    # Step 1: 类中心粗排
    if CENTROIDS:
        centroid_scores = {}
        for cls in VALID_CLASSES:
            if cls in CENTROIDS.files:
                centroid = CENTROIDS[cls].squeeze()
                score = cosine_sim(query_emb, centroid)
                centroid_scores[cls] = score
        
        sorted_by_centroid = sorted(centroid_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 检查是否需要精排
        if len(sorted_by_centroid) >= 2:
            top1_score = sorted_by_centroid[0][1]
            top2_score = sorted_by_centroid[1][1]
            need_refine = (top1_score - top2_score) < threshold
        else:
            need_refine = False
        
        # 如果分数差距大，直接返回粗排结果
        if not need_refine:
            results = [(cls, score, get_label(cls)) for cls, score in sorted_by_centroid[:k]]
            return results
    
    # Step 2: 全样本精排（准确但慢）
    all_scores = {}
    for cls in VALID_CLASSES:
        samples = BANK[cls]  # [N, 1536]
        # 计算与所有样本的最大相似度
        scores = [cosine_sim(query_emb, sample) for sample in samples]
        all_scores[cls] = max(scores)
    
    sorted_by_sample = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    results = [(cls, score, get_label(cls)) for cls, score in sorted_by_sample[:k]]
    return results


def main():
    parser = argparse.ArgumentParser(description="面料检索测试工具")
    parser.add_argument("image", type=str, help="测试图片路径")
    parser.add_argument("--top-k", type=int, default=5, help="返回 Top-K 结果（默认5）")
    parser.add_argument("--threshold", type=float, default=0.03, help="精排触发阈值（默认0.03）")
    
    args = parser.parse_args()
    
    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[ERR] 图片不存在: {img_path}", flush=True)
        return 1
    
    print(f"\n[1/2] 编码图片: {img_path.name}", flush=True)
    img = Image.open(img_path).convert("RGB")
    query_emb = image_to_emb(img)
    print(f"  ✓ 向量维度: {query_emb.shape}", flush=True)
    
    print(f"\n[2/2] 检索 Top-{args.top_k} 面料...", flush=True)
    results = retrieve_topk(query_emb, k=args.top_k, threshold=args.threshold)
    
    print(f"\n{'='*60}")
    print(f"检索结果 (Top-{args.top_k})")
    print(f"{'='*60}")
    
    for i, (cls_id, score, cn_name) in enumerate(results, 1):
        confidence = int(score * 100)
        bar = "█" * (confidence // 5) + "░" * (20 - confidence // 5)
        warning = " ⚠️ 建议人工确认" if score < 0.30 else ""
        print(f"{i:2d}. {cn_name:<12} ({cls_id:<15}) {score:.3f}  [{bar}] {confidence}%{warning}")
    
    print(f"{'='*60}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
