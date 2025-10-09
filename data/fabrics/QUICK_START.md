# 🚀 快速开始指南

## 📋 当前状态

已创建 **14 个**面料类别目录：

| 编号 | 面料 | 英文 | 目录 | 状态 |
|-----|------|------|------|------|
| 1 | 雪纺 | Chiffon | `chiffon/` | ⏳ 待添加图像 |
| 2 | 真丝 | Silk | `silk/` | ⏳ 待添加图像 |
| 3 | 牛仔 | Denim | `denim/` | ⏳ 待添加图像 |
| 4 | 缎 | Satin | `satin/` | ⏳ 待添加图像 |
| 5 | 棉布 | Cotton | `cotton/` | ⏳ 待添加图像 |
| 6 | 针织 | Knit | `knit/` | ⏳ 待添加图像 |
| 7 | 罗纹 | Rib | `rib/` | ⏳ 待添加图像 |
| 8 | 欧根纱 | Organza | `organza/` | ⏳ 待添加图像 |
| 9 | 呢绒 | Woolen | `woolen/` | ⏳ 待添加图像 |
| 10 | 灯芯绒 | Corduroy | `corduroy/` | ⏳ 待添加图像 |
| 11 | 帆布 | Canvas | `canvas/` | ⏳ 待添加图像 |
| 12 | 亚麻 | Linen | `linen/` | ⏳ 待添加图像 |
| 13 | 天丝 | Tencel | `tencel/` | ⏳ 待添加图像 |
| 14 | 蕾丝 | Lace | `lace/` | ⏳ 待添加图像 |

---

## 🎯 3 步开始使用

### Step 1: 添加参考图像

为每个面料类别添加 **3-5 张**参考图像：

```bash
# 示例：为雪纺添加 3 张参考图
data/fabrics/chiffon/
├── chiffon_01.jpg  # 复制或粘贴第 1 张图
├── chiffon_02.jpg  # 复制或粘贴第 2 张图
└── chiffon_03.jpg  # 复制或粘贴第 3 张图
```

**快速操作**:
1. 打开对应面料目录
2. 将图片直接拖拽或复制进去
3. 重命名为有意义的文件名

---

### Step 2: 构建向量库

所有图像添加完成后，运行：

```bash
venv\Scripts\python.exe tools\build_fabric_bank.py
```

**预期输出**:
```
Building fabric reference bank...

  [chiffon] Processed: chiffon_01.jpg
  [chiffon] Processed: chiffon_02.jpg
  [chiffon] Processed: chiffon_03.jpg
[OK] chiffon: 3 images -> shape (3, 512)

  [silk] Processed: silk_01.jpg
  [silk] Processed: silk_02.jpg
[OK] silk: 2 images -> shape (2, 512)

... (所有面料)

============================================================
✅ Saved fabric bank -> D:\...\data\fabric_bank.npz
   Total fabrics: 14
   Total images: 56
   File size: 135.2 KB
============================================================
```

---

### Step 3: 测试检索

```python
from PIL import Image
from src.clip_infer import rank_by_retrieval

# 加载测试图像
img = Image.open("test_patch.jpg")

# 检索 Top-5 相似面料
results = rank_by_retrieval(img, topk=5)

# 显示结果
for r in results:
    print(f"{r['id']}: {r['score']:.3f}")
```

**预期输出**:
```
chiffon: 0.856
silk: 0.742
organza: 0.701
satin: 0.689
tencel: 0.654
```

---

## 📊 图像要求

### ✅ 推荐的图像

- **分辨率**: 512×512 或更高
- **内容**: 面料特写，充满画面
- **光照**: 均匀、自然光
- **清晰度**: 焦点清晰，无模糊
- **背景**: 纯色或简单背景
- **多样性**: 不同角度、光照

### ❌ 不推荐的图像

- 模糊、失焦
- 过度曝光或欠曝
- 背景杂乱
- 面料占比 < 50%
- 严重色偏或滤镜

---

## 🎨 拍摄技巧

### 方法 1: 手机拍摄（最简单）

1. **距离**: 30-50cm
2. **光线**: 靠近窗户自然光
3. **角度**: 正对面料垂直拍摄
4. **焦点**: 点击屏幕对焦面料纹理
5. **拍摄**: 每个面料拍 3-5 张不同角度

### 方法 2: 网络下载

1. 搜索关键词: `"<面料名> 纹理 高清"`
2. 选择清晰的特写图
3. 下载后重命名
4. 确保图像无水印

### 方法 3: 现有图片库

1. 从产品图中裁剪面料区域
2. 使用图像编辑工具裁剪到合适大小
3. 保存为 JPG 格式

---

## 📝 命名建议

### 推荐命名格式

```
<fabric>_<variant>_<number>.jpg
```

**示例**:
```
chiffon_white_01.jpg
chiffon_pink_02.jpg
silk_satin_shiny_01.jpg
cotton_plain_white_01.jpg
denim_blue_texture_01.jpg
```

### 简单命名

```
chiffon_01.jpg
chiffon_02.jpg
chiffon_03.jpg
```

---

## 🔄 渐进式添加

**不需要一次性添加所有面料！**

### 推荐顺序

**Phase 1: 核心面料（优先）**
- ✅ Cotton 棉布
- ✅ Silk 真丝
- ✅ Knit 针织
- ✅ Denim 牛仔

**Phase 2: 常用面料**
- ✅ Satin 缎
- ✅ Chiffon 雪纺
- ✅ Linen 亚麻

**Phase 3: 特殊面料**
- ✅ Lace 蕾丝
- ✅ Organza 欧根纱
- ✅ Corduroy 灯芯绒
- ✅ 其他...

每添加几个面料后，重新运行 `build_fabric_bank.py` 即可。

---

## 🎯 最小可用配置

**最少**只需 **5 个面料 × 3 张图 = 15 张图**即可开始使用！

**推荐配置**:
- Cotton 棉布 (3 张)
- Silk 真丝 (3 张)
- Knit 针织 (3 张)
- Denim 牛仔 (3 张)
- Satin 缎 (3 张)

---

## 🐛 常见问题

### Q: 必须填满所有 14 个面料吗？
A: **不需要**！可以只添加部分面料，系统会自动识别已有的面料类别。

### Q: 图片必须是正方形吗？
A: **不需要**！CLIP 会自动缩放。但建议比例接近 1:1 效果更好。

### Q: 可以用同一面料的不同颜色吗？
A: **可以**！建议同一面料添加 2-3 种常见颜色的样本。

### Q: 图片大小有限制吗？
A: 建议 **< 5 MB** 每张。太大的图片会影响加载速度。

### Q: 后期可以继续添加吗？
A: **完全可以**！随时添加新面料或新图片，重新运行 `build_fabric_bank.py` 即可。

---

## ✅ 检查清单

添加图像前：
- [ ] 了解每个面料的特征（参考 README.txt）
- [ ] 准备清晰的参考图像
- [ ] 确认图像格式为 JPG/PNG

添加图像后：
- [ ] 检查每个目录至少有 3 张图
- [ ] 运行 `build_fabric_bank.py`
- [ ] 确认生成 `data/fabric_bank.npz`
- [ ] 测试检索功能

---

## 📞 需要帮助？

**查看详细文档**:
- `data/fabrics/README.md` - 完整使用说明
- `WORKFLOW.md` - 完整工作流程
- `tools/CLIP_USAGE.md` - CLIP 使用指南

**快速测试**:
```bash
# 检查当前状态
ls data/fabrics/*/

# 构建向量库
venv\Scripts\python.exe tools\build_fabric_bank.py

# 查看向量库大小
ls -lh data/fabric_bank.npz
```

---

**开始添加图像吧！** 🎨

---

**最后更新**: 2025-10-09

