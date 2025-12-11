# GameTools AI 助手指导文档

游戏策划本地化工具集，用于Excel批量处理、多语言翻译提取、JSON检测等。

## 项目架构

```
gametools/
├── core/               # 核心功能类（所有业务逻辑）
├── gui/                # tkinter GUI实现（统一界面入口）
├── tools/              # 命令行工具和辅助脚本
├── test/               # 测试脚本和测试数据生成
├── docs/               # 版本报告和功能文档
└── version.py          # 版本信息和历史记录
```

### 核心模块关系

| 模块 | 功能 | 关键方法 |
|------|------|----------|
| `batch_excel_modifier.py` | 批量改表（默认xlwings引擎） | `process_batch_modification()` |
| `excel_field_extractor.py` | 字段导出（检测本地化列） | `extract_fields()` |
| `table_range_translator.py` | 多语言提取 | `extract_translations()` |
| `cross_project_translator.py` | 跨项目翻译对应 | 支持缓存版 `*_cached.py` |
| `cache_manager.py` | LRU缓存+文件缓存 | `MemoryCache`, `FileCache` |

## 关键开发模式

### 1. 核心类标准结构
每个核心类遵循相同模式（参考 `batch_excel_modifier.py`）：
```python
class SomeProcessor:
    def __init__(self):
        self.supported_extensions = {'.xlsx', '.xls'}
        self.processing_stats = {}    # 统计信息字典
        self.error_logs = []          # 错误收集列表
        self.progress_callback = None # GUI进度回调

    def set_progress_callback(self, callback):
        """设置进度回调: callback(message, percentage)"""
        self.progress_callback = callback

    def _report_progress(self, message: str, percentage: float = None):
        """统一进度报告"""
        if self.progress_callback:
            self.progress_callback(message, percentage)
```

### 2. Excel处理引擎选择
- **xlwings**（默认）：调用Excel原生引擎，完全保留文件结构（批注、宏等）
- **openpyxl**（备用）：纯Python实现，不需要Excel安装
- 关键：批量改表必须用xlwings，否则会破坏文件结构导致其他工具无法读取

### 3. 错误处理模式
使用 `core/error_handler.py` 中的自定义异常：
```python
from core.error_handler import ExcelReadError, FileProcessingError, GameToolsError
# 异常包含 message, suggestion, original_error 属性
```

### 4. 本地化文本检测规则
检测中文、越南文、泰文字符（在 `excel_field_extractor.py`）：
```python
# Unicode范围
中文: \u4e00-\u9fff, \u3400-\u4dbf
越南文: \u00C0-\u1EF9
泰文: \u0E00-\u0E7F
```
过滤字段：`name`, `model`, `id`, `code`, `type` 等代码字段

### 5. GUI开发模式
统一界面在 `gui/gametools_unified.py`，使用多页签设计：
- 每个功能一个 `create_xxx_tab()` 方法
- 耗时操作必须用 `threading.Thread` 避免阻塞UI
- 结果存储在 `self.results_storage` 字典

## 常用命令

```bash
# 运行GUI（唯一入口）
双击 启动策划工具.bat
# 或: python gui/run_unified.py

# 运行测试
python test/run_all_tests.py
python test/test_cache_basic.py  # 单个测试

# 打包exe
python gui/build_unified.py
# 输出到 dist/gametools_vX.X.X.exe
```

## 配置文件

- `config.json`: 运行时配置（缓存、并行、日志等）
- `config_export.json`: 字段导出配置（表名、字段映射）

## 编码规范

- 所有Python文件使用 `# -*- coding: utf-8 -*-`
- 文件编码尝试顺序：`utf-8` → `gbk` → `gb2312`
- 中文注释和文档字符串
- 版本更新需同步修改 `version.py`

## 测试数据

- `test/create_test_excel.py`: 生成测试Excel
- `test/create_test_mapping_file.py`: 生成映射文件
- 测试前确保 `test/` 目录下有测试数据

## 注意事项

1. **Excel文件操作后必须关闭**：使用 `finally` 确保资源释放
2. **大文件分批处理**：使用 `chunk_size` 参数控制内存
3. **进度回调节流**：`ProgressTracker` 控制更新频率避免UI卡顿
4. **缓存失效**：文件修改后需清理相关缓存