# Project Structure | 项目结构

## English

### Directory Tree

```
fashion-prompt-extractor/
│
├── 📄 app_new.py                    # Main Streamlit application entry point
│                                    # 主 Streamlit 应用入口
│
├── 📁 src/                          # Source code directory | 源代码目录
│   ├── 📄 fabric_api_infer.py      # Core AI inference engine
│   │                                # 核心 AI 推理引擎
│   ├── 📁 aug/                      # Augmentation modules | 增强模块
│   │   └── 📄 web_search.py        # Web search functionality (optional)
│   │                                # 网络检索功能（可选）
│   └── 📁 utils/                    # Utility functions | 工具函数
│       └── 📄 logger.py             # Logging utilities
│                                    # 日志工具
│
├── 📁 scripts/                      # Setup and utility scripts | 设置和工具脚本
│   └── 📄 ensure_venv.ps1          # Virtual environment setup (PowerShell)
│                                    # 虚拟环境设置（PowerShell）
│
├── 📁 .streamlit/                   # Streamlit configuration | Streamlit 配置
│   └── 📄 secrets.toml             # API keys and secrets (create this)
│                                    # API 密钥和敏感信息（需创建）
│
├── 📄 run.ps1                       # Windows launcher script | Windows 启动脚本
├── 📄 requirements.txt              # Python dependencies | Python 依赖
│
├── 📄 README.md                     # Main project documentation | 主项目文档
├── 📄 USER_GUIDE.md                 # Detailed usage guide | 详细使用指南
├── 📄 CHANGELOG.md                  # Version history | 版本历史
├── 📄 LICENSE                       # MIT License | MIT 许可证
└── 📄 PROJECT_STRUCTURE.md          # This file | 本文件
```

### File Descriptions | 文件说明

#### Core Application Files | 核心应用文件

**`app_new.py`**
- **Purpose**: Main Streamlit web application
- **Key Functions**:
  - UI layout and component rendering
  - Image upload and cropping interface
  - Result display and formatting
  - Internationalization (I18n) support
- **Dependencies**: `streamlit`, `PIL`, `streamlit-cropper`

**用途**：主 Streamlit Web 应用
**主要功能**：
- UI 布局和组件渲染
- 图片上传和裁剪界面
- 结果显示和格式化
- 国际化（I18n）支持
**依赖**：`streamlit`、`PIL`、`streamlit-cropper`

---

**`src/fabric_api_infer.py`**
- **Purpose**: AI inference engine
- **Key Functions**:
  - DashScope API integration
  - Prompt engineering (bilingual templates)
  - JSON schema definition and parsing
  - Image encoding and preprocessing
- **Dependencies**: `dashscope`, `PIL`, `json`, `base64`

**用途**：AI 推理引擎
**主要功能**：
- 灵积 API 集成
- 提示词工程（双语模板）
- JSON 模式定义和解析
- 图像编码和预处理
**依赖**：`dashscope`、`PIL`、`json`、`base64`

---

#### Supporting Modules | 支持模块

**`src/aug/web_search.py`**
- **Purpose**: Optional web search augmentation
- **Key Functions**:
  - DuckDuckGo search integration
  - Result extraction and parsing
  - Content summarization
- **Status**: Optional feature, can be disabled

**用途**：可选的网络检索增强
**主要功能**：
- DuckDuckGo 搜索集成
- 结果提取和解析
- 内容摘要
**状态**：可选功能，可禁用

---

**`src/utils/logger.py`**
- **Purpose**: Centralized logging
- **Key Functions**:
  - Structured log formatting
  - Multi-level logging (DEBUG, INFO, WARNING, ERROR)
  - File and console output

**用途**：集中式日志
**主要功能**：
- 结构化日志格式
- 多级日志（DEBUG、INFO、WARNING、ERROR）
- 文件和控制台输出

---

#### Configuration Files | 配置文件

**`requirements.txt`**
```
streamlit>=1.32.0         # Web framework | Web 框架
streamlit-cropper         # Interactive cropping | 交互式裁剪
pillow                    # Image processing | 图像处理
numpy                     # Numerical operations | 数值运算
dashscope                 # Alibaba Cloud API | 阿里云 API
duckduckgo-search         # Web search (optional) | 网络检索（可选）
readability-lxml          # Web content extraction | 网页内容提取
requests                  # HTTP library | HTTP 库
```

**`.streamlit/secrets.toml`** (Create this file | 创建此文件)
```toml
DASHSCOPE_API_KEY = "your-api-key-here"
```

---

#### Scripts | 脚本

**`run.ps1`** (Windows)
- Automated application launcher
- Virtual environment activation
- Port conflict resolution
- Process management

**自动化应用启动器**
- 虚拟环境激活
- 端口冲突解决
- 进程管理

**`scripts/ensure_venv.ps1`**
- Virtual environment creation
- Dependency installation
- Pre-flight checks

**虚拟环境创建**
- 依赖安装
- 启动前检查

---

#### Documentation | 文档

**`README.md`**
- Project overview
- Quick start guide
- Feature list
- Installation instructions
- Bilingual (English/Chinese)

**项目概述**
- 快速开始指南
- 功能列表
- 安装说明
- 双语（英文/中文）

**`USER_GUIDE.md`**
- Detailed usage instructions
- Step-by-step workflows
- Troubleshooting tips
- Best practices
- Bilingual

**详细使用说明**
- 分步工作流程
- 故障排除提示
- 最佳实践
- 双语

**`CHANGELOG.md`**
- Version history
- Feature additions
- Bug fixes
- Breaking changes

**版本历史**
- 功能增加
- Bug 修复
- 破坏性更改

---

### Data Flow | 数据流

```
User Upload Image
用户上传图片
    ↓
Interactive Cropping (streamlit-cropper)
交互式裁剪（streamlit-cropper）
    ↓
Image Encoding (Base64)
图像编码（Base64）
    ↓
Prompt Generation (make_prompt)
提示词生成（make_prompt）
    ↓
DashScope API Call (cloud_infer)
灵积 API 调用（cloud_infer）
    ↓
JSON Response Parsing (try_parse_json)
JSON 响应解析（try_parse_json）
    ↓
Result Rendering (render_result_block)
结果渲染（render_result_block）
    ↓
Display to User
显示给用户
```

---

### Key Design Patterns | 关键设计模式

#### 1. Modular Architecture | 模块化架构
- **Separation of Concerns**: UI (app_new.py) separate from logic (src/)
- **关注点分离**：UI（app_new.py）与逻辑（src/）分离

#### 2. Template Method Pattern | 模板方法模式
- **Prompt Engineering**: Language-specific prompt templates
- **提示词工程**：语言特定的提示词模板

#### 3. Strategy Pattern | 策略模式
- **Multi-task Analysis**: Different strategies for fabric/print/construction
- **多任务分析**：面料/印花/工艺的不同策略

#### 4. Fallback Pattern | 回退模式
- **Error Handling**: Multiple fallback strategies for JSON parsing
- **错误处理**：JSON 解析的多种回退策略

---

### Environment Variables | 环境变量

```bash
# Required | 必需
DASHSCOPE_API_KEY        # Alibaba Cloud API key | 阿里云 API 密钥

# Optional | 可选
STREAMLIT_SERVER_PORT    # Custom port (default: 8501) | 自定义端口（默认：8501）
STREAMLIT_SERVER_HEADLESS # Headless mode (true/false) | 无头模式（true/false）
```

---

### Development Workflow | 开发工作流

```bash
# 1. Clone repository | 克隆仓库
git clone <repository-url>
cd fashion-prompt-extractor

# 2. Create virtual environment | 创建虚拟环境
python -m venv .venv

# 3. Activate environment | 激活环境
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies | 安装依赖
pip install -r requirements.txt

# 5. Configure API key | 配置 API 密钥
# Create .streamlit/secrets.toml with your API key
# 创建 .streamlit/secrets.toml 并添加 API 密钥

# 6. Run application | 运行应用
streamlit run app_new.py
# or | 或
.\run.ps1  # (Windows only)
```

---

### Testing | 测试

Currently manual testing is performed. Automated testing framework planned for v2.1.

目前执行手动测试。自动化测试框架计划在 v2.1 版本中实现。

**Test Cases Include | 测试用例包括：**
- Image upload functionality
- Cropping tool interaction
- API integration
- JSON parsing edge cases
- Language switching
- Error handling

**图片上传功能**
- 裁剪工具交互
- API 集成
- JSON 解析边缘情况
- 语言切换
- 错误处理

---

### Contributing | 贡献

When adding new features:
1. Follow existing code structure
2. Add bilingual comments for key functions
3. Update documentation
4. Test in both Chinese and English modes
5. Update CHANGELOG.md

添加新功能时：
1. 遵循现有代码结构
2. 为关键函数添加双语注释
3. 更新文档
4. 在中文和英文模式下测试
5. 更新 CHANGELOG.md

---

<div align="center">

**For questions, please refer to README.md or USER_GUIDE.md**

**如有疑问，请参考 README.md 或 USER_GUIDE.md**

</div>

