# -*- coding: utf-8 -*-
"""
Remove broken/unsupported fabric images
删除损坏或不支持格式的面料图片
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image

ROOT = Path("data/fabrics")

def remove_broken_images():
    """扫描并删除无法打开的图片"""
    if not ROOT.exists():
        print(f"[ERROR] {ROOT} not found")
        return
    
    fabric_dirs = [p for p in ROOT.iterdir() if p.is_dir()]
    removed_count = 0
    
    for fabric_dir in sorted(fabric_dirs):
        print(f"\n[{fabric_dir.name}]")
        
        image_files = list(fabric_dir.glob("*"))
        image_files = [f for f in image_files if f.is_file() and not f.name.startswith('.')]
        
        for img_path in sorted(image_files):
            # 跳过文本文件
            if img_path.suffix.lower() in ['.txt', '.md', '.json']:
                continue
            
            try:
                # 尝试打开并验证
                img = Image.open(img_path)
                img.verify()
                print(f"  ✓ {img_path.name}")
            except Exception as e:
                # 删除无法打开的文件
                print(f"  ✗ {img_path.name} - REMOVING (error: {str(e)[:40]})")
                img_path.unlink()
                removed_count += 1
    
    print("\n" + "="*60)
    print(f"Removed {removed_count} broken image(s)")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("Remove Broken Fabric Images")
    print("="*60)
    
    answer = input("\n⚠️  This will DELETE broken images. Continue? (yes/no): ")
    if answer.lower() in ['yes', 'y']:
        remove_broken_images()
        print("\n✅ Done! You can now rebuild the fabric bank:")
        print("   python tools\\build_fabric_bank.py")
    else:
        print("Cancelled.")

