# -*- coding: utf-8 -*-
"""
PyInstaller Runtime Hook - 修复 numpy 导入问题 (性能优化版)
此文件会在程序启动时最先执行，用于修复 numpy 在 PyInstaller 环境中的导入问题

性能优化:
- 使用懒加载，避免不必要的模块导入
- 最小化启动时的操作数量
- 缓存检查结果避免重复计算
"""

import sys
import os

# 快速检查：非PyInstaller环境直接跳过
if not hasattr(sys, '_MEIPASS'):
    pass  # 不是PyInstaller打包环境，跳过所有修复
else:
    def _fix_numpy_import():
        """修复 PyInstaller 打包后 numpy 无法导入的问题（优化版）"""
        import types
        
        meipass = sys._MEIPASS
        
        # 1. 设置关键环境变量（这些是轻量操作）
        os.environ.setdefault('NUMPY_EXPERIMENTAL_ARRAY_FUNCTION', '0')
        os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')  # 避免OpenBLAS多线程问题
        os.environ.setdefault('MKL_NUM_THREADS', '1')  # 避免MKL多线程问题
        
        # 2. 确保 __NUMPY_SETUP__ 设为 False（使用setdefault避免覆盖）
        import builtins
        if not hasattr(builtins, '__NUMPY_SETUP__'):
            builtins.__NUMPY_SETUP__ = False
        
        # 3. 优化 sys.path（只在需要时执行）
        meipass_lower = meipass.lower()
        sys.path = [p for p in sys.path 
                    if 'numpy' not in p.lower() or 
                    meipass_lower in p.lower() or 
                    'site-packages' in p.lower()]
        
        # 4. 确保 _MEIPASS 在 sys.path 最前面
        if meipass not in sys.path:
            sys.path.insert(0, meipass)
        
        # 5. 预创建 numpy.__config__ 模块（懒加载版本）
        def _create_fake_numpy_config():
            """创建一个最小化的模拟 numpy.__config__ 模块"""
            config_module = types.ModuleType('numpy.__config__')
            config_module.__file__ = os.path.join(meipass, 'numpy', '__config__.py')
            config_module.show = lambda mode='stdout': "NumPy (PyInstaller bundled)\n"
            config_module._built_with_meson = False
            return config_module
        
        # 仅在需要时创建模拟模块
        if 'numpy.__config__' not in sys.modules:
            try:
                # 尝试正常导入
                import importlib.util
                spec = importlib.util.find_spec('numpy.__config__')
                if spec is None:
                    sys.modules['numpy.__config__'] = _create_fake_numpy_config()
            except Exception:
                sys.modules['numpy.__config__'] = _create_fake_numpy_config()

    # 立即执行修复
    _fix_numpy_import()
    # 清理命名空间
    del _fix_numpy_import

