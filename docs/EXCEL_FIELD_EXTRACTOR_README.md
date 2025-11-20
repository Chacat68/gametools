# Excel表字段导出工具使用说明

## 功能概述

Excel表字段导出工具用于扫描指定目录下的所有Excel文件，检测表格中包含文本内容的列，并从物理行第5行提取字段名，输出格式为：`表名,字段1,字段2,...`

## 主要特性

- ✅ 自动检测包含文本内容的列（跳过纯数字列）
- ✅ 从物理行第5行提取字段名
- ✅ 支持递归扫描子目录
- ✅ 支持多个工作表
- ✅ 支持中文、英文、越南文等多语言字段名
- ✅ 输出CSV和Excel两种格式

## 使用方法

### 1. 命令行使用

```bash
# 基本用法
python tools/excel_field_extractor.py -d ./excel_files

# 指定输出目录
python tools/excel_field_extractor.py -d ./excel_files -o ./output

# 输出为Excel格式
python tools/excel_field_extractor.py -d ./excel_files -f excel

# 不递归扫描子目录
python tools/excel_field_extractor.py -d ./excel_files --no-recursive

# 查看帮助
python tools/excel_field_extractor.py -h
```

### 2. GUI界面使用

#### 方式1：独立启动
```bash
python gui/excel_field_extractor_gui.py
```
或双击运行：`gui/启动表字段导出工具.bat`

#### 方式2：统一GUI启动
```bash
python gui/gametools_unified.py
```
然后选择"表字段导出"页签

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
|------|--------|----------|----------|
| 测试表1.xlsx | 测试表1 | 5 | ID, 名称, 描述, 数值, 类型 |
| 多工作表测试.xlsx | 角色表 | 4 | 角色ID, 角色名, 等级, 职业 |

## 工作原理

1. **扫描目录**：遍历指定目录下的所有.xlsx和.xls文件
2. **检测文本列**：检查每一列是否包含文本内容（中文、英文、越南文等）
3. **提取字段名**：从物理行第5行提取包含文本列的单元格值作为字段名
4. **输出结果**：将结果导出为CSV或Excel格式

## 文本检测规则

工具会自动识别以下类型的文本：
- 中文字符（\u4e00-\u9fff）
- 英文字母（A-Z, a-z）
- 越南文字符（À-ỹ）

以下内容会被排除：
- 纯数字（123, 45.67等）
- 空单元格

## 字段名过滤规则

为了避免提取非翻译内容，工具会自动过滤以下字段名（不区分大小写）：

- `name` - 资源名称/代码标识符（如 `npc104_ui`, `item_001`）
- `model` - 模型ID/数字标识符（如 `0`, `1`, `100`）
- `id` - 数据ID/唯一标识符（如 `1001`, `2002`）
- `code` - 代码标识/枚举值（如 `WEAPON_TYPE_1`）
- `type` - 类型ID/分类标识（如 `1`, `2`, `TYPE_A`）

这些字段通常包含代码标识符、数字ID等非本地化内容，不应该出现在翻译字段列表中。

**示例**：
```
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

1. **物理行第5行**：工具固定从Excel文件的物理行第5行提取字段名
2. **文本检测**：只有包含文本内容的列才会被提取字段名
3. **多工作表**：每个工作表会单独提取字段信息
4. **输出文件名**：
   - CSV格式：`字段导出结果.csv`
   - Excel格式：`字段导出结果.xlsx`

## 典型应用场景

1. **数据库设计**：快速了解Excel表的字段结构
2. **文档生成**：自动生成表字段文档
3. **数据迁移**：提取源表字段信息用于数据映射
4. **项目交接**：快速了解项目中所有表的字段结构

## 常见问题

### Q: 如果表格没有第5行怎么办？
A: 工具会使用列号作为字段名（如"列1"、"列2"）

### Q: 纯数字列会被提取吗？
A: 不会。工具只提取包含文本内容的列

### Q: 支持.csv文件吗？
A: 目前只支持.xlsx和.xls格式的Excel文件

### Q: 可以自定义字段行号吗？
A: 当前版本固定为第5行，如需自定义请修改`core/excel_field_extractor.py`中的`field_row`变量

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

## 相关文件

- 核心模块：`core/excel_field_extractor.py`
- 命令行工具：`tools/excel_field_extractor.py`
- GUI界面：`gui/excel_field_extractor_gui.py`
- 测试脚本：`test/test_field_extractor.py`
- 测试数据生成：`test/create_test_excel_for_field_extractor.py`
