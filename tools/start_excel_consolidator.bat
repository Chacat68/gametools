@echo off
chcp 65001 >nul
echo Excel数据整合工具
echo ==================
echo.
echo 选择运行模式:
echo 1. GUI界面模式
echo 2. 命令行模式
echo 3. 退出
echo.
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    echo 启动GUI界面...
    python tools/excel_consolidator_gui.py
) else if "%choice%"=="2" (
    echo 命令行模式使用说明:
    echo python tools/excel_consolidator.py input_file.xlsx output_folder
    echo.
    echo 可选参数:
    echo   --output-filename 文件名  输出文件名（默认为整合结果.xlsx）
    echo   --group-column 列名       指定分组列（默认为第一列）
    echo   --no-summary             不包含汇总信息
    echo   --sheet-prefix 前缀      工作表名称前缀
    echo.
    pause
) else if "%choice%"=="3" (
    exit
) else (
    echo 无效选择，请重新运行脚本
    pause
)
