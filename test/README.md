# GameTools 测试文件夹

> 版本: v1.42.0 | 最后更新: 2026-01-10

## 📋 概述

本文件夹包含 GameTools 项目的所有**功能测试**和**测试数据生成工具**。  
涉及 Excel 的用例默认遵循策划表布局约定，见 [../docs/EXCEL_TABLE_LAYOUT.md](../docs/EXCEL_TABLE_LAYOUT.md)。

## 📁 目录结构

```text
test/
├── README.md (此文件)
│
├── 🛠️ 测试数据生成（合并版）
│   └── create_test_data.py              # 统一的测试数据生成工具
│
├── 🧪 功能测试脚本
│   ├── test_batch_modifier.py           # 批量改表测试（含CSV、Position模式）
│   ├── test_cache.py                    # 缓存系统测试（含基本功能、性能）
│   ├── test_config_sync.py              # 配置同步测试（写入 _runtime/config_sync）
│   ├── test_cross_project_redesigned.py # 跨项目翻译测试
│   ├── test_csv_mapping.py              # CSV映射测试
│   ├── test_error_logging.py            # 错误日志功能（写入 _runtime/output）
│   ├── test_field_extractor.py          # 字段导出测试（含CSV/JSON/Excel/过滤）
│   ├── test_json_format.py              # JSON格式验证
│   ├── test_language_detection.py       # 语言检测功能
│   ├── test_multilang_json.py           # 多语言JSON配置
│   ├── test_multi_lang_folders.py       # 多语言文件夹（写入 _runtime/multi_lang）
│   └── test_translation_csv_format.py   # 翻译CSV格式
│
├── 🚀 测试执行
│   ├── run_all_tests.py                 # 运行所有测试
│   └── run_tests.bat                    # Windows批处理脚本
│
├── 📊 按需生成的样例数据（由 create_test_data 写入 test/_runtime/generated/）
│   └── （子目录）test_data、test_excel_files、test_table_range 等，勿提交
│
├── 🗂️ _runtime/                          # 统一运行时输出（勿提交，见 .gitignore）
│   ├── config_sync/                     # test_config_sync.py
│   ├── multi_lang/                      # test_multi_lang_folders.py
│   ├── output/                          # test_error_logging.py
│   └── generated/                       # create_test_data.py（test_data、test_excel_files、test_table_range 等子目录）
│
└── 📁 test_output/                      # 其它测试可能使用的输出目录（勿提交）
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

# GUI 冒烟（仓库根目录脚本，不纳入 run_all_tests）
python verify_gui.py
```

## 📝 测试文件说明

| 测试文件 | 测试内容 |
| -------- | -------- |
| `test_batch_modifier.py` | 批量改表基本功能、CSV格式、Position定位模式 |
| `test_cache.py` | 内存缓存、文件缓存、LRU淘汰、性能对比 |
| `test_field_extractor.py` | CSV/JSON/Excel输出、字段过滤规则 |
| `test_config_sync.py` | Excel配置同步功能 |
| `test_cross_project_redesigned.py` | 跨项目翻译对应 |
| `test_language_detection.py` | 中文/越南文/泰文检测 |

## ⚠️ 注意事项

1. 运行测试前如缺少样例文件，请先执行 `python create_test_data.py --all`
2. `test/_runtime/`、`test/test_output/` 及按需生成的 Excel 目录为运行产物，**勿提交**（已 `.gitignore`）
3. 若本地仍有历史遗留的仓库根目录 `test_config_sync/`、`test_multi_lang/`、`test_output/`，可删除；新脚本已改为只写入 `test/_runtime/`
4. 已删除与现有能力重复的脚本：`test_progress_callback.py`（仅校验进度回调属性，无业务覆盖）、`test_layout.py`（窗口冒烟请用仓库根目录 **`verify_gui.py`**；后台任务与参数冻结见 **`test_gui_background_tasks.py`**）。
