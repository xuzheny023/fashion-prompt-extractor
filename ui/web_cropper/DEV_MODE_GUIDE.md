# 🚀 Web Cropper - 开发模式指南

## ✅ 开发模式设置

### 步骤 1: 安装前端依赖

```powershell
cd ui\web_cropper\frontend
npm install
```

**预期输出**:
```
added XXX packages in Xs
```

---

### 步骤 2: 启动 Vite 开发服务器

在 **Terminal 1** 中运行:

```powershell
cd ui\web_cropper\frontend
npm run dev
```

**预期输出**:
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ **验收点**: 看到 "ready" 和端口 5173

---

### 步骤 3: 设置环境变量并启动 Streamlit

在 **Terminal 2** 中运行:

**PowerShell**:
```powershell
$env:WEB_CROPPER_DEV = "http://localhost:5173"
streamlit run app_new.py
```

**Bash/Linux**:
```bash
export WEB_CROPPER_DEV="http://localhost:5173"
streamlit run app_new.py
```

**预期输出**:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

✅ **验收点**: Streamlit 启动成功

---

## ✅ 验收标准

### 1. 前端开发服务器运行
- [ ] `npm run dev` 成功启动
- [ ] 显示 "Vite dev server running on port 5173"
- [ ] 无错误信息

### 2. Streamlit 加载组件
- [ ] 设置 `WEB_CROPPER_DEV` 环境变量
- [ ] Streamlit 启动成功
- [ ] 浏览器打开 `http://localhost:8501`

### 3. 组件功能正常
- [ ] 上传图片后，左侧显示裁剪器
- [ ] 可以看到图片背景
- [ ] 可以拖动裁剪框
- [ ] 可以调整裁剪框大小
- [ ] 右侧预览立即更新

### 4. 热重载工作
- [ ] 修改 `frontend/src/App.tsx`
- [ ] 保存后浏览器自动刷新
- [ ] 更改立即生效

---

## 🔍 故障排除

### 问题 1: `npm install` 失败

**症状**: 
```
npm ERR! network timeout
```

**解决方案**:
```powershell
# 使用国内镜像
npm config set registry https://registry.npmmirror.com
npm install
```

---

### 问题 2: 端口 5173 被占用

**症状**:
```
Port 5173 is in use, trying another one...
```

**解决方案**:
1. 找到占用端口的进程:
```powershell
netstat -ano | findstr :5173
```

2. 终止进程或使用其他端口:
```powershell
# 修改 vite.config.ts 中的端口
server: {
  port: 5174,  // 改为其他端口
}
```

3. 更新环境变量:
```powershell
$env:WEB_CROPPER_DEV = "http://localhost:5174"
```

---

### 问题 3: 组件不显示

**症状**: Streamlit 页面空白或显示错误

**检查清单**:

1. **确认环境变量已设置**:
```powershell
# PowerShell
echo $env:WEB_CROPPER_DEV
# 应该输出: http://localhost:5173
```

2. **确认 Vite 服务器正在运行**:
- 访问 `http://localhost:5173` 应该看到组件界面

3. **检查浏览器控制台**:
- 按 F12 打开开发者工具
- 查看 Console 标签是否有错误
- 查看 Network 标签是否有失败的请求

4. **检查 CORS**:
- Vite dev server 应该自动处理 CORS
- 如果有问题，在 `vite.config.ts` 中添加:
```typescript
server: {
  port: 5173,
  cors: true
}
```

---

### 问题 4: 图片不显示

**症状**: 裁剪器显示但没有图片背景

**检查**:

1. **检查图片 URL**:
```typescript
// 在 App.tsx 中添加调试
console.log("Image URL:", args.imageUrl);
```

2. **检查 Network 标签**:
- 图片请求应该是 `/media/xxx.jpg`
- 状态码应该是 200

3. **检查相对 URL**:
- 确认 `__init__.py` 中 `_pil_to_media_url` 返回相对 URL
- 格式应该是 `/media/xxx.jpg` 而不是完整 URL

---

### 问题 5: 坐标不正确

**症状**: 裁剪后的预览位置不对

**检查**:

1. **验证坐标转换**:
```typescript
// 在 App.tsx 的 onCropComplete 中添加
console.log("Display size:", dw, dh);
console.log("Natural size:", iw, ih);
console.log("Scale:", scaleX, scaleY);
console.log("Result:", { x, y, w, h });
```

2. **验证 Python 侧接收**:
```python
# 在 app_new.py 中添加
if rect:
    st.write(f"Received rect: {rect}")
```

---

## 🎯 开发工作流

### 典型开发流程

1. **启动开发环境**:
```powershell
# Terminal 1: 前端
cd ui\web_cropper\frontend
npm run dev

# Terminal 2: Streamlit
$env:WEB_CROPPER_DEV = "http://localhost:5173"
streamlit run app_new.py
```

2. **修改代码**:
- 编辑 `frontend/src/App.tsx`
- 保存文件
- 浏览器自动刷新

3. **测试**:
- 上传图片
- 测试裁剪功能
- 检查预览更新

4. **调试**:
- 使用浏览器开发者工具 (F12)
- 查看 Console 日志
- 检查 Network 请求

---

## 📝 开发提示

### 1. 快速重启

如果遇到问题，快速重启所有服务:

```powershell
# 停止所有服务 (Ctrl+C)

# 清理并重启
cd ui\web_cropper\frontend
rm -r node_modules
npm install
npm run dev

# 在另一个终端
$env:WEB_CROPPER_DEV = "http://localhost:5173"
streamlit run app_new.py
```

### 2. 查看实时日志

**前端日志**:
- Vite dev server 输出在 Terminal 1
- 浏览器 Console (F12)

**后端日志**:
- Streamlit 输出在 Terminal 2
- Python print 语句会显示在这里

### 3. 调试技巧

**添加调试输出**:
```typescript
// App.tsx
useEffect(() => {
  console.log("Args received:", args);
}, [args]);

const onCropComplete = async (_area: any, areaPixels: any) => {
  console.log("Crop complete:", areaPixels);
  // ... rest of code
};
```

**检查 Streamlit 通信**:
```typescript
// 检查 Streamlit 对象是否存在
console.log("Streamlit available:", !!window.Streamlit);
console.log("Streamlit methods:", Object.keys(window.Streamlit || {}));
```

---

## ✅ 成功标志

当一切正常工作时，你应该看到:

### Terminal 1 (Vite)
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Terminal 2 (Streamlit)
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 浏览器 (http://localhost:8501)
- ✅ 上传图片后显示裁剪器
- ✅ 图片背景清晰可见
- ✅ 裁剪框可以拖动
- ✅ 裁剪框可以调整大小
- ✅ 右侧预览立即更新
- ✅ 无控制台错误

---

## 🎉 下一步

开发模式验证成功后:

1. ✅ 确认所有功能正常
2. ✅ 测试不同大小的图片
3. ✅ 测试不同的裁剪位置
4. ✅ 验证坐标准确性

然后我们可以:
- 添加生产构建模式
- 优化性能
- 添加更多功能

---

**当前状态**: 🟢 开发模式就绪  
**下一步**: 测试和验证

