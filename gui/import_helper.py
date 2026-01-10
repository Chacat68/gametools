#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入保护包装器 - 修复 PyInstaller 打包后的导入问题
特别是处理 numpy/pandas 在 exe 环境中的导入问题
"""

import sys
import os

# 修复 PyInstaller 环境下的 numpy 导入问题
def fix_pyinstaller_imports():
    """修复 PyInstaller 环境中的导入问题"""
    # 移除可能的 numpy 源目录从 sys.path
    original_path = sys.path.copy()
    sys.path = [p for p in sys.path if 'numpy' not in p.lower() or 'site-packages' in p.lower()]
    
    # 如果在 PyInstaller 环境中，设置临时目录
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # 设置 numpy 配置
        os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'
        
        # 避免 numpy 尝试导入其源目录
        numpy_base = os.path.join(sys._MEIPASS, 'numpy')
        if os.path.exists(numpy_base):
            # 清理可能导致问题的路径
            sys.path = [p for p in sys.path if numpy_base not in p]

# 在任何其他导入之前调用此函数
try:
    fix_pyinstaller_imports()
except Exception as e:
    print(f"警告: 导入修复失败 - {e}")

# 尝试导入关键依赖
try:
    import pandas  # noqa: F401
    import numpy   # noqa: F401
    import xlwings  # noqa: F401
    import openpyxl  # noqa: F401
except ImportError as e:
    print(f"错误: 无法导入必需的模块 - {e}")
    print("这可能是 PyInstaller 环境问题，请尝试以下方案：")
    print("1. 重新运行应用程序")
    print("2. 重新安装依赖: pip install -r requirements.txt")
    print("3. 使用非打包版本: python gui/run_unified.py")
    sys.exit(1)
