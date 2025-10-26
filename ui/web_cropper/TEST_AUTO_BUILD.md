# Web Cropper Auto-Build 测试指南

## 🎯 测试目标

验证 `ui/web_cropper/__init__.py` 的自动构建策略是否正常工作。

---

## ✅ 测试场景

### 场景 1: 首次运行（无构建产物）

**前置条件：**
```powershell
# 删除构建产物
rm -r ui/web_cropper/frontend/dist -ErrorAction SilentlyContinue
rm -r ui/web_cropper/frontend/build -ErrorAction SilentlyContinue
rm ui/web_cropper/frontend/.build.stamp -ErrorAction SilentlyContinue
```

**执行：**
```powershell
streamlit run app_new.py
```

**预期结果：**
- ✅ 自动检测到无构建产物
- ✅ 自动运行 `npm install` (或 `npm ci`)
- ✅ 自动运行 `npm run build`
- ✅ 创建 `.build.stamp` 文件
- ✅ 组件正常加载
- ✅ 控制台输出类似：
  ```
  ================================================================================
  🔨 web_cropper: Build needed (sources changed or no build output)
  ================================================================================
  
  📦 Running: npm ci (using package-lock.json)
  ✅ Dependencies installed
  🏗️  Running: npm run build
  ✅ Build completed successfully
  ================================================================================
  
  ✅ web_cropper: Using build from frontend/dist
  ```

---

### 场景 2: 后续运行（构建产物已存在，源码未变）

**前置条件：**
- 场景 1 已完成
- `dist/` 目录存在
- `.build.stamp` 文件存在

**执行：**
```powershell
streamlit run app_new.py
```

**预期结果：**
- ✅ 跳过构建（源码哈希未变）
- ✅ 直接使用现有构建产物
- ✅ 启动速度快
- ✅ 控制台输出类似：
  ```
  ✅ web_cropper: Using build from frontend/dist
  ```

---

### 场景 3: 源码修改后运行

**前置条件：**
- 场景 2 已完成
- 修改任意源文件（如 `src/App.tsx`）

**执行：**
```powershell
# 修改源码
echo "// test change" >> ui/web_cropper/frontend/src/App.tsx

# 运行
streamlit run app_new.py
```

**预期结果：**
- ✅ 检测到源码变化（哈希不匹配）
- ✅ 自动重新构建
- ✅ 更新 `.build.stamp`
- ✅ 组件加载新版本
- ✅ 控制台输出类似：
  ```
  ⚠️  web_cropper: Sources changed, rebuilding...
  
  ================================================================================
  🔨 web_cropper: Build needed (sources changed or no build output)
  ================================================================================
  
  📦 Running: npm ci (using package-lock.json)
  ✅ Dependencies installed
  🏗️  Running: npm run build
  ✅ Build completed successfully
  ================================================================================
  
  ✅ web_cropper: Using build from frontend/dist
  ```

---

### 场景 4: 开发模式（Dev Server 优先）

**前置条件：**
- 启动 Vite 开发服务器

**执行：**
```powershell
# Terminal 1: 启动开发服务器
cd ui/web_cropper/frontend
npm run dev

# Terminal 2: 设置环境变量并运行 Streamlit
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

**预期结果：**
- ✅ 检测到开发服务器可达
- ✅ 使用 `url=` 模式（不使用构建产物）
- ✅ 支持热重载
- ✅ 控制台输出类似：
  ```
  🚀 web_cropper: Using dev server at http://localhost:5173
  ```

---

### 场景 5: 开发模式回退（Dev Server 不可达）

**前置条件：**
- 开发服务器未启动
- 设置了 `WEB_CROPPER_DEV_URL` 环境变量

**执行：**
```powershell
$env:WEB_CROPPER_DEV_URL = "http://localhost:5173"
streamlit run app_new.py
```

**预期结果：**
- ✅ 尝试连接开发服务器失败
- ✅ 自动回退到构建产物
- ✅ 控制台输出类似：
  ```
  ⚠️  web_cropper: Dev server http://localhost:5173 not reachable, falling back to build
  ✅ web_cropper: Using build from frontend/dist
  ```

---

### 场景 6: Node.js 未安装

**前置条件：**
- 删除构建产物
- Node.js 不在 PATH 中（或重命名 node.exe）

**执行：**
```powershell
streamlit run app_new.py
```

**预期结果：**
- ✅ 检测到 Node.js 不可用
- ✅ 显示清晰的错误提示
- ✅ 不崩溃，继续声明组件
- ✅ 控制台输出类似：
  ```
  ❌ ERROR: Node.js not found!
     Please install Node.js from https://nodejs.org/
     Or manually build the frontend:
       cd ui\web_cropper\frontend
       npm install && npm run build
  
  ❌ web_cropper: No valid build output found!
     Component may not work correctly.
     Please manually build:
       cd ui\web_cropper\frontend
       npm install && npm run build
  ```

---

## 🔍 验证点

### 1. 构建幂等性
```powershell
# 连续运行两次
streamlit run app_new.py
# Ctrl+C 停止
streamlit run app_new.py
```
- ✅ 第二次运行应跳过构建

### 2. 哈希追踪文件
检查 `.build.stamp` 内容：
```powershell
cat ui/web_cropper/frontend/.build.stamp
```
- ✅ 应该是一个 32 字符的 MD5 哈希

### 3. 构建产物
检查构建输出：
```powershell
ls ui/web_cropper/frontend/dist/
```
- ✅ 应包含 `index.html`
- ✅ 应包含 `assets/` 目录

### 4. 组件功能
在 Streamlit 应用中：
- ✅ 组件正常渲染
- ✅ 图片显示正常
- ✅ 裁剪框可交互
- ✅ Confirm 按钮回传数据

---

## 🐛 故障排除

### 问题：构建一直触发
**原因：** `.build.stamp` 未正确保存或源码哈希计算不稳定

**解决：**
```powershell
# 手动创建 stamp
cd ui/web_cropper/frontend
python -c "import hashlib; print(hashlib.md5(b'manual').hexdigest())" > .build.stamp
```

### 问题：npm install 超时
**原因：** 网络慢或依赖包过大

**解决：**
```powershell
# 手动安装
cd ui/web_cropper/frontend
npm install --registry=https://registry.npmmirror.com
npm run build
```

### 问题：组件不显示
**原因：** 构建失败或路径错误

**解决：**
1. 检查 `dist/index.html` 是否存在
2. 查看 Streamlit 控制台错误
3. 打开浏览器 F12 查看网络请求

---

## 📊 性能基准

| 场景 | 首次启动时间 | 后续启动时间 |
|------|-------------|-------------|
| 无构建产物 | ~60s (含构建) | ~2s |
| 有构建产物 | ~2s | ~2s |
| 源码变更 | ~45s (重新构建) | ~2s |
| 开发模式 | ~2s | ~2s |

---

## ✅ 验收标准

- [ ] 场景 1-6 全部通过
- [ ] 构建幂等性验证通过
- [ ] 组件功能正常
- [ ] 错误提示清晰
- [ ] 无崩溃或异常退出
- [ ] `.build.stamp` 正确更新
- [ ] 开发模式和生产模式切换正常

---

## 🔗 相关文件

- `ui/web_cropper/__init__.py` - 组件加载器（本次重写）
- `ui/web_cropper/frontend/vite.config.ts` - Vite 配置
- `ui/web_cropper/frontend/package.json` - 依赖配置
- `app_new.py` - Streamlit 应用入口


