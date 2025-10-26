Param(
  [string]$Python = "python",
  [string]$Mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
)

Write-Host "==> Ensuring .venv" -ForegroundColor Cyan
if (!(Test-Path ".venv")) {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    & $Python -m venv .venv
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

$py = ".\.venv\Scripts\python.exe"

if (!(Test-Path $py)) {
    Write-Host "ERROR: Failed to create venv or python.exe not found" -ForegroundColor Red
    exit 1
}

Write-Host "`n==> Upgrading pip" -ForegroundColor Cyan
& $py -m pip install -U pip setuptools wheel --quiet

Write-Host "`n==> Setting pip mirror to $Mirror" -ForegroundColor Cyan
& $py -m pip config set global.index-url $Mirror | Out-Null

Write-Host "`n==> Installing requirements (force-reinstall for pinned versions)" -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    Write-Host "Installing from requirements.txt with --force-reinstall..." -ForegroundColor Gray
    Write-Host "This ensures pinned versions (streamlit==1.32.2, canvas==0.9.3.post2)" -ForegroundColor Gray
    & $py -m pip install -r requirements.txt --upgrade --force-reinstall
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "requirements.txt not found, installing default packages..." -ForegroundColor Yellow
    & $py -m pip install streamlit==1.32.2 pillow numpy dashscope streamlit-drawable-canvas==0.9.3.post2 duckduckgo-search readability-lxml requests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n==> Verifying critical dependencies" -ForegroundColor Cyan
$missing = @()
$required = @("streamlit", "dashscope", "streamlit-drawable-canvas", "duckduckgo-search")
foreach ($pkg in $required) {
    $check = & $py -m pip show $pkg 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missing += $pkg
    }
}
if ($missing.Count -gt 0) {
    Write-Host "WARNING: Missing packages: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Attempting to install missing packages..." -ForegroundColor Yellow
    & $py -m pip install $missing
} else {
    Write-Host "All critical dependencies verified ✓" -ForegroundColor Green
}

Write-Host "`n==> ✅ Environment ready!" -ForegroundColor Green
Write-Host "Python: $py" -ForegroundColor Gray
& $py --version

