# Web Cropper 组件设置指南

## 📦 前端依赖

### 核心库
- **React 18** - UI 框架
- **react-easy-crop** - 裁剪交互组件
- **streamlit-component-lib** - Streamlit 组件通信库
- **Vite 5** - 构建工具

### 开发工具
- **TypeScript** - 类型安全
- **@vitejs/plugin-react** - React 支持

---

## 🚀 快速开始

### 方式 1: 一键启动开发模式

```powershell
cd ui\web_cropper\frontend
.\setup_and_dev.ps1
```

然后在另一个终端：
```powershell
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

### 方式 2: 手动步骤

**Terminal 1 - 前端开发服务器：**
```powershell
cd ui\web_cropper\frontend
npm install
npm run dev
```

**Terminal 2 - Streamlit 应用：**
```powershell
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

---

## 🏗️ 构建生产版本

### 方式 1: 使用脚本
```powershell
cd ui\web_cropper\frontend
.\build.ps1
```

### 方式 2: 手动构建
```powershell
cd ui\web_cropper\frontend
npm install
npm run build
```

构建产物位于 `ui/web_cropper/frontend/dist/`

---

## 🔄 自动模式切换

后端 (`ui/web_cropper/__init__.py`) 会自动：

1. **优先使用开发服务器**
   - 检查环境变量 `WEB_CROPPER_DEV_URL`
   - 测试端口是否可达（300ms 超时）
   - 如果可达，使用开发服务器

2. **自动回退到构建产物**
   - 如果开发服务器不可用
   - 自动探测 `dist/` 或 `build/` 目录
   - 加载静态文件

3. **零配置生产部署**
   - 不设置 `WEB_CROPPER_DEV_URL`
   - 直接运行 `streamlit run app_new.py`
   - 自动使用构建产物

---

## 📁 目录结构

```
ui/web_cropper/
├── __init__.py              # Python 包装器（智能模式切换）
├── frontend/
│   ├── package.json         # 依赖配置
│   ├── vite.config.ts       # Vite 配置（端口 5173，输出 dist/）
│   ├── tsconfig.json        # TypeScript 配置
│   ├── index.html           # HTML 入口
│   ├── setup_and_dev.ps1    # 一键启动开发
│   ├── build.ps1            # 一键构建
│   ├── src/
│   │   ├── main.tsx         # React 入口（Streamlit 集成）
│   │   ├── App.tsx          # 主组件（裁剪逻辑）
│   │   └── style.css        # 样式
│   └── dist/                # 构建产物（自动生成）
└── SETUP.md                 # 本文档
```

---

## 🔧 配置说明

### vite.config.ts
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,      // 允许外部访问
    port: 5173,      // 开发服务器端口
  },
  build: {
    outDir: 'dist',  // 输出到 dist/（与后端一致）
    emptyOutDir: true,
  },
})
```

### package.json
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-easy-crop": "^5.0.6",
    "streamlit-component-lib": "^2.0.0"  // ← 关键依赖
  }
}
```

---

## 🐛 故障排除

### 问题：组件不显示
**检查：**
1. 开发服务器是否运行？`http://localhost:5173`
2. 环境变量是否设置？`$env:WEB_CROPPER_DEV_URL`
3. 构建产物是否存在？`ui/web_cropper/frontend/dist/index.html`

### 问题：图片不显示
**检查：**
1. 浏览器控制台（F12）是否有网络错误？
2. Streamlit 媒体文件管理器是否正常？
3. 图片 URL 是否为相对路径？（如 `/media/xxx.jpg`）

### 问题：裁剪框不响应
**检查：**
1. `react-easy-crop` 是否正确安装？
2. CSS 样式是否加载？
3. 浏览器控制台是否有 React 错误？

### 问题：npm install 失败
**解决：**
```powershell
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

---

## 📝 开发提示

### 热重载
- 修改 `src/App.tsx` 后自动刷新（< 100ms）
- 无需重启 Streamlit

### 调试
- 浏览器控制台（F12）查看 React 错误
- Streamlit 终端查看 Python 错误
- `console.log()` 在浏览器中可见

### TypeScript
- 类型错误会在编辑器中高亮
- 构建时会检查类型

---

## ✅ 验收标准

### 开发模式
- [ ] `npm run dev` 启动成功（端口 5173）
- [ ] Streamlit 显示组件
- [ ] 图片背景清晰可见
- [ ] 裁剪框可拖动和调整大小
- [ ] 右侧预览实时更新
- [ ] 修改代码后自动热重载

### 生产模式
- [ ] `npm run build` 构建成功
- [ ] `dist/index.html` 存在
- [ ] Streamlit 无需环境变量即可运行
- [ ] 功能与开发模式一致

---

## 🔗 相关链接

- [React Easy Crop](https://github.com/ValentinH/react-easy-crop)
- [Streamlit Component Library](https://github.com/streamlit/component-template)
- [Vite](https://vitejs.dev/)
- [TypeScript](https://www.typescriptlang.org/)


