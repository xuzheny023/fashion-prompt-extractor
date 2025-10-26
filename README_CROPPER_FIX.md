# 🎨 Web Cropper 使用指南

## 📋 概述

本项目集成了自定义的交互式裁剪组件 `web_cropper`，支持两种运行模式：
- **生产模式（推荐）**：自动构建，开箱即用
- **开发模式（可选）**：热重载，实时预览前端修改

---

## 🚀 模式 1: 生产模式（推荐）

### 特点
- ✅ **零配置**：无需手动构建前端
- ✅ **自动构建**：首次运行自动检测并构建（仅一次）
- ✅ **快速启动**：后续运行直接使用缓存的构建产物
- ✅ **生产就绪**：使用优化后的静态文件

### 使用方法

#### 直接运行
```bash
streamlit run app_new.py
```

**首次运行时：**
- 自动检测 `ui/web_cropper/frontend/dist/` 不存在
- 自动运行 `npm install` 和 `npm run build`
- 构建完成后启动应用（约 60 秒）

**后续运行时：**
- 直接使用已构建的 `dist/` 产物
- 秒级启动，无需等待

### 工作原理

```
启动应用
    ↓
检查 dist/ 是否存在？
    ↓ 否
检查源码是否变化？
    ↓ 是
自动构建前端
    ↓
加载组件
    ↓
应用就绪
```

### 手动重新构建（可选）

如果修改了前端代码，需要手动重新构建：

**Windows (PowerShell):**
```powershell
cd ui\web_cropper\frontend
npm run build
cd ..\..\..
streamlit run app_new.py
```

**macOS / Linux:**
```bash
cd ui/web_cropper/frontend
npm run build
cd ../../..
streamlit run app_new.py
```

---

## 🔥 模式 2: 开发模式（可选）

### 特点
- ✅ **热重载**：修改前端代码立即生效
- ✅ **快速迭代**：无需每次手动构建
- ✅ **开发友好**：实时查看修改效果
- ⚠️ **需要两个终端**：一个运行 Vite，一个运行 Streamlit

### 使用方法

#### 步骤 1: 启动 Vite 开发服务器

**Windows (PowerShell):**
```powershell
cd ui\web_cropper\frontend
npm run dev
```

**macOS / Linux:**
```bash
cd ui/web_cropper/frontend
npm run dev
```

**预期输出：**
```
  VITE v5.4.21  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

#### 步骤 2: 设置环境变量并启动 Streamlit

**Windows (PowerShell) - 新终端：**
```powershell
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

**macOS / Linux - 新终端：**
```bash
export WEB_CROPPER_DEV_URL="http://localhost:5173"
streamlit run app_new.py
```

#### 步骤 3: 开发和测试

1. 修改前端代码（如 `ui/web_cropper/frontend/src/App.tsx`）
2. 保存文件
3. 浏览器自动刷新，立即看到效果
4. 无需重启 Streamlit

#### 步骤 4: 切换回生产模式

**Windows (PowerShell):**
```powershell
# 清除环境变量
Remove-Item Env:\WEB_CROPPER_DEV_URL

# 重启 Streamlit（Ctrl+C 后重新运行）
streamlit run app_new.py
```

**macOS / Linux:**
```bash
# 清除环境变量
unset WEB_CROPPER_DEV_URL

# 重启 Streamlit（Ctrl+C 后重新运行）
streamlit run app_new.py
```

---

## 🔍 模式对比

| 特性 | 生产模式 | 开发模式 |
|------|---------|---------|
| **启动命令** | `streamlit run app_new.py` | `npm run dev` + 设置环境变量 |
| **首次启动** | 自动构建（约 60s） | 需要手动启动 Vite |
| **后续启动** | 秒级启动 | 需要保持 Vite 运行 |
| **修改前端** | 需要手动重新构建 | 自动热重载 |
| **适用场景** | 日常使用、生产部署 | 前端开发、调试 |
| **终端数量** | 1 个 | 2 个 |
| **网络要求** | 无 | localhost:5173 可达 |

---

## 🛠️ 故障排除

### 问题 1: 首次运行提示 "Node.js not found"

**症状：**
```
❌ ERROR: Node.js not found!
   Please install Node.js from https://nodejs.org/
```

**解决：**
1. 安装 Node.js（推荐 LTS 版本）：https://nodejs.org/
2. 重启终端
3. 验证安装：`node --version`
4. 重新运行：`streamlit run app_new.py`

---

### 问题 2: 开发模式下组件不显示

**症状：**
```
⚠️ web_cropper: Dev server http://localhost:5173 not reachable, falling back to build
```

**原因：** Vite 开发服务器未启动或端口被占用

**解决：**
1. 检查 Vite 是否运行：
   ```bash
   cd ui/web_cropper/frontend
   npm run dev
   ```
2. 确认端口 5173 未被占用
3. 验证环境变量已设置：
   - Windows: `echo $env:WEB_CROPPER_DEV_URL`
   - macOS/Linux: `echo $WEB_CROPPER_DEV_URL`

---

### 问题 3: 修改前端代码后无效果

**在生产模式：**
- 需要手动重新构建：
  ```bash
  cd ui/web_cropper/frontend
  npm run build
  ```

**在开发模式：**
- 检查 Vite 是否报错
- 检查浏览器控制台（F12）
- 尝试硬刷新（Ctrl+Shift+R）

---

### 问题 4: 构建失败

**症状：**
```
❌ npm run build failed:
[error details]
```

**解决：**
1. 删除 `node_modules` 和 `package-lock.json`：
   ```bash
   cd ui/web_cropper/frontend
   rm -r node_modules package-lock.json
   ```
2. 重新安装依赖：
   ```bash
   npm install
   ```
3. 手动构建：
   ```bash
   npm run build
   ```

---

### 问题 5: 组件完全不可用

**症状：**
```
⚠️ 裁剪组件不可用，使用完整图片进行识别
```

**原因：** 组件导入失败或构建产物缺失

**解决：**
1. 检查 `ui/web_cropper/frontend/dist/index.html` 是否存在
2. 手动构建：
   ```bash
   cd ui/web_cropper/frontend
   npm install
   npm run build
   ```
3. 验证构建产物：
   ```bash
   ls dist/
   # 应该看到 index.html 和 assets/
   ```
4. 重启 Streamlit

**注意：** 即使组件不可用，应用仍可正常运行，只是使用完整图片进行识别。

---

## 📚 快速参考

### 常用命令

**生产模式：**
```bash
# 运行应用（推荐）
streamlit run app_new.py

# 手动重新构建前端
cd ui/web_cropper/frontend && npm run build && cd ../../..
```

**开发模式：**
```bash
# Terminal 1: 启动 Vite
cd ui/web_cropper/frontend && npm run dev

# Terminal 2: 启动 Streamlit（Windows）
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"; streamlit run app_new.py

# Terminal 2: 启动 Streamlit（macOS/Linux）
export WEB_CROPPER_DEV_URL="http://localhost:5173" && streamlit run app_new.py
```

### 环境变量

| 变量 | 作用 | 示例 |
|------|------|------|
| `WEB_CROPPER_DEV_URL` | 指定开发服务器地址 | `http://localhost:5173` |

**设置（Windows）：**
```powershell
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
```

**设置（macOS/Linux）：**
```bash
export WEB_CROPPER_DEV_URL="http://localhost:5173"
```

**清除（Windows）：**
```powershell
Remove-Item Env:\WEB_CROPPER_DEV_URL
```

**清除（macOS/Linux）：**
```bash
unset WEB_CROPPER_DEV_URL
```

---

## 🎯 最佳实践

### 日常使用
1. ✅ 使用生产模式：`streamlit run app_new.py`
2. ✅ 让自动构建处理前端
3. ✅ 无需关心前端细节

### 前端开发
1. ✅ 使用开发模式
2. ✅ 保持 Vite 运行
3. ✅ 实时查看修改效果
4. ✅ 完成后手动构建：`npm run build`
5. ✅ 清除环境变量切换回生产模式

### 生产部署
1. ✅ 提前构建前端：
   ```bash
   cd ui/web_cropper/frontend
   npm ci  # 使用 package-lock.json
   npm run build
   ```
2. ✅ 提交 `dist/` 到版本控制（可选）
3. ✅ 部署时直接运行：`streamlit run app_new.py`

---

## 📖 相关文档

- [WEB_CROPPER_INTEGRATION.md](./WEB_CROPPER_INTEGRATION.md) - 集成详解
- [ui/web_cropper/COMPONENT_READY.md](./ui/web_cropper/COMPONENT_READY.md) - 组件功能
- [ui/web_cropper/IMPLEMENTATION_COMPLETE.md](./ui/web_cropper/IMPLEMENTATION_COMPLETE.md) - 实现总结
- [test_web_cropper.py](./test_web_cropper.py) - 独立测试

---

## ✅ 总结

### 推荐工作流

**普通用户：**
```bash
streamlit run app_new.py
# 完成！自动处理一切
```

**前端开发者：**
```bash
# 开发时
cd ui/web_cropper/frontend && npm run dev
# 另一个终端
export WEB_CROPPER_DEV_URL="http://localhost:5173"
streamlit run app_new.py

# 完成后
npm run build
unset WEB_CROPPER_DEV_URL
```

---

**版本：** 2.1.0  
**更新日期：** 2025-10-26  
**状态：** ✅ 生产就绪

