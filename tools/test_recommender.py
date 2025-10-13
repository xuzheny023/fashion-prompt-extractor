# -*- coding: utf-8 -*-
"""
推荐引擎测试

用法:
    python tools/test_recommender.py [图片路径]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from src.core.recommender import recommend
from src.utils.logger import get_logger

log = get_logger("test")

print("=" * 70)
print("推荐引擎测试")
print("=" * 70)

# 查找测试图片
test_image_path = None
if len(sys.argv) > 1:
    test_image_path = Path(sys.argv[1])
else:
    # 自动查找第一个可用的面料图片
    fabrics_dir = Path("data/fabrics")
    if fabrics_dir.exists():
        for img_file in fabrics_dir.rglob("*.jpg"):
            test_image_path = img_file
            break

if not test_image_path or not test_image_path.exists():
    print("❌ 未找到测试图片")
    print("\n用法: python tools/test_recommender.py [图片路径]")
    sys.exit(1)

print(f"\n📷 测试图片: {test_image_path}")
print("-" * 70)

# 加载图片
try:
    image = Image.open(test_image_path)
    print(f"✓ 图片加载成功: {image.size[0]}x{image.size[1]}")
except Exception as e:
    print(f"❌ 图片加载失败: {e}")
    sys.exit(1)

# 测试推荐
print("\n🔍 开始推荐...")
print("-" * 70)

try:
    result, meta = recommend(image, lang="zh")
    
    print("\n✅ 推荐完成!")
    print("=" * 70)
    
    # 显示性能指标
    print("\n📊 性能指标:")
    print(f"  耗时: {meta.ms} ms ({meta.seconds:.3f} 秒)")
    print(f"  粗排最高分: {meta.coarse_max:.3f}")
    print(f"  是否快速 (<200ms): {'是' if meta.is_fast() else '否'}")
    
    # 显示推荐结果
    print(f"\n🏆 推荐结果 (Top {len(result.items)}):")
    for i, item in enumerate(result.items, 1):
        # 置信度条
        bar_length = int(item.score * 30)
        confidence_bar = "█" * bar_length + "░" * (30 - bar_length)
        
        # 置信度标签
        if item.score >= 0.70:
            status = "🟢 高"
        elif item.score >= 0.50:
            status = "🟡 中"
        else:
            status = "🔴 低"
        
        print(f"\n  {i}. {item.label}")
        print(f"     置信度: {item.score:.2%} {status}")
        print(f"     [{confidence_bar}]")
    
    # 显示 AI 推理原因
    if result.ai_reason:
        print(f"\n💡 推理方式: {result.ai_reason}")
    
    # 高置信度过滤
    high_conf = result.filter_by_threshold(0.60)
    if high_conf:
        print(f"\n✨ 高置信度结果 (≥60%):")
        for item in high_conf:
            print(f"  • {item.label}: {item.score:.2%}")
    
    # 低置信度警告
    if result.top1.score < 0.50:
        print("\n⚠️  警告: 最高置信度较低，建议:")
        print("  1. 检查图片质量（光线、角度、清晰度）")
        print("  2. 补充更多训练样本")
        print("  3. 启用 AI 复核（在 .env 中设置 AI_BACKEND）")
    
except Exception as e:
    print(f"\n❌ 推荐失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)

print("\n📝 使用示例:")
print("""
# 在 app.py 或其他模块中
from src.core.recommender import recommend
from PIL import Image

# 单行调用即可
img = Image.open("fabric.jpg")
result, meta = recommend(img)

# 访问结果
print(f"Top 1: {result.top1.label} ({result.top1.score:.2%})")
print(f"Top 3: {[item.label for item in result.top3]}")
print(f"耗时: {meta.ms}ms")

# 高级用法
result, meta = recommend(
    img,
    top_k=10,      # 返回前 10 个结果
    topc=20,       # 粗排保留前 20 个类
    lang="en"      # 使用英文标签
)
""")

