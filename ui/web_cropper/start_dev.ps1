# Quick start script for DEV mode
# Usage: .\start_dev.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Web Cropper - DEV Mode Quick Start" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"

# Check if node_modules exists
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ npm install failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🚀 Starting DEV mode..." -ForegroundColor Yellow
Write-Host ""
Write-Host "This will start the Vite dev server on port 5173" -ForegroundColor Gray
Write-Host ""
Write-Host "To use with Streamlit, open another terminal and run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  PowerShell:" -ForegroundColor White
Write-Host "    `$env:WEB_CROPPER_DEV = `"http://localhost:5173`"" -ForegroundColor Gray
Write-Host "    streamlit run app_new.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  Bash:" -ForegroundColor White
Write-Host "    export WEB_CROPPER_DEV=`"http://localhost:5173`"" -ForegroundColor Gray
Write-Host "    streamlit run app_new.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Push-Location $frontendDir
npm run dev
Pop-Location

