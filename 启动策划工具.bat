@echo off
chcp 65001 >nul
echo ========================================
echo   gametools - 游戏策划工具集
echo ========================================
echo.
echo 功能模块:
echo   - 越南文检测导出
echo   - 跨项目翻译对应
echo   - JSON错误检测工具
echo   - Excel数据处理工具
echo   - Excel分页拆分
echo   - 表字段导出
echo   - 多语言翻译提取
echo   - 批量改表 (新增)
echo.
echo 正在启动...
echo.
python gui\run_unified.py
if errorlevel 1 (
    echo.
    echo 启动失败，请确保已安装Python和所需依赖
    echo 可以运行: pip install -r core\requirements.txt
)
pause
