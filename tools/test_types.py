# -*- coding: utf-8 -*-
"""
数据类型测试

用法:
    python tools/test_types.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.types import ScoreItem, RankedResult, QueryMeta

print("=" * 60)
print("标准化数据类型测试")
print("=" * 60)

# 测试1: ScoreItem
print("\n[1/5] 测试 ScoreItem:")
item1 = ScoreItem(label="cotton", score=0.85)
item2 = ScoreItem(label="linen", score=0.72)
item3 = ScoreItem(label="silk", score=0.68)
print(f"  ✓ item1: {item1.label} = {item1.score:.2f}")
print(f"  ✓ item2: {item2.label} = {item2.score:.2f}")
print(f"  ✓ item3: {item3.label} = {item3.score:.2f}")

# 测试2: ScoreItem 验证
print("\n[2/5] 测试 ScoreItem 数据验证:")
try:
    bad_item = ScoreItem(label="test", score=1.5)
    print("  ✗ 应该抛出 ValueError（score > 1.0）")
except ValueError as e:
    print(f"  ✓ 正确捕获异常: {e}")

try:
    bad_item = ScoreItem(label=123, score=0.5)
    print("  ✗ 应该抛出 TypeError（label 不是字符串）")
except TypeError as e:
    print(f"  ✓ 正确捕获异常: {e}")

# 测试3: RankedResult
print("\n[3/5] 测试 RankedResult:")
result = RankedResult(
    items=[item1, item2, item3],
    ai_reason="基于 CLIP 向量相似度"
)
print(f"  ✓ 总结果数: {len(result.items)}")
print(f"  ✓ Top 1: {result.top1.label} ({result.top1.score:.2f})")
print(f"  ✓ Top 3: {[item.label for item in result.top3]}")
print(f"  ✓ AI 原因: {result.ai_reason}")

# 测试4: RankedResult 方法
print("\n[4/5] 测试 RankedResult 方法:")
top2 = result.get_top_k(k=2)
print(f"  ✓ get_top_k(2): {[item.label for item in top2]}")

filtered = result.filter_by_threshold(threshold=0.70)
print(f"  ✓ filter_by_threshold(0.70): {[item.label for item in filtered]}")

# 测试5: QueryMeta
print("\n[5/5] 测试 QueryMeta:")
meta = QueryMeta(ms=150, coarse_max=0.92)
print(f"  ✓ 耗时: {meta.ms} ms ({meta.seconds:.3f} 秒)")
print(f"  ✓ 粗排最高分: {meta.coarse_max:.2f}")
print(f"  ✓ 是否快速 (<200ms): {meta.is_fast()}")
print(f"  ✓ 是否快速 (<100ms): {meta.is_fast(threshold_ms=100)}")

# 综合示例
print("\n[综合示例] 模拟完整的检索流程:")
print("-" * 60)

# 创建评分项
items = [
    ScoreItem("cotton", 0.89),
    ScoreItem("linen", 0.76),
    ScoreItem("silk", 0.68),
    ScoreItem("polyester", 0.55),
    ScoreItem("wool", 0.42),
]

# 创建排名结果
ranked = RankedResult(
    items=items,
    ai_reason="双通道 CLIP 特征匹配，重点关注纹理细腻度"
)

# 创建查询元数据
query_meta = QueryMeta(ms=185, coarse_max=0.91)

# 输出结果
print(f"\n查询性能:")
print(f"  耗时: {query_meta.ms} ms")
print(f"  粗排最高分: {query_meta.coarse_max:.2f}")

print(f"\n推荐结果 (Top 3):")
for i, item in enumerate(ranked.top3, 1):
    confidence_bar = "█" * int(item.score * 20)
    print(f"  {i}. {item.label:<12} {item.score:.2f} {confidence_bar}")

print(f"\n推理原因: {ranked.ai_reason}")

print(f"\n高置信度结果 (≥0.70):")
high_conf = ranked.filter_by_threshold(0.70)
for item in high_conf:
    print(f"  - {item.label}: {item.score:.2%}")

print("\n" + "=" * 60)
print("✅ 所有测试通过")
print("=" * 60)

print("\n💡 使用示例:")
print("""
# 在推荐函数中使用
def recommend_fabrics(image) -> tuple[RankedResult, QueryMeta]:
    import time
    t0 = time.perf_counter()
    
    # ... 检索逻辑 ...
    
    items = [ScoreItem(label, score) for label, score in results]
    result = RankedResult(items=items, ai_reason="CLIP 匹配")
    meta = QueryMeta(ms=int((time.perf_counter() - t0) * 1000))
    
    return result, meta

# 在 UI 中使用
result, meta = recommend_fabrics(image)
st.write(f"耗时: {meta.ms}ms")
for item in result.top3:
    st.write(f"{item.label}: {item.score:.2%}")
""")

