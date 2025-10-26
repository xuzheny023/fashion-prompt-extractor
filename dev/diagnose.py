#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive diagnostics for dependency and environment issues.
Helps identify why the app might not be using the correct Python interpreter.
"""

import sys
import os
import importlib.util
import subprocess
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_python_info():
    """Get detailed Python interpreter information."""
    return {
        "executable": sys.executable,
        "version": sys.version,
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "is_venv": sys.prefix != sys.base_prefix,
        "path": sys.path[:5],  # First 5 paths
    }

def check_venv():
    """Check if running in the correct venv."""
    workspace = Path(__file__).parent.parent
    expected_venv = workspace / ".venv" / "Scripts" / "python.exe"
    current = Path(sys.executable)
    
    return {
        "workspace": str(workspace),
        "expected_venv": str(expected_venv),
        "expected_exists": expected_venv.exists(),
        "current_python": str(current),
        "using_correct_venv": current.resolve() == expected_venv.resolve(),
    }

def check_module(module_name: str):
    """Check if a module is available and get its location."""
    spec = importlib.util.find_spec(module_name)
    if spec:
        return {
            "available": True,
            "location": spec.origin if spec.origin else "built-in",
        }
    return {"available": False, "location": None}

def check_vscode_settings():
    """Check VSCode settings for Python interpreter."""
    workspace = Path(__file__).parent.parent
    settings_file = workspace / ".vscode" / "settings.json"
    
    if not settings_file.exists():
        return {"exists": False, "interpreter": None}
    
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = json.load(f)
            interpreter = settings.get("python.defaultInterpreterPath")
            return {"exists": True, "interpreter": interpreter}
    except Exception as e:
        return {"exists": True, "error": str(e)}

def main():
    """Run comprehensive diagnostics."""
    print("\n" + "=" * 70)
    print("  🔬 Comprehensive Environment Diagnostics")
    print("=" * 70 + "\n")
    
    # Python Info
    print("📍 Python Interpreter Info")
    print("-" * 70)
    py_info = get_python_info()
    print(f"  Executable: {py_info['executable']}")
    print(f"  Version: {py_info['version'].split()[0]}")
    print(f"  In virtualenv: {'✅ Yes' if py_info['is_venv'] else '❌ No'}")
    print(f"  sys.prefix: {py_info['prefix']}")
    print()
    
    # Venv Check
    print("🏠 Virtual Environment Check")
    print("-" * 70)
    venv_info = check_venv()
    print(f"  Workspace: {venv_info['workspace']}")
    print(f"  Expected venv: {venv_info['expected_venv']}")
    print(f"  Venv exists: {'✅ Yes' if venv_info['expected_exists'] else '❌ No'}")
    print(f"  Using correct venv: {'✅ Yes' if venv_info['using_correct_venv'] else '❌ No'}")
    if not venv_info['using_correct_venv']:
        print(f"  ⚠️  Currently using: {venv_info['current_python']}")
    print()
    
    # VSCode Settings
    print("⚙️  VSCode Settings")
    print("-" * 70)
    vscode = check_vscode_settings()
    if vscode["exists"]:
        if "error" in vscode:
            print(f"  ⚠️  Error reading settings: {vscode['error']}")
        else:
            print(f"  Settings file: ✅ Exists")
            print(f"  Interpreter path: {vscode.get('interpreter', 'Not set')}")
    else:
        print(f"  Settings file: ❌ Not found")
        print(f"  Recommendation: Create .vscode/settings.json")
    print()
    
    # Module Checks
    print("📦 Critical Modules")
    print("-" * 70)
    modules = [
        ("streamlit", "streamlit"),
        ("PIL", "pillow"),
        ("numpy", "numpy"),
        ("dashscope", "dashscope"),
        ("streamlit_drawable_canvas", "streamlit-drawable-canvas"),
        ("duckduckgo_search", "duckduckgo-search"),
        ("readability", "readability-lxml"),
        ("requests", "requests"),
    ]
    
    all_ok = True
    for module_name, package_name in modules:
        info = check_module(module_name)
        if info["available"]:
            location = info["location"]
            if len(location) > 60:
                location = "..." + location[-57:]
            print(f"  ✅ {module_name:<30} {location}")
        else:
            print(f"  ❌ {module_name:<30} NOT FOUND (pip: {package_name})")
            all_ok = False
    print()
    
    # Summary
    print("=" * 70)
    if all_ok and venv_info['using_correct_venv']:
        print("✅ All checks passed! Environment is correctly configured.")
    else:
        print("⚠️  Issues detected. Recommended actions:")
        print()
        if not venv_info['using_correct_venv']:
            print("  1. Ensure you're using the correct Python interpreter:")
            print(f"     {venv_info['expected_venv']}")
            print()
            print("  2. In VSCode/Cursor:")
            print("     • Press Ctrl+Shift+P")
            print("     • Type: 'Python: Select Interpreter'")
            print("     • Choose: .venv\\Scripts\\python.exe")
            print()
        if not all_ok:
            print("  3. Install missing dependencies:")
            print(f"     {sys.executable} dev\\preflight.py --install")
            print()
            print("  4. Or run full setup:")
            print("     .\\scripts\\ensure_venv.ps1")
            print()
    print("=" * 70 + "\n")
    
    return 0 if (all_ok and venv_info['using_correct_venv']) else 1


if __name__ == "__main__":
    sys.exit(main())

