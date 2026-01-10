#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI启动优化示例 - 展示如何实施延迟Tab加载
这是一个参考实现，展示关键改动点
"""

# ============================================================================
# 改动点 1: __init__ 中的初始化调整
# ============================================================================

def __init__(self, root):
    """初始化GUI（优化版本）"""
    self.root = root
    self.root.title(f"gametools v{get_version()}")
    self.root.geometry("900x650")
    self.root.minsize(800, 550)
    
    # 设置窗口图标
    try:
        self.root.iconbitmap("icon.ico")
    except:
        pass
    
    # 设置样式（保持不变）
    self.setup_styles()
    
    # 懒加载：处理器实例缓存
    self._processors = {}
    
    # 扫描状态
    self.is_scanning = False
    
    # 结果存储字典
    self.results_storage = {
        'cross_project_translator': '',
        'json_detector': '',
        'excel_processor': '',
        'field_extractor': '',
        'table_range_translator': '',
        'sheet_splitter': '',
        'batch_modifier': '',
        'config_sync': '',
        'csv_converter': ''
    }
    
    # 字段提取结果数据
    self.field_extraction_results = None
    
    # ✅ 新增：Tab 追踪（标记已创建的 Tab）
    self._created_tabs = {}
    self.tab_configs = {}
    
    # 创建UI（现在非常快，只创建占位符）
    self.create_widgets()
    
    # ✅ 可选：后台预加载常用处理器
    self._preload_thread = threading.Thread(
        target=self._preload_common_processors, 
        daemon=True
    )
    self._preload_thread.start()


def _preload_common_processors(self):
    """后台预加载常用处理器，避免首次使用卡顿"""
    try:
        import time
        time.sleep(0.5)  # 等待UI显示完成
        
        # 预加载使用频率最高的处理器
        _ = self.json_detector
        _ = self.field_extractor
        logging.info("后台处理器预加载完成")
    except Exception as e:
        logging.warning(f"后台预加载失败: {e}")


# ============================================================================
# 改动点 2: create_widgets 改为创建占位符Tab
# ============================================================================

def create_widgets(self):
    """创建界面控件（延迟Tab加载版本）"""
    # 主框架
    main_frame = ttk.Frame(self.root, padding="5")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 配置网格权重
    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    # 创建笔记本控件（页签）
    self.notebook = ttk.Notebook(main_frame)
    self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # ✅ 新增：绑定Tab切换事件
    self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    # 定义所有Tab信息（不创建UI，只记录元数据）
    self.tab_configs = {
        'cross_project_translator': {
            'label': '跨项目翻译',
            'creator': self.create_cross_project_translator_tab
        },
        'json_detector': {
            'label': 'JSON检测',
            'creator': self.create_json_detector_tab
        },
        'excel_processor': {
            'label': 'Excel数据处理',
            'creator': self.create_excel_data_processor_tab
        },
        'sheet_splitter': {
            'label': '表单分割',
            'creator': self.create_sheet_splitter_tab
        },
        'field_extractor': {
            'label': '字段导出',
            'creator': self.create_field_extractor_tab
        },
        'table_range_translator': {
            'label': '多语言提取',
            'creator': self.create_table_range_translator_tab
        },
        'batch_modifier': {
            'label': '批量改表',
            'creator': self.create_batch_modifier_tab
        },
        'config_sync': {
            'label': '配置同步',
            'creator': self.create_config_sync_tab
        },
        'csv_converter': {
            'label': 'CSV转换',
            'creator': self.create_csv_converter_tab
        },
        'about': {
            'label': '关于',
            'creator': self.create_about_tab
        }
    }
    
    # ✅ 关键优化：创建占位符Tab，而非真实UI
    self._created_tabs = {}
    for tab_key, config in self.tab_configs.items():
        # 创建空白占位符
        placeholder = ttk.Frame(self.notebook)
        self.notebook.add(placeholder, text=config['label'])
        self._created_tabs[tab_key] = False  # 标记为未创建
    
    # 状态栏
    self.status_var = tk.StringVar(value="就绪")
    status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                          relief=tk.SUNKEN, anchor=tk.W, padding="3")
    status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))


def _on_tab_changed(self, event):
    """Tab切换时的回调 - 延迟加载Tab内容"""
    try:
        # 获取当前Tab索引
        current_tab = self.notebook.index(self.notebook.select())
        tab_keys = list(self.tab_configs.keys())
        
        if current_tab >= len(tab_keys):
            return
        
        tab_key = tab_keys[current_tab]
        
        # 如果该Tab还未创建过，则创建
        if not self._created_tabs.get(tab_key, False):
            self.status_var.set(
                f"正在加载 {self.tab_configs[tab_key]['label']}..."
            )
            self.root.update_idletasks()  # 强制更新显示
            
            try:
                # 调用对应的Tab创建函数
                self.tab_configs[tab_key]['creator'](is_lazy_loading=True)
                self._created_tabs[tab_key] = True
                logging.info(f"Tab '{tab_key}' 加载完成")
            except Exception as e:
                logging.error(f"Tab '{tab_key}' 加载失败: {e}", exc_info=True)
                messagebox.showerror("加载失败", f"无法加载{self.tab_configs[tab_key]['label']}: {e}")
            finally:
                self.status_var.set("就绪")
        
    except Exception as e:
        logging.error(f"Tab切换处理异常: {e}", exc_info=True)


# ============================================================================
# 改动点 3: 各Tab创建函数添加 is_lazy_loading 参数
# ============================================================================

def create_cross_project_translator_tab(self, is_lazy_loading=False):
    """创建跨项目翻译对应页签 (优化版本)"""
    
    # ✅ 如果是延迟加载模式，需要替换占位符
    if is_lazy_loading:
        current_index = self.notebook.index(self.notebook.select())
        translator_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.forget(current_index)
        self.notebook.insert(current_index, translator_frame, text="跨项目翻译")
    else:
        # 原始模式（兼容）
        translator_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(translator_frame, text="跨项目翻译")
    
    translator_frame.columnconfigure(0, weight=1)
    
    # 文件选择区域 - 代码保持不变
    file_frame = ttk.LabelFrame(translator_frame, text="文件选择", padding="8")
    file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
    file_frame.columnconfigure(1, weight=1)
    
    # ... 其余UI代码保持不变 ...


def create_json_detector_tab(self, is_lazy_loading=False):
    """创建JSON错误检测工具页签 (优化版本)"""
    
    if is_lazy_loading:
        current_index = self.notebook.index(self.notebook.select())
        json_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.forget(current_index)
        self.notebook.insert(current_index, json_frame, text="JSON检测")
    else:
        json_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(json_frame, text="JSON检测")
    
    # ... 其余代码保持不变 ...


# ... 类似地修改其他所有 create_xxx_tab 函数 ...


# ============================================================================
# 改动点 4: 优化处理器属性（改用延迟导入）
# ============================================================================

# ✅ 删除文件顶部的直接导入：
# from core.cross_project_translator import CrossProjectTranslator
# from core.excel_field_extractor import ExcelFieldExtractor
# ... 其他 7 个模块

# ✅ 改为属性中进行延迟导入

@property
def cross_project_translator(self):
    """延迟导入的跨项目翻译器"""
    if 'cross_project_translator' not in self._processors:
        from core.cross_project_translator import CrossProjectTranslator
        self._processors['cross_project_translator'] = CrossProjectTranslator()
    return self._processors['cross_project_translator']


@property
def json_detector(self):
    """延迟导入的JSON检测器"""
    if 'json_detector' not in self._processors:
        from tools.json_error_detector.json_error_detector import JSONErrorDetector
        self._processors['json_detector'] = JSONErrorDetector()
    return self._processors['json_detector']


@property
def excel_processor(self):
    """延迟导入的Excel处理器"""
    if 'excel_processor' not in self._processors:
        from tools.excel_data_processor import ExcelDataProcessor
        self._processors['excel_processor'] = ExcelDataProcessor()
    return self._processors['excel_processor']


@property
def field_extractor(self):
    """延迟导入的字段提取器"""
    if 'field_extractor' not in self._processors:
        from core.excel_field_extractor import ExcelFieldExtractor
        self._processors['field_extractor'] = ExcelFieldExtractor()
    return self._processors['field_extractor']


@property
def table_range_translator(self):
    """延迟导入的表范围翻译器"""
    if 'table_range_translator' not in self._processors:
        from core.table_range_translator import TableRangeTranslator
        self._processors['table_range_translator'] = TableRangeTranslator()
    return self._processors['table_range_translator']


@property
def sheet_splitter(self):
    """延迟导入的表单分割器"""
    if 'sheet_splitter' not in self._processors:
        from core.excel_sheet_splitter import ExcelSheetSplitter
        self._processors['sheet_splitter'] = ExcelSheetSplitter()
    return self._processors['sheet_splitter']


@property
def batch_modifier(self):
    """延迟导入的批量改表器"""
    if 'batch_modifier' not in self._processors:
        from core.batch_excel_modifier import BatchExcelModifier
        self._processors['batch_modifier'] = BatchExcelModifier()
    return self._processors['batch_modifier']


@property
def config_sync(self):
    """延迟导入的配置同步器"""
    if 'config_sync' not in self._processors:
        from core.excel_config_sync import ExcelConfigSync
        self._processors['config_sync'] = ExcelConfigSync()
    return self._processors['config_sync']


@property
def csv_converter(self):
    """延迟导入的CSV转换器"""
    if 'csv_converter' not in self._processors:
        from core.excel_to_csv_converter import ExcelToCsvConverter
        self._processors['csv_converter'] = ExcelToCsvConverter()
    return self._processors['csv_converter']


# ============================================================================
# 总结：关键改动
# ============================================================================
# 1. __init__: 添加 _created_tabs 和 tab_configs，启动后台预加载线程
# 2. create_widgets: 创建占位符Tab，绑定Tab切换事件
# 3. _on_tab_changed: 新增方法，首次切换时才创建真实Tab内容
# 4. create_xxx_tab: 添加 is_lazy_loading 参数，替换占位符
# 5. 处理器属性: 改用延迟导入（可选，进阶优化）
# ============================================================================
