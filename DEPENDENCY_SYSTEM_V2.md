# 🔧 Dependency System V2 - Complete Guide

**Version**: 2.0  
**Date**: 2025-10-24  
**Status**: ✅ Production Ready

---

## 🎯 Problem Solved

**Original Issue**: App shows "依赖缺失：streamlit-drawable-canvas" even after installation.

**Root Cause**: App was not using the correct Python interpreter (repo's `.venv`).

**Solution**: Multi-layered dependency management system with:
1. Force `.venv` interpreter in workspace
2. Accurate import detection
3. One-click install into current interpreter
4. Comprehensive diagnostics

---

## 📁 New Files

### 1. `.vscode/settings.json`
**Purpose**: Force VSCode/Cursor to use repo's `.venv` interpreter

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.analysis.indexing": false,
  "python.testing.pytestEnabled": false,
  "python.linting.enabled": false
}
```

**Key Features**:
- ✅ Automatically selects `.venv` Python
- ✅ Disables heavy background tasks (faster)
- ✅ Auto-activates venv in terminal

---

### 2. `dev/preflight.py`
**Purpose**: Dependency checker with auto-install capability

**Usage**:
```powershell
# Check only
.\.venv\Scripts\python.exe dev\preflight.py

# Check + auto-install
.\.venv\Scripts\python.exe dev\preflight.py --install
```

**Features**:
- ✅ Checks all 8 critical dependencies
- ✅ Maps import names to pip package names (e.g., `PIL` → `pillow`)
- ✅ Auto-install into **current** interpreter
- ✅ Uses CN mirror for faster downloads
- ✅ Exit code 0 (success) or 1 (failure) for scripting

**Example Output**:
```
🛫 Preflight Dependency Check
============================================================
Python interpreter: D:\fashion-prompt-extractor\.venv\Scripts\python.exe
Python version: 3.10.10

✅ All critical dependencies are available!
   ✓ streamlit                      (streamlit)
   ✓ PIL                            (pillow)
   ✓ numpy                          (numpy)
   ✓ dashscope                      (dashscope)
   ✓ streamlit_drawable_canvas      (streamlit-drawable-canvas)
   ✓ duckduckgo_search              (duckduckgo-search)
   ✓ readability                    (readability-lxml)
   ✓ requests                       (requests)

🚀 Ready to run: streamlit run app_new.py
```

---

### 3. `dev/diagnose.py`
**Purpose**: Comprehensive environment diagnostics

**Usage**:
```powershell
.\.venv\Scripts\python.exe dev\diagnose.py
```

**What It Checks**:
1. **Python Interpreter Info**
   - Executable path
   - Version
   - Whether in virtualenv
   - sys.prefix

2. **Virtual Environment**
   - Workspace location
   - Expected venv path
   - Whether venv exists
   - Whether using correct venv

3. **VSCode Settings**
   - Whether `.vscode/settings.json` exists
   - Configured interpreter path

4. **Module Availability**
   - All 8 critical modules
   - Their installation locations

**Example Output**:
```
🔬 Comprehensive Environment Diagnostics
======================================================================
📍 Python Interpreter Info
  Executable: D:\fashion-prompt-extractor\.venv\Scripts\python.exe
  Version: 3.10.10
  In virtualenv: ✅ Yes

🏠 Virtual Environment Check
  Using correct venv: ✅ Yes

⚙️  VSCode Settings
  Settings file: ✅ Exists
  Interpreter path: ${workspaceFolder}/.venv/Scripts/python.exe

📦 Critical Modules
  ✅ streamlit_drawable_canvas      ...site-packages\streamlit_drawable_canvas\__init__.py
  ...

✅ All checks passed! Environment is correctly configured.
```

---

## 🔄 Updated Files

### 1. `app_new.py`
**Changes**: New interactive dependency check with auto-fix UI

**Key Features**:
- ✅ Checks `streamlit_drawable_canvas` import on startup
- ✅ Shows diagnostic info (Python path, error message)
- ✅ **Option 1**: One-click auto-install button (uses current interpreter)
- ✅ **Option 2**: Shows exact pip command to copy
- ✅ **Option 3**: Guides to setup script
- ✅ After successful install, offers "Refresh Page" button

**UI Layout**:
```
❌ 依赖缺失：streamlit-drawable-canvas

🔍 诊断信息 / Diagnostics (expandable)
  Python: D:\fashion-prompt-extractor\.venv\Scripts\python.exe
  Error: No module named 'streamlit_drawable_canvas'

🛠️ 修复选项 / Fix Options

[选项 1: 一键自动修复]  [选项 2: 手动命令行安装]
[🚀 自动安装依赖]       python -m pip install streamlit-drawable-canvas

[选项 3: 使用配置脚本]
.\scripts\ensure_venv.ps1

💡 VSCode/Cursor 用户: Ctrl+Shift+P → Tasks → 01: Ensure venv & deps
```

---

### 2. `run.ps1`
**Changes**: Integrated preflight check with interactive auto-install

**Before**:
```powershell
# Old: Used test_imports.py
.\.venv\Scripts\python.exe test_imports.py
```

**After**:
```powershell
# New: Uses dev\preflight.py with interactive prompt
.\.venv\Scripts\python.exe dev\preflight.py
if ($LASTEXITCODE -ne 0) {
    $response = Read-Host "是否自动安装？(y/n)"
    if ($response -eq "y") {
        .\.venv\Scripts\python.exe dev\preflight.py --install
    }
}
```

**Benefits**:
- ✅ Detects missing deps before app starts
- ✅ Offers to auto-fix immediately
- ✅ Uses correct interpreter

---

## 🚀 Usage Workflows

### Workflow 1: Normal Startup (All Deps OK)
```
User: .\run.ps1
↓
System: Checks deps with preflight.py
↓
All OK → Starts Streamlit immediately
```

### Workflow 2: Missing Dependencies (CLI)
```
User: .\run.ps1
↓
System: Detects missing streamlit-drawable-canvas
↓
Prompt: "是否自动安装？(y/n)"
↓
User: y
↓
System: Installs into .venv
↓
Success → Starts Streamlit
```

### Workflow 3: Missing Dependencies (GUI)
```
User: Directly runs streamlit
↓
App: Detects missing dep
↓
UI: Shows auto-fix options
↓
User: Clicks "🚀 自动安装依赖"
↓
System: Installs into current interpreter
↓
UI: Shows "✅ 安装成功！请刷新页面"
↓
User: Clicks "🔄 刷新页面" or presses F5
↓
App: Loads successfully
```

### Workflow 4: Debugging Issues
```
User: .\.venv\Scripts\python.exe dev\diagnose.py
↓
System: Shows comprehensive diagnostics
↓
User: Identifies issue (e.g., wrong Python interpreter)
↓
Fix: Restart VSCode or select correct interpreter
```

---

## 🔍 Troubleshooting Guide

### Issue: App still shows "依赖缺失" after install

**Diagnosis**:
```powershell
.\.venv\Scripts\python.exe dev\diagnose.py
```

**Common Causes**:
1. ❌ Using system Python instead of `.venv`
2. ❌ Installed to wrong interpreter
3. ❌ VSCode cached wrong interpreter

**Fixes**:

#### Fix 1: Restart VSCode/Cursor
```
1. Close all terminals in VSCode
2. Close VSCode
3. Reopen VSCode
4. Terminal → New Terminal
5. Run: .\run.ps1
```

#### Fix 2: Manually Select Interpreter
```
1. Press Ctrl+Shift+P
2. Type: "Python: Select Interpreter"
3. Choose: .venv\Scripts\python.exe
4. Restart terminal
```

#### Fix 3: Force Reinstall
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Reinstall all deps
pip install -r requirements.txt --force-reinstall
```

#### Fix 4: Nuclear Option (Full Reset)
```powershell
# Delete venv
Remove-Item -Recurse -Force .venv

# Recreate
.\scripts\ensure_venv.ps1

# Restart VSCode
```

---

## 📊 Comparison: V1 vs V2

| Feature | V1 (Old) | V2 (New) |
|---------|----------|----------|
| Interpreter detection | ❌ None | ✅ Automatic |
| VSCode integration | ⚠️ Manual | ✅ Auto-configured |
| Error diagnosis | ⚠️ Generic message | ✅ Detailed diagnostics |
| Auto-fix | ❌ No | ✅ One-click in GUI & CLI |
| Verification | ⚠️ Basic | ✅ Comprehensive |
| User guidance | ⚠️ Commands only | ✅ Interactive UI |
| Install target | ⚠️ Unclear | ✅ Current interpreter |
| Debugging | ❌ Manual | ✅ `dev/diagnose.py` |

---

## 🎯 Acceptance Criteria - ALL MET

### ✅ 1. Force .venv interpreter
- `.vscode/settings.json` created
- `python.defaultInterpreterPath` points to `.venv`
- Auto-activates in terminal

### ✅ 2. Accurate import detection
- `dev/preflight.py` uses `importlib.util.find_spec()`
- Maps import names to pip packages (e.g., `PIL` → `pillow`)
- Shows module installation locations

### ✅ 3. One-click install
- GUI: "🚀 自动安装依赖" button in app
- CLI: `dev\preflight.py --install`
- Interactive: `run.ps1` with y/n prompt
- All install into **current** interpreter (`sys.executable`)

### ✅ 4. Show diagnostics
- `dev/diagnose.py` shows:
  - Python interpreter path
  - Virtualenv status
  - VSCode settings
  - Module locations
  - Clear recommendations

---

## 🧪 Testing

### Test 1: Verify .venv Usage
```powershell
# Should use .venv Python
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
# Output: D:\fashion-prompt-extractor\.venv\Scripts\python.exe
```

### Test 2: Preflight Check
```powershell
.\.venv\Scripts\python.exe dev\preflight.py
# Output: ✅ All dependencies available
```

### Test 3: Preflight Install
```powershell
# Simulate missing dep (uninstall first)
.\.venv\Scripts\python.exe -m pip uninstall streamlit-drawable-canvas -y

# Run preflight with install
.\.venv\Scripts\python.exe dev\preflight.py --install
# Output: 🔧 Installing... ✅ Success
```

### Test 4: Diagnostics
```powershell
.\.venv\Scripts\python.exe dev\diagnose.py
# Output: ✅ All checks passed
```

### Test 5: Full Workflow
```powershell
.\run.ps1
# Should: Check deps → Start app (or prompt to install)
```

---

## 📝 Documentation Files

1. **DEPENDENCY_SYSTEM_V2.md** (this file) - Complete guide
2. **START_HERE.md** - Updated with new tools
3. **DEPENDENCY_FIX_COMPLETE.md** - V1 fix report
4. **ACCEPTANCE_TEST_REPORT.md** - V1 acceptance tests

---

## 🎉 Benefits

### For Users
- ✅ Clear, actionable error messages
- ✅ One-click fixes (no terminal needed)
- ✅ Automatic environment detection
- ✅ Works in VSCode/Cursor/terminal

### For Developers
- ✅ Easier debugging with `diagnose.py`
- ✅ Consistent environment across team
- ✅ Automated testing with exit codes
- ✅ Extensible (easy to add new deps)

### For Deployment
- ✅ Reliable CI/CD (exit codes)
- ✅ Self-healing (auto-install)
- ✅ Clear logs (detailed output)
- ✅ Fast (CN mirror support)

---

## 🚀 Ready to Use

The dependency system is now **bulletproof**:

1. **Prevention**: `.vscode/settings.json` ensures correct interpreter
2. **Detection**: `preflight.py` catches issues early
3. **Diagnosis**: `diagnose.py` identifies root causes
4. **Remediation**: One-click fixes in GUI and CLI
5. **Verification**: Comprehensive checks at every step

**No more "ModuleNotFoundError" mysteries!** 🎊

---

**Status**: ✅ **PRODUCTION READY V2**

