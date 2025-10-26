# Test DEV mode setup
# Usage: .\test_dev_setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Testing DEV Mode Setup" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"
$passed = 0
$failed = 0

# Test 1: Check Node.js
Write-Host "1. Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "   ✅ Node.js version: $nodeVersion" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "   ❌ Node.js not found" -ForegroundColor Red
    Write-Host "      Install from: https://nodejs.org/" -ForegroundColor Gray
    $failed++
}

Write-Host ""

# Test 2: Check npm
Write-Host "2. Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version
    Write-Host "   ✅ npm version: $npmVersion" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "   ❌ npm not found" -ForegroundColor Red
    $failed++
}

Write-Host ""

# Test 3: Check frontend directory
Write-Host "3. Checking frontend directory..." -ForegroundColor Yellow
if (Test-Path $frontendDir) {
    Write-Host "   ✅ Frontend directory exists" -ForegroundColor Green
    $passed++
} else {
    Write-Host "   ❌ Frontend directory not found" -ForegroundColor Red
    $failed++
}

Write-Host ""

# Test 4: Check package.json
Write-Host "4. Checking package.json..." -ForegroundColor Yellow
$packageJson = Join-Path $frontendDir "package.json"
if (Test-Path $packageJson) {
    Write-Host "   ✅ package.json exists" -ForegroundColor Green
    $passed++
    
    # Check dependencies
    $content = Get-Content $packageJson -Raw | ConvertFrom-Json
    $deps = @("react", "react-dom", "react-easy-crop")
    foreach ($dep in $deps) {
        if ($content.dependencies.$dep) {
            Write-Host "      ✅ $dep" -ForegroundColor Green
        } else {
            Write-Host "      ❌ $dep missing" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   ❌ package.json not found" -ForegroundColor Red
    $failed++
}

Write-Host ""

# Test 5: Check source files
Write-Host "5. Checking source files..." -ForegroundColor Yellow
$srcDir = Join-Path $frontendDir "src"
$requiredFiles = @("main.tsx", "App.tsx", "style.css")
$allExist = $true

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $srcDir $file
    if (Test-Path $filePath) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing" -ForegroundColor Red
        $allExist = $false
    }
}

if ($allExist) {
    $passed++
} else {
    $failed++
}

Write-Host ""

# Test 6: Check vite.config.ts
Write-Host "6. Checking vite.config.ts..." -ForegroundColor Yellow
$viteConfig = Join-Path $frontendDir "vite.config.ts"
if (Test-Path $viteConfig) {
    Write-Host "   ✅ vite.config.ts exists" -ForegroundColor Green
    
    # Check port configuration
    $content = Get-Content $viteConfig -Raw
    if ($content -match "port:\s*5173") {
        Write-Host "      ✅ Port 5173 configured" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  Port 5173 not found in config" -ForegroundColor Yellow
    }
    
    $passed++
} else {
    Write-Host "   ❌ vite.config.ts not found" -ForegroundColor Red
    $failed++
}

Write-Host ""

# Test 7: Check Python __init__.py
Write-Host "7. Checking Python __init__.py..." -ForegroundColor Yellow
$initPy = Join-Path $PSScriptRoot "__init__.py"
if (Test-Path $initPy) {
    Write-Host "   ✅ __init__.py exists" -ForegroundColor Green
    
    # Check for DEV_URL
    $content = Get-Content $initPy -Raw
    if ($content -match "WEB_CROPPER_DEV") {
        Write-Host "      ✅ WEB_CROPPER_DEV environment variable check found" -ForegroundColor Green
    } else {
        Write-Host "      ❌ WEB_CROPPER_DEV check missing" -ForegroundColor Red
    }
    
    $passed++
} else {
    Write-Host "   ❌ __init__.py not found" -ForegroundColor Red
    $failed++
}

Write-Host ""

# Test 8: Check if dependencies are installed
Write-Host "8. Checking if dependencies are installed..." -ForegroundColor Yellow
$nodeModules = Join-Path $frontendDir "node_modules"
if (Test-Path $nodeModules) {
    Write-Host "   ✅ node_modules exists" -ForegroundColor Green
    $passed++
} else {
    Write-Host "   ⚠️  node_modules not found" -ForegroundColor Yellow
    Write-Host "      Run: cd frontend && npm install" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Test Results" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "✅ All tests passed! Ready for DEV mode." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: .\start_dev.ps1" -ForegroundColor White
    Write-Host "  2. In another terminal:" -ForegroundColor White
    Write-Host "     `$env:WEB_CROPPER_DEV = `"http://localhost:5173`"" -ForegroundColor Gray
    Write-Host "     streamlit run app_new.py" -ForegroundColor Gray
} else {
    Write-Host "❌ Some tests failed. Please fix the issues above." -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

