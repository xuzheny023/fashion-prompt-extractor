# -*- coding: utf-8 -*-
"""
检索性能基准测试

测试目标：
- 单次检索 < 500ms (CPU)
- retrieve_topk 返回 List[ScoreItem]

用法:
    python tools/benchmark_retrieval.py [图片路径] [--runs 10]
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

from src.fabric_clip_ranker import retrieve_topk, load_centroids, load_bank
from src.dual_clip import image_to_emb
from src.types import ScoreItem
from src.utils.logger import get_logger

log = get_logger("benchmark")

def benchmark_retrieval(image_path: Path, num_runs: int = 10):
    """性能基准测试"""
    
    print("=" * 70)
    print("检索性能基准测试")
    print("=" * 70)
    
    # 1. 加载图片
    print(f"\n📷 测试图片: {image_path}")
    try:
        img = Image.open(image_path)
        print(f"  ✓ 图片大小: {img.size[0]}x{img.size[1]}")
    except Exception as e:
        print(f"  ✗ 图片加载失败: {e}")
        return False
    
    # 2. 预热（首次加载模型和向量库）
    print("\n🔥 预热阶段...")
    print("  → 加载 CLIP 编码器...")
    t0 = time.perf_counter()
    query_emb = image_to_emb(img)
    warmup_encode_ms = (time.perf_counter() - t0) * 1000
    print(f"  ✓ 编码完成: {warmup_encode_ms:.0f}ms (首次包含模型加载)")
    
    print("  → 加载向量库...")
    t0 = time.perf_counter()
    _ = load_centroids()
    _ = load_bank()
    warmup_load_ms = (time.perf_counter() - t0) * 1000
    print(f"  ✓ 向量库加载: {warmup_load_ms:.0f}ms")
    
    print("  → 预热检索...")
    t0 = time.perf_counter()
    results, coarse_max = retrieve_topk(query_emb)
    warmup_retrieve_ms = (time.perf_counter() - t0) * 1000
    print(f"  ✓ 预热检索: {warmup_retrieve_ms:.0f}ms")
    
    # 3. 验证返回类型
    print("\n✅ 验证返回类型...")
    if not isinstance(results, list):
        print(f"  ✗ 返回类型错误: 期望 list, 实际 {type(results)}")
        return False
    if not results:
        print("  ✗ 返回结果为空")
        return False
    if not isinstance(results[0], ScoreItem):
        print(f"  ✗ 元素类型错误: 期望 ScoreItem, 实际 {type(results[0])}")
        return False
    print(f"  ✓ 返回类型正确: List[ScoreItem]")
    print(f"  ✓ 结果数量: {len(results)}")
    print(f"  ✓ Top 1: {results[0].label} ({results[0].score:.3f})")
    print(f"  ✓ 粗排最高分: {coarse_max:.3f}")
    
    # 4. 性能测试（多次运行）
    print(f"\n⚡ 性能测试 ({num_runs} 次运行)...")
    print("-" * 70)
    
    encode_times = []
    retrieve_times = []
    total_times = []
    
    for i in range(num_runs):
        # 编码
        t0 = time.perf_counter()
        query_emb = image_to_emb(img)
        encode_ms = (time.perf_counter() - t0) * 1000
        encode_times.append(encode_ms)
        
        # 检索
        t0 = time.perf_counter()
        results, coarse_max = retrieve_topk(query_emb)
        retrieve_ms = (time.perf_counter() - t0) * 1000
        retrieve_times.append(retrieve_ms)
        
        total_ms = encode_ms + retrieve_ms
        total_times.append(total_ms)
        
        print(f"  Run {i+1:2d}: 编码={encode_ms:5.0f}ms, 检索={retrieve_ms:5.0f}ms, 总计={total_ms:5.0f}ms")
    
    # 5. 统计分析
    print("\n📊 统计结果:")
    print("-" * 70)
    
    def stats(times, name):
        mean = np.mean(times)
        std = np.std(times)
        min_t = np.min(times)
        max_t = np.max(times)
        median = np.median(times)
        
        print(f"\n{name}:")
        print(f"  平均: {mean:.1f}ms")
        print(f"  中位数: {median:.1f}ms")
        print(f"  标准差: {std:.1f}ms")
        print(f"  范围: {min_t:.1f}ms - {max_t:.1f}ms")
        
        return mean
    
    encode_mean = stats(encode_times, "编码时间")
    retrieve_mean = stats(retrieve_times, "检索时间")
    total_mean = stats(total_times, "总耗时")
    
    # 6. 性能评估
    print("\n🎯 性能评估:")
    print("-" * 70)
    
    target_ms = 500
    passed = total_mean < target_ms
    
    if passed:
        print(f"  ✅ 通过: 平均耗时 {total_mean:.1f}ms < {target_ms}ms")
    else:
        print(f"  ⚠️  未达标: 平均耗时 {total_mean:.1f}ms >= {target_ms}ms")
    
    # 性能建议
    print("\n💡 性能建议:")
    if encode_mean > 200:
        print("  • 编码较慢，考虑使用 GPU 加速")
    if retrieve_mean > 200:
        print("  • 检索较慢，考虑:")
        print("    - 安装 FAISS: pip install faiss-cpu")
        print("    - 减少 TOPC 参数（默认 12）")
        print("    - 减少样本数量")
    if total_mean < 200:
        print("  • ✨ 性能优秀！")
    
    print("\n" + "=" * 70)
    return passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="检索性能基准测试")
    parser.add_argument("image", nargs="?", help="测试图片路径")
    parser.add_argument("--runs", type=int, default=10, help="运行次数（默认 10）")
    
    args = parser.parse_args()
    
    # 查找测试图片
    if args.image:
        test_image = Path(args.image)
    else:
        # 自动查找
        fabrics_dir = Path("data/fabrics")
        test_image = None
        if fabrics_dir.exists():
            for img_file in fabrics_dir.rglob("*.jpg"):
                test_image = img_file
                break
    
    if not test_image or not test_image.exists():
        print("❌ 未找到测试图片")
        print("\n用法: python tools/benchmark_retrieval.py [图片路径] [--runs 10]")
        sys.exit(1)
    
    # 运行基准测试
    success = benchmark_retrieval(test_image, num_runs=args.runs)
    
    sys.exit(0 if success else 1)

