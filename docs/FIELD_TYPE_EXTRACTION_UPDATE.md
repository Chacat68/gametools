# 字段类型提取功能更新说明

## 📋 更新内容

### JSON 格式输出修改

**修改时间**: 2025年11月20日

#### 变更说明

将 `fields_with_examples` 字段的内容从"字段名+示例值"改为"字段名+字段类型"。

#### 修改前后对比

**修改前**（从第7行提取示例数据）：
```json
{
  "text_tables": [
    {
      "table_name": "npc_config.xlsx",
      "sheet_name": "npc_list",
      "fields_with_examples": [
        "des_cn,张若",
        "des_vcn,Tiểu Long Nữ",
        "des_en,Little Dragon Girl"
      ],
      "field_count": 3
    }
  ]
}
```

**修改后**（从第6行提取字段类型）：
```json
{
  "text_tables": [
    {
      "table_name": "npc_config.xlsx",
      "sheet_name": "npc_list",
      "fields_with_examples": [
        "des_cn,策划",
        "des_vcn,前端",
        "des_en,后端"
      ],
      "field_count": 3
    }
  ]
}
```

---

## 📊 JSON 格式详细说明

### 完整结构

```json
{
  "no_text_tables": [
    {
      "table_name": "Excel文件名",
      "sheet_name": "工作表名"
    }
  ],
  "text_tables": [
    {
      "table_name": "Excel文件名",
      "sheet_name": "工作表名",
      "fields_with_examples": [
        "字段名,字段类型"
      ],
      "field_count": 字段数量
    }
  ]
}
```

### 字段说明

#### no_text_tables（无文本内容的表格）
- `table_name`: Excel 文件名
- `sheet_name`: 工作表名

#### text_tables（包含文本内容的表格）
- `table_name`: Excel 文件名
- `sheet_name`: 工作表名
- `fields_with_examples`: 字段名+字段类型数组
  - 格式: `"字段名,字段类型"`
  - 字段类型来自物理行**第6行**
  - 可能的类型值: 策划、前端、后端、前后端 等
- `field_count`: 字段数量

---

## 📝 Excel 表格结构要求

### 标准表格结构

```
行号 | 列A | 列B      | 列C       | 列D     | 列E  | 列F   | 列G
-----|-----|----------|-----------|---------|------|-------|-----
1    |     | 表头说明 |           |         |      |       |
5    | c_  | des_cn   | des_vcn   | des_en  | name | model | c_
6    |     | 策划     | 前端      | 后端    |前后端| 策划  |
7    | 1   | 张若     | Tiểu Long | Little  |npc_01| 0     |
8    | 2   | 黄蓉     | Hoàng     | Huang   |npc_02| 1     |
```

### 关键行说明

| 行号 | 用途 | 说明 |
|------|------|------|
| **第5行** | 字段名 | 定义每列的字段名称 |
| **第6行** | 字段类型 | **新增提取**：策划、前端、后端、前后端等 |
| **第7行+** | 数据行 | 实际的数据内容 |

---

## ⚙️ 提取规则

### 1. 扫描范围（不变）
- 仅扫描两个 `c_` 标记之间的列
- 不包含标记列本身
- 从第7行开始检测文本内容

### 2. 字段提取（修改）
- **第5行**: 提取字段名
- **第6行**: 提取字段类型（新功能）
- 过滤字段名: name, model, id, code, type

### 3. 字段类型说明
字段类型用于标识该字段的使用方：
- **策划**: 策划专用字段
- **前端**: 前端客户端使用
- **后端**: 后端服务器使用
- **前后端**: 前后端共用字段

---

## ⚠️ 警告信息

### 字段类型为空警告

当第6行的字段类型单元格为空时，会生成警告：

```
⚠️ 字段类型为空 | 文件: test.xlsx | 工作表: Sheet1 | 字段: des_cn | 位置: 第6行,第3列(C6)
```

此时输出格式为：`"字段名,"` （字段类型为空）

---

## 🧪 测试示例

### 创建测试文件

```bash
python create_test_field_type_excel.py
```

生成的测试文件：
- `test_field_types.xlsx`: 包含完整字段类型
- `test_no_types.xlsx`: 缺失字段类型（测试警告）

### 运行测试

```bash
python test_json_format.py
```

### 预期输出

```json
{
  "no_text_tables": [],
  "text_tables": [
    {
      "table_name": "test_field_types.xlsx",
      "sheet_name": "测试表",
      "fields_with_examples": [
        "des_cn,策划",
        "des_vcn,前端",
        "des_en,后端"
      ],
      "field_count": 3
    }
  ]
}
```

---

## 💡 使用建议

### CSV 和 Excel 格式

目前修改仅影响 **JSON 格式**的输出。CSV 和 Excel 格式保持不变，继续使用 `fields_with_examples` 显示字段信息。

如需修改 CSV 和 Excel 格式，可参考 JSON 格式的修改方式进行调整。

### 字段命名约定

建议在第6行使用统一的字段类型标识：
- ✅ 策划、前端、后端、前后端
- ✅ planner, frontend, backend, both
- ❌ 避免使用不规范的标识

---

## 📌 注意事项

1. **不影响扫描逻辑**: 仅修改输出内容，扫描范围和文本检测逻辑不变
2. **向后兼容**: 如果第6行不存在或为空，不会导致程序错误，只会生成警告
3. **字段过滤**: name、model、id、code、type 等字段仍然会被过滤
4. **编码处理**: JSON 输出使用 UTF-8 编码，支持中文、越南文等多语言

---

## 🔧 代码修改位置

修改文件：`core/excel_field_extractor.py`

主要修改：
1. 第6行字段类型提取逻辑
2. 警告信息从"示例数据为空"改为"字段类型为空"
3. 变量名从 `field_with_examples` 改为 `field_with_types`
4. 注释更新

---

## ✅ 验证清单

- [x] JSON 格式输出正确
- [x] 字段类型从第6行提取
- [x] 警告信息正确显示
- [x] 字段过滤功能正常
- [x] 扫描范围不变
- [x] 测试文件创建成功
- [x] 多语言支持正常
