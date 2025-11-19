# 表字段导出工具 - v2.0 更新说明

## 更新日期
2025年11月19日

## 主要变更

### 1. 🎯 新增JSON格式输出（默认）

工具现在默认输出标准JSON格式，方便其他工具读取和解析。

**JSON输出格式：**
```json
[
  {
    "table_name": "测试表1.xlsx",
    "sheet_name": "测试表1",
    "fields": ["ID", "名称", "描述", "数值", "类型"],
    "field_count": 5
  },
  {
    "table_name": "多工作表测试.xlsx",
    "sheet_name": "角色表",
    "fields": ["角色ID", "角色名", "等级", "职业"],
    "field_count": 4
  }
]
```

### 2. 📝 输出文件名改为英文

所有输出文件名从中文改为英文，便于跨平台使用和自动化处理：

- ~~字段导出结果.json~~ → `field_extraction_result.json`
- ~~字段导出结果.csv~~ → `field_extraction_result.csv`
- ~~字段导出结果.xlsx~~ → `field_extraction_result.xlsx`

### 3. 🖥️ GUI增强功能

#### 独立GUI和统一GUI都新增：
- ✅ JSON格式选项（默认选中）
- ✅ 复制JSON结果到剪贴板按钮
- ✅ JSON结果预览显示
- ✅ 在处理日志中直接显示JSON内容

#### 操作流程：
1. 选择扫描目录
2. 选择输出格式（JSON/CSV/Excel）
3. 点击"开始提取"
4. 查看JSON预览
5. 点击"复制JSON"按钮直接复制到剪贴板

### 4. 📊 统一的数据结构

process_directory方法现在返回更完整的数据：

```python
stats = {
    'total_files': 4,
    'total_sheets': 6,
    'total_fields': 26,
    'output_file': 'path/to/field_extraction_result.json',
    'results': [...]  # 完整的结果数据数组
}
```

## 使用示例

### 命令行
```bash
# JSON格式（默认）
python tools/excel_field_extractor.py -d ./excel_files

# 指定格式
python tools/excel_field_extractor.py -d ./excel_files -f json
python tools/excel_field_extractor.py -d ./excel_files -f csv
python tools/excel_field_extractor.py -d ./excel_files -f excel
```

### Python代码
```python
from core.excel_field_extractor import ExcelFieldExtractor

extractor = ExcelFieldExtractor()
stats = extractor.process_directory(
    directory_path="./excel_files",
    output_format='json'  # 默认值
)

# 访问结果数据
results = stats['results']
for item in results:
    print(f"{item['table_name']}#{item['sheet_name']}")
    print(f"字段: {item['fields']}")
```

### GUI使用
1. 启动统一GUI：`python gui/gametools_unified.py`
2. 选择"表字段导出"页签
3. 选择JSON格式（默认）
4. 开始提取后，可以直接在界面中看到JSON预览
5. 点击"复制JSON"按钮，JSON数据即复制到剪贴板

## JSON格式优势

1. **标准化**：易于解析和处理
2. **结构化**：包含完整的元数据（表名、工作表、字段数）
3. **可扩展**：未来可添加更多字段信息
4. **跨平台**：广泛支持，易于集成
5. **易读性**：格式化输出，便于人类阅读

## 兼容性

- ✅ 保持向后兼容
- ✅ 仍支持CSV和Excel格式
- ✅ 所有现有功能继续可用
- ✅ 新增功能不影响旧代码

## 文件变更

**修改的文件：**
- `core/excel_field_extractor.py` - 新增JSON支持
- `tools/excel_field_extractor.py` - 更新默认格式
- `gui/excel_field_extractor_gui.py` - 增强GUI功能
- `gui/gametools_unified.py` - 统一GUI集成

**新增的文件：**
- `test/test_field_extractor_json.py` - JSON格式测试

**更新的文档：**
- 所有相关文档已更新为JSON格式说明

## 测试验证

已通过完整测试：
- ✅ JSON格式输出正确
- ✅ 文件名为英文
- ✅ GUI显示JSON预览
- ✅ 复制到剪贴板功能正常
- ✅ 所有格式（JSON/CSV/Excel）都可正常工作

## 升级建议

如果你在使用旧版本：
1. 无需修改代码，工具会自动使用JSON格式
2. 如需CSV格式，在GUI中选择或使用 `-f csv` 参数
3. 输出文件名自动改为英文，请更新你的文件路径引用

## 下一步

可以基于JSON格式开发更多功能：
- 字段对比工具
- 表结构文档生成
- 数据验证工具
- 自动化测试集成

---

**版本：v2.0**  
**更新时间：2025年11月19日**  
**状态：稳定版本**
