# gametools
游戏工具集

一个集成了越南文检测和JSON格式检测工具的多功能游戏开发工具集。

## 项目结构

```
gametools/
├── core/                    # 核心功能模块
│   ├── localization_checker.py
│   └── requirements.txt
├── tools/                   # 工具脚本和模块
│   ├── json_format_detector/ # JSON格式检测工具（命令行版）
│   ├── demo.py              # 演示脚本
│   ├── quick_start.py       # 快速启动脚本
│   ├── run.bat              # 命令行启动脚本
│   └── start_gui.bat        # GUI启动脚本
├── gui/                     # GUI和打包相关文件
│   ├── gametools_unified.py # 统一界面主程序
│   ├── json_format_detector_gui.py # JSON检测GUI
│   ├── build_unified.py     # 统一版本构建脚本
│   └── ...                  # 其他GUI相关文件
├── docs/                    # 文档
│   ├── README.md
│   └── 完整使用说明.md
├── dist/                    # 输出文件目录
├── gametool.py             # 主程序
└── README.md               # 项目说明
```

## 功能特点

### 🎯 统一界面
- **多页签设计**: 将两个功能模块整合在一个界面中
- **现代化UI**: 基于tkinter的现代化图形界面
- **操作简单**: 直观的界面设计，易于使用

### 📊 越南文检测
- **批量扫描**: 检测目录下所有表格文件中的越南文
- **精确定位**: 单文件详细分析，定位越南文位置
- **递归扫描**: 支持扫描子目录
- **多格式支持**: Excel (.xlsx, .xls) 和 CSV (.csv, .tsv)
- **演示功能**: 一键创建测试文件

### 📋 JSON格式检测工具

### 📊 Excel数据处理工具
- **智能分组**: 根据A列内容自动分组数据
- **多文件输出**: 为每个A列内容创建单独的Excel文件（默认模式）
- **单文件输出**: 创建单个Excel文件包含多个工作表
- **自动文件名**: 根据A列内容自动生成文件名
- **重复检测**: 自动跳过已存在的文件
- **文件夹输出**: 支持选择输出文件夹而不是单个文件
- **汇总信息**: 可选择包含汇总统计信息
- **灵活配置**: 支持自定义分组列和工作表前缀
- **演示功能**: 一键创建测试文件
- **格式检测**: 检测JSON文件中text字段的格式一致性
- **自定义字段**: 支持设置要检测的字段名
- **详细报告**: 生成完整的检测报告
- **保存功能**: 支持保存检测结果到文件
- **多线程处理**: 界面响应流畅

## 快速开始

### 方法1: 统一界面（推荐）

```bash
# 安装依赖
pip install -r core/requirements.txt

# 运行统一界面
python gui/run_unified.py
```

或双击 `gui/启动gametools.bat`

### 方法2: 使用发布版本

1. 进入 `dist/` 目录
2. 双击 `gametools.exe`

### 方法3: 使用源码版本

```bash
# 安装依赖
pip install -r core/requirements.txt

# 启动GUI
python tools/start_gui.bat

# 或运行命令行版本
python tools/run.bat
```

## 界面说明

### 越南文检测页签
1. **选择目录**: 点击"浏览"按钮选择要扫描的目录
2. **设置选项**: 选择是否递归扫描子目录
3. **开始扫描**: 点击"开始扫描"按钮
4. **查看结果**: 在结果区域查看包含越南文的文件列表
5. **创建演示**: 点击"创建演示文件"按钮生成测试文件

### JSON格式检测工具页签
1. **选择文件**: 点击"浏览"按钮选择JSON文件
2. **设置字段**: 输入要检测的字段名（默认为"text"）
3. **开始检测**: 点击"开始检测"按钮
4. **查看结果**: 在结果区域查看详细的检测报告
5. **保存报告**: 点击"保存报告"按钮将结果保存到文件

### Excel数据处理工具页签
1. **选择文件**: 点击"浏览"按钮选择要处理的Excel文件
2. **选择输出文件夹**: 点击"浏览"按钮选择输出文件夹
3. **设置选项**: 
   - 选择输出模式（多文件/单文件）
   - 配置自动文件名生成
   - 设置分组列、工作表前缀等选项
4. **开始处理**: 点击"开始处理"按钮执行处理
5. **查看结果**: 在结果区域查看处理报告

#### 输出模式说明
- **多文件模式（默认）**: 为每个A列内容创建单独的Excel文件
- **单文件模式**: 创建单个Excel文件包含多个工作表
- **自动文件名**: 根据A列内容自动生成有意义的文件名
- **重复检测**: 自动跳过已存在的文件，避免覆盖

### 关于页签
- 显示程序版本信息
- 功能特性说明
- 使用方法和注意事项

## 测试示例

### 越南文检测测试
运行演示脚本创建测试文件：

```bash
python tools/demo.py
```

这将创建包含越南文的演示表格文件，然后使用图形界面进行测试。

### Excel数据处理工具测试
运行Excel工具演示脚本：

```bash
# 创建测试数据
python tools/create_test_excel.py

# 运行演示
python tools/demo_excel_data_processor.py

# 或使用GUI界面
python tools/excel_data_processor_gui.py
```

这将创建包含分组数据的测试Excel文件，演示多文件输出功能。

## 打包成exe文件

### 自动构建

```bash
# 运行构建脚本
python gui/build_unified.py
```

或双击 `gui/构建exe.bat`

### 构建结果

构建完成后会生成：
- `dist/gametools_v1.4.0.exe` - 主程序（带版本号）
- `dist/gametools.exe` - 主程序（兼容性版本）
- `dist/gametools_v1.4.0_便携版/` - 便携版包（带版本号）
- `dist/gametools_便携版/` - 便携版包（兼容性版本）

## 系统要求

- Python 3.7+
- Windows 10/11（推荐）
- 支持的操作系统：Windows, macOS, Linux

## 依赖包

- tkinter (通常随Python安装)
- pandas (数据处理)
- openpyxl (Excel文件处理)
- PyInstaller (用于打包)

## 工具目录

### 📁 tools/excel_data_processor/
Excel数据拆分和整合工具

- **智能分组**: 根据A列（或指定列）内容自动分组数据
- **多文件输出**: 为每个分组创建独立的Excel文件（默认模式）
- **单文件输出**: 创建单个Excel文件包含多个工作表
- **自动文件名**: 根据分组内容自动生成有意义的文件名
- **重复检测**: 自动跳过已存在的文件，避免意外覆盖
- **文件夹输出**: 支持选择输出文件夹而不是单个文件
- **汇总信息**: 每个文件包含独立的汇总统计信息
- **灵活配置**: 支持自定义分组列和工作表前缀
- **GUI界面**: 提供友好的图形化界面
- **命令行支持**: 支持批量处理和自动化

**快速开始：**
```bash
# GUI界面
python tools/excel_data_processor_gui.py

# 命令行模式
python tools/excel_data_processor.py input.xlsx output_folder

# 演示功能
python tools/demo_excel_data_processor.py
```

**功能特性：**
- 支持Excel文件格式：.xlsx, .xls
- 自动文件名生成和重复检测
- 多线程处理，界面响应流畅
- 完整的错误处理和日志记录
- 支持大文件处理

详细说明请查看 [tools/excel_data_processor/README.md](tools/excel_data_processor/README.md)

### 📁 tools/json_format_detector/
JSON文件text字段格式检测工具（命令行版本）

- 自动分析JSON文件中指定字段的格式模式
- 检测与通用格式不一致的内容
- 支持多种格式特征检测（长度、行数、空格、换行符等）
- 生成详细的检测报告
- 支持嵌套JSON结构

**快速开始：**
```bash
cd tools/json_format_detector
python detect_format.py example_data.json
```

详细说明请查看 [tools/json_format_detector/README.md](tools/json_format_detector/README.md)

### 📁 gui/
JSON文件text字段格式检测工具（图形界面版本）

- 🖥️ 直观的图形界面，操作简单
- 📁 文件浏览和选择功能
- 🔍 自定义检测字段名
- 📊 实时显示检测结果
- 💾 保存检测报告到文件
- ⚡ 多线程处理，界面响应流畅
- 📦 可打包成独立的exe文件

**快速开始：**
```bash
cd gui
python run_gui.py
```

**打包成exe：**
```bash
cd gui
python build.py
```

详细说明请查看 [gui/README.md](gui/README.md)

### 📁 dist/
输出文件目录

- 存放构建生成的exe文件
- 包含主程序和便携版包
- 可直接分发给用户使用

**文件说明：**
- `gametools_v1.4.0.exe` - 主程序（带版本号，推荐使用）
- `gametools.exe` - 主程序（兼容性版本）
- `gametools_v1.4.0_便携版/` - 便携版包（带版本号，推荐使用）
- `gametools_便携版/` - 便携版包（兼容性版本）

## 使用技巧

1. **多线程处理**: 所有检测操作都在后台线程中执行，不会阻塞界面
2. **实时反馈**: 界面会实时显示操作进度和结果
3. **错误处理**: 完善的错误提示和异常处理
4. **结果保存**: JSON检测结果可以保存为文本文件

## 注意事项

1. 确保文件格式正确
2. 大文件处理可能需要较长时间
3. 建议在检测前备份重要文件
4. 首次运行可能需要管理员权限

## 文档

- **快速开始**: 查看本README文件
- **完整说明**: 查看 [docs/完整使用说明.md](docs/完整使用说明.md)
- **详细文档**: 查看 `docs/` 目录

## 版本信息

- 版本: v1.4.0
- 开发日期: 2024年
- 支持语言: 中文界面
- 目标用户: 游戏策划人员和开发人员

### 更新历史
- **v1.4.0** (2024年12月): 添加统一的版本号管理系统，优化GUI界面版本显示，打包文件名包含版本号，优化界面大小以显示所有内容
- **v1.3.0** (2024年10月): Excel数据拆分工具多文件输出功能
- **v1.2.0** (2024年10月): Excel工具自动文件名生成和重复检测功能
- **v1.1.0** (2024年10月): Excel工具文件夹输出功能
- **v1.0.0** (2024年10月): 初始版本，包含越南文检测和JSON格式检测工具

## 技术支持

如有问题或建议，请联系开发团队。

---

**gametools**  
版权所有 © 2024