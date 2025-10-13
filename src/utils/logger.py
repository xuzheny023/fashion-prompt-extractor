# -*- coding: utf-8 -*-
"""
统一日志系统

使用 loguru 提供：
- 带颜色的控制台输出
- 自动轮转的文件日志
- 模块化日志记录

用法：
    from src.utils.logger import get_logger
    
    log = get_logger("my_module")
    log.info("这是一条信息")
    log.warning("这是一个警告")
    log.error("这是一个错误")
"""
from __future__ import annotations
import sys
from pathlib import Path
from loguru import logger

# 读取配置
try:
    from src.config import cfg
    LOG_DIR = cfg.LOG_FILE.parent
    LOG_LEVEL = cfg.LOG_LEVEL
except Exception:
    # 如果配置不可用，使用默认值
    LOG_DIR = Path("logs")
    LOG_LEVEL = "INFO"

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 移除默认的 handler
logger.remove()

# 添加控制台输出（带颜色）
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[mod]}</cyan> | <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True,
)

# 添加文件输出（自动轮转）
logger.add(
    LOG_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[mod]} | {message}",
    level=LOG_LEVEL,
    rotation="5 MB",       # 单个文件最大 5MB
    retention="10 days",   # 保留最近 10 天的日志
    compression="zip",     # 压缩旧日志
    enqueue=True,          # 异步写入
    backtrace=True,        # 显示完整堆栈
    diagnose=False,        # 生产环境关闭变量值显示
)


def get_logger(name: str = "app"):
    """
    获取模块化 logger
    
    Args:
        name: 模块名称，用于标识日志来源
    
    Returns:
        绑定了模块名称的 logger 对象
    
    Example:
        >>> log = get_logger("ui")
        >>> log.info("UI ready")
        2025-10-12 23:45:00 | INFO     | ui | UI ready
    """
    return logger.bind(mod=name)


# 便捷别名
def info(msg: str, module: str = "app"):
    """快速记录 info 日志"""
    get_logger(module).info(msg)


def warning(msg: str, module: str = "app"):
    """快速记录 warning 日志"""
    get_logger(module).warning(msg)


def error(msg: str, module: str = "app"):
    """快速记录 error 日志"""
    get_logger(module).error(msg)


def debug(msg: str, module: str = "app"):
    """快速记录 debug 日志"""
    get_logger(module).debug(msg)


# 导出
__all__ = [
    'get_logger',
    'logger',
    'info',
    'warning',
    'error',
    'debug',
]


