# 模型选择器功能说明

## ✨ 新增功能

### 1. 云端模型选择器

在侧边栏顶部添加了模型选择下拉框，支持 3 种云端引擎：

```python
engine_label = st.selectbox(
    "云端模型 / Cloud Engine",
    ["Cloud · Qwen-VL", 
     "Cloud · GPT-4o-mini (coming soon)", 
     "Cloud · Gemini (coming soon)"],
    index=0
)
```

**引擎映射**:
- `Cloud · Qwen-VL` → `cloud_qwen` (默认，已实现)
- `Cloud · GPT-4o-mini (coming soon)` → `cloud_gpt4o` (待实现)
- `Cloud · Gemini (coming soon)` → `cloud_gemini` (待实现)

### 2. API Key 状态检查

新增 `_has_key()` 辅助函数，检查所选引擎的 API Key 是否配置：

```python
def _has_key(engine: str) -> bool:
    """Check if the required API key exists for the given engine."""
    if engine == "cloud_qwen":
        return bool(st.secrets.get("DASHSCOPE_API_KEY")) or bool(os.getenv("DASHSCOPE_API_KEY"))
    if engine == "cloud_gpt4o":
        return bool(st.secrets.get("OPENAI_API_KEY")) or bool(os.getenv("OPENAI_API_KEY"))
    if engine == "cloud_gemini":
        return bool(st.secrets.get("GOOGLE_API_KEY")) or bool(os.getenv("GOOGLE_API_KEY"))
    return False
```

**检查来源**:
1. Streamlit Secrets (`.streamlit/secrets.toml`)
2. 环境变量 (`os.getenv()`)

### 3. 实时状态徽章

根据 API Key 配置状态显示不同的徽章：

| 状态 | 显示 | 颜色 | 说明 |
|------|------|------|------|
| **已配置** | ✅ API Key 已配置 | 绿色 | 可以正常使用 |
| **缺少 Key** | ❌ 缺少 DASHSCOPE_API_KEY | 红色 | 需要配置 API Key |
| **未实现** | ℹ️ 该引擎尚未开通或未实现 | 蓝色 | 功能开发中 |

```python
# API Key status badge
if _has_key(engine):
    st.success(f"✅ API Key 已配置")
else:
    if engine == "cloud_qwen":
        st.error("❌ 缺少 DASHSCOPE_API_KEY")
    else:
        st.info("ℹ️ 该引擎尚未开通或未实现。")
```

## 🎯 使用流程

### 用户视角

```
1. 打开应用
   ↓
2. 在侧边栏选择云端模型
   ↓
3. 查看 API Key 状态
   ├─ ✅ 已配置 → 可以使用
   └─ ❌ 未配置 → 需要配置
   ↓
4. 上传图片 → 裁剪 → 识别
   ↓
5. 使用所选引擎进行推理
```

### 开发者视角

```python
# 1. 用户选择模型
engine_label = st.selectbox(...)

# 2. 映射到引擎 ID
engine = {"Cloud · Qwen-VL": "cloud_qwen", ...}[engine_label]

# 3. 检查 API Key
if _has_key(engine):
    # 显示成功状态
else:
    # 显示错误或提示

# 4. 调用推理
res = analyze_image(patch_path, engine=engine, lang=lang)
```

## 📋 API Key 配置

### Qwen-VL (已实现)

**方法 1: Streamlit Secrets**
```toml
# .streamlit/secrets.toml
DASHSCOPE_API_KEY = "sk-your-dashscope-key"
```

**方法 2: 环境变量**
```bash
export DASHSCOPE_API_KEY="sk-your-dashscope-key"
```

### GPT-4o-mini (待实现)

**方法 1: Streamlit Secrets**
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-your-openai-key"
```

**方法 2: 环境变量**
```bash
export OPENAI_API_KEY="sk-your-openai-key"
```

### Gemini (待实现)

**方法 1: Streamlit Secrets**
```toml
# .streamlit/secrets.toml
GOOGLE_API_KEY = "your-google-api-key"
```

**方法 2: 环境变量**
```bash
export GOOGLE_API_KEY="your-google-api-key"
```

## 🔧 技术实现

### 代码结构

```
app_new.py (115 行)
├── _has_key() 函数 (Line 21-38)
│   ├── 检查 cloud_qwen
│   ├── 检查 cloud_gpt4o
│   └── 检查 cloud_gemini
│
├── 侧边栏 (Line 42-70)
│   ├── 模型选择器 (Line 46-55)
│   ├── API Key 状态 (Line 58-64)
│   └── 其他参数 (Line 68-70)
│
└── 识别逻辑 (Line 110)
    └── analyze_image(engine=engine)
```

### 关键变量

| 变量 | 类型 | 说明 |
|------|------|------|
| `engine_label` | str | 用户可读的模型名称 |
| `engine` | str | 引擎 ID (`cloud_qwen`, `cloud_gpt4o`, `cloud_gemini`) |
| `_has_key(engine)` | bool | API Key 是否配置 |

## 🎨 UI 示例

### 侧边栏布局

```
┌─────────────────────────────┐
│ 参数                        │
├─────────────────────────────┤
│ 云端模型 / Cloud Engine     │
│ [Cloud · Qwen-VL ▼]        │
│                             │
│ ✅ API Key 已配置           │
├─────────────────────────────┤
│ 选框大小(px)                │
│ ━━━●━━━━━━━ 160            │
│                             │
│ 预览放大倍数                │
│ ━━━●━━━━━━━ 1.6            │
│                             │
│ 语言 / Language             │
│ ◉ zh  ○ en                 │
└─────────────────────────────┘
```

### 状态徽章示例

**Qwen-VL (已配置)**
```
✅ API Key 已配置
```

**Qwen-VL (未配置)**
```
❌ 缺少 DASHSCOPE_API_KEY
```

**GPT-4o-mini (未实现)**
```
ℹ️ 该引擎尚未开通或未实现。
```

## 📊 代码统计

| 指标 | 数值 |
|------|------|
| 总行数 | 115 行 |
| 新增行数 | +30 行 |
| 新增函数 | 1 个 (`_has_key`) |
| 支持引擎 | 3 个 |
| 已实现引擎 | 1 个 (Qwen-VL) |

## ✅ 验收清单

- [x] 模型选择器已添加
- [x] 支持 3 种云端引擎
- [x] `_has_key()` 函数已实现
- [x] 支持 Streamlit Secrets
- [x] 支持环境变量
- [x] 实时状态徽章显示
- [x] 引擎动态传递到 `analyze_image()`
- [x] 语法验证通过
- [x] 未实现引擎显示友好提示

## 🚀 后续开发

### GPT-4o-mini 集成

1. 在 `src/fabric_api_infer.py` 中添加 GPT-4o-mini 支持
2. 实现 OpenAI API 调用
3. 统一返回格式
4. 更新模型选择器标签（移除 "coming soon"）

### Gemini 集成

1. 在 `src/fabric_api_infer.py` 中添加 Gemini 支持
2. 实现 Google AI API 调用
3. 统一返回格式
4. 更新模型选择器标签（移除 "coming soon"）

## 🎉 总结

模型选择器功能已完整实现：
- ✅ **UI 组件**: 下拉选择框 + 状态徽章
- ✅ **API Key 检查**: 支持 3 种引擎
- ✅ **动态引擎**: 根据用户选择调用不同模型
- ✅ **友好提示**: 未配置或未实现时显示清晰信息
- ✅ **扩展性**: 易于添加新的云端引擎

---

**更新时间**: 2025-10-24  
**版本**: 6.1 (Model Selector)  
**状态**: ✅ 完成并验证通过

