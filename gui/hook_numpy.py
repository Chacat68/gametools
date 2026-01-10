# -*- coding: utf-8 -*-
"""
PyInstaller hook for numpy
修复 numpy 导入错误的自定义hook
"""

from PyInstaller.utils.hooks import collect_submodules, get_module_file_attribute
import os

# 收集所有numpy子模块
hiddenimports = collect_submodules('numpy')

# 添加特定的numpy模块
hiddenimports.extend([
    'numpy.core',
    'numpy.lib',
    'numpy.compat',
    'numpy.f2py',
])

# 获取numpy的二进制数据
try:
    numpy_lib_dir = os.path.dirname(get_module_file_attribute('numpy'))
    binaries = []
    
    # 添加numpy的.so或.pyd文件
    for item in os.listdir(numpy_lib_dir):
        item_path = os.path.join(numpy_lib_dir, item)
        if item.endswith(('.so', '.pyd', '.dll')):
            binaries.append((item_path, 'numpy'))
except:
    binaries = []
