# -*- coding: utf-8 -*-
# Simple emoji icon resolver
_EMOJI = {
    "actions": "⚙️",
    "history": "🗂️",
    "recommend": "🎯",
    "analysis": "🔍",
    "confidence": "📈",
    "upload": "📤",
}

def E(key: str) -> str:
    return _EMOJI.get(key, "")
