@echo off
chcp 65001 >nul
echo 越南文检测 - 越南文表格检测器
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import pandas, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r ..\core\requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 运行主程序
python ..\core\localization_checker.py

echo.
echo 按任意键退出...
pause >nul
