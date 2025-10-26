# Deployment Verification Script
# Quick check for all acceptance criteria

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          🔍 Deployment Verification - V2.1                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$allPassed = $true

# D) requirements.txt
Write-Host "[D] requirements.txt 验证" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path requirements.txt) {
    $deps = Get-Content requirements.txt | Where-Object { $_ -ne "" }
    Write-Host "  ✓ requirements.txt 存在" -ForegroundColor Green
    Write-Host "  ✓ 依赖数量: $($deps.Count) (期望: 8)" -ForegroundColor $(if ($deps.Count -eq 8) {'Green'} else {'Red'})
    
    $required = @("streamlit", "pillow", "numpy", "dashscope", "streamlit-drawable-canvas", "duckduckgo-search", "readability-lxml", "requests")
    foreach ($pkg in $required) {
        $found = $deps -contains $pkg
        if ($found) {
            Write-Host "  ✓ $pkg" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $pkg (缺失)" -ForegroundColor Red
            $allPassed = $false
        }
    }
    
    if ($deps -contains "streamlit-cropper") {
        Write-Host "  ✗ streamlit-cropper 应该被移除" -ForegroundColor Red
        $allPassed = $false
    } else {
        Write-Host "  ✓ streamlit-cropper 已移除" -ForegroundColor Green
    }
} else {
    Write-Host "  ✗ requirements.txt 不存在" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# E1) app_new.py precise guard
Write-Host "[E1] app_new.py 精确保护" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path app_new.py) {
    $content = Get-Content app_new.py -Raw
    
    if ($content -match "from dev.preflight import ensure_packages") {
        Write-Host "  ✓ 导入 ensure_packages" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 缺少 ensure_packages 导入" -ForegroundColor Red
        $allPassed = $false
    }
    
    if ($content -match "probe = ensure_packages") {
        Write-Host "  ✓ 使用 probe = ensure_packages()" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 缺少 probe 调用" -ForegroundColor Red
        $allPassed = $false
    }
    
    if ($content -match 'if not probe\["ok"\]') {
        Write-Host "  ✓ 检查 probe['ok']" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 缺少 probe['ok'] 检查" -ForegroundColor Red
        $allPassed = $false
    }
    
    if ($content -match "st.rerun") {
        Write-Host "  ✓ 自动重载 st.rerun()" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 缺少 st.rerun()" -ForegroundColor Red
        $allPassed = $false
    }
    
    # Syntax check
    .\.venv\Scripts\python.exe -m py_compile app_new.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 语法检查通过" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 语法错误" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "  ✗ app_new.py 不存在" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# E2) dev/preflight.py
Write-Host "[E2] dev/preflight.py 存在" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path dev\preflight.py) {
    Write-Host "  ✓ dev/preflight.py 存在" -ForegroundColor Green
    
    $content = Get-Content dev\preflight.py -Raw
    if ($content -match "importlib.util.find_spec") {
        Write-Host "  ✓ 使用 importlib.util.find_spec()" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 未使用 find_spec()" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "  ✗ dev/preflight.py 不存在" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# E3) VSCode settings
Write-Host "[E3] VSCode 配置" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path .vscode\settings.json) {
    Write-Host "  ✓ .vscode/settings.json 存在" -ForegroundColor Green
    
    try {
        $settings = Get-Content .vscode\settings.json -Raw | ConvertFrom-Json
        $interpreterPath = $settings."python.defaultInterpreterPath"
        
        if ($interpreterPath -like "*/.venv/Scripts/python.exe" -or $interpreterPath -like "*.venv\Scripts\python.exe" -or $interpreterPath -like "*`${workspaceFolder}*") {
            Write-Host "  ✓ 解释器路径指向 .venv" -ForegroundColor Green
        } else {
            Write-Host "  ✗ 解释器路径不正确: $interpreterPath" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host "  ✗ 无法解析 settings.json" -ForegroundColor Red
        $allPassed = $false
    }
} else {
    Write-Host "  ✗ .vscode/settings.json 不存在" -ForegroundColor Red
    $allPassed = $false
}

Write-Host ""

# E4) .venv check
Write-Host "[E4] .venv 环境验证" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (Test-Path .venv\Scripts\python.exe) {
    Write-Host "  ✓ .venv\Scripts\python.exe 存在" -ForegroundColor Green
    
    $version = & .\.venv\Scripts\python.exe --version 2>&1
    Write-Host "  ✓ Python 版本: $version" -ForegroundColor Green
    
    # Check streamlit-drawable-canvas
    $pkg = & .\.venv\Scripts\python.exe -m pip show streamlit-drawable-canvas 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ streamlit-drawable-canvas 已安装" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  streamlit-drawable-canvas 未安装 (首次运行时会自动安装)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ .venv 不存在" -ForegroundColor Red
    Write-Host "  提示: 运行 .\scripts\ensure_venv.ps1 创建" -ForegroundColor Yellow
    $allPassed = $false
}

Write-Host ""

# Summary
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "║              ✅ 所有验证通过！可以部署！                     ║" -ForegroundColor Green
} else {
    Write-Host "║              ⚠️  部分验证失败，请检查上方详情                ║" -ForegroundColor Yellow
}
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "🚀 下一步：运行 " -NoNewline -ForegroundColor White
    Write-Host ".\run.ps1" -ForegroundColor Cyan -NoNewline
    Write-Host " 启动应用`n" -ForegroundColor White
    exit 0
} else {
    Write-Host "🔧 请修复上述问题后重新验证`n" -ForegroundColor Yellow
    exit 1
}



