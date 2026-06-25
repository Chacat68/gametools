# GameTools 文档目录

> 游戏工具集文档导航，当前程序版本请以 [../version.py](../version.py) 和 GUI 显示为准。

**策划 Excel 统一约定**（表头行、`COLUMN_MARKER` / `c_` 列范围、`ROW_BOUNDARY_KEYWORD` 行下限等）以 **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)** 为准，代码常量见 `../core/constants.py`。下文各功能文档中与行号相关的描述均与该规范对齐。

**仓库维护**：已移除 Sheet 分页拆分功能（`core/excel_sheet_splitter.py`、`tools/excel_sheet_splitter.py`）。已删除未被引用的占位模块（`error_handler`、`log_manager`、`progress_tracker`、`output_formats`、`result_filter`、`task_controller`）及历史 PyInstaller 钩子脚本；日志初始化见 `core/__init__.py`。测试与 **`test/create_test_data.py`** 产出在 **`test/_runtime/`**（含 **`generated/`**），勿提交。

**统一 GUI 路径**：各功能页的 JSON、目录、映射表等路径均在 **「工作台」** 选择；功能页以只读方式显示相同路径（空路径显示「暂无」），不在页内提供浏览按钮。下文操作步骤均按此约定描述。

## 📚 文档导航

### 🚀 快速入门

- **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)** - 策划 Excel 表头、列标记与行边界统一规范（**推荐先读**）
- **[BATCH_MODIFIER_GUIDE.md](BATCH_MODIFIER_GUIDE.md)** - 批量改表工具使用指南
- **[EXCEL_FIELD_EXTRACTOR_README.md](EXCEL_FIELD_EXTRACTOR_README.md)** - 表字段导出工具说明
- **[FIELD_FILTER_GUIDE.md](FIELD_FILTER_GUIDE.md)** - 字段过滤规则指南

### 🔧 核心功能文档

#### 多语言翻译

- **[MULTI_LANGUAGE_TEXT_EXTRACTOR.md](MULTI_LANGUAGE_TEXT_EXTRACTOR.md)** - 多语言文本提取工具
- **[TABLE_RANGE_TRANSLATOR_GUIDE.md](TABLE_RANGE_TRANSLATOR_GUIDE.md)** - 表范围翻译提取工具
- **[MULTILANG_JSON_GUIDE.md](MULTILANG_JSON_GUIDE.md)** - 多语言JSON配置指南
- **[MULTI_LANGUAGE_UI_LAYOUT.md](MULTI_LANGUAGE_UI_LAYOUT.md)** - 多语言UI布局文档

#### 缓存系统

- **[CACHE_SYSTEM_GUIDE.md](CACHE_SYSTEM_GUIDE.md)** - 翻译内容缓存机制详解

#### CSV格式支持

- **[CSV_MAPPING_SUPPORT.md](CSV_MAPPING_SUPPORT.md)** - CSV映射表格式说明
- **[TRANSLATION_CSV_SUPPORT.md](TRANSLATION_CSV_SUPPORT.md)** - 翻译CSV格式支持

#### 辅助工具（统一 GUI）

- **[CROSS_PROJECT_GUIDE.md](CROSS_PROJECT_GUIDE.md)** - 跨项目翻译
- **[JSON_DETECTOR_GUIDE.md](JSON_DETECTOR_GUIDE.md)** - JSON 错误检测
- **[EXCEL_DATA_PROCESSOR_GUIDE.md](EXCEL_DATA_PROCESSOR_GUIDE.md)** - Excel 数据整合

#### 库 / 命令行（未集成 GUI 页签）

- **配置同步**：`core/excel_config_sync.py`（测试见 `test/test_config_sync.py`）
- **Excel 转 CSV**：`core/excel_to_csv_converter.py`

### 📋 其他资源

- **[ERROR_LOGGING_FEATURE.md](ERROR_LOGGING_FEATURE.md)** - 错误日志和诊断功能（历史：v1.25.5）
- **[BUILD_REPORT_v1.43.0.md](BUILD_REPORT_v1.43.0.md)** - 构建报告历史快照
- **[VERSION_HISTORY_ARCHIVE.md](VERSION_HISTORY_ARCHIVE.md)** - 版本历史归档
- **[MULTILANG_JSON_GUIDE.md](MULTILANG_JSON_GUIDE.md)** - 多语言 JSON 配置（历史：v1.39.5）
- **[WORKFLOW_UI_ENHANCEMENT_PLAN.md](WORKFLOW_UI_ENHANCEMENT_PLAN.md)** - 已实施 UI 方案记录（仅供考古）

---

## 📖 按功能分类

### 🎯 表字段导出 (Excel Field Extractor)

用途：从Excel表格中提取字段名和类型信息

**相关文档：**

- **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)** - 表头行、列标记与行边界统一规范
- EXCEL_FIELD_EXTRACTOR_README.md - 完整使用指南
- BATCH_MODIFIER_GUIDE.md - 批量改表配置

**快速开始：**

```bash
python gui/run_unified.py
# 在「工作台」选择各语言目录与输出路径，再进入「字段导出」页签执行
```

---

### 🌍 多语言翻译提取 (Table Range Translator)

用途：按指定字段范围提取多语言翻译内容（中文、越南语、泰语、英语）

**相关文档：**

- **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)** - 与提取器共用的 Excel 行号与边界约定
- TABLE_RANGE_TRANSLATOR_GUIDE.md - 完整功能指南
- MULTILANG_JSON_GUIDE.md - JSON配置格式说明
- MULTI_LANGUAGE_TEXT_EXTRACTOR.md - 文本提取详解

**快速开始：**

```bash
python gui/run_unified.py
# 在「工作台」配置合并 JSON 与各语言目录，再进入「多语言翻译提取」页签执行
```

---

### 🔄 批量改表 (Batch Excel Modifier)

用途：批量修改多个Excel文件，支持映射表翻译

**相关文档：**

- **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)** - 目标策划表布局约定
- BATCH_MODIFIER_GUIDE.md - 完整使用指南

**快速开始：**

```bash
python gui/run_unified.py
# 在「工作台」选择 JSON、映射表、Excel 目录与报告路径，再进入「批量改表」页签执行
```

---

### 💾 翻译缓存 (Translation Cache)

用途：加速跨项目翻译对应，通过缓存提升性能

**相关文档：**

- [CROSS_PROJECT_GUIDE.md](CROSS_PROJECT_GUIDE.md) - 跨项目翻译操作
- CACHE_SYSTEM_GUIDE.md - 缓存系统详解

---

### 🔀 跨项目翻译

**快速开始：**

```bash
python gui/run_unified.py
# 在工作台选择映射文件、扫描目录、结果文件，再进入「跨项目翻译」页执行
```

详见 [CROSS_PROJECT_GUIDE.md](CROSS_PROJECT_GUIDE.md)。

---

### 🧪 JSON 错误检测

**快速开始：**

```bash
python gui/run_unified.py
# 在工作台选择 JSON 检测目录或文件，再进入「JSON 检测」页执行
```

详见 [JSON_DETECTOR_GUIDE.md](JSON_DETECTOR_GUIDE.md)。

---

### 📊 Excel 数据处理（整合）

**快速开始：**

```bash
python gui/run_unified.py
# 在工作台选择源文件与输出目录，在「数据处理」页配置选项后执行
```

详见 [EXCEL_DATA_PROCESSOR_GUIDE.md](EXCEL_DATA_PROCESSOR_GUIDE.md)。

---

## 🛠️ 配置文件说明

### config.json

运行时配置文件，包含：

- 缓存策略
- 并行处理设置
- 日志级别

### config_export.json

字段导出配置文件，包含：

- 字段提取规则
- 语言识别配置
- 表名/字段映射

---

## 📝 版本信息

当前版本：请以 [../version.py](../version.py) 和 GUI 显示为准

近期特性（详见根目录 [README.md](../README.md)）：

- **统一工作台**：路径集中选择，各功能页只读同步
- **本地化主流程**：字段导出 → 多语言提取 → 批量改表
- **xlwings 批量改表**：默认保留 Excel 文件结构
- **并行扫描与 LRU 缓存**：跨项目翻译与目录扫描性能优化

如需查看随仓库保留的构建记录样例，可参考：[BUILD_REPORT_v1.43.0.md](BUILD_REPORT_v1.43.0.md)（历史快照，非当前版本说明）

---

## 🔗 相关资源

- **项目主目录** - [../README.md](../README.md)
- **源代码** - [../core/](../core/) 核心模块
- **GUI程序** - [../gui/](../gui/) 用户界面
- **测试** - [../test/](../test/) 测试脚本

---

## ❓ 常见问题

### Q: 如何启动工具？

**A:** 双击运行 `启动策划工具.bat` 或执行 `python gui/run_unified.py`

### Q: 支持哪些文件格式？

**A:** 策划表主要为 `.xlsx` / `.xls`；批量改表映射表另支持 `.csv`（见 [CSV_MAPPING_SUPPORT.md](CSV_MAPPING_SUPPORT.md)）

### Q: 如何使用缓存加速？

**A:** 参考 [CACHE_SYSTEM_GUIDE.md](CACHE_SYSTEM_GUIDE.md)

### Q: 遇到问题如何诊断？

**A:** 参考 [ERROR_LOGGING_FEATURE.md](ERROR_LOGGING_FEATURE.md)

---

## 📞 更新日期

- 文档最后更新：2026-06-25（补充辅助工具指南、统一活跃文档页脚）
- 对应程序版本：请以 [../version.py](../version.py) 为准
