# -*- coding: utf-8 -*-
"""
PyInstaller Runtime Hook - 修复 numpy 导入问题
此文件会在程序启动时最先执行，用于修复 numpy 在 PyInstaller 环境中的导入问题

问题根源：
numpy 导入时会尝试 `from numpy.__config__ import show`，
如果导入失败会认为是从源目录运行并抛出错误。
PyInstaller 打包时可能没有正确包含 __config__.py 文件。

解决方案：
1. 设置 __NUMPY_SETUP__ = False 确保不会误判为在setup阶段
2. 创建一个模拟的 numpy.__config__ 模块
3. 清理 sys.path 中可能导致问题的路径
"""

import sys
import os
import types

def _fix_numpy_import():
    """修复 PyInstaller 打包后 numpy 无法导入的问题"""
    
    if not hasattr(sys, '_MEIPASS'):
        return
    
    meipass = sys._MEIPASS
    
    # 1. 确保 __NUMPY_SETUP__ 设为 False
    import builtins
    builtins.__NUMPY_SETUP__ = False
    
    # 2. 设置环境变量
    os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'  # 避免OpenBLAS多线程问题
    
    # 3. 清理 sys.path 中可能导致问题的路径
    cleaned_path = []
    for p in sys.path:
        p_lower = p.lower()
        # 跳过可能是 numpy 源目录的路径（不在 _MEIPASS 内）
        if 'numpy' in p_lower and meipass.lower() not in p_lower:
            if 'site-packages' not in p_lower:
                continue
        cleaned_path.append(p)
    sys.path[:] = cleaned_path
    
    # 4. 确保 _MEIPASS 在 sys.path 最前面
    if meipass not in sys.path:
        sys.path.insert(0, meipass)
    
    # 5. 如果工作目录可能有问题，切换到 _MEIPASS
    cwd = os.getcwd()
    if 'numpy' in cwd.lower():
        if os.path.exists(os.path.join(cwd, 'setup.py')):
            os.chdir(meipass)
    
    # 6. 预创建 numpy.__config__ 模块（如果不存在）
    # 这是最关键的修复 - numpy 会尝试导入这个模块来验证安装
    def _create_fake_numpy_config():
        """创建一个模拟的 numpy.__config__ 模块"""
        config_module = types.ModuleType('numpy.__config__')
        config_module.__file__ = os.path.join(meipass, 'numpy', '__config__.py')
        
        def show(mode='stdout'):
            """模拟的 show 函数"""
            info = "NumPy (PyInstaller bundled version)\n"
            if mode == 'stdout':
                print(info)
            return info
        
        config_module.show = show
        config_module._built_with_meson = False
        
        return config_module
    
    # 尝试正常导入，失败则使用模拟模块
    try:
        import numpy.__config__
    except ImportError:
        sys.modules['numpy.__config__'] = _create_fake_numpy_config()

# 立即执行修复
_fix_numpy_import()
