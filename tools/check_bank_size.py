# -*- coding: utf-8 -*-
"""
检查向量库大小和性能建议

用法：
    python tools/check_bank_size.py
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from pathlib import Path

BANK_PATH = Path("data/fabric_bank.npz")
CENTROIDS_PATH = Path("data/fabric_centroids.npz")

def format_size(bytes_size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def main():
    print("=" * 60)
    print("向量库大小检查")
    print("=" * 60)
    
    if not BANK_PATH.exists():
        print(f"❌ 向量库不存在: {BANK_PATH}")
        print("💡 请先运行: python tools/build_fabric_bank.py")
        return 1
    
    # 加载向量库
    bank = np.load(BANK_PATH)
    
    # 统计信息
    total_vectors = 0
    total_classes = len(bank.files)
    vector_dim = None
    
    print(f"\n📊 基本信息:")
    print(f"  类别数: {total_classes}")
    
    for cls in bank.files:
        X = bank[cls]
        if vector_dim is None:
            vector_dim = X.shape[1] if X.ndim == 2 else X.shape[0]
        total_vectors += X.shape[0] if X.ndim == 2 else 1
    
    print(f"  总向量数: {total_vectors:,}")
    print(f"  向量维度: {vector_dim}")
    print(f"  平均每类: {total_vectors / total_classes:.1f} 个向量")
    
    # 文件大小
    bank_size = BANK_PATH.stat().st_size
    print(f"\n💾 文件大小:")
    print(f"  fabric_bank.npz: {format_size(bank_size)}")
    
    if CENTROIDS_PATH.exists():
        cent_size = CENTROIDS_PATH.stat().st_size
        print(f"  fabric_centroids.npz: {format_size(cent_size)}")
    
    # 内存估算
    memory_estimate = total_vectors * vector_dim * 4  # float32
    print(f"\n🧠 内存估算:")
    print(f"  向量库内存: {format_size(memory_estimate)}")
    
    # 性能建议
    print(f"\n⚡ 性能建议:")
    
    if total_vectors < 10000:
        print("  ✓ 向量数量适中，NumPy 矩阵运算已足够快")
        print("  💡 可选：安装 faiss-cpu 可再提速 20-30%")
    elif total_vectors < 50000:
        print("  ⚠️ 向量数量较多，建议安装 FAISS 加速")
        print("  💡 运行: pip install faiss-cpu")
    else:
        print("  ⚠️ 向量数量很多，强烈建议使用 FAISS")
        print("  💡 运行: pip install faiss-cpu")
        print("  💡 考虑使用向量量化减少内存占用")
    
    # 优化建议
    print(f"\n🔧 优化建议:")
    
    samples_per_class = total_vectors / total_classes
    if samples_per_class > 15:
        print(f"  ⚠️ 平均每类 {samples_per_class:.1f} 个样本，可能过多")
        print("  💡 建议：保留最具代表性的 5-10 张图片")
        print("  💡 可减少检索时间 30-50%")
    elif samples_per_class < 3:
        print(f"  ⚠️ 平均每类只有 {samples_per_class:.1f} 个样本")
        print("  💡 建议：每类至少 5 张高质量图片")
        print("  💡 可提高识别准确率")
    else:
        print(f"  ✓ 样本数量适中 ({samples_per_class:.1f} 个/类)")
    
    # 详细统计
    print(f"\n📈 详细统计:")
    class_counts = []
    for cls in bank.files:
        X = bank[cls]
        count = X.shape[0] if X.ndim == 2 else 1
        class_counts.append((cls, count))
    
    # 按样本数排序
    class_counts.sort(key=lambda x: x[1], reverse=True)
    
    print(f"  样本最多的 5 个类:")
    for cls, count in class_counts[:5]:
        print(f"    {cls:<15}: {count:3d} 个")
    
    print(f"  样本最少的 5 个类:")
    for cls, count in class_counts[-5:]:
        status = "⚠️" if count < 3 else "  "
        print(f"    {status} {cls:<15}: {count:3d} 个")
    
    print("\n" + "=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())


