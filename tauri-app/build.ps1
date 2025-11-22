# GameTools Tauri 构建脚本
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GameTools Tauri - 生产构建" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 设置 Rust 环境
Write-Host "[1/3] 配置 Rust 环境..." -ForegroundColor Yellow
$env:Path = "$env:USERPROFILE\.cargo\bin;" + $env:Path

# 切换到项目目录
Set-Location "d:\dev\gametools\tauri-app"

# 检查依赖
Write-Host "[2/3] 检查依赖..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "安装 Node 依赖..." -ForegroundColor Yellow
    npm install
}

# 开始构建
Write-Host "[3/3] 开始构建..." -ForegroundColor Yellow
Write-Host "这可能需要 10-15 分钟（首次构建）..." -ForegroundColor Gray
Write-Host ""

npm run tauri:build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "✅ 构建成功!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "生成的文件位于:" -ForegroundColor Cyan
    Write-Host "  src-tauri\target\release\gametools.exe" -ForegroundColor White
    Write-Host "  src-tauri\target\release\bundle\" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "❌ 构建失败" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
}
