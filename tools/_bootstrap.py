# -*- coding: utf-8 -*-
"""
Bootstrap utilities to make CLI scripts robust in Cursor/PowerShell:
- Ensures stdout/stderr are line-buffered via PYTHONUNBUFFERED env (caller recommended)
- Enables faulthandler if available
- Registers pillow-heif opener for AVIF/HEIF
- Adds project root to sys.path for stable imports
- Provides helper to wrap main() with unified error reporting
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Enable faulthandler early
try:
    import faulthandler  # type: ignore
    faulthandler.enable()
except Exception:
    pass

# Register AVIF/HEIF so PIL can open .avif/.heic if package installed
try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass


def run_main_safely(main_func) -> int:
    """Run a main() callable with robust error reporting and flush behavior."""
    try:
        code = int(main_func() or 0)
        sys.stdout.flush()
        sys.stderr.flush()
        return code
    except KeyboardInterrupt:
        print("[INTERRUPTED] User cancelled.", flush=True)
        return 130
    except Exception as e:
        import traceback
        print("[ERROR] Unhandled exception:", flush=True)
        traceback.print_exc()
        sys.stderr.flush()
        return 1
