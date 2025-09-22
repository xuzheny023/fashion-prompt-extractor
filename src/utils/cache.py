from __future__ import annotations

import hashlib
import json


def hash_key(obj) -> str:
    try:
        s = json.dumps(obj, sort_keys=True, default=str)
    except Exception:
        s = str(obj)
    return hashlib.md5(s.encode()).hexdigest()


