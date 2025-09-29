@echo off
chcp 65001 >nul
echo 构建JSON格式检测工具exe文件...
echo.
python build.py
pause
