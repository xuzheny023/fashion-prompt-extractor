# 📋 布局重构总结

## ⚠️ 状态：部分完成，需要手动应用

由于文件编辑过程中出现编码和缩进问题，已恢复到 git 干净版本。

以下是需要应用的完整更改清单。

---

## 🎯 目标

**重构 `app_new.py` 布局为清晰的左右分栏：**
- **左侧 (colL)**: 原图 + 交互裁剪组件（仅此一处渲染）
- **右侧 (colR)**: 裁剪预览 + 识别按钮 + 推荐结果

**删除所有重复渲染**，确保每个元素只显示一次。

---

## 📝 需要的更改

### 1. 添加辅助函数（在 `# ==================== 辅助函数 ====================` 部分）

#### 1.1 添加 `ensure_min_size` 函数
```python
def ensure_min_size(pil_img: Image.Image, tgt: int = 640) -> Image.Image:
    """保证传云端的图片最短边≥tgt，避免太小导致识别失败。"""
    w, h = pil_img.size
    if min(w, h) >= tgt:
        return pil_img
    scale = tgt / min(w, h)
    nw, nh = int(w * scale), int(h * scale)
    return pil_img.resize((nw, nh), Image.BICUBIC)
```

#### 1.2 简化 `crop_pil` 函数（替换现有的 `crop_by_rect`）
```python
def crop_pil(img: Image.Image, rect: dict) -> Optional[Image.Image]:
    """
    根据 web_cropper 返回的 rect 裁剪图片。
    
    Args:
        img: 原始 PIL 图片
        rect: {x, y, w, h} 字典（组件返回的像素坐标）
    
    Returns:
        裁剪后的图片，如果 rect 无效则返回 None
    """
    if not rect:
        return None
    
    try:
        x = int(rect.get("x", 0))
        y = int(rect.get("y", 0))
        w = int(rect.get("w", 0))
        h = int(rect.get("h", 0))
        
        # 验证坐标
        if w <= 0 or h <= 0:
            return None
        
        # 裁剪（PIL.crop 使用 (left, top, right, bottom)）
        x1 = min(x + w, img.width)
        y1 = min(y + h, img.height)
        
        if x1 <= x or y1 <= y:
            return None
        
        return img.crop((x, y, x1, y1))
    except Exception as e:
        log.error(f"裁剪失败: {e}")
        return None
```

---

### 2. 更新主界面布局（替换 `# ==================== 主界面 ====================` 之后的所有代码）

```python
# ==================== 主界面 ====================
st.title(f"{E('app')} AI 面料识别与分析")
st.caption("基于云端 API 的智能面料识别系统")

# ==================== 布局：左原图+裁剪 / 右预览+识别 ====================
colL, colR = st.columns([7, 5], gap="large")

with colL:
    st.subheader("📷 图片预览 / 交互裁剪")
    
    if uploaded_file:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            log.info(f"图片已加载: {uploaded_file.name}, 尺寸: {img.size}")
        except Exception as e:
            st.error(f"❌ 图片加载失败: {e}")
            img = None
            rect = None
        
        if img and web_cropper:
            try:
                b64 = pil_to_b64(img)
                st.caption("💡 拖动矩形移动位置 • 拖动右下角调整大小 • 点击 Confirm 确认")
                
                # 调用裁剪组件（传入 box_size 实现热调节）
                rect = web_cropper(
                    key="web_cropper_main",
                    image_b64=b64,
                    box_size=crop_size,
                    minSize=32
                )
            except Exception as e:
                log.error(f"裁剪组件错误: {e}")
                st.warning(f"⚠️ 裁剪组件出错：{e}")
                rect = None
        elif img:
            # 无裁剪组件，显示原图
            st.image(img, use_container_width=True, caption=f"原始图片 ({img.width} × {img.height})")
            rect = None
        else:
            rect = None
    else:
        img, rect = None, None
        st.info("👈 请在左侧上传面料图片")

with colR:
    st.subheader("🔍 推荐结果")
    
    # 裁剪 & 预览
    patch = None
    if img and rect and isinstance(rect, dict) and rect.get("rect"):
        # 提取实际的 rect 数据
        actual_rect = rect.get("rect")
        patch = crop_pil(img, actual_rect)
        
        if patch:
            st.success(f"✓ 已选择裁剪区域：{patch.width} × {patch.height} px")
            
            # 应用预览放大倍数
            prev_w = int(patch.width * zoom_ratio)
            prev_h = int(patch.height * zoom_ratio)
            preview_img = patch.resize((prev_w, prev_h), Image.LANCZOS)
            
            st.image(
                preview_img,
                caption=f"预览区域 ({patch.width} × {patch.height}) · 放大 {zoom_ratio:.2f}x",
                use_column_width=False
            )
        else:
            st.warning("⚠️ 裁剪失败，请重新调整选框")
    elif img and not rect:
        st.info("👆 调整裁剪框后点击 Confirm 按钮")
    
    # 识别按钮
    api_key = get_api_key()
    can_recognize = bool(patch and api_key)
    
    if st.button("🔎 识别该区域", use_container_width=True, disabled=not can_recognize):
        if not api_key:
            st.error("❌ 未配置 API Key")
        else:
            with st.spinner("☁️ 云端识别中..."):
                try:
                    # 导入云端推理函数
                    from src.fabric_api_infer import analyze_image
                    
                    # 确保图片尺寸足够
                    infer_img = ensure_min_size(patch, 640)
                    
                    # 调用云端识别
                    result = analyze_image(
                        image=infer_img,
                        api_key=api_key,
                        lang=lang
                    )
                    
                    # 存储结果
                    st.session_state['last_result'] = result.get('result', {})
                    st.session_state['last_meta'] = result.get('meta', {})
                    st.session_state['last_meta']['engine'] = 'cloud'
                    
                    # 显示结果
                    st.success("✅ 识别完成")
                    
                    # 调用推荐面板渲染结果
                    render_recommend_panel(
                        image=infer_img,
                        top_k=top_k,
                        lang=lang
                    )
                    
                    # 显示引擎信息
                    engine = st.session_state['last_meta'].get('engine', '未知')
                    st.caption(f"🔧 引擎: {engine}")
                    
                except Exception as e:
                    log.error(f"识别失败: {e}")
                    st.error(f"❌ 识别失败: {e}")
    
    # 如果已有识别结果，显示
    elif 'last_result' in st.session_state and st.session_state.last_result:
        st.info("💡 已有识别结果，点击按钮重新识别")
        
        # 显示上次结果
        render_recommend_panel(
            image=patch if patch else img,
            top_k=top_k,
            lang=lang
        )
        
        # 显示引擎信息
        if 'last_meta' in st.session_state:
            engine = st.session_state.last_meta.get('engine', '未知')
            st.caption(f"🔧 引擎: {engine}")

# ==================== 底部信息 ====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("✂️ 交互式裁剪：拖动移动 • 拖角调整大小")
with col2:
    st.caption("☁️ 云端识别：DashScope API")
with col3:
    cropper_status = "✅ 可用" if web_cropper else "⚠️ 不可用"
    st.caption(f"🔧 裁剪组件：{cropper_status}")

def main():
    pass

if __name__ == "__main__":
    main()
```

---

## ✅ 已完成的更改

1. ✅ 侧边栏添加 `crop_size` 和 `zoom_ratio` 滑块
2. ✅ 更新 `web_cropper` 调用，传入 `box_size=crop_size`
3. ✅ 创建文档 `CROPPER_CONTROLS_ADDED.md`

---

## ⏳ 待完成的更改

1. ⏳ 添加 `ensure_min_size` 函数
2. ⏳ 简化 `crop_pil` 函数（替换 `crop_by_rect`）
3. ⏳ 完全重构主界面布局为左右分栏
4. ⏳ 删除所有重复渲染的代码
5. ⏳ 测试新布局

---

## 🚀 手动应用步骤

由于自动编辑出现问题，请按以下步骤手动应用更改：

### 步骤 1: 备份当前文件
```bash
cp app_new.py app_new.py.backup
```

### 步骤 2: 在编辑器中打开 `app_new.py`
```bash
code app_new.py  # 或使用你喜欢的编辑器
```

### 步骤 3: 应用更改
1. 在 `# ==================== 辅助函数 ====================` 部分：
   - 在 `pil_to_b64` 函数后添加 `ensure_min_size` 函数
   - 将 `crop_by_rect` 函数替换为简化的 `crop_pil` 函数

2. 替换 `# ==================== 主界面 ====================` 之后的所有代码为上面提供的新布局代码

### 步骤 4: 验证语法
```bash
python -m py_compile app_new.py
```

### 步骤 5: 测试应用
```bash
streamlit run app_new.py
```

---

## 📊 预期效果

### 布局结构
```
┌─────────────────────────────────────────────────────────────┐
│  AI 面料识别与分析                                          │
├──────────────────────┬──────────────────────────────────────┤
│  📷 图片预览 / 交互裁剪 │  🔍 推荐结果                         │
│  ┌────────────────┐  │  ┌────────────────┐                  │
│  │                │  │  │  裁剪预览      │                  │
│  │   原图 + 裁剪框 │  │  │  (放大显示)    │                  │
│  │                │  │  └────────────────┘                  │
│  └────────────────┘  │  [ 🔎 识别该区域 ]                   │
│                      │  ┌────────────────┐                  │
│                      │  │  识别结果      │                  │
│                      │  │  推荐面板      │                  │
│                      │  └────────────────┘                  │
└──────────────────────┴──────────────────────────────────────┘
```

### 交互流程
1. 上传图片 → 左侧显示原图 + 裁剪框
2. 调整裁剪框 → 右侧实时显示预览（按 `zoom_ratio` 放大）
3. 点击 Confirm → 确认裁剪区域
4. 点击"识别该区域" → 调用云端 API
5. 显示识别结果 → 右侧推荐面板

---

## 🐛 已知问题

- 自动编辑工具在处理多行缩进时出现问题
- 需要手动应用更改以确保正确性

---

## 📚 相关文档

- `CROPPER_CONTROLS_ADDED.md` - 裁剪控制滑块文档
- `CLEANUP_VERIFICATION.md` - 云端纯净化验收清单
- `APP_CLEANUP_COMPLETE.md` - app_new.py 清理文档

---

**创建时间**: 2025-10-26  
**状态**: 待手动应用  
**优先级**: 高

