# 构建生产版本
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Web Cropper Frontend Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "未找到 node_modules，先安装依赖..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: npm install 失败" -ForegroundColor Red
        exit 1
    }
}

# 构建
Write-Host "开始构建..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 构建失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  构建成功!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "输出目录: ui/web_cropper/frontend/dist/" -ForegroundColor Cyan
Write-Host ""
Write-Host "现在可以直接运行 Streamlit (生产模式):" -ForegroundColor Yellow
Write-Host "  streamlit run app_new.py" -ForegroundColor Gray
Write-Host ""


