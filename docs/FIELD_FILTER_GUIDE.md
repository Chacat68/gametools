# 字段过滤功能说明

## 功能概述

在表字段导出工具中添加了智能字段过滤功能，自动识别并过滤掉代码字段，只保留真正需要翻译的本地化文本字段。

## 过滤对比

### 过滤前

```
表名: alpha_transparency_artifacts.xlsx
工作表: artifact
字段列表: des_cn, des_vcn, des, name, model, id
字段数量: 6
```

问题：
- ❌ `name` 字段包含代码标识符（`npc104_ui`, `npc105_ui`）
- ❌ `model` 字段包含纯数字（`0`, `1`）
- ❌ `id` 字段包含ID标识符（`1001`, `1002`）

### 过滤后

```
表名: alpha_transparency_artifacts.xlsx
工作表: artifact
字段列表: des_cn, des_vcn, des
字段数量: 3
```

优势：
- ✅ 只保留本地化文本字段（`des_cn`, `des_vcn`, `des`）
- ✅ 自动过滤代码和数字字段
- ✅ 翻译人员只需关注真正的文本内容

## 默认过滤规则

| 字段名 | 典型内容 | 过滤原因 |
|--------|----------|----------|
| `name` | `npc104_ui`, `item_sword_001` | 资源标识符/代码 |
| `model` | `0`, `1`, `100` | 模型ID/数字标识 |
| `id` | `1001`, `2002`, `ID_001` | 数据唯一标识符 |
| `code` | `WEAPON_TYPE_1`, `SKILL_A` | 枚举值/代码常量 |
| `type` | `1`, `2`, `TYPE_NPC` | 类型ID/分类标识 |

## 实际案例

### 案例1: NPC配置表

**Excel表结构**:
```
| 序号 | des_cn | des_vcn | des | name | model | id |
|------|--------|---------|-----|------|-------|-----|
| 1 | 张若 | Tiểu Long Nữ | ... | npc104_ui | 0 | 1001 |
| 2 | 黄蓉 | Hoàng Dung | ... | npc105_ui | 0 | 1002 |
```

**提取结果**:
```json
{
  "excel_file": "npc_config.xlsx",
  "sheet_name": "npc_list",
  "fields": ["des_cn", "des_vcn", "des"],
  "field_count": 3
}
```

✅ 成功过滤: `name`, `model`, `id`

### 案例2: 道具配置表

**Excel表结构**:
```
| id | type | code | name_cn | name_vcn | desc_cn | desc_vcn |
|----|------|------|---------|----------|---------|----------|
| 1001 | 1 | ITEM_001 | 长剑 | Trường Kiếm | 描述 | Mô tả |
```

**提取结果**:
```json
{
  "excel_file": "item_config.xlsx",
  "sheet_name": "items",
  "fields": ["name_cn", "name_vcn", "desc_cn", "desc_vcn"],
  "field_count": 4
}
```

✅ 成功过滤: `id`, `type`, `code`

## 技术实现

### 1. 配置过滤字段列表

```python
# core/excel_field_extractor.py
class ExcelFieldExtractor:
    def __init__(self):
        # 要过滤的字段名列表（不区分大小写）
        self.excluded_field_names = {
            'name', 'model', 'id', 'code', 'type'
        }
```

### 2. 应用过滤逻辑

```python
# 提取字段时检查并过滤
for col_num in sorted(text_columns):
    field_name = str(field_cell.value)
    
    # 过滤掉指定的字段名
    if field_name.lower() in self.excluded_field_names:
        continue  # 跳过该字段
    
    fields.append(field_name)
```

## 自定义过滤规则

如果你的项目有其他需要过滤的字段，可以修改配置：

```python
# 添加更多过滤字段
self.excluded_field_names = {
    'name', 'model', 'id', 'code', 'type',
    'icon',      # 图标资源路径
    'prefab',    # 预制体路径
    'path',      # 文件路径
    'asset',     # 资源名称
    'key',       # 键值标识
}
```

## 注意事项

1. **不区分大小写**: `Name`, `NAME`, `name` 都会被过滤
2. **基于字段名**: 只检查第5行的字段名称
3. **内容检测优先**: 只有包含本地化文本的列才会检查字段名
4. **向后兼容**: 不影响现有功能，纯粹是过滤层面的优化

## 测试验证

运行测试脚本验证过滤功能：

```bash
# 创建测试数据
python create_filter_test_excel.py

# 运行测试
python test_field_filter.py
```

预期输出：
```
✅ 过滤成功: name/model/id/code/type 字段已被过滤
字段数量: 3
字段列表: des_cn, des_vcn, des
```

## 总结

字段过滤功能帮助你：
1. 🎯 **提高准确性** - 只提取真正的本地化字段
2. 🧹 **减少噪音** - 自动过滤代码和数字字段
3. ⚡ **节省时间** - 无需手动筛选非翻译内容
4. 🔧 **灵活配置** - 可根据项目需求自定义过滤规则
