@echo off
chcp 65001 >nul
title GameTools 现代化版本
cd /d "%~dp0"
python gui\run_modern.py
pause
