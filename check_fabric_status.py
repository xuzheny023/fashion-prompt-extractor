#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick fabric collection status checker
快速查看面料收集状态
"""
from pathlib import Path

ROOT = Path("data/fabrics")

def check_status():
    """检查每个面料类别的图片数量"""
    fabric_dirs = sorted([p for p in ROOT.iterdir() if p.is_dir()])
    
    ready = []      # ≥5 张图片
    partial = []    # 1-4 张图片  
    empty = []      # 0 张图片
    
    print("="*70)
    print("Fabric Collection Status")
    print("="*70)
    print(f"\nTotal directories: {len(fabric_dirs)}\n")
    
    for fabric_dir in fabric_dirs:
        # 统计图片文件（递归）
        patterns = ("**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.JPG", "**/*.PNG", "**/*.JPEG")
        image_files = []
        for pat in patterns:
            image_files.extend(fabric_dir.glob(pat))
        count = len(image_files)
        
        status = "✓" if count >= 5 else "○" if count > 0 else "✗"
        
        if count >= 5:
            ready.append((fabric_dir.name, count))
            print(f"  {status} {fabric_dir.name:<20} {count:>3} images (READY)")
        elif count > 0:
            partial.append((fabric_dir.name, count))
            print(f"  {status} {fabric_dir.name:<20} {count:>3} images (need {5-count} more)")
        else:
            empty.append((fabric_dir.name, count))
            # print(f"  {status} {fabric_dir.name:<20} {count:>3} images (EMPTY)")
    
    print("\n" + "="*70)
    print("Summary:")
    print(f"  ✓ Ready (≥5 images):  {len(ready):>3} categories")
    print(f"  ○ Partial (1-4):      {len(partial):>3} categories")
    print(f"  ✗ Empty (0):          {len(empty):>3} categories")
    print(f"  📁 Total:             {len(fabric_dirs):>3} categories")
    
    # 计算完成度
    total_needed = len(fabric_dirs) * 5
    total_collected = sum(count for _, count in ready) + sum(count for _, count in partial)
    progress = (total_collected / total_needed * 100) if total_needed > 0 else 0
    
    print(f"\n  📊 Progress: {total_collected}/{total_needed} images ({progress:.1f}%)")
    print("="*70)
    
    if ready:
        print(f"\n✅ Ready categories ({len(ready)}):")
        for name, count in ready:
            print(f"   {name:<20} {count} images")
    
    if partial:
        print(f"\n⚠️  Partial categories ({len(partial)}) - need more images:")
        for name, count in partial:
            print(f"   {name:<20} (has {count}, need {5-count} more)")
    
    print(f"\n💡 Next steps:")
    if len(ready) == 0:
        print(f"   1. Add images to at least one category to get started")
        print(f"   2. See tools/IMAGE_COLLECTION_GUIDE.md for help")
    elif len(ready) < 10:
        print(f"   1. Add images to {len(partial) + len(empty)} categories")
        print(f"   2. Target: Get 10+ categories ready for better coverage")
    else:
        print(f"   1. Great progress! {len(ready)} categories ready")
        print(f"   2. Run: python tools/build_fabric_bank.py")
        print(f"   3. Test with your fashion images")

if __name__ == "__main__":
    check_status()
