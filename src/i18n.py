# -*- coding: utf-8 -*-
"""
Internationalization (i18n) support for the fashion fabric analyzer
国际化支持模块,用于时尚面料分析器
"""
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any
try:
    from src.xutils.io import read_json_smart
except Exception:
    from src.utils.io import read_json_smart  # type: ignore


# Base directory for locale files
LOCALES_DIR = Path(__file__).parent.parent / "locales"


@lru_cache(maxsize=32)
def load_locale(lang: str) -> Dict[str, Any]:
    """
    Load locale file with caching.

    Args:
        lang: Language code (e.g., 'en', 'zh')

    Returns:
        Dictionary with translations

    Raises:
        FileNotFoundError: If locale file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    locale_path = LOCALES_DIR / f"{lang}.json"

    if not locale_path.exists():
        raise FileNotFoundError(f"Locale file not found: {locale_path}")
    return read_json_smart(locale_path)


def t(key: str, lang: str, **kwargs) -> str:
    """
    Get translated string with placeholder support.

    Args:
        key: Translation key (e.g., 'app.title')
        lang: Language code
        **kwargs: Placeholder values for string formatting

    Returns:
        Translated string with placeholders replaced

    Examples:
        t('app.title', 'zh') -> 'AI 时尚面料分析器'
        t('welcome.msg', 'en', name='John') -> 'Welcome, John!'
    """
    try:
        # Try to load the requested language
        locale_data = load_locale(lang)
    except Exception:
        # Fallback to English if requested language fails
        try:
            locale_data = load_locale('en')
        except Exception:
            # Final fallback: return the key itself
            return key

    # Navigate nested keys (e.g., 'app.title' -> locale_data['app']['title'])
    keys = key.split('.')
    value = locale_data

    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        # Key not found in current locale, try English fallback
        if lang != 'en':
            try:
                locale_data_en = load_locale('en')
                value = locale_data_en
                for k in keys:
                    value = value[k]
            except (KeyError, TypeError, FileNotFoundError, json.JSONDecodeError):
                # Final fallback: return the key itself
                return key
        else:
            # Already tried English, return the key
            return key

    # Format string with placeholders if any
    if kwargs:
        try:
            return str(value).format(**kwargs)
        except (KeyError, ValueError):
            # Formatting failed, return the string as-is
            return str(value)

    return str(value)


def clear_cache() -> None:
    """
    Clear the locale cache / 娓呯┖鏈湴鍖栫紦瀛?
    Useful when locale files are updated during runtime / 杩愯鏃舵洿鏂版湰鍦板寲鏂囦欢鏃舵湁鐢?
    """
    load_locale.cache_clear()


def get_available_languages() -> list[str]:
    """
    Get list of available language codes / 鑾峰彇鍙敤璇█浠g爜鍒楄〃

    Returns:
        List of language codes / 璇█浠g爜鍒楄〃
    """
    if not LOCALES_DIR.exists():
        return []

    languages = []
    for locale_file in LOCALES_DIR.glob("*.json"):
        lang_code = locale_file.stem
        languages.append(lang_code)

    return sorted(languages)


if __name__ == "__main__":
    # CLI testing
    import sys

    if len(sys.argv) >= 3:
        key = sys.argv[1]
        lang = sys.argv[2]
        kwargs = {}

        # Parse additional kwargs
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
