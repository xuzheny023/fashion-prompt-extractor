# -*- coding: utf-8 -*-
import logging

_LOGGERS = {}

def get_logger(name: str = "app"):
    if name in _LOGGERS:
        return _LOGGERS[name]
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        fmt = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    _LOGGERS[name] = logger
    return logger
