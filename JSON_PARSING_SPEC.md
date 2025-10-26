# JSON 解析规范

## 🎯 目标

实现鲁棒的 JSON 解析，能够处理各种格式的模型响应。

---

## 📋 解析策略

### 方法 1: Markdown 代码块提取

如果响应包含 markdown 代码块：

```
这是一些额外的文本...

```json
{
  "labels": ["皮革", "涤纶"],
  "confidences": [0.8, 0.2],
  "reasoning": "..."
}
```

更多文本...
```

**提取逻辑**:
```python
if "```json" in text:
    json_text = text.split("```json")[1].split("```")[0].strip()
elif "```" in text:
    json_text = text.split("```")[1].split("```")[0].strip()
```

### 方法 2: 正则表达式提取

如果响应包含纯文本 + JSON：

```
根据图片分析，这件衣服的面料是：
{
  "labels": ["皮革", "涤纶"],
  "confidences": [0.8, 0.2],
  "reasoning": "图片显示明显的皮革纹理..."
}
这是我的判断依据。
```

**提取逻辑**:
```python
match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
if match:
    json_text = match.group(0)
```

**正则说明**:
- `\{` - 匹配左花括号
- `[^{}]*` - 匹配非花括号字符
- `(?:\{[^{}]*\}[^{}]*)*` - 匹配嵌套的花括号（非捕获组）
- `\}` - 匹配右花括号
- `re.DOTALL` - `.` 匹配包括换行符在内的所有字符

---

## 🔄 标签归一化

### 归一化映射

使用预定义的 `_NORMALIZE` 映射将不同说法归一到标准词汇：

```python
_NORMALIZE = {
    "真皮": "皮革",
    "仿皮": "皮革",
    "丝缎": "缎面",
    "缎": "缎面",
    "锦纶": "尼龙",
    "聚酯": "涤纶",
    "丹宁": "牛仔",
    "rib": "针织",
    "rayon": "人造丝",
    "viscose": "人造丝",
    "acetate": "醋酸纤维",
    "flannel": "法兰绒"
}
```

### 归一化流程

```python
# 原始标签
labels = ["真皮", "聚酯", "丹宁"]

# 归一化
normalized_labels = [_NORMALIZE.get(label, label) for label in labels]
# 结果: ["皮革", "涤纶", "牛仔"]

# Cap to Top-3
top3_labels = normalized_labels[:3]
```

---

## 📊 置信度处理

### 场景 1: 置信度完整且匹配

```json
{
  "labels": ["皮革", "涤纶", "棉"],
  "confidences": [0.7, 0.2, 0.1]
}
```

**处理**: 直接使用

```python
top3_confidences = confidences[:3]
# 结果: [0.7, 0.2, 0.1]
```

### 场景 2: 置信度缺失

```json
{
  "labels": ["皮革", "涤纶"],
  "confidences": []
}
```

**处理**: 使用默认分布

```python
confidences = [0.6, 0.25, 0.15][:len(normalized_labels)]
# 结果: [0.6, 0.25]
```

### 场景 3: 置信度长度不匹配

```json
{
  "labels": ["皮革", "涤纶", "棉"],
  "confidences": [0.8]
}
```

**处理**: 使用默认分布

```python
if not confidences or len(confidences) != len(normalized_labels):
    confidences = [0.6, 0.25, 0.15][:len(normalized_labels)]
# 结果: [0.6, 0.25, 0.15]
```

### 场景 4: 标签少于3个

```json
{
  "labels": ["皮革"],
  "confidences": [1.0]
}
```

**处理**: 匹配长度

```python
top3_labels = normalized_labels[:3]  # ["皮革"]
top3_confidences = confidences[:3]   # [1.0]

if len(top3_confidences) > len(top3_labels):
    top3_confidences = top3_confidences[:len(top3_labels)]
# 结果: labels=["皮革"], confidences=[1.0]
```

---

## 🛡️ 回退策略

### 场景 1: JSON 解析失败

**输入**:
```
这件衣服看起来是皮革材质的，具有明显的光泽和纹理。
```

**处理**:
```python
except (json.JSONDecodeError, KeyError, ValueError, AttributeError):
    return {
        "materials": [],
        "confidence": [],
        "description": text,  # 保留原始文本
        "engine": "cloud_qwen",
        "cache_key": _md5_file(image_path)
    }
```

**前端显示**:
- 不显示 Top-3 材质（因为 `materials` 为空）
- 显示提示: "未从描述中抽取到明确的面料名称，已展示原始解释。"
- 在 expander 中显示完整的 `description`

---

## 📝 测试用例

### 测试 1: 标准 JSON（markdown 代码块）

**输入**:
```
```json
{
  "labels": ["真皮", "涤纶", "棉"],
  "confidences": [0.75, 0.15, 0.10],
  "reasoning": "夹克呈现明显的皮革光泽和纹理。"
}
```
```

**期望输出**:
```python
{
    "materials": ["皮革", "涤纶", "棉"],  # 归一化
    "confidence": [0.75, 0.15, 0.10],
    "description": "夹克呈现明显的皮革光泽和纹理。",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

### 测试 2: 纯文本 + JSON

**输入**:
```
根据图片分析，面料识别结果如下：
{"labels": ["丝缎", "锦纶"], "confidences": [0.9, 0.1], "reasoning": "光滑的缎面质感"}
以上是我的判断。
```

**期望输出**:
```python
{
    "materials": ["缎面", "尼龙"],  # 归一化
    "confidence": [0.9, 0.1],
    "description": "光滑的缎面质感",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

### 测试 3: 置信度缺失

**输入**:
```json
{
  "labels": ["皮革", "涤纶"],
  "reasoning": "皮革纹理明显"
}
```

**期望输出**:
```python
{
    "materials": ["皮革", "涤纶"],
    "confidence": [0.6, 0.25],  # 默认分布
    "description": "皮革纹理明显",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

### 测试 4: 置信度长度不匹配

**输入**:
```json
{
  "labels": ["皮革", "涤纶", "棉"],
  "confidences": [0.8],
  "reasoning": "主要是皮革"
}
```

**期望输出**:
```python
{
    "materials": ["皮革", "涤纶", "棉"],
    "confidence": [0.6, 0.25, 0.15],  # 默认分布
    "description": "主要是皮革",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

### 测试 5: 超过3个标签

**输入**:
```json
{
  "labels": ["皮革", "涤纶", "棉", "尼龙", "氨纶"],
  "confidences": [0.5, 0.2, 0.15, 0.1, 0.05],
  "reasoning": "混合材质"
}
```

**期望输出**:
```python
{
    "materials": ["皮革", "涤纶", "棉"],  # Cap to Top-3
    "confidence": [0.5, 0.2, 0.15],
    "description": "混合材质",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

### 测试 6: JSON 解析失败

**输入**:
```
这件衣服看起来是皮革材质的，具有明显的光泽和纹理。
```

**期望输出**:
```python
{
    "materials": [],  # 空
    "confidence": [],  # 空
    "description": "这件衣服看起来是皮革材质的，具有明显的光泽和纹理。",
    "engine": "cloud_qwen",
    "cache_key": "..."
}
```

**前端显示**:
```
ℹ️ 未从描述中抽取到明确的面料名称，已展示原始解释。

💡 解释 / Reasoning
这件衣服看起来是皮革材质的，具有明显的光泽和纹理。
```

---

## 🔍 代码实现

### 完整流程

```python
def _analyze_qwen(image_path: str, lang: str = "zh") -> Dict:
    # 1. 调用 Qwen-VL API
    resp = MultiModalConversation.call(...)
    text = (resp.output.get("text") or "").strip()
    
    try:
        # 2. 提取 JSON
        json_text = text
        if "```json" in text:
            json_text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_text = text.split("```")[1].split("```")[0].strip()
        else:
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if match:
                json_text = match.group(0)
        
        # 3. 解析 JSON
        data = json.loads(json_text)
        labels = data.get("labels", [])
        confidences = data.get("confidences", [])
        reasoning = data.get("reasoning", "")
        
        # 4. 归一化标签
        normalized_labels = [_NORMALIZE.get(label, label) for label in labels]
        
        # 5. 处理置信度
        if not confidences or len(confidences) != len(normalized_labels):
            confidences = [0.6, 0.25, 0.15][:len(normalized_labels)]
        
        # 6. Cap to Top-3
        top3_labels = normalized_labels[:3]
        top3_confidences = confidences[:3]
        
        if len(top3_confidences) > len(top3_labels):
            top3_confidences = top3_confidences[:len(top3_labels)]
        
        # 7. 返回结果
        return {
            "materials": top3_labels,
            "confidence": top3_confidences,
            "description": reasoning or text,
            "engine": "cloud_qwen",
            "cache_key": _md5_file(image_path)
        }
    
    except (json.JSONDecodeError, KeyError, ValueError, AttributeError):
        # 8. 回退策略
        return {
            "materials": [],
            "confidence": [],
            "description": text,
            "engine": "cloud_qwen",
            "cache_key": _md5_file(image_path)
        }
```

---

## ✅ 验收清单

- [x] 支持 markdown 代码块提取（```json```）
- [x] 支持正则表达式提取第一个 {...} 块
- [x] 标签归一化到标准形式
- [x] 置信度缺失时使用默认分布 [0.6, 0.25, 0.15]
- [x] 置信度长度不匹配时使用默认分布
- [x] Cap to Top-3
- [x] JSON 解析失败时返回空结果 + 原始文本
- [x] 所有异常都被捕获（JSONDecodeError, KeyError, ValueError, AttributeError）

---

## 🎯 优势

1. **鲁棒性**: 能处理各种格式的响应
2. **容错性**: JSON 解析失败时优雅降级
3. **一致性**: 标签归一化确保输出一致
4. **可预测性**: 置信度总是匹配标签数量
5. **用户友好**: 即使解析失败也能显示原始文本

---

**更新时间**: 2025-10-24  
**版本**: 7.1 (Robust JSON Parsing)  
**状态**: ✅ 已实现并验证

