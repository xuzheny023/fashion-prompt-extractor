# -*- coding: utf-8 -*-
"""
工具模块 - Cloud-Only Minimal Version
仅保留日志功能
"""

# 延迟导入，避免依赖问题
def get_logger(name: str = "app"):
    """延迟导入 get_logger"""
    try:
        from .logger import get_logger as _get_logger
        return _get_logger(name)
    except ImportError:
        # 如果 loguru 不可用，返回一个简单的 logger
        import logging
        return logging.getLogger(name)

__all__ = ['get_logger']
