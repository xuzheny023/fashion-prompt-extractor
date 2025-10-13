# 统一推荐引擎指南

## 📦 概述

`src/core/recommender.py` 是整个推荐系统的统一入口，整合了：

1. **CLIP 编码** - 双通道 1536 维向量
2. **向量检索** - 两阶段（粗排+精排）
3. **AI 复核** - 多模态大模型辅助（可选）
4. **标准输出** - `RankedResult` + `QueryMeta`

**核心价值：一行代码完成整个推荐流程**

---

## 🎯 快速开始

### 基本用法

```python
from src.core.recommender import recommend
from PIL import Image

# 加载图片
img = Image.open("fabric.jpg")

# 单行调用
result, meta = recommend(img)

# 访问结果
print(f"Top 1: {result.top1.label} ({result.top1.score:.2%})")
print(f"耗时: {meta.ms}ms")
```

就这么简单！✨

---

## 📋 完整 API

### recommend()

```python
def recommend(
    image: Image.Image,
    top_k: int | None = None,      # 返回前 K 个结果（默认 5）
    topc: int | None = None,        # 粗排保留前 C 个类（默认 12）
    lang: str = "zh"                # 语言："zh" 或 "en"
) -> tuple[RankedResult, QueryMeta]
```

**参数：**
- `image` - PIL 图片对象（必需）
- `top_k` - 返回结果数量（默认从 `cfg.TOPK` 读取）
- `topc` - 粗排候选类数（默认从 `cfg.TOPC` 读取）
- `lang` - 标签语言（`"zh"` 中文 / `"en"` 英文）

**返回：**
- `RankedResult` - 排名结果（包含 items 和 ai_reason）
- `QueryMeta` - 性能指标（ms 和 coarse_max）

---

## 🔍 推荐流程

```
图片输入
   ↓
┌─────────────────────┐
│ 阶段1: CLIP 编码    │  双通道 → 1536 维 → L2 归一化
└─────────────────────┘
   ↓
┌─────────────────────┐
│ 阶段2: 向量检索     │  粗排（类中心）→ 精排（完整样本）
└─────────────────────┘
   ↓
┌─────────────────────┐
│ 阶段3: AI 复核      │  低置信度或边界模糊 → 触发多模态大模型
│     (可选)          │
└─────────────────────┘
   ↓
┌─────────────────────┐
│ 阶段4: 构建结果     │  标准化输出：RankedResult + QueryMeta
└─────────────────────┘
```

---

## 📊 返回结果详解

### RankedResult

```python
result = RankedResult(
    items=[
        ScoreItem("棉", 0.89),
        ScoreItem("亚麻", 0.76),
        ScoreItem("丝绸", 0.68),
    ],
    ai_reason="CLIP 双通道向量检索"  # 或 "AI 复核 (openai)"
)

# 访问结果
result.top1              # ScoreItem: 得分最高项
result.top3              # List[ScoreItem]: 前3项
result.items             # List[ScoreItem]: 所有结果
result.ai_reason         # str: 推理方式

# 便捷方法
result.get_top_k(5)                    # 获取前5
result.filter_by_threshold(0.60)       # 过滤 ≥60% 的结果
```

### QueryMeta

```python
meta = QueryMeta(
    ms=185,           # 耗时（毫秒）
    coarse_max=0.92   # 粗排最高分
)

# 访问指标
meta.ms              # int: 毫秒
meta.seconds         # float: 秒
meta.coarse_max      # float: 粗排分数

# 便捷方法
meta.is_fast()              # 是否 <= 200ms
meta.is_fast(100)           # 是否 <= 100ms
```

---

## 🎨 使用场景

### 场景1: Streamlit UI

```python
import streamlit as st
from src.core.recommender import recommend

# 上传图片
uploaded = st.file_uploader("上传面料图片")
if uploaded:
    img = Image.open(uploaded)
    
    # 推荐
    with st.spinner("分析中..."):
        result, meta = recommend(img)
    
    # 显示性能
    st.caption(f"⚡ {meta.ms}ms · 粗排最高分: {meta.coarse_max:.2f}")
    
    # 显示结果
    for i, item in enumerate(result.top3, 1):
        st.write(f"**{i}. {item.label}**")
        st.progress(item.score)
        st.caption(f"置信度: {item.score:.2%}")
    
    # AI 推理说明
    if "AI" in result.ai_reason:
        st.info(f"💡 {result.ai_reason}")
```

### 场景2: 批量处理

```python
from pathlib import Path
from src.core.recommender import recommend
from PIL import Image

results = []
for img_path in Path("test_images").glob("*.jpg"):
    img = Image.open(img_path)
    result, meta = recommend(img, lang="en")
    
    results.append({
        "file": img_path.name,
        "top1": result.top1.label,
        "score": result.top1.score,
        "time_ms": meta.ms,
    })

# 导出为 CSV
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("batch_results.csv", index=False)
```

### 场景3: 高级配置

```python
from src.core.recommender import recommend

# 自定义参数
result, meta = recommend(
    img,
    top_k=10,      # 返回前 10 个（默认 5）
    topc=20,       # 粗排保留 20 个类（默认 12）
    lang="en"      # 英文标签
)

# 只要高置信度结果
confident = result.filter_by_threshold(0.70)
if confident:
    print(f"找到 {len(confident)} 个高置信度结果")
else:
    print("无高置信度结果，建议人工确认")
```

### 场景4: 结果日志记录

```python
from src.core.recommender import recommend
from src.utils.logger import get_logger

log = get_logger("fabric_api")

result, meta = recommend(img)

# 记录性能
if meta.is_fast():
    log.info(f"✓ 快速检索: {meta.ms}ms")
else:
    log.warning(f"⚠ 检索较慢: {meta.ms}ms")

# 记录结果
log.info(f"Top 1: {result.top1.label} ({result.top1.score:.2%})")

if result.top1.score < 0.50:
    log.warning("低置信度结果，建议复核")
```

---

## ⚙️ 配置

### 基础配置（.env）

```bash
# 检索参数
TOPK=5              # 返回结果数
TOPC=12             # 粗排候选数
LOW_CONF=0.30       # 低置信度阈值
CLOSE_GAP=0.03      # 分数差阈值

# AI 复核（可选）
AI_BACKEND=none     # none | openai | ollama
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini

# 性能开关
ENABLE_FAISS=true   # 启用 FAISS 加速
ENABLE_CACHE=true   # 启用缓存
```

### 代码配置

```python
from src.config import cfg

# 读取配置
print(f"返回结果数: {cfg.TOPK}")
print(f"AI 后端: {cfg.AI_BACKEND}")

# 运行时调整
cfg.TOPK = 10       # ⚠️ 不推荐，应在 .env 中配置
```

---

## 🤖 AI 复核

### 触发条件

AI 复核在以下情况自动触发：

1. **低置信度**：最高分 < `LOW_CONF`（默认 0.30）
2. **边界模糊**：前两名分数差 < `CLOSE_GAP`（默认 0.03）

### 启用 AI 复核

#### 方式1: OpenAI

```bash
# .env
AI_BACKEND=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

```bash
pip install openai
```

#### 方式2: Ollama（本地）

```bash
# .env
AI_BACKEND=ollama
OLLAMA_MODEL=llava:13b
OLLAMA_BASE_URL=http://localhost:11434
```

```bash
# 安装 Ollama
# https://ollama.ai

# 拉取模型
ollama pull llava:13b

# 启动服务
ollama serve
```

#### 方式3: 禁用

```bash
# .env
AI_BACKEND=none
```

### AI 工作流程

```python
# 用户无需关心，引擎自动处理
result, meta = recommend(img)

# 如果触发了 AI 复核
if "AI" in result.ai_reason:
    print("✓ AI 已介入复核")
    # result.items 已经是 AI 调整后的排名
```

---

## 🧪 测试

### 快速验证

```bash
python tools/verify_recommender.py
```

检查项：
- ✅ 模块导入
- ✅ 依赖完整性
- ✅ 向量库就绪

### 完整测试

```bash
# 自动选择测试图片
python tools/test_recommender.py

# 指定图片
python tools/test_recommender.py data/fabrics/cotton/001.jpg
```

输出示例：
```
======================================================================
推荐引擎测试
======================================================================

📷 测试图片: data/fabrics/cotton/cotton_01.jpg
----------------------------------------------------------------------
✓ 图片加载成功: 800x600

🔍 开始推荐...
----------------------------------------------------------------------

✅ 推荐完成!
======================================================================

📊 性能指标:
  耗时: 185 ms (0.185 秒)
  粗排最高分: 0.920
  是否快速 (<200ms): 是

🏆 推荐结果 (Top 5):

  1. 棉
     置信度: 89.00% 🟢 高
     [███████████████████████████░░░]

  2. 亚麻
     置信度: 76.00% 🟢 高
     [███████████████████████░░░░░░░]

  3. 丝绸
     置信度: 68.00% 🟡 中
     [████████████████████░░░░░░░░░░]

💡 推理方式: CLIP 双通道向量检索

✨ 高置信度结果 (≥60%):
  • 棉: 89.00%
  • 亚麻: 76.00%
  • 丝绸: 68.00%
```

---

## 🔧 故障排查

### 问题1: 向量库不存在

```
FileNotFoundError: data/fabric_bank.npz not found
```

**解决：**
```bash
python tools/build_fabric_bank.py
```

### 问题2: CLIP 模型下载慢

**解决：**
```bash
# 使用镜像加速
export HF_ENDPOINT=https://hf-mirror.com
python tools/build_fabric_bank.py
```

### 问题3: 内存不足

**解决：**
```python
# 减少 TOPC（粗排候选数）
result, meta = recommend(img, topc=8)  # 默认 12
```

### 问题4: AI 复核失败

```
⚠ AI 复核失败: Connection timeout
```

**解决：**
```bash
# 检查 API 配置
echo $OPENAI_API_KEY

# 或禁用 AI 复核
AI_BACKEND=none
```

---

## 📈 性能优化

### 优化1: 预热引擎（首次调用较慢）

```python
from src.core.recommender import get_engine

# 应用启动时预加载
engine = get_engine()  # 加载模型和向量库
```

### 优化2: 使用 FAISS 加速

```bash
pip install faiss-cpu  # CPU 版本
# 或
pip install faiss-gpu  # GPU 版本
```

```bash
# .env
ENABLE_FAISS=true
```

### 优化3: 调整粗排参数

```python
# TOPC 越小越快，但可能损失精度
result, meta = recommend(img, topc=8)   # 快速模式
result, meta = recommend(img, topc=20)  # 精确模式
```

### 优化4: 缓存结果（相同图片）

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def recommend_cached(img_hash: str, img_path: str):
    img = Image.open(img_path)
    return recommend(img)

# 使用
img_hash = hashlib.md5(img_bytes).hexdigest()
result, meta = recommend_cached(img_hash, img_path)
```

---

## 🎓 最佳实践

### ✅ DO

1. **使用统一入口**
   ```python
   from src.core.recommender import recommend  # ✅
   # 而不是直接调用 fabric_clip_ranker
   ```

2. **利用标准类型**
   ```python
   result, meta = recommend(img)
   print(result.top1.label)  # ✅ 类型安全
   ```

3. **记录性能指标**
   ```python
   if meta.ms > 500:
       log.warning("检索过慢，考虑优化")
   ```

4. **配置外部化**
   ```bash
   # .env
   TOPK=10
   ```

### ❌ DON'T

1. **不要绕过引擎层**
   ```python
   # ❌ 不推荐
   from src.fabric_clip_ranker import recommend_fabrics_clip
   
   # ✅ 推荐
   from src.core.recommender import recommend
   ```

2. **不要硬编码参数**
   ```python
   # ❌
   result, meta = recommend(img, top_k=5, topc=12)
   
   # ✅ 使用默认值或配置
   result, meta = recommend(img)
   ```

3. **不要忽略性能指标**
   ```python
   result, _ = recommend(img)  # ❌ 丢弃 meta
   ```

---

## 🔗 相关文档

- [数据类型](./TYPES_GUIDE.md) - `ScoreItem`, `RankedResult`, `QueryMeta`
- [配置管理](./CONFIG_GUIDE.md) - `src/config.py`
- [日志系统](./LOGGER_GUIDE.md) - `src/utils/logger.py`
- [CLIP 实现](../CLIP_IMPLEMENTATION_SUMMARY.md)

---

## 💡 后续改进

1. **批量推荐** - 支持一次处理多张图片
2. **流式输出** - 实时返回中间结果
3. **A/B 测试** - 对比不同参数配置
4. **结果解释** - 可视化相似样本

---

✅ **统一推荐引擎已就绪！** 现在可以在 `app.py` 中一行调用完成推荐。 🎉

