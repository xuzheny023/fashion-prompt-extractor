# CLIP 检索系统使用指南

## 📋 快速开始

### 1️⃣ 准备参考图像库

将面料参考图像按以下结构组织：

```
data/fabrics/
├── cotton/
│   ├── ref1.jpg
│   ├── ref2.jpg
│   └── ref3.png
├── silk_satin/
│   ├── sample1.jpg
│   └── sample2.jpeg
├── wool/
│   └── reference.jpg
└── ...
```

**要求：**
- 每个面料至少 3-5 张参考图像
- 图像格式：JPG、JPEG、PNG
- 建议分辨率：224x224 以上
- 质量优先于数量

### 2️⃣ 构建面料向量库

```bash
venv\Scripts\python.exe tools\build_fabric_bank.py
```

**输出：**
- `data/fabric_bank.npz` - 压缩的 CLIP 嵌入向量库

**预期输出示例：**
```
Building fabric reference bank...

  [cotton] Processed: ref1.jpg
  [cotton] Processed: ref2.jpg
[OK] cotton: 2 images -> shape (2, 512)
...

============================================================
✅ Saved fabric bank -> D:\...\data\fabric_bank.npz
   Total fabrics: 5
   Total images: 15
   File size: 18.3 KB
============================================================
```

### 3️⃣ （可选）训练线性分类头

如果有已标注的 patch 数据，可以训练线性头提升准确率：

```bash
venv\Scripts\python.exe tools\clip_train.py
```

**数据准备：**
```
data/patches/labeled/
├── cotton/
│   ├── patch1.jpg
│   └── patch2.png
├── silk/
│   └── patch1.jpg
└── ...
```

**输出：**
- `data/clip_model.pkl` - 训练好的 LogisticRegression 模型

**要求：**
- 每个类别至少 5-10 个标注样本
- 总样本数建议 > 20

### 4️⃣ 评估性能

```bash
venv\Scripts\python.exe tools\eval_quick.py
```

**功能：**
1. 评估 CLIP 检索的 Top-1 和 Top-K 准确率
2. 显示混淆矩阵
3. 评估线性分类头性能（如果存在）

**输出示例：**
```
============================================================
Overall Metrics
============================================================
Total samples: 35
Top-1 Accuracy: 85.71% (30/35)
Top-5 Accuracy: 97.14% (34/35)

============================================================
Per-Class Metrics
============================================================
Class                Samples    Top-1 Acc    Top-5 Acc
------------------------------------------------------------
cotton               15         93.33%       100.00%
silk                 8          75.00%       87.50%
wool                 12         83.33%       100.00%
```

---

## 🔧 在代码中使用

### 方式 1：纯 CLIP 检索

```python
from PIL import Image
from src.clip_infer import rank_by_retrieval

# 加载 patch 图像
patch_img = Image.open("path/to/patch.jpg")

# 检索 Top-5 相似面料
results = rank_by_retrieval(patch_img, topk=5)

# 结果格式: [{"id": "cotton", "score": 0.856}, ...]
for r in results:
    print(f"{r['id']}: {r['score']:.3f}")
```

### 方式 2：融合规则 + CLIP（推荐）

```python
from PIL import Image
from src.fabric_ranker import recommend_fabrics_localized, fuse_with_clip

# 1. 提取属性（假设已完成）
attrs = {
    "visual": {
        "dominant_color_name": "blue",
        "sheen_score": 0.6,
        "texture_complexity": 0.4
    }
}

# 2. 基于规则的推荐
base_results = recommend_fabrics_localized(
    attrs, 
    lang="zh", 
    top_k=10,
    rules_source="fine"
)

# 3. 融合 CLIP 检索
patch_img = Image.open("path/to/patch.jpg")
fused_results = fuse_with_clip(
    patch_img=patch_img,
    base_results=base_results,
    lang="zh",
    alpha=0.7,  # 0.7 规则 + 0.3 CLIP
    topk=5
)

# 4. 显示结果
for name, score, display_name, notes in fused_results:
    print(f"{display_name}: {score:.3f}")
```

---

## 🎛️ 参数调优

### `alpha` 权重（融合时）

- **alpha=1.0**: 完全基于规则（忽略 CLIP）
- **alpha=0.7**: 推荐值 - 平衡规则与视觉相似度
- **alpha=0.5**: 规则与 CLIP 均等权重
- **alpha=0.0**: 完全基于 CLIP 检索

**建议：**
- 规则库完善时：`alpha=0.7-0.8`
- 规则库不全时：`alpha=0.3-0.5`
- 纯视觉检索：`alpha=0.0`

### Top-K 数量

- **topk=3**: 仅显示最相似的 3 个面料
- **topk=5**: 推荐值 - 平衡多样性与准确率
- **topk=10**: 提供更多候选，适合探索

---

## 📊 性能优化建议

### 1. 提升参考库质量
- ✅ 每个面料收集多角度、多光照的参考图
- ✅ 参考图应覆盖典型纹理和颜色变化
- ✅ 避免过度曝光或模糊的图像

### 2. 标注数据积累
- ✅ 从低置信度的 patch 开始标注
- ✅ 关注易混淆的面料对（如 silk vs satin）
- ✅ 每周增量训练更新模型

### 3. 模型选择
当前使用 `ViT-B-32`（快速，中等精度）

**可升级到：**
- `ViT-B-16`: 更高精度，稍慢
- `ViT-L-14`: 最高精度，较慢

修改 `src/clip_infer.py` 第 25 行：
```python
_model, _, _preprocess = create_model_and_transforms("ViT-L-14", pretrained="openai")
```

---

## 🐛 常见问题

### Q1: "No embeddings collected"
**原因：** `data/fabrics/` 为空或结构不正确

**解决：**
```bash
# 检查目录结构
ls data/fabrics/

# 应该有子目录：
data/fabrics/cotton/ref1.jpg
data/fabrics/silk/ref1.jpg
```

### Q2: "Too few samples to train"
**原因：** 标注数据少于 20 个

**解决：**
- 先使用纯检索模式（不训练线性头）
- 持续积累标注数据到 50+ 再训练

### Q3: CLIP 检索速度慢
**原因：** 每次都重新加载模型

**解决：**
- 模型已实现懒加载（首次慢，后续快）
- 如需进一步优化，考虑预先提取 patch 嵌入并缓存

### Q4: 融合后结果反而变差
**原因：** `alpha` 权重不合适或参考库质量问题

**解决：**
1. 检查参考库是否包含该面料
2. 调整 `alpha` 权重（增大 alpha 降低 CLIP 影响）
3. 增加更多高质量参考图

---

## 📈 效果预期

**在典型场景下（50+ 面料类别，每类 5 张参考图）：**

| 指标 | 纯规则 | +CLIP 检索 | +线性头 |
|------|--------|-----------|---------|
| Top-1 准确率 | 60-70% | 75-85% | 85-92% |
| Top-5 准确率 | 85-90% | 92-96% | 96-98% |
| 处理速度 | 极快 | 快 | 快 |
| 冷启动时间 | 0s | 2-3s | 2-3s |

**建议迭代路径：**
1. 🚀 **Phase 1**: 纯规则系统（当前）
2. 🎯 **Phase 2**: +CLIP 检索融合（本次更新）
3. 📊 **Phase 3**: +标注数据 + 线性头训练
4. 🏆 **Phase 4**: 微调 CLIP 或更大模型

---

## 🔗 相关文件

- `src/clip_infer.py` - CLIP 推理核心模块
- `src/fabric_ranker.py` - 融合逻辑（`fuse_with_clip` 函数）
- `tools/build_fabric_bank.py` - 构建参考库脚本
- `tools/clip_train.py` - 训练线性头脚本
- `tools/eval_quick.py` - 评估脚本

---

**最后更新:** 2025-10-09  
**维护者:** Fashion Prompt Extractor Team

