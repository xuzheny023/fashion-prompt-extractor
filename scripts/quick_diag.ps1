Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "   Quick Diagnostics" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$py = ".\.venv\Scripts\python.exe"

# Check Python
Write-Host "[Python]" -ForegroundColor Yellow
if (Test-Path $py) {
    & $py --version
    Write-Host "Location: $py" -ForegroundColor Gray
} else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run task '01: Ensure venv & deps (CN mirror)' first" -ForegroundColor Yellow
    exit 1
}

# Check packages
Write-Host "`n[Installed Packages]" -ForegroundColor Yellow
$packages = & $py -m pip list | Select-String "streamlit|dashscope|streamlit-drawable-canvas|pillow|numpy|duckduckgo"
if ($packages) {
    $packages | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "  ⚠️ Core packages not found" -ForegroundColor Yellow
}

# Check secrets
Write-Host "`n[Secrets]" -ForegroundColor Yellow
if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "  ✅ Found .streamlit\secrets.toml" -ForegroundColor Green
    $content = Get-Content ".streamlit\secrets.toml" -Raw
    if ($content -match "DASHSCOPE_API_KEY") {
        Write-Host "  ✅ DASHSCOPE_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ DASHSCOPE_API_KEY not found in secrets.toml" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️ Missing .streamlit\secrets.toml" -ForegroundColor Yellow
}

# Check config
Write-Host "`n[Streamlit Config]" -ForegroundColor Yellow
if (Test-Path ".streamlit\config.toml") {
    Write-Host "  ✅ Found .streamlit\config.toml" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Missing .streamlit\config.toml (optional)" -ForegroundColor Yellow
}

# Network check
Write-Host "`n[Network]" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://pypi.org/simple/streamlit/" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Internet connection OK" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️ Internet check failed (timeout or blocked)" -ForegroundColor Yellow
}

# File structure
Write-Host "`n[Project Files]" -ForegroundColor Yellow
$files = @("app_new.py", "src/fabric_api_infer.py", "requirements.txt")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file missing" -ForegroundColor Red
    }
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "   Diagnostics Complete" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

