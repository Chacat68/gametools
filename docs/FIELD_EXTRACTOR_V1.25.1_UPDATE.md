# 表字段导出工具 v1.25.1 更新说明

## 🎯 核心功能增强

### 智能字段过滤
现在工具只提取**包含本地化文本**的字段，自动忽略代码配置和纯数字列。

### 支持的语言
- ✅ **中文**：包含中文汉字的字段
- ✅ **越南文**：包含越南语字符的字段（如 ắ, ơ, ư 等）
- ✅ **泰文**：包含泰文字符的字段（如 ก, ข, ค 等）

### 自动忽略的内容
- ❌ 纯数字列（ID, 编号等）
- ❌ 纯英文代码列（player_id, item_code等）
- ❌ 配置常量列（HP_MAX, CONFIG_NAME等）
- ❌ 布尔值列（true, false）
- ❌ 其他非本地化内容

## 📊 工作原理

### 扫描范围
- 从Excel文件的**第6行**开始扫描（数据行）
- 自动检测哪些列包含本地化文本
- 从**第5行**提取对应列的字段名

### 示例

**原始表格：**
```
第1行：表标题
第2-4行：其他信息
第5行：ID | 角色名称 | player_level | 等级 | Tên nhân vật | HP_MAX
第6行：1  | 张三     | 10          | 初级  | Nguyễn A    | 100
```

**提取结果：**
```json
{
  "fields": ["角色名称", "等级", "Tên nhân vật"]
}
```

- ✅ "角色名称"：包含中文 → 提取
- ✅ "等级"：包含中文 → 提取
- ✅ "Tên nhân vật"：包含越南文 → 提取
- ❌ "ID"：数据行只有纯数字 → 忽略
- ❌ "player_level"：数据行只有纯数字 → 忽略
- ❌ "HP_MAX"：数据行只有纯数字 → 忽略

## 🧪 测试验证

### 运行测试
```bash
# 测试字段过滤逻辑
python test/test_field_filter.py

# 创建测试Excel文件
python test/create_field_filter_test_excel.py

# 测试完整提取功能
python test/test_field_extraction_filtered.py
```

### 测试覆盖
- ✅ 中文、越南文、泰文字符识别
- ✅ 纯数字、英文代码过滤
- ✅ 混合内容处理
- ✅ 空值和特殊字符处理
- ✅ 完整Excel文件提取

## 📦 使用方法

### GUI方式
1. 运行 `dist/gametools/gametools.exe`
2. 选择"表字段导出"标签页
3. 选择输入目录和输出目录
4. 点击"开始提取"
5. 查看JSON预览，可以复制到剪贴板

### 命令行方式
```bash
python tools/excel_field_extractor.py -i input_folder -o output_folder -f json
```

### 编程方式
```python
from core.excel_field_extractor import ExcelFieldExtractor

extractor = ExcelFieldExtractor()
stats = extractor.process_directory(
    directory_path="input_folder",
    output_folder="output_folder",
    output_format="json"
)

# stats包含完整的提取结果
print(stats['results'])  # 所有字段数据
```

## 🔄 版本更新

### v1.25.1 (2025-11-19)
- 🎯 智能字段过滤：只提取包含中文、越南文、泰文的字段
- 🚫 自动忽略：纯数字ID、英文代码、配置项等
- 📊 优化扫描：只检查数据行（第6行起），提高准确性
- ✅ 全面测试：24个单元测试全部通过
- 📝 完整文档：更新使用说明和工作原理

### v1.25.0 (2025-11-19)
- 📊 表字段导出工具v2.0
- 🎯 JSON格式输出
- 🌐 英文文件名
- 📋 复制JSON功能
- 🖥️ GUI完整集成

## 💡 最佳实践

### 适用场景
1. **本地化管理**：快速识别需要翻译的表格字段
2. **配置整理**：区分数据字段和配置字段
3. **文档生成**：为策划提供字段清单
4. **质量检查**：验证哪些字段包含本地化内容

### 注意事项
1. Excel文件必须至少有6行（包含数据行）
2. 第5行应该是字段名行
3. 数据从第6行开始
4. 纯英文配置表会被完全忽略

## 📚 相关文档
- `docs/FIELD_EXTRACTOR_V2_UPDATE.md` - v2.0完整更新说明
- `docs/V2_QUICKSTART.md` - 快速入门指南
- `test/` - 测试代码和测试数据

## 🆘 问题排查

### 为什么某些字段没有被提取？
检查该列的数据行（第6行以后）是否包含中文/越南文/泰文。如果只包含英文、数字，则会被忽略。

### 如何提取纯英文字段？
当前版本专注于本地化内容。如需提取所有字段，请使用 v1.24.0 或更早版本。

### 表格结构不是从第5行开始怎么办？
当前版本假定第5行为字段行。如需自定义，请修改 `core/excel_field_extractor.py` 中的 `field_row` 和 `data_start_row` 参数。
