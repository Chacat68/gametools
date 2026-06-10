# 批量改表工具使用说明

目标表行号、字段类型行、数据起始行及行边界关键字与全项目一致，详见 **[EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)**（`core/constants.py`：`FIELD_NAME_ROW`、`FIELD_TYPE_ROW`、`DATA_START_ROW`、`ROW_BOUNDARY_KEYWORD` 等）。

## 功能概述

批量改表工具用于根据映射表（如分页Excel）批量修改多个Excel文件中的内容。通过配置表名列、ID列，结合JSON配置文件自动匹配需要修改的字段，可以精确地将映射表中的新值更新到目标Excel文件中。

## 图形界面

统一 GUI 中「批量改表」页签由 `gui/batch_modifier_page.py` 承载（工作台与各页共用路径型变量）；批量写入与 xlwings 编排仍由 `core/batch_excel_modifier.py` 实现。

## 使用场景

1. **多语言内容更新**: 根据翻译对照表批量更新游戏配置表中的多语言文本
2. **批量数据修正**: 根据修订清单批量修正多个配置表中的数据
3. **配置同步**: 将修改汇总表中的变更同步到多个目标表

## 核心特性

### JSON配置自动匹配（v1.30.0新增）

- **自动字段匹配**: 根据JSON配置文件中定义的 `fields` 和 `fields_with_examples` 自动确定需要修改的字段
- **智能过滤**: 只修改JSON配置中定义的字段，映射表中的其他列会被忽略
- **内容过滤**: 映射表语言列中的资源标识符（如 `ass_icon_001`）等非文案值会被跳过，规则见 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md) 与 `core/text_patterns.py`
- **配置复用**: 使用与其他工具（如字段提取器）相同的JSON配置文件

## 文件格式说明

### 映射表格式

映射表是一个Excel文件，包含要修改的信息：

| A列 (表名) | B列 | C列 (ID) | D列 (VN内容) | E列 | ... |
|------------|-----|----------|--------------|-----|-----|
| act_xxx.xlsx | des | 1080601 | 新越南文内容1 | ... | ... |
| act_xxx.xlsx | des | 1090601 | 新越南文内容2 | ... | ... |
| other.xlsx | des | 2001 | 新越南文内容3 | ... | ... |

**关键列说明**:
- **表名列**: 存储目标Excel文件名（如 `act_20206_shilian_0.xlsx`）
- **ID列**: 存储用于定位目标行的唯一标识（对应目标表的A列）
- **修改列**: 存储要更新的新值（列名需与JSON配置中的字段名一致）

### 目标Excel格式

目标 Excel 与字段导出 / 多语言提取共用布局，见 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)。摘要：

| Excel 行（默认） | 常量 | 说明 |
|------------------|------|------|
| 第 1–4 行 | — | 说明/预留，工具一般不解析 |
| 第 5 行 | `FIELD_NAME_ROW` | 字段名行 |
| 第 6 行 | `FIELD_TYPE_ROW` | 字段类型行 |
| 第 7 行起 | `DATA_START_ROW` | 数据行；向下遇 `ROW_BOUNDARY_KEYWORD`（默认 `over`）即停止遍历 |

**示例**:
```
A       | B    | C         | D     | E   | F
--------|------|-----------|-------|-----|-----
表名    |      |           |       |     |     <- 第1行
xxx     |      |           |       |     |     <- 第2-4行
id      | name | VN        | EN    | ... |     <- FIELD_NAME_ROW（字段名）
前后端  | 前端 | 前端       | 前端  | ... |     <- FIELD_TYPE_ROW（字段类型）
1080601 | 项目1| 越南文内容 | Eng...|     |     <- DATA_START_ROW 起（数据）
```

### JSON配置文件（必须）

JSON配置文件用于定义每个表需要修改的字段：

```json
{
  "text_tables": [
    {
      "table_name": "act_xxx.xlsx",
      "sheet_name": "Sheet1",
      "fields": ["VN", "EN"],
      "fields_with_examples": [
        "Support-CH,前端"
      ]
    }
  ]
}
```

**字段匹配规则**:
- `fields` 数组中的所有字段名会被匹配
- `fields_with_examples` 数组中的字段名（逗号前的部分）也会被匹配
- 只有同时出现在 JSON 配置和映射表中的字段才会被修改

## 操作步骤

### 1. 选择JSON配置文件
点击"浏览"选择JSON配置文件，该文件定义了每个表需要修改的字段。
点击"预览配置"可以查看JSON中的表和字段配置。

### 2. 选择映射表文件
点击"浏览文件"选择映射表Excel文件（如 `p9-3t_分页.xlsx`）

### 3. 选择工作表
如果映射表有多个工作表，选择包含修改数据的工作表（留空使用第一个工作表）

### 4. 选择Excel目录
选择包含要修改的Excel文件的目录

### 5. 配置列

- **表名列**: 映射表中存储目标文件名的列（默认"表名"）
- **ID列**: 映射表中存储行ID的列（默认"ID"）

### 6. 设置选项

- **创建备份**: 建议勾选，修改前会创建 `.bak` 备份文件

### 7. 开始修改

点击"开始修改"按钮，确认后开始批量修改

### 8. 查看结果

- 查看处理日志了解修改详情
- 查看生成的修改报告（Excel格式）

## 注意事项

1. **备份重要**: 建议始终开启备份选项
2. **ID唯一性**: 确保映射表中的ID能在目标表中唯一匹配到行
3. **列名一致性**: 映射表的列名需要与JSON配置中的字段名一致
4. **文件格式**: 目标 Excel 须符合 [EXCEL_TABLE_LAYOUT.md](EXCEL_TABLE_LAYOUT.md)（默认 `FIELD_NAME_ROW` 为字段名行，`DATA_START_ROW` 起为数据；批量改表 GUI 中的「字段行」「数据起始行」与上述常量默认一致，可按表调整）
5. **表名匹配**: JSON配置中的 `table_name` 需要与映射表中的表名一致

## 输出报告

修改完成后会生成Excel报告，包含：

1. **修改记录页**: 详细的每条修改记录
   - 文件名
   - ID
   - 字段名
   - Excel位置
   - 原值
   - 新值

2. **统计信息页**: 处理统计
   - 映射表总行数
   - 已处理行数
   - 跳过行数（表名不在JSON配置中）
   - 修改的文件数
   - 修改的单元格数
   - 错误数

3. **错误日志页**（如有错误）: 详细的错误信息

## 示例

### 示例1: 基本使用

假设有JSON配置文件 `config.json`:
```json
{
  "text_tables": [
    {
      "table_name": "item.xlsx",
      "fields": ["VN", "EN"],
      "fields_with_examples": []
    }
  ]
}
```

映射表 `mapping.xlsx`:
| 表名 | 分类 | ID | VN | EN | CH |
|------|------|-----|-----|-----|-----|
| item.xlsx | des | 1001 | Vũ khí mới | New weapon | 新武器 |
| item.xlsx | des | 1002 | Giáp mới | New armor | 新盔甲 |

配置：
- JSON配置: `config.json`
- 表名列: `表名`
- ID列: `ID`

执行后，`item.xlsx` 中 ID 为 1001 和 1002 的行：
- **VN 和 EN 列被更新**（在JSON配置中定义）
- **CH 列保持不变**（不在JSON配置中）

### 示例2: 使用 fields_with_examples

JSON配置:
```json
{
  "text_tables": [
    {
      "table_name": "item.xlsx",
      "fields": ["VN"],
      "fields_with_examples": ["Support-CH,前端"]
    }
  ]
}
```

此时 `VN` 和 `Support-CH` 两列都会被修改。
