# 批量改表功能 - CSV格式支持

## 概述

从版本 v1.36.5 开始，批量改表功能新增对 **CSV格式映射表** 的支持。除了原有的 Excel 格式（.xlsx/.xls），现在也可以使用 CSV 文件作为映射表。

## 功能特性

### ✅ 支持的文件格式

- **Excel 格式**：`.xlsx` `.xls`（完整支持，包括多工作表）
- **CSV 格式**：`.csv`（新增支持）

### 🎯 CSV 格式优势

1. **轻量级**：文件体积小，加载速度快
2. **通用性**：可被任何文本编辑器和表格软件打开
3. **版本控制友好**：纯文本格式，便于 Git 等版本控制系统追踪变更
4. **跨平台**：无需安装 Excel 即可编辑
5. **程序生成友好**：易于通过脚本自动生成

## CSV 映射表格式

### 标准列结构

```csv
Table,Classification,ID,VN,TH,EN,Support-CH
armor_ancient.xlsx,des,1001,古代盔甲描述越南文,古代盔甲描述泰文,Ancient Armor Description,古代盔甲描述
armor_ancient.xlsx,name,1001,古代盔甲名称越南文,古代盔甲名称泰文,Ancient Armor Name,古代盔甲
weapon_master.xlsx,des,2001,大师武器描述越南文,大师武器描述泰文,Master Weapon Description,大师武器描述
```

### 列说明

| 列名 | 说明 | 必填 |
|------|------|------|
| `Table` | Excel 表名（带扩展名） | ✅ |
| `Classification` | 字段分类（如 des、name） | ✅ |
| `ID` | 数据行ID | ✅ |
| `VN` / `TH` / `EN` 等 | 各语言内容列 | ⚠️ 至少一个 |

## 使用方法

### 1. GUI 界面使用

1. 在 **「工作台」** 选择 **映射表文件**（支持 `.csv`）
2. 打开 **批量改表** 页签，确认映射表路径已只读显示
3. 点击 **「预览映射」**；系统会自动识别并加载语言列
4. 其余步骤与 Excel 格式映射表相同（见 [BATCH_MODIFIER_GUIDE.md](BATCH_MODIFIER_GUIDE.md)）

### 2. 代码调用

```python
from core.batch_excel_modifier import BatchExcelModifier

modifier = BatchExcelModifier()

# 加载CSV映射表（与Excel用法完全相同）
df, columns = modifier.load_mapping_table('映射表.csv')

# 其他操作与Excel格式一致
# ...
```

## 编码处理

### 自动编码检测

系统会自动尝试多种编码格式读取 CSV 文件：

1. `utf-8`（优先）
2. `gbk`（简体中文）
3. `gb2312`（简体中文）
4. `utf-8-sig`（带BOM的UTF-8）

### 推荐编码

- **创建新文件**：使用 `UTF-8 with BOM`（Excel可直接识别）
- **纯英文**：使用 `UTF-8`
- **中文内容**：使用 `UTF-8 with BOM` 或 `GBK`

### Excel 保存为 CSV 注意事项

如果使用 Excel 保存 CSV，默认编码可能是 ANSI/GBK：
- **Excel 2016+**：另存为时选择"CSV UTF-8 (逗号分隔)"
- **旧版 Excel**：保存后可能需要用记事本转换编码

## 功能对比

| 功能 | Excel 格式 | CSV 格式 |
|------|-----------|----------|
| 数据加载 | ✅ | ✅ |
| 语言列识别 | ✅ | ✅ |
| 预览功能 | ✅ | ✅ |
| 批量修改 | ✅ | ✅ |
| 多工作表 | ✅ | ❌（CSV无工作表概念） |
| 格式保留 | ✅（颜色、批注等） | ⚠️（纯文本） |
| 文件体积 | 较大 | 小 |
| 打开速度 | 慢 | 快 |

## 测试示例

### 创建测试 CSV

使用仓库内示例或自行准备：

- 格式参考：`test/测试映射表.csv`
- 生成更多样例：`python test/create_test_data.py`（产出在 `test/_runtime/generated/`）

### 验证功能

```bash
python test/test_csv_mapping.py
```

## 技术细节

### 实现位置

- **核心逻辑**：`core/batch_excel_modifier.py`
  - `load_mapping_table()` - 支持 CSV 和 Excel
  - `get_mapping_sheets()` - CSV 返回空列表
  - `supported_mapping_formats` - 新增属性

- **GUI 界面**：`gui/batch_modifier_page.py`（路径在工作台选择；预览与语言列刷新由该页实现）

### 兼容性

- ✅ 向后兼容：原有 Excel 格式功能不受影响
- ✅ 混合使用：可在同一项目中混用 CSV 和 Excel
- ✅ 自动识别：系统根据文件扩展名自动选择处理方式

## 常见问题

### Q1: CSV 文件中文显示乱码？

**A**: 使用 UTF-8 with BOM 编码保存，或在 Excel 中选择"CSV UTF-8"格式。

### Q2: CSV 能使用多个工作表吗？

**A**: CSV 不支持工作表概念。如需多工作表，请使用 Excel 格式或拆分为多个 CSV 文件。

### Q3: CSV 和 Excel 映射表可以混用吗？

**A**: 可以，但建议在同一批次中保持格式统一。

### Q4: CSV 文件大小有限制吗？

**A**: 理论上无限制，但建议单文件不超过 10MB（约20万行）以保证性能。

### Q5: 如何快速将 Excel 转换为 CSV？

**A**: Excel → 另存为 → CSV UTF-8 (逗号分隔) (*.csv)

## 更新日志

- **v1.36.5** (2025-12-20)
  - ✨ 新增 CSV 格式映射表支持
  - ✨ 自动编码检测（支持 UTF-8/GBK/GB2312）
  - ✨ GUI 文件选择器支持 CSV
  - ✨ 预览功能支持 CSV
  - ✨ 语言列刷新支持 CSV

## 示例文件

参考 `test/测试映射表.csv` 查看标准格式示例。

---

**文档版本**：与 [../version.py](../version.py) 同步维护  
**最后更新**：2026-06-25
