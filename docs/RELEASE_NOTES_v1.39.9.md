# 批量改表CSV格式支持 - 版本 v1.39.9

## 🎉 新功能

批量改表功能现在支持 **CSV格式** 的映射表文件！

## ✨ 主要特性

### 1. 文件格式支持
- ✅ Excel 格式：`.xlsx` `.xls`（原有功能）
- ✅ CSV 格式：`.csv`（新增）

### 2. 自动编码检测
系统会自动尝试多种编码：
- UTF-8（优先）
- GBK（简体中文）
- GB2312（简体中文）
- UTF-8-sig（带BOM）

### 3. 完整功能支持
- ✅ 文件选择对话框支持 CSV
- ✅ 映射表预览支持 CSV
- ✅ 语言列自动识别支持 CSV
- ✅ 批量修改功能支持 CSV

## 📝 CSV 映射表格式示例

```csv
Table,Classification,ID,VN,TH,EN,Support-CH
armor_ancient.xlsx,des,1001,古代盔甲描述越南文,古代盔甲描述泰文,Ancient Armor Description,古代盔甲描述
armor_ancient.xlsx,name,1001,古代盔甲名称越南文,古代盔甲名称泰文,Ancient Armor Name,古代盔甲
weapon_master.xlsx,des,2001,大师武器描述越南文,大师武器描述泰文,Master Weapon Description,大师武器描述
```

## 🚀 快速使用

### 方法1：GUI界面
1. 打开批量改表页签
2. 点击"映射表文件"旁的"浏览"按钮
3. 选择 `.csv` 文件
4. 其他操作与 Excel 格式完全相同

### 方法2：代码调用
```python
from core.batch_excel_modifier import BatchExcelModifier

modifier = BatchExcelModifier()
df, columns = modifier.load_mapping_table('映射表.csv')
```

## 🎯 CSV 格式优势

| 优势 | 说明 |
|------|------|
| 🪶 轻量级 | 文件体积小，加载快 |
| 🔧 易编辑 | 任何文本编辑器可打开 |
| 🌐 通用性 | 无需 Excel 即可处理 |
| 📊 版本控制友好 | 便于 Git 追踪变更 |
| 🤖 程序友好 | 易于脚本自动生成 |

## 📚 文档

详细文档请参考：
- [CSV格式支持完整文档](docs/CSV_MAPPING_SUPPORT.md)
- [批量改表功能指南](docs/BATCH_MODIFIER_GUIDE.md)

## 🧪 测试

### 创建测试文件
```bash
python test/create_test_csv_mapping.py
```

### 运行测试
```bash
python test/test_csv_mapping.py
```

## 📦 文件变更

### 核心代码
- `core/batch_excel_modifier.py`
  - ✨ `load_mapping_table()` 支持 CSV
  - ✨ `get_mapping_sheets()` 支持 CSV
  - ✨ 新增 `supported_mapping_formats` 属性

### GUI界面
- `gui/gametools_unified.py`
  - ✨ `browse_batch_mapping_file()` 支持 CSV
  - ✨ `preview_batch_mapping()` 支持 CSV
  - ✨ `refresh_batch_languages()` 支持 CSV

### 测试脚本
- `test/create_test_csv_mapping.py` - 创建测试CSV文件
- `test/test_csv_mapping.py` - CSV加载功能测试

### 文档
- `docs/CSV_MAPPING_SUPPORT.md` - CSV格式支持文档

## ⚠️ 注意事项

1. **编码建议**：使用 UTF-8 with BOM 编码保存 CSV 文件
2. **Excel保存**：在 Excel 中选择"CSV UTF-8 (逗号分隔)"格式
3. **工作表**：CSV 不支持多工作表，需要多工作表请使用 Excel 格式
4. **兼容性**：完全向后兼容，不影响现有 Excel 格式功能

## 🔄 版本信息

- **版本号**：v1.39.9
- **发布日期**：2025-12-20
- **兼容性**：向后兼容所有旧版本

---

**如有问题或建议，请联系开发团队** 🎮
