# 表字段导出工具 - 字段过滤功能更新

**更新日期**: 2025-11-20  
**版本**: v1.27.1

## 更新内容

### 新增功能：字段名过滤规则

为表字段导出工具添加了字段名过滤功能，自动过滤掉包含代码、标识符或纯数字的字段，避免将这些非翻译内容提取到本地化字段列表中。

### 实现细节

#### 1. 过滤字段列表

在 `ExcelFieldExtractor` 类中添加了 `excluded_field_names` 属性，默认过滤以下字段名（不区分大小写）：

```python
self.excluded_field_names = {'name', 'model', 'id', 'code', 'type'}
```

这些字段通常包含：
- `name`: 资源名称/代码标识符（如 `npc104_ui`, `item_001`）
- `model`: 模型ID/数字标识符（如 `0`, `1`, `100`）
- `id`: 数据ID/唯一标识符（如 `1001`, `2002`）
- `code`: 代码标识/枚举值（如 `WEAPON_TYPE_1`）
- `type`: 类型ID/分类标识（如 `1`, `2`, `TYPE_A`）

#### 2. 过滤逻辑

在字段提取循环中，检查字段名并跳过被过滤的字段：

```python
# 提取字段名
field_cell = sheet.cell(row=field_row, column=col_num)
field_name = str(field_cell.value) if field_cell.value is not None else f"列{col_num}"

# 过滤掉指定的字段名（通常包含代码、标识符或纯数字）
if field_name.lower() in self.excluded_field_names:
    continue

fields.append(field_name)
```

### 使用示例

#### 测试场景

以 `alpha_transparency_artifacts.xlsx` 为例：

**原始表结构**：
```
| c_ | 序号 | 索引1 | 索引2 | des_cn | des_vcn | des | name | model | id | c_ |
```

**过滤前**：会提取所有包含文本内容的列
```
字段列表: des_cn, des_vcn, des, name, model, id
```

**过滤后**：只提取真正的本地化文本字段
```
字段列表: des_cn, des_vcn, des
```

被过滤的字段：
- `name`: `npc104_ui`, `npc105_ui` 等（UI资源标识符）
- `model`: `0`, `1` 等（模型ID数字）
- `id`: `1001`, `1002` 等（数据ID）

### 测试验证

创建了测试脚本验证过滤功能：

```bash
# 创建测试数据
python create_filter_test_excel.py

# 运行过滤测试
python test_field_filter.py
```

**测试结果**：
```
✅ 过滤成功: name/model/id/code/type 字段已被过滤
字段数量: 3
字段列表: des_cn, des_vcn, des
```

### 优势

1. **提高准确性**：避免将代码标识符和数字ID误认为需要翻译的文本
2. **减少噪音**：输出结果更清晰，只包含真正的本地化字段
3. **节省工作量**：翻译人员不需要手动筛选掉这些非翻译字段
4. **可扩展**：可以轻松添加更多需要过滤的字段名

### 自定义过滤规则

如需添加更多过滤字段，修改 `core/excel_field_extractor.py` 中的 `excluded_field_names` 集合：

```python
self.excluded_field_names = {'name', 'model', 'id', 'code', 'type', 'icon', 'prefab', 'path'}
```

### 兼容性

- ✅ 向后兼容：不影响现有功能
- ✅ 不区分大小写：`Name`, `NAME`, `name` 都会被过滤
- ✅ 仍然基于内容检测：只有包含本地化文本的列才会被检查字段名

## 修改文件

- `core/excel_field_extractor.py` - 添加字段名过滤逻辑
- `create_filter_test_excel.py` - 测试数据生成脚本
- `test_field_filter.py` - 过滤功能测试脚本

## 下一步

建议根据实际项目需求，继续扩展 `excluded_field_names` 列表，添加更多项目特定的代码字段名。
