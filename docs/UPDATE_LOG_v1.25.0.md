# GameTools 更新日志 - v1.25.0

## 发布日期
2025年11月19日

## 新增功能

### 🎉 表字段导出工具

新增了一个强大的表字段导出工具，用于快速提取Excel文件的字段信息。

#### 主要功能
- ✅ 自动扫描目录下的所有Excel文件（支持.xlsx和.xls）
- ✅ 智能检测包含文本内容的列（中文、英文、越南文等）
- ✅ 从物理行第5行提取字段名
- ✅ 支持多个工作表的批量处理
- ✅ 支持递归扫描子目录
- ✅ 输出CSV和Excel两种格式

#### 输出格式
```
表名,字段1,字段2,字段3,...
```

#### 使用方式

**方式1：统一GUI（推荐）**
```bash
python gui/gametools_unified.py
# 选择"表字段导出"页签
```

**方式2：独立GUI**
```bash
python gui/excel_field_extractor_gui.py
# 或双击：gui/启动表字段导出工具.bat
```

**方式3：命令行**
```bash
python tools/excel_field_extractor.py -d ./excel_files -f csv
```

**方式4：代码集成**
```python
from core.excel_field_extractor import ExcelFieldExtractor

extractor = ExcelFieldExtractor()
stats = extractor.process_directory("./excel_files")
```

## 文件变更

### 新增文件
- `core/excel_field_extractor.py` - 核心提取器
- `tools/excel_field_extractor.py` - 命令行工具
- `gui/excel_field_extractor_gui.py` - 独立GUI
- `gui/启动表字段导出工具.bat` - 快速启动脚本
- `test/test_field_extractor.py` - 测试脚本
- `test/create_test_excel_for_field_extractor.py` - 测试数据生成
- `docs/EXCEL_FIELD_EXTRACTOR_README.md` - 详细文档
- `docs/FIELD_EXTRACTOR_QUICKSTART.md` - 快速开始
- `docs/FIELD_EXTRACTOR_IMPLEMENTATION_REPORT.md` - 实现报告

### 修改文件
- `gui/gametools_unified.py` - 集成新工具到统一界面

## 技术细节

### 核心算法
使用正则表达式检测文本字符：
- 中文：\u4e00-\u9fff
- 英文：A-Z, a-z
- 越南文：À-ỹ

自动排除纯数字列，确保只提取包含文本的字段。

### 数据提取
固定从Excel文件的物理行第5行提取字段名，这符合大多数游戏配置表的标准格式。

## 测试验证

已通过完整测试：
- ✅ 中文字段提取
- ✅ 越南文字段提取
- ✅ 混合类型处理
- ✅ 多工作表处理
- ✅ CSV输出格式
- ✅ Excel输出格式

测试数据：4个Excel文件，6个工作表，26个字段
处理时间：< 1秒

## 应用场景

1. **数据库设计**：快速了解Excel表的字段结构
2. **文档生成**：自动生成表字段文档
3. **数据迁移**：提取源表字段信息用于映射
4. **项目交接**：快速了解项目表结构

## 代码统计

- 新增代码：约 1,061 行
- 修改代码：约 180 行
- 文档：约 350 行
- 总计：约 1,591 行

## 兼容性

- Python 3.7+
- 依赖库：pandas, openpyxl, tkinter
- 支持格式：.xlsx, .xls
- 操作系统：Windows, Linux, macOS

## 快速开始

### 1. 创建测试数据
```bash
python test/create_test_excel_for_field_extractor.py
```

### 2. 运行测试
```bash
python test/test_field_extractor.py
```

### 3. 启动工具
```bash
python gui/gametools_unified.py
```

## 文档资源

- 📖 详细使用文档：`docs/EXCEL_FIELD_EXTRACTOR_README.md`
- 🚀 快速开始：`docs/FIELD_EXTRACTOR_QUICKSTART.md`
- 📊 实现报告：`docs/FIELD_EXTRACTOR_IMPLEMENTATION_REPORT.md`

## 注意事项

1. 工具固定从物理行第5行提取字段名
2. 只提取包含文本内容的列（纯数字列自动跳过）
3. 支持多工作表，每个工作表单独提取
4. 输出文件名固定为"字段导出结果.csv"或"字段导出结果.xlsx"

## 下一步计划

- [ ] 支持自定义字段行号
- [ ] 支持CSV文件输入
- [ ] 添加字段类型检测
- [ ] 添加字段统计分析

## 反馈与支持

如有问题或建议，请通过项目Issue反馈。

---

**版本：v1.25.0**  
**更新时间：2025年11月19日**  
**状态：稳定版本**
