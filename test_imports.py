#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick import test for all critical dependencies.
Run this before starting the app to ensure environment is ready.
"""

import sys

def test_imports():
    """Test all critical imports."""
    print("\n" + "="*50)
    print("  🧪 Testing Critical Imports")
    print("="*50 + "\n")
    
    tests = [
        ("streamlit", "Streamlit web framework"),
        ("PIL", "Pillow image processing"),
        ("numpy", "NumPy numerical computing"),
        ("dashscope", "DashScope Qwen-VL API"),
        ("streamlit_drawable_canvas", "Interactive canvas component"),
        ("duckduckgo_search", "DuckDuckGo search"),
        ("readability", "HTML readability parser"),
        ("requests", "HTTP requests library"),
    ]
    
    failed = []
    
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<30} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:<30} - FAILED: {e}")
            failed.append(module_name)
    
    print("\n" + "="*50)
    
    if failed:
        print(f"❌ {len(failed)} import(s) failed:")
        for module in failed:
            print(f"   • {module}")
        print("\nPlease run:")
        print("  .\\scripts\\ensure_venv.ps1")
        print("or:")
        print("  pip install -r requirements.txt")
        print("="*50 + "\n")
        return False
    else:
        print("✅ All imports successful!")
        print("="*50 + "\n")
        print("🚀 Ready to run: streamlit run app_new.py")
        print()
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

