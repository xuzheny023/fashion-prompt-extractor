# -*- coding: utf-8 -*-
"""
命令行评测工具

自动评测面料识别准确率和性能

用法:
    python tools/eval_cli.py --dir eval_set
    python tools/eval_cli.py --dir eval_set --top-k 5
    python tools/eval_cli.py --dir eval_set --output logs/my_eval.csv
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import time
from typing import List, Dict, Tuple
import csv
from datetime import datetime
from PIL import Image
import numpy as np
from tqdm import tqdm

from src.core.recommender import recommend
from src.utils.logger import get_logger

log = get_logger("eval_cli")


def load_eval_dataset(eval_dir: Path) -> Dict[str, List[Path]]:
    """
    加载评测数据集
    
    目录结构：
        eval_dir/
        ├── cotton/
        │   ├── img1.jpg
        │   ├── img2.jpg
        │   └── ...
        ├── linen/
        │   └── ...
        └── ...
    
    Args:
        eval_dir: 评测数据集目录
    
    Returns:
        {label: [image_paths]}
    """
    if not eval_dir.exists():
        log.error(f"评测目录不存在: {eval_dir}")
        raise FileNotFoundError(f"评测目录不存在: {eval_dir}")
    
    dataset = {}
    
    # 遍历每个类别目录
    for label_dir in eval_dir.iterdir():
        if not label_dir.is_dir():
            continue
        
        label = label_dir.name
        
        # 收集该类别的所有图片
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            images.extend(label_dir.glob(f"*{ext}"))
            images.extend(label_dir.glob(f"*{ext.upper()}"))
        
        if images:
            dataset[label] = sorted(images)
            log.info(f"类别 {label}: {len(images)} 张图片")
    
    if not dataset:
        log.error(f"未找到任何图片: {eval_dir}")
        raise ValueError(f"未找到任何图片: {eval_dir}")
    
    total_images = sum(len(imgs) for imgs in dataset.values())
    log.info(f"总计: {len(dataset)} 个类别, {total_images} 张图片")
    
    return dataset


def evaluate_image(
    image_path: Path,
    ground_truth: str,
    top_k: int = 5
) -> Tuple[Dict, float]:
    """
    评测单张图片
    
    Args:
        image_path: 图片路径
        ground_truth: 真实标签
        top_k: 返回前 K 个结果
    
    Returns:
        result_dict: 评测结果字典
        elapsed_ms: 耗时（毫秒）
    """
    try:
        # 加载图片
        img = Image.open(image_path).convert("RGB")
        
        # 推荐
        t0 = time.perf_counter()
        result, meta = recommend(img, top_k=top_k, lang="en")
        elapsed_ms = (time.perf_counter() - t0) * 1000
        
        # 提取预测结果
        predictions = [item.label for item in result.items]
        scores = [item.score for item in result.items]
        
        # 判断准确性
        top1_correct = predictions[0] == ground_truth if predictions else False
        top3_correct = ground_truth in predictions[:3] if len(predictions) >= 3 else False
        top5_correct = ground_truth in predictions[:5] if len(predictions) >= 5 else False
        
        result_dict = {
            'image': image_path.name,
            'ground_truth': ground_truth,
            'top1_pred': predictions[0] if predictions else 'N/A',
            'top1_score': scores[0] if scores else 0.0,
            'top3_preds': ','.join(predictions[:3]),
            'top5_preds': ','.join(predictions[:5]),
            'top1_correct': top1_correct,
            'top3_correct': top3_correct,
            'top5_correct': top5_correct,
            'time_ms': elapsed_ms,
            'coarse_max': meta.coarse_max,
            'ai_reason': result.ai_reason
        }
        
        return result_dict, elapsed_ms
        
    except Exception as e:
        log.error(f"评测失败 {image_path}: {e}")
        return {
            'image': image_path.name,
            'ground_truth': ground_truth,
            'top1_pred': 'ERROR',
            'top1_score': 0.0,
            'top3_preds': '',
            'top5_preds': '',
            'top1_correct': False,
            'top3_correct': False,
            'top5_correct': False,
            'time_ms': 0.0,
            'coarse_max': 0.0,
            'ai_reason': str(e)
        }, 0.0


def evaluate_dataset(
    dataset: Dict[str, List[Path]],
    top_k: int = 5,
    output_csv: Path = None
) -> Dict:
    """
    评测整个数据集
    
    Args:
        dataset: {label: [image_paths]}
        top_k: 返回前 K 个结果
        output_csv: 输出 CSV 路径
    
    Returns:
        统计结果字典
    """
    all_results = []
    all_times = []
    
    # 按类别统计
    class_stats = {label: {'total': 0, 'top1': 0, 'top3': 0, 'top5': 0} 
                   for label in dataset.keys()}
    
    # 计算总图片数
    total_images = sum(len(imgs) for imgs in dataset.values())
    
    # 创建进度条
    pbar = tqdm(total=total_images, desc="评测进度", unit="img")
    
    # 遍历每个类别
    for label, image_paths in dataset.items():
        log.info(f"\n评测类别: {label} ({len(image_paths)} 张)")
        
        for img_path in image_paths:
            result_dict, elapsed_ms = evaluate_image(img_path, label, top_k)
            
            all_results.append(result_dict)
            all_times.append(elapsed_ms)
            
            # 更新统计
            class_stats[label]['total'] += 1
            if result_dict['top1_correct']:
                class_stats[label]['top1'] += 1
            if result_dict['top3_correct']:
                class_stats[label]['top3'] += 1
            if result_dict['top5_correct']:
                class_stats[label]['top5'] += 1
            
            pbar.update(1)
    
    pbar.close()
    
    # 保存详细结果到 CSV
    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'image', 'ground_truth', 'top1_pred', 'top1_score',
                'top3_preds', 'top5_preds', 'top1_correct', 'top3_correct',
                'top5_correct', 'time_ms', 'coarse_max', 'ai_reason'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        log.info(f"详细结果已保存: {output_csv}")
    
    # 计算整体统计
    total_correct_top1 = sum(1 for r in all_results if r['top1_correct'])
    total_correct_top3 = sum(1 for r in all_results if r['top3_correct'])
    total_correct_top5 = sum(1 for r in all_results if r['top5_correct'])
    
    overall_stats = {
        'total_images': len(all_results),
        'total_classes': len(dataset),
        'top1_accuracy': total_correct_top1 / len(all_results) if all_results else 0,
        'top3_accuracy': total_correct_top3 / len(all_results) if all_results else 0,
        'top5_accuracy': total_correct_top5 / len(all_results) if all_results else 0,
        'class_stats': class_stats,
        'time_stats': {
            'mean': np.mean(all_times) if all_times else 0,
            'median': np.median(all_times) if all_times else 0,
            'p50': np.percentile(all_times, 50) if all_times else 0,
            'p95': np.percentile(all_times, 95) if all_times else 0,
            'p99': np.percentile(all_times, 99) if all_times else 0,
            'min': np.min(all_times) if all_times else 0,
            'max': np.max(all_times) if all_times else 0,
        }
    }
    
    return overall_stats


def print_report(stats: Dict):
    """打印评测报告"""
    
    print("\n" + "=" * 70)
    print("评测报告")
    print("=" * 70)
    
    # 整体准确率
    print("\n📊 整体准确率:")
    print(f"  总图片数: {stats['total_images']}")
    print(f"  总类别数: {stats['total_classes']}")
    print(f"  Top-1 准确率: {stats['top1_accuracy']:.2%} ({int(stats['top1_accuracy'] * stats['total_images'])}/{stats['total_images']})")
    print(f"  Top-3 准确率: {stats['top3_accuracy']:.2%} ({int(stats['top3_accuracy'] * stats['total_images'])}/{stats['total_images']})")
    print(f"  Top-5 准确率: {stats['top5_accuracy']:.2%} ({int(stats['top5_accuracy'] * stats['total_images'])}/{stats['total_images']})")
    
    # 按类别准确率
    print("\n📋 按类别准确率:")
    print(f"{'类别':<20} {'总数':>6} {'Top-1':>8} {'Top-3':>8} {'Top-5':>8}")
    print("-" * 70)
    
    for label, class_stat in sorted(stats['class_stats'].items()):
        total = class_stat['total']
        top1 = class_stat['top1']
        top3 = class_stat['top3']
        top5 = class_stat['top5']
        
        top1_acc = top1 / total if total > 0 else 0
        top3_acc = top3 / total if total > 0 else 0
        top5_acc = top5 / total if total > 0 else 0
        
        print(f"{label:<20} {total:>6} {top1_acc:>7.1%} {top3_acc:>7.1%} {top5_acc:>7.1%}")
    
    # 耗时统计
    print("\n⏱️  耗时统计 (ms):")
    time_stats = stats['time_stats']
    print(f"  平均值: {time_stats['mean']:.1f} ms")
    print(f"  中位数: {time_stats['median']:.1f} ms")
    print(f"  P50: {time_stats['p50']:.1f} ms")
    print(f"  P95: {time_stats['p95']:.1f} ms")
    print(f"  P99: {time_stats['p99']:.1f} ms")
    print(f"  最小值: {time_stats['min']:.1f} ms")
    print(f"  最大值: {time_stats['max']:.1f} ms")
    
    # 性能评估
    print("\n🎯 性能评估:")
    if time_stats['p95'] < 500:
        print("  ✅ 优秀 - P95 < 500ms")
    elif time_stats['p95'] < 1000:
        print("  ✓ 良好 - P95 < 1000ms")
    else:
        print("  ⚠️  需要优化 - P95 >= 1000ms")
    
    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="面料识别评测工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/eval_cli.py --dir eval_set
  python tools/eval_cli.py --dir eval_set --top-k 5
  python tools/eval_cli.py --dir eval_set --output logs/my_eval.csv
        """
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        required=True,
        help='评测数据集目录（结构：dir/<label>/*.jpg）'
    )
    
    parser.add_argument(
        '--top-k',
        type=int,
        default=5,
        help='返回前 K 个结果（默认 5）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='logs/eval_report.csv',
        help='输出 CSV 路径（默认 logs/eval_report.csv）'
    )
    
    args = parser.parse_args()
    
    # 转换路径
    eval_dir = Path(args.dir)
    output_csv = Path(args.output)
    
    print("=" * 70)
    print("面料识别评测工具")
    print("=" * 70)
    print(f"\n配置:")
    print(f"  评测目录: {eval_dir}")
    print(f"  Top-K: {args.top_k}")
    print(f"  输出文件: {output_csv}")
    print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 加载数据集
        print("\n[1/3] 加载数据集...")
        dataset = load_eval_dataset(eval_dir)
        
        # 2. 评测
        print("\n[2/3] 开始评测...")
        stats = evaluate_dataset(dataset, top_k=args.top_k, output_csv=output_csv)
        
        # 3. 打印报告
        print("\n[3/3] 生成报告...")
        print_report(stats)
        
        print(f"\n✅ 评测完成！")
        print(f"详细结果: {output_csv.resolve()}")
        
        return 0
        
    except Exception as e:
        log.exception("评测失败")
        print(f"\n❌ 评测失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

