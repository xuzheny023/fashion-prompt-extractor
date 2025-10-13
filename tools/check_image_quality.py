# -*- coding: utf-8 -*-
"""
Fabric image quality checker
面料图片质量检查器
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
try:
    from tools._bootstrap import run_main_safely  # type: ignore
except Exception:
    run_main_safely = None

# 质量标准
MIN_WIDTH = 224
MIN_HEIGHT = 224
RECOMMENDED_WIDTH = 512
RECOMMENDED_HEIGHT = 512
MAX_FILE_SIZE_MB = 10

def check_image_quality(img_path: Path) -> dict:
    """
    检查单张图片质量
    
    返回检查结果字典
    """
    result = {
        'path': img_path,
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    try:
        img = Image.open(img_path)
        
        # 检查尺寸
        width, height = img.size
        result['size'] = (width, height)
        
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            result['errors'].append(f"Too small: {width}x{height} < {MIN_WIDTH}x{MIN_HEIGHT}")
            result['valid'] = False
        elif width < RECOMMENDED_WIDTH or height < RECOMMENDED_HEIGHT:
            result['warnings'].append(f"Small: {width}x{height} (recommended ≥{RECOMMENDED_WIDTH}x{RECOMMENDED_HEIGHT})")
        
        # 检查文件大小
        file_size_mb = img_path.stat().st_size / 1024 / 1024
        result['file_size_mb'] = file_size_mb
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            result['warnings'].append(f"Large file: {file_size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB")
        
        # 检查图片模式
        result['mode'] = img.mode
        if img.mode not in ['RGB', 'L']:
            result['warnings'].append(f"Unusual mode: {img.mode}")
        
        # 检查图片是否太暗或太亮
        if img.mode in ['RGB', 'L']:
            img_array = np.array(img.convert('L'))
            mean_brightness = img_array.mean()
            result['brightness'] = mean_brightness
            
            if mean_brightness < 30:
                result['warnings'].append(f"Too dark: brightness {mean_brightness:.0f}/255")
            elif mean_brightness > 225:
                result['warnings'].append(f"Too bright: brightness {mean_brightness:.0f}/255")
        
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Cannot open: {str(e)[:50]}")
    
    return result

def _gather_images_recursive(fabric_dir: Path):
    patterns = ("**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.JPG", "**/*.PNG", "**/*.JPEG")
    image_files = []
    for pat in patterns:
        image_files.extend(fabric_dir.glob(pat))
    return image_files


def check_all_fabrics(progress: bool = False):
    """检查所有面料图片质量"""
    fabrics_dir = Path("data/fabrics")
    fabric_dirs = sorted([d for d in fabrics_dir.iterdir() if d.is_dir()])
    
    print("="*70)
    print("Fabric Image Quality Check")
    print("="*70)
    print(f"\nQuality Standards:")
    print(f"  • Minimum size: {MIN_WIDTH}x{MIN_HEIGHT}")
    print(f"  • Recommended: {RECOMMENDED_WIDTH}x{RECOMMENDED_HEIGHT}")
    print(f"  • Max file size: {MAX_FILE_SIZE_MB}MB")
    print("="*70)
    
    total_images = 0
    valid_images = 0
    error_images = 0
    warning_images = 0
    grand_total = 0
    per_dir_files = {}

    # 预统计总数以便进度展示
    if progress:
        for fabric_dir in fabric_dirs:
            files = _gather_images_recursive(fabric_dir)
            per_dir_files[fabric_dir] = files
            grand_total += len(files)
    
    for fabric_dir in fabric_dirs:
        # 递归扫描子目录中的图片
        if progress:
            image_files = per_dir_files.get(fabric_dir, [])
        else:
            image_files = _gather_images_recursive(fabric_dir)
        
        if not image_files:
            continue
        
        print(f"\n[{fabric_dir.name}] - {len(image_files)} images")
        
        for img_path in image_files:
            total_images += 1
            result = check_image_quality(img_path)
            
            status = "✓"
            if result['errors']:
                status = "✗"
                error_images += 1
            elif result['warnings']:
                status = "⚠"
                warning_images += 1
            else:
                valid_images += 1
            
            # 显示结果
            size_str = f"{result.get('size', ('?', '?'))[0]}x{result.get('size', ('?', '?'))[1]}"
            size_mb = result.get('file_size_mb', 0)
            
            prefix = f"[{total_images}/{grand_total}] " if progress and grand_total > 0 else "  "
            print(f"{prefix}{status} {img_path.name:<30} {size_str:<12} {size_mb:>5.1f}MB", end="")
            
            if result['errors']:
                print(f"  ✗ {'; '.join(result['errors'])}")
            elif result['warnings']:
                print(f"  ⚠ {'; '.join(result['warnings'])}")
            else:
                print()
    
    print("\n" + "="*70)
    print("Summary:")
    print(f"  ✓ Valid:    {valid_images:>4} ({valid_images/total_images*100:.1f}%)")
    print(f"  ⚠ Warning:  {warning_images:>4} ({warning_images/total_images*100:.1f}%)")
    print(f"  ✗ Error:    {error_images:>4} ({error_images/total_images*100:.1f}%)")
    print(f"  📊 Total:   {total_images:>4}")
    print("="*70)
    
    if error_images > 0:
        print("\n💡 Tip: Remove or replace error images before building fabric bank")

def check_single_fabric(fabric_name: str, progress: bool = False):
    """检查单个面料类别的图片质量"""
    fabric_dir = Path(f"data/fabrics/{fabric_name}")
    
    if not fabric_dir.exists():
        print(f"✗ Fabric category not found: {fabric_name}")
        return
    
    image_files = _gather_images_recursive(fabric_dir)
    
    if not image_files:
        print(f"✗ No images found in {fabric_dir}")
        return
    
    print(f"\n[{fabric_name}] Quality Check - {len(image_files)} images\n")
    
    for idx, img_path in enumerate(image_files, 1):
        result = check_image_quality(img_path)
        
        status = "✓" if result['valid'] and not result['warnings'] else "⚠" if result['valid'] else "✗"

        prefix = f"[{idx}/{len(image_files)}] " if progress else ""
        print(f"{prefix}{status} {img_path.name}")
        if result.get('size'):
            print(f"   Size: {result['size'][0]}x{result['size'][1]}")
        if result.get('file_size_mb'):
            print(f"   File: {result['file_size_mb']:.1f}MB")
        if result.get('brightness'):
            print(f"   Brightness: {result['brightness']:.0f}/255")
        
        if result['errors']:
            for err in result['errors']:
                print(f"   ✗ {err}")
        if result['warnings']:
            for warn in result['warnings']:
                print(f"   ⚠ {warn}")
        print()

if __name__ == "__main__":
    import sys

    def _cli():
        args = sys.argv[1:]
        progress_flag = False
        non_flags = []
        for a in args:
            if a.startswith('-'):
                if a in ("--progress", "-p"):
                    progress_flag = True
            else:
                non_flags.append(a)

        if non_flags:
            check_single_fabric(non_flags[0], progress=progress_flag)
        else:
            check_all_fabrics(progress=progress_flag)
        return 0

    if run_main_safely:
        raise SystemExit(run_main_safely(_cli))
    sys.exit(_cli())

