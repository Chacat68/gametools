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
        
        # 清理 sys.path 中可能导致 numpy 认为在源目录的路径
        cleaned_path = []
        for p in sys.path:
            p_lower = p.lower()
            # 保留 _MEIPASS 内的路径
            if meipass.lower() in p_lower:
                cleaned_path.append(p)
            # 保留 site-packages 路径
            elif 'site-packages' in p_lower:
                cleaned_path.append(p)
            # 排除可能的 numpy 源目录
            elif 'numpy' in p_lower:
                continue
            else:
                cleaned_path.append(p)
        
        sys.path[:] = cleaned_path
        
        # 确保 _MEIPASS 在 sys.path 最前面
        if meipass not in sys.path:
            sys.path.insert(0, meipass)
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
