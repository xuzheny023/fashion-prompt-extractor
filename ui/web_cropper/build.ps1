# Build script for web_cropper component
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Building web_cropper Streamlit Component" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"

# Step 1: Check if Node.js is installed
Write-Host "1. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies
Write-Host ""
Write-Host "2. Installing npm dependencies..." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "   Running: npm install" -ForegroundColor Gray
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed"
        }
        Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "   ✓ Dependencies already installed (node_modules exists)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Failed to install dependencies: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Step 3: Build the component
Write-Host ""
Write-Host "3. Building component..." -ForegroundColor Yellow
try {
    Write-Host "   Running: npm run build" -ForegroundColor Gray
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build failed"
    }
    Write-Host "   ✓ Build completed" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Build failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Step 4: Verify build output
Write-Host ""
Write-Host "4. Verifying build output..." -ForegroundColor Yellow
$buildDir = Join-Path $frontendDir "build"
$bundleJs = Join-Path $buildDir "bundle.js"
$bundleCss = Join-Path $buildDir "bundle.css"

if (Test-Path $bundleJs) {
    $jsSize = (Get-Item $bundleJs).Length / 1KB
    Write-Host "   ✓ bundle.js: $([math]::Round($jsSize, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "   ✗ bundle.js not found" -ForegroundColor Red
    exit 1
}

if (Test-Path $bundleCss) {
    $cssSize = (Get-Item $bundleCss).Length / 1KB
    Write-Host "   ✓ bundle.css: $([math]::Round($cssSize, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "   ⚠ bundle.css not found (optional)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  ✓ Build completed successfully!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Import in Python: from ui.web_cropper import web_cropper" -ForegroundColor White
Write-Host "  2. Use in Streamlit: crop = web_cropper(image_url='...', key='cropper')" -ForegroundColor White
Write-Host ""

