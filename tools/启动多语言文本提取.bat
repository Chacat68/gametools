@echo off
chcp 65001 > nul
title 翻译提取 - 多语言版本

echo.
echo ========================================
echo   翻译提取工具 - 多语言版本
echo ========================================
echo.
echo 正在启动GUI界面...
echo.

python tools\excel_text_extractor_gui.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败！请确保已安装Python和所需依赖包。
    echo.
    pause
)
