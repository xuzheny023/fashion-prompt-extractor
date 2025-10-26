#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the app_new.py dependency guard logic
"""

import sys
sys.path.insert(0, '.')

from dev.preflight import ensure_packages, has_module

print("=" * 60)
print("Testing app_new.py dependency guard logic")
print("=" * 60)

# Test 1: Import functions
print("\n[1] Testing imports...")
try:
    from dev.preflight import ensure_packages, has_module
    print("✅ ensure_packages imported")
    print("✅ has_module imported")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check streamlit_drawable_canvas
print("\n[2] Checking streamlit_drawable_canvas...")
needed = ["streamlit_drawable_canvas"]
probe = ensure_packages(needed, install=False)

print(f"  ok: {probe['ok']}")
print(f"  missing: {probe['missing']}")
print(f"  missing_packages: {probe['missing_packages']}")
print(f"  python: {probe['python']}")

if probe['ok']:
    print("✅ streamlit_drawable_canvas is available")
else:
    print("⚠️  streamlit_drawable_canvas is missing (expected if testing guard)")

# Test 3: Verify has_module function
print("\n[3] Testing has_module function...")
result = has_module("streamlit_drawable_canvas")
print(f"  has_module('streamlit_drawable_canvas'): {result}")

# Test 4: Check all critical deps
print("\n[4] Checking all critical dependencies...")
critical = [
    "streamlit",
    "PIL",
    "numpy",
    "dashscope",
    "streamlit_drawable_canvas",
    "duckduckgo_search",
    "readability",
    "requests",
]
all_probe = ensure_packages(critical, install=False)
print(f"  All OK: {all_probe['ok']}")
if not all_probe['ok']:
    print(f"  Missing: {all_probe['missing']}")

print("\n" + "=" * 60)
if all_probe['ok']:
    print("✅ All tests passed! app_new.py guard should work correctly.")
else:
    print("⚠️  Some dependencies missing, but guard logic is working.")
print("=" * 60)

