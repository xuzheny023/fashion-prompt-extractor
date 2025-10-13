# 标准化数据类型指南

## 📦 概述

`src/types.py` 定义了项目中统一的数据结构，确保函数返回值的一致性和可维护性。

## 📋 核心类型

### 1️⃣ ScoreItem - 评分项

单个评分结果，包含标签和置信度。

```python
from src.types import ScoreItem

item = ScoreItem(label="cotton", score=0.85)
print(f"{item.label}: {item.score:.2%}")  # cotton: 85.00%
```

**字段:**
- `label: str` - 标签/类别名称
- `score: float` - 置信度分数 [0.0, 1.0]

**验证:**
- `label` 必须是字符串
- `score` 必须在 [0.0, 1.0] 范围内

---

### 2️⃣ RankedResult - 排名结果

包含多个评分项的排名列表。

```python
from src.types import RankedResult, ScoreItem

result = RankedResult(
    items=[
        ScoreItem("cotton", 0.89),
        ScoreItem("linen", 0.76),
        ScoreItem("silk", 0.68),
    ],
    ai_reason="基于 CLIP 双通道特征匹配"
)
```

**字段:**
- `items: List[ScoreItem]` - 评分项列表
- `ai_reason: str` - AI 推理原因（可选）

**属性:**
- `top1` - 得分最高的项
- `top3` - 得分前3的项

**方法:**
- `get_top_k(k=5)` - 获取前 K 个结果
- `filter_by_threshold(threshold=0.5)` - 过滤低于阈值的结果

---

### 3️⃣ QueryMeta - 查询元数据

查询的性能指标。

```python
from src.types import QueryMeta

meta = QueryMeta(ms=150, coarse_max=0.92)
print(f"耗时: {meta.ms}ms")
print(f"秒: {meta.seconds:.3f}s")
print(f"快速: {meta.is_fast()}")  # True if <= 200ms
```

**字段:**
- `ms: int` - 查询耗时（毫秒）
- `coarse_max: float` - 粗排阶段最高分

**属性:**
- `seconds` - 耗时（秒）

**方法:**
- `is_fast(threshold_ms=200)` - 判断是否快速

---

## 🎯 使用场景

### 场景1: 更新推荐函数签名

**之前:**
```python
def recommend_fabrics(image):
    # ...
    return [(label1, score1, display1), (label2, score2, display2)]
```

**之后:**
```python
from src.types import RankedResult, QueryMeta, ScoreItem
import time

def recommend_fabrics(image) -> tuple[RankedResult, QueryMeta]:
    t0 = time.perf_counter()
    
    # ... 检索逻辑 ...
    raw_results = [("cotton", 0.89), ("linen", 0.76)]
    
    # 转换为标准类型
    items = [ScoreItem(label=lbl, score=scr) for lbl, scr in raw_results]
    result = RankedResult(
        items=items,
        ai_reason="CLIP 双通道匹配"
    )
    
    # 性能指标
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    meta = QueryMeta(ms=elapsed_ms, coarse_max=0.92)
    
    return result, meta
```

---

### 场景2: UI 中使用

**Streamlit 示例:**

```python
from src.types import RankedResult, QueryMeta
import streamlit as st

# 获取结果
result, meta = recommend_fabrics(uploaded_image)

# 显示性能
st.caption(f"⚡ 查询耗时: {meta.ms}ms · 粗排最高分: {meta.coarse_max:.2f}")

# 显示前3推荐
st.subheader("推荐结果")
for i, item in enumerate(result.top3, 1):
    st.write(f"**{i}. {item.label}**")
    st.progress(item.score)  # 0.0-1.0 自动转百分比
    st.caption(f"置信度: {item.score:.2%}")

# 显示 AI 推理
if result.ai_reason:
    st.info(f"💡 {result.ai_reason}")

# 只显示高置信度结果
high_conf = result.filter_by_threshold(0.70)
st.write(f"高置信度结果 ({len(high_conf)}):")
for item in high_conf:
    st.write(f"- {item.label}: {item.score:.2%}")
```

---

### 场景3: 日志记录

```python
from src.utils.logger import get_logger
from src.types import RankedResult, QueryMeta

log = get_logger("fabric_recommender")

result, meta = recommend_fabrics(image)

# 记录性能
if meta.is_fast():
    log.info(f"快速检索完成: {meta.ms}ms")
else:
    log.warning(f"检索较慢: {meta.ms}ms (建议优化)")

# 记录结果
log.info(f"Top 1: {result.top1.label} ({result.top1.score:.2f})")
log.debug(f"所有结果: {[(item.label, item.score) for item in result.items]}")
```

---

### 场景4: 结果过滤与处理

```python
from src.types import RankedResult

result, meta = recommend_fabrics(image)

# 获取前5
top5 = result.get_top_k(k=5)

# 过滤低置信度
confident = result.filter_by_threshold(0.60)

# 检查最佳结果
if result.top1.score >= 0.80:
    print(f"高置信度推荐: {result.top1.label}")
elif result.top1.score >= 0.50:
    print(f"中等置信度推荐: {result.top1.label}")
else:
    print("置信度较低，建议人工确认")
```

---

## ✅ 迁移清单

将现有代码迁移到标准类型：

### 1. `src/fabric_clip_ranker.py`

```python
# 修改 recommend_fabrics_clip 返回值
def recommend_fabrics_clip(image, top_k=5) -> tuple[RankedResult, QueryMeta]:
    import time
    t0 = time.perf_counter()
    
    # ... 检索逻辑 ...
    
    items = [ScoreItem(label=cls, score=score) for cls, score in results]
    result = RankedResult(items=items)
    meta = QueryMeta(ms=int((time.perf_counter()-t0)*1000), coarse_max=coarse_max)
    
    return result, meta
```

### 2. `app.py`

```python
# 更新 UI 调用
if use_clip:
    result, meta = recommend_fabrics_clip(image)
    
    # 显示性能
    st.caption(f"⚡ {meta.ms}ms · 粗排: {meta.coarse_max:.2f}")
    
    # 显示结果
    for i, item in enumerate(result.items, 1):
        display_name = get_label(item.label) if lang == "zh" else item.label
        st.write(f"{i}. **{display_name}** — {item.score:.2f}")
        st.progress(item.score)
```

### 3. `src/region_recommender.py`

```python
# 统一规则引擎返回值
def recommend_from_features(features) -> RankedResult:
    # ... 规则匹配 ...
    
    items = [ScoreItem(label=name, score=score) for name, score in matches]
    return RankedResult(items=items, ai_reason="基于规则引擎匹配")
```

---

## 🎨 类型注解示例

```python
from typing import List, Tuple
from src.types import RankedResult, QueryMeta, ScoreItem

# 函数签名
def rank_fabrics(scores: List[Tuple[str, float]]) -> RankedResult:
    items = [ScoreItem(label=lbl, score=scr) for lbl, scr in scores]
    return RankedResult(items=items)

# 返回多个值
def search_with_meta(query: str) -> Tuple[RankedResult, QueryMeta]:
    result = rank_fabrics([("cotton", 0.85)])
    meta = QueryMeta(ms=150)
    return result, meta

# 可选返回
from typing import Optional

def try_recommend(image) -> Optional[RankedResult]:
    if not is_valid(image):
        return None
    # ...
    return RankedResult(items=items)
```

---

## 🧪 测试

运行测试：

```bash
python tools/test_types.py
```

测试内容：
- ✅ 数据验证（类型、范围）
- ✅ 属性访问（top1, top3）
- ✅ 方法调用（get_top_k, filter_by_threshold）
- ✅ 综合场景模拟

---

## 📝 最佳实践

### ✅ DO

1. **始终使用标准类型返回结果**
   ```python
   def recommend(...) -> tuple[RankedResult, QueryMeta]:
   ```

2. **为 AI 推理添加解释**
   ```python
   RankedResult(items=items, ai_reason="基于纹理特征匹配")
   ```

3. **记录性能指标**
   ```python
   QueryMeta(ms=elapsed_ms, coarse_max=max_score)
   ```

4. **利用内置方法简化代码**
   ```python
   result.top3  # 而不是 result.items[:3]
   ```

### ❌ DON'T

1. **不要返回原始元组/列表**
   ```python
   # ❌ 旧方式
   return [("cotton", 0.85, "棉"), ("linen", 0.72, "亚麻")]
   
   # ✅ 新方式
   items = [ScoreItem("cotton", 0.85), ScoreItem("linen", 0.72)]
   return RankedResult(items=items)
   ```

2. **不要忽略性能指标**
   ```python
   # ❌
   return results
   
   # ✅
   return results, QueryMeta(ms=elapsed_ms)
   ```

3. **不要手动验证数据范围**
   ```python
   # ❌ 手动检查
   if score < 0 or score > 1:
       raise ValueError("...")
   
   # ✅ dataclass 自动验证
   item = ScoreItem(label="test", score=score)
   ```

---

## 🔗 相关文档

- [配置管理](./CONFIG_GUIDE.md) - `src/config.py`
- [日志系统](./LOGGER_GUIDE.md) - `src/utils/logger.py`
- [CLIP 检索](../CLIP_IMPLEMENTATION_SUMMARY.md)

---

## 💡 后续改进

1. **添加序列化支持** - JSON / Protobuf
2. **扩展元数据** - 添加 model_version, query_id 等
3. **结果缓存** - 基于图片哈希缓存结果
4. **批量推荐** - 支持批量图片处理

---

✅ **数据类型标准化已完成！** 可以开始迁移现有代码了。

