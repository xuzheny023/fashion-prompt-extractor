# 🚀 Web Cropper 快速开始

## 一分钟上手

### 生产模式（推荐）

```bash
# 就这一条命令！
streamlit run app_new.py
```

**首次运行：** 自动构建前端（约 60 秒）  
**后续运行：** 秒级启动

---

## 开发模式（可选）

### Windows (PowerShell)

```powershell
# Terminal 1: 启动 Vite
cd ui\web_cropper\frontend
npm run dev

# Terminal 2: 启动 Streamlit
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

### macOS / Linux

```bash
# Terminal 1: 启动 Vite
cd ui/web_cropper/frontend
npm run dev

# Terminal 2: 启动 Streamlit
export WEB_CROPPER_DEV_URL="http://localhost:5173"
streamlit run app_new.py
```

---

## 切换回生产模式

### Windows (PowerShell)

```powershell
Remove-Item Env:\WEB_CROPPER_DEV_URL
streamlit run app_new.py
```

### macOS / Linux

```bash
unset WEB_CROPPER_DEV_URL
streamlit run app_new.py
```

---

## 常见问题

### Node.js 未安装？
下载安装：https://nodejs.org/

### 组件不显示？
```bash
cd ui/web_cropper/frontend
npm install
npm run build
```

### 修改前端后无效？
- **生产模式：** 运行 `npm run build`
- **开发模式：** 自动热重载

---

**详细文档：** [README_CROPPER_FIX.md](./README_CROPPER_FIX.md)

