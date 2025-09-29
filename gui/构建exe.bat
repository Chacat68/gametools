@echo off
chcp 65001 >nul
echo 构建gametools统一版本exe文件...
echo.
python gui/build_unified.py
pause