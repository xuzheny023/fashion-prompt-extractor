# -*- coding: utf-8 -*-
"""
Internationalization (i18n) support for the fashion fabric analyzer
鍥介檯鍖栨敮鎸佹ā鍧楋紝鐢ㄤ簬鏈嶈闈㈡枡鍒嗘瀽鍣?
"""
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any
try:
    from src.xutils.io import read_json_smart
except Exception:
    from src.utils.io import read_json_smart  # type: ignore


# Base directory for locale files / 鏈湴鍖栨枃浠跺熀纭€鐩綍
LOCALES_DIR = Path(__file__).parent.parent / "locales"


@lru_cache(maxsize=32)
def load_locale(lang: str) -> Dict[str, Any]:
    """
    Load locale file with caching / 鍔犺浇鏈湴鍖栨枃浠讹紙甯︾紦瀛橈級

    Args:
        lang: Language code (e.g., 'en', 'zh') / 璇█浠ｇ爜锛堝 'en', 'zh'锛?

    Returns:
        Dictionary with translations / 缈昏瘧瀛楀吀

    Raises:
        FileNotFoundError: If locale file doesn't exist / 濡傛灉鏈湴鍖栨枃浠朵笉瀛樺湪
        json.JSONDecodeError: If JSON is malformed / 濡傛灉JSON鏍煎紡閿欒
    """
    locale_path = LOCALES_DIR / f"{lang}.json"

    if not locale_path.exists():
        raise FileNotFoundError(f"Locale file not found: {locale_path}")
    return read_json_smart(locale_path)


def t(key: str, lang: str, **kwargs) -> str:
    """
    Get translated string with placeholder support / 鑾峰彇缈昏瘧瀛楃涓诧紙鏀寔鍗犱綅绗︼級

    Args:
        key: Translation key (e.g., 'app.title') / 缈昏瘧閿紙濡?'app.title'锛?
        lang: Language code / 璇█浠ｇ爜
        **kwargs: Placeholder values for string formatting / 瀛楃涓叉牸寮忓寲鐨勫崰浣嶇鍊?

    Returns:
        Translated string with placeholders replaced / 鏇挎崲鍗犱綅绗﹀悗鐨勭炕璇戝瓧绗︿覆

    Examples:
        t('app.title', 'zh') -> 'AI 鏈嶈闈㈡枡鍒嗘瀽甯?
        t('welcome.msg', 'en', name='John') -> 'Welcome, John!'
    """
    try:
        # Try to load the requested language / 灏濊瘯鍔犺浇璇锋眰鐨勮瑷€
        locale_data = load_locale(lang)
    except Exception:
        # Fallback to English if requested language fails / 濡傛灉璇锋眰璇█澶辫触锛屽洖閫€鍒拌嫳鏂?
        try:
            locale_data = load_locale('en')
        except Exception:
            # Final fallback: return the key itself / 鏈€缁堝洖閫€锛氳繑鍥為敭鏈韩
            return key

    # Navigate nested keys (e.g., 'app.title' -> locale_data['app']['title'])
    # 瀵艰埅宓屽閿紙濡?'app.title' -> locale_data['app']['title']锛?
    keys = key.split('.')
    value = locale_data

    try:
        for k in keys:
            value = value[k]
    except (KeyError, TypeError):
        # Key not found in current locale, try English fallback / 褰撳墠璇█涓壘涓嶅埌閿紝灏濊瘯鑻辨枃鍥為€€
        if lang != 'en':
            try:
                locale_data_en = load_locale('en')
                value = locale_data_en
                for k in keys:
                    value = value[k]
            except (KeyError, TypeError, FileNotFoundError, json.JSONDecodeError):
                # Final fallback: return the key itself / 鏈€缁堝洖閫€锛氳繑鍥為敭鏈韩
                return key
        else:
            # Already tried English, return the key / 宸茬粡灏濊瘯杩囪嫳鏂囷紝杩斿洖閿?
            return key

    # Format string with placeholders if any / 濡傛灉鏈夊崰浣嶇鍒欐牸寮忓寲瀛楃涓?
    if kwargs:
        try:
            return str(value).format(**kwargs)
        except (KeyError, ValueError):
            # Formatting failed, return the string as-is / 鏍煎紡鍖栧け璐ワ紝杩斿洖鍘熷瓧绗︿覆
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
    Get list of available language codes / 鑾峰彇鍙敤璇█浠ｇ爜鍒楄〃

    Returns:
        List of language codes / 璇█浠ｇ爜鍒楄〃
    """
    if not LOCALES_DIR.exists():
        return []

    languages = []
    for locale_file in LOCALES_DIR.glob("*.json"):
        lang_code = locale_file.stem
        languages.append(lang_code)

    return sorted(languages)


if __name__ == "__main__":
    # CLI testing / CLI娴嬭瘯
    import sys

    if len(sys.argv) >= 3:
        key = sys.argv[1]
        lang = sys.argv[2]
        kwargs = {}

        # Parse additional kwargs / 瑙ｆ瀽棰濆鍙傛暟
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
