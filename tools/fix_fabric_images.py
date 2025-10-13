# -*- coding: utf-8 -*-
"""
Fix fabric images: convert unsupported formats and rename files
修复面料图片：转换不支持的格式并重命名文件
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import sys

ROOT = Path("data/fabrics")

def fix_images():
    """
    扫描并修复所有面料图片：
    1. 尝试打开每张图片
    2. 如果格式不支持，尝试用其他库转换
    3. 重命名为标准 .jpg 格式
    """
    if not ROOT.exists():
        print(f"[ERROR] {ROOT} not found")
        return
    
    fabric_dirs = [p for p in ROOT.iterdir() if p.is_dir()]
    if not fabric_dirs:
        print(f"[WARN] No fabric directories found")
        return
    
    fixed_count = 0
    error_count = 0
    
    for fabric_dir in sorted(fabric_dirs):
        print(f"\n[{fabric_dir.name}]", flush=True)
        
        # 查找所有可能的图片文件
        image_files = list(fabric_dir.glob("*"))
        image_files = [f for f in image_files if f.is_file() and not f.name.startswith('.')]
        
        if not image_files:
            print(f"  (no files)", flush=True)
            continue
        
        for img_path in sorted(image_files):
            # 跳过 README 等文本文件
            if img_path.suffix.lower() in ['.txt', '.md', '.json']:
                continue
            
            try:
                # 尝试用 Pillow 打开
                print(f"  Checking: {img_path.name} ... ", end="", flush=True)
                img = Image.open(img_path)
                img.verify()  # 验证图片完整性
                
                # 重新打开以便后续操作（verify 后需要重开）
                img = Image.open(img_path).convert("RGB")
                
                # 检查是否需要重命名
                if img_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                    # 转换为标准格式
                    new_name = img_path.stem + '.jpg'
                    new_path = img_path.parent / new_name
                    
                    # 如果目标文件已存在，添加编号
                    counter = 1
                    while new_path.exists():
                        new_name = f"{img_path.stem}_{counter}.jpg"
                        new_path = img_path.parent / new_name
                        counter += 1
                    
                    # 保存为 JPG
                    img.save(new_path, "JPEG", quality=95)
                    print(f"✓ Converted to {new_name}")
                    
                    # 删除原文件
                    img_path.unlink()
                    fixed_count += 1
                else:
                    print("✓ OK", flush=True)
                
            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}", flush=True)
                
                # 尝试使用 imageio 或其他库处理 AVIF
                try:
                    import imageio.v3 as iio
                    print(f"    Trying imageio ... ", end="", flush=True)
                    
                    # 读取图片
                    img_array = iio.imread(img_path)
                    
                    # 转换为 PIL Image
                    img = Image.fromarray(img_array)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 保存为 JPG
                    new_name = img_path.stem + '.jpg'
                    new_path = img_path.parent / new_name
                    
                    counter = 1
                    while new_path.exists():
                        new_name = f"{img_path.stem}_{counter}.jpg"
                        new_path = img_path.parent / new_name
                        counter += 1
                    
                    img.save(new_path, "JPEG", quality=95)
                    print(f"✓ Converted to {new_name}")
                    
                    # 删除原文件
                    img_path.unlink()
                    fixed_count += 1
                    
                except Exception as e2:
                    print(f"✗ Still failed: {str(e2)[:50]}")
                    error_count += 1
    
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"  ✓ Fixed/Converted: {fixed_count} files")
    print(f"  ✗ Failed: {error_count} files")
    print("="*60)
    
    if error_count > 0:
        print("\n💡 Tip: For failed files, you may need to:")
        print("   1. Install pillow-avif-plugin: pip install pillow-avif-plugin")
        print("   2. Or manually convert them using online tools")
        print("   3. Or simply remove them if not needed")

if __name__ == "__main__":
    print("="*60)
    print("Fabric Image Format Fixer")
    print("="*60)
    fix_images()

