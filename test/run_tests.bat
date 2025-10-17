@REM 运行所有测试的批处理脚本
@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ================================================================
echo GameTools 测试套件启动
echo ================================================================
echo.

python test\run_all_tests.py

pause
