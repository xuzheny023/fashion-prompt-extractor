# 🚀 快速开始

## ✅ 环境配置

### Python 依赖（7 个最小依赖）
- ✅ streamlit>=1.32.0
- ✅ pillow
- ✅ numpy
- ✅ dashscope
- ✅ duckduckgo-search (网络搜索)
- ✅ readability-lxml (内容提取)
- ✅ requests (HTTP 客户端)

### 前端组件（首次运行需构建）
- ✅ web_cropper - React 裁剪组件（react-easy-crop + 放大镜）

## 🔨 首次设置

### 1. 安装 Python 依赖
```powershell
# 使用 VSCode 任务（推荐）
# Ctrl+Shift+P → Tasks: Run Task → 01: Ensure venv & deps

# 或手动运行
.\scripts\ensure_venv.ps1
```

### 2. 构建前端组件（一次性）
```powershell
# 使用构建脚本（推荐）
.\scripts\build_frontend.ps1

# 或手动构建
cd ui\web_cropper
.\build.ps1
cd ..\..
```

**注意**：需要 Node.js 18+ 才能构建前端。如未安装，请访问：https://nodejs.org/

## 🎯 启动应用

### 方法一：使用启动脚本（推荐）
```powershell
.\run.ps1
```

### 方法二：手动启动
```powershell
.\.venv\Scripts\streamlit.exe run app_new.py
```

### 方法三：使用 VSCode 任务
1. 按 `Ctrl+Shift+P`
2. 输入 `Tasks: Run Task`
3. 选择 `02: Run Streamlit (dev)`

## 🔑 API Key 配置

应用需要阿里云 DashScope API Key 才能使用云端识别功能。

### 查看/编辑 API Key
编辑文件：`.streamlit\secrets.toml`

```toml
DASHSCOPE_API_KEY = "sk-your-key-here"
```

### 获取 API Key
访问：https://dashscope.console.aliyun.com/apiKey

## 📖 使用流程

1. **上传图片**：点击上传按钮，选择一张面料图片
2. **调整裁剪框**：在左侧画布上拖动/调整蓝色方框
3. **预览区域**：右侧会实时显示裁剪区域的预览
4. **识别面料**：点击"识别该区域"按钮
5. **查看结果**：查看 Top-5 面料识别结果、置信度、推理过程和网络证据

## ⚙️ 功能说明

### 侧边栏控制
- **模型选择**：当前仅支持 Qwen-VL
- **选框大小**：调整裁剪框尺寸 (80-320px)
- **预览放大倍数**：调整右侧预览的缩放比例
- **语言切换**：中文/英文
- **联网验证**：启用后会通过网络搜索验证识别结果

### 网络搜索 (RAG)
启用后，系统会：
1. 使用 Qwen-VL 进行初步视觉识别
2. 通过 DuckDuckGo/Wikipedia/百度百科搜索候选面料信息
3. 结合网络证据重新排序，给出最终的 Top-5 结果
4. 提供可点击的证据链接

## 🛠️ 故障排查

### 依赖问题（最常见）

#### 快速诊断
```powershell
# 运行完整诊断（推荐）
.\.venv\Scripts\python.exe dev\diagnose.py

# 或快速检查依赖
.\.venv\Scripts\python.exe dev\preflight.py
```

#### 一键修复
```powershell
# 自动安装缺失依赖
.\.venv\Scripts\python.exe dev\preflight.py --install

# 或完整重装
.\scripts\ensure_venv.ps1
```

#### 应用内修复
如果应用显示"依赖缺失"，直接点击 **"🚀 自动安装依赖"** 按钮

### API Key 错误
检查 `.streamlit\secrets.toml` 中的 Key 是否正确

### VSCode 解释器问题
1. 按 `Ctrl+Shift+P`
2. 输入 "Python: Select Interpreter"
3. 选择 `.venv\Scripts\python.exe`
4. 重启终端

## 📂 项目结构

```
fashion-prompt-extractor/
├── app_new.py                 # 主应用入口（含自动修复UI）
├── src/
│   ├── fabric_api_infer.py   # 云端推理引擎 (Open-Set + RAG)
│   └── aug/
│       └── web_search.py     # 网络搜索模块 (多引擎回退)
├── dev/                       # 🆕 开发工具
│   ├── preflight.py          # 依赖检查与自动安装
│   └── diagnose.py           # 完整环境诊断
├── .vscode/
│   ├── settings.json         # 🆕 强制使用 .venv 解释器
│   └── tasks.json            # VSCode 一键任务
├── .streamlit/
│   ├── config.toml           # Streamlit 配置
│   └── secrets.toml          # API Key (已忽略提交)
├── scripts/
│   └── ensure_venv.ps1       # 环境配置脚本
├── run.ps1                   # 一键启动脚本（含依赖预检）
└── requirements.txt          # 依赖清单（8个最小依赖）
```

## 🎉 现在就开始吧！

运行：
```powershell
.\run.ps1
```

然后在浏览器中打开：http://localhost:8501

祝您使用愉快！ 🚀

