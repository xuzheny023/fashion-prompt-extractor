# AI Fashion Fabric Analyst | AI 设计落地助手

<div align="center">

**Transform AI-generated fashion designs into production-ready specifications**

**将 AI 生成的设计图转化为可生产的技术规格**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](#english) | [中文](#chinese)

</div>

---

<a name="english"></a>
## 🌟 English Documentation

### Overview

**AI Fashion Fabric Analyst** is an intelligent design-to-production assistant powered by Alibaba Cloud's Qwen-VL-Max vision-language model. It helps fashion designers, pattern makers, and manufacturers analyze design images and receive detailed, production-oriented recommendations.

### ✨ Key Features

- **📐 Fabric Analysis**: Identify material composition, weave structure, weight (gsm), gloss level, stretch properties, handfeel, and finishing processes
- **🎨 Print & Graphic Analysis**: Determine print types, color count, resolution requirements, repeat sizes, suitable base fabrics, and complete workflow recommendations
- **🔧 Construction Analysis**: Get specifications for stitch types, needle/thread combinations, seam types, edge finishes, interlining requirements, and tolerance standards
- **💰 Multi-Budget Recommendations**: Receive low-cost, mid-range, and high-end options for each analysis
- **⚠️ DFM Risk Assessment**: Identify potential manufacturability issues (shrinkage, color fastness, pilling, etc.)
- **🎯 Context-Aware Analysis**: Results tailored to your budget level, use case, and specific constraints
- **🌐 Bilingual Support**: Full Chinese and English interface and results
- **✂️ Interactive Cropping**: Select specific regions of interest for targeted analysis

### 🚀 Quick Start

#### Prerequisites

- Python 3.8 or higher
- Alibaba Cloud DashScope API Key ([Get yours here](https://dashscope.aliyuncs.com/))
- Windows, macOS, or Linux

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fashion-prompt-extractor.git
cd fashion-prompt-extractor
```

2. **Set up virtual environment**
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**

Create `.streamlit/secrets.toml`:
```toml
DASHSCOPE_API_KEY = "your-api-key-here"
```

Or set as environment variable:
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-api-key-here"

# macOS/Linux
export DASHSCOPE_API_KEY="your-api-key-here"
```

#### Running the Application

**Windows:**
```powershell
.\run.ps1
```

**macOS/Linux:**
```bash
streamlit run app_new.py
```

The application will open at `http://localhost:8501` (or `http://localhost:9000` if using `run.ps1`).

### 📖 How to Use

1. **Select Language**: Choose your preferred language (中文/English) at the top of the sidebar
2. **Upload Image**: Upload a design image (AI-generated or photographed)
3. **Set Context Parameters**:
   - **ROI Type**: Auto-detect, Fabric, Print, or Construction
   - **Budget Level**: Low cost, Mid-range, or High-end
   - **Use Case**: Casual, Evening, Activewear, Office, Home, Wedding, or Stage
   - **Constraints**: Select multiple requirements (eco-friendly, washable, durable, etc.)
4. **Select Region**: 
   - Drag the orange crop box to select the area you want to analyze
   - Or use the full image for comprehensive analysis
5. **Analyze**: Click "Analyze Selected Region" to get AI-powered recommendations
6. **Review Results**: 
   - **Summary**: One-sentence conclusion
   - **Detailed Analysis**: Comprehensive technical specifications
   - **Recommendations**: Budget-specific material/process options
   - **DFM Risks**: Potential production issues
   - **Next Actions**: Recommended next steps

### 🏗️ Architecture

```
fashion-prompt-extractor/
├── app_new.py                 # Main Streamlit application
├── src/
│   ├── fabric_api_infer.py   # AI inference engine (DashScope API)
│   ├── aug/
│   │   └── web_search.py     # Web search augmentation (optional)
│   └── utils/
│       └── logger.py          # Logging utilities
├── scripts/
│   └── ensure_venv.ps1       # Virtual environment setup
├── run.ps1                    # Windows launcher script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .streamlit/
    └── secrets.toml          # API key configuration (create this)
```

### 🔧 Configuration

#### Model Selection

The application uses `qwen-vl-max` by default. You can select different models in the sidebar:
- `qwen-vl`: Standard model
- `qwen-vl-plus`: Enhanced model (automatically uses qwen-vl-max)

#### Language Settings

- **UI Language**: Toggle between Chinese and English in the sidebar
- **Output Language**: AI results will match your selected language

#### Advanced Options

- **Enable Web Search**: Augment AI analysis with web-sourced information
- **Search Results**: Configure the number of web results to retrieve (1-10)

### 🎯 Use Cases

- **Fashion Designers**: Validate design feasibility and get production specifications
- **Pattern Makers**: Receive technical details for pattern construction
- **Manufacturers**: Assess production requirements and potential risks
- **Sourcing Teams**: Get material recommendations across different budget levels
- **Quality Control**: Identify potential DFM issues early in the design phase

### 🛠️ Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **AI Model**: Qwen-VL-Max (Alibaba Cloud DashScope)
- **Image Processing**: PIL/Pillow
- **Cropping Tool**: streamlit-cropper
- **Web Search**: DuckDuckGo (optional augmentation)

### 📝 API Reference

#### Main Inference Function

```python
from src.fabric_api_infer import cloud_infer

result = cloud_infer(
    pil_image=image,           # PIL Image object
    engine="qwen-vl",          # Model engine
    lang="en",                 # Language: "zh" or "en"
    enable_web=False,          # Enable web search
    k_per_query=4,             # Web search result count
    task_type="fabric",        # "fabric", "print", "construction", or "auto"
    budget="mid",              # "low", "mid", or "high"
    scene="casual",            # Target use case
    constraints="eco,wash"     # Comma-separated constraints
)
```

#### Response Schema

```json
{
  "task": "fabric|print|construction",
  "summary": "One-sentence conclusion",
  "details": {
    "fabric": { /* fabric-specific fields */ },
    "print": { /* print-specific fields */ },
    "construction": { /* construction-specific fields */ }
  },
  "recommendations": {
    "budget_low": "Low-cost option",
    "budget_mid": "Mid-range option",
    "budget_high": "High-end option",
    "suppliers_or_process": ["Recommendation 1", "Recommendation 2"]
  },
  "dfm_risks": ["Risk 1", "Risk 2"],
  "next_actions": ["Action 1", "Action 2"]
}
```

### 🐛 Troubleshooting

**Port Already in Use**
```powershell
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
```

**API Key Error**
- Verify your `DASHSCOPE_API_KEY` is correctly set
- Check `.streamlit/secrets.toml` or environment variables
- Ensure your API key is active and has sufficient quota

**Cropping Tool Issues**
- If the interactive cropper doesn't load, the app will fall back to numerical input mode
- You can manually enter coordinates (x1, y1, x2, y2) for region selection

**Chinese Characters in English Mode**
- Restart the application after changing language settings
- Clear Streamlit cache: Menu → Settings → Clear cache

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- Alibaba Cloud for the Qwen-VL-Max model
- Streamlit for the excellent web framework
- The open-source community for various supporting libraries

---

<a name="chinese"></a>
## 🌟 中文文档

### 概述

**AI 设计落地助手** 是一款基于阿里云通义千问视觉大模型（Qwen-VL-Max）的智能设计生产助手。帮助服装设计师、制版师和生产厂商分析设计图，获得详细的生产导向建议。

### ✨ 核心功能

- **📐 面料分析**：识别材质成分、组织结构、克重（gsm）、光泽度、弹性、手感和后整理工艺
- **🎨 印花图案分析**：判断印花类型、套色数、分辨率要求、重复尺寸、合适底布和完整工艺流程推荐
- **🔧 结构工艺分析**：提供针型、针线规格、缝型、边缝处理、衬料要求和公差标准等规格
- **💰 多价位方案**：针对每次分析提供低成本、中等价位和高端三种选择
- **⚠️ DFM 风险评估**：识别潜在的可制造性问题（缩水、色牢度、起球等）
- **🎯 场景化分析**：根据预算档位、使用场景和特殊约束定制化结果
- **🌐 双语支持**：完整的中英文界面和结果输出
- **✂️ 交互式裁剪**：选择特定感兴趣区域进行针对性分析

### 🚀 快速开始

#### 前置要求

- Python 3.8 或更高版本
- 阿里云灵积 API 密钥（[点此获取](https://dashscope.aliyuncs.com/)）
- Windows、macOS 或 Linux 系统

#### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/fashion-prompt-extractor.git
cd fashion-prompt-extractor
```

2. **创建虚拟环境**
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置 API 密钥**

创建 `.streamlit/secrets.toml` 文件：
```toml
DASHSCOPE_API_KEY = "你的API密钥"
```

或设置为环境变量：
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="你的API密钥"

# macOS/Linux
export DASHSCOPE_API_KEY="你的API密钥"
```

#### 运行应用

**Windows:**
```powershell
.\run.ps1
```

**macOS/Linux:**
```bash
streamlit run app_new.py
```

应用将在 `http://localhost:8501`（或使用 `run.ps1` 时为 `http://localhost:9000`）打开。

### 📖 使用指南

1. **选择语言**：在侧边栏顶部选择首选语言（中文/English）
2. **上传图片**：上传设计图片（AI 生成或实物拍摄）
3. **设置上下文参数**：
   - **ROI 区域类型**：自动识别、面料分析、印花工艺或结构做法
   - **预算档位**：低成本、中等或高端
   - **使用场景**：日常休闲、晚礼服、运动装、商务正装、家居服、婚礼服装或舞台表演
   - **约束条件**：多选要求（环保、可水洗、耐磨等）
4. **选择区域**：
   - 拖动橙色裁剪框选择要分析的区域
   - 或使用整张图片进行综合分析
5. **AI 分析**：点击"AI 分析选中区域"获取 AI 推荐
6. **查看结果**：
   - **总结**：一句话核心结论
   - **详细分析**：全面的技术规格
   - **推荐方案**：不同预算的材料/工艺选择
   - **DFM 风险**：潜在生产问题
   - **下一步行动**：建议的后续步骤

### 🏗️ 项目结构

```
fashion-prompt-extractor/
├── app_new.py                 # Streamlit 主应用
├── src/
│   ├── fabric_api_infer.py   # AI 推理引擎（灵积 API）
│   ├── aug/
│   │   └── web_search.py     # 网络检索增强（可选）
│   └── utils/
│       └── logger.py          # 日志工具
├── scripts/
│   └── ensure_venv.ps1       # 虚拟环境设置
├── run.ps1                    # Windows 启动脚本
├── requirements.txt           # Python 依赖
├── README.md                  # 本文件
└── .streamlit/
    └── secrets.toml          # API 密钥配置（需创建）
```

### 🔧 配置说明

#### 模型选择

应用默认使用 `qwen-vl-max`。可在侧边栏选择不同模型：
- `qwen-vl`：标准模型
- `qwen-vl-plus`：增强模型（自动使用 qwen-vl-max）

#### 语言设置

- **界面语言**：在侧边栏切换中文和英文
- **输出语言**：AI 结果将匹配所选语言

#### 高级选项

- **启用联网增强**：使用网络信息增强 AI 分析
- **检索条数**：配置网络结果数量（1-10 条）

### 🎯 应用场景

- **服装设计师**：验证设计可行性，获取生产规格
- **制版师**：获得版型制作的技术细节
- **生产厂商**：评估生产要求和潜在风险
- **采购团队**：获得不同预算档位的材料推荐
- **质量控制**：在设计阶段早期识别 DFM 问题

### 🛠️ 技术栈

- **前端框架**：Streamlit（Python Web 框架）
- **AI 模型**：Qwen-VL-Max（阿里云灵积平台）
- **图像处理**：PIL/Pillow
- **裁剪工具**：streamlit-cropper
- **网络检索**：DuckDuckGo（可选增强）

### 📝 API 参考

#### 主推理函数

```python
from src.fabric_api_infer import cloud_infer

result = cloud_infer(
    pil_image=image,           # PIL Image 对象
    engine="qwen-vl",          # 模型引擎
    lang="zh",                 # 语言："zh" 或 "en"
    enable_web=False,          # 启用网络检索
    k_per_query=4,             # 网络检索结果数
    task_type="fabric",        # "fabric"、"print"、"construction" 或 "auto"
    budget="mid",              # "low"、"mid" 或 "high"
    scene="casual",            # 目标使用场景
    constraints="环保,可水洗"   # 逗号分隔的约束条件
)
```

#### 响应格式

```json
{
  "task": "fabric|print|construction",
  "summary": "一句话结论",
  "details": {
    "fabric": { /* 面料相关字段 */ },
    "print": { /* 印花相关字段 */ },
    "construction": { /* 工艺相关字段 */ }
  },
  "recommendations": {
    "budget_low": "低成本方案",
    "budget_mid": "中等价位方案",
    "budget_high": "高端方案",
    "suppliers_or_process": ["建议1", "建议2"]
  },
  "dfm_risks": ["风险1", "风险2"],
  "next_actions": ["行动1", "行动2"]
}
```

### 🐛 故障排除

**端口已被占用**
```powershell
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
```

**API 密钥错误**
- 验证 `DASHSCOPE_API_KEY` 是否正确设置
- 检查 `.streamlit/secrets.toml` 或环境变量
- 确保 API 密钥有效且有足够配额

**裁剪工具问题**
- 如果交互式裁剪器无法加载，应用会自动切换到数值输入模式
- 可以手动输入坐标（x1, y1, x2, y2）来选择区域

**英文模式下出现中文字符**
- 更改语言设置后重启应用
- 清除 Streamlit 缓存：菜单 → 设置 → 清除缓存

### 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- 阿里云提供的 Qwen-VL-Max 模型
- Streamlit 优秀的 Web 框架
- 开源社区提供的各种支持库

---

<div align="center">

**Made with ❤️ for Fashion Tech**

**为时尚科技而生 ❤️**

</div>
