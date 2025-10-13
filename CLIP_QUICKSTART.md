# CLIP 面料识别 - 快速开始

## 🎯 功能概述

基于双通道 CLIP 模型的智能面料识别系统：
- **通道1**: HuggingFace ViT-B/32 (512维) → 全局语义特征
- **通道2**: LAION ViT-H/14 (1024维) → 纹理细节特征
- **融合**: 1536维向量 + L2归一化

## 📋 使用步骤

### 1. 构建面料向量库

首次使用需要运行一次（约15-35分钟）：

```powershell
# 进入项目目录
cd D:\fashion-prompt-extractor

# 清理缓存
Remove-Item -Recurse -Force src\__pycache__, tools\__pycache__ -ErrorAction SilentlyContinue

# 运行构建脚本
$env:OPENCLIP_CACHE_DIR = "$PWD\cache\open_clip"
$env:PYTHONUNBUFFERED = "1"
.\venv\Scripts\python.exe -u tools\build_fabric_bank.py
```

**输出示例**：
```
[INFO] 已处理 64 个类别
[OK] saved → D:\fashion-prompt-extractor\data\fabric_bank.npz
[OK] saved → D:\fashion-prompt-extractor\data\fabric_centroids.npz
```

**验证维度**：
```powershell
.\venv\Scripts\python.exe -c "import numpy as np; b=np.load('data/fabric_bank.npz'); print(f'✓ 向量维度: {b[b.files[0]].shape[1]}')"
```

应输出：`✓ 向量维度: 1536`

### 2. 命令行测试检索

```powershell
# 测试单张图片
.\venv\Scripts\python.exe -u tools\test_retrieval_cli.py data\fabrics\denim\16235f7db5ab74f5bf459d020088786a.jpg

# 返回 Top-10 结果
.\venv\Scripts\python.exe -u tools\test_retrieval_cli.py path\to\your\image.jpg --top-k 10
```

**输出示例**：
```
============================================================
检索结果 (Top-5)
============================================================
 1. 牛仔面料       (denim          ) 0.856  [████████████████░░░░] 85%
 2. 帆布           (canvas         ) 0.723  [██████████████░░░░░░] 72%
 3. 斜纹布         (twill          ) 0.689  [█████████████░░░░░░░] 68%
 4. 灯芯绒         (corduroy       ) 0.645  [████████████░░░░░░░░] 64%
 5. 亚麻           (linen          ) 0.612  [████████████░░░░░░░░] 61%
============================================================
```

### 3. 在 UI 中使用

1. **启动 Streamlit**：
   ```powershell
   streamlit run app.py
   ```

2. **打开浏览器**：`http://localhost:8501`

3. **启用 CLIP 模式**：
   - 在左侧边栏找到 `🔬 使用 CLIP 向量检索 (实验性)`
   - 勾选启用

4. **上传图片并查看结果**：
   - 上传服装图片
   - 系统会显示：`🔬 使用 CLIP 双通道向量检索...`
   - 查看 Top-5 推荐结果，带置信度条和中文名称

## 📊 结果说明

- **置信度 ≥ 70%** (绿色区域): 高可信度
- **置信度 30-70%** (黄色区域): 中等可信度
- **置信度 < 30%** (红色区域): 低可信度，显示 `⚠️ 建议人工确认/补图`

## 🔧 高级功能

### 检索策略

系统采用两阶段检索：

1. **粗排**（快）：使用类中心向量（centroids）
2. **精排**（准）：当 Top1 和 Top2 分数差 < 0.03 时，对全部样本重新计算

### 自定义阈值

```python
# 在代码中调整
recommend_fabrics_clip(image, top_k=5, threshold=0.03)
```

- `threshold` 越小 → 越容易触发精排 → 更准但更慢
- `threshold` 越大 → 更多使用粗排 → 更快但可能不准

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `data/fabric_bank.npz` | 完整向量库 (所有样本的1536维向量) |
| `data/fabric_centroids.npz` | 类中心向量库 (每个类的平均向量) |
| `data/fabric_labels.json` | 中文标签映射 |
| `data/fabric_aliases.json` | 中文别名（用于搜索） |
| `src/dual_clip.py` | 双通道 CLIP 编码器 |
| `src/fabric_clip_ranker.py` | CLIP 面料推荐器 |
| `src/fabric_labels.py` | 标签管理 API |
| `tools/build_fabric_bank.py` | 向量库构建脚本 |
| `tools/test_retrieval_cli.py` | 命令行检索测试工具 |

## 🐛 常见问题

### Q: 向量维度还是 512 而不是 1536？

**A**: Python 使用了旧缓存。执行：
```powershell
Remove-Item -Recurse -Force src\__pycache__, tools\__pycache__
.\venv\Scripts\python.exe -u tools\build_fabric_bank.py
```

### Q: 首次运行很慢？

**A**: 正常。首次需要下载 LAION ViT-H/14 模型（约1.6GB）。后续运行会快很多。

### Q: UI 报错 "向量库未找到"？

**A**: 请先运行步骤1构建向量库。

### Q: 识别准确率不高？

**A**: 可能原因：
- 面料类别图片数量不足（<5张）
- 图片质量差或角度问题
- 面料类别本身相似（如不同类型的织物）

**解决方案**：
1. 补充高质量面料图片
2. 重新构建向量库
3. 调整 `threshold` 参数触发精排

## 📈 性能优化

- **首次加载慢**：CLIP 模型加载需要几秒，后续使用单例模式缓存
- **大图处理慢**：建议将图片缩放到 1024px 以内
- **多类别慢**：类中心粗排可以处理 100+ 类别，全样本精排建议 <50 类别

## 🎨 扩展面料库

如需添加新面料类别：

1. 在 `data/fabrics/` 下创建新文件夹（小写英文）
2. 添加至少 5 张高质量纹理图片（512px+，无印花）
3. 在 `data/fabric_labels.json` 添加中文名
4. 在 `data/fabric_aliases.json` 添加别名（可选）
5. 重新运行 `build_fabric_bank.py`

---

**版本**: 1.0  
**更新时间**: 2025-10-12


