# 🧪 组件调试功能已添加

## 📋 添加内容

### 1. `ui/components/__init__.py`
添加了 `debug_components()` 函数：

```python
def debug_components():
    """
    Temporary debug function to verify component structure.
    TODO: Remove after components are stable.
    
    Returns:
        dict with keys: package_file, exports, tree, error (if any)
    """
```

**返回信息：**
- `package_file` - `ui/components/__init__.py` 的完整路径
- `exports` - 所有可用的导出（`render_*` 和 `save_to_history`）
- `tree` - `ui/components/` 目录下的所有 `.py` 文件
- `error` - 如果出错，包含错误信息（否则为 None）

---

### 2. `app_new.py`
在页面配置后添加了调试面板：

```python
# TODO: Temporary debug panel - remove after components are stable
try:
    from ui.components import debug_components
    _debug_info = debug_components()
    
    with st.expander("🧪 Components Debug", expanded=False):
        # 显示调试信息
        ...
except Exception as _e:
    # Silently fail if debug not available
    pass
```

---

## 🎯 功能说明

### 调试面板显示内容

1. **执行状态**
   - ✅ 成功：显示 "Debug function executed"
   - ❌ 失败：显示错误信息

2. **Package 位置**
   - 显示 `ui/components/__init__.py` 的绝对路径
   - 用于确认 Python 找到了正确的包

3. **可用导出**
   - 列出所有成功导入的 `render_*` 函数和 `save_to_history`
   - 如果为空，显示警告

4. **目录文件列表**
   - 列出 `ui/components/` 下的所有 `.py` 文件
   - 用于对比哪些文件存在但未成功导出

5. **缺失检查**
   - 检查预期的 6 个导出是否都存在
   - 如果有缺失，显示警告和提示

---

## 📊 使用示例

### 场景 1: 所有组件正常
```
🧪 Components Debug
  ✅ Debug function executed
  
  Package location:
  D:\fashion-prompt-extractor\ui\components\__init__.py
  
  Available exports:
  render_analysis_panel, render_actions_panel, render_confidence_panel,
  render_history_panel, render_recommend_panel, save_to_history
  
  Files in ui/components/:
  __init__.py, actions_panel.py, analysis_panel.py, confidence_panel.py,
  history_panel.py, recommend_panel.py
  
  ✅ All expected exports are available
```

---

### 场景 2: 部分组件缺失
```
🧪 Components Debug
  ✅ Debug function executed
  
  Package location:
  D:\fashion-prompt-extractor\ui\components\__init__.py
  
  Available exports:
  render_analysis_panel, render_recommend_panel, save_to_history
  
  Files in ui/components/:
  __init__.py, actions_panel.py, analysis_panel.py, confidence_panel.py,
  history_panel.py, recommend_panel.py
  
  ⚠️ Missing expected exports: render_actions_panel, render_confidence_panel,
     render_history_panel
  💡 Hint: Check if corresponding .py files exist and import successfully
```

**分析：**
- 文件存在但导出失败 → 可能是导入错误或语法错误
- 需要检查对应的 `.py` 文件

---

### 场景 3: 目录不存在
```
🧪 Components Debug
  ✅ Debug function executed
  
  Package location:
  D:\fashion-prompt-extractor\ui\components\__init__.py
  
  Available exports:
  (empty)
  
  Files in ui/components/:
  ⚠️ No Python files found
  
  ⚠️ Missing expected exports: render_analysis_panel, render_recommend_panel,
     render_confidence_panel, render_actions_panel, render_history_panel,
     save_to_history
  💡 Hint: Check if corresponding .py files exist and import successfully
```

**分析：**
- 包路径可能错误
- 或者目录结构有问题

---

## 🔍 故障排除

### 问题 1: 调试面板不显示
**原因：** `debug_components()` 导入失败

**检查：**
1. 确认 `ui/components/__init__.py` 存在
2. 确认文件语法正确
3. 查看 Streamlit 控制台是否有错误

---

### 问题 2: 显示 "No exports found"
**原因：** 所有组件导入都失败了

**检查：**
1. 查看 "Files in ui/components/" 列表
2. 如果文件存在，逐个检查文件语法
3. 尝试手动导入：
   ```python
   from ui.components.analysis_panel import render_analysis_panel
   ```

---

### 问题 3: 部分导出缺失
**原因：** 对应的组件文件有问题

**解决步骤：**
1. 找到缺失的导出（如 `render_analysis_panel`）
2. 检查对应文件（如 `analysis_panel.py`）是否存在
3. 手动导入测试：
   ```python
   python
   >>> from ui.components.analysis_panel import render_analysis_panel
   # 查看错误信息
   ```
4. 修复错误后重启 Streamlit

---

## 🗑️ 移除说明

### 何时移除
- ✅ 所有组件都正常工作
- ✅ 不再需要调试信息
- ✅ 准备生产部署

### 如何移除

#### 1. 从 `app_new.py` 移除调试面板
删除以下代码块：
```python
# TODO: Temporary debug panel - remove after components are stable
try:
    from ui.components import debug_components
    _debug_info = debug_components()
    
    with st.expander("🧪 Components Debug", expanded=False):
        # ... 整个调试面板代码 ...
        
except Exception as _e:
    pass
```

#### 2. 从 `ui/components/__init__.py` 移除函数（可选）
删除 `debug_components()` 函数定义（或保留，不影响性能）

---

## ✅ 验收

- ✅ 语法检查通过
- ✅ 调试面板在页面顶部显示（折叠状态）
- ✅ 展开后显示完整调试信息
- ✅ 不影响应用正常运行
- ✅ 如果调试功能不可用，应用仍可正常启动

---

## 📝 TODO 提醒

```
TODO: Remove debug panel after components are stable
Location: app_new.py (line ~17-61)
```

---

**状态：** ✅ 调试功能已添加

**位置：**
- `ui/components/__init__.py` - `debug_components()` 函数
- `app_new.py` - 调试面板（页面顶部，折叠状态）

**使用：** 运行 `streamlit run app_new.py`，展开 "🧪 Components Debug" 查看信息

