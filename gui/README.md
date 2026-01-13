# GameTools GUI 模块

基于 tkinter 的图形界面，提供传统版本和现代化版本两种选择。

## 🆕 现代化版本（推荐）

现代化版本采用全新的侧边栏导航设计，界面更美观、操作更便捷。

### 快速启动

```bash
# 方法1: 运行启动脚本
python run_modern.py

# 方法2: 使用批处理文件（Windows）
双击 ../启动现代化工具.bat
```

### 特性

- 🎨 **现代扁平化设计** - 采用现代UI风格，简洁美观
- 📱 **侧边栏导航** - 左侧导航栏 + 右侧内容区布局
- 🏠 **仪表盘首页** - 快捷入口，一目了然
- ⚡ **延迟加载** - 页面按需加载，启动速度快
- 🎯 **统一组件库** - 标准化的按钮、输入框、进度条等组件

### 目录结构

```
gui/
├── gametools_modern.py     # 现代化界面主程序
├── run_modern.py           # 现代化版本启动脚本
├── build_modern.py         # 现代化版本打包脚本
├── modern_theme.py         # 主题配置（颜色、字体、尺寸）
├── components/             # 现代化UI组件
│   ├── __init__.py
│   ├── sidebar.py          # 侧边栏导航组件
│   └── widgets.py          # 通用组件（按钮、卡片、进度条等）
├── pages/                  # 功能页面
│   ├── __init__.py
│   ├── base_page.py        # 页面基类
│   ├── home_page.py        # 首页/仪表盘
│   ├── about_page.py       # 关于页面
│   ├── batch_modifier_page.py
│   ├── json_detector_page.py
│   ├── field_extractor_page.py
│   └── csv_converter_page.py
└── ...
```

---

## 传统版本

传统版本使用 Tab 页签设计，保持向后兼容。

### 快速启动

```bash
# 方法1: 运行启动脚本
python run_unified.py

# 方法2: 直接运行主程序
python gametools_unified.py

# 方法3: 使用批处理文件（Windows）
双击 ../启动策划工具.bat
```

### 目录结构

```
gui/
├── gametools_unified.py    # 传统界面主程序
├── run_unified.py          # 传统版本启动脚本
├── build_unified.py        # 传统版本打包脚本
├── gametools_unified.spec  # PyInstaller 配置文件
├── tabs/                   # 传统版本页签模块
│   ├── base_tab.py         # 页签基类
│   ├── batch_modifier_tab.py
│   ├── config_sync_tab.py
│   └── ...
└── ...
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

## 页签可见性设置

用户可以在「关于」页面中点击「界面设置」按钮来自定义显示哪些功能页签：

1. 打开「关于」页签
2. 点击「⚙️ 界面设置」按钮
3. 在弹窗中勾选/取消勾选需要显示的功能页签
4. 点击「保存」
5. 重启程序后生效

---

## 打包发布

### 现代化版本打包

```bash
# 运行现代化版本打包脚本
python build_modern.py

# 完整清理后打包
python build_modern.py --clean

# 输出位置
dist/gametools_v{版本号}.exe
```

### 传统版本打包

```bash
# 运行传统版本打包脚本
python build_unified.py

# 输出位置
dist/gametools_v{版本号}.exe
```

---

## 性能优化

- **页面延迟加载**: 只在用户访问时创建页面 UI
- **模块延迟导入**: 减少启动时导入时间
- **后台预加载**: 常用处理器后台初始化
- **启动时间**: 优化后 ~0.5 秒

---

- Python 3.8+
- Windows 10/11
- 依赖: tkinter, pandas, openpyxl, xlwings
