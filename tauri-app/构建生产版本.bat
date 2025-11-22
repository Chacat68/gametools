@echo off
chcp 65001 > nul
echo ====================================
echo GameTools Tauri 版本 - 构建生产版本
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

echo.
echo [2/4] 检查 Rust...
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Rust
    pause
    exit /b 1
)
echo ✅ Rust 已安装

echo.
echo [3/4] 检查依赖...
if not exist "node_modules" (
    echo 正在安装依赖...
    call npm install
)
echo ✅ 依赖已就绪

echo.
echo [4/4] 开始构建...
echo ====================================
echo.

echo 正在设置 Rust 环境变量...
set PATH=%USERPROFILE%\.cargo\bin;%PATH%

call npm run tauri:build

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo ✅ 构建成功!
    echo ====================================
    echo.
    echo 生成的文件位于:
    echo   src-tauri\target\release\gametools.exe
    echo   src-tauri\target\release\bundle\
    echo.
) else (
    echo.
    echo ====================================
    echo ❌ 构建失败
    echo ====================================
    echo.
)

pause
