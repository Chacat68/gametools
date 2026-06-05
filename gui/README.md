# GameTools GUI 模块

基于 tkinter 的图形界面，现统一为单窗口侧边导航方案。

## 当前界面

当前版本保留原有功能模块，但收敛为一套轻量主题和单入口布局：

- 左侧导航切换功能模块
- 右侧工作区专注当前任务
- 统一样式、减少多套 UI 并存带来的维护成本
- 延迟加载处理器，优先保证启动速度和响应性
- 历史上的拆分页签方案和 modern 打包入口已移除，避免继续分叉

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
├── gametools_unified.py    # 统一界面主程序与功能装配
├── json_detector_page.py   # JSON 检测页签控制器
├── result_store.py         # 各功能页结果文本存储
├── task_runner.py          # 后台任务与 UI 主线程回调封装
├── run_unified.py          # 统一界面启动脚本
├── build_unified.py        # 统一界面打包脚本
├── ui_theme.py             # 公共主题配置
├── gametools_unified.spec  # PyInstaller 配置文件
└── ...
```

### 拆分约定

`gametools_unified.py` 负责窗口、导航和功能页装配；单个功能页的 UI 与动作逻辑逐步迁移到独立 `*_page.py` 模块。公共的结果缓存和后台线程调度分别放在 `result_store.py` 与 `task_runner.py`，功能页应通过主界面提供的兼容方法访问这些能力。

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

## 模块可见性设置

用户可以在「关于」页面中点击「界面设置」按钮来自定义显示哪些功能模块：

1. 打开「关于」页面
2. 点击「界面设置」按钮
3. 在弹窗中勾选/取消勾选需要显示的功能页签
4. 点击「保存」
5. 重启程序后生效

---

## 打包发布

```bash
# 运行打包脚本
python build_unified.py

# 未变化时跳过重打包
python build_unified.py --skip-unchanged

# 输出位置
dist/gametools_v{版本号}.exe
```

`--skip-unchanged` 会校验源码、打包参数和构建环境版本，完全一致时直接复用已有 exe，并保持当前版本号不变。

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
