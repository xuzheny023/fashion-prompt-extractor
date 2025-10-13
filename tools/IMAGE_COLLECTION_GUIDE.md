# 面料图片收集工具使用指南

## 📦 可用工具

### 1. 图片下载器 (`download_fabric_images.py`)

**功能**：从URL列表批量下载面料参考图片

**使用方法**：

#### 方法A：批量下载（推荐）

1. 在每个面料类别文件夹创建 `urls.txt` 文件：
   ```
   data/fabrics/denim/urls.txt
   data/fabrics/silk/urls.txt
   ```

2. 在 `urls.txt` 中添加图片URL（每行一个）：
   ```
   https://example.com/denim1.jpg
   https://example.com/denim2.jpg
   https://example.com/denim3.jpg
   # 注释以 # 开头
   ```

3. 运行批量下载：
   ```bash
   python tools/download_fabric_images.py
   ```

#### 方法B：单个类别下载

```bash
python tools/download_fabric_images.py denim
```

**示例 urls.txt**：
```txt
# Denim fabric reference images
https://images.unsplash.com/photo-xxx/denim.jpg
https://pixabay.com/get/xxx/denim-texture.jpg
https://www.pexels.com/photo/xxx/blue-denim.jpg
```

---

### 2. 图片整理器 (`organize_fabric_images.py`)

**功能**：将下载的图片整理到对应的面料类别

#### 方法A：交互式整理（推荐新手）

1. 将图片放入收件箱：
   ```
   data/fabrics_inbox/
   ```

2. 运行交互式整理：
   ```bash
   python tools/organize_fabric_images.py
   ```

3. 对每张图片，输入类别名或命令：
   - 输入类别名（如 `denim`）：移动到该类别
   - `skip`：跳过此图片
   - `list`：显示所有可用类别
   - `quit`：退出

**示例交互**：
```
[1/10] fabric_001.jpg
  Size: (800, 600), Mode: RGB
  Category? denim
  ✓ Moved to: data/fabrics/denim/denim_005.jpg

[2/10] texture.jpg
  Category? list
  Available categories:
     1. canvas
     2. chiffon
     3. denim
     ...
  Category? silk
  ✓ Moved to: data/fabrics/silk/silk_003.jpg
```

#### 方法B：自动整理（批量处理）

1. 按规范命名图片（`类别_xxx.jpg`）：
   ```
   denim_ref01.jpg
   silk_texture_001.jpg
   cotton_sample.jpg
   ```

2. 放入收件箱：`data/fabrics_inbox/`

3. 运行自动整理：
   ```bash
   python tools/organize_fabric_images.py auto
   ```

---

### 3. 图片质量检查器 (`check_image_quality.py`)

**功能**：检查图片是否符合质量标准

**质量标准**：
- ✅ 最小尺寸：224x224
- 📏 推荐尺寸：≥512x512
- 📦 文件大小：≤10MB
- 🎨 亮度：30-225/255

#### 检查所有图片：
```bash
python tools/check_image_quality.py
```

#### 检查单个类别：
```bash
python tools/check_image_quality.py denim
```

**输出示例**：
```
[denim] - 5 images
  ✓ denim_001.jpg         800x600      0.5MB
  ⚠ denim_002.jpg         300x300      0.2MB  ⚠ Small: 300x300
  ✗ denim_003.jpg         150x150      0.1MB  ✗ Too small: 150x150 < 224x224

Summary:
  ✓ Valid:    3 (60.0%)
  ⚠ Warning:  1 (20.0%)
  ✗ Error:    1 (20.0%)
```

---

### 4. 图片格式修复器 (`fix_fabric_images.py`)

**功能**：转换不支持的图片格式为标准JPG

```bash
python tools/fix_fabric_images.py
```

**功能**：
- 检测所有图片
- 转换不支持格式（AVIF等）为JPG
- 删除无法处理的损坏图片

---

## 🔄 完整工作流程

### 快速开始（推荐流程）

#### 阶段1：准备URLs
```bash
# 1. 为优先类别创建URL文件
notepad data/fabrics/denim/urls.txt
notepad data/fabrics/silk/urls.txt
# ... 添加图片URLs

# 2. 批量下载
python tools/download_fabric_images.py
```

#### 阶段2：整理图片
```bash
# 3. 将散图放入收件箱
# 手动复制到 data/fabrics_inbox/

# 4. 交互式整理
python tools/organize_fabric_images.py
```

#### 阶段3：质量检查
```bash
# 5. 检查图片质量
python tools/check_image_quality.py

# 6. 修复格式问题
python tools/fix_fabric_images.py
```

#### 阶段4：构建向量库
```bash
# 7. 重新构建面料向量库
python tools/build_fabric_bank.py
```

---

## 📸 图片来源推荐

### 免费图片库（无版权问题）
1. **Unsplash**
   - https://unsplash.com/s/photos/fabric-texture
   - 高质量，完全免费

2. **Pexels**
   - https://www.pexels.com/search/fabric/
   - 免费商用

3. **Pixabay**
   - https://pixabay.com/images/search/fabric/
   - CC0许可

### 面料专业网站
1. **Fabric.com**
2. **Mood Fabrics**
3. **Fashion Snoops**（需订阅）

### 搜索技巧
- 英文关键词效果更好
- 加上 "texture", "close-up", "detail"
- 示例：`silk fabric texture close-up`

---

## 💡 收集建议

### 图片选择标准

✅ **好的参考图片**：
- 清晰的纹理特写
- 均匀光照
- 纯色或简单背景
- 尺寸≥512x512
- 代表性的面料样本

❌ **避免的图片**：
- 模糊不清
- 光照不均（阴影、反光）
- 复杂背景
- 尺寸太小
- 非典型样本

### 数量建议

| 阶段 | 每类图片数 | 说明 |
|------|-----------|------|
| 最低要求 | 3-5张 | 可以工作，但精度较低 |
| 推荐 | 5-10张 | 平衡质量和效率 |
| 理想 | 10-20张 | 更好的检索精度 |

### 多样性建议

每个类别的图片应包含：
- 不同颜色（如果适用）
- 不同纹理密度
- 不同拍摄角度
- 不同光照条件

---

## 🔧 故障排除

### 问题1：下载失败
```
✗ Failed: HTTPError 403
```
**解决**：URL可能有防盗链，换个图片源

### 问题2：图片太小
```
✗ Too small: 200x200 < 224x224
```
**解决**：找更高分辨率的图片，或去除该图片

### 问题3：无法识别格式
```
✗ Cannot identify image file
```
**解决**：
```bash
python tools/fix_fabric_images.py
```

### 问题4：类别名错误
```
✗ Category 'demim' not found
```
**解决**：检查拼写，使用 `list` 命令查看可用类别

---

## 📊 进度跟踪

查看收集进度：
```bash
python check_fabric_status.py
```

输出示例：
```
✓ denim      5 images (READY)
○ silk       3 images (need 2 more)
✗ leather    0 images (EMPTY)
```

---

## 🎯 优先级建议

### 第1批（最常用，优先收集）：
```
denim, cotton, silk, lace, knit, wool, leather, chiffon, satin, linen
```

### 第2批（常用）：
```
corduroy, velvet, canvas, twill, polyester, nylon, mesh, tulle, organza
```

### 第3批（特殊面料）：
```
sequin, metallic, pvc, faux_leather, transparent, waterproof
```

---

## 📞 需要帮助？

如果遇到问题，检查：
1. 图片格式是否支持（JPG/PNG）
2. 文件路径是否正确
3. 类别名拼写是否正确
4. 网络连接是否正常（下载时）

祝收集顺利！🎉


