# Development script for web_cropper component
# Usage: .\dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  web_cropper Development Mode" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"

# Step 1: Check Node.js
Write-Host "1. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js not found" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies if needed
Write-Host ""
Write-Host "2. Checking dependencies..." -ForegroundColor Yellow
Push-Location $frontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing dependencies..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        exit 1
    }
}
Write-Host "   ✓ Dependencies ready" -ForegroundColor Green

# Step 3: Start dev server
Write-Host ""
Write-Host "3. Starting development server..." -ForegroundColor Yellow
Write-Host "   Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "   To use dev mode in Streamlit, set environment variable:" -ForegroundColor Yellow
Write-Host "   `$env:WEB_CROPPER_DEV = `"http://localhost:5173`"" -ForegroundColor Gray
Write-Host ""
Write-Host "   Then run your Streamlit app in another terminal:" -ForegroundColor Yellow
Write-Host "   streamlit run app_new.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

npm run dev

Pop-Location
