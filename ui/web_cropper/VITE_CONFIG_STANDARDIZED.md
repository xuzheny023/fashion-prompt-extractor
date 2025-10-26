# ✅ Vite 配置标准化完成

## 📋 配置标准

### `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,        // ✅ 允许外部访问
    port: 5173,        // ✅ 标准端口
  },
  build: {
    outDir: 'dist',    // ✅ 标准输出目录
    emptyOutDir: true, // ✅ 构建前清空
    rollupOptions: {
      external: ['streamlit-component-lib'], // ✅ 外部化 Streamlit 库
    },
  },
})
```

---

## ✅ 验收测试

### 1. 构建输出
```powershell
cd ui/web_cropper/frontend
npm run build
```

**结果：**
```
✓ 31 modules transformed.
dist/index.html                   0.40 kB │ gzip:  0.26 kB
dist/assets/index-DuSYu4Ny.css    0.24 kB │ gzip:  0.17 kB
dist/assets/index-DsEp5cmH.js   143.88 kB │ gzip: 46.42 kB
✓ built in 485ms
```

**验证：**
- ✅ `dist/index.html` 存在
- ✅ `dist/assets/` 目录包含 CSS 和 JS
- ✅ 构建成功无错误

### 2. 开发服务器
```powershell
npm run dev
```

**预期：**
- ✅ 监听端口 5173
- ✅ 允许外部访问（`host: true`）
- ✅ 热重载可用

---

## 📁 文件结构

```
ui/web_cropper/frontend/
├── dist/                    ✅ 构建输出（新）
│   ├── index.html
│   └── assets/
│       ├── index-*.css
│       └── index-*.js
├── build/                   ⚠️  旧构建（可删除）
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   └── style.css
├── vite.config.ts           ✅ 已标准化
├── package.json
└── tsconfig.json
```

---

## 🔄 与后端集成

### Python 组件加载器
`ui/web_cropper/__init__.py` 应检测以下目录（按优先级）：

1. **开发模式：** `http://localhost:5173` (如果 `WEB_CROPPER_DEV_URL` 设置且可达)
2. **生产模式：** `frontend/dist/` (优先)
3. **回退：** `frontend/build/` (兼容旧版)

---

## 🚀 使用方式

### 开发模式
```powershell
# Terminal 1: 启动开发服务器
cd ui/web_cropper/frontend
npm run dev

# Terminal 2: 运行 Streamlit
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

### 生产模式
```powershell
# 一次性构建
cd ui/web_cropper/frontend
npm run build

# 运行 Streamlit（自动使用 dist/）
cd ../../..
streamlit run app_new.py
```

---

## 📊 配置对比

| 配置项 | 旧值 | 新值 | 说明 |
|--------|------|------|------|
| `build.outDir` | `"build"` | `"dist"` | ✅ 标准化 |
| `build.emptyOutDir` | - | `true` | ✅ 避免旧文件 |
| `build.rollupOptions.external` | - | `["streamlit-component-lib"]` | ✅ 外部化 |
| `server.host` | - | `true` | ✅ 允许外部访问 |
| `server.port` | `5173` | `5173` | ✅ 保持不变 |

---

## ✅ 验收标准

- ✅ `npm run build` 成功
- ✅ 输出到 `dist/index.html`
- ✅ `dist/assets/` 包含 CSS 和 JS
- ✅ 开发服务器监听 5173
- ✅ `streamlit-component-lib` 外部化
- ✅ 无构建错误或警告

---

## 🔗 相关文件

- `ui/web_cropper/frontend/vite.config.ts` - **已更新**
- `ui/web_cropper/frontend/package.json` - 依赖配置
- `ui/web_cropper/__init__.py` - Python 加载器（待更新以优先使用 dist/）

---

**状态：** ✅ 配置标准化完成

**构建产物：** `ui/web_cropper/frontend/dist/`

**下一步：** 更新 Python 加载器以优先检测 `dist/` 目录

