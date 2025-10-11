@echo off
chcp 65001 >nul
echo 启动越南文检测 - 图形界面版本
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
python -c "import pandas, openpyxl, tkinter" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r ..\core\requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 启动GUI程序
echo 启动图形界面...
python ..\gametool.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)
