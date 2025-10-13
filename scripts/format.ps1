# -*- coding: utf-8 -*-
# PowerShell script for code formatting and linting
# Usage: .\scripts\format.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "代码格式化与 Lint 检查" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

# 检查虚拟环境
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "`n❌ 虚拟环境不存在，请先创建虚拟环境" -ForegroundColor Red
    exit 1
}

# 检查并安装依赖
Write-Host "`n[1/4] 检查依赖..." -ForegroundColor Yellow

$blackInstalled = & .\venv\Scripts\python.exe -m pip show black 2>$null
$ruffInstalled = & .\venv\Scripts\python.exe -m pip show ruff 2>$null

if (-not $blackInstalled) {
    Write-Host "  → 安装 black..." -ForegroundColor Gray
    & .\venv\Scripts\python.exe -m pip install black --quiet
}

if (-not $ruffInstalled) {
    Write-Host "  → 安装 ruff..." -ForegroundColor Gray
    & .\venv\Scripts\python.exe -m pip install ruff --quiet
}

Write-Host "  ✓ 依赖已就绪" -ForegroundColor Green

# 运行 Black 格式化
Write-Host "`n[2/4] 运行 Black 格式化..." -ForegroundColor Yellow
Write-Host "  → 格式化 Python 文件..." -ForegroundColor Gray

& .\venv\Scripts\python.exe -m black . --exclude "/(\.git|\.hg|\.mypy_cache|\.tox|\.venv|venv|_build|buck-out|build|dist)/" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Black 格式化完成" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Black 格式化有警告" -ForegroundColor Yellow
}

# 运行 Ruff 检查和修复
Write-Host "`n[3/4] 运行 Ruff Lint 检查..." -ForegroundColor Yellow
Write-Host "  → 检查并自动修复..." -ForegroundColor Gray

$ruffOutput = & .\venv\Scripts\python.exe -m ruff check . --fix 2>&1
$ruffExitCode = $LASTEXITCODE

if ($ruffExitCode -eq 0) {
    Write-Host "  ✓ Ruff 检查通过，无问题" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Ruff 发现问题（已自动修复部分）" -ForegroundColor Yellow
    if ($ruffOutput) {
        Write-Host "`n  详细信息:" -ForegroundColor Gray
        $ruffOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }
}

# 统计信息
Write-Host "`n[4/4] 统计信息..." -ForegroundColor Yellow

$pyFiles = Get-ChildItem -Path . -Filter "*.py" -Recurse -File | Where-Object {
    $_.FullName -notmatch "\\(venv|\.venv|__pycache__|\.git|build|dist)\\"
}

$totalLines = 0
foreach ($file in $pyFiles) {
    $totalLines += (Get-Content $file.FullName | Measure-Object -Line).Lines
}

Write-Host "  Python 文件数: $($pyFiles.Count)" -ForegroundColor Cyan
Write-Host "  总代码行数: $totalLines" -ForegroundColor Cyan

# 完成
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "✅ 格式化与 Lint 检查完成！" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan

Write-Host "`n💡 提示:" -ForegroundColor Yellow
Write-Host "  • Black: 代码格式化（行宽 100）" -ForegroundColor Gray
Write-Host "  • Ruff: 快速 Lint 检查（忽略 E501）" -ForegroundColor Gray
Write-Host "  • 配置文件: pyproject.toml" -ForegroundColor Gray
Write-Host "  • 编辑器配置: .editorconfig" -ForegroundColor Gray

Write-Host "`n📝 下一步:" -ForegroundColor Yellow
Write-Host "  git add ." -ForegroundColor Cyan
Write-Host "  git commit -m `"chore: format & lint (black/ruff) + config`"" -ForegroundColor Cyan

exit 0

