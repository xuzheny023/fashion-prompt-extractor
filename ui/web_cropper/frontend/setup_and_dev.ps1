# 快速设置并启动前端开发服务器
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Web Cropper Frontend Setup & Dev" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Node.js
Write-Host "检查 Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Node.js" -ForegroundColor Red
    Write-Host "请先安装 Node.js: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Node.js 版本: $nodeVersion" -ForegroundColor Green

# 检查 npm
Write-Host "检查 npm..." -ForegroundColor Yellow
$npmVersion = npm --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 npm" -ForegroundColor Red
    exit 1
}
Write-Host "  npm 版本: $npmVersion" -ForegroundColor Green
Write-Host ""

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: npm install 失败" -ForegroundColor Red
    exit 1
}
Write-Host "  依赖安装完成" -ForegroundColor Green
Write-Host ""

# 启动开发服务器
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动开发服务器 (端口 5173)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 在另一个终端运行 Streamlit:" -ForegroundColor Yellow
Write-Host '  $env:WEB_CROPPER_DEV_URL = "http://localhost:5173"' -ForegroundColor Gray
Write-Host "  streamlit run app_new.py" -ForegroundColor Gray
Write-Host ""

npm run dev


