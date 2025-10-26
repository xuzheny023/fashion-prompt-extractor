# 引擎路由器代码结构

## 📊 重构前后对比

### ❌ 重构前 (混乱的单体函数)

```python
@st.cache_data(show_spinner=False, ttl=7200)
def analyze_image(image_path: str, engine: str = "cloud_qwen", lang: str = "zh") -> Dict:
    """使用云端 VLM 分析面料图片"""
    
    # 引擎检查
    if engine == "cloud_qwen":
        pass
    elif engine == "cloud_gpt4o":
        raise NotImplementedError(...)
    elif engine == "cloud_gemini":
        raise NotImplementedError(...)
    else:
        raise ValueError(...)
    
    # Qwen-VL 实现（耦合在路由器中）
    if MultiModalConversation is None:
        raise RuntimeError("dashscope is not installed")
    
    api_key = _need_secret("DASHSCOPE_API_KEY")
    prompt = _build_prompt(lang)
    
    resp = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-vl-plus",
        messages=[...]
    )
    
    text = (resp.output.get("text") or "").strip()
    mats = _extract_materials(text, topk=3)
    conf = [0.6, 0.25, 0.15][:len(mats)] if mats else []
    
    return {
        "materials": mats,
        "confidence": conf,
        "description": text,
        "engine": engine,
        "cache_key": _md5_file(image_path)
    }
```

**问题**:
- ❌ 路由逻辑和实现逻辑混在一起
- ❌ 添加新引擎需要修改大量代码
- ❌ 难以测试单个引擎
- ❌ 职责不清晰

---

### ✅ 重构后 (清晰的职责分离)

```python
# ============================================================
# 引擎实现层 (Engine Implementations)
# ============================================================

def _analyze_qwen(image_path: str, lang: str = "zh") -> Dict:
    """
    使用 Qwen-VL 分析面料图片。
    
    职责: 仅负责 Qwen-VL 的推理逻辑
    """
    if MultiModalConversation is None:
        raise RuntimeError("dashscope is not installed. pip install dashscope")
    
    api_key = _need_secret("DASHSCOPE_API_KEY")
    prompt = _build_prompt(lang)
    
    resp = MultiModalConversation.call(
        api_key=api_key,
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [
                {"image": image_path},
                {"text": prompt}
            ]
        }]
    )
    
    text = (resp.output.get("text") or "").strip()
    mats = _extract_materials(text, topk=3)
    conf = [0.6, 0.25, 0.15][:len(mats)] if mats else []
    
    return {
        "materials": mats,
        "confidence": conf,
        "description": text,
        "engine": "cloud_qwen",
        "cache_key": _md5_file(image_path)
    }


# 未来可以轻松添加：
# def _analyze_gpt4o(image_path: str, lang: str = "zh") -> Dict:
#     """使用 GPT-4o-mini 分析面料图片"""
#     ...
#
# def _analyze_gemini(image_path: str, lang: str = "zh") -> Dict:
#     """使用 Gemini 分析面料图片"""
#     ...


# ============================================================
# 路由层 (Router Layer)
# ============================================================

@st.cache_data(show_spinner=False, ttl=7200)
def analyze_image(image_path: str, engine: str = "cloud_qwen", lang: str = "zh") -> Dict:
    """
    使用云端 VLM 分析面料图片 - 引擎路由器。
    
    职责: 仅负责根据 engine 参数分发请求
    """
    # Engine router
    if engine == "cloud_qwen":
        return _analyze_qwen(image_path, lang=lang)
    elif engine == "cloud_gpt4o":
        raise RuntimeError("engine cloud_gpt4o not implemented yet")
    elif engine == "cloud_gemini":
        raise RuntimeError("engine cloud_gemini not implemented yet")
    else:
        raise ValueError(f"Unknown engine: {engine}")
```

**优势**:
- ✅ 职责清晰: 路由器只做路由，实现只做实现
- ✅ 易于扩展: 添加新引擎只需实现新函数并添加路由分支
- ✅ 易于测试: 可以单独测试 `_analyze_qwen()`
- ✅ 易于维护: 修改 Qwen-VL 逻辑不影响路由器

---

## 🏗️ 架构层次

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (app_new.py)                │
│  • 用户选择引擎                                          │
│  • 前端保护: if engine != "cloud_qwen": st.warning()   │
│  • 调用: analyze_image(path, engine, lang)             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Router Layer (analyze_image)               │
│  • 接收请求                                             │
│  • 根据 engine 参数分发                                 │
│  • 统一缓存 (@st.cache_data)                           │
└─────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ _analyze_qwen │  │_analyze_gpt4o │  │_analyze_gemini│
│               │  │               │  │               │
│ ✅ 已实现     │  │ 🚧 待实现     │  │ 🚧 待实现     │
│               │  │               │  │               │
│ Qwen-VL API   │  │ OpenAI API    │  │ Google API    │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## 🔄 数据流

### 成功流程 (cloud_qwen)

```
用户上传图片
  ↓
app_new.py: 前端检查通过
  ↓
调用 analyze_image(path, engine="cloud_qwen", lang="zh")
  ↓
Router: if engine == "cloud_qwen"
  ↓
调用 _analyze_qwen(path, lang="zh")
  ↓
检查 MultiModalConversation
  ↓
获取 DASHSCOPE_API_KEY
  ↓
调用 Qwen-VL API
  ↓
提取材料 + 生成置信度
  ↓
返回结果字典
  ↓
Router: 返回给前端
  ↓
app_new.py: 渲染 Top-3 + 推理文本
```

### 错误流程 (cloud_gpt4o)

```
用户选择 GPT-4o-mini
  ↓
app_new.py: 前端检查
  ↓
if engine != "cloud_qwen":
  ↓
st.warning("该引擎尚未实现")
st.stop()  ← 优雅停止
```

### 备用防线 (如果前端被绕过)

```
调用 analyze_image(path, engine="cloud_gpt4o")
  ↓
Router: elif engine == "cloud_gpt4o"
  ↓
raise RuntimeError("engine cloud_gpt4o not implemented yet")
  ↓
app_new.py: except Exception as e
  ↓
st.error(f"云端分析失败：{e}")
```

---

## 📝 代码位置

### src/fabric_api_infer.py

| 行号 | 内容 | 说明 |
|------|------|------|
| 1-112 | 导入、错误类、辅助函数 | `_need_secret`, `_md5_file`, `_extract_materials`, `_build_prompt` |
| 115-158 | `_analyze_qwen()` | Qwen-VL 实现 |
| 163-197 | `analyze_image()` | 引擎路由器 |
| 189-197 | 路由逻辑 | `if/elif/else` 分支 |

### app_new.py

| 行号 | 内容 | 说明 |
|------|------|------|
| 43-60 | 侧边栏引擎选择 | `st.selectbox` + API Key 状态 |
| 107-110 | 前端保护 | `if engine != "cloud_qwen": st.warning()` |
| 119-120 | 调用路由器 | `analyze_image(patch_path, engine=engine, lang=lang)` |

---

## 🎯 添加新引擎的步骤

### 示例: 添加 GPT-4o-mini

#### 步骤 1: 实现引擎函数

```python
# src/fabric_api_infer.py

def _analyze_gpt4o(image_path: str, lang: str = "zh") -> Dict:
    """使用 GPT-4o-mini 分析面料图片"""
    try:
        import openai
    except ImportError:
        raise RuntimeError("openai is not installed. pip install openai")
    
    api_key = _need_secret("OPENAI_API_KEY")
    prompt = _build_prompt(lang)
    
    # 调用 OpenAI API
    # ...
    
    return {
        "materials": mats,
        "confidence": conf,
        "description": text,
        "engine": "cloud_gpt4o",
        "cache_key": _md5_file(image_path)
    }
```

#### 步骤 2: 更新路由器

```python
# src/fabric_api_infer.py

def analyze_image(image_path: str, engine: str = "cloud_qwen", lang: str = "zh") -> Dict:
    # Engine router
    if engine == "cloud_qwen":
        return _analyze_qwen(image_path, lang=lang)
    elif engine == "cloud_gpt4o":
        return _analyze_gpt4o(image_path, lang=lang)  # ← 修改这里
    elif engine == "cloud_gemini":
        raise RuntimeError("engine cloud_gemini not implemented yet")
    else:
        raise ValueError(f"Unknown engine: {engine}")
```

#### 步骤 3: 更新前端检查

```python
# app_new.py

if engine not in ["cloud_qwen", "cloud_gpt4o"]:  # ← 添加 "cloud_gpt4o"
    st.warning("⚠️ 该引擎尚未实现，当前仅支持 Qwen-VL。")
    st.info("请在侧边栏选择 'Cloud · Qwen-VL' 引擎。")
    st.stop()
```

#### 步骤 4: 更新 UI 标签

```python
# app_new.py

engine_label = st.selectbox(
    "云端模型 / Cloud Engine",
    [
        "Cloud · Qwen-VL",
        "Cloud · GPT-4o-mini",  # ← 移除 "(coming soon)"
        "Cloud · Gemini (coming soon)"
    ],
    index=0
)
```

#### 步骤 5: 添加依赖

```bash
# requirements.txt
streamlit
pillow
numpy
dashscope
streamlit-cropper
openai  # ← 新增
```

---

## ✅ 验收清单

### 代码质量

- [x] `_analyze_qwen()` 函数独立且完整
- [x] `analyze_image()` 仅负责路由
- [x] 语法验证通过
- [x] 保持缓存装饰器 `@st.cache_data`
- [x] 保持 `NoAPIKeyError` 检查
- [x] 错误类型正确 (`RuntimeError`, `ValueError`)

### 功能验证

- [x] `cloud_qwen` 正常工作
- [x] `cloud_gpt4o` 抛出 `RuntimeError`
- [x] `cloud_gemini` 抛出 `RuntimeError`
- [x] 未知引擎抛出 `ValueError`
- [x] 前端保护正常工作

### 可维护性

- [x] 职责清晰分离
- [x] 易于添加新引擎
- [x] 易于测试单个引擎
- [x] 代码结构清晰

---

## 🚀 总结

### 重构收益

1. **职责分离**: 路由器和实现完全解耦
2. **易于扩展**: 添加新引擎只需 3-5 步
3. **易于测试**: 可以单独测试每个引擎
4. **易于维护**: 修改一个引擎不影响其他部分
5. **代码清晰**: 结构一目了然

### 下一步

当需要添加 GPT-4o-mini 或 Gemini 支持时：
1. 实现 `_analyze_gpt4o()` 或 `_analyze_gemini()`
2. 在路由器中添加一行: `return _analyze_xxx(...)`
3. 更新前端检查列表
4. 完成！

---

**更新时间**: 2025-10-24  
**版本**: 6.5 (Engine Router Refactor)  
**状态**: ✅ 完成并验证通过

