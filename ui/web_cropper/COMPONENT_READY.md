# ✅ Web Cropper Component Ready

## 📋 实现摘要

已完成轻量级交互式裁剪组件，包含完整的 Streamlit 集成。

---

## 🎯 核心功能

### 1. **Streamlit API 集成**
- ✅ `Streamlit.setComponentReady()` - 在 main.tsx 中调用
- ✅ `Streamlit.setFrameHeight()` - 自动调整高度
- ✅ `Streamlit.setComponentValue()` - 返回裁剪矩形

### 2. **交互式裁剪**
- ✅ **拖动移动** - 点击矩形区域拖动
- ✅ **调整大小** - 拖动右下角圆点调整
- ✅ **实时反馈** - 显示当前尺寸（宽 × 高）
- ✅ **边界限制** - 自动限制在图片范围内
- ✅ **最小尺寸** - 防止矩形过小（默认 32px）

### 3. **用户界面**
- ✅ 半透明遮罩突出裁剪区域
- ✅ 虚线边框（青色 #00d4ff）
- ✅ 可视化调整手柄
- ✅ 尺寸标签实时显示
- ✅ Confirm 和 Reset 按钮
- ✅ 操作提示文本

---

## 📡 数据契约

### 输入（props.args）
```typescript
{
  image_b64: string,      // base64 编码的图片（无 data: 前缀）
  box?: {                 // 可选的初始矩形
    x: number,
    y: number,
    w: number,
    h: number
  },
  minSize?: number        // 最小尺寸（默认 32）
}
```

### 输出（Streamlit.setComponentValue）
```typescript
{
  rect: {
    x: number,    // 左上角 X 坐标（CSS 像素）
    y: number,    // 左上角 Y 坐标（CSS 像素）
    w: number,    // 宽度（CSS 像素）
    h: number     // 高度（CSS 像素）
  }
}
```

---

## 🎨 视觉设计

### 裁剪矩形
- **边框：** 2px 虚线，青色 (#00d4ff)
- **遮罩：** 外部区域 40% 黑色半透明
- **光标：** 移动时显示 grab/grabbing

### 调整手柄
- **位置：** 右下角
- **样式：** 12px 圆形，青色背景，白色边框
- **光标：** nwse-resize（对角线调整）

### 尺寸标签
- **位置：** 矩形上方
- **内容：** 宽 × 高（四舍五入）
- **样式：** 青色背景，白色文字

### 按钮
- **Confirm：** 青色背景 (#00d4ff)，白色文字，带 ✓ 图标
- **Reset：** 灰色背景 (#666)，白色文字，带 ↻ 图标

---

## 🔧 技术实现

### main.tsx
```typescript
import { withStreamlitConnection, Streamlit } from 'streamlit-component-lib'
import App from './App'

const Wrapped = withStreamlitConnection(App)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Wrapped />
  </React.StrictMode>
)

// ✅ 关键调用
Streamlit.setComponentReady()
Streamlit.setFrameHeight()
```

### App.tsx 核心逻辑
```typescript
// 1. 状态管理
const [rect, setRect] = useState<Rect>(box || { x: 50, y: 50, w: 200, h: 200 })
const [isDragging, setIsDragging] = useState(false)
const [isResizing, setIsResizing] = useState(false)

// 2. 自动调整高度
useEffect(() => {
  Streamlit.setFrameHeight()
}, [rect, image_b64])

// 3. 拖动逻辑
const handleMouseMove = (e: React.MouseEvent) => {
  if (isDragging) {
    const newX = Math.max(0, Math.min(imgSize.width - rect.w, rect.x + dx))
    const newY = Math.max(0, Math.min(imgSize.height - rect.h, rect.y + dy))
    setRect({ ...rect, x: newX, y: newY })
  }
}

// 4. 确认回传
const onConfirm = () => {
  Streamlit.setComponentValue({ rect })
}
```

---

## ✅ 验收测试

### 测试 1: 基本渲染
```python
from ui.web_cropper import web_cropper
import base64
from PIL import Image
import io

# 创建测试图片
img = Image.new('RGB', (800, 600), color='red')
buf = io.BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()

# 调用组件
result = web_cropper(
    key="test",
    image_b64=b64,
    box=None,
    minSize=32
)
```

**预期：**
- ✅ 显示红色图片
- ✅ 显示居中的裁剪矩形
- ✅ 可以拖动和调整大小

### 测试 2: 初始矩形
```python
result = web_cropper(
    key="test2",
    image_b64=b64,
    box={"x": 100, "y": 100, "w": 300, "h": 200},
    minSize=50
)
```

**预期：**
- ✅ 矩形位置为 (100, 100)
- ✅ 矩形尺寸为 300 × 200
- ✅ 最小尺寸限制为 50px

### 测试 3: 确认回传
**操作：**
1. 拖动矩形到新位置
2. 调整矩形大小
3. 点击 Confirm 按钮

**预期：**
- ✅ `result` 包含 `{ "rect": { "x": ..., "y": ..., "w": ..., "h": ... } }`
- ✅ 坐标值为 CSS 像素单位

### 测试 4: Reset 功能
**操作：**
1. 移动/调整矩形
2. 点击 Reset 按钮

**预期：**
- ✅ 矩形恢复到居中位置
- ✅ 尺寸恢复到默认（图片的 50% 或 200px）

---

## 📦 构建产物

```
ui/web_cropper/frontend/dist/
├── index.html                   (0.40 kB)
└── assets/
    ├── index-DuSYu4Ny.css      (0.24 kB)
    └── index-DlqC1P08.js       (145.70 kB)
```

**构建时间：** 485ms

---

## 🚀 使用示例

### Python 端（app_new.py）
```python
import streamlit as st
from ui.web_cropper import web_cropper
import base64
from PIL import Image
import io

# 加载图片
uploaded_file = st.file_uploader("Upload Image")
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    
    # 转换为 base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    
    # 调用组件
    result = web_cropper(
        key="cropper",
        image_b64=b64,
        box=None,
        minSize=32
    )
    
    # 处理结果
    if result and 'rect' in result:
        rect = result['rect']
        st.write(f"Crop area: {rect['x']}, {rect['y']}, {rect['w']}, {rect['h']}")
        
        # 裁剪图片
        cropped = img.crop((
            rect['x'], rect['y'],
            rect['x'] + rect['w'],
            rect['y'] + rect['h']
        ))
        st.image(cropped, caption="Cropped")
```

---

## 🎯 关键特性

### ✅ 无需重型库
- 纯 React + TypeScript
- 无 react-easy-crop 或其他裁剪库
- 总大小 < 150 kB（gzip 后 < 50 kB）

### ✅ 流畅交互
- 实时拖动和调整
- 无延迟反馈
- 边界自动限制

### ✅ Streamlit 集成
- 自动高度调整
- 状态持久化
- 组件就绪通知

### ✅ 开发友好
- TypeScript 类型安全
- 清晰的数据契约
- 易于扩展

---

## 🔄 后续增强（可选）

如需更强大的功能，可考虑：

1. **比例锁定** - 保持固定宽高比
2. **多个裁剪框** - 同时裁剪多个区域
3. **旋转支持** - 旋转裁剪框
4. **缩放控制** - 放大/缩小图片
5. **触摸支持** - 移动设备手势
6. **键盘快捷键** - 方向键微调位置

当前实现已满足基本需求，保持轻量级。

---

## 📚 相关文件

- `ui/web_cropper/frontend/src/main.tsx` - **已更新** - Streamlit 集成
- `ui/web_cropper/frontend/src/App.tsx` - **已重写** - 交互式裁剪组件
- `ui/web_cropper/frontend/vite.config.ts` - **已标准化** - 构建配置
- `ui/web_cropper/frontend/dist/` - **已构建** - 生产产物

---

## ✅ 验收标准

- ✅ `Streamlit.setComponentReady()` 在 main.tsx 中调用
- ✅ `Streamlit.setFrameHeight()` 自动调用
- ✅ `Streamlit.setComponentValue()` 返回 `{ rect }`
- ✅ 图片正确显示（base64 无 data: 前缀）
- ✅ 矩形可拖动移动
- ✅ 矩形可调整大小
- ✅ Confirm 按钮回传数据
- ✅ Reset 按钮恢复默认
- ✅ 无需开发服务器（从 dist/ 加载）
- ✅ 轻量级实现（无重型库）

---

**状态：** ✅ 组件就绪，可投入使用

**版本：** 1.0.0

**构建时间：** 2025-10-26

