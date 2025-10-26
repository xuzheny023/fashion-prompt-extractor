#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick verification script for web_cropper auto-build setup.
"""
import sys
from pathlib import Path

def check_file(path: Path, description: str) -> bool:
    """Check if a file exists."""
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("\n" + "="*80)
    print("  Web Cropper Setup Verification")
    print("="*80 + "\n")
    
    root = Path(__file__).parent
    frontend = root / "frontend"
    
    all_good = True
    
    # Check Python files
    print("📦 Python Files:")
    all_good &= check_file(root / "__init__.py", "Component loader")
    print()
    
    # Check frontend structure
    print("📁 Frontend Structure:")
    all_good &= check_file(frontend, "Frontend directory")
    all_good &= check_file(frontend / "package.json", "Package config")
    all_good &= check_file(frontend / "vite.config.ts", "Vite config")
    all_good &= check_file(frontend / "tsconfig.json", "TypeScript config")
    all_good &= check_file(frontend / "index.html", "HTML entry")
    print()
    
    # Check source files
    print("📝 Source Files:")
    src = frontend / "src"
    all_good &= check_file(src / "main.tsx", "React entry")
    all_good &= check_file(src / "App.tsx", "App component")
    all_good &= check_file(src / "style.css", "Styles")
    print()
    
    # Check build output (optional)
    print("🏗️  Build Output (optional):")
    dist = frontend / "dist"
    build = frontend / "build"
    
    has_dist = check_file(dist / "index.html", "Dist build")
    has_build = check_file(build / "index.html", "Build output")
    
    if not has_dist and not has_build:
        print("   ℹ️  No build output found (will auto-build on first run)")
    print()
    
    # Check Node.js
    print("🔧 Dependencies:")
    import subprocess
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            timeout=5,
            shell=sys.platform == "win32",
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()
            print(f"✅ Node.js: {version}")
        else:
            print("❌ Node.js: not working")
            all_good = False
    except Exception as e:
        print(f"❌ Node.js: not found ({e})")
        all_good = False
    
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            timeout=5,
            shell=sys.platform == "win32",
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()
            print(f"✅ npm: {version}")
        else:
            print("❌ npm: not working")
            all_good = False
    except Exception as e:
        print(f"❌ npm: not found ({e})")
        all_good = False
    print()
    
    # Summary
    print("="*80)
    if all_good:
        print("✅ All checks passed!")
        print("\nNext steps:")
        print("  1. Run: streamlit run app_new.py")
        print("  2. Or dev mode:")
        print("     Terminal 1: cd ui/web_cropper/frontend && npm run dev")
        print("     Terminal 2: $env:WEB_CROPPER_DEV_URL='http://localhost:5173'; streamlit run app_new.py")
    else:
        print("❌ Some checks failed!")
        print("\nPlease fix the issues above before running.")
        print("\nCommon fixes:")
        print("  - Install Node.js: https://nodejs.org/")
        print("  - Check file paths are correct")
        print("  - Run: cd ui/web_cropper/frontend && npm install")
    print("="*80 + "\n")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())


