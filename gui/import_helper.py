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
    
    # 如果在 PyInstaller 环境中
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        meipass = sys._MEIPASS
        
        # 设置 numpy 配置
        os.environ.setdefault('NUMPY_EXPERIMENTAL_ARRAY_FUNCTION', '0')
        
        # 确保 _MEIPASS 在 sys.path 最前面
        if meipass not in sys.path:
            sys.path.insert(0, meipass)
        
        # 预导入核心模块以确保打包后可用
        try:
            import core
            import core.batch_excel_modifier
            import core.excel_field_extractor
            import core.table_range_translator
            import core.cross_project_translator
            import core.cross_project_translator_cached
            import tools.json_error_detector
        except ImportError as e:
            print(f"预导入核心模块失败: {e}")
    else:
        # 非 PyInstaller 环境，移除可能的 numpy 源目录
        sys.path = [p for p in sys.path if 'numpy' not in p.lower() or 'site-packages' in p.lower()]

# 延迟导入验证函数（不在模块加载时立即执行）
def verify_imports():
    """验证关键依赖是否可导入（供外部调用）"""
    missing = []
    for module in ['pandas', 'numpy', 'xlwings', 'openpyxl']:
        try:
            __import__(module)
        except ImportError as e:
            missing.append((module, str(e)))
    
    if missing:
        print("警告: 以下模块导入失败:")
        for module, error in missing:
            print(f"  - {module}: {error}")
        return False
    return True
