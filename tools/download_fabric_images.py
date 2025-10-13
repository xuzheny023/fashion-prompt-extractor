# -*- coding: utf-8 -*-
"""
Fabric image downloader - Download reference images from URLs
面料图片下载器 - 从URL批量下载参考图片
"""
from __future__ import annotations
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO
import time

def download_image(url: str, save_path: Path, timeout: int = 10) -> bool:
    """
    从URL下载图片并保存
    
    Args:
        url: 图片URL
        save_path: 保存路径
        timeout: 超时时间（秒）
    
    Returns:
        是否成功
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # 验证是否为有效图片
        img = Image.open(BytesIO(response.content))
        img.verify()
        
        # 重新打开并转换为RGB
        img = Image.open(BytesIO(response.content)).convert('RGB')
        
        # 保存为JPG
        img.save(save_path, 'JPEG', quality=95)
        return True
        
    except Exception as e:
        print(f"    ✗ Failed: {str(e)[:60]}")
        return False

def download_from_urls_file(fabric_name: str, urls_file: Path = None):
    """
    从URL列表文件下载图片
    
    文件格式（每行一个URL）：
    https://example.com/image1.jpg
    https://example.com/image2.jpg
    """
    if urls_file is None:
        urls_file = Path(f"data/fabrics/{fabric_name}/urls.txt")
    
    if not urls_file.exists():
        print(f"✗ URLs file not found: {urls_file}")
        return
    
    fabric_dir = Path(f"data/fabrics/{fabric_name}")
    fabric_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取URL列表
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"\n[{fabric_name}] Downloading {len(urls)} images...")
    
    success = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        # 生成文件名
        save_path = fabric_dir / f"{fabric_name}_{i:03d}.jpg"
        
        # 如果已存在则跳过
        if save_path.exists():
            print(f"  [{i}/{len(urls)}] Skipped (already exists)")
            success += 1
            continue
        
        print(f"  [{i}/{len(urls)}] Downloading from {url[:50]}... ", end="", flush=True)
        
        if download_image(url, save_path):
            print("✓")
            success += 1
        else:
            failed += 1
        
        # 避免请求过快
        time.sleep(0.5)
    
    print(f"\n  Summary: ✓ {success} success, ✗ {failed} failed")
    return success, failed

def batch_download():
    """批量下载所有有urls.txt的面料类别"""
    fabrics_dir = Path("data/fabrics")
    
    print("="*60)
    print("Batch Fabric Image Downloader")
    print("="*60)
    
    # 查找所有有urls.txt的类别
    url_files = list(fabrics_dir.glob("*/urls.txt"))
    
    if not url_files:
        print("\n✗ No urls.txt files found in fabric directories")
        print("\n💡 Usage:")
        print("   1. Create urls.txt in each fabric folder:")
        print("      data/fabrics/denim/urls.txt")
        print("      data/fabrics/silk/urls.txt")
        print("   2. Add image URLs (one per line)")
        print("   3. Run this script")
        return
    
    print(f"\nFound {len(url_files)} fabric categories with URLs")
    
    total_success = 0
    total_failed = 0
    
    for url_file in sorted(url_files):
        fabric_name = url_file.parent.name
        success, failed = download_from_urls_file(fabric_name, url_file)
        total_success += success
        total_failed += failed
    
    print("\n" + "="*60)
    print(f"Total: ✓ {total_success} downloaded, ✗ {total_failed} failed")
    print("="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 下载单个类别
        fabric_name = sys.argv[1]
        download_from_urls_file(fabric_name)
    else:
        # 批量下载
        batch_download()


