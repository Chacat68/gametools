# GameTools 测试文件夹

> 版本: v1.39.6 | 最后更新: 2025-12-16

## 📋 概述

本文件夹包含 GameTools 项目的所有**功能测试**和**测试数据生成工具**。

## 📁 目录结构

```
test/
├── README.md (此文件)
│
├── 🧪 功能测试脚本 (15个)
│   ├── test_batch_modifier.py              # 批量改表工具测试
│   ├── test_cache_basic.py                 # 缓存系统基本功能
│   ├── test_cache_performance.py           # 缓存性能对比
│   ├── test_config_sync.py                 # 配置同步测试
│   ├── test_cross_project_redesigned.py    # 跨项目翻译测试
│   ├── test_error_logging.py               # 错误日志功能
│   ├── test_excel_position.py              # Excel位置验证
│   ├── test_field_extraction_filtered.py   # 字段提取过滤
│   ├── test_field_extractor.py             # 字段导出工具
│   ├── test_field_extractor_json.py        # 字段导出JSON格式
│   ├── test_field_filter.py                # 字段过滤规则
│   ├── test_json_format.py                 # JSON格式验证
│   ├── test_language_detection.py          # 语言检测功能
│   ├── test_layout.py                      # GUI布局测试
│   ├── test_multi_lang_folders.py          # 多语言文件夹
│   ├── test_multilang_json.py              # 多语言JSON配置
│   ├── test_phase2_integration.py          # Phase2集成测试
│   └── test_phase2_units.py                # Phase2单元测试
│
├── 🛠️ 测试数据生成 (6个)
│   ├── create_test_excel.py                # 创建基础测试Excel
│   ├── create_test_excel_for_field_extractor.py  # 字段导出测试数据
│   ├── create_test_field_type_excel.py     # 字段类型测试数据
│   ├── create_test_mapping_file.py         # 映射文件测试数据
│   ├── create_test_table_range.py          # 表范围翻译测试数据
│   └── create_filter_test_excel.py         # 过滤功能测试数据
│
├── 🚀 测试执行
│   ├── run_all_tests.py                    # 运行所有测试
│   └── run_tests.bat                       # Windows批处理脚本
│
├── 📊 测试数据目录
│   ├── test_excel_files/                   # Excel测试文件
│   ├── test_config_sync/                   # 配置同步测试数据
│   ├── test_multi_lang/                    # 多语言测试数据
│   ├── test_table_range/                   # 表范围翻译测试数据
│   └── test_output/                        # 测试输出结果
│
└── .gitkeep
```

---

## 🧪 测试分类

### 1️⃣ 核心功能测试

#### 字段导出工具 (Field Extractor)
- `test_field_extractor.py` - 基本功能测试
- `test_field_extractor_json.py` - JSON格式输出
- `test_field_extraction_filtered.py` - 带过滤的提取
- `test_field_filter.py` - 过滤规则测试

#### 多语言翻译 (Multi-Language)
- `test_multilang_json.py` - JSON配置格式
- `test_multi_lang_folders.py` - 多语言文件夹结构
- `test_language_detection.py` - 语言检测

#### 表范围翻译 (Table Range Translator)
- `test_excel_position.py` - Excel位置验证
- `test_cross_project_redesigned.py` - 跨项目翻译

#### 批量改表 (Batch Modifier)
- `test_batch_modifier.py` - 批量修改测试
- `test_config_sync.py` - 配置同步

### 2️⃣ 性能和缓存测试

- `test_cache_basic.py` - 缓存基本功能
- `test_cache_performance.py` - 性能对比（有缓存 vs 无缓存）

### 3️⃣ 集成测试

- `test_phase2_integration.py` - Phase 2功能集成测试
- `test_phase2_units.py` - Phase 2单元测试套件

### 4️⃣ 其他

- `test_error_logging.py` - 错误日志系统
- `test_json_format.py` - JSON格式验证
- `test_layout.py` - GUI布局

---

## 🚀 快速开始

### 运行所有测试

```bash
# 方式1：Python脚本
cd d:\dev\gametools
python test/run_all_tests.py

# 方式2：Windows批处理
cd d:\dev\gametools\test
run_tests.bat

# 方式3：单个测试
python test/test_cache_basic.py
python test/test_field_extractor.py
```

### 生成测试数据

```bash
# 创建所有测试数据
cd d:\dev\gametools
python test/create_test_excel.py
python test/create_test_mapping_file.py
python test/create_test_table_range.py
```

---

## 📊 测试数据目录说明

### test_excel_files/
用于字段导出、过滤等功能的测试Excel文件
```
生成方式: python test/create_test_excel_for_field_extractor.py
输出: test_excel_files/
```

### test_config_sync/
Excel配置同步测试数据
```
结构:
  source/              # 源文件
  target1/             # 目标文件集1
  target2/             # 目标文件集2
```

### test_multi_lang/
多语言提取测试数据
```
生成方式: python test/create_test_table_range.py
输出: test_table_range/ (主要数据)
     test_multi_lang/ (配置)
```

### test_table_range/
表范围翻译测试数据
```
包含: 中文/越南文/泰文配置文件和测试数据
用于: TABLE_RANGE_TRANSLATOR 功能测试
```

### test_output/
测试执行的输出结果
```
包含: CSV、JSON、Excel等格式的测试输出
注意: 此目录会被测试脚本覆盖
```

---

## 📝 测试执行流程

### 1. 前置条件
```bash
# 确保环境已配置
cd d:\dev\gametools
pip install -r core/requirements.txt
```

### 2. 生成测试数据
```bash
# 创建测试数据（按需执行）
python test/create_test_excel.py
python test/create_test_table_range.py
```

### 3. 运行测试
```bash
# 运行所有测试
python test/run_all_tests.py

# 或运行特定测试
python test/test_cache_basic.py
python test/test_field_extractor.py
```

### 4. 查看结果
```
✓ 成功: test passed
✗ 失败: test failed
结果输出: test_output/
```

---

## ✅ 测试覆盖范围

| 功能模块 | 测试文件 | 覆盖率 |
|---------|---------|--------|
| 字段导出 (Field Extractor) | test_field_extractor*.py | ✓ 完整 |
| 多语言翻译 | test_multilang*.py, test_language_detection.py | ✓ 完整 |
| 表范围翻译 | test_excel_position.py | ✓ 完整 |
| 批量改表 | test_batch_modifier.py, test_config_sync.py | ✓ 完整 |
| 缓存系统 | test_cache_*.py | ✓ 完整 |
| 跨项目翻译 | test_cross_project_redesigned.py | ✓ 完整 |
| 错误处理 | test_error_logging.py | ✓ 完整 |
| GUI布局 | test_layout.py | ✓ 基础 |

---

## 🔧 运行特定测试模块

### 缓存系统测试
```bash
python test/test_cache_basic.py           # 基本功能
python test/test_cache_performance.py     # 性能对比
```

### 字段导出工具
```bash
python test/test_field_extractor.py       # 基本功能
python test/test_field_extractor_json.py  # JSON输出
python test/test_field_filter.py          # 过滤规则
```

### 多语言功能
```bash
python test/test_multilang_json.py        # JSON配置
python test/test_multi_lang_folders.py    # 文件夹结构
python test/test_language_detection.py    # 语言检测
```

### Phase 2集成
```bash
python test/test_phase2_units.py          # 单元测试
python test/test_phase2_integration.py    # 集成测试
```

---

## 📌 注意事项

1. **测试数据生成** - 运行测试前可能需要先生成测试数据
2. **依赖项** - 确保已安装 `requirements.txt` 中的所有依赖
3. **输出文件** - 测试生成的文件存储在 `test_output/` 目录
4. **清理策略** - 旧的演示和验证文件已被删除，保留核心功能测试
5. **相对路径** - 所有测试应从项目根目录运行 `python test/test_xxx.py`

---

## 🐛 故障排除

### Q: 找不到模块
**A:** 确保在项目根目录运行测试
```bash
cd d:\dev\gametools
python test/test_cache_basic.py
```

### Q: 找不到测试数据文件
**A:** 先生成测试数据
```bash
python test/create_test_excel.py
python test/create_test_table_range.py
```

### Q: 某些测试失败
**A:** 检查是否有必需的依赖未安装
```bash
pip install -r core/requirements.txt
```

---

## 📞 相关文档

- **项目文档** - [../docs/README.md](../docs/README.md)
- **版本信息** - [../version.py](../version.py)
- **构建报告** - [../docs/BUILD_REPORT.md](../docs/BUILD_REPORT.md)

