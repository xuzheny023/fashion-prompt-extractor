# -*- coding: utf-8 -*-
"""
测试评测工具
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("开始测试评测工具...")

# 测试1: 导入
print("\n[1/3] 测试导入...")
try:
    from tools.eval_cli import load_eval_dataset, evaluate_image
    print("  ✓ 导入成功")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试2: 加载数据集
print("\n[2/3] 测试数据集加载...")
try:
    eval_dir = Path("eval_set")
    dataset = load_eval_dataset(eval_dir)
    print(f"  ✓ 加载成功: {len(dataset)} 个类别")
    for label, images in dataset.items():
        print(f"    - {label}: {len(images)} 张")
except Exception as e:
    print(f"  ✗ 加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试3: 评测单张图片
print("\n[3/3] 测试单张图片评测...")
try:
    # 取第一张图片
    first_label = list(dataset.keys())[0]
    first_image = dataset[first_label][0]
    
    print(f"  测试图片: {first_image}")
    print(f"  真实标签: {first_label}")
    
    result_dict, elapsed_ms = evaluate_image(first_image, first_label, top_k=5)
    
    print(f"  ✓ 评测成功")
    print(f"    - Top-1 预测: {result_dict['top1_pred']}")
    print(f"    - Top-1 分数: {result_dict['top1_score']:.2f}")
    print(f"    - Top-1 正确: {result_dict['top1_correct']}")
    print(f"    - 耗时: {elapsed_ms:.1f}ms")
    
except Exception as e:
    print(f"  ✗ 评测失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ 所有测试通过！")
print("\n现在可以运行完整评测:")
print("  python tools/eval_cli.py --dir eval_set")

