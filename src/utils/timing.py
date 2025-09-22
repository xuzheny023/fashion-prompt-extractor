from __future__ import annotations

from time import perf_counter
from functools import wraps


def timeit(tag: str):
    def deco(f):
        @wraps(f)
        def g(*a, **kw):
            t0 = perf_counter()
            r = f(*a, **kw)
            dt = perf_counter() - t0
            print(f"[time] {tag}: {dt:.3f}s")
            return r
        return g
    return deco


