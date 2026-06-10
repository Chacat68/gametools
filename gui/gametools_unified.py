#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools - 统一用户界面
集成JSON格式检测和Excel处理工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from copy import deepcopy
from datetime import datetime
import importlib.util
from pathlib import Path
import subprocess
import logging

# 修复 PyInstaller 环境下的导入问题（必须在其他导入之前调用）
# 检测是否在 PyInstaller 环境
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    # PyInstaller 环境使用绝对导入
    from gui.import_helper import fix_pyinstaller_imports
    from gui.json_detector_page import JsonDetectorPage
    from gui.cross_project_page import CrossProjectPage
    from gui.field_extractor_page import FieldExtractorPage
    from gui.table_range_page import TableRangePage
    from gui.batch_modifier_page import BatchModifierPage
    from gui.excel_data_processor_page import ExcelDataProcessorPage
    from gui.result_store import ResultStore
    from gui.task_runner import TaskRunner
    from gui.ui_theme import apply_ui_theme
else:
    # 开发环境使用相对导入
    from .import_helper import fix_pyinstaller_imports
    from .json_detector_page import JsonDetectorPage
    from .cross_project_page import CrossProjectPage
    from .field_extractor_page import FieldExtractorPage
    from .table_range_page import TableRangePage
    from .batch_modifier_page import BatchModifierPage
    from .excel_data_processor_page import ExcelDataProcessorPage
    from .result_store import ResultStore
    from .task_runner import TaskRunner
    from .ui_theme import apply_ui_theme
fix_pyinstaller_imports()

# 添加模块路径（仅在非 PyInstaller 环境）
if not hasattr(sys, 'frozen'):
    sys.path.append(str(Path(__file__).parent.parent))

# 导入core模块（会自动初始化日志配置）
import core
from core.cross_project_translator_cached import CrossProjectTranslatorWithCache
from core.excel_field_extractor import ExcelFieldExtractor
from core.table_range_translator import TableRangeTranslator
from core.batch_excel_modifier import BatchExcelModifier
from core.config_manager import config_manager
from core.constants import (
    SUPPORTED_LANGUAGES,
    FIELD_NAME_ROW,
    DATA_START_ROW,
)
from tools.json_error_detector.json_error_detector import JSONErrorDetector
from tools.excel_data_processor import ExcelDataProcessor
from version import get_version, format_version_string, get_build_date


TAB_VISUALS = {
    'home': {'tag': 'HM', 'tone': '#4a7c8f'},
    'cross_project_translator': {'tag': 'CP', 'tone': '#c27a52'},
    'json_detector': {'tag': 'JS', 'tone': '#5e8778'},
    'excel_data_processor': {'tag': 'XL', 'tone': '#5f7f98'},
    'field_extractor': {'tag': 'FD', 'tone': '#a48749'},
    'table_range_translator': {'tag': 'ML', 'tone': '#8e7258'},
    'batch_modifier': {'tag': 'BM', 'tone': '#86606c'},
    'about': {'tag': 'AB', 'tone': '#647b85'},
}

TASK_RESULT_KEYS = {
    'cross_project_translator': 'cross_project_translator',
    'json_detector': 'json_detector',
    'excel_data_processor': 'excel_processor',
    'field_extractor': 'field_extractor',
    'table_range_translator': 'table_range_translator',
    'batch_modifier': 'batch_modifier',
}

RESULT_TASK_KEYS = {value: key for key, value in TASK_RESULT_KEYS.items()}

TASK_TITLES = {
    'home': '工作台',
    'cross_project_translator': '跨项目翻译',
    'json_detector': 'JSON检测',
    'excel_data_processor': '数据处理',
    'field_extractor': '字段导出',
    'table_range_translator': '多语言提取',
    'batch_modifier': '批量改表',
}

NAV_SECTIONS = [
    ('工作台', ('home',)),
    ('主要流程', ('field_extractor', 'table_range_translator', 'batch_modifier', 'cross_project_translator')),
    ('辅助工具', ('excel_data_processor', 'json_detector')),
    ('关于', ('about',)),
]

HOME_FLOW_SPECS = [
    ('field_extractor', '字段导出', '扫描多语言表并生成合并 JSON，作为多语言提取的配置输入。'),
    ('table_range_translator', '多语言提取', '按合并 JSON 从各语言目录抽取可交付翻译总表。'),
    ('batch_modifier', '批量改表', '按映射表与 JSON 配置回填 Excel，适合高频改表。'),
    ('cross_project_translator', '跨项目翻译', '根据映射关系对齐项目间文本。'),
]

HOME_SUPPORT_SPECS = [
    ('excel_data_processor', '数据处理', '拆分、转换和整理 Excel 数据。'),
    ('json_detector', 'JSON检测', '校验 JSON 结构与多语言格式。'),
]

TAB_DESCRIPTIONS = {
    'home': '在此统一选择各语言表目录、输出目录及常用配置文件路径，与各功能页输入框实时同步。',
    'cross_project_translator': '映射、项目目录与输出路径请在「工作台」选择；本页展示当前值并执行跨项目翻译。',
    'json_detector': '检测目录请在「工作台」选择；本页展示路径并执行 JSON 校验。',
    'excel_data_processor': '源文件与输出目录请在「工作台」选择；本页展示路径并配置整合选项。',
    'field_extractor': '语言目录与输出路径请在「工作台」选择；本页展示路径并配置导出选项与执行提取。',
    'table_range_translator': '合并 JSON 与各语言目录请在「工作台」选择；本页展示路径并执行多语言提取。',
    'batch_modifier': 'JSON、映射表、Excel 目录与报告路径请在「工作台」选择；本页展示路径并配置改表选项。',
    'about': '在这里查看工具信息、界面设置和诊断入口。',
}

BUTTON_LABELS = {
    'start_generation': '开始生成',
    'start_detection': '开始检测',
    'start_consolidation': '开始整合',
    'start_extraction': '开始提取',
    'start_batch_modifier': '开始批量修改',
    'view_results': '查看结果',
    'clear_results': '清空结果',
    'export_results': '导出结果',
    'save_report': '保存报告',
    'preview_data': '预览数据',
    'preview_mapping': '预览映射',
    'copy_results': '复制结果',
    'view_logs': '查看日志',
    'refresh_languages': '刷新语言列表',
    'use_field_for_trt': '用于多语言提取',
}


class GameToolsUnified:
    """gametools统一界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"gametools v{get_version()}")

        self.ui_config = config_manager.config.ui
        self._processors = {}
        self.is_scanning = False
        self.task_panels = {}
        self.task_state = {}
        self.inline_messages = {}
        self.dashboard_frames = {}
        self.tab_scroll_context = {}
        self.responsive_layouts = []
        self._active_tab_scroll_key = None
        self._validation_watchers_ready = False
        self._is_restoring_state = False
        self._sidebar_hidden = False
        self._last_saved_form_state = None
        self._form_state_save_job = None
        self._form_state_watchers_ready = False
        self.result_store = ResultStore(TASK_RESULT_KEYS.values())
        self.results_storage = self.result_store.storage
        self.task_runner = TaskRunner(
            self.root,
            lambda: getattr(self, 'status_var', None),
            lambda kind, title, message: self._show_message(kind, title, message),
            threading,
        )
        self.field_extraction_results = None
        self._field_last_merged_json_path = None

        self._apply_saved_window_geometry()
        self.root.minsize(980, 680)
        
        # 设置样式
        self.setup_styles()
        self._apply_window_icon()
        
        # 创建界面
        self.create_widgets()
        self._apply_sidebar_width(self.ui_config.sidebar_width)

        self._restore_form_state()
        self._initialize_validation_watchers()
        self._refresh_all_inline_messages()
        self._apply_sidebar_state(self.ui_config.sidebar_collapsed)

        self._refresh_dashboard()
    
    # ==================== 懒加载处理器属性 ====================
    def _get_processor(self, name, factory):
        """通用懒加载处理器获取方法"""
        if name not in self._processors:
            self._processors[name] = factory()
        return self._processors[name]
    
    @property
    def cross_project_translator(self):
        return self._get_processor('cross_project_translator', CrossProjectTranslatorWithCache)
    
    @property
    def json_detector(self):
        return self._get_processor('json_detector', JSONErrorDetector)
    
    @property
    def excel_processor(self):
        return self._get_processor('excel_processor', ExcelDataProcessor)
    
    @property
    def field_extractor(self):
        return self._get_processor('field_extractor', ExcelFieldExtractor)
    
    @property
    def table_range_translator(self):
        return self._get_processor('table_range_translator', TableRangeTranslator)
    
    @property
    def batch_modifier(self):
        return self._get_processor('batch_modifier', BatchExcelModifier)

    def _replace_processor(self, name, factory):
        """用新的处理器实例替换缓存，适用于必须隔离运行态的任务。"""
        processor = factory()
        self._processors[name] = processor
        return processor

    def _get_cross_project_page(self):
        """获取跨项目翻译页签控制器。"""
        if not hasattr(self, 'cross_project_page'):
            self.cross_project_page = CrossProjectPage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.cross_project_page

    def _get_table_range_page(self):
        """获取多语言翻译提取页签控制器。"""
        if not hasattr(self, 'table_range_page'):
            self.table_range_page = TableRangePage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.table_range_page

    def _get_field_extractor_page(self):
        """获取表字段导出页签控制器。"""
        if not hasattr(self, 'field_extractor_page'):
            self.field_extractor_page = FieldExtractorPage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.field_extractor_page

    def _get_batch_modifier_page(self):
        """获取批量改表页签控制器。"""
        if not hasattr(self, 'batch_modifier_page'):
            self.batch_modifier_page = BatchModifierPage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.batch_modifier_page

    def _get_excel_data_processor_page(self):
        """获取 Excel 数据处理页签控制器。"""
        if not hasattr(self, 'excel_data_processor_page'):
            self.excel_data_processor_page = ExcelDataProcessorPage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.excel_data_processor_page

    def _get_json_detector_page(self):
        """获取 JSON 检测页签控制器。"""
        if not hasattr(self, 'json_detector_page'):
            self.json_detector_page = JsonDetectorPage(self, TAB_DESCRIPTIONS, BUTTON_LABELS)
        return self.json_detector_page
    
    # ==================== 懒加载处理器属性 结束 ====================
    
    def setup_styles(self):
        """设置界面样式"""
        self.palette, self.style = apply_ui_theme(self.root, font_size=self.ui_config.font_size)

    def _resolve_runtime_asset(self, *relative_paths):
        """在开发环境与 PyInstaller 环境下定位资源文件。"""
        search_roots = []
        if hasattr(sys, '_MEIPASS'):
            search_roots.append(Path(sys._MEIPASS))

        current_dir = Path(__file__).resolve().parent
        search_roots.extend([current_dir, current_dir.parent, Path.cwd()])

        checked_paths = set()
        for root in search_roots:
            for relative_path in relative_paths:
                candidate = root / relative_path
                normalized = str(candidate)
                if normalized in checked_paths:
                    continue
                checked_paths.add(normalized)
                if candidate.exists():
                    return candidate
        return None

    def _apply_window_icon(self):
        """应用窗口与打包产物共享的图标资源。"""
        icon_path = self._resolve_runtime_asset(
            Path('gui_assets') / 'gametools.ico',
            Path('assets') / 'gametools.ico',
            Path('gui') / 'assets' / 'gametools.ico',
            Path('icon.ico'),
        )
        if not icon_path:
            return

        try:
            self.root.iconbitmap(str(icon_path))
        except Exception:
            logging.exception("加载窗口图标失败: %s", icon_path)

    def _apply_sidebar_width(self, width=None):
        """应用侧栏宽度配置。"""
        if not hasattr(self, 'sidebar_frame'):
            return

        try:
            sidebar_width = int(width or getattr(self.ui_config, 'sidebar_width', 240) or 240)
        except (TypeError, ValueError):
            sidebar_width = 240

        sidebar_width = max(220, min(sidebar_width, 320))
        self.sidebar_frame.configure(width=sidebar_width)
        self.sidebar_frame.grid_propagate(False)

    def _apply_saved_window_geometry(self):
        """按配置恢复窗口大小和位置。"""
        width = max(int(getattr(self.ui_config, 'window_width', 1260) or 1260), 980)
        height = max(int(getattr(self.ui_config, 'window_height', 820) or 820), 680)
        geometry = f"{width}x{height}"

        if (
            getattr(self.ui_config, 'auto_save_position', True)
            and getattr(self.ui_config, 'window_x', -1) >= 0
            and getattr(self.ui_config, 'window_y', -1) >= 0
        ):
            geometry += f"+{self.ui_config.window_x}+{self.ui_config.window_y}"

        self.root.geometry(geometry)

    def shutdown(self):
        """在关闭窗口前持久化界面状态。"""
        self._save_ui_preferences()

    def _save_ui_preferences(self):
        """保存窗口状态、当前页签和表单输入。"""
        try:
            self.root.update_idletasks()
            self.ui_config.window_width = max(self.root.winfo_width(), 980)
            self.ui_config.window_height = max(self.root.winfo_height(), 680)

            if getattr(self.ui_config, 'auto_save_position', True):
                self.ui_config.window_x = max(self.root.winfo_x(), 0)
                self.ui_config.window_y = max(self.root.winfo_y(), 0)

            self.ui_config.last_active_tab = self._get_current_tab_key()
            self.ui_config.sidebar_collapsed = self._sidebar_hidden
            self.ui_config.saved_form_state = self._collect_form_state()
            self.ui_config.recent_paths = {
                key: value
                for key, value in self.ui_config.saved_form_state.items()
                if isinstance(value, str) and (':' in value or '/' in value or '\\' in value)
            }
            config_manager.save_config()
        except Exception:
            logging.exception("保存界面状态失败")

    def _get_current_tab_key(self):
        """获取当前选中的页面 key。"""
        selected = self.notebook.select() if hasattr(self, 'notebook') else ''
        for meta in getattr(self, 'tab_registry', []):
            if str(meta['frame']) == selected:
                return meta['key']
        return 'about'

    def _get_form_state_vars(self):
        """收集需要持久化的输入变量。"""
        mappings = [
            ('json_detector.path', 'json_path_var'),
            ('excel.input', 'excel_input_var'),
            ('excel.output_folder', 'excel_output_folder_var'),
            ('excel.output_filename', 'excel_output_filename_var'),
            ('excel.group_column', 'excel_group_column_var'),
            ('excel.sheet_prefix', 'excel_sheet_prefix_var'),
            ('excel.include_summary', 'excel_include_summary_var'),
            ('cross.mapping', 'cpt_mapping_file_var'),
            ('cross.project_dir', 'cpt_project_dir_var'),
            ('cross.output_file', 'cpt_output_file_var'),
            ('field.zh_dir', 'field_zh_dir_var'),
            ('field.vn_dir', 'field_vn_dir_var'),
            ('field.th_dir', 'field_th_dir_var'),
            ('field.en_dir', 'field_en_dir_var'),
            ('field.output_dir', 'field_output_dir_var'),
            ('field.recursive', 'field_recursive_var'),
            ('field.output_format', 'field_output_format_var'),
            ('field.zh_enabled', 'field_zh_check_var'),
            ('field.vn_enabled', 'field_vn_check_var'),
            ('field.th_enabled', 'field_th_check_var'),
            ('field.en_enabled', 'field_en_check_var'),
            ('trt.merged_json', 'trt_merged_json_var'),
            ('trt.zh_dir', 'trt_zh_dir_var'),
            ('trt.vn_dir', 'trt_vn_dir_var'),
            ('trt.th_dir', 'trt_th_dir_var'),
            ('trt.en_dir', 'trt_en_dir_var'),
            ('trt.output_dir', 'trt_output_dir_var'),
            ('batch.json', 'batch_json_var'),
            ('batch.mapping', 'batch_mapping_var'),
            ('batch.excel_dir', 'batch_excel_dir_var'),
            ('batch.report', 'batch_report_var'),
            ('batch.language', 'batch_language_var'),
            ('batch.backup', 'batch_backup_var'),
            ('batch.field_row', 'batch_field_row_var'),
            ('batch.data_start_row', 'batch_data_start_row_var'),
        ]

        variables = {}
        for key, attr_name in mappings:
            if hasattr(self, attr_name):
                variables[key] = getattr(self, attr_name)
        return variables

    def _collect_form_state(self):
        """导出当前表单状态。"""
        state = {}
        for key, variable in self._get_form_state_vars().items():
            try:
                state[key] = variable.get()
            except Exception:
                continue
        return state

    def _apply_named_values(self, values):
        """按持久化 key 回填表单值。"""
        if not values:
            return

        variables = self._get_form_state_vars()
        self._is_restoring_state = True
        try:
            for key, value in values.items():
                variable = variables.get(key)
                if variable is None:
                    continue
                try:
                    variable.set(value)
                except Exception:
                    continue
        finally:
            self._is_restoring_state = False

        merged_json = getattr(self, 'trt_merged_json_var', None)
        if merged_json and merged_json.get().strip() and os.path.exists(merged_json.get().strip()):
            self._detect_merged_json_languages(merged_json.get().strip())

        batch_json = getattr(self, 'batch_json_var', None)
        if batch_json and batch_json.get().strip() and os.path.exists(batch_json.get().strip()):
            self._update_batch_json_language_label(batch_json.get().strip())

    def _restore_form_state(self):
        """恢复上次关闭前的表单输入。"""
        saved_state = getattr(self.ui_config, 'saved_form_state', {}) or {}
        if saved_state:
            self._apply_named_values(saved_state)

        merged_json = getattr(self, 'trt_merged_json_var', None)
        if merged_json and merged_json.get().strip() and os.path.exists(merged_json.get().strip()):
            self._detect_merged_json_languages(merged_json.get().strip())

        batch_json = getattr(self, 'batch_json_var', None)
        if batch_json and batch_json.get().strip() and os.path.exists(batch_json.get().strip()):
            self._update_batch_json_language_label(batch_json.get().strip())

    def _toggle_sidebar(self):
        """折叠或展开左侧导航。"""
        self._apply_sidebar_state(not self._sidebar_hidden)

    def _apply_sidebar_state(self, collapsed):
        """应用导航折叠状态。"""
        if not hasattr(self, 'sidebar_frame'):
            return

        self._sidebar_hidden = bool(collapsed)
        if self._sidebar_hidden:
            self.sidebar_frame.grid_remove()
        else:
            self.sidebar_frame.grid()

        if hasattr(self, 'sidebar_toggle_button'):
            self.sidebar_toggle_button.config(text="显示导航" if self._sidebar_hidden else "收起导航")

    def _create_inline_message(self, parent, row, columnspan=3):
        """在输入区域底部创建就地提示标签。"""
        label = tk.Label(
            parent,
            text='',
            anchor='w',
            justify='left',
            wraplength=620,
            bg=self.palette['surface'],
            fg=self.palette['muted_text'],
            font=('Microsoft YaHei UI', 9),
        )
        label.grid(row=row, column=0, columnspan=columnspan, sticky=(tk.W, tk.E), pady=(8, 0))
        return label

    def _set_inline_message(self, key, text='', tone='muted'):
        """更新页面就地校验提示。"""
        label = self.inline_messages.get(key)
        if not label:
            return

        color_map = {
            'muted': self.palette['muted_text'],
            'info': self.palette['info'],
            'success': self.palette['success'],
            'warning': self.palette['warning'],
            'error': self.palette['error'],
        }
        label.config(text=text, fg=color_map.get(tone, self.palette['muted_text']))

    def _create_task_panel(self, parent, task_key):
        """创建统一的任务状态卡片。"""
        card = tk.Frame(
            parent,
            bg=self.palette['surface'],
            highlightthickness=1,
            highlightbackground=self.palette['border'],
            padx=12,
            pady=12,
        )
        card.pack(fill=tk.X, pady=(14, 0))

        header = tk.Frame(card, bg=self.palette['surface'])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text='任务状态',
            bg=self.palette['surface'],
            fg=self.palette['text'],
            font=('Bahnschrift', 10, 'bold'),
        ).pack(side=tk.LEFT)

        status_var = tk.StringVar(value='尚未开始')
        status_label = tk.Label(
            header,
            textvariable=status_var,
            bg=self.palette['surface'],
            fg=self.palette['muted_text'],
            font=('Bahnschrift', 10, 'bold'),
        )
        status_label.pack(side=tk.RIGHT)

        progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(card, maximum=100, variable=progress_var).pack(fill=tk.X, pady=(10, 8))

        message_var = tk.StringVar(value='执行后会在这里显示过程进度')
        tk.Label(
            card,
            textvariable=message_var,
            bg=self.palette['surface'],
            fg=self.palette['muted_text'],
            justify='left',
            anchor='w',
            wraplength=250,
            font=('Microsoft YaHei UI', 9),
        ).pack(fill=tk.X)

        summary_var = tk.StringVar(value='最近结果摘要会显示在这里')
        tk.Label(
            card,
            textvariable=summary_var,
            bg=self.palette['surface'],
            fg=self.palette['text'],
            justify='left',
            anchor='w',
            wraplength=250,
            font=('Microsoft YaHei UI', 9),
        ).pack(fill=tk.X, pady=(10, 10))

        button_row = ttk.Frame(card)
        button_row.pack(fill=tk.X)
        ttk.Button(
            button_row,
            text='查看详情',
            style='Quiet.TButton',
            command=lambda key=task_key: self.show_results_dialog(TASK_RESULT_KEYS[key]),
        ).pack(side=tk.LEFT)

        self.task_panels[task_key] = {
            'card': card,
            'status_var': status_var,
            'status_label': status_label,
            'progress_var': progress_var,
            'message_var': message_var,
            'summary_var': summary_var,
        }

    def _build_summary_text(self, headline, metrics=None, detail=None):
        """构建任务摘要文本。"""
        lines = [headline]
        for label, value in (metrics or [])[:4]:
            lines.append(f"{label}: {value}")
        if detail:
            lines.append(detail)
        return '\n'.join(line for line in lines if line)

    def _set_task_panel_state(self, task_key, status_text, message=None, progress=None,
                              summary=None, tone='muted'):
        """刷新任务卡片内容。"""
        panel = self.task_panels.get(task_key)
        if not panel:
            return

        color_map = {
            'muted': self.palette['muted_text'],
            'info': self.palette['info'],
            'success': self.palette['success'],
            'warning': self.palette['warning'],
            'error': self.palette['error'],
        }
        panel['status_var'].set(status_text)
        panel['status_label'].config(fg=color_map.get(tone, self.palette['muted_text']))
        if message is not None:
            panel['message_var'].set(message)
        if progress is not None:
            panel['progress_var'].set(max(0, min(100, float(progress))))
        if summary is not None:
            panel['summary_var'].set(summary)

    def _begin_task_tracking(self, task_key, message, inputs=None):
        """记录任务开始状态。"""
        self.task_state[task_key] = {
            'status': 'running',
            'started_at': datetime.now().isoformat(timespec='seconds'),
            'inputs': dict(inputs or {}),
            'headline': '',
            'metrics': [],
            'detail': '',
        }
        self._set_task_panel_state(
            task_key,
            '进行中',
            message=message,
            progress=8,
            summary='等待处理结果...',
            tone='info',
        )

    def _update_task_progress(self, task_key, message, progress=None):
        """刷新任务执行中的过程信息。"""
        panel = self.task_panels.get(task_key)
        current_progress = panel['progress_var'].get() if panel else 0
        if progress is None:
            progress = min(current_progress + 6, 92)

        self._set_task_panel_state(
            task_key,
            '进行中',
            message=message,
            progress=progress,
            tone='info',
        )

    def _complete_task_tracking(self, task_key, status, headline, metrics=None, detail=None):
        """记录任务完成态，并写入最近任务列表。"""
        state = self.task_state.setdefault(task_key, {})
        state.update({
            'status': status,
            'headline': headline,
            'metrics': metrics or [],
            'detail': detail or '',
            'finished_at': datetime.now().isoformat(timespec='seconds'),
        })

        display_status = {
            'success': '已完成',
            'warning': '需注意',
            'error': '失败',
            'info': '已更新',
        }.get(status, status)

        summary_text = self._build_summary_text(headline, metrics, detail)
        self._set_task_panel_state(
            task_key,
            display_status,
            message=detail or headline,
            progress=100,
            summary=summary_text,
            tone=status,
        )
        self._record_recent_task(task_key, status, headline, metrics, detail, state.get('inputs', {}))

    def _record_recent_task(self, task_key, status, headline, metrics=None, detail=None, inputs=None):
        """记录最近执行任务，供关于页快速恢复。"""
        entry = {
            'key': task_key,
            'title': TASK_TITLES.get(task_key, task_key),
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'headline': headline,
            'detail': detail or '',
            'metrics': [
                {'label': label, 'value': str(value)}
                for label, value in (metrics or [])
            ],
            'inputs': dict(inputs or {}),
        }

        history = [
            item for item in getattr(self.ui_config, 'recent_tasks', [])
            if not (
                item.get('key') == task_key
                and item.get('headline') == headline
            )
        ]
        history.insert(0, entry)
        self.ui_config.recent_tasks = history[:8]
        config_manager.save_config()
        self._refresh_dashboard()

    def _open_recent_task(self, entry):
        """从关于页快速恢复最近一次任务输入。"""
        if not entry:
            return

        self._apply_named_values(entry.get('inputs', {}))
        task_key = entry.get('key')
        if task_key in self.tab_lookup:
            self.select_tab(task_key)
        self._refresh_all_inline_messages()

    def _collect_diagnostics_text(self):
        """收集打包版诊断信息摘要。"""
        log_dir = Path('logs')
        latest_log = None
        latest_error = '最近没有错误日志'

        if log_dir.exists():
            logs = sorted(log_dir.glob('*.log'), key=lambda item: item.stat().st_mtime, reverse=True)
            latest_log = logs[0] if logs else None

        if latest_log:
            try:
                with open(latest_log, 'r', encoding='utf-8') as file_obj:
                    tail_lines = file_obj.readlines()[-200:]
                for line in reversed(tail_lines):
                    if any(level in line for level in ('ERROR', 'CRITICAL', 'WARNING')):
                        latest_error = line.strip()
                        break
            except Exception:
                latest_error = '最近日志存在，但读取失败'

        engine_lines = []
        for module_name in ('xlwings', 'openpyxl', 'pandas'):
            engine_lines.append(f"{module_name}: {'可用' if importlib.util.find_spec(module_name) else '缺失'}")

        recent_task = (getattr(self.ui_config, 'recent_tasks', []) or [{}])[0]
        recent_task_text = recent_task.get('title', '暂无') if isinstance(recent_task, dict) else '暂无'

        lines = [
            f"版本: {format_version_string()}",
            f"构建日期: {get_build_date()}",
            f"Python: {sys.executable}",
            f"工作目录: {Path.cwd()}",
            f"配置文件: {config_manager.config_file.resolve()}",
            f"日志目录: {log_dir.resolve()}",
            f"最近记录: {recent_task_text}",
            f"最新日志: {latest_log.resolve() if latest_log else '暂无'}",
            f"最近错误: {latest_error}",
            "引擎状态: " + ' | '.join(engine_lines),
        ]
        return '\n'.join(lines)

    def _copy_diagnostics_to_clipboard(self):
        """复制诊断信息到剪贴板。"""
        diagnostics = self._collect_diagnostics_text()
        self.root.clipboard_clear()
        self.root.clipboard_append(diagnostics)
        self.root.update()
        messagebox.showinfo('成功', '诊断信息已复制到剪贴板')

    def _show_diagnostics_dialog(self):
        """显示完整诊断信息，避免关于页被技术细节淹没。"""
        snapshot = self._collect_diagnostics_snapshot()
        dialog = tk.Toplevel(self.root)
        dialog.title('环境诊断')
        dialog.geometry('760x560')
        dialog.minsize(640, 420)
        dialog.transient(self.root)

        container = ttk.Frame(dialog, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text=snapshot['status_title'],
            bg=self.palette['surface'],
            fg=self._resolve_tone_color(snapshot['status_tone']),
            font=('Bahnschrift', 13, 'bold'),
        ).pack(anchor=tk.W)

        ttk.Label(
            container,
            text='这里保留完整环境信息，关于页只显示对执行任务有帮助的摘要。',
            style='Info.TLabel',
        ).pack(anchor=tk.W, pady=(6, 12))

        result_text = scrolledtext.ScrolledText(
            container,
            wrap=tk.WORD,
            font=('Consolas', 9),
        )
        result_text.pack(fill=tk.BOTH, expand=True)
        result_text.insert('1.0', '\n'.join(snapshot['full_lines']))
        result_text.config(state='disabled')

        actions = ttk.Frame(container)
        actions.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(actions, text='复制诊断', style='Quiet.TButton', command=self._copy_diagnostics_to_clipboard).pack(side=tk.LEFT)
        ttk.Button(actions, text='关闭', style='Accent.TButton', command=dialog.destroy).pack(side=tk.RIGHT)

    def _resolve_tone_color(self, tone):
        """将状态 tone 转换为实际颜色。"""
        return {
            'muted': self.palette['muted_text'],
            'info': self.palette['info'],
            'success': self.palette['success'],
            'warning': self.palette['warning'],
            'error': self.palette['error'],
        }.get(tone, self.palette['text'])

    def _collect_diagnostics_snapshot(self):
        """收集关于页摘要和完整诊断所需的数据。"""
        log_dir = Path('logs')
        latest_log = None
        latest_issue = '最近没有错误或警告记录'
        latest_issue_tone = 'success'

        if log_dir.exists():
            logs = sorted(log_dir.glob('*.log'), key=lambda item: item.stat().st_mtime, reverse=True)
            latest_log = logs[0] if logs else None

        if latest_log:
            try:
                with open(latest_log, 'r', encoding='utf-8') as file_obj:
                    tail_lines = file_obj.readlines()[-200:]
                for line in reversed(tail_lines):
                    if 'CRITICAL' in line or 'ERROR' in line:
                        latest_issue = line.strip()
                        latest_issue_tone = 'error'
                        break
                    if 'WARNING' in line:
                        latest_issue = line.strip()
                        latest_issue_tone = 'warning'
                        break
            except Exception:
                latest_issue = '最近日志存在，但读取失败'
                latest_issue_tone = 'warning'
        else:
            latest_issue = '尚未生成运行日志，首次执行任务后会记录到 logs 目录'
            latest_issue_tone = 'info'

        available_engines = []
        missing_engines = []
        for module_name in ('xlwings', 'openpyxl', 'pandas'):
            if importlib.util.find_spec(module_name):
                available_engines.append(module_name)
            else:
                missing_engines.append(module_name)

        recent_task = (getattr(self.ui_config, 'recent_tasks', []) or [{}])[0]
        recent_task_text = recent_task.get('title', '暂无') if isinstance(recent_task, dict) else '暂无'

        status_tone = 'success'
        status_title = '环境状态正常'
        if latest_issue_tone == 'error':
            status_tone = 'error'
            status_title = '环境中有错误记录'
        elif latest_issue_tone == 'warning' or missing_engines:
            status_tone = 'warning'
            status_title = '环境需要关注'
        elif latest_issue_tone == 'info':
            status_tone = 'info'
            status_title = '首次运行前环境摘要'

        engine_summary = f"{len(available_engines)}/3 可用"
        if missing_engines:
            engine_summary += f"，缺少 {', '.join(missing_engines)}"

        summary_lines = [
            f"最近记录: {recent_task_text}",
            f"引擎状态: {engine_summary}",
            f"日志状态: {'已生成' if latest_log else '尚未生成'}",
        ]

        full_lines = [
            f"版本: {format_version_string()}",
            f"构建日期: {get_build_date()}",
            f"Python: {sys.executable}",
            f"工作目录: {Path.cwd()}",
            f"配置文件: {config_manager.config_file.resolve()}",
            f"日志目录: {log_dir.resolve()}",
            f"最近记录: {recent_task_text}",
            f"最新日志: {latest_log.resolve() if latest_log else '暂无'}",
            f"最近问题: {latest_issue}",
            "引擎状态: " + ' | '.join(
                f"{module_name}: {'可用' if module_name in available_engines else '缺失'}"
                for module_name in ('xlwings', 'openpyxl', 'pandas')
            ),
        ]

        return {
            'status_title': status_title,
            'status_tone': status_tone,
            'summary_lines': summary_lines,
            'latest_issue': latest_issue,
            'latest_issue_tone': latest_issue_tone,
            'full_lines': full_lines,
        }

    def _refresh_dashboard(self):
        """刷新关于页中的最近记录和诊断区域。"""
        recent_tasks = getattr(self.ui_config, 'recent_tasks', []) or []
        latest_entry = recent_tasks[0] if recent_tasks else None

        recent_title = self.dashboard_frames.get('recent_title')
        recent_detail = self.dashboard_frames.get('recent_detail')
        recent_action = self.dashboard_frames.get('recent_action')

        if latest_entry:
            recent_summary = latest_entry.get('headline') or latest_entry.get('title') or '最近记录'
            recent_meta = ' · '.join(
                part for part in (latest_entry.get('timestamp', ''), latest_entry.get('title', '')) if part
            )
            detail_lines = []
            if recent_meta:
                detail_lines.append(recent_meta)
            if latest_entry.get('detail'):
                detail_lines.append(latest_entry['detail'])
            if len(recent_tasks) > 1:
                detail_lines.append(f"另有 {len(recent_tasks) - 1} 条最近记录已收起保存。")
            if not detail_lines:
                detail_lines.append('可从这里继续上一次流程。')

            if recent_title:
                recent_title.config(text=recent_summary)
            if recent_detail:
                recent_detail.config(text='\n'.join(detail_lines))
            if recent_action:
                recent_action.config(
                    text='打开最近记录',
                    state=tk.NORMAL,
                    command=lambda item=latest_entry: self._open_recent_task(item),
                )
        else:
            if recent_title:
                recent_title.config(text='还没有最近记录')
            if recent_detail:
                recent_detail.config(text='执行任一功能后，最近记录会显示在这里，方便回到上次处理现场。')
            if recent_action:
                recent_action.config(text='等待最近记录', state=tk.DISABLED, command=lambda: None)

        snapshot = self._collect_diagnostics_snapshot()

        diagnostics_status = self.dashboard_frames.get('diagnostics_status')
        if diagnostics_status:
            diagnostics_status.config(
                text=snapshot['status_title'],
                fg=self._resolve_tone_color(snapshot['status_tone']),
            )

        diagnostics_summary = self.dashboard_frames.get('diagnostics_summary')
        if diagnostics_summary:
            diagnostics_summary.config(text=' · '.join(snapshot['summary_lines']))

    def _watch_vars(self, callback, *variables):
        """给变量绑定校验刷新回调。"""
        def handler(*_args):
            if self._is_restoring_state:
                return
            try:
                if self.root.winfo_exists():
                    callback()
            except tk.TclError:
                return

        for variable in variables:
            variable.trace_add('write', handler)

    def _initialize_validation_watchers(self):
        """初始化所有输入区的就地校验监听。"""
        if self._validation_watchers_ready:
            return

        self._watch_vars(self._refresh_json_validation, self.json_path_var)
        self._watch_vars(
            self._refresh_excel_validation,
            self.excel_input_var,
            self.excel_output_folder_var,
            self.excel_output_filename_var,
        )
        self._watch_vars(
            self._refresh_cpt_validation,
            self.cpt_mapping_file_var,
            self.cpt_project_dir_var,
            self.cpt_output_file_var,
        )
        self._watch_vars(
            self._refresh_field_validation,
            self.field_zh_dir_var,
            self.field_vn_dir_var,
            self.field_th_dir_var,
            self.field_en_dir_var,
            self.field_output_dir_var,
            self.field_zh_check_var,
            self.field_vn_check_var,
            self.field_th_check_var,
            self.field_en_check_var,
        )
        self._watch_vars(
            self._refresh_trt_validation,
            self.trt_merged_json_var,
            self.trt_zh_dir_var,
            self.trt_vn_dir_var,
            self.trt_th_dir_var,
            self.trt_en_dir_var,
            self.trt_output_dir_var,
        )
        self._watch_vars(
            self._refresh_batch_validation,
            self.batch_json_var,
            self.batch_mapping_var,
            self.batch_excel_dir_var,
            self.batch_report_var,
            self.batch_language_var,
            self.batch_field_row_var,
            self.batch_data_start_row_var,
        )
        self._validation_watchers_ready = True

    def _refresh_all_inline_messages(self):
        """刷新所有页面的当前输入提示。"""
        self._refresh_json_validation()
        self._refresh_excel_validation()
        self._refresh_cpt_validation()
        self._refresh_field_validation()
        self._refresh_trt_validation()
        self._refresh_batch_validation()

    def _validate_json_inputs(self, strict=False):
        path = self.json_path_var.get().strip()
        if not path:
            return False, '请选择单个 JSON 文件或目录后再开始检测。', 'error' if strict else 'warning'
        if not os.path.exists(path):
            return False, '当前路径不存在，请重新选择。', 'error'
        target = '目录' if os.path.isdir(path) else '单个文件'
        return True, f'将检测 {target}: {path}', 'success'

    def _validate_excel_inputs(self, strict=False):
        return self._get_excel_data_processor_page().validate_inputs(strict=strict)

    def _validate_cpt_inputs(self, strict=False):
        return self._get_cross_project_page().validate_inputs(strict=strict)

    def _validate_field_inputs(self, strict=False):
        return self._get_field_extractor_page().validate_inputs(strict=strict)

    def _validate_trt_inputs(self, strict=False):
        return self._get_table_range_page().validate_inputs(strict=strict)

    def _validate_batch_inputs(self, strict=False):
        return self._get_batch_modifier_page().validate_inputs(strict=strict)

    def _refresh_json_validation(self):
        _, text, tone = self._validate_json_inputs(strict=False)
        self._set_inline_message('json_detector', text, tone)

    def _refresh_excel_validation(self):
        self._get_excel_data_processor_page().refresh_validation()

    def _refresh_cpt_validation(self):
        self._get_cross_project_page().refresh_validation()

    def _refresh_field_validation(self):
        self._get_field_extractor_page().refresh_validation()

    def _refresh_trt_validation(self):
        self._get_table_range_page().refresh_validation()

    def _refresh_batch_validation(self):
        self._get_batch_modifier_page().refresh_validation()

    def _create_scrollable_tab_body(self, tab_key, tab_frame, padding):
        """为页签创建统一的滚动容器。"""
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(0, weight=1)

        scroll_host = ttk.Frame(tab_frame, style='App.TFrame')
        scroll_host.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_host.columnconfigure(0, weight=1)
        scroll_host.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            scroll_host,
            bg=self.palette['app_bg'],
            highlightthickness=0,
            borderwidth=0,
            relief='flat',
        )
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(scroll_host, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        body = ttk.Frame(canvas, padding=padding, style='Page.TFrame')
        body.columnconfigure(0, weight=1)
        window = canvas.create_window((0, 0), window=body, anchor='nw')

        self.tab_scroll_context[tab_key] = {
            'host': scroll_host,
            'canvas': canvas,
            'scrollbar': scrollbar,
            'body': body,
            'window': window,
            'scroll_enabled': False,
        }

        body.bind('<Configure>', lambda _event, key=tab_key: self._update_tab_scrollregion(key))
        canvas.bind('<Configure>', lambda event, key=tab_key: self._update_tab_canvas_width(key, event.width))
        scroll_host.bind('<Enter>', lambda _event, key=tab_key: self._bind_tab_mousewheel(key))
        scroll_host.bind('<Leave>', lambda _event, key=tab_key: self._unbind_tab_mousewheel(key))
        self.root.after_idle(lambda key=tab_key: self._refresh_tab_scrollbar(key))
        return body

    def _update_tab_scrollregion(self, tab_key):
        """同步页签滚动区域。"""
        context = self.tab_scroll_context.get(tab_key)
        if not context:
            return

        context['canvas'].configure(scrollregion=context['canvas'].bbox('all'))
        self._refresh_tab_scrollbar(tab_key)

    def _update_tab_canvas_width(self, tab_key, width):
        """让页签内容宽度跟随可视区域变化。"""
        context = self.tab_scroll_context.get(tab_key)
        if not context:
            return

        context['canvas'].itemconfigure(context['window'], width=width)
        self._refresh_tab_scrollbar(tab_key)

    def _refresh_tab_scrollbar(self, tab_key):
        """按内容高度决定是否显示页签滚动条。"""
        context = self.tab_scroll_context.get(tab_key)
        if not context:
            return

        bbox = context['canvas'].bbox('all')
        content_height = bbox[3] - bbox[1] if bbox else 0
        canvas_height = context['canvas'].winfo_height()
        should_scroll = canvas_height > 1 and content_height > canvas_height + 2
        context['scroll_enabled'] = should_scroll

        if should_scroll:
            if not context['scrollbar'].winfo_ismapped():
                context['scrollbar'].grid(row=0, column=1, sticky=(tk.N, tk.S))
        else:
            context['canvas'].yview_moveto(0)
            if context['scrollbar'].winfo_ismapped():
                context['scrollbar'].grid_remove()
            if self._active_tab_scroll_key == tab_key:
                self._unbind_tab_mousewheel(tab_key)

    def _bind_tab_mousewheel(self, tab_key):
        """鼠标进入页签内容区域后启用滚轮滚动。"""
        context = self.tab_scroll_context.get(tab_key)
        if context and context['scroll_enabled']:
            self._active_tab_scroll_key = tab_key
            self.notebook.bind_all('<MouseWheel>', self._on_tab_mousewheel)

    def _unbind_tab_mousewheel(self, tab_key=None):
        """鼠标离开页签内容区域后取消滚轮绑定。"""
        if tab_key is None or self._active_tab_scroll_key == tab_key:
            self._active_tab_scroll_key = None
            self.notebook.unbind_all('<MouseWheel>')

    def _on_tab_mousewheel(self, event):
        """处理页签内容区的滚轮滚动。"""
        if not event.delta or not self._active_tab_scroll_key:
            return

        context = self.tab_scroll_context.get(self._active_tab_scroll_key)
        if context and context['scroll_enabled']:
            context['canvas'].yview_scroll(int(-event.delta / 120), 'units')

    def _register_tab(self, key, title, description, padding="16"):
        """注册主工作区页面并保存导航信息。"""
        frame = ttk.Frame(self.notebook, style='App.TFrame')
        body = self._create_scrollable_tab_body(key, frame, padding)
        self.notebook.add(frame, text=title)
        self.tab_registry.append({
            'key': key,
            'title': title,
            'description': description,
            'frame': frame,
        })
        self.tab_lookup[key] = self.tab_registry[-1]
        return body

    def _get_tab_visual(self, key):
        """获取页面导航缩写和色块信息。"""
        return TAB_VISUALS.get(key, {'tag': 'GT', 'tone': self.palette['accent']})

    def _register_responsive_layout(self, layout_frame, left_column, right_column,
                                    left_weight=3, right_weight=2, breakpoint=940):
        """注册会在窄宽度下自动堆叠的双列布局。"""
        context = {
            'layout_frame': layout_frame,
            'left_column': left_column,
            'right_column': right_column,
            'left_weight': left_weight,
            'right_weight': right_weight,
            'breakpoint': breakpoint,
            'is_stacked': None,
        }
        self.responsive_layouts.append(context)
        layout_frame.bind('<Configure>', lambda event, ctx=context: self._apply_responsive_layout(ctx, event.width))
        self.root.after_idle(lambda ctx=context: self._apply_responsive_layout(ctx))
        return context

    def _apply_responsive_layout(self, context, width=None):
        """根据当前宽度在双列与单列堆叠之间切换。"""
        layout_frame = context['layout_frame']
        if not layout_frame.winfo_exists():
            return

        available_width = width or layout_frame.winfo_width()
        if available_width <= 1:
            return

        should_stack = available_width < context['breakpoint']
        if context['is_stacked'] == should_stack:
            return

        left_column = context['left_column']
        right_column = context['right_column']

        if should_stack:
            layout_frame.columnconfigure(0, weight=1)
            layout_frame.columnconfigure(1, weight=0)
            layout_frame.rowconfigure(0, weight=0)
            layout_frame.rowconfigure(1, weight=0)
            left_column.grid_configure(row=0, column=0, padx=(0, 0), pady=(0, 0))
            right_column.grid_configure(row=1, column=0, pady=(12, 0))
        else:
            layout_frame.columnconfigure(0, weight=context['left_weight'])
            layout_frame.columnconfigure(1, weight=context['right_weight'])
            layout_frame.rowconfigure(0, weight=1)
            layout_frame.rowconfigure(1, weight=0)
            left_column.grid_configure(row=0, column=0, padx=(0, 12), pady=(0, 0))
            right_column.grid_configure(row=0, column=1, pady=(0, 0))

        context['is_stacked'] = should_stack

    def _build_tab_columns(self, parent, left_weight=3, right_weight=2):
        """构建统一的响应式双列布局。"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        layout_frame = ttk.Frame(parent, style='Page.TFrame')
        layout_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        layout_frame.columnconfigure(0, weight=left_weight)
        layout_frame.columnconfigure(1, weight=right_weight)
        layout_frame.rowconfigure(0, weight=1)

        left_column = ttk.Frame(layout_frame, style='Page.TFrame')
        left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 12))
        left_column.columnconfigure(0, weight=1)

        right_column = ttk.Frame(layout_frame, style='Page.TFrame')
        right_column.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_column.columnconfigure(0, weight=1)

        self._register_responsive_layout(
            layout_frame,
            left_column,
            right_column,
            left_weight=left_weight,
            right_weight=right_weight,
            breakpoint=940,
        )

        return left_column, right_column

    def _set_batch_advanced_visibility(self, expanded):
        """切换批量改表页的高级选项显示状态。"""
        self._get_batch_modifier_page().set_advanced_visibility(expanded)

    def _toggle_batch_advanced_options(self):
        """展开或收起批量改表页的高级选项。"""
        self._get_batch_modifier_page().toggle_advanced_options()

    def _create_action_panel(self, parent, row, pady=(0, 0)):
        """创建侧边动作卡。"""
        panel = tk.Frame(
            parent,
            bg=self.palette['surface_alt'],
            highlightthickness=1,
            highlightbackground=self.palette['border'],
            padx=12,
            pady=12,
        )
        panel.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N), pady=pady)
        return panel

    def _format_section_title(self, step_number, title):
        """统一区块标题的步骤前缀。"""
        return f"{step_number}. {title}"

    def _decorate_action_panel(self, panel, title, description):
        """为右侧动作卡添加统一标题和说明。"""
        tk.Label(
            panel,
            text=title,
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            font=('Bahnschrift', 11, 'bold'),
        ).pack(anchor=tk.W)
        tk.Label(
            panel,
            text=description,
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            wraplength=280,
            justify='left',
            font=('Microsoft YaHei UI', 9),
        ).pack(anchor=tk.W, pady=(6, 12))

    def _create_action_strip(self, parent, row, pady=(8, 0)):
        """创建紧凑操作条，减少按钮区的散乱感。"""
        strip_card = self._create_action_panel(parent, row, pady=pady)

        strip_frame = ttk.Frame(strip_card, style='Page.TFrame')
        strip_frame.pack(anchor=tk.W, fill=tk.X)
        return strip_frame

    def _tab_visibility_enabled(self, key: str) -> bool:
        """模块页签是否应在侧栏与 Notebook 中显示（about 始终显示）。"""
        if key == 'about':
            return True
        return bool(getattr(config_manager.config.tabs, key, True))

    def _build_navigation(self):
        """构建左侧导航。"""
        self.nav_widgets = {}
        meta_by_key = {meta['key']: meta for meta in self.tab_registry}

        for section_title, section_keys in NAV_SECTIONS:
            section_items = [
                meta_by_key[key]
                for key in section_keys
                if key in meta_by_key and self._tab_visibility_enabled(key)
            ]
            if not section_items:
                continue

            section_frame = tk.Frame(self.nav_items_frame, bg=self.palette['sidebar_bg'])
            section_frame.pack(fill=tk.X, pady=(0, 14))

            section_header = tk.Frame(section_frame, bg=self.palette['sidebar_bg'])
            section_header.pack(fill=tk.X, pady=(0, 6))
            section_header.grid_columnconfigure(1, weight=1)

            tk.Label(
                section_header,
                text=section_title,
                bg=self.palette['sidebar_bg'],
                fg=self.palette['sidebar_muted'],
                font=('Microsoft YaHei UI', 8, 'bold'),
            ).grid(row=0, column=0, sticky=tk.W)
            tk.Frame(section_header, bg=self.palette['sidebar_hover'], height=1).grid(
                row=0, column=1, sticky=(tk.W, tk.E), padx=(8, 0)
            )

            for meta in section_items:
                visual = self._get_tab_visual(meta['key'])
                card = tk.Frame(
                    section_frame,
                    bg=self.palette['sidebar_bg'],
                    highlightthickness=1,
                    highlightbackground=self.palette['sidebar_hover'],
                    cursor='hand2',
                )
                card.pack(fill=tk.X, pady=(0, 4))

                edge = tk.Frame(card, bg=self.palette['sidebar_bg'], width=4)
                edge.pack(side=tk.LEFT, fill=tk.Y)

                content = tk.Frame(card, bg=self.palette['sidebar_bg'], padx=10, pady=8)
                content.pack(side=tk.LEFT, fill=tk.X, expand=True)
                content.grid_columnconfigure(1, weight=1)

                icon_box = tk.Frame(content, bg=visual['tone'], width=30, height=30)
                icon_box.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
                icon_box.grid_propagate(False)

                icon_label = tk.Label(
                    icon_box,
                    text=visual['tag'],
                    bg=visual['tone'],
                    fg=self.palette['accent_text'],
                    font=('Bahnschrift', 9, 'bold'),
                )
                icon_label.place(relx=0.5, rely=0.5, anchor='center')

                title_label = tk.Label(
                    content,
                    text=meta['title'],
                    bg=self.palette['sidebar_bg'],
                    fg=self.palette['sidebar_text'],
                    anchor='w',
                    font=('Microsoft YaHei UI', 9, 'bold'),
                )
                title_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

                for widget in (card, edge, content, icon_box, icon_label, title_label):
                    widget.bind('<Button-1>', lambda _event, tab_key=meta['key']: self.select_tab(tab_key))

                self.nav_widgets[meta['key']] = {
                    'card': card,
                    'edge': edge,
                    'content': content,
                    'icon_box': icon_box,
                    'icon_label': icon_label,
                    'title': title_label,
                    'tone': visual['tone'],
                }

    def _update_nav_scrollregion(self, _event=None):
        """同步导航滚动区域。"""
        self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox('all'))
        self._refresh_nav_scrollbar()

    def _refresh_nav_scrollbar(self):
        """仅在导航内容超出可视区域时显示滚动条。"""
        if not hasattr(self, 'nav_scrollbar'):
            return

        bbox = self.nav_canvas.bbox('all')
        content_height = bbox[3] - bbox[1] if bbox else 0
        canvas_height = self.nav_canvas.winfo_height()
        should_scroll = canvas_height > 1 and content_height > canvas_height + 2

        if should_scroll:
            if not self.nav_scrollbar.winfo_ismapped():
                self.nav_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        else:
            self.nav_canvas.yview_moveto(0)
            if self.nav_scrollbar.winfo_ismapped():
                self.nav_scrollbar.grid_remove()
            self._unbind_nav_mousewheel()

        self.nav_scroll_enabled = should_scroll

    def _update_nav_canvas_width(self, event):
        """让导航内容宽度跟随侧栏宽度变化。"""
        self.nav_canvas.itemconfigure(self.nav_canvas_window, width=event.width)
        self._refresh_nav_scrollbar()

    def _bind_nav_mousewheel(self, _event=None):
        """鼠标进入导航区域后启用滚轮滚动。"""
        if self.nav_scroll_enabled:
            self.nav_canvas.bind_all('<MouseWheel>', self._on_nav_mousewheel)

    def _unbind_nav_mousewheel(self, _event=None):
        """鼠标离开导航区域后取消滚轮绑定，避免影响其他区域。"""
        self.nav_canvas.unbind_all('<MouseWheel>')

    def _on_nav_mousewheel(self, event):
        """处理 Windows 下的鼠标滚轮滚动。"""
        if self.nav_scroll_enabled and event.delta:
            self.nav_canvas.yview_scroll(int(-event.delta / 120), 'units')

    def _update_navigation_state(self, active_key):
        """刷新导航高亮状态。"""
        for key, widgets in self.nav_widgets.items():
            is_active = key == active_key
            widgets['card'].configure(
                bg=self.palette['sidebar_active'] if is_active else self.palette['sidebar_bg'],
                highlightbackground=self.palette['accent'] if is_active else self.palette['sidebar_hover'],
            )
            widgets['edge'].configure(
                bg=self.palette['accent'] if is_active else self.palette['sidebar_bg'],
            )
            widgets['content'].configure(
                bg=self.palette['sidebar_active'] if is_active else self.palette['sidebar_bg'],
            )
            widgets['icon_box'].configure(
                bg=self.palette['accent'] if is_active else widgets['tone'],
            )
            widgets['icon_label'].configure(
                bg=self.palette['accent'] if is_active else widgets['tone'],
            )
            widgets['title'].configure(
                bg=self.palette['sidebar_active'] if is_active else self.palette['sidebar_bg'],
                fg=self.palette['sidebar_text'],
            )

    def _sync_header_with_current_tab(self, _event=None):
        """根据当前页面刷新头部标题。"""
        selected = self.notebook.select()
        self._unbind_tab_mousewheel()
        for meta in self.tab_registry:
            if str(meta['frame']) == selected:
                self.page_title_var.set(meta['title'])
                self.page_desc_var.set(meta['description'])
                self.page_tag_var.set(self._get_tab_visual(meta['key'])['tag'])
                self._update_navigation_state(meta['key'])
                self._refresh_tab_scrollbar(meta['key'])
                break

    def select_tab(self, key):
        """通过侧边导航切换页面。"""
        meta = self.tab_lookup.get(key)
        if not meta:
            return
        if not self._tab_visibility_enabled(key):
            key = self._get_default_tab_key()
            meta = self.tab_lookup.get(key)
            if not meta:
                return
        self.notebook.select(meta['frame'])
        self._sync_header_with_current_tab()

    def _get_default_tab_key(self):
        """返回启动时应选中的默认页面。"""
        if 'home' in self.tab_lookup and self._tab_visibility_enabled('home'):
            return 'home'
        for _section_title, keys in NAV_SECTIONS:
            for key in keys:
                if key != 'about' and key in self.tab_lookup and self._tab_visibility_enabled(key):
                    return key
        if self.tab_registry:
            for meta in self.tab_registry:
                if self._tab_visibility_enabled(meta['key']):
                    return meta['key']
        return 'about'

    def _apply_tabs_visibility_runtime(self):
        """根据 config.tabs 立即同步 Notebook 页签与侧栏（保存界面设置后调用）。"""
        for meta in self.tab_registry:
            key = meta['key']
            if key == 'about':
                continue
            frame = meta['frame']
            if not self._tab_visibility_enabled(key) and str(frame) in self.notebook.tabs():
                # Windows 部分 Tk 版本上 hide() 不会真正移除页签，forget 可稳定同步侧栏与主区
                self.notebook.forget(frame)

        visible_metas = [m for m in self.tab_registry if self._tab_visibility_enabled(m['key'])]
        for idx, meta in enumerate(visible_metas):
            frame = meta['frame']
            if str(frame) not in self.notebook.tabs():
                self.notebook.insert(idx, frame, text=meta['title'])
            else:
                cur = self.notebook.index(frame)
                if cur != idx:
                    self.notebook.insert(idx, frame, text=meta['title'])

        selected = self.notebook.select()
        current_key = None
        for meta in self.tab_registry:
            if str(meta['frame']) == selected:
                current_key = meta['key']
                break
        if current_key is not None and not self._tab_visibility_enabled(current_key):
            self.select_tab(self._get_default_tab_key())

        for child in self.nav_items_frame.winfo_children():
            child.destroy()
        self._build_navigation()
        self.root.after_idle(self._update_nav_scrollregion)

    def create_widgets(self):
        """创建界面控件"""
        self.tab_registry = []
        self.tab_lookup = {}

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        app_frame = ttk.Frame(self.root, style='App.TFrame', padding=18)
        app_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        app_frame.columnconfigure(1, weight=1)
        app_frame.rowconfigure(0, weight=1)

        self.sidebar_frame = tk.Frame(
            app_frame,
            bg=self.palette['sidebar_bg'],
            width=max(int(getattr(self.ui_config, 'sidebar_width', 240) or 240), 220),
        )
        self.sidebar_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 16))
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.columnconfigure(0, weight=1)
        self.sidebar_frame.rowconfigure(1, weight=1)

        brand_frame = tk.Frame(self.sidebar_frame, bg=self.palette['sidebar_bg'])
        brand_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=18, pady=(20, 16))

        brand_mark = tk.Frame(brand_frame, bg=self.palette['accent'], height=5, width=48)
        brand_mark.pack(anchor=tk.W, pady=(0, 14))

        ttk.Label(brand_frame, text="GameTools", style='SidebarTitle.TLabel').pack(anchor=tk.W)
        tk.Label(
            brand_frame,
            text='本地化统一工作流',
            bg=self.palette['sidebar_bg'],
            fg=self.palette['sidebar_muted'],
            font=('Microsoft YaHei UI', 8),
        ).pack(anchor=tk.W, pady=(6, 0))
        ttk.Label(
            brand_frame,
            text=f"v{get_version()}",
            style='SidebarMeta.TLabel',
        ).pack(anchor=tk.W, pady=(4, 0))

        nav_container = tk.Frame(self.sidebar_frame, bg=self.palette['sidebar_bg'])
        nav_container.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(12, 8), pady=(0, 12))
        nav_container.columnconfigure(0, weight=1)
        nav_container.rowconfigure(0, weight=1)

        self.nav_scroll_enabled = False

        self.nav_canvas = tk.Canvas(
            nav_container,
            bg=self.palette['sidebar_bg'],
            highlightthickness=0,
            borderwidth=0,
            relief='flat',
        )
        self.nav_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.nav_scrollbar = ttk.Scrollbar(nav_container, orient='vertical', command=self.nav_canvas.yview)
        self.nav_canvas.configure(yscrollcommand=self.nav_scrollbar.set)

        self.nav_items_frame = tk.Frame(self.nav_canvas, bg=self.palette['sidebar_bg'])
        self.nav_canvas_window = self.nav_canvas.create_window((0, 0), window=self.nav_items_frame, anchor='nw')
        self.nav_items_frame.bind('<Configure>', self._update_nav_scrollregion)
        self.nav_canvas.bind('<Configure>', self._update_nav_canvas_width)
        self.nav_canvas.bind('<Enter>', self._bind_nav_mousewheel)
        self.nav_canvas.bind('<Leave>', self._unbind_nav_mousewheel)
        self.nav_items_frame.bind('<Enter>', self._bind_nav_mousewheel)
        self.nav_items_frame.bind('<Leave>', self._unbind_nav_mousewheel)
        self.root.after_idle(self._refresh_nav_scrollbar)

        sidebar_footer = tk.Frame(self.sidebar_frame, bg=self.palette['sidebar_bg'])
        sidebar_footer.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=18, pady=(4, 18))

        footer_rule = tk.Frame(sidebar_footer, bg=self.palette['sidebar_hover'], height=1)
        footer_rule.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(sidebar_footer, text="统一工作流", style='SidebarMeta.TLabel').pack(anchor=tk.W)

        workspace_frame = ttk.Frame(app_frame, style='App.TFrame')
        workspace_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        workspace_frame.columnconfigure(0, weight=1)
        workspace_frame.rowconfigure(1, weight=1)

        header_frame = tk.Frame(
            workspace_frame,
            bg=self.palette['surface_alt'],
            highlightthickness=1,
            highlightbackground=self.palette['border'],
            padx=18,
            pady=14,
        )
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        self.page_title_var = tk.StringVar(value="关于")
        self.page_desc_var = tk.StringVar(value=TAB_DESCRIPTIONS['about'])
        self.page_tag_var = tk.StringVar(value="GT")

        title_block = tk.Frame(header_frame, bg=self.palette['surface_alt'])
        title_block.grid(row=0, column=0, sticky=(tk.W, tk.E))
        title_block.grid_columnconfigure(0, weight=1)

        ttk.Label(title_block, textvariable=self.page_title_var, style='HeaderTitle.TLabel').grid(
            row=0, column=0, sticky=tk.W
        )
        tk.Label(
            title_block,
            textvariable=self.page_desc_var,
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            font=('Microsoft YaHei UI', 9),
            anchor='w',
            justify='left',
        ).grid(row=1, column=0, sticky=tk.W, pady=(4, 0))

        meta_frame = tk.Frame(header_frame, bg=self.palette['surface_alt'])
        meta_frame.grid(row=0, column=1, sticky=tk.E)
        ttk.Label(meta_frame, textvariable=self.page_tag_var, style='HeaderTag.TLabel').pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            meta_frame,
            text=f"v{get_version()}",
            bg=self.palette['surface_alt'],
            fg=self.palette['accent'],
            font=('Bahnschrift', 10, 'bold'),
        ).pack(side=tk.LEFT, padx=(0, 12))
        self.sidebar_toggle_button = ttk.Button(
            meta_frame,
            text='收起导航',
            style='Quiet.TButton',
            command=self._toggle_sidebar,
        )
        self.sidebar_toggle_button.pack(side=tk.LEFT)

        content_frame = ttk.Frame(workspace_frame, style='App.TFrame')
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(content_frame, style='Navigation.TNotebook')
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.notebook.bind('<<NotebookTabChanged>>', self._sync_header_with_current_tab)
        
        # 获取页签可见性配置
        tabs_config = config_manager.config.tabs

        # 路径变量先于各页签创建，工作台与各功能页共用同一 StringVar 以实现同步
        self._init_workspace_path_vars()
        if getattr(tabs_config, 'home', True):
            self.create_home_tab()
        
        # 创建各个功能页签（根据配置决定是否显示）
        if tabs_config.cross_project_translator:
            self.create_cross_project_translator_tab()
        if tabs_config.json_detector:
            self.create_json_detector_tab()
        if tabs_config.excel_data_processor:
            self.create_excel_data_processor_tab()
        if tabs_config.field_extractor:
            self.create_field_extractor_tab()
        if tabs_config.table_range_translator:
            self.create_table_range_translator_tab()
        if tabs_config.batch_modifier:
            self.create_batch_modifier_tab()
        
        # 关于页签（始终显示）
        self.create_about_tab()

        self._build_navigation()
        if self.tab_registry:
            self.select_tab(self._get_default_tab_key())

        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(workspace_frame, textvariable=self.status_var, style='Status.TLabel', anchor=tk.W)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(12, 0))
    
    def _init_workspace_path_vars(self):
        """在创建页签前初始化路径型 StringVar，供工作台与各功能页共用（一处修改、处处同步）。"""
        self.field_zh_dir_var = tk.StringVar()
        self.field_vn_dir_var = tk.StringVar()
        self.field_th_dir_var = tk.StringVar()
        self.field_en_dir_var = tk.StringVar()
        self.trt_zh_dir_var = self.field_zh_dir_var
        self.trt_vn_dir_var = self.field_vn_dir_var
        self.trt_th_dir_var = self.field_th_dir_var
        self.trt_en_dir_var = self.field_en_dir_var

        self.field_output_dir_var = tk.StringVar()
        self.trt_output_dir_var = self.field_output_dir_var

        self.field_zh_check_var = tk.BooleanVar(value=True)
        self.field_vn_check_var = tk.BooleanVar(value=True)
        self.field_th_check_var = tk.BooleanVar(value=True)
        self.field_en_check_var = tk.BooleanVar(value=False)
        self.field_recursive_var = tk.BooleanVar(value=False)
        self.field_output_format_var = tk.StringVar(value="json")

        self.trt_merged_json_var = tk.StringVar()
        self.trt_output_var = tk.StringVar()
        self.trt_zh_json_var = tk.StringVar()
        self.trt_vn_json_var = tk.StringVar()
        self.trt_th_json_var = tk.StringVar()
        self.trt_en_json_var = tk.StringVar()
        self.trt_json_var = self.trt_merged_json_var

        self.json_path_var = tk.StringVar()
        self.excel_input_var = tk.StringVar()
        self.excel_output_folder_var = tk.StringVar()
        self.excel_output_filename_var = tk.StringVar(value='整合结果.xlsx')
        self.excel_group_column_var = tk.StringVar()
        self.excel_sheet_prefix_var = tk.StringVar()
        self.excel_include_summary_var = tk.BooleanVar(value=True)

        self.cpt_mapping_file_var = tk.StringVar()
        self.cpt_project_dir_var = tk.StringVar()
        self.cpt_output_file_var = tk.StringVar()

        self.batch_json_var = tk.StringVar()
        self.batch_mapping_var = tk.StringVar()
        self.batch_excel_dir_var = tk.StringVar()
        self.batch_report_var = tk.StringVar()

        self.batch_language_var = tk.StringVar(value='VN')
        self.batch_sheet_var = tk.StringVar()
        self.batch_auto_match_var = tk.BooleanVar(value=False)
        self.batch_table_col_var = tk.StringVar(value='')
        self.batch_id_col_var = tk.StringVar(value='ID')
        self.batch_field_col_var = tk.StringVar(value='Classification')
        self.batch_advanced_toggle_var = tk.StringVar(value='展开高级选项')
        self.batch_backup_var = tk.BooleanVar(value=True)
        self.batch_data_start_row_var = tk.StringVar(value=str(DATA_START_ROW))
        self.batch_field_row_var = tk.StringVar(value=str(FIELD_NAME_ROW))

    def _home_add_path_row(self, parent, row, label_text, string_var, browse_command):
        """工作台单行：标签 + 路径输入 + 浏览。"""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 6),
        )
        ttk.Entry(parent, textvariable=string_var, font=('Microsoft YaHei', 9)).grid(
            row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 6),
        )
        ttk.Button(
            parent, text='选择', command=browse_command, style='Subtle.TButton',
        ).grid(row=row, column=2, pady=(0, 6))

    def _workspace_path_display(self, parent, textvariable, **grid_kw):
        """各功能页只读路径展示（与工作台共用 StringVar，纯文本无输入框样式）。"""
        lbl = ttk.Label(
            parent,
            font=('Microsoft YaHei', 9),
            anchor=tk.W,
            justify=tk.LEFT,
        )

        def _sync(*_args):
            raw = textvariable.get()
            v = (raw or '').strip()
            lbl.configure(text=v if v else '暂无')

        textvariable.trace_add('write', _sync)
        _sync()
        lbl.grid(**grid_kw)
        return lbl

    def create_home_tab(self):
        """工作台：集中选择目录与常用文件路径，与各功能页输入框绑定同一变量。"""
        body = self._register_tab(
            'home',
            '工作台',
            TAB_DESCRIPTIONS['home'],
        )
        body.columnconfigure(0, weight=1)

        intro = ttk.Label(
            body,
            text=(
                '以下路径与各功能页中的只读路径展示绑定同一变量：在此用「选择」修改后，各页立即同步；'
                '功能页不再提供浏览按钮，请在本页完成路径配置。可按当日任务只填需要的项。'
            ),
            style='Info.TLabel',
            wraplength=780,
            justify='left',
        )
        intro.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 14))

        main = ttk.Frame(body)
        main.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main.columnconfigure((0, 1), weight=1, uniform='home_cols')

        left = ttk.LabelFrame(main, text=self._format_section_title(1, '本地化主路径'), padding=12)
        left.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 8))
        left.columnconfigure(1, weight=1)

        r = 0
        for label, var, cmd in (
            ('中文表目录:', self.field_zh_dir_var, lambda: self.browse_field_language_dir('zh')),
            ('越南语表目录:', self.field_vn_dir_var, lambda: self.browse_field_language_dir('vn')),
            ('泰语表目录:', self.field_th_dir_var, lambda: self.browse_field_language_dir('th')),
            ('英语表目录:', self.field_en_dir_var, lambda: self.browse_field_language_dir('en')),
        ):
            self._home_add_path_row(left, r, label, var, cmd)
            r += 1
        self._home_add_path_row(
            left, r, '导出 / 多语言输出目录:', self.field_output_dir_var, self.browse_field_output_directory,
        )
        r += 1
        self._home_add_path_row(
            left, r, '合并 JSON（多语言提取）:', self.trt_merged_json_var, self.browse_trt_merged_json,
        )
        r += 1
        self.inline_messages['home'] = self._create_inline_message(left, row=r, columnspan=3)

        right = ttk.LabelFrame(main, text=self._format_section_title(2, '其它工具路径'), padding=12)
        right.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), padx=(8, 0))
        right.columnconfigure(1, weight=1)

        r2 = 0
        for label, var, cmd in (
            ('JSON 检测目录:', self.json_path_var, self.browse_json_folder),
            ('Excel 整合源文件:', self.excel_input_var, self.browse_excel_input_file),
            ('Excel 整合输出目录:', self.excel_output_folder_var, self.browse_excel_output_folder),
            ('跨项目映射文件:', self.cpt_mapping_file_var, self.browse_cpt_mapping_file),
            ('跨项目扫描目录:', self.cpt_project_dir_var, self.browse_cpt_project_directory),
            ('跨项目输出文件:', self.cpt_output_file_var, self.browse_cpt_output_file),
            ('批量改表 JSON:', self.batch_json_var, self.browse_batch_json_file),
            ('批量改表映射:', self.batch_mapping_var, self.browse_batch_mapping_file),
            ('批量改表 Excel 目录:', self.batch_excel_dir_var, self.browse_batch_excel_directory),
            ('批量改表报告文件:', self.batch_report_var, self.browse_batch_report_file),
        ):
            self._home_add_path_row(right, r2, label, var, cmd)
            r2 += 1

    def create_cross_project_translator_tab(self):
        """创建跨项目翻译对应页签"""
        self._get_cross_project_page().build()
    
    
    def create_json_detector_tab(self):
        """创建JSON错误检测工具页签"""
        self._get_json_detector_page().build()
    
    def create_excel_data_processor_tab(self):
        """创建Excel数据处理工具页签"""
        self._get_excel_data_processor_page().build()

    def create_field_extractor_tab(self):
        """创建表字段导出页签"""
        self._get_field_extractor_page().build()
    
    def create_table_range_translator_tab(self):
        """创建多语言翻译提取页签"""
        self._get_table_range_page().build()
    
    def create_batch_modifier_tab(self):
        """创建批量改表页签"""
        self._get_batch_modifier_page().build()

    def create_about_tab(self):
        """创建关于页。"""
        about_frame = self._register_tab(
            'about',
            '关于',
            TAB_DESCRIPTIONS['about'],
            padding="18"
        )

        about_frame.columnconfigure(0, weight=1)
        about_frame.rowconfigure(2, weight=1)

        intro_frame = tk.Frame(
            about_frame,
            bg=self.palette['surface_alt'],
            highlightthickness=1,
            highlightbackground=self.palette['border'],
            padx=20,
            pady=16,
        )
        intro_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        intro_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            intro_frame,
            text='GameTools',
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            font=('Bahnschrift', 18, 'bold'),
        ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(
            intro_frame,
            text='统一处理改表、提取、翻译和检测，关于页集中展示版本、模块和诊断信息。',
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            font=('Microsoft YaHei UI', 9),
            anchor='w',
            justify='left',
        ).grid(row=1, column=0, sticky=tk.W, pady=(6, 0))

        intro_actions = tk.Frame(intro_frame, bg=self.palette['surface_alt'])
        intro_actions.grid(row=0, column=1, rowspan=2, sticky=tk.E)
        ttk.Button(intro_actions, text='界面设置', style='Quiet.TButton', command=self.show_settings_dialog).pack(side=tk.LEFT)
        ttk.Button(intro_actions, text='查看诊断', style='Quiet.TButton', command=self._show_diagnostics_dialog).pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(
            intro_actions,
            text=f"v{get_version()}",
            bg=self.palette['surface_alt'],
            fg=self.palette['accent'],
            font=('Bahnschrift', 10, 'bold'),
        ).pack(side=tk.LEFT, padx=(12, 0))

        def create_about_card(parent, title, row, column):
            card = tk.Frame(
                parent,
                bg=self.palette['surface_alt'],
                highlightthickness=1,
                highlightbackground=self.palette['border'],
                padx=18,
                pady=16,
            )
            card.grid(row=row, column=column, sticky=(tk.W, tk.E, tk.N, tk.S))
            card.grid_columnconfigure(0, weight=1)
            tk.Label(
                card,
                text=title,
                bg=self.palette['surface_alt'],
                fg=self.palette['text'],
                font=('Bahnschrift', 12, 'bold'),
                anchor='w',
            ).grid(row=0, column=0, sticky=tk.W)
            return card

        enabled_titles = [
            self.tab_lookup[key]['title']
            for _section_title, keys in NAV_SECTIONS
            for key in keys
            if key != 'about' and key in self.tab_lookup
        ]
        default_tab_title = self.tab_lookup.get(self._get_default_tab_key(), {}).get('title', '关于')

        info_frame = ttk.LabelFrame(about_frame, text='工具信息', padding=14)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

        overview_card = create_about_card(info_frame, '定位与能力', row=0, column=0)
        tk.Label(
            overview_card,
            text='GameTools 面向策划本地化流程，统一收纳批量改表、多语言提取、字段导出和检测能力，减少多入口切换。',
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            wraplength=360,
            justify='left',
            font=('Microsoft YaHei UI', 9),
        ).grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        tk.Label(
            overview_card,
            text='当前启用模块',
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            font=('Microsoft YaHei UI', 9),
        ).grid(row=2, column=0, sticky=tk.W, pady=(14, 0))
        tk.Label(
            overview_card,
            text='、'.join(enabled_titles) if enabled_titles else '当前没有启用功能模块，可在界面设置中开启。',
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            wraplength=360,
            justify='left',
            font=('Microsoft YaHei UI', 9),
        ).grid(row=3, column=0, sticky=tk.W, pady=(6, 0))
        ttk.Button(
            overview_card,
            text='管理模块显示',
            style='Subtle.TButton',
            command=self.show_settings_dialog,
        ).grid(row=4, column=0, sticky=tk.W, pady=(12, 0))

        version_card = create_about_card(info_frame, '版本与环境', row=0, column=1)
        version_card.columnconfigure(1, weight=1)
        version_rows = [
            ('当前版本', format_version_string()),
            ('构建日期', get_build_date()),
            ('Python 环境', f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ('默认入口', default_tab_title),
        ]
        for index, (label_text, value_text) in enumerate(version_rows, start=1):
            tk.Label(
                version_card,
                text=label_text,
                bg=self.palette['surface_alt'],
                fg=self.palette['muted_text'],
                font=('Microsoft YaHei UI', 9),
            ).grid(row=index, column=0, sticky=tk.W, pady=(8 if index == 1 else 10, 0), padx=(0, 14))
            tk.Label(
                version_card,
                text=value_text,
                bg=self.palette['surface_alt'],
                fg=self.palette['text'],
                font=('Bahnschrift', 10, 'bold') if index < 3 else ('Microsoft YaHei UI', 9),
                anchor='w',
                justify='left',
            ).grid(row=index, column=1, sticky=(tk.W, tk.E), pady=(8 if index == 1 else 10, 0))

        self._register_responsive_layout(
            info_frame,
            overview_card,
            version_card,
            left_weight=1,
            right_weight=1,
            breakpoint=940,
        )

        status_frame = ttk.LabelFrame(about_frame, text='状态与支持', padding=14)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)

        recent_panel = create_about_card(status_frame, '最近记录', row=0, column=0)
        recent_title = tk.Label(
            recent_panel,
            text='还没有最近记录',
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            justify='left',
            anchor='w',
            font=('Bahnschrift', 12, 'bold'),
        )
        recent_title.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        recent_detail = tk.Label(
            recent_panel,
            text='执行任一功能后，最近记录会显示在这里，方便回到上次处理现场。',
            bg=self.palette['surface_alt'],
            fg=self.palette['muted_text'],
            justify='left',
            anchor='w',
            wraplength=360,
            font=('Microsoft YaHei UI', 9),
        )
        recent_detail.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        recent_action = ttk.Button(
            recent_panel,
            text='等待最近记录',
            style='Quiet.TButton',
            state=tk.DISABLED,
        )
        recent_action.grid(row=3, column=0, sticky=tk.W, pady=(12, 0))

        diagnostics_panel = create_about_card(status_frame, '环境诊断', row=0, column=1)
        diagnostics_status = tk.Label(
            diagnostics_panel,
            text='环境状态读取中...',
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            justify='left',
            anchor='w',
            font=('Bahnschrift', 11, 'bold'),
        )
        diagnostics_status.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        diagnostics_summary = tk.Label(
            diagnostics_panel,
            text='',
            bg=self.palette['surface_alt'],
            fg=self.palette['text'],
            justify='left',
            anchor='w',
            wraplength=360,
            font=('Microsoft YaHei UI', 9),
        )
        diagnostics_summary.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        diagnostics_actions = tk.Frame(diagnostics_panel, bg=self.palette['surface_alt'])
        diagnostics_actions.grid(row=3, column=0, sticky=tk.W, pady=(12, 0))
        ttk.Button(
            diagnostics_actions,
            text='查看完整诊断',
            style='Quiet.TButton',
            command=self._show_diagnostics_dialog,
        ).pack(side=tk.LEFT)
        ttk.Button(
            diagnostics_actions,
            text='复制诊断',
            style='Quiet.TButton',
            command=self._copy_diagnostics_to_clipboard,
        ).pack(side=tk.LEFT, padx=(8, 0))

        self._register_responsive_layout(
            status_frame,
            recent_panel,
            diagnostics_panel,
            left_weight=1,
            right_weight=1,
            breakpoint=940,
        )

        self.dashboard_frames['recent_title'] = recent_title
        self.dashboard_frames['recent_detail'] = recent_detail
        self.dashboard_frames['recent_action'] = recent_action
        self.dashboard_frames['diagnostics_status'] = diagnostics_status
        self.dashboard_frames['diagnostics_summary'] = diagnostics_summary
    
    def show_settings_dialog(self):
        """显示设置对话框"""
        # 页签配置信息：(配置键, 显示名称, 描述)
        TAB_CONFIGS = [
            ('home', '工作台'),
            ('field_extractor', '字段导出'),
            ('table_range_translator', '多语言提取'),
            ('batch_modifier', '批量改表'),
            ('cross_project_translator', '跨项目翻译'),
            ('json_detector', 'JSON检测'),
            ('excel_data_processor', '数据处理'),
        ]
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("界面与模块设置")
        dialog.geometry("520x560")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        appearance_frame = ttk.LabelFrame(main_frame, text="外观与布局", padding="12")
        appearance_frame.pack(fill=tk.X, pady=(0, 14))
        appearance_frame.columnconfigure(1, weight=1)

        font_size_var = tk.StringVar(value=str(getattr(self.ui_config, 'font_size', 10)))
        sidebar_width_var = tk.StringVar(value=str(getattr(self.ui_config, 'sidebar_width', 240)))
        auto_position_var = tk.BooleanVar(value=getattr(self.ui_config, 'auto_save_position', True))

        ttk.Label(appearance_frame, text="界面字号").grid(row=0, column=0, sticky=tk.W, padx=(0, 12), pady=(0, 8))
        ttk.Combobox(
            appearance_frame,
            textvariable=font_size_var,
            values=[str(value) for value in range(9, 15)],
            state='readonly',
            width=10,
        ).grid(row=0, column=1, sticky=tk.W, pady=(0, 8))

        ttk.Label(appearance_frame, text="侧栏宽度").grid(row=1, column=0, sticky=tk.W, padx=(0, 12), pady=(0, 8))
        ttk.Combobox(
            appearance_frame,
            textvariable=sidebar_width_var,
            values=['220', '240', '260', '280', '300', '320'],
            state='readonly',
            width=10,
        ).grid(row=1, column=1, sticky=tk.W, pady=(0, 8))

        ttk.Checkbutton(
            appearance_frame,
            text="记住窗口位置",
            variable=auto_position_var,
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 0))

        ttk.Label(
            appearance_frame,
            text="侧栏宽度会立即应用；字号样式会尽量即时刷新，复杂页面建议重启后确认。",
            style='Info.TLabel',
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        title_label = ttk.Label(main_frame, text="模块显示", style='Heading.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 页签勾选区域
        tabs_frame = ttk.LabelFrame(main_frame, text="页签列表", padding="10")
        tabs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 存储变量
        tab_vars = {}
        tabs_config = config_manager.config.tabs
        
        for idx, (key, name) in enumerate(TAB_CONFIGS):
            var = tk.BooleanVar(value=getattr(tabs_config, key, True))
            tab_vars[key] = var
            
            checkbox = ttk.Checkbutton(tabs_frame, text=name, variable=var)
            checkbox.grid(row=idx, column=0, sticky=tk.W, pady=3)
        
        # 快捷按钮
        quick_frame = ttk.Frame(main_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 15))
        
        def select_all():
            for var in tab_vars.values():
                var.set(True)
        
        def deselect_all():
            for var in tab_vars.values():
                var.set(False)
        
        ttk.Button(quick_frame, text="全选", command=select_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_frame, text="全不选", command=deselect_all).pack(side=tk.LEFT)
        
        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_and_close():
            try:
                font_size = max(9, min(int(font_size_var.get()), 14))
            except (TypeError, ValueError):
                font_size = 10

            try:
                sidebar_width = max(220, min(int(sidebar_width_var.get()), 320))
            except (TypeError, ValueError):
                sidebar_width = 240

            # 保存设置
            for key, var in tab_vars.items():
                setattr(config_manager.config.tabs, key, var.get())

            previous_font_size = getattr(self.ui_config, 'font_size', 10)
            previous_sidebar_width = getattr(self.ui_config, 'sidebar_width', 240)
            self.ui_config.font_size = font_size
            self.ui_config.sidebar_width = sidebar_width
            self.ui_config.auto_save_position = auto_position_var.get()
            
            from core.config_manager import save_config
            if save_config():
                self.setup_styles()
                self._apply_sidebar_width(sidebar_width)
                self._apply_tabs_visibility_runtime()
                self._sync_header_with_current_tab()
                self._refresh_dashboard()

                change_messages = []
                if previous_sidebar_width != sidebar_width:
                    change_messages.append('侧栏宽度已立即应用')
                if previous_font_size != font_size:
                    change_messages.append('字号样式已刷新，复杂页面建议重启后再次确认')
                change_messages.append('模块页签与侧栏导航已按勾选立即更新')

                messagebox.showinfo("保存成功", "设置已保存。\n\n" + '\n'.join(change_messages), parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("保存失败", "保存设置时出错，请检查配置文件权限。", parent=dialog)
        
        ttk.Button(button_frame, text="保存", command=save_and_close, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
    
    # 结果存储辅助函数
    def append_result(self, result_type, text):
        """追加文本到结果存储（所有结果只在查看结果弹窗中显示）"""
        self.result_store.append(result_type, text)
    
    def clear_result(self, result_type):
        """清空结果存储"""
        self.result_store.clear(result_type)
    
    def get_result(self, result_type):
        """获取结果存储内容"""
        return self.result_store.get(result_type)

    def _call_on_ui_thread(self, callback, *args, **kwargs):
        """确保UI更新总是在主线程执行。"""
        self.task_runner.call_on_ui_thread(callback, *args, **kwargs)

    def _append_result_async(self, result_type, text):
        """在线程中安全地追加结果文本。"""
        self._call_on_ui_thread(self.append_result, result_type, text)

    def _append_result_batch(self, result_type, *parts):
        """一次性追加多段文本，减少零碎的结果拼接调用。"""
        self.append_result(result_type, ''.join(parts))

    def _append_result_batch_async(self, result_type, *parts):
        """在线程中安全地批量追加多段文本。"""
        self._call_on_ui_thread(self._append_result_batch, result_type, *parts)

    def _clear_result_async(self, result_type):
        """在线程中安全地清空结果文本。"""
        self._call_on_ui_thread(self.clear_result, result_type)

    def _set_status_async(self, text):
        """在线程中安全地更新状态栏。"""
        self._call_on_ui_thread(self.status_var.set, text)

    def _configure_widget_async(self, widget, **kwargs):
        """在线程中安全地更新控件属性。"""
        self._call_on_ui_thread(widget.config, **kwargs)

    def _show_message(self, kind, title, message):
        """统一封装消息框调用，便于后台任务复用和测试替身。"""
        handlers = {
            'info': messagebox.showinfo,
            'warning': messagebox.showwarning,
            'error': messagebox.showerror,
        }
        handlers[kind](title, message)

    def _show_message_async(self, kind, title, message):
        """在线程中安全地弹出消息框。"""
        self._call_on_ui_thread(self._show_message, kind, title, message)

    def _format_banner_block(self, title, width=60, char='=', leading_newline=False):
        """格式化常见的标题分隔块。"""
        prefix = '\n' if leading_newline else ''
        line = char * width
        return f"{prefix}{line}\n{title}\n{line}\n"

    def _format_key_value_lines(self, items):
        """格式化键值行列表。"""
        return ''.join(f"{label}: {value}\n" for label, value in items)

    def _format_prefixed_lines(self, items, prefix="  - "):
        """格式化带统一前缀的多行文本。"""
        return ''.join(f"{prefix}{item}\n" for item in items)

    def _start_background_task(self, target, args=(), status_message=None, widgets_to_disable=()):
        """统一启动后台线程，并在启动前冻结按钮与状态。"""
        return self.task_runner.start_background_task(
            target,
            args=args,
            status_message=status_message,
            widgets_to_disable=widgets_to_disable,
        )

    def _finish_background_task(self, widgets_to_enable=(), status_message=None,
                                dialog_kind=None, dialog_title=None, dialog_message=None):
        """统一后台任务完成时的按钮恢复、状态更新与消息提示。"""
        self.task_runner.finish_background_task(
            widgets_to_enable=widgets_to_enable,
            status_message=status_message,
            dialog_kind=dialog_kind,
            dialog_title=dialog_title,
            dialog_message=dialog_message,
        )

    def _finish_background_task_async(self, widgets_to_enable=(), status_message=None,
                                      dialog_kind=None, dialog_title=None, dialog_message=None):
        """在线程中安全地执行统一收尾。"""
        self.task_runner.finish_background_task_async(
            widgets_to_enable=widgets_to_enable,
            status_message=status_message,
            dialog_kind=dialog_kind,
            dialog_title=dialog_title,
            dialog_message=dialog_message,
        )
    
    # 统一的结果查看对话框
    def show_results_dialog(self, result_type):
        """显示结果查看对话框（二级菜单）"""
        # 获取对应的结果内容
        result_content = self.results_storage.get(result_type, '')
        
        if not result_content.strip():
            messagebox.showinfo("提示", "暂无处理结果")
            return
        
        # 创建对话框窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("查看处理结果")
        dialog.geometry("900x700")
        dialog.minsize(700, 500)
        
        # 结果标题映射
        title_map = {
            'cross_project_translator': '跨项目翻译对应结果',
            'json_detector': 'JSON错误检测结果',
            'excel_processor': 'Excel数据处理结果',
            'field_extractor': '表字段导出结果',
            'table_range_translator': '多语言翻译提取结果',
            'batch_modifier': '批量改表结果',
        }
        
        # 标题
        title_frame = ttk.Frame(dialog, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, 
                               text=title_map.get(result_type, '处理结果'),
                               style='Heading.TLabel')
        title_label.pack()

        task_key = RESULT_TASK_KEYS.get(result_type)
        task_summary = self.task_state.get(task_key, {}) if task_key else {}
        if task_summary:
            summary_frame = tk.Frame(
                dialog,
                bg=self.palette['surface_alt'],
                highlightthickness=1,
                highlightbackground=self.palette['border'],
                padx=12,
                pady=12,
            )
            summary_frame.pack(fill=tk.X, padx=10)

            headline = task_summary.get('headline') or '最近一次执行摘要'
            tk.Label(
                summary_frame,
                text=headline,
                bg=self.palette['surface_alt'],
                fg=self.palette['text'],
                font=('Bahnschrift', 11, 'bold'),
            ).pack(anchor=tk.W)

            metrics = task_summary.get('metrics', [])
            if metrics:
                metrics_text = '    '.join(f"{label}: {value}" for label, value in metrics)
                tk.Label(
                    summary_frame,
                    text=metrics_text,
                    bg=self.palette['surface_alt'],
                    fg=self.palette['info'],
                    font=('Microsoft YaHei UI', 9),
                ).pack(anchor=tk.W, pady=(6, 0))

            detail = task_summary.get('detail', '')
            if detail:
                tk.Label(
                    summary_frame,
                    text=detail,
                    bg=self.palette['surface_alt'],
                    fg=self.palette['muted_text'],
                    wraplength=840,
                    justify='left',
                    font=('Microsoft YaHei UI', 9),
                ).pack(anchor=tk.W, pady=(6, 0))
        
        # 结果显示区域
        result_frame = ttk.Frame(dialog, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        result_text = scrolledtext.ScrolledText(result_frame, 
                                               wrap=tk.WORD, 
                                               font=("Consolas", 9))
        result_text.pack(fill=tk.BOTH, expand=True)
        result_text.insert(tk.END, result_content)
        result_text.config(state='disabled')  # 只读
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        # 复制按钮
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(result_content)
            messagebox.showinfo("成功", "结果已复制到剪贴板")
        
        copy_button = ttk.Button(button_frame, text="复制到剪贴板", 
                                command=copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 保存按钮
        def save_to_file():
            file_path = filedialog.asksaveasfilename(
                title="保存结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_content)
                    messagebox.showinfo("成功", f"结果已保存到: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        save_button = ttk.Button(button_frame, text="保存到文件", 
                                command=save_to_file)
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭", 
                                 command=dialog.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # 设置对话框为模态
        dialog.transient(self.root)
        dialog.grab_set()
    
    # JSON格式检测工具相关方法
    def browse_json_folder(self):
        """浏览JSON文件夹"""
        self._get_json_detector_page().browse_folder()
    
    def start_json_detection(self):
        """开始JSON错误检测"""
        self._get_json_detector_page().start_detection()
    
    def _json_detection(self, path):
        """JSON错误检测（后台线程）"""
        self._get_json_detector_page()._run_detection(path)
    
    def _update_json_results(self, report):
        """更新JSON错误检测结果"""
        self._get_json_detector_page()._update_results(report)
    
    def _show_json_error(self, error_msg):
        """显示JSON错误检测错误"""
        self._get_json_detector_page()._show_error(error_msg)
    
    def clear_json_results(self):
        """清空JSON检测结果"""
        self._get_json_detector_page().clear_results()
    
    def save_json_report(self):
        """保存JSON检测报告"""
        self._get_json_detector_page().save_report()
    
    # Excel数据处理工具相关方法（委托给 excel_data_processor_page）
    def browse_excel_input_file(self):
        """浏览Excel输入文件"""
        self._get_excel_data_processor_page().browse_input_file()

    def browse_excel_output_folder(self):
        """浏览Excel输出文件夹"""
        self._get_excel_data_processor_page().browse_output_folder()

    def start_excel_consolidation(self):
        """开始Excel数据整合"""
        self._get_excel_data_processor_page().start_consolidation()

    def preview_excel_data(self):
        """预览Excel数据"""
        self._get_excel_data_processor_page().preview_data()

    def clear_excel_results(self):
        """清空Excel整合结果"""
        self._get_excel_data_processor_page().clear_results()


    # ==================== 跨项目翻译对应相关方法 ====================

    def browse_cpt_mapping_file(self):
        self._get_cross_project_page().browse_mapping_file()

    def browse_cpt_project_directory(self):
        self._get_cross_project_page().browse_project_directory()

    def browse_cpt_output_file(self):
        self._get_cross_project_page().browse_output_file()

    def start_cross_project_translation(self):
        self._get_cross_project_page().start_translation()

    def clear_cpt_results(self):
        self._get_cross_project_page().clear_results()

    def export_cpt_results(self):
        self._get_cross_project_page().export_results()
    
    # ==================== 表字段导出相关方法 ====================

    def browse_field_language_dir(self, lang_code):
        self._get_field_extractor_page().browse_language_dir(lang_code)

    def browse_field_scan_directory(self):
        self._get_field_extractor_page().browse_scan_directory()

    def browse_field_output_directory(self):
        self._get_field_extractor_page().browse_output_directory()

    def start_field_extraction(self):
        self._get_field_extractor_page().start_field_extraction()

    def clear_field_results(self):
        self._get_field_extractor_page().clear_field_results()

    def show_field_error_logs(self):
        self._get_field_extractor_page().show_field_error_logs()

    def copy_field_json_result(self):
        self._get_field_extractor_page().copy_field_json_result()

    def _apply_field_export_to_trt(self, merged_json_path):
        """将字段导出结果写入多语言提取页并切换页签。"""
        if 'table_range_translator' not in self.tab_lookup:
            messagebox.showwarning(
                '多语言提取未启用',
                '当前界面未启用「多语言提取」页签，请在「关于」→「界面与模块设置」中开启。',
            )
            return
        merged_json_path = str(Path(merged_json_path).resolve())
        self.trt_merged_json_var.set(merged_json_path)
        self._detect_merged_json_languages(merged_json_path)
        pairs = [
            (self.field_zh_dir_var, self.trt_zh_dir_var),
            (self.field_vn_dir_var, self.trt_vn_dir_var),
            (self.field_th_dir_var, self.trt_th_dir_var),
            (self.field_en_dir_var, self.trt_en_dir_var),
        ]
        for fv, tv in pairs:
            v = fv.get().strip()
            if v:
                tv.set(v)
        out = self.field_output_dir_var.get().strip()
        if out:
            self.trt_output_dir_var.set(out)
        self.select_tab('table_range_translator')
        try:
            self._save_ui_preferences()
        except Exception:
            logging.exception('保存衔接后的表单状态失败')

    # ==================== 多语言翻译提取相关方法 ====================

    def _detect_merged_json_languages(self, json_path):
        self._get_table_range_page().detect_merged_json_languages(json_path)

    def browse_trt_merged_json(self):
        self._get_table_range_page().browse_merged_json()

    def browse_trt_lang_json(self, lang_code):
        self._get_table_range_page().browse_lang_json(lang_code)

    def browse_trt_json_file(self):
        self._get_table_range_page().browse_json_file()

    def browse_trt_vn_directory(self):
        self._get_table_range_page().browse_vn_directory()

    def browse_trt_zh_directory(self):
        self._get_table_range_page().browse_zh_directory()

    def browse_trt_th_directory(self):
        self._get_table_range_page().browse_th_directory()

    def browse_trt_en_directory(self):
        self._get_table_range_page().browse_en_directory()

    def browse_trt_output_directory(self):
        self._get_table_range_page().browse_output_directory()

    def browse_trt_output_file(self):
        self._get_table_range_page().browse_output_file()

    def start_table_range_translation(self):
        self._get_table_range_page().start_translation()

    def clear_trt_results(self):
        self._get_table_range_page().clear_results()

    # 批量改表相关方法（委托给 batch_modifier_page）
    def browse_batch_mapping_file(self):
        """浏览批量改表映射文件。"""
        self._get_batch_modifier_page().browse_mapping_file()

    def refresh_batch_sheets(self):
        """刷新映射表的工作表列表（保留兼容性，实际调用刷新语言）。"""
        self._get_batch_modifier_page().refresh_sheets()

    def refresh_batch_languages(self):
        """刷新可用的语言列表。"""
        self._get_batch_modifier_page().refresh_languages()

    def browse_batch_json_file(self):
        """浏览批量改表 JSON 配置文件。"""
        self._get_batch_modifier_page().browse_json_file()

    def _update_batch_json_language_label(self, json_path):
        """更新批量改表 JSON 语言标记（页签未创建时为 no-op）。"""
        self._get_batch_modifier_page().update_json_language_label(json_path)

    def browse_batch_excel_directory(self):
        """浏览要修改的 Excel 文件目录。"""
        self._get_batch_modifier_page().browse_excel_directory()

    def browse_batch_report_file(self):
        """浏览修改报告保存位置。"""
        self._get_batch_modifier_page().browse_report_file()

    def preview_batch_mapping(self):
        """预览映射表内容。"""
        self._get_batch_modifier_page().preview_mapping()

    def start_batch_modification(self):
        """开始批量修改。"""
        self._get_batch_modifier_page().start_modification()

    def clear_batch_results(self):
        """清空批量改表结果。"""
        self._get_batch_modifier_page().clear_results()

    def preview_batch_json_config(self):
        """预览 JSON 配置内容。"""
        self._get_batch_modifier_page().preview_json_config()


def main():
    """主函数"""
    if sys.platform.startswith('win'):
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    root = tk.Tk()
    app = GameToolsUnified(root)
    
    # 设置窗口关闭事件
    def on_closing():
        app.shutdown()
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()