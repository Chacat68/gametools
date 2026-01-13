@echo off
chcp 65001 >nul
title GameTools - 游戏策划工具集（现代化版本）
cd /d "%~dp0"
echo ========================================
echo   gametools - 游戏策划工具集
echo   [现代化版本]
echo ========================================
echo.
echo 功能模块:
echo   - 批量改表
echo   - 字段导出
echo   - 分页拆分
echo   - 配置同步
echo   - Excel转CSV
echo   - 数据处理
echo   - 跨项目翻译
echo   - 多语言提取
echo   - JSON检测
echo.
echo 正在启动...
echo.
python gui\run_modern.py
if errorlevel 1 (
    echo.
    echo 启动失败，请确保已安装Python和所需依赖
    echo 可以运行: pip install -r requirements.txt
)
pause
