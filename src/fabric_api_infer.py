# -*- coding: utf-8 -*-
"""
云端 VLM 面料识别 - 稳定版
Cloud VLM fabric recognition with structured prompts and robust JSON parsing.
"""

from typing import Dict, List
from PIL import Image
import io
import base64
import os
import json
import re

try:
    import dashscope
    from dashscope import MultiModalConversation
except Exception:
    dashscope = None
    MultiModalConversation = None

# ==================== 模型映射 ====================
MODEL_MAP = {
    "qwen-vl": "qwen-vl-plus",
    "qwen-vl-plus": "qwen-vl-plus",
}

# ==================== 系统提示词 ====================
SYS_PROMPT_ZH = (
    "你是资深面料工程师。请基于给定图像中**被框选区域**，按以下结构化JSON输出："
    '{"labels":[字符串数组，最多3个，按可能性降序],"confidences":[0-1数组，与labels对齐],'
    '"reasoning":"你的判断依据（纹理、光泽、组织、密度、反光、起毛、褶皱等）"}。'
    "若无法准确判断，请给出可能方向并降低置信度。禁止输出除JSON外的多余文字。"
)

SYS_PROMPT_EN = (
    "You are a senior textile engineer. Based on the cropped region, "
    'return pure JSON: {"labels":[... up to 3],"confidences":[0-1],"reasoning":"..."}. '
    "If uncertain, provide likely directions with lower confidences. No extra text."
)

# ==================== 辅助函数 ====================
def image_to_dashscope_bytes(img: Image.Image) -> bytes:
    """将 PIL Image 转换为 DashScope 接受的字节流"""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def make_prompt(lang: str) -> str:
    """根据语言选择系统提示词"""
    return SYS_PROMPT_ZH if lang == "zh" else SYS_PROMPT_EN

def try_parse_json(text: str) -> dict:
    """
    简单 JSON 抽取（从大段文字里找首个 {...}）
    
    尝试策略：
    1. 直接 json.loads
    2. 提取 markdown 代码块
    3. 正则提取第一个 JSON 对象
    """
    # 策略1: 直接解析
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    
    # 策略2: 提取 markdown 代码块
    if "```json" in text:
        try:
            json_text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    if "```" in text:
        try:
            json_text = text.split("```")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    # 策略3: 正则提取
    match = re.search(r'\{.*\}', text, flags=re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    
    return {}

def ensure_min_size(pil_img: Image.Image, tgt: int = 640) -> Image.Image:
    """保证传云端的图片最短边≥tgt，避免太小导致识别失败"""
    w, h = pil_img.size
    if min(w, h) >= tgt:
        return pil_img
    scale = tgt / min(w, h)
    nw, nh = int(w * scale), int(h * scale)
    return pil_img.resize((nw, nh), Image.BICUBIC)

# ==================== 云端推理 ====================
def cloud_infer(
    pil_image: Image.Image,
    engine: str,
    lang: str = "zh",
    enable_web: bool = False,
    k_per_query: int = 4
) -> Dict:
    """
    云端面料识别 - 稳定版
    
    Args:
        pil_image: PIL Image 对象
        engine: 模型引擎 ("qwen-vl", "qwen-vl-plus")
        lang: 语言 ("zh", "en")
        enable_web: 是否启用联网检索（暂未实现）
        k_per_query: 每个候选检索条数（暂未实现）
    
    Returns:
        {
            "labels": ["面料1", "面料2", ...],
            "confidences": [0.6, 0.3, 0.1],
            "reasoning": "判断依据",
            "raw": "原始响应文本",
            "model": "实际使用的模型名",
            "engine": "cloud"
        }
    """
    # 检查依赖
    if dashscope is None or MultiModalConversation is None:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": "DashScope SDK 未安装。请运行: pip install dashscope",
            "raw": "",
            "model": engine,
            "engine": "error"
        }
    
    # 获取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        # 尝试从 streamlit secrets 读取
        try:
            import streamlit as st
            api_key = st.secrets.get("DASHSCOPE_API_KEY")
        except Exception:
            pass
    
    if not api_key:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": "缺少 DASHSCOPE_API_KEY。请在 .streamlit/secrets.toml 或环境变量中配置。",
            "raw": "",
            "model": engine,
            "engine": "error"
        }
    
    # 设置 API Key
    dashscope.api_key = api_key
    
    # 选择模型
    model = MODEL_MAP.get(engine, "qwen-vl-plus")
    
    # 确保图片尺寸足够
    pil_image = ensure_min_size(pil_image, 640)
    
    # 转换为字节流
    img_bytes = image_to_dashscope_bytes(pil_image)
    
    # 构建消息
    sys_msg = {"role": "system", "content": [{"text": make_prompt(lang)}]}
    user_msg = {
        "role": "user",
        "content": [
            {"image": img_bytes},
            {"text": "识别该裁剪区域的材质" if lang == "zh" else "Identify the material of this cropped region"}
        ]
    }
    
    # 调用 API
    try:
        response = MultiModalConversation.call(
            model=model,
            messages=[sys_msg, user_msg],
            top_p=0.7,
            temperature=0.2,
        )
        
        # 提取响应文本
        if hasattr(response, 'output'):
            if isinstance(response.output, dict):
                raw_text = response.output.get('text', '') or response.output.get('content', '') or str(response.output)
            else:
                raw_text = str(response.output)
        else:
            raw_text = str(response)
        
        # 解析 JSON
        data = try_parse_json(raw_text)
        
        if not data:
            # 解析失败，返回原始文本
            return {
                "labels": [],
                "confidences": [],
                "reasoning": raw_text[:500] if raw_text else "模型返回为空",
                "raw": raw_text,
                "model": model,
                "engine": "cloud"
            }
        
        # 提取字段并兜底
        labels = data.get("labels", [])
        confidences = data.get("confidences", [])
        reasoning = data.get("reasoning", raw_text)
        
        # 对齐 labels 和 confidences
        if len(confidences) < len(labels):
            # 补齐置信度
            remaining = 1.0 - sum(confidences)
            avg_conf = remaining / max(1, len(labels) - len(confidences))
            confidences.extend([avg_conf] * (len(labels) - len(confidences)))
        elif len(confidences) > len(labels):
            # 截断置信度
            confidences = confidences[:len(labels)]
        
        # 归一化置信度
        total_conf = sum(confidences) if confidences else 1.0
        if total_conf > 0:
            confidences = [c / total_conf for c in confidences]
        
        return {
            "labels": labels,
            "confidences": confidences,
            "reasoning": reasoning,
            "raw": raw_text,
            "model": model,
            "engine": "cloud"
        }
    
    except Exception as e:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": f"调用失败: {type(e).__name__}: {str(e)}",
            "raw": "",
            "model": model,
            "engine": "error"
        }

# ==================== 兼容接口 ====================
def analyze_image(
    image: Image.Image,
    api_key: str = None,
    lang: str = "zh",
    engine: str = "qwen-vl",
    enable_web: bool = False,
    k_per_query: int = 4
) -> Dict:
    """
    分析图片 - 兼容旧接口
    
    Args:
        image: PIL Image 对象
        api_key: API Key（可选，会自动从环境变量或 secrets 读取）
        lang: 语言
        engine: 模型引擎
        enable_web: 是否启用联网检索
        k_per_query: 每个候选检索条数
    
    Returns:
        {
            "result": {
                "labels": [...],
                "confidences": [...],
                "reasoning": "...",
                "raw": "..."
            },
            "meta": {
                "engine": "cloud",
                "model": "qwen-vl-plus"
            }
        }
    """
    # 如果提供了 api_key，设置到环境变量
    if api_key:
        os.environ["DASHSCOPE_API_KEY"] = api_key
    
    # 调用云端推理
    result = cloud_infer(
        pil_image=image,
        engine=engine,
        lang=lang,
        enable_web=enable_web,
        k_per_query=k_per_query
    )
    
    # 提取 meta 信息
    model = result.pop("model", engine)
    engine_status = result.pop("engine", "cloud")
    
    return {
        "result": result,
        "meta": {
            "engine": engine_status,
            "model": model
        }
    }
