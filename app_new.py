# -*- coding: utf-8 -*-
"""
AI Fashion Fabric Analyst | AI 设计落地助手
==============================================

English:
---------
A Streamlit-based AI application that analyzes fashion design images and provides
production-oriented recommendations for fabrics, prints, and construction details.

Features:
- Interactive region-of-interest (ROI) cropping
- Multi-language support (Chinese/English)
- Context-aware analysis (budget, use case, constraints)
- Detailed production specifications
- DFM (Design for Manufacturability) risk assessment

Powered by: Alibaba Cloud DashScope (Qwen-VL-Max)

中文：
------
基于 Streamlit 的 AI 应用，分析时尚设计图并提供面料、印花和工艺细节的
生产导向建议。

功能特点：
- 交互式感兴趣区域（ROI）裁剪
- 多语言支持（中文/英文）
- 场景化分析（预算、使用场景、约束条件）
- 详细生产规格
- DFM（可制造性设计）风险评估

技术支持：阿里云灵积平台（Qwen-VL-Max）

Author: AI Fashion Tech Team
License: MIT
Version: 2.0
"""
import streamlit as st
from PIL import Image
import io
import base64
import os
from typing import Optional, Tuple

# 导入云端推理模块
try:
    from src.fabric_api_infer import cloud_infer
except ImportError:
    cloud_infer = None

st.set_page_config(
    page_title="AI Fashion Fabric Analyst",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== API Key 管理 ====================
def get_api_key(engine: str = "qwen-vl") -> Optional[str]:
    """
    统一获取 API Key | Unified API Key retrieval
    
    Args:
        engine: 模型引擎名称 | Model engine name
            - "qwen-vl": Alibaba DashScope
            - "openai-gpt4v": OpenAI GPT-4 Vision
            - "google-gemini": Google Gemini Vision
    
    优先级 | Priority:
    1. 用户在侧边栏输入的密钥 | User input from sidebar
    2. .streamlit/secrets.toml 配置 | secrets.toml configuration
    3. 环境变量 | Environment variable
    
    Returns:
        str | None: API密钥或None
    """
    # 根据引擎确定环境变量名
    env_var_map = {
        "qwen-vl": "DASHSCOPE_API_KEY",
        "openai-gpt4v": "OPENAI_API_KEY",
        "google-gemini": "GOOGLE_API_KEY"
    }
    env_var = env_var_map.get(engine, "DASHSCOPE_API_KEY")
    
    # 优先使用用户输入的密钥（针对当前引擎）
    session_key = f"user_api_key_{engine}"
    if session_key in st.session_state and st.session_state[session_key]:
        return st.session_state[session_key]
    
    # 其次使用配置文件或环境变量
    try:
        return st.secrets.get(env_var) or os.getenv(env_var)
    except Exception:
        return os.getenv(env_var)

# ==================== 导入组件 ====================
# 日志
try:
    from src.utils.logger import get_logger
    log = get_logger("app")
except Exception:
    import logging
    log = logging.getLogger("app")

# ==================== 组件依赖可用性探测 ====================
CROP_CANVAS_AVAILABLE = False
try:
    from streamlit_cropper import st_cropper  # noqa: F401
    CROP_CANVAS_AVAILABLE = True
except Exception:
    CROP_CANVAS_AVAILABLE = False

# ==================== 双语配置 ====================
I18N = {
    "zh": {
        "app_title": "👔 设计落地助手",
        "app_subtitle": "AI Design to Production",
        "upload_label": "📤 上传设计图/效果图",
        "upload_help": "上传 AI 生成的效果图、款式图等",
        "analysis_params": "⚙️ 分析参数",
        "roi_type": "📍 ROI 区域类型",
        "roi_help": "选择要分析的区域类型，或让AI自动判断",
        "task_auto": "🤖 自动识别",
        "task_fabric": "📐 面料分析",
        "task_print": "🎨 印花工艺",
        "task_construction": "🔧 结构做法",
        "production_context": "🎯 生产上下文",
        "budget": "预算档位",
        "budget_low": "💰 低成本",
        "budget_mid": "💎 中等",
        "budget_high": "👑 高端",
        "scene": "使用场景",
        "scene_casual": "👕 日常休闲",
        "scene_evening": "👗 晚礼服",
        "scene_activewear": "🏃 运动装",
        "scene_office": "💼 商务正装",
        "scene_home": "🏠 家居服",
        "scene_wedding": "💒 婚礼服装",
        "scene_stage": "🎭 舞台表演",
        "constraints": "约束条件（可多选）",
        "constraint_eco": "环保",
        "constraint_wash": "可水洗",
        "constraint_durable": "耐磨",
        "constraint_stretch": "四向弹",
        "constraint_wrinkle": "防皱",
        "constraint_quickdry": "快干",
        "constraint_uv": "抗UV",
        "constraint_antibac": "抗菌",
        "basic_settings": "🔧 基础设置",
        "model": "云端模型",
        "model_qwen": "阿里云通义千问 (Qwen-VL)",
        "model_openai": "OpenAI (GPT-4 Vision)",
        "model_google": "Google (Gemini Vision)",
        "language": "语言",
        "enable_web": "启用联网增强",
        "enable_web_help": "从互联网检索补充信息（如最新材料、供应商、价格等）。注意：会增加 10-15 秒响应时间",
        "web_results": "检索条数",
        "api_status": "API 状态",
        "api_ok": "✅ API KEY 已配置",
        "api_missing": "❌ 缺失 DASHSCOPE_API_KEY",
        "api_key_input": "🔑 API 密钥（可选）",
        "api_key_placeholder": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
        "api_key_help": "在此输入您的阿里云灵积 API 密钥，或在 .streamlit/secrets.toml 中配置",
        "api_get_key": "📖 如何获取 API 密钥？",
        "api_tutorial": "点击查看教程",
        "api_link": "https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key",
        "about": "ℹ️ 关于",
        "about_content": """
**AI 设计落地助手** 基于阿里云通义千问视觉模型，帮助设计师和制版师快速分析设计图的可制造性。

**核心功能**：
- 📐 **面料分析**：识别材质、纱支、克重、光泽度等
- 🎨 **印花工艺**：推荐印花方式、颜色数、制版要求
- 🔧 **结构做法**：针法、缝份、拼接方式分析

**技术支持**：DashScope API + Qwen-VL-Max
        """,
        "main_title": "🎯 AI 设计落地助手",
        "main_subtitle": "将 AI 设计图转化为实际产品方案 | 面料·印花·工艺 智能分析",
        "image_section": "📸 设计图 | 拖动橙色框选择分析区域",
        "crop_hint": "✂️ 拖动橙色框选择区域 | 拖动角点调整大小",
        "crop_failed": "⚠️ 裁剪工具加载失败，切换到数值裁剪模式",
        "manual_crop": "🎯 数值裁剪模式",
        "start_x": "起点X",
        "start_y": "起点Y",
        "end_x": "终点X",
        "end_y": "终点Y",
        "upload_first": "请先上传图片",
        "result_section": "🎯 AI 分析结果",
        "selected_area": "✂️ 已选择区域",
        "analyze_region": "🤖 AI 分析选中区域",
        "analyze_full": "🤖 分析整张图片",
        "analyzing": "🤖 AI 分析中...",
        "error_no_infer": "❌ 云端推理模块不可用",
        "error_no_key": "DASHSCOPE_API_KEY 缺失",
        "footer_crop": "✂️ 交互式裁剪：拖动移动 • 拖角调整大小",
        "footer_cloud": "☁️ 云端识别：DashScope API",
        "footer_tech": "🔧 技术栈：Streamlit + Qwen-VL",
        "summary": "📋 总结",
        "details": "🔍 详细分析",
        "recommendations": "💡 推荐方案",
        "dfm_risks": "⚠️ DFM 风险",
        "next_actions": "📌 下一步行动",
        "material": "材质",
        "weave": "织法",
        "weight": "克重",
        "gloss": "光泽度",
        "stretch": "弹性",
        "handfeel": "手感",
        "finish": "后整理",
        "alternatives": "可替代面料",
        "low_cost": "💰 低成本方案",
        "mid_cost": "💎 中等成本",
        "high_cost": "👑 高端方案",
        "estimated_cost": "预估成本",
        "moq_risk": "MOQ风险",
        "print_type": "印花类型",
        "colors": "颜色数",
        "resolution": "分辨率要求",
        "repeat_size": "重复尺寸",
        "base_fabric": "底布建议",
        "workflow": "推荐工艺流程",
        "risks": "潜在风险",
        "stitch_type": "针法类型",
        "needle_thread": "针/线规格",
        "seam_type": "缝份类型",
        "edge_finish": "边缘处理",
        "interlining": "衬里建议",
        "tolerance": "公差要求",
        "image_load_error": "图片加载失败",
    },
    "en": {
        "app_title": "👔 Design to Production",
        "app_subtitle": "AI Design to Production Assistant",
        "upload_label": "📤 Upload Design Image",
        "upload_help": "Upload AI-generated design or style images",
        "analysis_params": "⚙️ Analysis Parameters",
        "roi_type": "📍 ROI Type",
        "roi_help": "Select analysis type or let AI auto-detect",
        "task_auto": "🤖 Auto Detect",
        "task_fabric": "📐 Fabric Analysis",
        "task_print": "🎨 Print Process",
        "task_construction": "🔧 Construction",
        "production_context": "🎯 Production Context",
        "budget": "Budget Level",
        "budget_low": "💰 Low Cost",
        "budget_mid": "💎 Mid Range",
        "budget_high": "👑 High End",
        "scene": "Use Case",
        "scene_casual": "👕 Casual",
        "scene_evening": "👗 Evening",
        "scene_activewear": "🏃 Activewear",
        "scene_office": "💼 Office",
        "scene_home": "🏠 Home",
        "scene_wedding": "💒 Wedding",
        "scene_stage": "🎭 Stage",
        "constraints": "Constraints (Multi-select)",
        "constraint_eco": "Eco-friendly",
        "constraint_wash": "Washable",
        "constraint_durable": "Durable",
        "constraint_stretch": "4-way Stretch",
        "constraint_wrinkle": "Wrinkle-resistant",
        "constraint_quickdry": "Quick-dry",
        "constraint_uv": "UV-resistant",
        "constraint_antibac": "Anti-bacterial",
        "basic_settings": "🔧 Basic Settings",
        "model": "Cloud Model",
        "model_qwen": "Alibaba Qwen-VL",
        "model_openai": "OpenAI (GPT-4 Vision)",
        "model_google": "Google (Gemini Vision)",
        "language": "Language",
        "enable_web": "Enable Web Search",
        "enable_web_help": "Retrieve additional information from the internet (latest materials, suppliers, prices, etc.). Note: Increases response time by 10-15 seconds",
        "web_results": "Search Results",
        "api_status": "API Status",
        "api_ok": "✅ API KEY Configured",
        "api_missing": "❌ DASHSCOPE_API_KEY Missing",
        "api_key_input": "🔑 API Key (Optional)",
        "api_key_placeholder": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
        "api_key_help": "Enter your Alibaba Cloud DashScope API key here, or configure in .streamlit/secrets.toml",
        "api_get_key": "📖 How to get API Key?",
        "api_tutorial": "View Tutorial",
        "api_link": "https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key",
        "about": "ℹ️ About",
        "about_content": """
**AI Design to Production Assistant** powered by Alibaba Cloud Qwen-VL, helps designers and pattern makers analyze design manufacturability.

**Core Features**:
- 📐 **Fabric Analysis**: Material, yarn count, weight, gloss, etc.
- 🎨 **Print Process**: Print method, color count, production requirements
- 🔧 **Construction**: Stitch types, seam allowances, joining methods

**Tech Stack**: DashScope API + Qwen-VL-Max
        """,
        "main_title": "🎯 AI Design to Production Assistant",
        "main_subtitle": "Transform AI Designs into Production Plans | Fabric · Print · Process Analysis",
        "image_section": "📸 Design Image | Drag Orange Box to Select Area",
        "crop_hint": "✂️ Drag to select area | Drag corners to resize",
        "crop_failed": "⚠️ Crop tool failed, switching to manual mode",
        "manual_crop": "🎯 Manual Crop Mode",
        "start_x": "Start X",
        "start_y": "Start Y",
        "end_x": "End X",
        "end_y": "End Y",
        "upload_first": "Please upload an image first",
        "result_section": "🎯 AI Analysis Results",
        "selected_area": "✂️ Selected Area",
        "analyze_region": "🤖 Analyze Selected Region",
        "analyze_full": "🤖 Analyze Full Image",
        "analyzing": "🤖 Analyzing...",
        "error_no_infer": "❌ Cloud inference unavailable",
        "error_no_key": "DASHSCOPE_API_KEY missing",
        "footer_crop": "✂️ Interactive Crop: Drag to move • Drag corners to resize",
        "footer_cloud": "☁️ Cloud Recognition: DashScope API",
        "footer_tech": "🔧 Tech Stack: Streamlit + Qwen-VL",
        "summary": "📋 Summary",
        "details": "🔍 Detailed Analysis",
        "recommendations": "💡 Recommendations",
        "dfm_risks": "⚠️ DFM Risks",
        "next_actions": "📌 Next Actions",
        "material": "Material",
        "weave": "Weave",
        "weight": "Weight",
        "gloss": "Gloss",
        "stretch": "Stretch",
        "handfeel": "Handfeel",
        "finish": "Finish",
        "alternatives": "Alternatives",
        "low_cost": "💰 Low Cost Option",
        "mid_cost": "💎 Mid Range",
        "high_cost": "👑 High End",
        "estimated_cost": "Est. Cost",
        "moq_risk": "MOQ Risk",
        "print_type": "Print Type",
        "colors": "Colors",
        "resolution": "Resolution",
        "repeat_size": "Repeat Size",
        "base_fabric": "Base Fabric",
        "workflow": "Workflow",
        "risks": "Risks",
        "stitch_type": "Stitch Type",
        "needle_thread": "Needle/Thread",
        "seam_type": "Seam Type",
        "edge_finish": "Edge Finish",
        "interlining": "Interlining",
        "tolerance": "Tolerance",
        "image_load_error": "Image load failed",
    }
}

# ==================== 辅助函数 ====================
# 简化辅助函数 - 仅保留必要功能
def t(key, lang="zh"):
    """翻译辅助函数"""
    return I18N.get(lang, I18N["zh"]).get(key, key)

# ==================== 侧边栏 ====================
# 先初始化语言选择（顶部）
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

with st.sidebar:
    # 语言选择放在最顶部
    lang = st.radio("🌐 Language / 语言", ["zh", "en"], index=0, horizontal=True, key="lang_selector")
    st.session_state["lang"] = lang
    
    st.divider()
    
    st.title(t("app_title", lang))
    st.caption(t("app_subtitle", lang))
    
    uploaded_file = st.file_uploader(
        t("upload_label", lang),
        type=["jpg", "jpeg", "png"],
        help=t("upload_help", lang)
    )
    
    st.divider()
    st.header(t("analysis_params", lang))
    
    # === 区域类型选择 ===
    st.subheader(t("roi_type", lang))
    task_type = st.radio(
        "",
        ["auto", "fabric", "print", "construction"],
        index=0,
        format_func=lambda x: {
            "auto": t("task_auto", lang),
            "fabric": t("task_fabric", lang),
            "print": t("task_print", lang),
            "construction": t("task_construction", lang)
        }[x],
        help=t("roi_help", lang)
    )
    
    st.divider()
    
    # === 上下文参数 ===
    st.subheader(t("production_context", lang))
    
    budget = st.select_slider(
        t("budget", lang),
        options=["low", "mid", "high"],
        value="mid",
        format_func=lambda x: {
            "low": t("budget_low", lang),
            "mid": t("budget_mid", lang),
            "high": t("budget_high", lang)
        }[x]
    )
    
    scene = st.selectbox(
        t("scene", lang),
        ["casual", "evening", "activewear", "office", "home", "wedding", "stage"],
        index=0,
        format_func=lambda x: {
            "casual": t("scene_casual", lang),
            "evening": t("scene_evening", lang),
            "activewear": t("scene_activewear", lang),
            "office": t("scene_office", lang),
            "home": t("scene_home", lang),
            "wedding": t("scene_wedding", lang),
            "stage": t("scene_stage", lang)
        }[x]
    )
    
    # 约束条件的内部值保持英文，显示使用双语
    constraint_map_zh = {
        "eco": "环保", "wash": "可水洗", "durable": "耐磨", 
        "stretch": "四向弹", "wrinkle": "防皱", "quickdry": "快干", 
        "uv": "抗UV", "antibac": "抗菌"
    }
    constraint_map_en = {
        "eco": "Eco-friendly", "wash": "Washable", "durable": "Durable", 
        "stretch": "4-way Stretch", "wrinkle": "Wrinkle-resistant", 
        "quickdry": "Quick-dry", "uv": "UV-resistant", "antibac": "Anti-bacterial"
    }
    constraint_display = constraint_map_zh if lang == "zh" else constraint_map_en
    
    constraints_options = st.multiselect(
        t("constraints", lang),
        list(constraint_display.keys()),
        default=[],
        format_func=lambda x: constraint_display[x]
    )
    # 转换为英文值用于API
    constraints = ",".join(constraints_options) if constraints_options else "none"
    
    st.divider()
    
    # === 基础设置 ===
    st.subheader(t("basic_settings", lang))
    
    # 模型选择
    model_options = {
        "qwen-vl": t("model_qwen", lang),
        "openai-gpt4v": t("model_openai", lang),
        "google-gemini": t("model_google", lang)
    }
    engine = st.selectbox(
        t("model", lang), 
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=0
    )
    enable_web = st.checkbox(
        t("enable_web", lang), 
        value=False,
        help=t("enable_web_help", lang)
    )
    if enable_web:
        k_per_query = st.slider(t("web_results", lang), 1, 10, 4)
    else:
        k_per_query = 4
    
    st.divider()
    
    # === API 密钥配置 ===
    st.subheader(t("api_key_input", lang))
    
    # 根据模型选择确定 API 密钥的环境变量名称和占位符
    api_config = {
        "qwen-vl": {
            "env_var": "DASHSCOPE_API_KEY",
            "placeholder_zh": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
            "placeholder_en": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
            "help_zh": "在此输入您的阿里云灵积 API 密钥，或在 .streamlit/secrets.toml 中配置",
            "help_en": "Enter your Alibaba Cloud DashScope API key here, or configure in .streamlit/secrets.toml",
        },
        "openai-gpt4v": {
            "env_var": "OPENAI_API_KEY",
            "placeholder_zh": "sk-proj-xxxxxxxxxxxxxxxxxx",
            "placeholder_en": "sk-proj-xxxxxxxxxxxxxxxxxx",
            "help_zh": "在此输入您的 OpenAI API 密钥，或在 .streamlit/secrets.toml 中配置",
            "help_en": "Enter your OpenAI API key here, or configure in .streamlit/secrets.toml",
        },
        "google-gemini": {
            "env_var": "GOOGLE_API_KEY",
            "placeholder_zh": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx",
            "placeholder_en": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxx",
            "help_zh": "在此输入您的 Google AI Studio API 密钥，或在 .streamlit/secrets.toml 中配置",
            "help_en": "Enter your Google AI Studio API key here, or configure in .streamlit/secrets.toml",
        }
    }
    
    current_config = api_config.get(engine, api_config["qwen-vl"])
    placeholder = current_config["placeholder_zh"] if lang == "zh" else current_config["placeholder_en"]
    help_text = current_config["help_zh"] if lang == "zh" else current_config["help_en"]
    
    # 用户输入API密钥
    user_api_key = st.text_input(
        label="",
        value="",
        type="password",
        placeholder=placeholder,
        help=help_text,
        key=f"user_api_key_input_{engine}"
    )
    
    # 保存到 session_state
    if user_api_key:
        st.session_state[f"user_api_key_{engine}"] = user_api_key
    
    # 获取最终使用的API密钥（优先级：用户输入 > secrets.toml > 环境变量）
    final_api_key = None
    if f"user_api_key_{engine}" in st.session_state and st.session_state[f"user_api_key_{engine}"]:
        final_api_key = st.session_state[f"user_api_key_{engine}"]
    else:
        try:
            final_api_key = st.secrets.get(current_config["env_var"]) or os.getenv(current_config["env_var"])
        except Exception:
            final_api_key = os.getenv(current_config["env_var"])
    
    # 显示API密钥状态
    if final_api_key:
        status_text = t("api_ok", lang)
        st.success(status_text)
    else:
        status_text = t("api_missing", lang)
        st.error(status_text)
    
    # 根据模型显示不同的教程链接
    with st.expander(t("api_get_key", lang), expanded=False):
        if engine == "qwen-vl":
            if lang == "zh":
                st.markdown("""
                **获取阿里云灵积 API 密钥**
                
                1. 访问 [阿里云灵积平台](https://dashscope.aliyun.com/)
                2. 注册/登录阿里云账号
                3. 在控制台中创建 API Key
                4. 复制密钥并粘贴到上方输入框
                
                🔗 **官方文档**: [如何获取 API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)
                """)
            else:
                st.markdown("""
                **Get Alibaba Cloud DashScope API Key**
                
                1. Visit [Alibaba Cloud DashScope](https://dashscope.aliyun.com/)
                2. Register/Login to your Alibaba Cloud account
                3. Create an API Key in the console
                4. Copy and paste the key above
                
                🔗 **Official Docs**: [How to Get API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)
                """)
        
        elif engine == "openai-gpt4v":
            if lang == "zh":
                st.markdown("""
                **获取 OpenAI API 密钥**
                
                1. 访问 [OpenAI Platform](https://platform.openai.com/)
                2. 注册/登录 OpenAI 账号
                3. 进入 [API Keys 页面](https://platform.openai.com/api-keys)
                4. 点击 "Create new secret key" 创建新密钥
                5. 复制密钥并粘贴到上方输入框
                
                ⚠️ **注意**: 需要 GPT-4 Vision 权限
                
                🔗 **官方文档**: [OpenAI API Keys](https://platform.openai.com/docs/api-reference/authentication)
                
                💰 **定价**: [OpenAI Pricing](https://openai.com/api/pricing/)
                """)
            else:
                st.markdown("""
                **Get OpenAI API Key**
                
                1. Visit [OpenAI Platform](https://platform.openai.com/)
                2. Register/Login to your OpenAI account
                3. Go to [API Keys page](https://platform.openai.com/api-keys)
                4. Click "Create new secret key" to create a new key
                5. Copy and paste the key above
                
                ⚠️ **Note**: GPT-4 Vision access required
                
                🔗 **Official Docs**: [OpenAI API Keys](https://platform.openai.com/docs/api-reference/authentication)
                
                💰 **Pricing**: [OpenAI Pricing](https://openai.com/api/pricing/)
                """)
        
        elif engine == "google-gemini":
            if lang == "zh":
                st.markdown("""
                **获取 Google AI Studio API 密钥**
                
                1. 访问 [Google AI Studio](https://aistudio.google.com/)
                2. 使用 Google 账号登录
                3. 点击 "Get API Key" 获取密钥
                4. 复制密钥并粘贴到上方输入框
                
                ⚠️ **注意**: 需要 Gemini Pro Vision 权限
                
                🔗 **官方文档**: [Google AI Studio](https://ai.google.dev/tutorials/setup)
                
                💰 **定价**: [Gemini Pricing](https://ai.google.dev/pricing)
                """)
            else:
                st.markdown("""
                **Get Google AI Studio API Key**
                
                1. Visit [Google AI Studio](https://aistudio.google.com/)
                2. Login with your Google account
                3. Click "Get API Key" to obtain your key
                4. Copy and paste the key above
                
                ⚠️ **Note**: Gemini Pro Vision access required
                
                🔗 **Official Docs**: [Google AI Studio](https://ai.google.dev/tutorials/setup)
                
                💰 **Pricing**: [Gemini Pricing](https://ai.google.dev/pricing)
                """)
    
    
    st.divider()
    with st.expander(t("about", lang), expanded=False):
        st.markdown(t("about_content", lang))

st.title(t("main_title", lang))
st.caption(t("main_subtitle", lang))

# 结果展示 - 统一 Schema 渲染
def render_result_block(result: dict, engine_name: str, lang: str = "zh"):
    """渲染AI分析结果 - 支持统一JSON Schema"""
    # 提取 meta 信息（如果有）
    meta = result.get("_meta", {})
    actual_model = meta.get("model", engine_name)
    st.caption(f"🤖 {t('model', lang)}: {actual_model}")
    
    # === 调试信息（已禁用） ===
    # st.write("🐛 DEBUG: result keys =", list(result.keys()))
    # st.write("🐛 DEBUG: task =", result.get("task"))
    # debug_info = result.get("_debug")
    # if debug_info:
    #     with st.expander("🔍 详细调试信息", expanded=False):
    #         st.json(debug_info)
    
    # 检查是否是新统一格式（包含task字段）
    task = result.get("task")
    analysis_type = result.get("type")  # 兼容旧格式
    
    # === 新统一格式 ===
    if task in ["fabric", "print", "construction"]:
        # 显示摘要
        summary = result.get("summary")
        if summary:
            st.success(f"**{t('summary', lang)}**: {summary}")
        
        details = result.get("details", {})
        recommendations = result.get("recommendations", {})
        dfm_risks = result.get("dfm_risks", [])
        next_actions = result.get("next_actions", [])
        
        # === 卡片1: 详细分析 ===
        with st.expander(t("details", lang), expanded=True):
            if task == "fabric" and "fabric" in details:
                fab = details["fabric"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{t('material', lang)}**: {fab.get('material', 'N/A')}")
                    st.markdown(f"**{t('weave', lang)}**: {fab.get('weave_or_knit', 'N/A')}")
                    weight = fab.get('weight_gsm', [])
                    if isinstance(weight, list) and len(weight) == 2:
                        st.markdown(f"**{t('weight', lang)}**: {weight[0]}-{weight[1]} gsm")
                    st.markdown(f"**{t('stretch', lang)}**: {fab.get('stretch', 'N/A')}")
                with col2:
                    st.markdown(f"**{t('gloss', lang)}**: {fab.get('gloss', 'N/A')}")
                    st.markdown(f"**{t('handfeel', lang)}**: {fab.get('handfeel', 'N/A')}")
                    finish = fab.get('finish', [])
                    if finish:
                        st.markdown(f"**{t('finish', lang)}**: {', '.join(finish)}")
                
                # 替代面料
                alts = fab.get('alternatives', [])
                if alts:
                    st.markdown(f"**{t('alternatives', lang)}**:")
                    for alt in alts:
                        st.markdown(f"- {alt}")
            
            elif task == "print" and "print" in details:
                prt = details["print"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{t('print_type', lang)}**: {prt.get('type', 'N/A')}")
                    st.markdown(f"**{t('colors', lang)}**: {prt.get('colors', 'N/A')}")
                    st.markdown(f"**{t('resolution', lang)}**: {prt.get('resolution_dpi', 'N/A')} dpi")
                with col2:
                    st.markdown(f"**{t('repeat_size', lang)}**: {prt.get('repeat', 'N/A')}")
                    bases = prt.get('base_fabric_suggestion', [])
                    if bases:
                        st.markdown(f"**{t('base_fabric', lang)}**: {', '.join(bases)}")
                
                # 工艺流程
                workflow = prt.get('workflow', [])
                if workflow:
                    st.markdown(f"**{t('workflow', lang)}**:")
                    for i, step in enumerate(workflow, 1):
                        st.markdown(f"{i}. {step}")
                
                # 风险点
                risks = prt.get('risks', [])
                if risks:
                    st.markdown(f"**⚠️ {t('risks', lang)}**:")
                    for risk in risks:
                        st.markdown(f"- {risk}")
            
            elif task == "construction" and "construction" in details:
                cons = details["construction"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{t('stitch_type', lang)}**: {cons.get('stitch', 'N/A')}")
                    st.markdown(f"**{t('needle_thread', lang)}**: {cons.get('needle_thread', 'N/A')}")
                    st.markdown(f"**{t('seam_type', lang)}**: {cons.get('seam', 'N/A')}")
                with col2:
                    st.markdown(f"**{t('edge_finish', lang)}**: {cons.get('edge_finish', 'N/A')}")
                    st.markdown(f"**{t('interlining', lang)}**: {cons.get('interlining', 'N/A')}")
                    st.markdown(f"**{t('tolerance', lang)}**: {cons.get('tolerance', 'N/A')}")
        
        # === 卡片2: 三档价位建议 ===
        with st.expander(t("recommendations", lang), expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"### {t('low_cost', lang)}")
                st.write(recommendations.get('budget_low', 'N/A'))
            with col2:
                st.markdown(f"### {t('mid_cost', lang)}")
                st.write(recommendations.get('budget_mid', 'N/A'))
            with col3:
                st.markdown(f"### {t('high_cost', lang)}")
                st.write(recommendations.get('budget_high', 'N/A'))
            
            # 采购/工艺建议
            suppliers = recommendations.get('suppliers_or_process', [])
            if suppliers:
                st.markdown(f"**{t('workflow', lang)}**:")
                for sup in suppliers:
                    st.markdown(f"- {sup}")
        
        # === 卡片3: DFM风险 ===
        if dfm_risks:
            with st.expander(t("dfm_risks", lang), expanded=False):
                for risk in dfm_risks:
                    st.warning(f"• {risk}")
        
        # === 卡片4: 下一步行动 ===
        if next_actions:
            with st.expander(t("next_actions", lang), expanded=False):
                for i, action in enumerate(next_actions, 1):
                    st.markdown(f"**{i}.** {action}")
    
    # === 兼容旧格式 ===
    elif analysis_type == "fabric":
        # === 面料分析结果 ===
        st.success("📐 面料区域分析")
        
        material = result.get("material", "未识别")
        st.markdown(f"### 主要材质：**{material}**")
        
        # 多价位方案
        alternatives = result.get("alternatives", [])
        if alternatives:
            st.markdown("#### 💰 制作方案（按价位）")
            for alt in alternatives:
                with st.expander(f"📦 {alt.get('name', '方案')}", expanded=False):
                    st.markdown(f"**材质**: {alt.get('material', 'N/A')}")
                    st.markdown(f"**价格区间**: {alt.get('price_range', 'N/A')}")
                    st.markdown(f"**特性**: {alt.get('characteristics', 'N/A')}")
        
        # 使用场景
        scenarios = result.get("usage_scenarios", [])
        if scenarios:
            st.markdown("#### 🎯 适用场景")
            for scenario in scenarios:
                st.markdown(f"- {scenario}")
        
        # 面料特性
        properties = result.get("properties")
        if properties:
            with st.expander("✨ 面料特性", expanded=False):
                st.write(properties)
        
        # 采购建议
        sourcing = result.get("sourcing_tips")
        if sourcing:
            with st.expander("🛒 采购建议", expanded=False):
                st.write(sourcing)
    
    elif analysis_type == "print":
        # === 印花/图案分析结果 ===
        st.success("🎨 印花/图案区域分析")
        
        pattern = result.get("pattern_style", "未识别")
        st.markdown(f"### 图案风格：**{pattern}**")
        
        # 推荐工艺
        techniques = result.get("recommended_techniques", [])
        if techniques:
            st.markdown("#### 🛠️ 推荐制作工艺")
            for tech in techniques:
                with st.expander(f"⚙️ {tech.get('name', '工艺')}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**成本**: {tech.get('cost', 'N/A')}")
                        st.markdown(f"**适用**: {tech.get('suitable_for', 'N/A')}")
                    with col2:
                        st.markdown(f"**优点**: {tech.get('pros', 'N/A')}")
                        st.markdown(f"**缺点**: {tech.get('cons', 'N/A')}")
        
        # 复杂度和颜色
        col1, col2 = st.columns(2)
        with col1:
            complexity = result.get("complexity")
            if complexity:
                st.markdown(f"**复杂度**: {complexity}")
        with col2:
            color_count = result.get("color_count")
            if color_count:
                st.markdown(f"**色彩数**: {color_count}")
        
        # 生产建议
        tips = result.get("production_tips")
        if tips:
            with st.expander("📋 生产建议", expanded=False):
                st.write(tips)
    
    elif analysis_type == "detail":
        # === 工艺细节分析结果 ===
        st.success("🔧 工艺细节区域分析")
        
        detail_type = result.get("detail_type", "未识别")
        st.markdown(f"### 细节类型：**{detail_type}**")
        
        # 推荐工艺
        techniques = result.get("techniques", [])
        if techniques:
            st.markdown("#### 🛠️ 推荐工艺")
            for tech in techniques:
                st.markdown(f"- {tech}")
        
        # 难度和成本
        col1, col2 = st.columns(2)
        with col1:
            difficulty = result.get("difficulty")
            if difficulty:
                st.markdown(f"**难度**: {difficulty}")
        with col2:
            cost = result.get("cost_estimate")
            if cost:
                st.markdown(f"**成本估算**: {cost}")
        
        # 替代方案
        alternatives = result.get("alternatives", [])
        if alternatives:
            with st.expander("🔄 替代方案", expanded=False):
                for alt in alternatives:
                    st.markdown(f"- {alt}")
    
    else:
        # === 旧格式或解析失败 ===
        st.warning("⚠️ 未识别到明确结果")
        
        # 显示原始响应（总是展开，方便调试）
        raw_json = meta.get("raw") if meta else result.get("raw") or result.get("reasoning")
        if raw_json:
            with st.expander("🔍 查看原始响应", expanded=True):
                st.code(raw_json, language="json")

# ==================== 布局：左预览 / 右推荐 ====================
colL, colR = st.columns([7, 5], gap="large")

with colL:
    st.subheader(t("image_section", lang))
    img = None
    uploaded = uploaded_file
    if uploaded:
        try:
            img = Image.open(uploaded).convert("RGB")
        except Exception as _e:
            st.error(f"{t('image_load_error', lang)}：{_e}")
            img = None

        patch = None

        # 裁剪工具：streamlit-cropper（直接在原图上操作）
        if img and CROP_CANVAS_AVAILABLE:
            try:
                from streamlit_cropper import st_cropper
                
                # 使用 st_cropper 进行可视化裁剪（自带图片显示）
                cropped_img = st_cropper(
                    img, 
                    realtime_update=True,  # 实时更新
                    box_color='#FF6B00',   # 橙色边框
                    aspect_ratio=None,      # 自由比例
                    key="image_cropper"
                )
                
                # st_cropper 直接返回裁剪后的图片
                if cropped_img and cropped_img.size[0] > 0 and cropped_img.size[1] > 0:
                    patch = cropped_img
                        
            except Exception as e:
                st.warning(t("crop_failed", lang))
                log.error(f"st_cropper error: {e}")
                patch = None

        # 兜底：数值裁剪
        if img and patch is None:
            st.caption(t("manual_crop", lang))
            st.image(img, caption=f"{img.size[0]}×{img.size[1]}px", use_container_width=True)
            
            W, H = img.size
            default_size = min(W, H, 300)  # 默认选区大小
            
            col1, col2 = st.columns(2)
            with col1:
                x1 = st.number_input(t("start_x", lang), 0, W, 0, 10)
                y1 = st.number_input(t("start_y", lang), 0, H, 0, 10)
            with col2:
                x2 = st.number_input(t("end_x", lang), 0, W, min(W, default_size), 10)
                y2 = st.number_input(t("end_y", lang), 0, H, min(H, default_size), 10)
            
            if x2 > x1 and y2 > y1:
                patch = img.crop((x1, y1, x2, y2))

        # 保存到 session_state
        st.session_state["__patch__"] = patch
        st.session_state["__img__"] = img
    else:
        st.info(t("upload_first", lang))
        st.session_state["__patch__"] = None
        st.session_state["__img__"] = None

with colR:
    st.subheader(t("result_section", lang))
    patch = st.session_state.get("__patch__")
    img = st.session_state.get("__img__")
    
    # 显示选区信息
    if patch:
        w, h = patch.size
        st.caption(f"{t('selected_area', lang)}：{w}×{h}px")

    # 分析按钮
    rec_btn = st.button(t("analyze_region", lang), use_container_width=True, disabled=not bool(patch), type="primary")
    if rec_btn:
        if cloud_infer is None:
            st.error(t("error_no_infer", lang))
        else:
            api_key_now = get_api_key(engine)
            if not api_key_now:
                st.error(t("error_no_key", lang))
            else:
                with st.spinner(t("analyzing", lang)):
                    result = cloud_infer(
                        patch, 
                        engine=engine, 
                        lang=lang, 
                        enable_web=enable_web, 
                        k_per_query=k_per_query,
                        task_type=task_type,
                        budget=budget,
                        scene=scene,
                        constraints=constraints
                    )
                render_result_block(result, engine, lang)

    # 兜底：整图识别
    if (not patch) and img:
        if st.button(t("analyze_full", lang), use_container_width=True, type="primary"):
            if cloud_infer is None:
                st.error(t("error_no_infer", lang))
            else:
                api_key_now = get_api_key(engine)
                if not api_key_now:
                    st.error(t("error_no_key", lang))
                else:
                    with st.spinner(t("analyzing", lang)):
                        result = cloud_infer(
                            img, 
                            engine=engine, 
                            lang=lang, 
                            enable_web=enable_web, 
                            k_per_query=k_per_query,
                            task_type=task_type,
                            budget=budget,
                            scene=scene,
                            constraints=constraints
                        )
                    render_result_block(result, engine, lang)

# ==================== 底部信息 ====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(t("footer_crop", lang))
with col2:
    st.caption(t("footer_cloud", lang))
with col3:
    st.caption(t("footer_tech", lang))

def main():
    pass

if __name__ == "__main__":
    main()
