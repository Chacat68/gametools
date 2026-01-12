# -*- coding: utf-8 -*-
"""
PyInstaller hook for numpy (性能优化版)
仅收集必需的numpy子模块，减少打包体积和启动时间
"""

from PyInstaller.utils.hooks import collect_submodules, get_module_file_attribute
import os

# 只收集核心numpy子模块（而非全部）
# 这大大减少了分析时间和最终包体积
hiddenimports = [
    # 核心模块
    'numpy.core',
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'numpy.core._dtype_ctypes',
    'numpy.core.multiarray',
    'numpy.core.umath',
    'numpy.core.numerictypes',
    'numpy.core.numeric',
    'numpy.core.fromnumeric',
    'numpy.core.shape_base',
    # 库模块
    'numpy.lib',
    'numpy.lib.format',
    'numpy.lib.mixins',
    'numpy.lib.stride_tricks',
    # 随机数
    'numpy.random',
    'numpy.random.mtrand',
    'numpy.random._common',
    # 线性代数（pandas可能需要）
    'numpy.linalg',
    'numpy.linalg._umath_linalg',
    # FFT
    'numpy.fft',
    # 兼容性
    'numpy.compat',
    # numpy 2.x 新核心
    'numpy._core',
    'numpy._core._multiarray_umath',
]

# 排除不需要的numpy子模块
excludedimports = [
    'numpy.distutils',
    'numpy.f2py',
    'numpy.testing',
    'numpy.tests',
    'numpy.doc',
    'numpy.matrixlib',
    'numpy.polynomial',
    'numpy.ma',  # masked arrays（如果不需要）
]

# 获取numpy的二进制数据（只收集核心DLL）
binaries = []
try:
    numpy_lib_dir = os.path.dirname(get_module_file_attribute('numpy'))
    
    # 只添加核心的.pyd/.dll文件
    core_patterns = ['_multiarray', 'umath', 'mtrand', 'linalg', 'fft']
    
    for item in os.listdir(numpy_lib_dir):
        item_path = os.path.join(numpy_lib_dir, item)
        if item.endswith(('.so', '.pyd', '.dll')):
            # 只添加核心二进制文件
            if any(pattern in item.lower() for pattern in core_patterns):
                binaries.append((item_path, 'numpy'))
except Exception:
    pass

# 显式设置datas为空以避免收集不必要的数据文件
datas = []
