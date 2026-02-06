# GameTools 测试文件夹

> 版本: v1.42.0 | 最后更新: 2026-01-10

## 📋 概述

本文件夹包含 GameTools 项目的所有**功能测试**和**测试数据生成工具**。

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
├── 📊 测试数据目录
│   ├── test_excel_files/                # Excel测试文件
│   ├── test_config_sync/                # 配置同步测试数据
│   ├── test_multi_lang/                 # 多语言测试数据
│   └── test_table_range/                # 表范围翻译测试数据
│
└── 📁 输出目录
    └── test_output/                     # 测试输出（已加入.gitignore）
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

### 系统依赖
在Linux系统上运行测试前，需要先安装tkinter：
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install python3-tk

# 或使用项目提供的自动安装脚本
./setup_linux.sh
```

### 测试数据
1. 运行测试前请先生成测试数据：`python create_test_data.py --all`
2. 测试输出目录 `test_output/` 已加入 `.gitignore`
3. 测试数据目录的内容可由 `create_test_data.py` 重新生成
4. 所有`.xlsx`和`.bak`测试文件已从git追踪中移除，可自动重新生成

