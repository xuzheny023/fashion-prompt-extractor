# UI 组件化指南

## 📦 概述

将 Streamlit UI 拆分为可复用的组件模块，实现：
- 🎯 **关注点分离** - 每个面板专注单一功能
- 🔄 **可复用性** - 组件可在不同页面复用
- 🧪 **易测试性** - 独立测试每个组件
- 📝 **易维护性** - 清晰的代码结构

---

## 🗂️ 组件结构

```
ui/components/
├── __init__.py              # 组件导出
├── analysis_panel.py        # 分析面板
├── recommend_panel.py       # 推荐面板 ⭐
├── confidence_panel.py      # 置信度面板
├── actions_panel.py         # 操作面板
└── history_panel.py         # 历史记录面板
```

---

## 🎯 核心组件

### 1. recommend_panel.py ⭐

**职责：** 调用 `core.recommender.recommend` 进行面料推荐

**特性：**
- ✅ 4 阶段进度条
- ✅ 展示 `ScoreItem` 列表
- ✅ 显示 `ai_reason`
- ✅ 自动保存到 `session_state`

**进度条阶段：**
1. **加载数据 (5%)** - 初始化
2. **编码查询 (25%)** - CLIP 编码
3. **粗排 (40%)** - 类中心相似度
4. **精排 (85%)** - 类内完整样本
5. **完成 (100%)** - 显示耗时

**使用示例：**
```python
from ui.components import render_recommend_panel

render_recommend_panel(
    image=pil_image,
    top_k=5,
    lang="zh"
)
```

**输出：**
- 进度条动画
- 性能指标（耗时、粗排分、速度）
- 推荐结果列表（带置信度条）
- AI 推理说明（如果有）
- 高置信度过滤
- 低置信度警告

---

### 2. analysis_panel.py

**职责：** 显示图片分析信息

**包含：**
- 📏 图片尺寸
- 📍 点击坐标
- ⏱️ 处理时间
- 🔍 元数据

**使用示例：**
```python
from ui.components import render_analysis_panel

render_analysis_panel(
    image_info={
        "width": 800,
        "height": 600,
        "format": "JPEG",
        "size_kb": 245.6
    },
    click_coords=(320, 240),
    processing_time=0.185
)
```

---

### 3. confidence_panel.py

**职责：** 置信度分析和质量评估

**包含：**
- 📊 置信度分布
- 📈 统计信息
- 🎯 质量评估
- 💡 改进建议
- 📉 分数差距分析

**使用示例：**
```python
from ui.components import render_confidence_panel

render_confidence_panel(result=ranked_result)
```

**输出：**
- 最高分/平均分/最低分
- 分级统计（高/中/低/极低）
- 质量评估（优秀/良好/一般/较差）
- 改进建议
- 前两名差距分析

---

### 4. actions_panel.py

**职责：** 提供各种操作功能

**包含：**
- 📥 导出 JSON
- 📊 导出 CSV
- 📋 复制结果
- 💾 保存图片
- 🔄 重新分析
- 📦 批量处理

**使用示例：**
```python
from ui.components import render_actions_panel

render_actions_panel(
    result=ranked_result,
    meta=query_meta,
    image=pil_image
)
```

---

### 5. history_panel.py

**职责：** 历史记录管理

**包含：**
- 📜 历史列表
- 📊 统计信息
- 🔍 历史对比
- 📥 导出历史
- 🗑️ 清除历史

**使用示例：**
```python
from ui.components import render_history_panel

render_history_panel(max_items=10)
```

**自动保存：**
```python
from ui.components.history_panel import save_to_history

save_to_history(result, meta, "image.jpg")
```

---

## 🎨 app_new.py 示例

### 完整布局

```python
import streamlit as st
from ui.components import (
    render_analysis_panel,
    render_recommend_panel,
    render_confidence_panel,
    render_actions_panel,
    render_history_panel
)

# 页面配置
st.set_page_config(layout="wide")

# 侧边栏
with st.sidebar:
    uploaded_file = st.file_uploader("上传图片")
    top_k = st.slider("返回结果数", 3, 10, 5)

# 主界面
if uploaded_file:
    image = Image.open(uploaded_file)
    
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.image(image)
    
    with right_col:
        # 使用 tabs 组织面板
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 推荐", "📊 分析", "📈 置信度", "⚡ 操作", "📜 历史"
        ])
        
        with tab1:
            render_recommend_panel(image, top_k=top_k)
        
        with tab2:
            render_analysis_panel(image_info=...)
        
        with tab3:
            if 'last_result' in st.session_state:
                render_confidence_panel(st.session_state.last_result)
        
        with tab4:
            if 'last_result' in st.session_state:
                render_actions_panel(
                    result=st.session_state.last_result,
                    meta=st.session_state.last_meta,
                    image=image
                )
        
        with tab5:
            render_history_panel()
```

---

## 🔄 数据流

```
用户上传图片
    ↓
render_recommend_panel()
    ↓
调用 recommend(image)
    ↓
显示进度条 (4 阶段)
    ↓
保存到 session_state
    ↓
其他面板读取 session_state
    ↓
render_confidence_panel()
render_actions_panel()
```

---

## 📊 进度条详解

### 实现方式

```python
# 创建进度条
progress_bar = st.progress(0.05, text="🔄 加载数据...")

# 阶段1: 加载数据 (5%)
progress_bar.progress(0.05, text="🔄 加载数据...")

# 阶段2: 编码查询 (25%)
progress_bar.progress(0.25, text="🧠 CLIP 编码中...")

# 阶段3: 粗排 (40%)
progress_bar.progress(0.40, text="🔍 类中心粗排...")

# 阶段4: 精排 (85%)
progress_bar.progress(0.85, text="✨ 类内精排...")

# 完成 (100%)
progress_bar.progress(1.0, text=f"✅ 完成 ({meta.ms}ms)")
```

### 进度映射

| 阶段 | 进度 | 说明 | 预计耗时 |
|------|------|------|----------|
| 加载数据 | 5% | 初始化 | < 10ms |
| CLIP 编码 | 25% | 双通道编码 | 50-100ms |
| 类中心粗排 | 40% | 64 个类中心 | 5-10ms |
| 类内精排 | 85% | 12×10 样本 | 20-50ms |
| 完成 | 100% | 显示结果 | - |

---

## 🎯 使用场景

### 场景1: 简单推荐

```python
# 只需一行
render_recommend_panel(image)
```

### 场景2: 自定义参数

```python
render_recommend_panel(
    image=image,
    top_k=10,
    lang="en"
)
```

### 场景3: 完整分析流程

```python
# 1. 推荐
render_recommend_panel(image)

# 2. 分析（读取 session_state）
if 'last_result' in st.session_state:
    result = st.session_state.last_result
    meta = st.session_state.last_meta
    
    # 3. 置信度
    render_confidence_panel(result)
    
    # 4. 操作
    render_actions_panel(result, meta, image)
    
    # 5. 保存历史
    save_to_history(result, meta, "image.jpg")
```

### 场景4: 批量处理

```python
from ui.components.actions_panel import render_batch_actions

render_batch_actions()
```

---

## 🧪 测试

### 运行测试

```bash
python tools/test_ui_components.py
```

### 测试内容

- ✅ 组件导入
- ✅ 函数签名
- ✅ 类型兼容
- ✅ 数据创建
- ✅ 历史记录
- ✅ 文件结构

### 测试输出

```
============================================================
UI 组件测试
============================================================

[1/6] 测试组件导入...
  ✓ 所有组件导入成功

[2/6] 验证函数签名...
  ✓ render_analysis_panel 签名正确
  ✓ render_recommend_panel 签名正确
  ✓ render_confidence_panel 签名正确
  ✓ render_actions_panel 签名正确
  ✓ render_history_panel 签名正确

...

✅ 所有测试通过！
```

---

## 🚀 启动新版 UI

```bash
streamlit run app_new.py
```

**访问：** http://localhost:8501

---

## 📝 最佳实践

### ✅ DO

1. **使用组件化设计**
   ```python
   # ✅ 好
   render_recommend_panel(image)
   
   # ❌ 差
   # 在 app.py 中写 200 行推荐逻辑
   ```

2. **利用 session_state 共享数据**
   ```python
   # 推荐面板自动保存
   st.session_state.last_result = result
   
   # 其他面板读取
   if 'last_result' in st.session_state:
       render_confidence_panel(st.session_state.last_result)
   ```

3. **使用 tabs 组织面板**
   ```python
   tab1, tab2, tab3 = st.tabs(["推荐", "分析", "操作"])
   with tab1:
       render_recommend_panel(image)
   ```

4. **提供清晰的用户反馈**
   ```python
   # 进度条
   st.progress(0.5, text="处理中...")
   
   # 状态消息
   st.success("✓ 完成")
   st.warning("⚠️ 注意")
   st.error("❌ 错误")
   ```

### ❌ DON'T

1. **不要在组件内硬编码配置**
   ```python
   # ❌ 差
   def render_panel():
       top_k = 5  # 硬编码
   
   # ✅ 好
   def render_panel(top_k: int = 5):
       pass
   ```

2. **不要在组件间直接传递大对象**
   ```python
   # ❌ 差
   render_panel_a(huge_data)
   render_panel_b(huge_data)
   
   # ✅ 好
   st.session_state.data = huge_data
   render_panel_a()  # 内部读取 session_state
   render_panel_b()
   ```

3. **不要忽略异常处理**
   ```python
   # ❌ 差
   result = recommend(image)  # 可能抛出异常
   
   # ✅ 好
   try:
       result = recommend(image)
   except FileNotFoundError:
       st.error("向量库未找到")
   ```

---

## 🔧 扩展组件

### 创建新组件

```python
# ui/components/my_panel.py

import streamlit as st

def render_my_panel(data):
    """
    我的自定义面板
    
    Args:
        data: 输入数据
    """
    st.subheader("我的面板")
    
    # 实现逻辑
    st.write(data)
```

### 注册组件

```python
# ui/components/__init__.py

from .my_panel import render_my_panel

__all__ = [
    # ... 其他组件
    'render_my_panel',
]
```

### 使用新组件

```python
# app.py

from ui.components import render_my_panel

render_my_panel(data)
```

---

## 📚 相关文档

- [推荐引擎](./RECOMMENDER_GUIDE.md) - `src/core/recommender.py`
- [数据类型](./TYPES_GUIDE.md) - `ScoreItem`, `RankedResult`, `QueryMeta`
- [配置管理](./CONFIG_GUIDE.md) - `src/config.py`
- [架构总览](./ARCHITECTURE_SUMMARY.md)

---

## 💡 后续改进

1. **组件样式** - 自定义 CSS 主题
2. **国际化** - 多语言支持
3. **响应式** - 移动端适配
4. **动画效果** - 更流畅的过渡
5. **缓存优化** - 减少重复渲染

---

✅ **UI 组件化完成！** 现在可以在 `app.py` 中使用这些组件构建清晰、可维护的界面。 🎉

