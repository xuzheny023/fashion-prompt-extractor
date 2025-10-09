# 面料参考图像库 | Fabric Reference Image Bank

本目录用于存放各类面料的参考图像，供 CLIP 检索系统使用。

## 📁 目录结构

```
data/fabrics/
├── chiffon/      # 雪纺
├── silk/         # 真丝
├── denim/        # 牛仔
├── satin/        # 缎
├── cotton/       # 棉布
├── knit/         # 针织
├── rib/          # 罗纹
├── organza/      # 欧根纱
├── woolen/       # 呢绒
├── corduroy/     # 灯芯绒
├── canvas/       # 帆布
├── linen/        # 亚麻
├── tencel/       # 天丝
└── lace/         # 蕾丝
```

## 📋 使用说明

### 1. 添加参考图像

在每个面料目录中添加 **3-5 张**代表性图像：

```
data/fabrics/chiffon/
├── ref_01.jpg  # 正面图
├── ref_02.jpg  # 侧光图
├── ref_03.jpg  # 不同角度
├── ref_04.jpg  # (可选) 不同颜色
└── ref_05.jpg  # (可选) 纹理细节
```

### 2. 图像要求

- ✅ **分辨率**: ≥ 224×224 像素（推荐 512×512）
- ✅ **格式**: JPG、JPEG、PNG
- ✅ **内容**: 纯面料特写，避免复杂背景
- ✅ **质量**: 清晰、光照均匀
- ✅ **多样性**: 不同角度、光照、颜色（同一面料）

### 3. 推荐拍摄方式

**理想拍摄条件**:
- 📷 使用手机或相机正对面料拍摄
- 💡 自然光或柔和白光（避免强烈阴影）
- 📐 保持 30-50cm 距离
- 🎯 让面料充满画面的 80% 以上

**多样性建议**:
- 正面平铺 (1 张)
- 侧光展示纹理 (1 张)
- 45° 角度 (1 张)
- 不同颜色样本（如有）(1-2 张)

### 4. 构建向量库

添加完图像后，运行以下命令：

```bash
venv\Scripts\python.exe tools\build_fabric_bank.py
```

**预期输出**:
```
Building fabric reference bank...

  [chiffon] Processed: ref_01.jpg
  [chiffon] Processed: ref_02.jpg
  [chiffon] Processed: ref_03.jpg
[OK] chiffon: 3 images -> shape (3, 512)
...

============================================================
✅ Saved fabric bank -> D:\...\data\fabric_bank.npz
   Total fabrics: 14
   Total images: 56
   File size: 135.2 KB
============================================================
```

## 🎯 质量检查

### 好的参考图示例 ✅

- 清晰的纹理细节
- 均匀的光照
- 面料充满画面
- 颜色真实

### 不推荐的图像 ❌

- 模糊/失焦
- 过度曝光或欠曝
- 背景杂乱
- 面料占比过小
- 严重色偏

## 📊 数量建议

| 面料数量 | 每个面料图像数 | 总图像数 | 预期效果 |
|---------|-------------|---------|---------|
| **10-15** | 3-5 张 | 30-75 张 | 基础可用 |
| **20-30** | 5-8 张 | 100-240 张 | 良好 |
| **50+** | 8-10 张 | 400+ 张 | 优秀 |

## 🔄 更新流程

1. **添加新图像**到对应目录
2. **重新运行** `build_fabric_bank.py`
3. **评估效果** 使用 `eval_quick.py`
4. **调整优化** 根据评估结果补充图像

## 📝 命名规范（建议）

```
<fabric_type>_<variant>_<angle>_<number>.jpg

示例:
chiffon_white_front_01.jpg
chiffon_pink_side_01.jpg
silk_satin_detail_01.jpg
```

## 🎓 常见问题

**Q: 每个面料至少需要几张图？**  
A: 最少 3 张，推荐 5 张。少于 3 张会影响检索准确率。

**Q: 可以用网络下载的图片吗？**  
A: 可以，但要确保：
- 图像清晰
- 颜色真实
- 避免水印
- 尺寸合适

**Q: 需要相同尺寸吗？**  
A: 不需要，CLIP 会自动缩放到 224×224。

**Q: 可以后期添加更多面料吗？**  
A: 可以！随时添加新目录，重新运行 `build_fabric_bank.py` 即可。

---

**维护者**: Fashion Prompt Extractor Team  
**最后更新**: 2025-10-09

