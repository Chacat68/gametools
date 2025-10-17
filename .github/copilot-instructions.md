# GameTools AI 助手指导文档

这是一个用于游戏开发的工具集，主要用于检测和处理越南语本地化内容。本指导文档将帮助 AI 助手理解项目架构和工作流程。

## 核心架构

项目由以下主要组件构成：

### 核心模块 (`core/`)
- `localization_checker.py`: 越南语检测的核心逻辑
- `excel_vietnamese_scanner.py`: Excel 文件扫描引擎
- `vietnamese_excel_processor.py`: Excel 处理器，整合了检测和导出功能

### 工具模块 (`tools/`)
- Excel 数据处理工具
- Excel 文本提取工具
- JSON 格式检测工具

### GUI 模块 (`gui/`)
- 统一的图形界面入口
- 各工具的 GUI 实现

## 关键工作流

### 1. 越南语检测流程

```python
from core.vietnamese_excel_processor import VietnameseExcelProcessor

processor = VietnameseExcelProcessor()
stats = processor.process_directory(
    directory_path="input_folder",
    output_folder="output_folder",
    recursive=True
)
```

### 2. 文件格式支持
- Excel 文件: `.xlsx`, `.xls`
- CSV 文件: `.csv`, `.tsv`

## 项目特定约定

1. 文本类型分类：
   - "中文"
   - "越南文"
   - "中越混合"
   - "中英混合"
   - "越英混合"
   - "其他"

2. 结果输出格式：
   ```python
   {
       'excel_file': str,      # 文件名
       'sheet_name': str,      # 工作表名
       'row': int,            # 行号
       'col': int,            # 列号
       'column_name': str,    # 列名
       'content': str,        # 内容
       'language_type': str,  # 语言类型
       'position': str,       # Excel 位置引用 (例如 "A1")
       'file_path': str       # 完整文件路径
   }
   ```

## 关键文件和目录

- `/core`: 核心功能实现
- `/tools`: 命令行工具集
- `/gui`: 图形界面实现
- `/docs`: 构建报告和使用说明

## 开发工作流程

1. 功能开发
   - 在相应模块下实现功能
   - 同时提供命令行和 GUI 接口

2. 测试数据
   - 使用 `/test_excel_files` 目录进行测试
   - 通过 `tools/create_test_excel.py` 创建测试数据

## 集成要点

1. 错误处理：
   - 文件编码处理（支持 utf-8、gbk、gb2312）
   - Excel 文件格式兼容性

2. 性能考虑：
   - 大文件处理时使用分批读取
   - 支持递归扫描目录结构

## 调试指南

1. GUI 调试
   ```bash
   python gui/run_gui.py
   ```

2. 命令行调试
   ```bash
   python tools/quick_start.py
   ```

## 备注

- 使用 `pandas` 处理 Excel 文件
- 使用 `openpyxl` 进行 Excel 输出格式化
- 遵循中文编码规范和注释要求