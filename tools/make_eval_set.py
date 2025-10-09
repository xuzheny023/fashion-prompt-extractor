# -*- coding: utf-8 -*-
"""
Generate eval_set.jsonl from labeled patches.
从已标注的 patches 生成评估集

Usage:
    python tools/make_eval_set.py [--split 0.2] [--output data/eval_set.jsonl]

This tool will:
1. Scan data/patches/labeled/<label>/*.jpg
2. Randomly split images into train/test sets
3. Generate eval_set.jsonl with test samples
"""
from __future__ import annotations
import json
import argparse
from pathlib import Path
from collections import defaultdict
import random

ROOT = Path("data/patches/labeled")
DEFAULT_OUTPUT = Path("data/eval_set.jsonl")

def collect_labeled_images():
    """
    Collect all labeled images from data/patches/labeled/.
    收集所有已标注图像
    
    Returns:
        Dict mapping label -> list of image paths
    """
    if not ROOT.exists():
        print(f"[ERROR] Labeled data directory not found: {ROOT.resolve()}")
        return {}
    
    labeled = defaultdict(list)
    
    class_dirs = [p for p in ROOT.iterdir() if p.is_dir()]
    
    if not class_dirs:
        print(f"[ERROR] No class directories found in {ROOT.resolve()}")
        return {}
    
    for cls_dir in class_dirs:
        label = cls_dir.name
        image_files = [
            p for p in cls_dir.glob("*.*")
            if p.suffix.lower() in ['.jpg', '.jpeg', '.png']
        ]
        
        if image_files:
            labeled[label].extend(image_files)
            print(f"[{label}] Found {len(image_files)} images")
    
    return labeled

def make_eval_set(split_ratio=0.2, output=DEFAULT_OUTPUT, seed=42):
    """
    Generate evaluation set JSONL file.
    生成评估集 JSONL 文件
    
    Args:
        split_ratio: Ratio of test samples (0.0 - 1.0) / 测试集比例
        output: Output JSONL file path / 输出文件路径
        seed: Random seed for reproducibility / 随机种子
    """
    random.seed(seed)
    
    labeled = collect_labeled_images()
    
    if not labeled:
        print("\n[ERROR] No labeled images found. Cannot generate eval set.")
        return
    
    print(f"\n{'='*60}")
    print(f"Generating evaluation set (split ratio: {split_ratio:.0%})")
    print(f"{'='*60}\n")
    
    eval_samples = []
    
    for label, image_paths in sorted(labeled.items()):
        # Shuffle and split
        shuffled = list(image_paths)
        random.shuffle(shuffled)
        
        n_test = max(1, int(len(shuffled) * split_ratio))
        test_set = shuffled[:n_test]
        
        print(f"[{label}] Total: {len(shuffled)}, Test: {n_test}")
        
        # Generate JSONL entries
        for img_path in test_set:
            # Try to extract coords from JSON metadata if exists
            coords = [0, 0]  # Default coords
            json_path = img_path.with_suffix('.json')
            
            if json_path.exists():
                try:
                    metadata = json.loads(json_path.read_text(encoding='utf-8'))
                    if 'coords' in metadata:
                        coords = metadata['coords']
                    elif 'click_xy' in metadata:
                        coords = metadata['click_xy']
                except Exception:
                    pass
            
            eval_samples.append({
                "image": str(img_path),
                "coords": coords,
                "label": label
            })
    
    # Write JSONL
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with output.open('w', encoding='utf-8') as f:
        for sample in eval_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"\n{'='*60}")
    print(f"✅ Generated evaluation set -> {output.resolve()}")
    print(f"   Total samples: {len(eval_samples)}")
    print(f"   Classes: {len(labeled)}")
    print(f"   File size: {output.stat().st_size / 1024:.1f} KB")
    print(f"{'='*60}")
    
    # Show sample
    print("\nSample entries:")
    for sample in eval_samples[:3]:
        print(f"  {json.dumps(sample, ensure_ascii=False)}")
    if len(eval_samples) > 3:
        print(f"  ... and {len(eval_samples) - 3} more samples")

def main():
    parser = argparse.ArgumentParser(
        description="Generate eval_set.jsonl from labeled patches"
    )
    parser.add_argument(
        '--split', 
        type=float, 
        default=0.2,
        help='Test split ratio (default: 0.2 = 20%%)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default=str(DEFAULT_OUTPUT),
        help=f'Output JSONL file path (default: {DEFAULT_OUTPUT})'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    args = parser.parse_args()
    
    if args.split < 0 or args.split > 1:
        print("[ERROR] Split ratio must be between 0.0 and 1.0")
        return
    
    make_eval_set(
        split_ratio=args.split,
        output=Path(args.output),
        seed=args.seed
    )

if __name__ == "__main__":
    main()

