# -*- coding: utf-8 -*-
"""
统一配置中心

使用 pydantic-settings 管理所有配置项，支持：
- 默认值
- 环境变量覆盖
- .env 文件
- 类型验证

用法：
    from src.config import cfg
    
    print(cfg.FABRIC_BANK)  # 获取路径
    print(cfg.TOPC)         # 获取参数
"""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class _Settings(BaseSettings):
    """全局配置类（单例）"""
    
    # ==================== 基础路径 ====================
    ROOT: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = ROOT / "data"
    CACHE_DIR: Path = ROOT / "cache"
    FABRIC_BANK: Path = DATA_DIR / "fabric_bank.npz"
    FABRIC_CENTROIDS: Path = DATA_DIR / "fabric_centroids.npz"
    FABRIC_LABELS: Path = DATA_DIR / "fabric_labels.json"
    FABRIC_ALIASES: Path = DATA_DIR / "fabric_aliases.json"
    FABRIC_RULES: Path = DATA_DIR / "fabric_rules.json"
    FABRIC_FINE_RULES: Path = DATA_DIR / "fabric_fine_rules.json"
    
    # ==================== 检索参数 ====================
    MIN_SAMPLES: int = 3        # 最少样本数
    TOPC: int = 12              # 粗排进入精排的类数
    TOPK: int = 5               # 返回的候选面料数
    LOW_CONF: float = 0.30      # 低置信度阈值
    CLOSE_GAP: float = 0.03     # 分数差距阈值（触发精排）
    
    # ==================== 模型缓存 ====================
    OPENCLIP_CACHE: Path = CACHE_DIR / "open_clip"
    HF_CACHE: Path = CACHE_DIR / "huggingface"
    
    # ==================== CLIP 模型配置 ====================
    # 通道1: HuggingFace (OpenAI) CLIP
    HF_MODEL_DIR: str = ""  # 留空则自动下载，或指定本地路径
    HF_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    
    # 通道2: OpenCLIP (LAION)
    OC_ARCH: str = "ViT-H-14"
    OC_PRETRAINED: str = "laion2b_s32b_b79k"
    
    # ==================== AI 复核 ====================
    AI_BACKEND: str = "none"           # "none" | "openai" | "ollama"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""           # 从环境变量读取
    OLLAMA_MODEL: str = "llava:13b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # ==================== 功能开关 ====================
    ENABLE_CLIP: bool = True           # 启用 CLIP 检索
    ENABLE_FAISS: bool = True          # 启用 FAISS 加速（如果可用）
    ENABLE_CACHE: bool = True          # 启用缓存
    ENABLE_PROGRESS: bool = True       # 启用进度条
    
    # ==================== UI 配置 ====================
    PREVIEW_WIDTH: int = 720
    DEFAULT_MAX_SIDE: int = 1024
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"            # DEBUG | INFO | WARNING | ERROR
    LOG_FILE: Path = ROOT / "logs" / "app.log"
    
    # ==================== Pydantic 配置 ====================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保必要的目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.OPENCLIP_CACHE.mkdir(parents=True, exist_ok=True)
        if self.LOG_FILE.parent:
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ==================== 全局单例 ====================
cfg = _Settings()


# ==================== 便捷函数 ====================
def check_vector_bank() -> bool:
    """检查向量库是否存在"""
    return cfg.FABRIC_BANK.exists() and cfg.FABRIC_CENTROIDS.exists()


def get_cache_dir(name: str) -> Path:
    """获取特定缓存目录"""
    cache_dir = cfg.CACHE_DIR / name
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def is_ai_enabled() -> bool:
    """检查是否启用 AI 复核"""
    return cfg.AI_BACKEND != "none"


# ==================== 导出 ====================
__all__ = [
    'cfg',
    'check_vector_bank',
    'get_cache_dir',
    'is_ai_enabled',
]


