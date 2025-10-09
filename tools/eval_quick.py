# -*- coding: utf-8 -*-
"""
Quick evaluation tool for CLIP-based fabric retrieval.
CLIP 面料检索快速评估工具

Usage:
    python tools/eval_quick.py

Input:
    data/patches/labeled/<label>/*.jpg (test set)
    data/fabric_bank.npz (reference bank)
    data/clip_model.pkl (optional: linear head)
    
Output:
    Accuracy metrics and confusion matrix
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
import sys
from collections import defaultdict, Counter

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clip_infer import rank_by_retrieval, image_to_emb

ROOT = Path("data/patches/labeled")
BANK_PATH = Path("data/fabric_bank.npz")
MODEL_PATH = Path("data/clip_model.pkl")

def evaluate_retrieval(topk: int = 5):
    """
    Evaluate CLIP retrieval performance on labeled test set.
    在已标注测试集上评估 CLIP 检索性能
    
    Args:
        topk: Number of top results to consider / 考虑的 Top-K 结果数量
    """
    if not ROOT.exists():
        print(f"[ERROR] Test set not found: {ROOT.resolve()}")
        print("Please create data/patches/labeled/<label>/ with test images.")
        return
    
    if not BANK_PATH.exists():
        print(f"[ERROR] Fabric bank not found: {BANK_PATH.resolve()}")
        print("Please run: python tools/build_fabric_bank.py")
        return
    
    class_dirs = sorted([p for p in ROOT.iterdir() if p.is_dir()])
    
    if not class_dirs:
        print(f"[ERROR] No class directories found in {ROOT.resolve()}")
        return
    
    print(f"{'='*60}")
    print("CLIP Retrieval Evaluation")
    print(f"{'='*60}\n")
    print(f"Test set: {ROOT.resolve()}")
    print(f"Fabric bank: {BANK_PATH.resolve()}")
    print(f"Top-K: {topk}\n")
    
    # Metrics storage
    top1_correct = 0
    topk_correct = 0
    total_samples = 0
    
    class_metrics = defaultdict(lambda: {"correct": 0, "total": 0, "topk_correct": 0})
    confusion = defaultdict(Counter)
    
    print("Processing samples...\n")
    
    for cls_dir in class_dirs:
        label = cls_dir.name
        image_files = [
            p for p in cls_dir.glob("*.*") 
            if p.suffix.lower() in ['.jpg', '.jpeg', '.png']
        ]
        
        if not image_files:
            continue
        
        print(f"[{label}] Evaluating {len(image_files)} samples...")
        
        for img_p in image_files:
            try:
                img = Image.open(img_p).convert("RGB")
                results = rank_by_retrieval(img, topk=topk, bank_path=BANK_PATH)
                
                if not results:
                    print(f"  [WARN] No results for {img_p.name}")
                    continue
                
                # Top-1 prediction
                pred_top1 = results[0]["id"]
                
                # Top-K predictions
                pred_topk = [r["id"] for r in results]
                
                # Check correctness
                is_top1_correct = (pred_top1 == label)
                is_topk_correct = (label in pred_topk)
                
                total_samples += 1
                class_metrics[label]["total"] += 1
                
                if is_top1_correct:
                    top1_correct += 1
                    class_metrics[label]["correct"] += 1
                
                if is_topk_correct:
                    topk_correct += 1
                    class_metrics[label]["topk_correct"] += 1
                
                # Update confusion matrix
                confusion[label][pred_top1] += 1
                
            except Exception as e:
                print(f"  [ERROR] {img_p.name}: {e}")
    
    if total_samples == 0:
        print("\n[ERROR] No samples were successfully processed.")
        return
    
    # Calculate metrics
    top1_acc = top1_correct / total_samples
    topk_acc = topk_correct / total_samples
    
    print(f"\n{'='*60}")
    print("Overall Metrics")
    print(f"{'='*60}")
    print(f"Total samples: {total_samples}")
    print(f"Top-1 Accuracy: {top1_acc:.2%} ({top1_correct}/{total_samples})")
    print(f"Top-{topk} Accuracy: {topk_acc:.2%} ({topk_correct}/{total_samples})")
    
    # Per-class metrics
    print(f"\n{'='*60}")
    print("Per-Class Metrics")
    print(f"{'='*60}")
    print(f"{'Class':<20} {'Samples':<10} {'Top-1 Acc':<12} {'Top-{} Acc'.format(topk):<12}")
    print("-" * 60)
    
    for label in sorted(class_metrics.keys()):
        metrics = class_metrics[label]
        total = metrics["total"]
        correct = metrics["correct"]
        topk_correct_count = metrics["topk_correct"]
        
        acc = correct / total if total > 0 else 0
        topk_acc_class = topk_correct_count / total if total > 0 else 0
        
        print(f"{label:<20} {total:<10} {acc:<12.2%} {topk_acc_class:<12.2%}")
    
    # Confusion matrix (only if manageable size)
    if len(class_metrics) <= 10:
        print(f"\n{'='*60}")
        print("Confusion Matrix (True Label -> Top-1 Prediction)")
        print(f"{'='*60}")
        
        all_labels = sorted(class_metrics.keys())
        
        # Header
        header = "True \\ Pred"
        print(f"{header:<15}", end="")
        for pred_label in all_labels:
            print(f"{pred_label[:10]:<12}", end="")
        print()
        print("-" * (15 + 12 * len(all_labels)))
        
        # Rows
        for true_label in all_labels:
            print(f"{true_label:<15}", end="")
            for pred_label in all_labels:
                count = confusion[true_label][pred_label]
                print(f"{count:<12}", end="")
            print()
    
    print(f"\n{'='*60}")


def evaluate_linear_head():
    """
    Evaluate trained linear classification head (if exists).
    评估训练好的线性分类头（如果存在）
    """
    if not MODEL_PATH.exists():
        print(f"\n[INFO] Linear head not found: {MODEL_PATH.resolve()}")
        print("Skipping linear head evaluation.")
        print("To train: python tools/clip_train.py")
        return
    
    try:
        import joblib
        from sklearn.metrics import classification_report
        
        clf = joblib.load(MODEL_PATH)
        
        print(f"\n{'='*60}")
        print("Linear Head Evaluation")
        print(f"{'='*60}\n")
        print(f"Model: {MODEL_PATH.resolve()}")
        print(f"Classes: {len(clf.classes_)}")
        
        # Load test data
        X, y = [], []
        class_dirs = sorted([p for p in ROOT.iterdir() if p.is_dir()])
        
        for cls_dir in class_dirs:
            label = cls_dir.name
            image_files = [
                p for p in cls_dir.glob("*.*") 
                if p.suffix.lower() in ['.jpg', '.jpeg', '.png']
            ]
            
            for img_p in image_files:
                try:
                    img = Image.open(img_p).convert("RGB")
                    emb = image_to_emb(img)
                    X.append(emb)
                    y.append(label)
                except Exception:
                    pass
        
        if len(X) == 0:
            print("[ERROR] No test samples loaded.")
            return
        
        X = np.array(X)
        y = np.array(y)
        
        # Predict
        y_pred = clf.predict(X)
        acc = clf.score(X, y)
        
        print(f"\nTest set size: {len(X)} samples")
        print(f"Accuracy: {acc:.2%}\n")
        print("Classification Report:")
        print(classification_report(y, y_pred, zero_division=0))
        
    except Exception as e:
        print(f"[ERROR] Linear head evaluation failed: {e}")


if __name__ == "__main__":
    print("Starting quick evaluation...\n")
    
    # Evaluate retrieval
    evaluate_retrieval(topk=5)
    
    # Evaluate linear head (if available)
    evaluate_linear_head()
    
    print("\n✅ Evaluation complete.")

