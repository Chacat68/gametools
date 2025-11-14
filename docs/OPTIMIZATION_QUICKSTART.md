# GameTools 优化功能快速使用指南

本指南涵盖 **Phase 1** (性能优化) 和 **Phase 2** (用户体验) 的所有功能。

## 📋 目录

- [Phase 1: 性能优化](#phase-1-性能优化)
- [Phase 2: 用户体验优化](#phase-2-用户体验优化)

---

## Phase 1: 性能优化

### 1. 并行处理

```python
from core.vietnamese_excel_processor import VietnameseExcelProcessor

# 启用并行处理（推荐用于多文件）
processor = VietnameseExcelProcessor(
    enable_parallel=True,    # 启用并行
    max_workers=4            # 4个线程
)

# 扫描目录
results = processor.scan_directory("data/", recursive=True)
print(f"找到 {len(results)} 个越南文位置")
```

**性能提升**: 3-5倍（处理多文件时）

---

### 2. 大文件流式处理

```python
# 自动检测大文件并使用流式处理
processor = VietnameseExcelProcessor(
    chunk_size=10000  # 每次处理10000行
)

# 处理超大文件（>50MB会自动分块）
results = processor.scan_excel_file("large_file.xlsx")
```

**优势**: 
- 内存占用降低80%
- 支持处理500MB+文件

---

### 3. 智能缓存

```python
from core.cache_manager import MemoryCache

# 创建缓存
cache = MemoryCache(
    max_size=1000,        # 最多1000项
    max_memory_mb=500,    # 最大500MB
    default_ttl=3600      # 1小时过期
)

# 使用缓存
cache.set("key", data)
value = cache.get("key")

# 查看统计
stats = cache.get_stats()
print(f"命中率: {stats['hit_rate']}")
print(f"内存使用: {stats['memory_usage_mb']}")
```

---

### 4. 增强日志

```python
from core.log_manager import setup_logging, get_logger

# 设置日志（启动时调用一次）
setup_logging(
    level=logging.INFO,
    log_to_file=True,
    log_to_console=True,
    use_colors=True
)

# 使用日志
logger = get_logger(__name__)
logger.info("处理开始")
logger.error("发生错误")
```

**特性**:
- ✅ 彩色输出
- ✅ 自动保存到文件
- ✅ 自动清理旧日志

---

### 5. 进度跟踪

```python
from core.progress_tracker import ConsoleProgressBar

# 创建进度条
progress = ConsoleProgressBar(
    total=100,
    description="处理文件"
)

# 更新进度
for i in range(100):
    process_item(i)
    progress.update(1)  # +1

# 查看摘要
summary = progress.get_summary()
print(f"耗时: {summary['elapsed_time']}")
```

**效果**:
```
处理文件: |████████████████| 50.0% (50/100) - 剩余: 30秒
```

---

### 6. 错误处理

```python
from core.error_handler import (
    validate_file_path,
    validate_directory,
    FileProcessingError
)

# 验证文件
try:
    file_path = validate_file_path(
        "data.xlsx",
        must_exist=True,
        extensions=['.xlsx', '.xls']
    )
except FileProcessingError as e:
    print(e)  # 自动包含建议
```

**优势**:
- ✅ 友好的错误消息
- ✅ 自动修复建议
- ✅ 详细的上下文信息

---

## 💡 完整示例

```python
from core.vietnamese_excel_processor import VietnameseExcelProcessor
from core.log_manager import setup_logging, get_logger
from core.progress_tracker import ConsoleProgressBar

# 1. 设置日志
setup_logging(level=logging.INFO, log_to_file=True, use_colors=True)
logger = get_logger(__name__)

# 2. 创建优化的处理器
processor = VietnameseExcelProcessor(
    enable_parallel=True,      # 并行处理
    max_workers=4,             # 4线程
    chunk_size=10000           # 大文件分块
)

# 3. 处理文件
try:
    logger.info("开始扫描...")
    results, files = processor.scan_directory(
        "data/",
        recursive=True,
        return_files=True
    )
    
    # 4. 输出结果
    output_path = processor.create_output_excel(
        results,
        "output/",
        "检测结果.xlsx"
    )
    
    logger.info(f"完成！找到 {len(results)} 个越南文位置")
    logger.info(f"结果已保存到: {output_path}")
    
except Exception as e:
    logger.error(f"处理失败: {e}")
```

---

## 📊 配置建议

### 开发环境
```python
processor = VietnameseExcelProcessor(
    enable_parallel=False,  # 方便调试
    chunk_size=5000
)
```

### 生产环境
```python
processor = VietnameseExcelProcessor(
    enable_parallel=True,
    max_workers=8,          # 根据CPU核心数
    chunk_size=20000
)
```

### 内存受限环境
```python
processor = VietnameseExcelProcessor(
    enable_parallel=False,  # 节省内存
    chunk_size=5000         # 小块处理
)

cache = MemoryCache(max_memory_mb=100)  # 限制缓存
```

---

## 🧪 测试优化效果

```bash
# 运行完整测试
python test/test_optimizations.py
```

测试内容：
- ✅ 并行vs串行性能对比
- ✅ 缓存命中率
- ✅ 进度跟踪
- ✅ 错误处理
- ✅ 日志系统

---

## Phase 2: 用户体验优化

### 1. 配置管理

```python
from core.config_manager import ConfigManager

# 获取配置管理器（单例）
config = ConfigManager()

# 读取配置
parallel_enabled = config.get("scan.enable_parallel")
max_memory = config.get("cache.max_memory_mb")

# 修改配置
config.set("scan.chunk_size", 20000)
config.set("cache.max_memory_mb", 1000)

# 保存配置（自动持久化）
config.save()

# 导出/导入配置
config.export_config("backup.json")
config.import_config("backup.json")

# 重置到默认值
config.reset_to_defaults()
```

**优势**:
- ✅ 用户偏好持久化
- ✅ 跨会话配置保持
- ✅ 备份/恢复配置

---

### 2. 任务控制

```python
from core.task_controller import TaskController, controllable

# 方式1：直接控制
controller = TaskController()

# 启动任务
task = controller.start(processor.process_directory, "data/")

# 控制任务
controller.pause()    # 暂停
controller.resume()   # 恢复
controller.cancel()   # 取消

# 等待完成
result = task.wait(timeout=60)

# 方式2：使用装饰器
@controllable
def scan_files(directory, controller=None):
    for file in files:
        if controller:
            controller.check_point()  # 检查暂停/取消
        process_file(file)

# 调用
task = controller.start(scan_files, "data/")
```

**适用场景**:
- 🔄 大型目录扫描
- 🔄 批量处理任务
- 🔄 用户可能需要中断的操作

---

### 3. 进度跟踪增强

```python
from core.progress_tracker import ProgressTracker

# 创建进度跟踪器
tracker = ProgressTracker(total=100, desc="扫描文件")

# 启用子步骤
tracker.enable_substeps(True)

# 主步骤
for i in range(10):
    tracker.update(i * 10)
    
    # 子步骤
    tracker.start_substeps(5, f"处理文件 {i+1}")
    for j in range(5):
        tracker.update_substep(j + 1, f"读取工作表 {j+1}")

# 查看统计
stats = tracker.get_stats()
print(f"平均速度: {stats['avg_speed']} it/s")
print(f"预计剩余: {stats['eta_seconds']}秒")
```

**输出示例**:
```
扫描文件: 30% |████████░░░░░░░░| 30/100 [00:15<00:35, 2.0 it/s]
  └─ 处理文件 4: 60% |██████░░░░| 3/5 读取工作表 3
```

---

### 4. 结果过滤搜索

```python
from core.result_filter import ResultFilter, QuickSearch, FilterOperator

# 创建过滤器
filter_obj = ResultFilter()

# 链式添加条件
filtered = (filter_obj
    .add_filter('language_type', FilterOperator.EQUALS, '越南文')
    .add_filter('row', FilterOperator.GREATER_THAN, 10)
    .add_sort('row', 'asc')
    .apply(results))

# 快速搜索
search_results = QuickSearch.search(results, "config", fields=['file'])

# 正则搜索
regex_results = QuickSearch.regex_search(results, r"test_\d+\.xlsx")

# 便捷函数
from core.result_filter import quick_filter, quick_search

# 简单过滤
viet_results = quick_filter(results, language_type='越南文')

# 快速搜索
config_results = quick_search(results, 'config')
```

**过滤操作符**:
- `EQUALS`, `NOT_EQUALS` - 等于/不等于
- `CONTAINS`, `NOT_CONTAINS` - 包含/不包含
- `STARTS_WITH`, `ENDS_WITH` - 开头/结尾
- `GREATER_THAN`, `LESS_THAN` - 大于/小于
- `IN_LIST` - 在列表中
- `REGEX` - 正则匹配

---

### 5. 多格式输出

```python
from core.output_formats import ResultExporter, OutputFormat

# 创建导出器
exporter = ResultExporter()

# 方式1：自动识别格式（根据扩展名）
exporter.export(results, "output.xlsx")  # Excel
exporter.export(results, "output.json")  # JSON
exporter.export(results, "output.html")  # HTML

# 方式2：指定格式
exporter.export(results, "report", format_type=OutputFormat.HTML)

# 添加元数据
metadata = {
    'scan_date': '2024-01-15',
    'total_files': 50,
    'version': '1.24.0'
}

exporter.export(results, "report.xlsx", metadata=metadata)

# 格式特定选项

# Excel选项
exporter.export(results, "output.xlsx",
    sheet_name='检测结果',
    auto_filter=True,       # 自动筛选
    freeze_panes=True       # 冻结首行
)

# CSV选项
exporter.export(results, "output.csv",
    encoding='utf-8-sig',   # Excel兼容
    delimiter=','
)

# JSON选项
exporter.export(results, "output.json",
    indent=2,
    ensure_ascii=False
)

# HTML选项
exporter.export(results, "output.html",
    title='越南文检测报告',
    metadata=metadata
)
```

**支持格式**:
- ✅ **Excel** (.xlsx) - 样式丰富，筛选，冻结
- ✅ **CSV** (.csv) - 通用格式，Excel可打开
- ✅ **JSON** (.json) - 结构化，程序处理
- ✅ **HTML** (.html) - 美观报告，浏览器查看
- ✅ **Markdown** (.md) - 文档集成
- ✅ **Text** (.txt) - 纯文本

---

## 💡 完整工作流（Phase 1 + Phase 2）

```python
from core.config_manager import ConfigManager
from core.task_controller import TaskController
from core.vietnamese_excel_processor import VietnameseExcelProcessor
from core.result_filter import ResultFilter, FilterOperator
from core.output_formats import ResultExporter

# 1. 加载配置
config = ConfigManager()

# 2. 创建优化的处理器
processor = VietnameseExcelProcessor(
    max_workers=config.get('scan.max_workers'),
    enable_parallel=config.get('scan.enable_parallel'),
    chunk_size=config.get('scan.chunk_size')
)

# 3. 创建任务控制器
controller = TaskController()

# 4. 定义可控任务
@controllable
def scan_with_control(directory, controller=None):
    return processor.process_directory(directory)

# 5. 启动任务（用户可暂停/恢复）
task = controller.start(scan_with_control, "input_folder/")

# 用户可以控制
# controller.pause()   # 暂停
# controller.resume()  # 恢复

# 6. 等待完成
results = task.wait()

# 7. 过滤结果
filter_obj = ResultFilter()
filter_obj.add_filter('language_type', FilterOperator.CONTAINS, '越南')
filtered = filter_obj.apply(results)

# 8. 导出多种格式
exporter = ResultExporter()

metadata = {
    'scan_directory': 'input_folder/',
    'total_files': len(results),
    'filtered_count': len(filtered)
}

# Excel报告
exporter.export(filtered, "vietnamese_results.xlsx", metadata=metadata)

# HTML报告
exporter.export(filtered, "vietnamese_results.html", 
                title='越南文检测报告', metadata=metadata)

# JSON（程序处理）
exporter.export(filtered, "vietnamese_results.json", metadata=metadata)

print(f"✓ 扫描完成！找到 {len(filtered)} 条越南文相关记录")
print("✓ 结果已导出为 Excel、HTML 和 JSON 格式")
```

---

## 🧪 测试 Phase 2 功能

```bash
# 运行 Phase 2 集成测试
python test/test_phase2_integration.py
```

测试内容：
- ✅ 配置管理（读写、导入/导出）
- ✅ 任务控制（暂停/恢复/取消）
- ✅ 子步骤进度跟踪
- ✅ 结果过滤和搜索
- ✅ 6种格式导出

---

## 📚 更多信息

查看完整文档：
- `docs/OPTIMIZATION_REPORT_v1.23.0.md` - Phase 1 详细报告
- `docs/OPTIMIZATION_REPORT_v1.24.0.md` - Phase 2 详细报告
- `core/error_handler.py` - 错误处理API
- `core/log_manager.py` - 日志管理API
- `core/progress_tracker.py` - 进度跟踪API

---

**版本**: v1.22.0  
**更新日期**: 2025-11-14
