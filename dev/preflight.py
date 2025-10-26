#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Preflight dependency checker with auto-install capability.
Ensures all critical packages are available in the current interpreter.
"""

import sys
import subprocess
import os
import importlib.util
import shutil
from typing import List, Dict

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MIRROR = os.environ.get("PIP_INDEX_URL", "https://pypi.tuna.tsinghua.edu.cn/simple")

# Map from import name to package name (for cases where they differ)
PACKAGE_MAP = {
    "PIL": "pillow",
    "streamlit_drawable_canvas": "streamlit-drawable-canvas",
    "duckduckgo_search": "duckduckgo-search",
    "readability": "readability-lxml",
}

CRITICAL_MODULES = [
    "streamlit",
    "PIL",
    "numpy",
    "dashscope",
    "streamlit_drawable_canvas",
    "duckduckgo_search",
    "readability",
    "requests",
]


def has_module(name: str) -> bool:
    """Check if a module can be imported."""
    return importlib.util.find_spec(name) is not None


def get_package_name(module_name: str) -> str:
    """Convert module name to pip package name."""
    return PACKAGE_MAP.get(module_name, module_name)


def ensure_packages(pkgs: List[str], install: bool = False) -> Dict:
    """
    Check if packages are available in current interpreter.
    
    Args:
        pkgs: List of module names to check
        install: If True, attempt to install missing packages
        
    Returns:
        Dictionary with:
        - ok: bool - All packages available
        - missing: list - Missing module names
        - missing_packages: list - Missing pip package names
        - python: str - Current Python executable path
        - pip: str - Pip executable path
    """
    missing = [p for p in pkgs if not has_module(p)]
    missing_packages = [get_package_name(m) for m in missing]
    
    pip_path = shutil.which("pip")
    if not pip_path:
        # Fallback to python -m pip
        pip_path = f"{sys.executable} -m pip"
    
    info = {
        "ok": len(missing) == 0,
        "missing": missing,
        "missing_packages": missing_packages,
        "python": sys.executable,
        "pip": pip_path,
    }
    
    if install and missing:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        print(f"   Using Python: {sys.executable}")
        print(f"   Using mirror: {MIRROR}\n")
        
        cmd = [sys.executable, "-m", "pip", "install", "-i", MIRROR] + missing_packages
        
        try:
            subprocess.check_call(cmd)
            # Verify installation
            still_missing = [p for p in pkgs if not has_module(p)]
            info["ok"] = len(still_missing) == 0
            info["missing"] = still_missing
            info["missing_packages"] = [get_package_name(m) for m in still_missing]
            
            if info["ok"]:
                print("\n✅ All packages installed successfully!")
            else:
                print(f"\n⚠️ Some packages still missing: {', '.join(still_missing)}")
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Installation failed with error: {e}")
            info["ok"] = False
            
    return info


def main():
    """Run preflight check with optional auto-install."""
    print("\n" + "=" * 60)
    print("  🛫 Preflight Dependency Check")
    print("=" * 60 + "\n")
    
    print(f"Python interpreter: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}\n")
    
    # Check packages
    result = ensure_packages(CRITICAL_MODULES, install=False)
    
    if result["ok"]:
        print("✅ All critical dependencies are available!\n")
        for module in CRITICAL_MODULES:
            pkg = get_package_name(module)
            print(f"   ✓ {module:<30} ({pkg})")
        print("\n" + "=" * 60)
        print("🚀 Ready to run: streamlit run app_new.py")
        print("=" * 60 + "\n")
        return 0
    else:
        print("❌ Missing dependencies detected:\n")
        for module in result["missing"]:
            pkg = get_package_name(module)
            print(f"   ✗ {module:<30} ({pkg})")
        
        print("\n" + "=" * 60)
        print("Options to fix:")
        print("=" * 60 + "\n")
        print("1. Auto-install now (recommended):")
        print(f"   {sys.executable} dev/preflight.py --install\n")
        print("2. Manual install:")
        print(f"   {sys.executable} -m pip install {' '.join(result['missing_packages'])}\n")
        print("3. Run setup script:")
        print("   .\\scripts\\ensure_venv.ps1\n")
        
        return 1


if __name__ == "__main__":
    # Support --install flag
    install_mode = "--install" in sys.argv
    
    if install_mode:
        result = ensure_packages(CRITICAL_MODULES, install=True)
        sys.exit(0 if result["ok"] else 1)
    else:
        sys.exit(main())

