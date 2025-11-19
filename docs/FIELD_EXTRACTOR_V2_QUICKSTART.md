# 表字段导出工具 v2.0 - 快速使用指南

## 🎯 核心功能

扫描Excel文件，提取包含文本的列的字段信息，输出为标准JSON格式。

## 📋 输出格式

### JSON格式（推荐，默认）

```json
[
  {
    "table_name": "测试表1.xlsx",
    "sheet_name": "测试表1",
    "fields": ["ID", "名称", "描述", "数值", "类型"],
    "field_count": 5
  }
]
```

**优势：**
- ✅ 标准化，易于解析
- ✅ 包含完整元数据
- ✅ 方便其他工具读取
- ✅ 支持直接复制到剪贴板

## 🚀 快速开始

### 方式1：统一GUI（最简单）

```bash
python gui/gametools_unified.py
```

1. 选择"表字段导出"页签
2. 浏览选择Excel文件夹
3. 选择JSON格式（默认）
4. 点击"开始提取"
5. 查看JSON预览
6. 点击"复制JSON"获取结果

### 方式2：独立GUI

```bash
python gui/excel_field_extractor_gui.py
```

界面功能与统一GUI相同。

### 方式3：命令行

```bash
# JSON格式（默认）
python tools/excel_field_extractor.py -d 你的Excel文件夹

# CSV格式
python tools/excel_field_extractor.py -d 你的Excel文件夹 -f csv

# Excel格式
python tools/excel_field_extractor.py -d 你的Excel文件夹 -f excel
```

### 方式4：Python代码

```python
from core.excel_field_extractor import ExcelFieldExtractor

extractor = ExcelFieldExtractor()
stats = extractor.process_directory(
    directory_path="./excel_files",
    output_format='json'
)

# 获取结果数据
results = stats['results']
for item in results:
    print(f"{item['table_name']} - {item['fields']}")
```

## 📁 输出文件

**文件名（英文）：**
- JSON: `field_extraction_result.json`
- CSV: `field_extraction_result.csv`
- Excel: `field_extraction_result.xlsx`

**默认位置：** 扫描目录（可自定义）

## 💡 使用技巧

### 1. 批量处理

```bash
# 递归扫描所有子文件夹
python tools/excel_field_extractor.py -d ./all_excels -f json

# 不递归扫描
python tools/excel_field_extractor.py -d ./single_folder --no-recursive
```

### 2. 复制JSON结果

GUI中点击"复制JSON"按钮，JSON数据立即复制到剪贴板，可以：
- 粘贴到代码编辑器
- 保存为新文件
- 发送给其他工具

### 3. 读取JSON结果

```python
import json

# 读取JSON文件
with open('field_extraction_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 处理数据
for item in data:
    table = item['table_name']
    sheet = item['sheet_name']
    fields = item['fields']
    print(f"{table}#{sheet}: {', '.join(fields)}")
```

### 4. 过滤和筛选

```python
import json

with open('field_extraction_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查找特定表
target_tables = [item for item in data if '角色' in item['sheet_name']]

# 统计字段数
total_fields = sum(item['field_count'] for item in data)
print(f"总字段数: {total_fields}")
```

## 🔧 配置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| 扫描目录 | 包含Excel文件的文件夹 | 必填 |
| 输出目录 | 结果保存位置 | 扫描目录 |
| 输出格式 | json/csv/excel | json |
| 递归扫描 | 是否扫描子文件夹 | 是 |

## ⚡ 性能

- 处理速度：约100个表/秒
- 内存占用：低（流式处理）
- 支持大文件：是

## 🎨 应用场景

### 1. API接口设计
```python
# 快速了解所有表结构，设计API
data = load_json('field_extraction_result.json')
for item in data:
    generate_api_endpoint(item['fields'])
```

### 2. 数据库设计
```python
# 根据Excel字段生成建表SQL
for item in data:
    create_sql = f"CREATE TABLE {item['sheet_name']} ("
    for field in item['fields']:
        create_sql += f"{field} VARCHAR(255), "
    create_sql += ");"
```

### 3. 文档自动生成
```python
# 生成表字段文档
for item in data:
    doc += f"## {item['table_name']}\n"
    doc += f"字段列表: {', '.join(item['fields'])}\n\n"
```

### 4. 数据验证
```python
# 验证所有表是否包含必需字段
required_fields = ['ID', '名称']
for item in data:
    missing = set(required_fields) - set(item['fields'])
    if missing:
        print(f"{item['sheet_name']} 缺少字段: {missing}")
```

## 🐛 常见问题

### Q: 为什么某些列没有被提取？
A: 只提取包含文本的列，纯数字列会被自动跳过。

### Q: 如何自定义字段行号？
A: 当前固定为第5行，可修改 `core/excel_field_extractor.py` 中的 `field_row` 变量。

### Q: JSON文件乱码怎么办？
A: 使用UTF-8编码打开，Python读取时指定 `encoding='utf-8'`。

### Q: 可以处理CSV文件吗？
A: 目前只支持 .xlsx 和 .xls 格式。

## 📊 JSON Schema

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "table_name": {"type": "string", "description": "Excel文件名"},
      "sheet_name": {"type": "string", "description": "工作表名"},
      "fields": {"type": "array", "items": {"type": "string"}},
      "field_count": {"type": "integer", "description": "字段数量"}
    },
    "required": ["table_name", "sheet_name", "fields", "field_count"]
  }
}
```

## 🔗 相关资源

- 详细文档：`docs/EXCEL_FIELD_EXTRACTOR_README.md`
- 版本更新：`docs/FIELD_EXTRACTOR_V2_UPDATE.md`
- 实现报告：`docs/FIELD_EXTRACTOR_IMPLEMENTATION_REPORT.md`

## 📞 获取帮助

```bash
# 查看命令行帮助
python tools/excel_field_extractor.py -h

# 运行测试
python test/test_field_extractor_json.py
```

---

**版本：v2.0**  
**格式：JSON（默认）**  
**文件名：英文**  
**更新：2025-11-19**
