# GameTools 测试文件夹

> 版本: v1.42.0 | 最后更新: 2026-01-10

## 📋 概述

本文件夹包含 GameTools 项目的所有**功能测试**和**测试数据生成工具**。  
涉及 Excel 的用例默认遵循策划表布局约定，见 [../docs/EXCEL_TABLE_LAYOUT.md](../docs/EXCEL_TABLE_LAYOUT.md)。

## 📁 目录结构

```
test/
├── README.md (此文件)
│
├── 🛠️ 测试数据生成（合并版）
│   └── create_test_data.py              # 统一的测试数据生成工具
│
├── 🧪 功能测试脚本
│   ├── test_batch_modifier.py           # 批量改表测试（含CSV、Position模式）
│   ├── test_cache.py                    # 缓存系统测试（含基本功能、性能）
│   ├── test_config_sync.py              # 配置同步测试
│   ├── test_cross_project_redesigned.py # 跨项目翻译测试
│   ├── test_csv_mapping.py              # CSV映射测试
│   ├── test_error_logging.py            # 错误日志功能
│   ├── test_field_extractor.py          # 字段导出测试（含CSV/JSON/Excel/过滤）
│   ├── test_json_format.py              # JSON格式验证
│   ├── test_language_detection.py       # 语言检测功能
│   ├── test_layout.py                   # GUI布局测试
│   ├── test_multilang_json.py           # 多语言JSON配置
│   ├── test_multi_lang_folders.py       # 多语言文件夹
│   └── test_translation_csv_format.py   # 翻译CSV格式
│
├── 🚀 测试执行
│   ├── run_all_tests.py                 # 运行所有测试
│   └── run_tests.bat                    # Windows批处理脚本
│
├── 📊 test/ 内置测试夹具
│   ├── test_excel_files/                # Excel测试文件（按需生成）
│   ├── test_config_sync/                # 随仓库提交的最小配置夹具
│   ├── test_multi_lang/                 # 随仓库提交的最小配置夹具
│   └── test_table_range/                # 表范围翻译测试数据（按需生成）
│
└── 📁 运行产物
    └── test_output/                     # 测试运行时自动创建，不再提交到仓库
```

## 🚀 快速开始

### 运行所有测试
```bash
python run_all_tests.py
# 或
run_tests.bat
```

### 生成测试数据
```bash
# 生成所有测试数据
python create_test_data.py --all

# 只生成特定类型
python create_test_data.py --excel      # 基础Excel
python create_test_data.py --field      # 字段提取测试数据
python create_test_data.py --filter     # 过滤测试数据
python create_test_data.py --mapping    # 映射文件
python create_test_data.py --csv        # CSV映射
python create_test_data.py --range      # 表范围测试
```

### 运行单个测试
```bash
# 字段提取测试（支持多种选项）
python test_field_extractor.py --all
python test_field_extractor.py --json   # 只测试JSON格式
python test_field_extractor.py --filter # 只测试过滤功能

# 批量改表测试
python test_batch_modifier.py --all
python test_batch_modifier.py --csv     # 只测试CSV格式
python test_batch_modifier.py --position # 只测试Position模式

# 缓存系统测试
python test_cache.py --all
python test_cache.py --basic  # 只测试基本功能
python test_cache.py --perf   # 只测试性能
```

## 📝 测试文件说明

| 测试文件 | 测试内容 |
|---------|---------|
| `test_batch_modifier.py` | 批量改表基本功能、CSV格式、Position定位模式 |
| `test_cache.py` | 内存缓存、文件缓存、LRU淘汰、性能对比 |
| `test_field_extractor.py` | CSV/JSON/Excel输出、字段过滤规则 |
| `test_config_sync.py` | Excel配置同步功能 |
| `test_cross_project_redesigned.py` | 跨项目翻译对应 |
| `test_language_detection.py` | 中文/越南文/泰文检测 |

## ⚠️ 注意事项

1. 运行测试前如缺少样例文件，请先执行 `python create_test_data.py --all`
2. `test_output/` 和部分 Excel 样例属于运行产物，测试时会按需自动创建
3. `test/` 下的 `test_config_sync/`、`test_multi_lang/` 是随仓库提交的最小配置夹具，不是运行产物
4. 项目根目录下的 `test_config_sync/`、`test_multi_lang/` 是测试脚本运行时使用的工作目录，里面的 Excel 和导出文件可以重新生成

