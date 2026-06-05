#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools统一版本启动脚本
用于直接运行统一界面，无需打包
"""

import sys
import os
from pathlib import Path

# 确保在正确的目录中运行
if __name__ == "__main__":
    # 检测是否在 PyInstaller 环境
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包环境（numpy/pandas 依赖由 PyInstaller 官方 hook 处理）
        # 设置工作目录为 exe 所在目录
        exe_dir = Path(sys.executable).parent
        os.chdir(exe_dir)
        
        # 确保 _MEIPASS 在 sys.path 中
        if sys._MEIPASS not in sys.path:
            sys.path.insert(0, sys._MEIPASS)
        
        # 导入并运行统一界面（使用绝对导入）
        from gui.gametools_unified import main
    else:
        # 开发环境
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        os.chdir(project_root)
        
        # 导入并运行统一界面
        from gui.gametools_unified import main
    
    print("启动gametools统一界面...")
    main()
