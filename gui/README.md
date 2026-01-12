# GameTools GUI 模块

基于 tkinter 的统一图形界面，整合所有游戏策划工具。

## 快速启动

```bash
# 方法1: 运行启动脚本
python run_unified.py

# 方法2: 直接运行主程序
python gametools_unified.py

# 方法3: 使用批处理文件（Windows）
双击 ../启动策划工具.bat
```

## 目录结构

```
gui/
├── gametools_unified.py    # 统一界面主程序
├── run_unified.py          # GUI 启动脚本
├── build_unified.py        # PyInstaller 打包脚本
├── gametools_unified.spec  # PyInstaller 配置文件
├── tabs/                   # 各功能页签模块
│   ├── base_tab.py         # 页签基类
│   ├── batch_modifier_tab.py
│   ├── config_sync_tab.py
│   ├── cross_project_tab.py
│   ├── csv_converter_tab.py
│   ├── field_extractor_tab.py
│   ├── json_detector_tab.py
│   ├── sheet_splitter_tab.py
│   ├── table_range_translator_tab.py
│   └── about_tab.py
├── base_detector_gui.py    # 检测器 GUI 基类
├── gui_utils.py            # GUI 工具函数
├── import_helper.py        # PyInstaller 导入修复
├── hook_numpy.py           # numpy 打包钩子
└── pyi_rth_numpy_fix.py    # numpy 运行时钩子
```

## 功能页签

| 页签 | 功能 | 核心模块 |
|------|------|----------|
| 跨项目翻译对应 | 翻译映射和对照 | `cross_project_translator.py` |
| JSON检测 | JSON语法和格式错误检测 | `json_error_detector.py` |
| Excel数据处理 | A列分组和拆分 | `excel_data_processor.py` |
| 表字段导出 | 提取本地化字段 | `excel_field_extractor.py` |
| 多语言翻译提取 | 按配置提取多语言 | `table_range_translator.py` |
| 分页拆分 | 按首列创建分页 | `excel_sheet_splitter.py` |
| 批量改表 | 批量修改Excel | `batch_excel_modifier.py` |
| 配置同步 | Excel配置一致性检查 | `excel_config_sync.py` |
| Excel转CSV | 批量转换格式 | `excel_to_csv_converter.py` |

## 打包发布

```bash
# 运行打包脚本
python build_unified.py

# 输出位置
dist/gametools_v{版本号}.exe
```

## 性能优化

- **Tab 延迟加载**: 只在用户切换时创建 Tab UI
- **模块延迟导入**: 减少启动时导入时间
- **后台预加载**: 常用处理器后台初始化
- **启动时间**: 优化后 ~0.5 秒

## 系统要求

- Python 3.8+
- Windows 10/11
- 依赖: tkinter, pandas, openpyxl, xlwings
