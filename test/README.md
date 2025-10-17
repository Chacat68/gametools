# 测试文件夹

## 概述

此文件夹是 GameTools 项目的**集中测试目录**，所有测试文件应放在此处。

## 文件夹结构

```
test/
├── README.md (此文件)
├── 缓存系统测试
│   ├── test_cache_basic.py          # 缓存基本功能测试
│   ├── test_cache_performance.py    # 缓存性能对比测试
│
├── 功能模块测试
│   ├── test_new_column_names.py            # 新列名兼容性测试
│   ├── test_fixed_compatibility.py         # 兼容性修复测试
│   ├── test_cross_project_redesigned.py    # 跨项目翻译设计测试
│
├── 测试数据生成工具
│   ├── create_test_excel.py         # 创建测试 Excel 文件
│   ├── create_test_mapping_file.py  # 创建测试映射文件
│   ├── check_mixed_test.py          # 混合文本检测测试
│
└── GUI 测试
    └── test_layout.py                # GUI 布局测试
```

## 测试文件说明

### 缓存系统测试

#### `test_cache_basic.py`
- **用途**: 验证缓存系统的基本功能
- **测试内容**:
  - 内存缓存（LRU）功能
  - 文件缓存（Pickle）功能
  - 统一缓存管理器
  - 增强版翻译工具集成
- **运行方式**: `python test/test_cache_basic.py`
- **预期结果**: ✓ 所有功能测试通过

#### `test_cache_performance.py`
- **用途**: 对比带缓存和不带缓存的性能差异
- **测试内容**:
  - 创建测试数据和文件
  - 无缓存翻译对应性能测试
  - 缓存版冷启动性能测试
  - 缓存版热启动性能测试
  - 生成性能对比报告
- **运行方式**: `python test/test_cache_performance.py`
- **预期结果**: 缓存版本比无缓存版本快 7-10 倍

### 功能模块测试

#### `test_new_column_names.py`
- **用途**: 测试新列名的兼容性处理
- **运行方式**: `python test/test_new_column_names.py`

#### `test_fixed_compatibility.py`
- **用途**: 测试修复的兼容性问题
- **运行方式**: `python test/test_fixed_compatibility.py`

#### `test_cross_project_redesigned.py`
- **用途**: 测试重新设计的跨项目翻译功能
- **运行方式**: `python test/test_cross_project_redesigned.py`

### 测试数据生成工具

#### `create_test_excel.py`
- **用途**: 生成用于测试的 Excel 文件
- **使用方式**: `python test/create_test_excel.py`

#### `create_test_mapping_file.py`
- **用途**: 生成用于测试的映射文件
- **使用方式**: `python test/create_test_mapping_file.py`

#### `check_mixed_test.py`
- **用途**: 测试混合文本检测功能
- **使用方式**: `python test/check_mixed_test.py`

### GUI 测试

#### `test_layout.py`
- **用途**: 测试 GUI 界面布局
- **运行方式**: `python test/test_layout.py`

## 规约与最佳实践

### 命名规范
- ✅ 测试文件必须以 `test_` 开头
- ✅ 数据生成工具以 `create_test_` 开头
- ✅ 辅助检测工具以 `check_` 开头
- ✅ 文件名全小写，用下划线分隔

### 文件结构
每个测试文件应包含：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块说明
简短描述此测试的目的
"""

import sys
from pathlib import Path

# 添加模块路径 - 这个很关键！
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入需要测试的模块
# ...

# 测试函数和逻辑
# ...
```

### 导入路径配置
由于测试文件位于 `test/` 子目录，必须正确配置导入路径：
```python
# ✅ 正确做法：指向项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))

# 然后导入模块
from core.cache_manager import CacheManager
from core.cross_project_translator import CrossProjectTranslator
```

### 资源清理
每个测试应清理生成的临时文件：
```python
# 例如清理测试缓存
import shutil
if Path(".test_cache").exists():
    shutil.rmtree(".test_cache")
```

## 运行所有测试

### 单个测试运行
```bash
cd d:\dev\gametools
python test\test_cache_basic.py
python test\test_cache_performance.py
```

### 批量运行所有测试
```bash
cd d:\dev\gametools
for($file in Get-ChildItem test\test_*.py) { python $file.FullName }
```

### 使用 pytest (推荐用于大型项目)
```bash
pip install pytest
pytest test\
```

## 版本兼容性

- **Python**: 3.7 及以上
- **依赖项**: 参见 `core/requirements.txt`
  - pandas
  - openpyxl
  - (其他依赖...)

## CI/CD 集成

这个测试文件夹已为 CI/CD 集成做好准备：

```yaml
# 示例 GitHub Actions 工作流
- name: Run Tests
  run: |
    cd gametools
    python -m pytest test/ -v
```

## 常见问题

### Q: 导入错误 "ModuleNotFoundError"
A: 确保在测试文件开头添加了:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Q: 测试文件生成的临时数据未清理
A: 检查测试结束时是否有清理代码，例如:
```python
if Path(".test_cache").exists():
    import shutil
    shutil.rmtree(".test_cache")
```

### Q: 测试在新环境运行失败
A: 确保已安装所有依赖:
```bash
pip install -r core/requirements.txt
```

## 添加新测试

新增测试时，请遵循以下步骤：

1. **创建文件**: `test/test_新功能.py`
2. **编写测试**: 包含清晰的测试逻辑和注释
3. **添加路径**: 在文件顶部配置 `sys.path`
4. **清理资源**: 测试完成后清理临时文件
5. **验证运行**: 确保测试能独立运行成功
6. **更新本文档**: 在相应部分添加说明

## 相关文档

- [缓存系统指南](../docs/CACHE_SYSTEM_GUIDE.md)
- [缓存实现说明](../docs/CACHE_IMPLEMENTATION.md)
- [项目 README](../README.md)

---

**最后更新**: 2025-10-17
**项目版本**: v1.19.0
