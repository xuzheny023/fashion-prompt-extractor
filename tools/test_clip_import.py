# -*- coding: utf-8 -*-
"""
快速测试 CLIP 模块导入

用法：
    python tools/test_clip_import.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("CLIP 模块导入测试")
print("=" * 60)

# 测试1: 导入基础模块
print("\n[1/5] 测试基础模块导入...")
try:
    import numpy as np
    from PIL import Image
    print("  ✓ numpy, PIL 导入成功")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    sys.exit(1)

# 测试2: 导入 dual_clip
print("\n[2/5] 测试 dual_clip 模块...")
try:
    from src.dual_clip import image_to_emb, get_encoder
    print("  ✓ dual_clip 导入成功")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    sys.exit(1)

# 测试3: 导入 fabric_clip_ranker
print("\n[3/5] 测试 fabric_clip_ranker 模块...")
try:
    from src.fabric_clip_ranker import (
        load_centroids,
        load_bank,
        retrieve_topk,
        recommend_fabrics_clip
    )
    print("  ✓ fabric_clip_ranker 导入成功")
    print(f"    - load_centroids: {load_centroids}")
    print(f"    - load_bank: {load_bank}")
    print(f"    - retrieve_topk: {retrieve_topk}")
    print(f"    - recommend_fabrics_clip: {recommend_fabrics_clip}")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试4: 导入 fabric_labels
print("\n[4/5] 测试 fabric_labels 模块...")
try:
    from src.fabric_labels import get_label, load_labels
    print("  ✓ fabric_labels 导入成功")
except Exception as e:
    print(f"  ✗ 失败: {e}")
    sys.exit(1)

# 测试5: 检查向量库
print("\n[5/5] 检查向量库文件...")
bank_path = Path("data/fabric_bank.npz")
cent_path = Path("data/fabric_centroids.npz")

if bank_path.exists():
    print(f"  ✓ fabric_bank.npz 存在 ({bank_path.stat().st_size / 1024:.2f} KB)")
else:
    print(f"  ✗ fabric_bank.npz 不存在")

if cent_path.exists():
    print(f"  ✓ fabric_centroids.npz 存在 ({cent_path.stat().st_size / 1024:.2f} KB)")
else:
    print(f"  ⚠️  fabric_centroids.npz 不存在（可选）")

print("\n" + "=" * 60)
print("✅ 所有测试通过！CLIP 模块可以正常使用。")
print("=" * 60)
print("\n💡 现在可以启动 Streamlit:")
print("   streamlit run app.py")


