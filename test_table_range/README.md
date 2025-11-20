# 表范围翻译提取器测试文件

## 测试文件说明

### Excel测试文件

1. **角色配置.xlsx**
   - 工作表: 角色列表
   - 字段: id(策划), name_cn(前端), name_vn(前端), name_th(前端), desc_cn(后端), model(策划)
   - 预期导出: name_cn, name_vn, name_th, desc_cn（跳过id和model）

2. **物品配置.xlsx**
   - 工作表: 物品列表
   - 字段: item_id(策划), item_name_cn(前端), item_name_vn(前端), item_desc(前后端), price(后端)
   - 预期导出: item_name_cn, item_name_vn, item_desc, price（跳过item_id）

3. **任务配置.xlsx**
   - 工作表: 任务列表
   - 字段: quest_id(策划), quest_title(前端), quest_desc(前后端), reward(策划)
   - 预期导出: quest_title, quest_desc（跳过quest_id和reward）

### JSON配置文件

**field_config.json**
- 包含 no_text_tables（跳过）和 text_tables（处理）
- 每个表格的字段名和字段类型配置

## 使用方法

### 命令行测试
```bash
python core/table_range_translator.py field_config.json test_table_range --output 翻译总表.xlsx
```

### GUI测试
1. 启动GUI: `python gui/gametools_unified.py`
2. 选择"表范围翻译提取"页签
3. 选择JSON配置: test_table_range/field_config.json
4. 选择Excel目录: test_table_range/
5. 选择输出文件: 翻译总表.xlsx
6. 点击"开始提取"

## 预期结果

生成的翻译总表应包含3个工作表:
- 角色配置
- 物品配置
- 任务配置

每个工作表包含列:
- 字段名
- 字段类型
- ID
- 行号
- 中文内容
- 越南文
- 泰文
- 语言类型

## 功能特点

✓ 自动跳过 no_text_tables
✓ 只导出前端、后端、前后端字段
✓ 忽略策划字段
✓ 按表格分工作表
✓ 支持中文、越南文、泰文识别
