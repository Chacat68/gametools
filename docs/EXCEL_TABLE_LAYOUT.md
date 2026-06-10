# 策划 Excel 表布局统一规范

本仓库中**字段导出**、**多语言提取**、**批量改表**、**配置同步**等工具共用同一套表头与数据区约定。行号与列标记的**唯一代码来源**为 `core/constants.py`；修改默认布局时请先改常量，再回归相关测试。

## 行号（Excel 物理行，1-based）

| 常量 | 默认行号 | 含义 |
|------|----------|------|
| `FIELD_NAME_ROW` | 5 | 字段名/列名（英文名等） |
| `FIELD_TYPE_ROW` | 6 | 字段类型：`策划`、`前端`、`后端`、`前后端` |
| `DATA_START_ROW` | 7 | 首行数据（表头之下） |

第 1–4 行一般为说明或预留，各工具**不依赖**其具体内容。

## pandas 行索引（0-based）

读入 `DataFrame` 后，与上表对应关系为「物理行号 − 1」：

| 常量 | 默认索引 | 对应物理行 |
|------|----------|------------|
| `FIELD_NAME_ROW_INDEX` | 4 | `FIELD_NAME_ROW` |
| `FIELD_TYPE_ROW_INDEX` | 5 | `FIELD_TYPE_ROW` |
| `DATA_START_ROW_INDEX` | 6 | `DATA_START_ROW` |

多语言提取器（`TableRangeTranslator`）在 `DataFrame` 上遍历数据时使用 `DATA_START_ROW_INDEX`。

## 列范围标记

| 常量 | 默认值 | 说明 |
|------|--------|------|
| `COLUMN_MARKER` | `c_` | 在**字段名行**上，单元格**值严格等于**该字符串的列视为「左右边界标记」；两标记之间的列参与字段扫描。 |

注意：字段名以 `c_` 开头（如 `c_story`）的列是**数据列**，因整格值不等于单独的 `c_`，不会被误判为边界。

## 字段类型与导出策略

| 常量 | 说明 |
|------|------|
| `EXPORTABLE_FIELD_TYPES` | `前端`、`后端`、`前后端`：参与翻译导出 |
| `SKIP_FIELD_TYPE` | `策划`：跳过 |

## 数据区行下限边界（结束遍历）

| 常量 | 默认值 | 规则 |
|------|--------|------|
| `ROW_BOUNDARY_KEYWORD` | `over` | 从 `DATA_START_ROW`（或 pandas 的 `DATA_START_ROW_INDEX`）起**向下**扫描数据区时，若某一行的**任意单元格**在去掉首尾空白后、按**小写**比较等于该字符串，则该行视为**数据区下限边界行**。 |

**遍历语义（必须遵守）：**

1. **边界行本身**不作为数据解析（不导出、不写入翻译总表等）。
2. **边界行以下的所有行**均不再遍历：一旦检测到边界行，当前「按行向下」的循环应立即 **`break`**，结束遍历。
3. 实现上通常先用 `_find_boundary_row` 将 `range` 上界缩到边界行索引之前，再在循环首部用 `_check_row_boundary` 做一次防御性判断，避免上界计算与表内容不一致时越过边界。

**公共实现**：openpyxl 与 pandas 两套边界检测已统一到 `core/excel_layout_utils.py`，字段导出与多语言提取通过该模块调用，避免逻辑漂移。

该约定与 `FIELD_NAME_ROW`、列标记 `COLUMN_MARKER` 相互独立。

## 单元格内容过滤（全工具统一）

策划表数据区中，下列内容**不应**视为待翻译文案。规则由 `core/text_patterns.py` 统一定义，各工具通过 `is_translatable_text()` / `is_filterable_content()` 调用，**勿在业务模块重复实现**。

| 类型 | 示例 | 说明 |
|------|------|------|
| 纯数字 | `1001`, `0.5` | 配置数值 |
| 空括号/数组占位 | `{}`, `[2,99]` | 结构化占位 |
| 配置关键字 | `null`, `true` | 非文案 |
| 游戏资源标识符 | `ass_sss_`, `ass_icon_001`, `npc104_ui` | 「英文/数字 + 下划线」片段 |

**已接入的工具：**

- 字段导出（`excel_field_extractor.py`）：列文本检测、排除名字段抽样
- 多语言翻译提取（`table_range_translator.py`）：提取与语言分类
- 批量改表（`batch_excel_modifier.py`）：映射表写入时跳过非文案值

## 相关文档与代码

- **规范全文（本文档）**：`docs/EXCEL_TABLE_LAYOUT.md`
- 常量定义：`core/constants.py`
- 对外再导出：`core/__init__.py`
- 字段导出：`core/excel_field_extractor.py`
- 多语言提取：`core/table_range_translator.py`
- 批量改表：`core/batch_excel_modifier.py`（GUI 默认值与 `FIELD_NAME_ROW` / `DATA_START_ROW` 一致）
- 配置同步：`core/excel_config_sync.py`（跳过列映射依赖 `FIELD_NAME_ROW`）
- 多语言提取详细流程：`docs/TABLE_RANGE_TRANSLATOR_GUIDE.md`
- 批量改表：`docs/BATCH_MODIFIER_GUIDE.md`
- 字段导出说明：`docs/EXCEL_FIELD_EXTRACTOR_README.md`
- 字段过滤：`docs/FIELD_FILTER_GUIDE.md`
- 单元格内容过滤规则：`core/text_patterns.py`（`is_translatable_text` / `is_asset_identifier`）
