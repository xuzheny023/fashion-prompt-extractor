# 面料数据收集完整指南 / Complete Fabric Collection Guide

## 📊 当前状态

✅ **已完成：**
- ✅ 64个面料类别目录已创建
- ✅ CLIP模型已配置（transformers + 本地模型）
- ✅ 中文标签和别名系统已就绪
- ✅ 图片收集辅助工具已创建
- ✅ 构建脚本已准备就绪

**进度：** 43/320 images (13.4%)
- ✅ **0** 个类别达标（≥5张图）
- 🟡 **12** 个类别部分完成（1-4张图）
- ⚪ **52** 个类别为空

---

## 🗂️ 核心文件结构

```
data/
├── fabrics/                          # 面料参考图片目录
│   ├── denim/                        # 每个面料类别一个文件夹
│   │   ├── denim_001.jpg
│   │   ├── denim_002.jpg
│   │   └── urls.txt                  # (可选) URL列表用于下载
│   ├── silk/
│   └── ...                           # 64个类别
├── fabrics_inbox/                    # 收件箱（待整理的图片）
├── fabric_bank.npz                   # CLIP向量库（生成）
├── fabric_labels.json                # ✨ 中文标签
└── fabric_aliases.json               # ✨ 别名映射

src/
├── clip_infer.py                     # CLIP模型加载和推理
├── fabric_labels.py                  # ✨ 标签和别名管理
└── fabric_ranker.py                  # 面料推荐（已集成中文标签）

tools/
├── build_fabric_bank.py              # 构建CLIP向量库
├── download_fabric_images.py         # ✨ 从URL下载图片
├── organize_fabric_images.py         # ✨ 交互式整理图片
├── check_image_quality.py            # ✨ 图片质量检查
├── fix_fabric_images.py              # 图片格式修复
└── IMAGE_COLLECTION_GUIDE.md         # ✨ 详细使用指南

check_fabric_status.py                # ✨ 快速查看收集进度
```

---

## 🎯 快速开始（3种方式）

### 方式1：从URL批量下载（推荐）

```bash
# 1. 创建URL列表文件
# 在 data/fabrics/denim/urls.txt 中添加：
https://example.com/denim1.jpg
https://example.com/denim2.jpg

# 2. 批量下载
python tools/download_fabric_images.py

# 3. 检查质量
python tools/check_image_quality.py

# 4. 构建向量库
python tools/build_fabric_bank.py
```

### 方式2：交互式整理本地图片

```bash
# 1. 将图片放入收件箱
# 复制图片到 data/fabrics_inbox/

# 2. 交互式整理
python tools/organize_fabric_images.py
# 对每张图片输入类别名，如 "denim"

# 3. 构建向量库
python tools/build_fabric_bank.py
```

### 方式3：自动批量整理

```bash
# 1. 按规范命名图片（类别_xxx.jpg）
# denim_001.jpg, silk_texture.jpg, etc.

# 2. 放入收件箱
# 复制到 data/fabrics_inbox/

# 3. 自动整理
python tools/organize_fabric_images.py auto

# 4. 构建向量库
python tools/build_fabric_bank.py
```

---

## 🛠️ 工具详解

### 1. 📥 图片下载器
**文件：** `tools/download_fabric_images.py`

**功能：** 从URL列表批量下载面料参考图片

**使用：**
```bash
# 批量下载所有类别（有urls.txt的）
python tools/download_fabric_images.py

# 下载单个类别
python tools/download_fabric_images.py denim
```

**URL文件格式：**
```txt
# data/fabrics/denim/urls.txt
https://images.unsplash.com/photo-xxx/denim.jpg
https://pixabay.com/get/xxx/denim-texture.jpg
# 注释以 # 开头
```

---

### 2. 📂 图片整理器
**文件：** `tools/organize_fabric_images.py`

**功能：** 交互式或自动整理图片到对应类别

**交互模式：**
```bash
python tools/organize_fabric_images.py
```
- 输入类别名（如 `denim`）：移动到该类别
- `skip`：跳过此图片
- `list`：显示所有可用类别
- `quit`：退出

**自动模式：**
```bash
python tools/organize_fabric_images.py auto
```
- 自动根据文件名前缀分类（`denim_xxx.jpg` → `denim/`）

---

### 3. ✅ 图片质量检查器
**文件：** `tools/check_image_quality.py`

**功能：** 检查图片是否符合质量标准

**质量标准：**
- ✅ 最小尺寸：224x224
- 📏 推荐尺寸：≥512x512
- 📦 文件大小：≤10MB
- 🎨 亮度：30-225/255

**使用：**
```bash
# 检查所有图片
python tools/check_image_quality.py

# 检查单个类别
python tools/check_image_quality.py denim
```

---

### 4. 🔧 图片格式修复器
**文件：** `tools/fix_fabric_images.py`

**功能：** 转换不支持的图片格式为标准JPG

```bash
python tools/fix_fabric_images.py
```

---

### 5. 📊 进度查看器
**文件：** `check_fabric_status.py`

**功能：** 快速查看收集进度

```bash
python check_fabric_status.py
```

**输出示例：**
```
✓ denim      5 images (READY)
○ silk       3 images (need 2 more)
✗ leather    0 images (EMPTY)
```

---

## 🌏 中文标签系统

### 核心文件

**1. `data/fabric_labels.json`** - 中文标签
```json
{
  "denim": "牛仔面料",
  "silk": "真丝",
  "chiffon": "雪纺"
}
```

**2. `data/fabric_aliases.json`** - 别名映射
```json
{
  "denim": ["丹宁", "牛仔布", "牛仔"],
  "silk": ["丝", "桑蚕丝"]
}
```

### Python API

**文件：** `src/fabric_labels.py`

```python
from src.fabric_labels import get_label, search_fabric

# 获取中文标签
get_label("denim")  # → "牛仔面料"

# 搜索（支持中文、英文、别名）
search_fabric("牛仔")    # → ["denim"]
search_fabric("silk")    # → ["silk"]
search_fabric("雪纺")    # → ["chiffon", "chiffon_crinkle", "chiffon_pearl"]
```

### UI 集成

`fabric_ranker.py` 已自动集成中文标签：

```python
from src.fabric_ranker import localize_fabric

# 在UI中显示
display_name, notes = localize_fabric("denim", lang="zh")
# display_name = "牛仔面料"
```

---

## 📸 图片来源推荐

### 免费高质量图库

| 网站 | URL | 特点 |
|------|-----|------|
| **Unsplash** | https://unsplash.com/s/photos/fabric-texture | 高质量，完全免费 |
| **Pexels** | https://www.pexels.com/search/fabric/ | 免费商用 |
| **Pixabay** | https://pixabay.com/images/search/fabric/ | CC0许可 |

### 搜索技巧

```
✅ 好的关键词：
- "denim fabric texture close-up"
- "silk fabric detail"
- "chiffon material texture"

❌ 避免：
- 单个词搜索（太宽泛）
- 没有 "fabric" / "texture" 的搜索
```

---

## 🎯 收集建议

### 图片选择标准

✅ **好的参考图片：**
- 清晰的纹理特写
- 均匀光照
- 纯色或简单背景
- 尺寸≥512x512
- 代表性的面料样本

❌ **避免的图片：**
- 模糊不清
- 光照不均（阴影、反光）
- 复杂背景
- 尺寸太小
- 非典型样本

### 数量建议

| 阶段 | 每类图片数 | 说明 |
|------|-----------|------|
| **最低要求** | 3-5张 | 可以工作，但精度较低 |
| **推荐** | 5-10张 | ⭐ 平衡质量和效率 |
| **理想** | 10-20张 | 更好的检索精度 |

### 多样性建议

每个类别的图片应包含：
- ✓ 不同颜色（如果适用）
- ✓ 不同纹理密度
- ✓ 不同拍摄角度
- ✓ 不同光照条件

---

## 📋 推荐收集顺序

### 第1批（最常用，优先收集）：
```
denim, cotton, silk, lace, knit, wool, leather, 
chiffon, satin, linen
```
**目标：** 10个类别 × 5张图 = 50张

### 第2批（常用）：
```
corduroy, velvet, canvas, twill, polyester, nylon, 
mesh, tulle, organza
```
**目标：** 9个类别 × 5张图 = 45张

### 第3批（特殊面料）：
```
sequin, metallic, pvc, faux_leather, transparent, waterproof,
embroidery, print, quilting, etc.
```
**目标：** 剩余45个类别逐步补充

---

## 🔄 完整工作流程

```bash
# ========== 阶段1：准备 ==========
# 1. 查看当前状态
python check_fabric_status.py

# ========== 阶段2：收集图片 ==========
# 方式A：从URL下载
python tools/download_fabric_images.py

# 方式B：整理本地图片
python tools/organize_fabric_images.py

# ========== 阶段3：质量检查 ==========
# 3. 检查图片质量
python tools/check_image_quality.py

# 4. 修复格式问题
python tools/fix_fabric_images.py

# ========== 阶段4：构建向量库 ==========
# 5. 构建CLIP向量库
python tools/build_fabric_bank.py
# 输出：data/fabric_bank.npz

# ========== 阶段5：验证 ==========
# 6. 再次查看状态
python check_fabric_status.py

# 7. 在主应用中测试
streamlit run app.py
```

---

## 🚨 常见问题

### Q1：下载失败
```
✗ Failed: HTTPError 403
```
**解决：** URL可能有防盗链，换个图片源

### Q2：图片太小
```
✗ Too small: 200x200 < 224x224
```
**解决：** 找更高分辨率的图片，或删除该图片

### Q3：无法识别格式
```
✗ Cannot identify image file
```
**解决：**
```bash
python tools/fix_fabric_images.py
```

### Q4：类别名拼写错误
```
✗ Category 'demim' not found
```
**解决：** 检查拼写，使用 `list` 命令查看可用类别

### Q5：如何快速达标？
**回答：** 只需给12个部分完成的类别各补1-3张图（共15-20张），即可有12个可用类别：
```
canvas, chiffon, corduroy, cotton, denim, knit, 
lace, linen, organza, satin, silk, woolen
```

---

## 📚 详细文档

- **图片收集指南：** `tools/IMAGE_COLLECTION_GUIDE.md`
- **CLIP使用说明：** `tools/CLIP_USAGE.md`
- **功能总结：** `FEATURE_SUMMARY.md`

---

## ✅ 下一步

1. **立即开始：** 给部分完成的12个类别补充图片（最快路径）
2. **中期目标：** 收集30个常用类别（第1批+第2批）
3. **长期目标：** 完成全部64个类别

**💡 建议：** 先用10-12个类别测试整个系统，确认效果后再扩展到全部64个类别。

---

## 📞 技术支持

如果遇到问题：
1. 检查 `check_fabric_status.py` 输出
2. 运行 `python tools/check_image_quality.py`
3. 查看 `tools/IMAGE_COLLECTION_GUIDE.md`
4. 检查图片格式（JPG/PNG）

祝收集顺利！🎉


