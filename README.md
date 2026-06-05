# gametools

游戏工具集

一个集成了策划本地化、跨项目翻译对应、JSON 检测、Excel 处理、翻译提取、批量改表等功能的多功能游戏开发工具集。

## 🚀 当前版本

当前版本请以 [version.py](version.py) 和程序界面显示为准。

**最新特性：**

- ✨ **xlwings 引擎支持**：使用 Excel 原生引擎修改文件，完全保留文件结构
- ⚡ **并行处理**：多文件处理速度提升 3–5 倍
- 🧠 **智能缓存**：LRU 策略，命中率可达 70–90%
- 🛡️ **增强错误处理**：友好的错误消息和修复建议
- 📈 **进度跟踪**：实时进度和 ETA 显示

## 项目结构

```text
gametools/
├── core/                    # 核心功能模块
│   ├── batch_excel_modifier.py   # 批量 Excel 修改器
│   ├── cache_manager.py          # 缓存管理系统
│   ├── config_manager.py         # 配置管理器
│   ├── cross_project_translator.py       # 跨项目翻译工具
│   ├── cross_project_translator_cached.py # 增强版翻译工具（支持缓存）
│   ├── excel_config_sync.py      # Excel 配置同步器
│   ├── excel_field_extractor.py  # 表字段导出器
│   ├── excel_sheet_splitter.py   # Excel 工作表拆分器
│   ├── excel_to_csv_converter.py # Excel 转 CSV 转换器
│   └── table_range_translator.py # 多语言翻译提取器
├── tools/                   # 工具脚本和模块
│   ├── json_error_detector/      # JSON 错误检测核心模块
│   ├── excel_data_processor.py   # Excel 数据处理脚本
│   └── excel_sheet_splitter.py   # 分页拆分命令行入口
├── gui/                     # GUI 和打包相关文件
│   ├── gametools_unified.py      # 统一界面主程序
│   ├── build_unified.py          # 统一版本构建脚本
│   └── run_unified.py            # GUI 启动脚本
├── test/                    # 测试文件夹
│   ├── test_*.py                 # 功能测试脚本
│   ├── create_test_data.py       # 测试数据生成工具
│   ├── run_all_tests.py          # 运行所有测试脚本
│   ├── test_config_sync/         # 随仓库提交的最小配置夹具
│   ├── test_multi_lang/          # 随仓库提交的最小配置夹具
│   └── README.md                 # 测试文档
├── test_config_sync/        # 配置同步测试运行时工作目录（按需生成）
├── test_multi_lang/         # 多语言测试运行时工作目录（按需生成）
├── test_output/             # 测试运行输出目录（按需生成）
├── docs/                    # 文档目录
├── dist/                    # 输出文件目录
└── README.md               # 项目说明
```

## 📸 界面示意

![GameTools 主界面](docs/images/screenshot_main.png)

*当前仓库展示的是新版工作台示意图。由于自动化环境无法抓取交互桌面，实际运行界面请以程序启动结果为准。*

## 功能特点

### 🎯 统一界面

- **多页签设计**：将多个功能模块整合在一个界面中
- **工作台路径同步**：「工作台」页集中选择常用目录与文件路径；各功能页以 **纯文本** 同步显示同一路径（空路径显示「暂无」），不再提供本页内的「浏览/选择」按钮。
- **现代化 UI**：基于 tkinter 的现代化图形界面
- **操作简单**：直观的界面设计，易于使用

### 📋 JSON 错误检测工具

- **语法错误检测**：检测尾随逗号、单引号、注释等 JSON 标准不允许的语法
- **编码错误检测**：检测文件编码问题
- **详细报告**：生成完整的检测报告
- **保存功能**：支持保存检测结果到文件
- **多线程处理**：界面响应流畅

### 📊 Excel 数据处理工具

- **智能分组**：根据 A 列内容自动分组数据
- **多文件输出**：为每个 A 列内容创建单独的 Excel 文件（默认模式）
- **单文件输出**：创建单个 Excel 文件包含多个工作表
- **自动文件名**：根据 A 列内容自动生成文件名
- **重复检测**：自动跳过已存在的文件
- **文件夹输出**：支持选择输出文件夹而不是单个文件
- **汇总信息**：可选择包含汇总统计信息
- **灵活配置**：支持自定义分组列和工作表前缀
- **演示功能**：一键创建测试文件

### 📑 表字段导出工具

- **智能提取**：自动检测包含本地化文本的列，从 **`FIELD_NAME_ROW`（默认第 5 行）** 读取字段名
- **字段过滤**：自动过滤 `name`、`model`、`id`、`code`、`type` 等代码字段
- **多语言目录**：在「表字段导出」页签可为中文、越南语、泰语、英语分别指定目录并独立勾选是否导出
- **精准识别**：只保留真正需要翻译的文本字段（如 `des_cn`、`des_vcn`）
- **列范围标记**：识别两个 **`COLUMN_MARKER`**（默认 `c_`）之间的列；数据区遇 **`ROW_BOUNDARY_KEYWORD`**（默认 `over`）即停止向下扫描（详见 [docs/EXCEL_TABLE_LAYOUT.md](docs/EXCEL_TABLE_LAYOUT.md)）
- **多格式输出**：支持 CSV、Excel、JSON 三种输出格式
- **递归扫描**：支持批量处理目录下所有 Excel 文件
- **详细报告**：包含字段列表、示例数据、统计信息
- **已集成**：已合并到统一界面的「表字段导出」页签

### 🌐 多语言翻译提取工具

- **智能配置**：根据字段导出的 JSON 配置，自动提取多语言翻译内容
- **字段类型筛选**：只导出 `EXPORTABLE_FIELD_TYPES` 所含类型，跳过 `SKIP_FIELD_TYPE`（约定见 [docs/EXCEL_TABLE_LAYOUT.md](docs/EXCEL_TABLE_LAYOUT.md)）
- **多语言支持**：合并 JSON 可含 `ZH`/`VN`/`TH`/`EN` 等顶层键；GUI 为各语言配置 Excel 目录；导出 CSV/总表列为 `ZH`、`VN`、`TH`、`EN`
- **精确定位**：记录 Excel 物理位置和字段名；数据区行下限遵循 **`ROW_BOUNDARY_KEYWORD`**
- **批量处理**：支持批量处理多个目录的 Excel 文件
- **灵活配置**：JSON 格式配置，易于扩展和维护
- **详细报告**：生成包含所有提取结果的 Excel 文件
- **已集成**：已合并到统一界面的「多语言翻译提取」页签

### 📝 批量改表工具

- **映射表驱动**：根据映射表（如分页 Excel）批量修改多个 Excel 文件
- **目标表格式**：与字段导出/多语言提取共用布局，见 [docs/EXCEL_TABLE_LAYOUT.md](docs/EXCEL_TABLE_LAYOUT.md)
- **xlwings 引擎**：支持使用 Excel 原生引擎，完全保留文件结构
- **灵活配置**：支持自定义表名列、ID 列、修改列
- **JSON 配置**：可选配合 JSON 配置文件定义字段映射
- **精确定位**：根据 ID 精确定位要修改的行
- **多列修改**：支持同时修改多个列的内容
- **自动备份**：修改前自动创建 `.bak` 备份文件
- **详细报告**：生成包含修改记录、统计信息、错误日志的报告
- **预览功能**：支持预览映射表内容
- **已集成**：已合并到统一界面的「批量改表」页签

## Excel 表布局规范

字段导出、多语言提取、批量改表、配置同步等工具共用同一套表头行（字段名 / 字段类型 / 数据起始行）与可选列范围标记；数据区向下遇到 `ROW_BOUNDARY_KEYWORD`（默认 `over`）即视为行遍历下限并停止。约定说明见 [docs/EXCEL_TABLE_LAYOUT.md](docs/EXCEL_TABLE_LAYOUT.md)；默认数值集中在 `core/constants.py`，避免各处硬编码。

## 快速开始

### 方法 1：使用发布版本（推荐）

1. 进入 `dist/` 目录
2. 双击最新的 `gametools_v*.exe`

### 方法 2：使用源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行统一界面
python gui/run_unified.py
```

或双击 `gui/启动gametools.bat`

### 方法 3：使用启动脚本

双击项目根目录下的 `启动策划工具.bat`

## 界面说明

以下为 **统一工作台**（`python gui/run_unified.py` 或打包 exe）侧栏页签说明。启动后默认打开 **「工作台」** 页：可在此一次性选择各语言表目录、统一输出目录、合并 JSON、JSON 检测目录、Excel 与批量改表相关路径等；各功能页以 **只读方式显示相同路径**（与工作台共用变量），**不再提供各页内的浏览选择按钮**。

推荐本地化顺序：**字段导出** → **多语言提取** → **批量改表**；辅助工具按需使用。

### 工作台

- **本地化主路径**：中文 / 越南语 / 泰语 / 英语表目录（与「字段导出」「多语言提取」共用）、导出与多语言输出目录（两页共用）、多语言合并 JSON。
- **其它工具路径**：JSON 检测目录、Excel 整合源文件与输出目录、跨项目翻译三项、批量改表四项。
- 可在「关于 → 界面与模块设置」中关闭「工作台」页签；**保存后主区页签与侧栏会立即更新**（关闭后路径仍与各功能页共用变量，仅隐藏集中入口）。

### 字段导出

1. 在 **「工作台」** 选择各语言 Excel 目录与输出目录；本页 **只读显示** 相同路径，并用「导出」勾选参与导出的语言。
2. 输出格式选 **JSON** 时会在输出目录生成合并文件（默认名见 `core.constants.FIELD_EXTRACTION_MERGED_JSON_NAME`）。
3. 点击「开始提取」；完成后若存在合并 JSON，可使用 **「用于多语言提取」** 一键切换到多语言页（路径已同步，无需再选）。

### 多语言提取

1. 合并 JSON、各语言目录与输出目录均在 **「工作台」** 选择；本页 **只读显示**。
2. 点击开始提取，生成翻译总表等结果。

### 批量改表

1. JSON、映射表、Excel 目录、报告文件路径在 **「工作台」** 选择；本页只读显示，并在本页选择目标语言、高级选项等。
2. 执行批量修改；详细行为见 [docs/BATCH_MODIFIER_GUIDE.md](docs/BATCH_MODIFIER_GUIDE.md)。

### 跨项目翻译

映射文件、扫描目录、输出文件路径在 **「工作台」** 选择；本页只读显示并执行跨项目对齐（与上列流水线并行，无强制先后顺序）。

### JSON 错误检测工具页签

1. **检测目录**：在 **「工作台」** 选择包含 JSON 的文件夹；本页只读显示该路径。
2. **选择模式**：选择检测模式（自动检测、仅检测文件、仅检测文件夹）
3. **开始检测**：点击「开始检测」按钮
4. **查看结果**：在结果区域查看详细的检测报告
5. **保存报告**：点击「保存报告」按钮将结果保存到文件

### Excel 数据处理工具页签

1. **源文件与输出目录**：在 **「工作台」** 选择；本页只读显示。
2. **输出文件名**：在本页填写（如「整合结果.xlsx」）。
3. **处理选项**：输出模式（多文件 / 单文件）、分组列、工作表前缀、是否汇总工作表等。
4. **开始处理**：点击「开始处理」按钮执行处理。
5. **查看结果**：在结果区域查看处理报告。

#### 输出模式说明

- **多文件模式（默认）**：为每个 A 列内容创建单独的 Excel 文件
- **单文件模式**：创建单个 Excel 文件包含多个工作表
- **自动文件名**：根据 A 列内容自动生成有意义的文件名
- **重复检测**：自动跳过已存在的文件，避免覆盖

### 关于页签

- 显示程序版本信息
- 功能特性说明
- 使用方法和注意事项
- **界面与模块设置**：可开关各功能页签

#### 输出模式说明

- **多文件模式（默认）**：为每个 A 列内容创建单独的 Excel 文件
- **单文件模式**：创建单个 Excel 文件包含多个工作表
- **自动文件名**：根据 A 列内容自动生成有意义的文件名
- **重复检测**：自动跳过已存在的文件，避免覆盖

### 关于页签

- 显示程序版本信息
- 功能特性说明
- 使用方法和注意事项

## 测试说明

### 📋 测试文件夹结构

所有测试文件已集中在 `test/` 文件夹中。详见 [test/README.md](test/README.md)

```text
test/
├── test_*.py                    # 功能测试脚本
├── create_test_data.py          # 测试数据生成工具
├── run_all_tests.py             # 运行所有测试脚本
├── run_tests.bat                # 测试启动脚本
├── test_config_sync/            # 随仓库提交的最小配置夹具
├── test_multi_lang/             # 随仓库提交的最小配置夹具
└── README.md                    # 详细测试文档
```

另外，项目根目录下的 `test_config_sync/`、`test_multi_lang/`、`test_output/` 属于测试运行时工作目录或输出目录，都会按需自动生成，不需要长期保留样例 Excel 和导出文件。

### 🧪 运行测试

```bash
# 快速运行单个测试
python test\test_cache.py

# 运行所有测试
python test\run_all_tests.py
```

## 打包成 exe 文件

```bash
# 运行构建脚本
python gui/build_unified.py

# 未变化时跳过重打包（不会额外递增版本号）
python gui/build_unified.py --skip-unchanged

# 开发测试快速打包（禁用 UPX，减少优化）
python gui/build_unified.py --fast

# 打包过程长时间无输出时查看详细阶段
python gui/build_unified.py --pyinstaller-log-level INFO
```

构建完成后会在 `dist/` 目录生成 `gametools_vX.X.X.exe`。

exe 与主窗口默认使用 `gui/assets/gametools.ico` 作为图标。若要换新图标，可替换该文件，或在 `gui/assets/` 下执行 `python build_gametools_icon.py` 用脚本重新生成（见 `gui/assets/README.md`）。

`--skip-unchanged` 会同时检查源码、打包参数和当前打包环境版本；只有这些输入都未变化时才直接复用已有产物。

`gui/.build_cache.json` 为本地增量缓存，已加入 `.gitignore`，无需提交。

构建脚本会在 PyInstaller 长时间无输出时定时打印心跳提示；可用 `--progress-interval 10` 调整提示间隔，或用 `--build-timeout 1800` 为构建设置超时。

## 系统要求

- Python 3.7+
- Windows 10/11（推荐）
- 支持的操作系统：Windows、macOS、Linux

## 依赖包

- tkinter（通常随 Python 安装）
- pandas（数据处理）
- xlwings（默认 Excel 修改引擎，需要安装 Excel）
- PyInstaller（用于打包）

## 版本信息

- 版本：以 [version.py](version.py) 和 GUI 显示为准
- 开发日期：2025 年
- 支持语言：中文界面
- 目标用户：游戏策划人员和开发人员

详细版本历史请查看 [version.py](version.py)

## 技术支持

如有问题或建议，请联系开发团队。

---

**gametools**  
版权所有 © 2024-2025
