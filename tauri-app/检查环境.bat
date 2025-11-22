@echo off
chcp 65001 > nul
echo ====================================
echo GameTools Tauri - 环境检查和安装
echo ====================================
echo.

:: 检查 Node.js
echo [1/3] 检查 Node.js...
where node >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Node.js 已安装
    node --version
) else (
    echo ❌ 未安装 Node.js
    echo.
    echo 请访问以下链接下载安装 Node.js:
    echo https://nodejs.org/
    echo.
    echo 推荐下载 LTS 版本
    pause
    exit /b 1
)

echo.
echo [2/3] 检查 Rust...
where rustc >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Rust 已安装
    rustc --version
    cargo --version
) else (
    echo ❌ 未安装 Rust
    echo.
    echo 正在打开 Rust 安装页面...
    echo.
    echo 请按照以下步骤操作:
    echo 1. 下载并运行 rustup-init.exe
    echo 2. 选择默认安装选项
    echo 3. 安装完成后关闭并重新打开此窗口
    echo.
    start https://www.rust-lang.org/tools/install
    pause
    exit /b 1
)

echo.
echo [3/3] 检查 Python...
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Python 已安装
    python --version
) else (
    echo ❌ 未安装 Python
    echo.
    echo 请访问以下链接下载安装 Python:
    echo https://www.python.org/downloads/
    echo.
    echo ⚠️ 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo.
echo ====================================
echo ✅ 所有依赖都已安装!
echo ====================================
echo.
echo 现在可以运行以下命令:
echo   - 启动开发模式.bat
echo   - 构建生产版本.bat
echo.
pause
