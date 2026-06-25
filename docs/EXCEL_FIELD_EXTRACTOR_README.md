# Excel表字段导出工具使用说明

行号、列范围标记（`COLUMN_MARKER`，默认 `c_`）、数据区行下限（`ROW_BOUNDARY_KEYWORD`，默认 `over`）等与全项目统一，详见 **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)**；默认数值定义在 **`core/constants.py`**。

## 功能概述

Excel表字段导出工具用于扫描指定目录下的所有 Excel 文件，检测表格中包含文本内容的列，并从 **`FIELD_NAME_ROW`（默认第 5 行）** 读取字段名、从 **`FIELD_TYPE_ROW`（默认第 6 行）** 读取字段类型，输出格式为：`表名,字段1,字段2,...`

## 主要特性

- ✅ 自动检测包含文本内容的列（跳过纯数字列）
- ✅ 从 **`FIELD_NAME_ROW`** 读取字段名，从 **`FIELD_TYPE_ROW`** 读取字段类型（与 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md) 一致）
- ✅ 支持递归扫描子目录
- ✅ 支持多个工作表
- ✅ 支持中文、英文、越南文等多语言字段名
- ✅ 输出CSV和Excel两种格式

## 使用方法

### 1. 命令行 / 代码

字段导出由 `core/excel_field_extractor.py` 提供；统一 GUI 通过 `gui/field_extractor_page.py` 调用。无独立 `tools/` 命令行入口时，请使用 GUI 或下方代码集成。

### 2. GUI界面使用（统一工作台）

```bash
python gui/run_unified.py
```

1. 在 **「工作台」** 选择各语言 Excel 目录与输出目录  
2. 进入 **「字段导出」** 页签，勾选要导出的语言，选择输出格式（建议 JSON 以便衔接多语言提取）  
3. 点击 **「开始提取」**；完成后可使用 **「用于多语言提取」** 跳转  

路径在功能页为 **只读显示**，不在页内提供浏览按钮。

### 3. 代码集成使用

```python
from core.excel_field_extractor import ExcelFieldExtractor

# 创建提取器实例
extractor = ExcelFieldExtractor()

# 处理目录
stats = extractor.process_directory(
    directory_path="./excel_files",
    output_folder="./output",
    output_format='csv',  # 或 'excel'
    recursive=True
)

# 查看统计信息
print(f"扫描文件数: {stats['total_files']}")
print(f"工作表数: {stats['total_sheets']}")
print(f"提取字段数: {stats['total_fields']}")
print(f"输出文件: {stats['output_file']}")
```

## 输出格式

### CSV格式

```csv
表名,字段1,字段2,字段3,...
测试表1.xlsx#测试表1,ID,名称,描述,数值,类型
多工作表测试.xlsx#角色表,角色ID,角色名,等级,职业
越南文测试表.xlsx#Bảng thử nghiệm,ID,Tên,Mô tả,Giá trị
```

### Excel格式

| 表名 | 工作表 | 字段数量 | 字段列表 |
| --- | --- | --- | --- |
| 测试表1.xlsx | 测试表1 | 5 | ID, 名称, 描述, 数值, 类型 |
| 多工作表测试.xlsx | 角色表 | 4 | 角色ID, 角色名, 等级, 职业 |

## 工作原理

1. **扫描目录**：遍历指定目录下的所有.xlsx和.xls文件
2. **检测文本列**：检查每一列是否包含文本内容（中文、英文、越南文等）
3. **提取字段名与类型**：在 **`FIELD_NAME_ROW`** 行提取字段名；字段类型在 **`FIELD_TYPE_ROW`** 行（详见布局规范文档）
4. **输出结果**：将结果导出为CSV或Excel格式

## 文本检测规则

工具会自动识别以下类型的文本：

- 中文字符（\u4e00-\u9fff）
- 英文字母（A-Z, a-z）
- 越南文字符（À-ỹ）

以下内容会被排除：

- 纯数字（123, 45.67等）
- 空单元格
- 游戏资源/配置标识符（「英文/数字 + 下划线」片段，如 `ass_sss_`、`ass_icon_001`）

## 字段名过滤规则

为了避免提取非翻译内容，工具会自动过滤以下字段名（不区分大小写）：

- `name` - 资源名称/代码标识符（如 `npc104_ui`, `item_001`）
- `model` - 模型ID/数字标识符（如 `0`, `1`, `100`）
- `id` - 数据ID/唯一标识符（如 `1001`, `2002`）
- `code` - 代码标识/枚举值（如 `WEAPON_TYPE_1`）
- `type` - 类型ID/分类标识（如 `1`, `2`, `TYPE_A`）

这些字段通常包含代码标识符、数字ID等非本地化内容，不应该出现在翻译字段列表中。

对以上字段名，工具会在数据区抽样检查单元格内容：**仅当出现过中文、越南文或泰文字符时才保留该列**（避免把真正的中越泰文案 `name` 列误删）；纯拉丁 ID（如 `ITEM_001`）、纯数字等仍视为代码列并过滤。

**示例**：

```text
原始字段: c_, 序号, des_cn, des_vcn, des, name, model, id, c_
过滤后: des_cn, des_vcn, des
```

如需自定义过滤规则，可修改 `core/excel_field_extractor.py` 中的 `excluded_field_names` 集合。

## 测试

### 创建测试数据

```bash
python test/create_test_excel_for_field_extractor.py
```

### 运行测试

```bash
python test/test_field_extractor.py
```

## 注意事项

1. **`FIELD_NAME_ROW`（默认第 5 行）**：从该行读取字段名；若表行数不足，会退化为「列1、列2」等形式
2. **文本检测**：只有包含文本内容的列才会被提取字段名
3. **多工作表**：每个工作表会单独提取字段信息
4. **数据区下限**：从 **`DATA_START_ROW`** 起向下扫描时，遇 **`ROW_BOUNDARY_KEYWORD`**（默认 `over`）即停止，该行及以下不参与统计（见 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)）
5. **输出文件名**：
   - CSV格式：`字段导出结果.csv`
   - Excel格式：`字段导出结果.xlsx`

## 典型应用场景

1. **数据库设计**：快速了解Excel表的字段结构
2. **文档生成**：自动生成表字段文档
3. **数据迁移**：提取源表字段信息用于数据映射
4. **项目交接**：快速了解项目中所有表的字段结构

## 常见问题

### Q: 如果表格没有字段名行（默认第 5 行）怎么办？

A: 工具会使用列号作为字段名（如「列1」「列2」）

### Q: 纯数字列会被提取吗？

A: 不会。工具只提取包含文本内容的列

### Q: 支持.csv文件吗？

A: 目前只支持.xlsx和.xls格式的Excel文件

### Q: 可以自定义字段名/类型所在行吗？

A: 全项目默认值在 **`core/constants.py`** 中的 `FIELD_NAME_ROW`、`FIELD_TYPE_ROW`、`DATA_START_ROW`；修改后字段导出与多语言提取等会一并受影响，请先阅读 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md) 并做回归验证。批量改表在 GUI 中另有可配置的「字段行」「数据起始行」，与上述常量默认对齐。

## 版本历史

- v1.27.1 (2025-11-20)
  - ✨ 新增字段名过滤功能
  - 自动过滤 name、model、id、code、type 等代码字段
  - 提高本地化字段提取的准确性

- v1.0.0 (2025-11-19)
  - 首次发布
  - 支持CSV和Excel输出格式
  - 支持递归扫描
  - 支持多语言字段名

## 并行扫描与配置

目录内多 Excel 文件的扫描会使用 `core/parallel_utils.py`，读取 `config.json` → `scan.enable_parallel`（默认 `true`）与 `scan.max_workers`（默认 `4`）。关闭并行时将回退为单线程顺序处理。

行边界检测与 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md) 一致，实现位于 `core/excel_layout_utils.py`。

首次使用请复制根目录 `config.example.json` 为 `config.json`（该文件已加入 `.gitignore`，不会提交本机窗口位置等偏好）。

## 相关文件

- **布局与常量**：[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)，`core/constants.py`，`core/excel_layout_utils.py`
- 核心模块：`core/excel_field_extractor.py`
- GUI 页签：`gui/field_extractor_page.py`
- 测试脚本：`test/test_field_extractor.py`
- 测试数据：`test/create_test_data.py`（产出在 `test/_runtime/generated/`）
