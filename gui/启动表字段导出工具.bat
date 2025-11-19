@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ========================================
echo 启动表字段导出工具GUI
echo ========================================
echo.
python gui\excel_field_extractor_gui.py
pause
