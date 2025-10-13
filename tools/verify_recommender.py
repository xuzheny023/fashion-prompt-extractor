# -*- coding: utf-8 -*-
"""
快速验证推荐引擎

用法:
    python tools/verify_recommender.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 验证推荐引擎...")

# 1. 测试导入
print("\n[1/3] 测试导入...")
try:
    from src.core.recommender import recommend
    print("  ✓ recommend 导入成功")
except ImportError as e:
    print(f"  ✗ 导入失败: {e}")
    sys.exit(1)

# 2. 测试依赖
print("\n[2/3] 测试依赖模块...")
try:
    from src.types import RankedResult, QueryMeta
    from src.dual_clip import get_encoder
    from src.fabric_clip_ranker import retrieve_topk
    from src.ai_boost import LMMReranker
    print("  ✓ 所有依赖模块正常")
except ImportError as e:
    print(f"  ✗ 依赖模块缺失: {e}")
    sys.exit(1)

# 3. 测试向量库
print("\n[3/3] 测试向量库...")
try:
    from src.config import check_vector_bank
    if check_vector_bank():
        print("  ✓ 向量库已就绪")
    else:
        print("  ⚠ 向量库不存在，请运行: python tools/build_fabric_bank.py")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ 向量库检查失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有验证通过！")
print("=" * 60)

print("\n💡 使用方法:")
print("""
# 在 app.py 中单行调用
from src.core.recommender import recommend
from PIL import Image

img = Image.open("fabric.jpg")
result, meta = recommend(img)

print(f"Top 1: {result.top1.label} ({result.top1.score:.2%})")
print(f"耗时: {meta.ms}ms")
""")

print("\n📝 完整测试:")
print("  python tools/test_recommender.py [图片路径]")

