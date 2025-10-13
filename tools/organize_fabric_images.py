# -*- coding: utf-8 -*-
"""
Fabric image organizer - Organize downloaded images into fabric categories
面料图片整理器 - 将下载的图片整理到对应的面料类别
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import shutil

def organize_images_interactive():
    """交互式整理图片"""
    
    # 检查是否有待整理的图片目录
    inbox_dir = Path("data/fabrics_inbox")
    
    if not inbox_dir.exists():
        print("Creating inbox directory...")
        inbox_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 Created: {inbox_dir}")
        print("\n💡 Usage:")
        print("   1. Put your fabric images in: data/fabrics_inbox/")
        print("   2. Run this script again")
        print("   3. For each image, type the fabric category name")
        print("   4. Or type 'skip' to skip, 'quit' to exit")
        return
    
    # 获取所有图片
    image_files = (
        list(inbox_dir.glob("*.jpg")) +
        list(inbox_dir.glob("*.jpeg")) +
        list(inbox_dir.glob("*.png"))
    )
    
    if not image_files:
        print(f"✗ No images found in {inbox_dir}")
        print("\n💡 Put your fabric images in: data/fabrics_inbox/")
        return
    
    # 获取所有可用的面料类别
    fabrics_dir = Path("data/fabrics")
    categories = sorted([d.name for d in fabrics_dir.iterdir() if d.is_dir()])
    
    print("="*60)
    print("Interactive Fabric Image Organizer")
    print("="*60)
    print(f"\nFound {len(image_files)} images to organize")
    print(f"Available categories: {len(categories)}")
    print("\nCommands: [fabric_name] | skip | quit | list")
    print("-"*60)
    
    organized = 0
    skipped = 0
    
    for i, img_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] {img_path.name}")
        
        # 尝试显示图片信息
        try:
            img = Image.open(img_path)
            print(f"  Size: {img.size}, Mode: {img.mode}")
        except Exception as e:
            print(f"  ⚠️  Cannot open: {e}")
        
        # 询问分类
        while True:
            category = input("  Category? ").strip().lower()
            
            if category == 'quit':
                print(f"\nStopped. Organized: {organized}, Skipped: {skipped}")
                return
            
            if category == 'skip':
                skipped += 1
                break
            
            if category == 'list':
                print("\n  Available categories:")
                for j, cat in enumerate(categories, 1):
                    print(f"    {j:2d}. {cat}")
                continue
            
            # 检查类别是否存在
            target_dir = fabrics_dir / category
            if not target_dir.exists():
                print(f"  ✗ Category '{category}' not found. Try 'list' to see all.")
                continue
            
            # 移动图片
            try:
                # 生成新文件名
                existing = len(list(target_dir.glob("*.jpg")))
                new_name = f"{category}_{existing+1:03d}.jpg"
                target_path = target_dir / new_name
                
                # 转换并保存
                img = Image.open(img_path).convert('RGB')
                img.save(target_path, 'JPEG', quality=95)
                
                # 删除原文件
                img_path.unlink()
                
                print(f"  ✓ Moved to: {target_path}")
                organized += 1
                break
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                break
    
    print("\n" + "="*60)
    print(f"Summary: ✓ {organized} organized, ○ {skipped} skipped")
    print("="*60)

def auto_organize_by_prefix():
    """
    根据文件名前缀自动整理
    
    文件命名格式：category_xxx.jpg
    例如：denim_001.jpg, silk_fabric_01.jpg
    """
    inbox_dir = Path("data/fabrics_inbox")
    
    if not inbox_dir.exists():
        print(f"✗ Inbox directory not found: {inbox_dir}")
        return
    
    image_files = (
        list(inbox_dir.glob("*.jpg")) +
        list(inbox_dir.glob("*.jpeg")) +
        list(inbox_dir.glob("*.png"))
    )
    
    if not image_files:
        print(f"✗ No images found in {inbox_dir}")
        return
    
    fabrics_dir = Path("data/fabrics")
    categories = {d.name for d in fabrics_dir.iterdir() if d.is_dir()}
    
    print("="*60)
    print("Auto Organize by Filename Prefix")
    print("="*60)
    
    organized = 0
    failed = 0
    
    for img_path in image_files:
        # 从文件名提取类别（取第一个下划线前的部分）
        parts = img_path.stem.split('_')
        if not parts:
            print(f"✗ {img_path.name}: No prefix found")
            failed += 1
            continue
        
        category = parts[0].lower()
        
        if category not in categories:
            print(f"✗ {img_path.name}: Category '{category}' not found")
            failed += 1
            continue
        
        # 移动图片
        try:
            target_dir = fabrics_dir / category
            existing = len(list(target_dir.glob("*.jpg")))
            new_name = f"{category}_{existing+1:03d}.jpg"
            target_path = target_dir / new_name
            
            img = Image.open(img_path).convert('RGB')
            img.save(target_path, 'JPEG', quality=95)
            img_path.unlink()
            
            print(f"✓ {img_path.name} → {target_path}")
            organized += 1
            
        except Exception as e:
            print(f"✗ {img_path.name}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Summary: ✓ {organized} organized, ✗ {failed} failed")
    print("="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'auto':
        auto_organize_by_prefix()
    else:
        organize_images_interactive()


