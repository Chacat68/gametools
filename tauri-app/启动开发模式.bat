@echo off
chcp 65001 > nul
echo ====================================
echo GameTools Tauri 版本 - 开发模式
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] 检查 Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js
    echo 请访问 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

echo.
echo [2/3] 检查 Rust...
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Rust
    echo 请访问 https://www.rust-lang.org/tools/install 下载安装
    pause
    exit /b 1
)
echo ✅ Rust 已安装

echo.
echo [3/3] 检查依赖...
if not exist "node_modules" (
    echo 正在安装依赖...
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 依赖已就绪

echo.
echo ====================================
echo 启动开发服务器...
echo ====================================
echo.

echo 正在设置 Rust 环境变量...
set PATH=%USERPROFILE%\.cargo\bin;%PATH%

call npm run tauri:dev

pause
