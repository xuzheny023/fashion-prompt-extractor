# -*- coding: utf-8 -*-
"""
Train linear classification head on labeled patches.
在已标注的 patch 数据上训练线性分类头

Usage:
    python tools/clip_train.py

Input:
    data/patches/labeled/<label>/*.jpg
    
Output:
    data/clip_model.pkl
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
import joblib
import sys
from collections import Counter

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.linear_model import LogisticRegression
from src.clip_infer import image_to_emb

ROOT = Path("data/patches/labeled")
OUT = Path("data/clip_model.pkl")

def load_dataset():
    """
    Load labeled dataset from data/patches/labeled/.
    从 data/patches/labeled/ 加载已标注数据集
    
    Expected structure:
        data/patches/labeled/
            ├── cotton/
            │   ├── patch1.jpg
            │   └── patch2.png
            ├── silk/
            │   └── patch1.jpg
            └── ...
    
    Returns:
        X: numpy array of embeddings (N, D)
        y: numpy array of labels (N,)
    """
    X, y = [], []
    
    if not ROOT.exists():
        print(f"[ERROR] No labeled dataset found: {ROOT.resolve()}")
        print("Please create data/patches/labeled/<label>/ and add annotated images.")
        return np.array([]), np.array([])
    
    class_dirs = sorted([p for p in ROOT.iterdir() if p.is_dir()])
    
    if not class_dirs:
        print(f"[ERROR] No class directories found in {ROOT.resolve()}")
        print("Expected structure: data/patches/labeled/<label>/*.jpg")
        return np.array([]), np.array([])
    
    print(f"Loading dataset from {ROOT.resolve()}...\n")
    
    for cls_dir in class_dirs:
        label = cls_dir.name
        image_files = list(cls_dir.glob("*.*"))
        
        if not image_files:
            print(f"[WARN] {label}: No images found")
            continue
        
        print(f"[{label}] Processing {len(image_files)} images...")
        loaded_count = 0
        
        for img_p in image_files:
            # Skip JSON metadata files
            if img_p.suffix.lower() in ['.json', '.txt']:
                continue
                
            try:
                img = Image.open(img_p).convert("RGB")
                emb = image_to_emb(img)
                X.append(emb)
                y.append(label)
                loaded_count += 1
            except Exception as e:
                print(f"  [skip] {img_p.name}: {e}")
        
        print(f"  ✓ Loaded {loaded_count} samples for '{label}'")
    
    return np.array(X), np.array(y)

def train_and_save():
    """
    Train logistic regression classifier and save to disk.
    训练逻辑回归分类器并保存到磁盘
    """
    X, y = load_dataset()
    
    if len(X) == 0:
        print("\n[ERROR] No samples loaded. Cannot train model.")
        return
    
    if len(X) < 20:
        print(f"\n[WARN] Too few samples to train ({len(X)} samples).")
        print("Recommendation: Need at least 20 images for reliable training.")
        print("Continuing anyway for demonstration purposes...")
    
    # Display class distribution
    class_counts = Counter(y)
    print(f"\n{'='*60}")
    print("Class Distribution:")
    for label, count in sorted(class_counts.items()):
        print(f"  {label}: {count} samples")
    print(f"Total: {len(X)} samples, {len(class_counts)} classes")
    print(f"{'='*60}\n")
    
    # Train classifier
    print("Training LogisticRegression classifier...")
    clf = LogisticRegression(
        max_iter=2000, 
        n_jobs=-1, 
        multi_class="auto",
        random_state=42
    )
    clf.fit(X, y)
    
    # Ensure output directory exists
    OUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(clf, OUT)
    
    # Calculate train accuracy
    acc = clf.score(X, y)
    
    print(f"\n{'='*60}")
    print(f"✅ Saved linear head -> {OUT.resolve()}")
    print(f"   Model: LogisticRegression")
    print(f"   Classes: {len(clf.classes_)}")
    print(f"   Train-set accuracy: {acc:.2%}")
    print(f"   File size: {OUT.stat().st_size / 1024:.1f} KB")
    print(f"{'='*60}")
    
    # Display per-class accuracy
    if len(class_counts) <= 10:  # Only show for reasonable number of classes
        from sklearn.metrics import classification_report
        y_pred = clf.predict(X)
        print("\nPer-class metrics:")
        print(classification_report(y, y_pred, zero_division=0))

if __name__ == "__main__":
    print("Training CLIP linear classification head...\n")
    train_and_save()

