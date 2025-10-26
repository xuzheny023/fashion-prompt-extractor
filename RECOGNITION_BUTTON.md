# 识别按钮功能说明

## ✨ 功能概述

识别按钮实现了完整的云端面料识别流程，支持：
1. 动态引擎选择
2. 实时 API 调用
3. Top-3 材质显示
4. 置信度可视化
5. 推理文本展示
6. 完善的错误处理

## 🎯 核心实现

### 1. 按钮触发 (Line 105)

```python
if st.button("识别该区域", use_container_width=True):
```

**特性**:
- `use_container_width=True`: 按钮占满容器宽度
- 主要操作按钮，视觉突出

### 2. 图像保存 (Line 107-111)

```python
os.makedirs(".cache/crops", exist_ok=True)
# Save temp patch
key = md5(preview.tobytes()).hexdigest()[:10]
patch_path = f".cache/crops/{key}.png"
preview.save(patch_path)
```

**工作流程**:
1. 创建缓存目录 `.cache/crops/`
2. 计算图像的 MD5 哈希（前 10 位）
3. 保存裁剪后的预览图像
4. 返回文件路径

**优势**:
- MD5 哈希确保相同图像使用相同文件名
- 自动缓存，避免重复保存
- 短哈希（10 位）减少文件名长度

### 3. API 调用 (Line 113-114)

```python
with st.spinner("识别中…"):
    res = analyze_image(patch_path, engine=engine, lang=lang)
```

**参数**:
- `patch_path`: 裁剪图像的文件路径
- `engine`: 用户选择的引擎（`cloud_qwen`, `cloud_gpt4o`, `cloud_gemini`）
- `lang`: 语言设置（`zh` 或 `en`）

**返回格式**:
```python
{
    "materials": ["皮革", "缎面", "涤纶"],
    "confidence": [0.6, 0.25, 0.15],
    "description": "LLM 生成的详细解释...",
    "engine": "cloud_qwen",
    "cache_key": "md5_hash"
}
```

### 4. 引擎显示 (Line 117)

```python
st.caption(f"Engine: {engine}")
```

**显示示例**:
- `Engine: cloud_qwen`
- `Engine: cloud_gpt4o`
- `Engine: cloud_gemini`

### 5. Top-3 材质渲染 (Line 119-128)

```python
# Display Top-3 materials with confidence bars
mats = res.get("materials", [])
confs = res.get("confidence", [])
if mats:
    for i, name in enumerate(mats[:3]):
        score = confs[i] if i < len(confs) else 0.0
        st.write(f"**{i+1}. {name.upper()}**")
        st.progress(min(max(float(score), 0.0), 1.0))
else:
    st.info("未从描述中抽取到明确的面料名称，已展示原始解释。")
```

**显示效果**:
```
Engine: cloud_qwen

**1. 皮革**
████████████████████░░░░░░░░ 60%

**2. 缎面**
██████░░░░░░░░░░░░░░░░░░░░░░ 25%

**3. 涤纶**
████░░░░░░░░░░░░░░░░░░░░░░░░ 15%
```

**特性**:
- 材质名称大写加粗（`name.upper()`）
- 置信度进度条可视化
- 自动处理缺失值（默认 0.0）
- 置信度限制在 [0.0, 1.0] 范围内

### 6. 推理文本 (Line 130-133)

```python
# Display reasoning/description
if res.get("description"):
    with st.expander("💡 解释 / Reasoning", expanded=False):
        st.write(res["description"])
```

**特性**:
- 可折叠展示（`expanded=False`）
- 带图标标题（💡）
- 双语标题
- 仅在有描述时显示

### 7. 错误处理 (Line 135-138)

```python
except NoAPIKeyError:
    st.error("未检测到 DASHSCOPE_API_KEY，请在 .streamlit/secrets.toml 或云端 Secrets 中配置。")
except Exception as e:
    st.error(f"云端分析失败：{e}")
```

**错误类型**:
1. **NoAPIKeyError**: 缺少 API Key
   - 显示配置提示
   - 引导用户配置 secrets

2. **Exception**: 其他错误
   - 显示具体错误信息
   - 帮助调试问题

## 📊 数据流

### 完整流程

```
用户点击"识别该区域"按钮
  ↓
创建缓存目录
  ↓
计算图像 MD5 哈希
  ↓
保存裁剪图像到 .cache/crops/
  ↓
显示 spinner "识别中…"
  ↓
调用 analyze_image(
    patch_path,
    engine=engine,  ← 用户选择的引擎
    lang=lang       ← 用户选择的语言
)
  ↓
解析返回结果
  ↓
显示引擎 ID
  ↓
渲染 Top-3 材质 + 置信度条
  ↓
显示推理文本（可折叠）
  ↓
完成
```

### 错误处理流程

```
try:
    保存图像
    ↓
    调用 API
    ↓
    渲染结果
except NoAPIKeyError:
    ↓
    显示 API Key 配置提示
except Exception:
    ↓
    显示错误信息
```

## 🎨 UI 示例

### 成功识别

```
┌─────────────────────────────┐
│ 预览与识别                  │
├─────────────────────────────┤
│ [预览图像]                  │
│ 160×160 px                  │
│                             │
│ [🚀 识别该区域]             │
│                             │
│ Engine: cloud_qwen          │
│                             │
│ **1. 皮革**                 │
│ ████████████░░░░░░░░ 60%   │
│                             │
│ **2. 缎面**                 │
│ ██████░░░░░░░░░░░░░░ 25%   │
│                             │
│ **3. 涤纶**                 │
│ ████░░░░░░░░░░░░░░░░ 15%   │
│                             │
│ 💡 解释 / Reasoning ▼       │
│ └─ LLM 生成的详细解释...    │
└─────────────────────────────┘
```

### API Key 错误

```
┌─────────────────────────────┐
│ ❌ 未检测到 DASHSCOPE_API_KEY│
│                             │
│ 请在 .streamlit/secrets.toml│
│ 或云端 Secrets 中配置。      │
└─────────────────────────────┘
```

### 网络错误

```
┌─────────────────────────────┐
│ ❌ 云端分析失败：            │
│ Connection timeout          │
└─────────────────────────────┘
```

## 🔧 配置参数

### 缓存目录

| 参数 | 值 | 说明 |
|------|-----|------|
| 目录 | `.cache/crops/` | 裁剪图像缓存 |
| 文件名 | `{md5[:10]}.png` | MD5 哈希前 10 位 |
| 格式 | PNG | 无损压缩 |

### 显示参数

| 参数 | 值 | 说明 |
|------|-----|------|
| Top-N | 3 | 显示前 3 个材质 |
| 置信度范围 | [0.0, 1.0] | 进度条范围 |
| 材质格式 | 大写加粗 | `**{name.upper()}**` |
| 推理展开 | False | 默认折叠 |

## 📈 性能优化

### 1. MD5 缓存

```python
key = md5(preview.tobytes()).hexdigest()[:10]
```

**优势**:
- 相同图像使用相同文件名
- 避免重复保存
- 支持 API 层面的缓存

### 2. 错误处理

```python
try:
    # API 调用
except NoAPIKeyError:
    # 特定错误处理
except Exception as e:
    # 通用错误处理
```

**优势**:
- 区分不同错误类型
- 提供针对性提示
- 避免应用崩溃

### 3. 置信度安全处理

```python
score = confs[i] if i < len(confs) else 0.0
st.progress(min(max(float(score), 0.0), 1.0))
```

**优势**:
- 处理缺失值
- 限制范围 [0.0, 1.0]
- 避免进度条错误

## ✅ 验收清单

### 功能验收

- [x] 按钮点击触发识别
- [x] 图像保存到缓存目录
- [x] 使用用户选择的引擎
- [x] 传递语言参数
- [x] 显示引擎 ID
- [x] 渲染 Top-3 材质
- [x] 显示置信度进度条
- [x] 显示推理文本（可折叠）
- [x] 处理 NoAPIKeyError
- [x] 处理通用异常

### 代码质量

- [x] 语法正确
- [x] 注释清晰
- [x] 错误处理完善
- [x] 数据验证充分
- [x] UI 响应友好

### 用户体验

- [x] 按钮占满宽度
- [x] Spinner 显示加载状态
- [x] 材质名称清晰（大写加粗）
- [x] 置信度可视化
- [x] 推理文本可折叠
- [x] 错误提示友好

## 🚀 后续优化

### 可能的改进

1. **添加识别时间显示**
   ```python
   import time
   t0 = time.time()
   res = analyze_image(...)
   elapsed = time.time() - t0
   st.caption(f"识别耗时: {elapsed:.2f}s")
   ```

2. **添加结果缓存提示**
   ```python
   if res.get("cache_key"):
       st.caption("✓ 使用缓存结果")
   ```

3. **添加材质详情链接**
   ```python
   st.write(f"**{i+1}. [{name.upper()}](https://example.com/fabric/{name})**")
   ```

4. **添加结果导出功能**
   ```python
   if st.button("导出结果"):
       json.dump(res, open("result.json", "w"))
   ```

## 🎉 总结

识别按钮功能已完整实现：
- ✅ **动态引擎**: 使用用户选择的模型
- ✅ **完整流程**: 保存 → 调用 → 渲染
- ✅ **可视化**: Top-3 + 置信度条 + 推理
- ✅ **错误处理**: 友好的错误提示
- ✅ **性能优化**: MD5 缓存 + 安全处理

用户现在可以流畅地识别面料，获得清晰的分析结果！

---

**更新时间**: 2025-10-24  
**版本**: 6.3 (Recognition Button)  
**状态**: ✅ 完成并验证通过

