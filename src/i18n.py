# -*- coding: utf-8 -*-
"""
Internationalization (i18n) support for the fashion fabric analyzer
国际化支持模块，用于服装面料分析器
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any


# Base directory for locale files / 本地化文件基础目录
LOCALES_DIR = Path(__file__).parent.parent / "locales"


@lru_cache(maxsize=32)
def load_locale(lang: str) -> Dict[str, Any]:
    """
    Load locale file with caching / 加载本地化文件（带缓存）
    
    Args:
        lang: Language code (e.g., 'en', 'zh') / 语言代码（如 'en', 'zh'）
    
    Returns:
        Dictionary with translations / 翻译字典
    
    Raises:
        FileNotFoundError: If locale file doesn't exist / 如果本地化文件不存在
        json.JSONDecodeError: If JSON is malformed / 如果JSON格式错误
    """
    locale_path = LOCALES_DIR / f"{lang}.json"
    
    if not locale_path.exists():
        raise FileNotFoundError(f"Locale file not found: {locale_path}")
    
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def t(key: str, lang: str, **kwargs) -> str:
    """
    Get translated string with placeholder support / 获取翻译字符串（支持占位符）
    
    Args:
        key: Translation key (e.g., 'app.title') / 翻译键（如 'app.title'）
        lang: Language code / 语言代码
        **kwargs: Placeholder values for string formatting / 字符串格式化的占位符值
    
    Returns:
        Translated string with placeholders replaced / 替换占位符后的翻译字符串
    
    Examples:
        t('app.title', 'zh') -> 'AI 服装面料分析师'
        t('welcome.msg', 'en', name='John') -> 'Welcome, John!'
    """
    try:
        # Try to load the requested language / 尝试加载请求的语言
        locale_data = load_locale(lang)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to English if requested language fails / 如果请求语言失败，回退到英文
        try:
            locale_data = load_locale('en')
        except (FileNotFoundError, json.JSONDecodeError):
            # Final fallback: return the key itself / 最终回退：返回键本身
            return key
    
    # Navigate nested keys (e.g., 'app.title' -> locale_data['app']['title'])
    # 导航嵌套键（如 'app.title' -> locale_data['app']['title']）
    keys = key.split('.')
    value = locale_data
    
    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        # Key not found in current locale, try English fallback / 当前语言中找不到键，尝试英文回退
        if lang != 'en':
            try:
                locale_data_en = load_locale('en')
                value = locale_data_en
                for k in keys:
                    value = value[k]
            except (KeyError, TypeError, FileNotFoundError, json.JSONDecodeError):
                # Final fallback: return the key itself / 最终回退：返回键本身
                return key
        else:
            # Already tried English, return the key / 已经尝试过英文，返回键
            return key
    
    # Format string with placeholders if any / 如果有占位符则格式化字符串
    if kwargs:
        try:
            return str(value).format(**kwargs)
        except (KeyError, ValueError):
            # Formatting failed, return the string as-is / 格式化失败，返回原字符串
            return str(value)
    
    return str(value)


def clear_cache() -> None:
    """
    Clear the locale cache / 清空本地化缓存
    Useful when locale files are updated during runtime / 运行时更新本地化文件时有用
    """
    load_locale.cache_clear()


def get_available_languages() -> list[str]:
    """
    Get list of available language codes / 获取可用语言代码列表
    
    Returns:
        List of language codes / 语言代码列表
    """
    if not LOCALES_DIR.exists():
        return []
    
    languages = []
    for locale_file in LOCALES_DIR.glob("*.json"):
        lang_code = locale_file.stem
        languages.append(lang_code)
    
    return sorted(languages)


if __name__ == "__main__":
    # CLI testing / CLI测试
    import sys
    
    if len(sys.argv) >= 3:
        key = sys.argv[1]
        lang = sys.argv[2]
        kwargs = {}
        
        # Parse additional kwargs / 解析额外参数
        for arg in sys.argv[3:]:
            if '=' in arg:
                k, v = arg.split('=', 1)
                kwargs[k] = v
        
        result = t(key, lang, **kwargs)
        print(result)
    else:
        print("Usage: python -m src.i18n <key> <lang> [key=value ...]")
        print("Example: python -m src.i18n app.title zh")
        print("Example: python -m src.i18n welcome.msg en name=John")
