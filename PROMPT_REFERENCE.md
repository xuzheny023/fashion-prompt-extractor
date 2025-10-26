# 📝 提示词参考卡

## Pass 1: 视觉识别（初始候选生成）

### 中文版本

```
你是专业的纺织品分析师。请仅基于给定的图片块，描述材质并提出最多8个可能的面料名称（开放集，无固定列表）。输出纯JSON：

{
  "candidates": [{"label": "<面料名称>", "confidence": 0.0-1.0}, ...],
  "visual_notes": "<简短备注>"
}

规则：
• 使用简洁的标准名称（如可能）
• 如果不确定，仍提供最佳猜测
• 可以包含具体名称（如"Harris粗花呢"、"雪纺"、"经编针织"、"羊绒"等）
• 不要在JSON外添加任何文本
```

### 英文版本

```
You are a professional textile analyst. Based ONLY on the given image patch, describe the material and propose up to 8 possible fabric names (open-set; no fixed list). Output pure JSON:

{
  "candidates": [{"label": "<fabric name>", "confidence": 0.0-1.0}, ...],
  "visual_notes": "<short notes>"
}

Rules:
• Use concise, canonical names if possible
• If unsure, still provide best guesses
• You may include specific names like 'Harris tweed', 'chiffon', 'warp knit', 'cashmere', etc.
• Do NOT add extra text outside JSON
```

---

## Pass 2: RAG 重排序（基于证据）

### 中文版本

```
给定初始候选和以下网络证据（摘要和URL），重新排序并选择最多5个最终标签及置信度（0..1），并提供简短推理。输出纯JSON：

{
  "labels": [...],
  "confidences": [...],
  "reasoning": "...",
  "evidence": [{"label":"...", "urls":[...]}]
}

指南：
• 优先选择定义/属性与visual_notes匹配的标签（如光泽、纤维类型、编织方式）
• 可以包含具体名称（如"Harris粗花呢"、"雪纺"、"经编针织"、"羊绒"等）
• 如果两个名称是同义词，保留更常见或标准的术语

初始视觉判断：
{visual_notes}

初始候选：
{candidates_str}

网络证据：
{evidence_str}
```

### 英文版本

```
Given the initial candidates and the following web evidence (snippets and URLs), re-rank and select up to 5 final labels with confidences (0..1), and provide a short reasoning. Output pure JSON:

{
  "labels": [...],
  "confidences": [...],
  "reasoning": "...",
  "evidence": [{"label":"...", "urls":[...]}]
}

Guidelines:
• Prefer labels whose definitions/properties match the visual_notes (e.g., luster, fiber type, weave)
• You may include specific names like 'Harris tweed', 'chiffon', 'warp knit', 'cashmere', etc.
• If two names are synonyms, keep the more common or canonical term

Initial Visual Judgment:
{visual_notes}

Initial Candidates:
{candidates_str}

Web Evidence:
{evidence_str}
```

---

## 关键设计原则

### 1. 开放集（Open-Set）
- ❌ 不使用固定词汇表
- ✅ 允许任意面料名称
- ✅ 鼓励专业术语

### 2. 简洁性
- 提示词精简，去除冗余说明
- 直接要求 JSON 格式
- 明确规则（bullet points）

### 3. 鲁棒性
- Pass 1 即使不确定也提供猜测
- Pass 2 综合视觉和证据
- 同义词处理（保留标准术语）

### 4. 语义对齐
- Pass 2 强调与 visual_notes 的匹配
- 考虑光泽、纤维类型、编织方式等属性
- 证据驱动的重排序

---

## 示例输出

### Pass 1 输出

```json
{
  "candidates": [
    {"label": "小羊皮", "confidence": 0.55},
    {"label": "PU皮革", "confidence": 0.20},
    {"label": "牛皮", "confidence": 0.10},
    {"label": "涤纶", "confidence": 0.08},
    {"label": "尼龙", "confidence": 0.04},
    {"label": "棉", "confidence": 0.02},
    {"label": "混纺", "confidence": 0.01}
  ],
  "visual_notes": "表面有细腻皮革纹理和自然光泽，质感柔软"
}
```

### Pass 2 输出

```json
{
  "labels": ["小羊皮", "PU皮革", "牛皮", "涤纶", "尼龙"],
  "confidences": [0.60, 0.18, 0.12, 0.07, 0.03],
  "reasoning": "基于视觉特征和联网证据，小羊皮的可能性最高，因为光泽度和纹理细腻度与典型小羊皮特征高度匹配。",
  "evidence": [
    {"label": "小羊皮", "urls": ["https://baike.baidu.com/item/小羊皮", "https://www.zhihu.com/question/..."]},
    {"label": "PU皮革", "urls": ["https://baike.baidu.com/item/PU"]}
  ]
}
```

---

## 实现位置

| 提示词 | 函数 | 文件 | 行号 |
|--------|------|------|------|
| Pass 1 (中文) | `_build_prompt_pass1(lang="zh")` | `src/fabric_api_infer.py` | 65-77 |
| Pass 1 (英文) | `_build_prompt_pass1(lang="en")` | `src/fabric_api_infer.py` | 79-90 |
| Pass 2 (中文) | `_build_prompt_pass2(..., lang="zh")` | `src/fabric_api_infer.py` | 111-133 |
| Pass 2 (英文) | `_build_prompt_pass2(..., lang="en")` | `src/fabric_api_infer.py` | 135-156 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2025-10-24 | 初始版本（开放集 + RAG） |
| 1.1 | 2025-10-24 | 简化提示词，使用 bullet points |

---

**文档状态**: ✅ 已完成  
**最后更新**: 2025-10-24

