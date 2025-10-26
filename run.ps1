# 一键启动脚本
Write-Host "==> 启动 AI 面料识别应用" -ForegroundColor Green

# 检查虚拟环境
if (!(Test-Path ".venv\Scripts\streamlit.exe")) {
    Write-Host "❌ 虚拟环境未正确配置，请先运行 scripts\ensure_venv.ps1" -ForegroundColor Red
    exit 1
}

# 快速依赖检查（使用新的预检查系统）
Write-Host "`n==> 检查依赖..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe dev\preflight.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️ 发现缺失依赖" -ForegroundColor Yellow
    $response = Read-Host "是否自动安装？(y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "`n==> 正在安装依赖..." -ForegroundColor Cyan
        .\.venv\Scripts\python.exe dev\preflight.py --install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "`n❌ 自动安装失败，请运行 scripts\ensure_venv.ps1" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "`n请运行以下命令之一修复依赖：" -ForegroundColor Yellow
        Write-Host "  1. .\.venv\Scripts\python.exe dev\preflight.py --install" -ForegroundColor Gray
        Write-Host "  2. .\scripts\ensure_venv.ps1" -ForegroundColor Gray
        exit 1
    }
}

# 检查 API Key
if (Test-Path ".streamlit\secrets.toml") {
    Write-Host "✅ 检测到 secrets 配置文件" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未检测到 .streamlit\secrets.toml" -ForegroundColor Yellow
    Write-Host "如果需要使用云端识别，请配置 DASHSCOPE_API_KEY" -ForegroundColor Yellow
}

Write-Host "`n==> 启动 Streamlit 应用..." -ForegroundColor Cyan
Write-Host "应用地址: http://localhost:8501" -ForegroundColor Gray
Write-Host "按 Ctrl+C 停止服务`n" -ForegroundColor Gray

.\.venv\Scripts\streamlit.exe run app_new.py

