# 表字段导出工具 - 快速开始

## 快速启动

### 方式1：使用统一GUI（推荐）
```bash
# 启动统一工具集
python gui/gametools_unified.py

# 或双击运行
gui/启动gametools.bat
```
然后在界面中选择"表字段导出"页签

### 方式2：独立GUI启动
```bash
# 启动独立界面
python gui/excel_field_extractor_gui.py

# 或双击运行
gui/启动表字段导出工具.bat
```

### 方式3：命令行使用
```bash
# 快速开始
python tools/excel_field_extractor.py -d 你的Excel文件夹路径

# 示例：扫描test_excel_files文件夹
python tools/excel_field_extractor.py -d test_excel_files
```

## 测试工具

### 1. 创建测试数据
```bash
python test/create_test_excel_for_field_extractor.py
```

### 2. 运行测试
```bash
python test/test_field_extractor.py
```

## 使用流程

### GUI使用流程：
1. 启动工具（任选上述方式之一）
2. 选择"扫描目录"（包含Excel文件的文件夹）
3. 选择"输出目录"（可选，默认为扫描目录）
4. 选择输出格式（CSV或Excel）
5. 点击"开始提取"按钮
6. 等待处理完成
7. 查看结果或打开输出文件

### 输出结果示例：

**CSV格式：**
```
表名,字段1,字段2,字段3
测试表1.xlsx#测试表1,ID,名称,描述,数值,类型
多工作表测试.xlsx#角色表,角色ID,角色名,等级,职业
```

**Excel格式：**
包含以下列：表名、工作表、字段数量、字段列表

## 主要特性

- ✅ 自动检测包含文本的列
- ✅ 从物理行第5行提取字段名
- ✅ 支持多个工作表
- ✅ 支持中文、英文、越南文等多语言
- ✅ 支持递归扫描子目录
- ✅ CSV和Excel两种输出格式

## 注意事项

1. 工具固定从Excel文件的**物理行第5行**提取字段名
2. 只提取包含**文本内容**的列（纯数字列会被跳过）
3. 支持的文件格式：`.xlsx`、`.xls`
4. 每个工作表会单独提取字段信息

## 获取帮助

- 详细文档：`docs/EXCEL_FIELD_EXTRACTOR_README.md`
- 命令行帮助：`python tools/excel_field_extractor.py -h`
- 测试示例：查看 `test/` 目录

## 故障排除

### 问题：找不到模块
**解决**：确保在项目根目录运行命令
```bash
cd d:\dev\gametools
python tools/excel_field_extractor.py -d test_excel_files
```

### 问题：输出文件为空
**检查**：
1. Excel文件中是否有包含文本的列？
2. Excel文件是否有第5行？
3. 是否选择了正确的扫描目录？

### 问题：字段名显示为"列1"、"列2"
**原因**：Excel文件行数不足5行，或第5行对应单元格为空
**解决**：确保Excel文件的第5行包含字段名

## 贡献与反馈

如有问题或建议，请通过项目Issue反馈。
