from __future__ import annotations

# Centralized emoji utilities for Streamlit UI
# Goal: avoid multi-codepoint/ZJW/shortcodes that cause runtime errors

# Whitelist of semantically named emojis. Prefer simple single-codepoint where possible.
SAFE_EMOJI: dict[str, str] = {
    "photo": "📷",
    "target": "🎯",
    "gear": "⚙️",   # If this fails on your env, replace with "⚙"
    "ok": "✅",
    "error": "❌",
    "warn": "⚠️",
    "time": "⏱️",   # If this fails, replace with "⏱"
    "brain": "💡",   # Use 💡 instead of 🧠 for broader compatibility
    "speed": "🚀",
    "search": "🔎",  # Magnifier for search/recognition
    "history": "🕓",  # Use clock instead of 🗂️ which may include VS-16
    "save": "💾",
    "calc": "📈",
    "info": "ℹ️",   # If this fails, replace with a simpler fallback like "i"
}

# Backward compatibility mapping
SAFE = SAFE_EMOJI
UNSAFE = {
    "🧠": "brain",
    "🪄": "speed",   # magic → speed (approx)
    "🧵": "target",  # fabric/thread → target (approx)
    "🩶": "ok",      # fallback
}

try:
    import regex as _regex  # optional dependency for grapheme clusters
except Exception:  # pragma: no cover
    _regex = None


def is_single_grapheme(s: str) -> bool:
    if not s:
        return False
    # Prefer regex \X if available
    if _regex is not None:
        try:
            clusters = _regex.findall(r"\X", s)
            return len(clusters) == 1
        except Exception:
            pass
    # Conservative fallback: common single-codepoint emojis are length 1
    try:
        return len(s) == 1
    except Exception:
        return False


def normalize(e: str | None, fallback: str = "ℹ️") -> str:
    val = (e or "").strip()
    if not val:
        return fallback
    # reject shortcodes like :rocket:
    if (val.startswith(":") and val.endswith(":")):
        return fallback
    # reject multi-grapheme sequences
    if not is_single_grapheme(val):
        return fallback
    return val


def safe(key: str, fallback_key: str = "info") -> str:
    base = SAFE_EMOJI.get(key, "")
    fb = SAFE_EMOJI.get(fallback_key, "ℹ️")
    return normalize(base, fb)


# Maintain old E(...) alias for compatibility
E = safe

# Keys for tooling/lint purposes
SAFE_KEYS = sorted(SAFE_EMOJI.keys())


if __name__ == "__main__":
    print("[icons] sanity check:")
    for k in ("ok", "error", "warn", "time", "brain", "speed", "search", "history", "save", "calc", "info"):
        v = safe(k)
        print(f" - {k}: {v!r}, single_grapheme={is_single_grapheme(v)}")


