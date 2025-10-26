# Build Frontend Components Script
# Usage: .\scripts\build_frontend.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Building Frontend Components" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Node.js is installed
Write-Host "1. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✓ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Node.js 18+ from: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

# Step 2: Build web_cropper component
Write-Host "2. Building web_cropper component..." -ForegroundColor Yellow

$webCropperDir = Join-Path $PSScriptRoot "..\ui\web_cropper"

if (-not (Test-Path $webCropperDir)) {
    Write-Host "   ✗ web_cropper directory not found at: $webCropperDir" -ForegroundColor Red
    exit 1
}

Push-Location $webCropperDir

try {
    # Check if build script exists
    $buildScript = Join-Path $webCropperDir "build.ps1"
    if (Test-Path $buildScript) {
        Write-Host "   Running: .\build.ps1" -ForegroundColor Gray
        & $buildScript
        if ($LASTEXITCODE -ne 0) {
            throw "Build script failed"
        }
    } else {
        # Fallback: manual build
        Write-Host "   Build script not found, building manually..." -ForegroundColor Gray
        
        $frontendDir = Join-Path $webCropperDir "frontend"
        Push-Location $frontendDir
        
        try {
            # Install dependencies
            if (-not (Test-Path "node_modules")) {
                Write-Host "   Installing npm dependencies..." -ForegroundColor Gray
                npm install
                if ($LASTEXITCODE -ne 0) {
                    throw "npm install failed"
                }
            }
            
            # Build
            Write-Host "   Building component..." -ForegroundColor Gray
            npm run build
            if ($LASTEXITCODE -ne 0) {
                throw "npm run build failed"
            }
            
            Write-Host "   ✓ web_cropper built successfully" -ForegroundColor Green
        } finally {
            Pop-Location
        }
    }
} catch {
    Write-Host "   ✗ Failed to build web_cropper: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  ✓ All frontend components built successfully!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\run.ps1" -ForegroundColor White
Write-Host "  2. Upload an image and test the cropper" -ForegroundColor White
Write-Host ""
Write-Host "Note: You only need to run this script once, or when updating components." -ForegroundColor Yellow
Write-Host ""

