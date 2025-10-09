# -*- coding: utf-8 -*-
"""
Quick evaluation using JSONL test set.
使用 JSONL 测试集快速评估

Usage:
    python tools/eval_quick.py

Input:
    data/eval_set.jsonl - Each line: {"image":"path","coords":[x,y],"label":"fabric_id"}
    
Output:
    Top@1 and Top@3 accuracy metrics
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clip_infer import rank_by_retrieval

EVAL = Path("data/eval_set.jsonl")

def eval_clip_only(topk=5):
    """
    Evaluate CLIP retrieval using JSONL test set.
    使用 JSONL 测试集评估 CLIP 检索
    
    Args:
        topk: Number of top results to retrieve / 检索结果数量
    """
    if not EVAL.exists():
        print(f"[ERROR] Evaluation set not found: {EVAL.resolve()}")
        print("\nExpected format (JSONL):")
        print('{"image":"path/to/image.jpg","coords":[x,y],"label":"cotton"}')
        print('{"image":"path/to/image2.jpg","coords":[x,y],"label":"silk"}')
        print("...")
        return
    
    print(f"{'='*60}")
    print("CLIP Retrieval Evaluation (JSONL)")
    print(f"{'='*60}\n")
    print(f"Eval set: {EVAL.resolve()}")
    print(f"Top-K: {topk}\n")
    
    # Load test set
    try:
        lines = [
            json.loads(line) 
            for line in EVAL.read_text(encoding="utf-8").strip().splitlines()
            if line.strip()
        ]
    except Exception as e:
        print(f"[ERROR] Failed to parse JSONL: {e}")
        return
    
    if not lines:
        print("[ERROR] Evaluation set is empty.")
        return
    
    print(f"Processing {len(lines)} samples...\n")
    
    top1 = 0
    top3 = 0
    errors = []
    
    for idx, record in enumerate(lines, 1):
        try:
            # Load image
            img_path = record.get("image")
            if not img_path:
                errors.append(f"Line {idx}: Missing 'image' field")
                continue
            
            img = Image.open(img_path).convert("RGB")
            
            # Note: coords are provided but not used in this simple version
            # If you have patch extraction function, you can use coords to crop
            # coords = record.get("coords", [None, None])
            
            # Get ground truth label
            label = record.get("label")
            if not label:
                errors.append(f"Line {idx}: Missing 'label' field")
                continue
            
            # Retrieve recommendations
            recs = rank_by_retrieval(img, topk=topk)
            
            if not recs:
                errors.append(f"Line {idx}: No recommendations returned")
                continue
            
            # Extract predicted IDs
            ids = [x["id"] for x in recs]
            
            # Check accuracy
            if ids and label == ids[0]:
                top1 += 1
            if label in ids[:3]:
                top3 += 1
            
            # Progress indicator
            if idx % 10 == 0:
                print(f"Processed {idx}/{len(lines)} samples...")
                
        except FileNotFoundError as e:
            errors.append(f"Line {idx}: Image not found - {img_path}")
        except Exception as e:
            errors.append(f"Line {idx}: {str(e)}")
    
    # Calculate metrics
    n = len(lines) - len(errors)
    
    if n == 0:
        print("\n[ERROR] No samples were successfully processed.")
        if errors:
            print("\nErrors encountered:")
            for err in errors[:10]:  # Show first 10 errors
                print(f"  - {err}")
        return
    
    top1_acc = top1 / n
    top3_acc = top3 / n
    
    print(f"\n{'='*60}")
    print("Results")
    print(f"{'='*60}")
    print(f"Total samples: {len(lines)}")
    print(f"Successfully processed: {n}")
    print(f"Errors: {len(errors)}")
    print(f"\nTop@1 Accuracy: {top1_acc:.2%} ({top1}/{n})")
    print(f"Top@3 Accuracy: {top3_acc:.2%} ({top3}/{n})")
    print(f"{'='*60}")
    
    # Show errors if any
    if errors:
        print(f"\n⚠️  {len(errors)} errors encountered:")
        for err in errors[:5]:  # Show first 5 errors
            print(f"  - {err}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")


if __name__ == "__main__":
    print("Starting CLIP evaluation...\n")
    eval_clip_only(topk=5)
    print("\n✅ Evaluation complete.")
