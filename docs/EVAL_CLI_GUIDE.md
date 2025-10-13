# 命令行评测工具指南

## 📦 概述

`tools/eval_cli.py` 是一个自动化评测工具，用于评估面料识别模型的准确率和性能。

**特性：**
- ✅ 自动批量评测
- ✅ Top-1 / Top-3 / Top-5 准确率统计
- ✅ 按类别准确率分析
- ✅ 耗时分布统计（P50/P95/P99）
- ✅ 详细结果导出（CSV）

---

## 🚀 快速开始

### 基本用法

```bash
python tools/eval_cli.py --dir eval_set
```

### 完整参数

```bash
python tools/eval_cli.py \
    --dir eval_set \
    --top-k 5 \
    --output logs/eval_report.csv
```

---

## 📁 数据集格式

### 目录结构

```
eval_set/
├── cotton/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── linen/
│   ├── img1.jpg
│   └── ...
├── silk/
│   └── ...
└── ...
```

**要求：**
- 每个子目录名称为类别标签
- 支持 `.jpg`, `.jpeg`, `.png`, `.webp` 格式
- 图片文件名任意

---

## 📊 输出报告

### 控制台输出

```
======================================================================
评测报告
======================================================================

📊 整体准确率:
  总图片数: 22
  总类别数: 3
  Top-1 准确率: 72.73% (16/22)
  Top-3 准确率: 90.91% (20/22)
  Top-5 准确率: 95.45% (21/22)

📋 按类别准确率:
类别                  总数   Top-1   Top-3   Top-5
----------------------------------------------------------------------
cotton                  6    83.3%  100.0%  100.0%
linen                   8    75.0%   87.5%   87.5%
silk                    8    62.5%   87.5%  100.0%

⏱️  耗时统计 (ms):
  平均值: 185.3 ms
  中位数: 178.5 ms
  P50: 178.5 ms
  P95: 245.2 ms
  P99: 268.9 ms
  最小值: 152.3 ms
  最大值: 289.4 ms

🎯 性能评估:
  ✅ 优秀 - P95 < 500ms

======================================================================
```

### CSV 文件

**路径:** `logs/eval_report.csv`

**字段：**
- `image` - 图片文件名
- `ground_truth` - 真实标签
- `top1_pred` - Top-1 预测
- `top1_score` - Top-1 分数
- `top3_preds` - Top-3 预测（逗号分隔）
- `top5_preds` - Top-5 预测（逗号分隔）
- `top1_correct` - Top-1 是否正确
- `top3_correct` - Top-3 是否正确
- `top5_correct` - Top-5 是否正确
- `time_ms` - 耗时（毫秒）
- `coarse_max` - 粗排最高分
- `ai_reason` - AI 推理方式

**示例：**
```csv
image,ground_truth,top1_pred,top1_score,top3_preds,top5_preds,top1_correct,top3_correct,top5_correct,time_ms,coarse_max,ai_reason
img1.jpg,cotton,cotton,0.89,cotton,linen,silk,True,True,True,185.3,0.92,CLIP 双通道向量检索
img2.jpg,linen,linen,0.76,linen,cotton,silk,True,True,True,178.5,0.88,CLIP 双通道向量检索
...
```

---

## 🎯 参数说明

### --dir (必需)

评测数据集目录路径

```bash
--dir eval_set
--dir /path/to/dataset
```

### --top-k (可选)

返回前 K 个结果，默认 5

```bash
--top-k 3   # 只返回前 3 个
--top-k 10  # 返回前 10 个
```

### --output (可选)

输出 CSV 文件路径，默认 `logs/eval_report.csv`

```bash
--output logs/my_eval.csv
--output results/eval_$(date +%Y%m%d).csv
```

---

## 📈 评测指标

### 准确率指标

#### Top-1 准确率
预测的第 1 名是否正确

```
Top-1 Accuracy = (Top-1 正确数) / (总图片数)
```

#### Top-3 准确率
真实标签是否在预测的前 3 名中

```
Top-3 Accuracy = (Top-3 正确数) / (总图片数)
```

#### Top-5 准确率
真实标签是否在预测的前 5 名中

```
Top-5 Accuracy = (Top-5 正确数) / (总图片数)
```

### 性能指标

#### 耗时统计

- **平均值 (Mean)** - 所有图片的平均耗时
- **中位数 (Median)** - 中间值
- **P50** - 50% 的图片耗时 ≤ 此值
- **P95** - 95% 的图片耗时 ≤ 此值
- **P99** - 99% 的图片耗时 ≤ 此值

#### 性能评级

| P95 耗时 | 评级 |
|----------|------|
| < 500ms | ✅ 优秀 |
| < 1000ms | ✓ 良好 |
| ≥ 1000ms | ⚠️ 需要优化 |

---

## 🧪 使用示例

### 示例1: 基本评测

```bash
# 评测 eval_set 目录
python tools/eval_cli.py --dir eval_set
```

**输出：**
- 控制台报告
- `logs/eval_report.csv`

### 示例2: 自定义输出

```bash
# 指定输出文件
python tools/eval_cli.py \
    --dir eval_set \
    --output results/eval_20251013.csv
```

### 示例3: 只看 Top-3

```bash
# 只返回前 3 个结果
python tools/eval_cli.py \
    --dir eval_set \
    --top-k 3
```

### 示例4: 批量评测

```bash
# 评测多个数据集
for dataset in eval_set_v1 eval_set_v2 eval_set_v3; do
    python tools/eval_cli.py \
        --dir $dataset \
        --output logs/eval_$dataset.csv
done
```

---

## 📊 结果分析

### 使用 Python 分析

```python
import pandas as pd

# 读取结果
df = pd.read_csv('logs/eval_report.csv')

# 整体准确率
top1_acc = df['top1_correct'].mean()
top3_acc = df['top3_correct'].mean()

print(f"Top-1: {top1_acc:.2%}")
print(f"Top-3: {top3_acc:.2%}")

# 按类别统计
class_stats = df.groupby('ground_truth').agg({
    'top1_correct': 'mean',
    'top3_correct': 'mean',
    'time_ms': 'mean'
})

print(class_stats)

# 找出错误案例
errors = df[df['top1_correct'] == False]
print(f"错误案例: {len(errors)}")
print(errors[['image', 'ground_truth', 'top1_pred', 'top1_score']])
```

### 使用 Excel 分析

1. 打开 `logs/eval_report.csv`
2. 插入数据透视表
3. 按 `ground_truth` 分组
4. 计算 `top1_correct` 的平均值

---

## 🔧 故障排查

### 问题1: 找不到图片

```
❌ 评测失败: 未找到任何图片: eval_set
```

**解决：**
- 检查目录路径是否正确
- 确保子目录中有图片文件
- 检查图片格式（支持 jpg/png/webp）

### 问题2: 向量库不存在

```
❌ 向量库未找到: data/fabric_bank.npz
```

**解决：**
```bash
python tools/build_fabric_bank.py
```

### 问题3: 内存不足

**症状：** 评测大数据集时内存溢出

**解决：**
- 分批评测
- 减少 `--top-k` 参数
- 使用更小的图片

### 问题4: 评测速度慢

**症状：** P95 > 1000ms

**解决：**
```bash
# 1. 安装 FAISS
pip install faiss-cpu

# 2. 启用 FAISS
# .env
ENABLE_FAISS=true

# 3. 减少 TOPC
TOPC=8
```

---

## 📝 最佳实践

### 1. 数据集准备

- ✅ 每个类别至少 10 张图片
- ✅ 图片质量清晰
- ✅ 类别分布均衡
- ✅ 包含多样化样本

### 2. 评测流程

```bash
# 1. 准备数据集
mkdir -p eval_set
# 复制图片到对应类别目录

# 2. 运行评测
python tools/eval_cli.py --dir eval_set

# 3. 分析结果
python tools/analyze_eval.py logs/eval_report.csv

# 4. 改进模型
# 根据错误案例调整训练数据
```

### 3. 持续评测

```bash
# 定期评测（cron job）
0 2 * * * cd /path/to/project && \
    python tools/eval_cli.py --dir eval_set \
    --output logs/eval_$(date +\%Y\%m\%d).csv
```

---

## 🎓 进阶用法

### 自定义评测脚本

```python
from tools.eval_cli import load_eval_dataset, evaluate_dataset

# 加载数据集
dataset = load_eval_dataset(Path("eval_set"))

# 评测
stats = evaluate_dataset(
    dataset,
    top_k=5,
    output_csv=Path("my_eval.csv")
)

# 自定义分析
print(f"Top-1: {stats['top1_accuracy']:.2%}")
print(f"P95: {stats['time_stats']['p95']:.1f}ms")
```

### 集成到 CI/CD

```yaml
# .github/workflows/eval.yml
name: Model Evaluation

on:
  push:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run evaluation
        run: python tools/eval_cli.py --dir eval_set
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: eval-report
          path: logs/eval_report.csv
```

---

## 📚 相关文档

- [推荐引擎](./RECOMMENDER_GUIDE.md)
- [数据类型](./TYPES_GUIDE.md)
- [性能优化](../PERFORMANCE_OPTIMIZATION.md)

---

## 💡 提示

- 📊 定期评测以监控模型性能
- 🔍 分析错误案例以改进模型
- ⚡ 关注 P95 耗时以优化性能
- 📈 跟踪准确率趋势以评估改进效果

---

✅ **评测工具已就绪！** 现在可以自动评测模型性能。 🎉

