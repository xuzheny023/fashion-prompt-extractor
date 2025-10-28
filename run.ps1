# AI Design Production Assistant - Startup Script
Write-Host "==> Starting AI Design Production Assistant" -ForegroundColor Green

# Check virtual environment
if (!(Test-Path ".venv\Scripts\streamlit.exe")) {
    Write-Host "ERROR: Virtual environment not found. Please run: .\scripts\ensure_venv.ps1" -ForegroundColor Red
    exit 1
}

# Quick dependency check
Write-Host "`n==> Checking dependencies..." -ForegroundColor Cyan
$depCheck = .\.venv\Scripts\python.exe -c "import streamlit, dashscope, PIL; print('OK')" 2>&1
if ($depCheck -notlike "*OK*") {
    Write-Host "WARNING: Missing dependencies" -ForegroundColor Yellow
    $response = Read-Host "Auto install? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "==> Installing dependencies..." -ForegroundColor Cyan
        .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
        Write-Host "SUCCESS: Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "Please run: .\scripts\ensure_venv.ps1" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "SUCCESS: All dependencies OK" -ForegroundColor Green
}

# Check API Key
if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "SUCCESS: API Key config found" -ForegroundColor Green
} else {
    Write-Host "WARNING: .streamlit\secrets.toml not found" -ForegroundColor Yellow
    Write-Host "         You need DASHSCOPE_API_KEY for cloud recognition" -ForegroundColor Gray
}

# Kill any existing streamlit processes
Write-Host "`n==> Killing existing streamlit processes..." -ForegroundColor Cyan
Get-Process -Name streamlit* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start application
Write-Host "==> Starting application..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:9000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

.\.venv\Scripts\streamlit.exe run app_new.py --server.port=9000
