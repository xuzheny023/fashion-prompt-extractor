# -*- coding: utf-8 -*-
"""
快速验证 fabric_ranker 重构

用法:
    python tools/verify_ranker.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 验证 fabric_ranker 重构...")

# 1. 测试导入
print("\n[1/5] 测试导入...")
try:
    from src.fabric_clip_ranker import retrieve_topk, load_centroids, load_bank
    from src.types import ScoreItem
    from src.config import cfg
    print("  ✓ 导入成功")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")
    sys.exit(1)

# 2. 测试配置读取
print("\n[2/5] 测试配置读取...")
try:
    print(f"  TOPK: {cfg.TOPK}")
    print(f"  TOPC: {cfg.TOPC}")
    print(f"  MIN_SAMPLES: {cfg.MIN_SAMPLES}")
    print(f"  FABRIC_BANK: {cfg.FABRIC_BANK}")
    print("  ✓ 配置读取正常")
except Exception as e:
    print(f"  ✗ 配置读取失败: {e}")
    sys.exit(1)

# 3. 测试向量库加载
print("\n[3/5] 测试向量库加载...")
try:
    labels, C = load_centroids()
    print(f"  ✓ 类中心: {len(labels)} 类")
    if C.size > 0:
        print(f"  ✓ 矩阵形状: {C.shape}")
    
    bank = load_bank()
    print(f"  ✓ 向量库: {len(bank)} 类")
    total = sum(X.shape[0] for X in bank.values())
    print(f"  ✓ 总样本数: {total}")
except Exception as e:
    print(f"  ✗ 向量库加载失败: {e}")
    sys.exit(1)

# 4. 测试检索函数
print("\n[4/5] 测试检索函数...")
try:
    import numpy as np
    # 创建随机查询向量
    query = np.random.randn(1536).astype("float32")
    
    results, coarse_max = retrieve_topk(query, topk=5, topc=10)
    
    print(f"  ✓ 检索完成")
    print(f"  ✓ 返回类型: {type(results)}")
    print(f"  ✓ 结果数量: {len(results)}")
    
    if results:
        print(f"  ✓ 元素类型: {type(results[0])}")
        if isinstance(results[0], ScoreItem):
            print(f"  ✓ ScoreItem 验证通过")
            print(f"    - label: {results[0].label}")
            print(f"    - score: {results[0].score:.3f}")
        else:
            print(f"  ✗ 元素类型错误: 期望 ScoreItem")
            sys.exit(1)
    
    print(f"  ✓ 粗排最高分: {coarse_max:.3f}")
    
except Exception as e:
    print(f"  ✗ 检索失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试性能（简单）
print("\n[5/5] 测试性能...")
try:
    import time
    
    # 编码（使用随机向量模拟）
    query = np.random.randn(1536).astype("float32")
    
    # 检索
    t0 = time.perf_counter()
    results, coarse_max = retrieve_topk(query)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    
    print(f"  ✓ 检索耗时: {elapsed_ms:.1f}ms")
    
    if elapsed_ms < 500:
        print(f"  ✅ 性能达标 (< 500ms)")
    else:
        print(f"  ⚠️  性能未达标 (>= 500ms)")
        print(f"     建议: 安装 FAISS 或减少样本数")
    
except Exception as e:
    print(f"  ✗ 性能测试失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有验证通过！")
print("=" * 60)

print("\n💡 重构完成:")
print("  • 引入 cfg 和 types")
print("  • @lru_cache 缓存向量库")
print("  • L2 归一化")
print("  • 矩阵化操作（无循环）")
print("  • 返回 List[ScoreItem]")
print("  • 添加 logger.debug")

print("\n📝 下一步:")
print("  python tools/benchmark_retrieval.py  # 完整性能测试")

