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
    from gui.result_store import ResultStore
    from gui.task_runner import TaskRunner
    from gui.ui_theme import apply_ui_theme
else:
    # 开发环境使用相对导入
    from .import_helper import fix_pyinstaller_imports
    from .json_detector_page import JsonDetectorPage
    from .result_store import ResultStore
    from .task_runner import TaskRunner
    from .ui_theme import apply_ui_theme
fix_pyinstaller_imports()

# 添加模块路径（仅在非 PyInstaller 环境）
if not hasattr(sys, 'frozen'):
    sys.path.append(str(Path(__file__).parent.parent))

# 导入core模块（会自动初始化日志配置）
import core
from core.cross_project_translator import CrossProjectTranslator
from core.excel_field_extractor import ExcelFieldExtractor
from core.table_range_translator import TableRangeTranslator
from core.batch_excel_modifier import BatchExcelModifier
from core.config_manager import config_manager
from core.constants import SUPPORTED_LANGUAGES, MERGED_JSON_LANGUAGE_KEYS
from tools.json_error_detector.json_error_detector import JSONErrorDetector
from tools.excel_data_processor import ExcelDataProcessor
from version import get_version, format_version_string, get_build_date


TAB_VISUALS = {
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
    'cross_project_translator': '跨项目翻译',
    'json_detector': 'JSON检测',
    'excel_data_processor': '数据处理',
    'field_extractor': '字段导出',
    'table_range_translator': '多语言提取',
    'batch_modifier': '批量改表',
}

NAV_SECTIONS = [
    ('主要流程', ('batch_modifier', 'table_range_translator', 'field_extractor', 'cross_project_translator')),
    ('辅助工具', ('excel_data_processor', 'json_detector')),
    ('关于', ('about',)),
]

HOME_FLOW_SPECS = [
    ('batch_modifier', '批量改表', '覆盖高频改表、输出和回填，是默认主流程。'),
    ('table_range_translator', '多语言提取', '从语言目录提取可交付翻译内容。'),
    ('cross_project_translator', '跨项目翻译', '根据映射关系对齐项目间文本。'),
    ('field_extractor', '字段导出', '快速确认可本地化字段与示例文本。'),
]

HOME_SUPPORT_SPECS = [
    ('excel_data_processor', '数据处理', '拆分、转换和整理 Excel 数据。'),
    ('json_detector', 'JSON检测', '校验 JSON 结构与多语言格式。'),
]

TAB_DESCRIPTIONS = {
    'cross_project_translator': '在这里完成映射加载、项目扫描和翻译对应输出。',
    'json_detector': '在这里完成 JSON 检测、问题定位和结果整理。',
    'excel_data_processor': '在这里完成 Excel 整理、分组整合和结果输出。',
    'field_extractor': '在这里完成多语言字段扫描、筛选和导出。',
    'table_range_translator': '在这里完成配置读取、多语言提取和结果输出。',
    'batch_modifier': '在这里完成配置加载、批量改表和结果输出。',
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
        self.result_store = ResultStore(TASK_RESULT_KEYS.values())
        self.results_storage = self.result_store.storage
        self.task_runner = TaskRunner(
            self.root,
            lambda: getattr(self, 'status_var', None),
            lambda kind, title, message: self._show_message(kind, title, message),
            threading,
        )
        self.field_extraction_results = None

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
        return self._get_processor('cross_project_translator', CrossProjectTranslator)
    
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
        input_file = self.excel_input_var.get().strip()
        output_folder = self.excel_output_folder_var.get().strip()
        output_filename = self.excel_output_filename_var.get().strip()

        if not input_file:
            return False, '请选择要整合的源 Excel 文件。', 'error' if strict else 'warning'
        if not os.path.exists(input_file):
            return False, '源文件不存在，请检查路径。', 'error'
        if not output_folder:
            return False, '请选择输出目录。', 'error' if strict else 'warning'
        if not os.path.exists(output_folder):
            return False, '输出目录不存在，请重新选择。', 'error'
        if not output_filename:
            return False, '请输入输出文件名。', 'error' if strict else 'warning'
        output_file = os.path.join(output_folder, output_filename)
        return True, f'结果将输出到: {output_file}', 'success'

    def _validate_cpt_inputs(self, strict=False):
        mapping_file = self.cpt_mapping_file_var.get().strip()
        project_dir = self.cpt_project_dir_var.get().strip()
        output_file = self.cpt_output_file_var.get().strip()

        if not mapping_file:
            return False, '请选择映射文件。', 'error' if strict else 'warning'
        if not os.path.exists(mapping_file):
            return False, '映射文件不存在，请重新选择。', 'error'
        if not project_dir:
            return False, '请选择项目目录。', 'error' if strict else 'warning'
        if not os.path.exists(project_dir):
            return False, '项目目录不存在，请重新选择。', 'error'
        if not output_file:
            return False, '请填写输出文件路径。', 'error' if strict else 'warning'
        return True, f'将基于映射表输出到: {output_file}', 'success'

    def _validate_field_inputs(self, strict=False):
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        selections = [
            (lang_names['zh'], self.field_zh_check_var.get(), self.field_zh_dir_var.get().strip()),
            (lang_names['vn'], self.field_vn_check_var.get(), self.field_vn_dir_var.get().strip()),
            (lang_names['th'], self.field_th_check_var.get(), self.field_th_dir_var.get().strip()),
            (lang_names['en'], self.field_en_check_var.get(), self.field_en_dir_var.get().strip()),
        ]
        active = [(label, path) for label, enabled, path in selections if enabled]

        if not active:
            return False, '至少勾选一个语言并填写目录。', 'error' if strict else 'warning'

        for label, path in active:
            if not path:
                return False, f'{label}已勾选，但目录还未填写。', 'error' if strict else 'warning'
            if not os.path.exists(path):
                return False, f'{label}目录不存在，请重新选择。', 'error'

        output_dir = self.field_output_dir_var.get().strip()
        if output_dir and not os.path.exists(output_dir):
            return False, '输出目录不存在，请重新选择。', 'error'
        if not output_dir:
            return True, '未填写输出目录时，将自动使用首个有效语言目录。', 'info'
        return True, f'已选择 {len(active)} 个语言目录，结果输出到: {output_dir}', 'success'

    def _validate_trt_inputs(self, strict=False):
        merged_json = self.trt_merged_json_var.get().strip()
        if not merged_json:
            return False, '请选择合并 JSON 配置文件。', 'error' if strict else 'warning'
        if not os.path.exists(merged_json):
            return False, 'JSON 配置文件不存在，请重新选择。', 'error'

        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        lang_dirs = [
            (lang_names['zh'], self.trt_zh_dir_var.get().strip()),
            (lang_names['vn'], self.trt_vn_dir_var.get().strip()),
            (lang_names['th'], self.trt_th_dir_var.get().strip()),
            (lang_names['en'], self.trt_en_dir_var.get().strip()),
        ]
        valid_dirs = [(label, path) for label, path in lang_dirs if path]
        if not valid_dirs:
            return False, '请至少填写一个语言目录。', 'error' if strict else 'warning'

        for label, path in valid_dirs:
            if not os.path.exists(path):
                return False, f'{label}目录不存在，请重新选择。', 'error'

        output_dir = self.trt_output_dir_var.get().strip()
        if output_dir and not os.path.exists(output_dir):
            return False, '输出目录不存在，请重新选择。', 'error'
        if not output_dir:
            return True, '未填写输出目录时，将自动使用首个语言目录。', 'info'
        return True, f'将从 {len(valid_dirs)} 个语言目录提取并输出到: {output_dir}', 'success'

    def _validate_batch_inputs(self, strict=False):
        json_file = self.batch_json_var.get().strip()
        mapping_file = self.batch_mapping_var.get().strip()
        excel_dir = self.batch_excel_dir_var.get().strip()
        target_language = self.batch_language_var.get().strip()

        if not json_file:
            return False, '请选择 JSON 配置文件。', 'error' if strict else 'warning'
        if not os.path.exists(json_file):
            return False, 'JSON 配置文件不存在，请重新选择。', 'error'
        if not mapping_file:
            return False, '请选择映射表文件。', 'error' if strict else 'warning'
        if not os.path.exists(mapping_file):
            return False, '映射表文件不存在，请重新选择。', 'error'
        if not excel_dir:
            return False, '请选择 Excel 文件目录。', 'error' if strict else 'warning'
        if not os.path.exists(excel_dir):
            return False, 'Excel 文件目录不存在，请重新选择。', 'error'
        if not target_language:
            return False, '请选择目标语言。', 'error' if strict else 'warning'

        for value, label in ((self.batch_field_row_var.get().strip(), '字段行'), (self.batch_data_start_row_var.get().strip(), '数据起始行')):
            if value and not value.isdigit():
                return False, f'{label}需要是整数。', 'error' if strict else 'warning'

        report_file = self.batch_report_var.get().strip()
        if report_file:
            return True, f'将按 {target_language} 批量修改，并写出报告: {report_file}', 'success'
        return True, f'将按 {target_language} 批量修改，报告文件可选。', 'info'

    def _refresh_json_validation(self):
        _, text, tone = self._validate_json_inputs(strict=False)
        self._set_inline_message('json_detector', text, tone)

    def _refresh_excel_validation(self):
        _, text, tone = self._validate_excel_inputs(strict=False)
        self._set_inline_message('excel_data_processor', text, tone)

    def _refresh_cpt_validation(self):
        _, text, tone = self._validate_cpt_inputs(strict=False)
        self._set_inline_message('cross_project_translator', text, tone)

    def _refresh_field_validation(self):
        _, text, tone = self._validate_field_inputs(strict=False)
        self._set_inline_message('field_extractor', text, tone)

    def _refresh_trt_validation(self):
        _, text, tone = self._validate_trt_inputs(strict=False)
        self._set_inline_message('table_range_translator', text, tone)

    def _refresh_batch_validation(self):
        _, text, tone = self._validate_batch_inputs(strict=False)
        self._set_inline_message('batch_modifier', text, tone)

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
        frame = getattr(self, 'batch_advanced_body', None)
        if frame is None:
            return

        self._batch_advanced_expanded = bool(expanded)
        if self._batch_advanced_expanded:
            frame.grid()
        else:
            frame.grid_remove()

        if hasattr(self, 'batch_advanced_toggle_var'):
            self.batch_advanced_toggle_var.set('收起高级选项' if self._batch_advanced_expanded else '展开高级选项')

        self.root.after_idle(lambda: self._update_tab_scrollregion('batch_modifier'))

    def _toggle_batch_advanced_options(self):
        """展开或收起批量改表页的高级选项。"""
        self._set_batch_advanced_visibility(not getattr(self, '_batch_advanced_expanded', False))

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

    def _build_navigation(self):
        """构建左侧导航。"""
        self.nav_widgets = {}
        meta_by_key = {meta['key']: meta for meta in self.tab_registry}

        for section_title, section_keys in NAV_SECTIONS:
            section_items = [meta_by_key[key] for key in section_keys if key in meta_by_key]
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
        self.notebook.select(meta['frame'])
        self._sync_header_with_current_tab()

    def _get_default_tab_key(self):
        """返回启动时应选中的默认页面。"""
        for _section_title, keys in NAV_SECTIONS:
            for key in keys:
                if key != 'about' and key in self.tab_lookup:
                    return key
        if self.tab_registry:
            return self.tab_registry[0]['key']
        return 'about'

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
    
    def create_cross_project_translator_tab(self):
        """创建跨项目翻译对应页签"""
        translator_frame = self._register_tab(
            'cross_project_translator',
            '跨项目翻译',
            TAB_DESCRIPTIONS['cross_project_translator']
        )

        left_column, right_column = self._build_tab_columns(translator_frame, left_weight=5, right_weight=2)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(left_column, text=self._format_section_title(1, "输入配置"), padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # 映射文件选择
        ttk.Label(file_frame, text="映射:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_mapping_file_var = tk.StringVar()
        self.cpt_mapping_file_entry = ttk.Entry(file_frame, textvariable=self.cpt_mapping_file_var)
        self.cpt_mapping_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_mapping_browse_button = ttk.Button(file_frame, text="选择", command=self.browse_cpt_mapping_file, style='Subtle.TButton')
        self.cpt_mapping_browse_button.grid(row=0, column=2, pady=2)
        
        # 项目目录选择
        ttk.Label(file_frame, text="目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_project_dir_var = tk.StringVar()
        self.cpt_project_dir_entry = ttk.Entry(file_frame, textvariable=self.cpt_project_dir_var)
        self.cpt_project_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_project_browse_button = ttk.Button(file_frame, text="选择", command=self.browse_cpt_project_directory, style='Subtle.TButton')
        self.cpt_project_browse_button.grid(row=1, column=2, pady=2)
        
        # 输出文件选择
        ttk.Label(file_frame, text="结果:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_output_file_var = tk.StringVar()
        self.cpt_output_file_entry = ttk.Entry(file_frame, textvariable=self.cpt_output_file_var)
        self.cpt_output_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_output_browse_button = ttk.Button(file_frame, text="选择", command=self.browse_cpt_output_file, style='Subtle.TButton')
        self.cpt_output_browse_button.grid(row=2, column=2, pady=2)

        self.inline_messages['cross_project_translator'] = self._create_inline_message(file_frame, row=3)
        
        action_panel = self._create_action_panel(right_column, 0)
        self._decorate_action_panel(action_panel, '2. 执行与结果', '执行后可直接导出或查看翻译对应结果。')

        self.cpt_process_button = ttk.Button(action_panel, text=BUTTON_LABELS['start_generation'], command=self.start_cross_project_translation, style='Accent.TButton')
        self.cpt_process_button.pack(fill=tk.X)
        self.cpt_clear_button = ttk.Button(action_panel, text=BUTTON_LABELS['clear_results'], command=self.clear_cpt_results, style='Danger.TButton')
        self.cpt_clear_button.pack(fill=tk.X, pady=(8, 0))
        self.cpt_export_button = ttk.Button(action_panel, text=BUTTON_LABELS['export_results'], command=self.export_cpt_results, state="disabled", style='Quiet.TButton')
        self.cpt_export_button.pack(fill=tk.X, pady=(8, 0))
        self.cpt_view_results_button = ttk.Button(action_panel, text=BUTTON_LABELS['view_results'], command=lambda: self.show_results_dialog('cross_project_translator'), style='Quiet.TButton')
        self.cpt_view_results_button.pack(fill=tk.X, pady=(8, 0))
        self._create_task_panel(action_panel, 'cross_project_translator')
    
    
    def create_json_detector_tab(self):
        """创建JSON错误检测工具页签"""
        self._get_json_detector_page().build()
    
    def create_excel_data_processor_tab(self):
        """创建Excel数据处理工具页签"""
        # Excel数据处理工具框架
        excel_frame = self._register_tab(
            'excel_data_processor',
            '数据处理',
            TAB_DESCRIPTIONS['excel_data_processor']
        )

        left_column, right_column = self._build_tab_columns(excel_frame)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(left_column, text=self._format_section_title(1, "输入文件"), padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="源文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.excel_input_var = tk.StringVar()
        self.excel_input_entry = ttk.Entry(file_frame, textvariable=self.excel_input_var, 
                                         font=("Microsoft YaHei", 9))
        self.excel_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.excel_input_browse_button = ttk.Button(file_frame, text="选择", 
                                command=self.browse_excel_input_file, style='Subtle.TButton')
        self.excel_input_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出设置
        output_frame = ttk.LabelFrame(right_column, text=self._format_section_title(2, "输出设置"), padding="10")
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        output_frame.columnconfigure(1, weight=1)
        
        # 输出文件夹
        ttk.Label(output_frame, text="目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.excel_output_folder_var = tk.StringVar()
        self.excel_output_folder_entry = ttk.Entry(output_frame, textvariable=self.excel_output_folder_var, 
                                                 font=("Microsoft YaHei", 9))
        self.excel_output_folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.excel_output_browse_button = ttk.Button(output_frame, text="选择", 
                                 command=self.browse_excel_output_folder, style='Subtle.TButton')
        self.excel_output_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出文件名
        ttk.Label(output_frame, text="文件名:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.excel_output_filename_var = tk.StringVar(value="整合结果.xlsx")
        self.excel_output_var = tk.StringVar()
        self.excel_output_filename_entry = ttk.Entry(output_frame, textvariable=self.excel_output_filename_var, 
                                                   width=25, font=("Microsoft YaHei", 9))
        self.excel_output_filename_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(left_column, text=self._format_section_title(3, "处理选项"), padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        options_frame.columnconfigure(1, weight=1)
        
        # 分组列设置
        ttk.Label(options_frame, text="分组列:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.excel_group_column_var = tk.StringVar()
        self.excel_group_column_entry = ttk.Entry(options_frame, textvariable=self.excel_group_column_var, 
                                                width=15, font=("Microsoft YaHei", 9))
        self.excel_group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        # 工作表前缀
        ttk.Label(options_frame, text="工作表前缀:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.excel_sheet_prefix_var = tk.StringVar()
        self.excel_sheet_prefix_entry = ttk.Entry(options_frame, textvariable=self.excel_sheet_prefix_var, 
                                                width=15, font=("Microsoft YaHei", 9))
        self.excel_sheet_prefix_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # 包含汇总信息选项
        self.excel_include_summary_var = tk.BooleanVar(value=True)
        self.excel_include_summary_check = ttk.Checkbutton(options_frame, text="汇总工作表", 
                                                          variable=self.excel_include_summary_var)
        self.excel_include_summary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        self.inline_messages['excel_data_processor'] = self._create_inline_message(left_column, row=2, columnspan=1)
        
        action_panel = self._create_action_panel(right_column, 1)
        self._decorate_action_panel(action_panel, '4. 执行与结果', '整合后可预览数据或查看结果摘要。')

        self.excel_process_button = ttk.Button(action_panel, text=BUTTON_LABELS['start_consolidation'], 
                                               command=self.start_excel_consolidation, 
                                               style='Accent.TButton')
        self.excel_process_button.pack(fill=tk.X)

        self.excel_clear_button = ttk.Button(action_panel, text=BUTTON_LABELS['clear_results'], 
                     command=self.clear_excel_results, style='Danger.TButton')
        self.excel_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.excel_preview_button = ttk.Button(action_panel, text=BUTTON_LABELS['preview_data'], 
                                               command=self.preview_excel_data,
                       state="disabled", style='Quiet.TButton')
        self.excel_preview_button.pack(fill=tk.X, pady=(8, 0))

        self.excel_view_results_button = ttk.Button(action_panel, text=BUTTON_LABELS['view_results'], 
                       command=lambda: self.show_results_dialog('excel_processor'), style='Quiet.TButton')
        self.excel_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self._create_task_panel(action_panel, 'excel_data_processor')
    
    def create_field_extractor_tab(self):
        """创建表字段导出页签"""
        # 字段导出器框架
        field_frame = self._register_tab(
            'field_extractor',
            '字段导出',
            TAB_DESCRIPTIONS['field_extractor']
        )

        left_column, right_column = self._build_tab_columns(field_frame)
        
        # 目录选择区域 - 多语言分支
        dir_frame = ttk.LabelFrame(left_column, text=self._format_section_title(1, "语言目录"), padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_zh_dir_var = tk.StringVar()
        self.field_zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_zh_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_zh_browse_button = ttk.Button(dir_frame, text="选择", 
                            command=lambda: self.browse_field_language_dir('zh'), style='Subtle.TButton')
        self.field_zh_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        self.field_zh_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_zh_check_var).grid(row=0, column=3, padx=(5, 0), pady=(0, 8))
        
        # 越南语目录
        ttk.Label(dir_frame, text="越南语:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_vn_dir_var = tk.StringVar()
        self.field_vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_vn_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_vn_browse_button = ttk.Button(dir_frame, text="选择", 
                            command=lambda: self.browse_field_language_dir('vn'), style='Subtle.TButton')
        self.field_vn_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        self.field_vn_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_vn_check_var).grid(row=1, column=3, padx=(5, 0), pady=(0, 8))
        
        # 泰语目录
        ttk.Label(dir_frame, text="泰语:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_th_dir_var = tk.StringVar()
        self.field_th_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_th_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_th_browse_button = ttk.Button(dir_frame, text="选择", 
                            command=lambda: self.browse_field_language_dir('th'), style='Subtle.TButton')
        self.field_th_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        self.field_th_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_th_check_var).grid(row=2, column=3, padx=(5, 0), pady=(0, 8))
        
        # 英语目录
        ttk.Label(dir_frame, text="英语:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_en_dir_var = tk.StringVar()
        self.field_en_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_en_dir_var,
                                           font=("Microsoft YaHei", 9))
        self.field_en_dir_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_en_browse_button = ttk.Button(dir_frame, text="选择",
                            command=lambda: self.browse_field_language_dir('en'), style='Subtle.TButton')
        self.field_en_browse_button.grid(row=3, column=2, pady=(0, 8))
        
        self.field_en_check_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_en_check_var).grid(row=3, column=3, padx=(5, 0), pady=(0, 8))
        
        # 输出文件夹
        ttk.Label(dir_frame, text="输出:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.field_output_dir_var = tk.StringVar()
        self.field_output_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_output_dir_var, 
                                               font=("Microsoft YaHei", 9))
        self.field_output_dir_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.field_output_browse_button = ttk.Button(dir_frame, text="选择", 
                                command=self.browse_field_output_directory, style='Subtle.TButton')
        self.field_output_browse_button.grid(row=4, column=2)

        self.inline_messages['field_extractor'] = self._create_inline_message(dir_frame, row=5, columnspan=4)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(right_column, text=self._format_section_title(2, "导出选项"), padding="10")
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        
        # 递归扫描选项
        self.field_recursive_var = tk.BooleanVar(value=False)
        self.field_recursive_check = ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                                                    variable=self.field_recursive_var)
        self.field_recursive_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # 输出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(format_frame, text="格式:").pack(side=tk.LEFT, padx=(0, 10))
        self.field_output_format_var = tk.StringVar(value="json")
        ttk.Radiobutton(format_frame, text="JSON", 
                       variable=self.field_output_format_var, 
                       value="json").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="CSV", 
                       variable=self.field_output_format_var, 
                       value="csv").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Excel", 
                       variable=self.field_output_format_var, 
                       value="excel").pack(side=tk.LEFT)
        
        action_panel = self._create_action_panel(right_column, 1)
        self._decorate_action_panel(action_panel, '3. 执行与结果', '提取后可复制结果、查看日志或打开结果。')

        self.field_extract_button = ttk.Button(action_panel, text=BUTTON_LABELS['start_extraction'], 
                                              command=self.start_field_extraction, 
                                              style='Accent.TButton')
        self.field_extract_button.pack(fill=tk.X)
        
        self.field_copy_button = ttk.Button(action_panel, text=BUTTON_LABELS['copy_results'], 
                                    command=self.copy_field_json_result, style='Quiet.TButton')
        self.field_copy_button.pack(fill=tk.X, pady=(8, 0))
        
        self.field_error_log_button = ttk.Button(action_panel, text=BUTTON_LABELS['view_logs'], 
                                     command=self.show_field_error_logs, style='Quiet.TButton')
        self.field_error_log_button.pack(fill=tk.X, pady=(8, 0))
        
        self.field_clear_button = ttk.Button(action_panel, text=BUTTON_LABELS['clear_results'], 
                                     command=self.clear_field_results, style='Danger.TButton')
        self.field_clear_button.pack(fill=tk.X, pady=(8, 0))
        
        self.field_view_results_button = ttk.Button(action_panel, text=BUTTON_LABELS['view_results'], 
                                         command=lambda: self.show_results_dialog('field_extractor'), style='Quiet.TButton')
        self.field_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self._create_task_panel(action_panel, 'field_extractor')
    
    def create_table_range_translator_tab(self):
        """创建多语言翻译提取页签"""
        # 多语言翻译提取器框架
        trt_frame = self._register_tab(
            'table_range_translator',
            '多语言提取',
            TAB_DESCRIPTIONS['table_range_translator']
        )

        left_column, right_column = self._build_tab_columns(trt_frame)
        
        # JSON配置文件选择区域
        json_frame = ttk.LabelFrame(left_column, text=self._format_section_title(1, "提取配置"), padding="10")
        json_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        json_frame.columnconfigure(1, weight=1)
        
        # 合并JSON配置文件
        ttk.Label(json_frame, text="JSON:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_merged_json_var = tk.StringVar()
        self.trt_merged_json_entry = ttk.Entry(json_frame, textvariable=self.trt_merged_json_var, 
                                               font=("Microsoft YaHei", 9))
        self.trt_merged_json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_merged_json_browse_button = ttk.Button(json_frame, text="选择", 
                                command=self.browse_trt_merged_json, style='Subtle.TButton')
        self.trt_merged_json_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # JSON语言检测结果显示
        self.trt_json_lang_label = ttk.Label(json_frame, text="", style='AccentInfo.TLabel')
        self.trt_json_lang_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(right_column, text=self._format_section_title(2, "语言目录"), padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_zh_dir_var = tk.StringVar()
        self.trt_zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_zh_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_zh_browse_button = ttk.Button(dir_frame, text="选择", 
                              command=self.browse_trt_zh_directory, style='Subtle.TButton')
        self.trt_zh_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # 越南文目录
        ttk.Label(dir_frame, text="越南语:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_vn_dir_var = tk.StringVar()
        self.trt_vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_vn_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_vn_browse_button = ttk.Button(dir_frame, text="选择", 
                              command=self.browse_trt_vn_directory, style='Subtle.TButton')
        self.trt_vn_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        # 泰文目录
        ttk.Label(dir_frame, text="泰语:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_th_dir_var = tk.StringVar()
        self.trt_th_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_th_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_th_browse_button = ttk.Button(dir_frame, text="选择", 
                              command=self.browse_trt_th_directory, style='Subtle.TButton')
        self.trt_th_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        # 英语目录
        ttk.Label(dir_frame, text="英语:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_en_dir_var = tk.StringVar()
        self.trt_en_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_en_dir_var,
                                         font=("Microsoft YaHei", 9))
        self.trt_en_dir_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_en_browse_button = ttk.Button(dir_frame, text="选择",
                              command=self.browse_trt_en_directory, style='Subtle.TButton')
        self.trt_en_browse_button.grid(row=3, column=2, pady=(0, 8))
        
        # 输出设置
        output_frame = ttk.LabelFrame(left_column, text=self._format_section_title(3, "输出设置"), padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.trt_output_dir_var = tk.StringVar()
        self.trt_output_dir_entry = ttk.Entry(output_frame, textvariable=self.trt_output_dir_var, 
                                              font=("Microsoft YaHei", 9))
        self.trt_output_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.trt_output_dir_browse_button = ttk.Button(output_frame, text="选择", 
                                   command=self.browse_trt_output_directory, style='Subtle.TButton')
        self.trt_output_dir_browse_button.grid(row=0, column=2)

        self.inline_messages['table_range_translator'] = self._create_inline_message(output_frame, row=1)
        
        # 兼容旧变量
        self.trt_output_var = tk.StringVar()
        self.trt_zh_json_var = tk.StringVar()
        self.trt_vn_json_var = tk.StringVar()
        self.trt_th_json_var = tk.StringVar()
        self.trt_en_json_var = tk.StringVar()
        self.trt_json_var = self.trt_merged_json_var
        
        action_panel = self._create_action_panel(right_column, 1)
        self._decorate_action_panel(action_panel, '4. 执行与结果', '提取后可直接查看输出结果。')

        self.trt_process_button = ttk.Button(action_panel, text=BUTTON_LABELS['start_extraction'], 
                                            command=self.start_table_range_translation, 
                                            style='Accent.TButton')
        self.trt_process_button.pack(fill=tk.X)
        
        self.trt_clear_button = ttk.Button(action_panel, text=BUTTON_LABELS['clear_results'], 
                                  command=self.clear_trt_results, style='Danger.TButton')
        self.trt_clear_button.pack(fill=tk.X, pady=(8, 0))
        
        self.trt_view_results_button = ttk.Button(action_panel, text=BUTTON_LABELS['view_results'], 
                                      command=lambda: self.show_results_dialog('table_range_translator'), style='Quiet.TButton')
        self.trt_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self._create_task_panel(action_panel, 'table_range_translator')
    
    def create_batch_modifier_tab(self):
        """创建批量改表页签"""
        batch_frame = self._register_tab(
            'batch_modifier',
            '批量改表',
            TAB_DESCRIPTIONS['batch_modifier']
        )

        left_column, right_column = self._build_tab_columns(batch_frame, left_weight=5, right_weight=3)

        basic_frame = ttk.LabelFrame(left_column, text="1. 基础配置", padding="12")
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        basic_frame.columnconfigure(1, weight=1)

        ttk.Label(basic_frame, text="JSON 配置:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_json_var = tk.StringVar()
        self.batch_json_entry = ttk.Entry(basic_frame, textvariable=self.batch_json_var, font=("Microsoft YaHei", 9))
        self.batch_json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        self.batch_json_browse_button = ttk.Button(
            basic_frame,
            text="选择",
            command=self.browse_batch_json_file,
            style='Subtle.TButton',
        )
        self.batch_json_browse_button.grid(row=0, column=2, pady=(0, 8))

        self.batch_json_lang_label = ttk.Label(basic_frame, text="", style='AccentInfo.TLabel')
        self.batch_json_lang_label.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(basic_frame, text="映射表:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_mapping_var = tk.StringVar()
        self.batch_mapping_entry = ttk.Entry(basic_frame, textvariable=self.batch_mapping_var, font=("Microsoft YaHei", 9))
        self.batch_mapping_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        self.batch_mapping_browse_button = ttk.Button(
            basic_frame,
            text="选择",
            command=self.browse_batch_mapping_file,
            style='Subtle.TButton',
        )
        self.batch_mapping_browse_button.grid(row=2, column=2, pady=(0, 8))

        ttk.Label(basic_frame, text="目标语言:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        language_row = ttk.Frame(basic_frame)
        language_row.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        language_row.columnconfigure(0, weight=1)

        self.batch_language_var = tk.StringVar(value="VN")
        default_languages = ['VN', 'Support-CH', 'TH', 'EN', 'Polish-CH', 'VN.1']
        self.batch_language_combo = ttk.Combobox(
            language_row,
            textvariable=self.batch_language_var,
            values=default_languages,
            state='readonly',
        )
        self.batch_language_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.batch_language_combo.bind('<<ComboboxSelected>>', self._on_batch_language_changed)

        self.batch_refresh_lang_button = ttk.Button(
            language_row,
            text=BUTTON_LABELS['refresh_languages'],
            command=self.refresh_batch_languages,
            style='Subtle.TButton',
        )
        self.batch_refresh_lang_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(
            basic_frame,
            text="语言列表会根据映射表自动刷新，默认优先沿用当前选择。",
            style='Info.TLabel',
        ).grid(row=4, column=1, columnspan=2, sticky=tk.W)

        self.batch_sheet_var = tk.StringVar()

        target_frame = ttk.LabelFrame(left_column, text="2. 执行目标", padding="12")
        target_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        target_frame.columnconfigure(1, weight=1)

        ttk.Label(target_frame, text="Excel 目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_excel_dir_var = tk.StringVar()
        self.batch_excel_dir_entry = ttk.Entry(target_frame, textvariable=self.batch_excel_dir_var, font=("Microsoft YaHei", 9))
        self.batch_excel_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        self.batch_excel_dir_browse_button = ttk.Button(
            target_frame,
            text="选择",
            command=self.browse_batch_excel_directory,
            style='Subtle.TButton',
        )
        self.batch_excel_dir_browse_button.grid(row=0, column=2, pady=(0, 8))

        ttk.Label(target_frame, text="报告文件:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_report_var = tk.StringVar()
        self.batch_report_entry = ttk.Entry(target_frame, textvariable=self.batch_report_var, font=("Microsoft YaHei", 9))
        self.batch_report_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        self.batch_report_browse_button = ttk.Button(
            target_frame,
            text="选择",
            command=self.browse_batch_report_file,
            style='Subtle.TButton',
        )
        self.batch_report_browse_button.grid(row=1, column=2, pady=(0, 8))

        ttk.Label(
            target_frame,
            text="报告文件可选。若留空，批量修改仍会执行，但不会额外生成 Excel 报告。",
            style='Info.TLabel',
        ).grid(row=2, column=1, columnspan=2, sticky=tk.W)

        self.inline_messages['batch_modifier'] = self._create_inline_message(target_frame, row=3, columnspan=3)

        self.batch_auto_match_var = tk.BooleanVar(value=False)
        self.batch_table_col_var = tk.StringVar(value="")
        self.batch_id_col_var = tk.StringVar(value="ID")
        self.batch_field_col_var = tk.StringVar(value="Classification")

        advanced_frame = ttk.LabelFrame(left_column, text="3. 高级选项", padding="12")
        advanced_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N))
        advanced_frame.columnconfigure(0, weight=1)

        advanced_header = ttk.Frame(advanced_frame)
        advanced_header.grid(row=0, column=0, sticky=(tk.W, tk.E))
        advanced_header.columnconfigure(1, weight=1)

        self.batch_advanced_toggle_var = tk.StringVar(value='展开高级选项')
        ttk.Button(
            advanced_header,
            textvariable=self.batch_advanced_toggle_var,
            style='Quiet.TButton',
            command=self._toggle_batch_advanced_options,
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            advanced_header,
            text="默认值适用于大多数策划表，只有遇到特殊表结构时再调整。",
            style='Info.TLabel',
        ).grid(row=0, column=1, sticky=tk.W, padx=(12, 0))

        self.batch_backup_var = tk.BooleanVar(value=True)
        self.batch_data_start_row_var = tk.StringVar(value="7")
        self.batch_field_row_var = tk.StringVar(value="5")

        self.batch_advanced_body = ttk.Frame(advanced_frame)
        self.batch_advanced_body.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(12, 0))
        self.batch_advanced_body.columnconfigure(1, weight=1)
        self.batch_advanced_body.columnconfigure(3, weight=1)

        self.batch_backup_check = ttk.Checkbutton(
            self.batch_advanced_body,
            text="生成 .bak 备份，便于回滚已修改文件",
            variable=self.batch_backup_var,
        )
        self.batch_backup_check.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        ttk.Label(self.batch_advanced_body, text="数据起始行:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8))
        self.batch_data_start_row_entry = ttk.Entry(
            self.batch_advanced_body,
            textvariable=self.batch_data_start_row_var,
            width=6,
            font=("Microsoft YaHei", 9),
        )
        self.batch_data_start_row_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 12))

        ttk.Label(self.batch_advanced_body, text="字段行:").grid(row=1, column=2, sticky=tk.W, padx=(0, 8))
        self.batch_field_row_entry = ttk.Entry(
            self.batch_advanced_body,
            textvariable=self.batch_field_row_var,
            width=6,
            font=("Microsoft YaHei", 9),
        )
        self.batch_field_row_entry.grid(row=1, column=3, sticky=tk.W)

        ttk.Label(
            self.batch_advanced_body,
            text="Position 列会优先定位单元格；若没有 Position，则使用 ID 作为行号。",
            style='Info.TLabel',
        ).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        self._set_batch_advanced_visibility(False)

        guide_frame = ttk.LabelFrame(right_column, text=self._format_section_title(4, "执行流程"), padding="12")
        guide_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        ttk.Label(
            guide_frame,
            text="建议先预览，再批量写入",
            style='Heading.TLabel',
        ).pack(anchor=tk.W)
        for step_text in (
            '1. 先选择 JSON 配置和映射表，并刷新目标语言列表。',
            '2. 确认待修改 Excel 目录，报告文件按需填写。',
            '3. 用预览核对映射内容，再执行批量修改。',
        ):
            ttk.Label(guide_frame, text=step_text, style='Info.TLabel').pack(anchor=tk.W, pady=(6, 0))

        action_panel = self._create_action_panel(right_column, 1)
        self._decorate_action_panel(action_panel, '5. 执行与结果', '修改会直接写入原 Excel。建议先用预览确认当前映射列、语言和目录。')

        self.batch_process_button = ttk.Button(
            action_panel,
            text=BUTTON_LABELS['start_batch_modifier'],
            command=self.start_batch_modification,
            style='Accent.TButton',
        )
        self.batch_process_button.pack(fill=tk.X)

        secondary_actions = ttk.Frame(action_panel)
        secondary_actions.pack(fill=tk.X, pady=(10, 0))
        secondary_actions.columnconfigure((0, 1), weight=1)

        self.batch_preview_button = ttk.Button(
            secondary_actions,
            text=BUTTON_LABELS['preview_mapping'],
            command=self.preview_batch_mapping,
            style='Quiet.TButton',
        )
        self.batch_preview_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 6))

        self.batch_view_results_button = ttk.Button(
            secondary_actions,
            text=BUTTON_LABELS['view_results'],
            command=lambda: self.show_results_dialog('batch_modifier'),
            style='Quiet.TButton',
        )
        self.batch_view_results_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(6, 0))

        self.batch_clear_button = ttk.Button(
            action_panel,
            text=BUTTON_LABELS['clear_results'],
            command=self.clear_batch_results,
            style='Danger.TButton',
        )
        self.batch_clear_button.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(
            action_panel,
            text='执行前会再次弹出确认信息，并显示 Position 或 ID 的定位方式。',
            style='Info.TLabel',
        ).pack(anchor=tk.W, pady=(10, 0))

        self._create_task_panel(action_panel, 'batch_modifier')
    
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
            ('cross_project_translator', '跨项目翻译'),
            ('json_detector', 'JSON检测'),
            ('excel_data_processor', '数据处理'),
            ('field_extractor', '字段导出'),
            ('table_range_translator', '多语言提取'),
            ('batch_modifier', '批量改表'),
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
                self._sync_header_with_current_tab()
                self._refresh_dashboard()

                change_messages = []
                if previous_sidebar_width != sidebar_width:
                    change_messages.append('侧栏宽度已立即应用')
                if previous_font_size != font_size:
                    change_messages.append('字号样式已刷新，复杂页面建议重启后再次确认')
                change_messages.append('模块显隐在下次启动时完全生效')

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
            'config_sync': 'Excel配置同步结果'
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
    
    # Excel数据处理工具相关方法
    def browse_excel_input_file(self):
        """浏览Excel输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.excel_input_var.set(file_path)
            if not self.excel_output_folder_var.get():
                self.excel_output_folder_var.set(str(Path(file_path).parent))
            if not self.excel_output_filename_var.get() or self.excel_output_filename_var.get() == "整合结果.xlsx":
                input_path = Path(file_path)
                self.excel_output_filename_var.set(f"{input_path.stem}_整合{input_path.suffix}")
    
    def browse_excel_output_folder(self):
        """浏览Excel输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.excel_output_folder_var.set(folder_path)
            # 自动设置输出文件名
            if not self.excel_output_filename_var.get():
                self.excel_output_filename_var.set("整合结果.xlsx")
    
    def start_excel_consolidation(self):
        """开始Excel数据整合"""
        input_file = self.excel_input_var.get().strip()
        output_folder = self.excel_output_folder_var.get().strip()
        output_filename = self.excel_output_filename_var.get().strip()

        valid, message, tone = self._validate_excel_inputs(strict=True)
        self._set_inline_message('excel_data_processor', message, tone)
        if not valid:
            return
        
        # 构建完整的输出文件路径
        output_file = os.path.join(output_folder, output_filename)

        self._begin_task_tracking(
            'excel_data_processor',
            '正在整合 Excel 数据...',
            {
                'excel.input': input_file,
                'excel.output_folder': output_folder,
                'excel.output_filename': output_filename,
                'excel.output_file': output_file,
            },
        )
        
        group_column = self.excel_group_column_var.get().strip() or None
        include_summary = self.excel_include_summary_var.get()
        sheet_prefix = self.excel_sheet_prefix_var.get().strip()

        # 在新线程中执行整合
        self._start_background_task(
            self._excel_consolidation_process,
            args=(input_file, output_file, group_column, include_summary, sheet_prefix),
            status_message="正在处理Excel数据...",
            widgets_to_disable=(self.excel_process_button, self.excel_preview_button),
        )
    
    def _excel_consolidation_process(self, input_file, output_file, group_column,
                                     include_summary, sheet_prefix):
        """Excel数据整合处理（后台线程）"""
        try:
            self._call_on_ui_thread(
                self._update_task_progress,
                'excel_data_processor',
                f"正在处理: {os.path.basename(input_file)}",
                35,
            )
            # 清空结果
            self._call_on_ui_thread(self.clear_result, 'excel_processor')
            
            # 显示开始信息
            self._append_result_batch_async(
                'excel_processor',
                self._format_key_value_lines([
                    ("开始处理文件", input_file),
                    ("输出文件", output_file),
                ]),
                "-" * 50 + "\n",
            )
            
            # 执行处理
            success = self.excel_processor.process_file(
                input_path=input_file,
                output_folder=os.path.dirname(output_file),
                output_filename=os.path.basename(output_file),
                group_column=group_column,
                include_summary=include_summary,
                sheet_prefix=sheet_prefix
            )
            
            # 显示结果
            if success:
                self._call_on_ui_thread(self._show_excel_success_result)
            else:
                self._call_on_ui_thread(self._show_excel_error_result, "处理失败")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self._call_on_ui_thread(self._show_excel_error_result, error_msg)
    
    def _show_excel_success_result(self):
        """显示Excel整合成功结果"""
        report = self.excel_processor.get_process_report()
        self.append_result('excel_processor', report)
        self.append_result('excel_processor', "\n\n✅ Excel数据处理完成！")

        output_file = self.task_state.get('excel_data_processor', {}).get('inputs', {}).get('excel.output_file', '')
        self._complete_task_tracking(
            'excel_data_processor',
            'success',
            'Excel 数据整合完成',
            metrics=[('输出文件', os.path.basename(output_file) if output_file else '已生成')],
            detail='预览和详细报告已可查看。',
        )
        self._finish_background_task(
            widgets_to_enable=(self.excel_process_button, self.excel_preview_button),
            status_message="Excel处理完成",
            dialog_kind='info',
            dialog_title="成功",
            dialog_message="Excel数据处理完成！请点击查看结果按钮查看详细报告",
        )
    
    def _show_excel_error_result(self, error_msg):
        """显示Excel处理错误结果"""
        self.append_result('excel_processor', f"❌ {error_msg}\n")
        self._complete_task_tracking(
            'excel_data_processor',
            'error',
            'Excel 数据整合失败',
            metrics=[('错误', 1)],
            detail=error_msg,
        )
        self._finish_background_task(
            widgets_to_enable=(self.excel_process_button, self.excel_preview_button),
            status_message="Excel处理失败",
            dialog_kind='error',
            dialog_title="错误",
            dialog_message=error_msg,
        )
    
    def preview_excel_data(self):
        """预览Excel数据"""
        input_file = self.excel_input_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请先选择输入文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        try:
            # 读取文件
            df = self.excel_processor.read_excel_file(input_file)
            
            # 显示预览信息
            preview_text = f"文件预览: {os.path.basename(input_file)}\n"
            preview_text += f"总行数: {len(df)}\n"
            preview_text += f"总列数: {len(df.columns)}\n"
            preview_text += f"列名: {list(df.columns)}\n\n"
            
            # 显示前几行数据
            preview_text += "前5行数据:\n"
            preview_text += df.head().to_string()
            
            # 显示A列的唯一值
            if len(df) > 0:
                first_col = df.columns[0]
                unique_values = df[first_col].unique()
                preview_text += f"\n\n第一列 '{first_col}' 的唯一值:\n"
                for i, value in enumerate(unique_values[:10]):  # 只显示前10个
                    preview_text += f"{i+1}. {value}\n"
                if len(unique_values) > 10:
                    preview_text += f"... 还有 {len(unique_values) - 10} 个值\n"
            
            # 清空并显示预览
            self.clear_result('excel_processor')
            self.append_result('excel_processor', preview_text)
            messagebox.showinfo("预览", "预览数据加载完成！请点击查看结果按钮查看")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览数据失败: {str(e)}")
    
    def clear_excel_results(self):
        """清空Excel整合结果"""
        self.clear_result('excel_processor')
        self._set_task_panel_state(
            'excel_data_processor',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
    
    # ==================== 跨项目翻译对应相关方法 ====================
    
    def browse_cpt_mapping_file(self):
        """浏览映射文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.cpt_mapping_file_var.set(file_path)
            # 自动设置输出文件名
            if not self.cpt_output_file_var.get():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(os.path.dirname(file_path), f"{base_name}_翻译对应结果.xlsx")
                self.cpt_output_file_var.set(output_path)
    
    def browse_cpt_project_directory(self):
        """浏览项目目录"""
        dir_path = filedialog.askdirectory(title="选择项目目录")
        if dir_path:
            self.cpt_project_dir_var.set(dir_path)
    
    def browse_cpt_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.cpt_output_file_var.set(file_path)
    
    def start_cross_project_translation(self):
        """开始跨项目翻译对应"""
        mapping_file = self.cpt_mapping_file_var.get().strip()
        project_dir = self.cpt_project_dir_var.get().strip()
        output_file = self.cpt_output_file_var.get().strip()

        valid, message, tone = self._validate_cpt_inputs(strict=True)
        self._set_inline_message('cross_project_translator', message, tone)
        if not valid:
            return

        self._begin_task_tracking(
            'cross_project_translator',
            '正在建立跨项目翻译对应...',
            {
                'cross.mapping': mapping_file,
                'cross.project_dir': project_dir,
                'cross.output_file': output_file,
            },
        )
        
        # 在新线程中执行翻译对应
        self._start_background_task(
            self._cross_project_translation,
            args=(mapping_file, project_dir, output_file),
            status_message="正在处理翻译对应...",
            widgets_to_disable=(self.cpt_process_button,),
        )
    
    def _cross_project_translation(self, mapping_file, project_dir, output_file):
        """跨项目翻译对应（后台线程）"""
        succeeded = False
        completion_message = "翻译对应处理失败，请查看结果详情"
        metrics = []

        try:
            # 清空结果
            self._call_on_ui_thread(self.clear_result, 'cross_project_translator')
            self._configure_widget_async(self.cpt_export_button, state="disabled")
            self._call_on_ui_thread(
                self._update_task_progress,
                'cross_project_translator',
                f"正在分析映射表: {os.path.basename(mapping_file)}",
                24,
            )
            
            # 开始处理
            self._append_result_batch_async(
                'cross_project_translator',
                "开始处理翻译对应...\n",
                self._format_key_value_lines([
                    ("映射文件", mapping_file),
                    ("项目目录", project_dir),
                    ("输出文件", output_file),
                ]),
                '=' * 60 + '\n',
            )
            
            # 处理翻译映射
            results = self.cross_project_translator.process_translation_mapping(
                mapping_file, project_dir)
            self._call_on_ui_thread(
                self._update_task_progress,
                'cross_project_translator',
                '正在生成结果与导出文件...',
                72,
            )
            
            if results:
                # 显示处理报告
                report = self.cross_project_translator.get_processing_report()
                self._append_result_async('cross_project_translator', f"{report}\n")
                
                # 导出结果
                if self.cross_project_translator.export_results(output_file):
                    self._append_result_async('cross_project_translator', f"结果已导出到: {output_file}\n")
                    # 启用导出按钮
                    self._configure_widget_async(self.cpt_export_button, state="normal")
                    succeeded = True
                    completion_message = "翻译对应完成！请点击查看结果按钮查看详细报告"
                    failed_count = len([item for item in results if item.get('status') != 'success'])
                    metrics = [
                        ('结果数', len(results)),
                        ('失败项', failed_count),
                        ('导出文件', os.path.basename(output_file)),
                    ]
                else:
                    self._append_result_async('cross_project_translator', "导出失败！\n")
                    completion_message = "翻译对应结果导出失败，请查看结果详情"
                    metrics = [('结果数', len(results)), ('导出', '失败')]
                
                # 显示详细结果（前20条）
                self._append_result_batch_async(
                    'cross_project_translator',
                    "\n详细结果（前20条）:\n",
                    '=' * 60 + '\n',
                )
                
                for i, result in enumerate(results[:20]):
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    self._append_result_async(
                        'cross_project_translator',
                        f"{status_icon} 第{result['index']}行: {result['file_name']} -> {result['content'][:50]}...\n"
                    )
                
                if len(results) > 20:
                    self._append_result_async('cross_project_translator', f"... 还有 {len(results) - 20} 条结果，请查看导出的Excel文件\n")
                
            else:
                self._append_result_async('cross_project_translator', "处理失败，没有生成结果\n")
                completion_message = "处理失败，没有生成结果"
            
            self._append_result_async('cross_project_translator', "\n处理完成！\n")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self._append_result_async('cross_project_translator', f"❌ {error_msg}\n")
            completion_message = error_msg
        finally:
            self._call_on_ui_thread(self._finish_cross_project_translation, succeeded, completion_message, metrics)

    def _finish_cross_project_translation(self, succeeded, completion_message, metrics=None):
        """统一收敛跨项目翻译对应任务的完成态，避免失败时误报成功。"""
        self._complete_task_tracking(
            'cross_project_translator',
            'success' if succeeded else 'error',
            '跨项目翻译完成' if succeeded else '跨项目翻译失败',
            metrics=metrics or [],
            detail=completion_message,
        )
        self._finish_background_task(
            widgets_to_enable=(self.cpt_process_button,),
            status_message="翻译对应完成" if succeeded else "翻译对应失败",
            dialog_kind='info' if succeeded else 'error',
            dialog_title="完成" if succeeded else "错误",
            dialog_message=completion_message,
        )
    
    def clear_cpt_results(self):
        """清空跨项目翻译对应结果"""
        self.clear_result('cross_project_translator')
        self.cpt_export_button.config(state="disabled")
        self._set_task_panel_state(
            'cross_project_translator',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
    
    def export_cpt_results(self):
        """导出跨项目翻译对应结果"""
        if not self.cross_project_translator.translation_results:
            messagebox.showwarning("警告", "没有结果可导出")
            return
        
        # 选择导出文件
        file_path = filedialog.asksaveasfilename(
            title="导出翻译对应结果",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.cross_project_translator.export_results(file_path):
                messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
    
    # ==================== 表字段导出相关方法 ====================
    
    def browse_field_language_dir(self, lang_code):
        """浏览特定语言的目录"""
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        dir_path = filedialog.askdirectory(title=f"选择{lang_names.get(lang_code, '')}目录")
        if dir_path:
            if lang_code == 'zh':
                self.field_zh_dir_var.set(dir_path)
            elif lang_code == 'vn':
                self.field_vn_dir_var.set(dir_path)
            elif lang_code == 'th':
                self.field_th_dir_var.set(dir_path)
            elif lang_code == 'en':
                self.field_en_dir_var.set(dir_path)
            # 如果输出目录为空，自动设置为该目录的父目录
            if not self.field_output_dir_var.get():
                self.field_output_dir_var.set(dir_path)
    
    def browse_field_scan_directory(self):
        """浏览字段提取扫描目录（兼容旧方法）"""
        dir_path = filedialog.askdirectory(title="选择扫描目录")
        if dir_path:
            # 默认设置为中文目录
            self.field_zh_dir_var.set(dir_path)
            if not self.field_output_dir_var.get():
                self.field_output_dir_var.set(dir_path)
    
    def browse_field_output_directory(self):
        """浏览字段提取输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.field_output_dir_var.set(dir_path)
    
    def start_field_extraction(self):
        """开始字段提取"""
        # 收集选中的语言目录
        directories = {}
        if self.field_zh_check_var.get() and self.field_zh_dir_var.get().strip():
            directories['zh'] = self.field_zh_dir_var.get().strip()
        if self.field_vn_check_var.get() and self.field_vn_dir_var.get().strip():
            directories['vn'] = self.field_vn_dir_var.get().strip()
        if self.field_th_check_var.get() and self.field_th_dir_var.get().strip():
            directories['th'] = self.field_th_dir_var.get().strip()
        if self.field_en_check_var.get() and self.field_en_dir_var.get().strip():
            directories['en'] = self.field_en_dir_var.get().strip()
        
        output_dir = self.field_output_dir_var.get().strip()

        valid, message, tone = self._validate_field_inputs(strict=True)
        self._set_inline_message('field_extractor', message, tone)
        if not valid:
            return
        
        if not output_dir:
            # 使用第一个有效目录作为输出目录
            output_dir = list(directories.values())[0]
            self.field_output_dir_var.set(output_dir)

        output_format = self.field_output_format_var.get()
        recursive = self.field_recursive_var.get()

        self._begin_task_tracking(
            'field_extractor',
            '正在提取多语言字段...',
            {
                'field.zh_dir': self.field_zh_dir_var.get().strip(),
                'field.vn_dir': self.field_vn_dir_var.get().strip(),
                'field.th_dir': self.field_th_dir_var.get().strip(),
                'field.en_dir': self.field_en_dir_var.get().strip(),
                'field.output_dir': output_dir,
                'field.output_format': output_format,
                'field.recursive': recursive,
                'field.zh_enabled': self.field_zh_check_var.get(),
                'field.vn_enabled': self.field_vn_check_var.get(),
                'field.th_enabled': self.field_th_check_var.get(),
                'field.en_enabled': self.field_en_check_var.get(),
            },
        )
        
        # 在新线程中执行提取
        self._start_background_task(
            self._field_extraction_thread,
            args=(directories, output_dir, output_format, recursive),
            status_message="正在提取表字段...",
            widgets_to_disable=(self.field_extract_button,),
        )
    
    def _field_extraction_thread(self, directories, output_dir, output_format, recursive):
        """字段提取线程 - 支持多语言"""
        try:
            # 清空结果存储
            self._clear_result_async('field_extractor')
            self.field_extractor.set_progress_callback(
                lambda msg, percentage=None: (
                    self._append_result_async('field_extractor', msg + "\n"),
                    self._call_on_ui_thread(self._update_task_progress, 'field_extractor', msg, percentage),
                )
            )
            self._append_result_batch_async(
                'field_extractor',
                self._format_banner_block("开始提取多语言表字段信息...", width=60),
            )
            
            lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
            for lang, dir_path in directories.items():
                self._append_result_async('field_extractor', f"{lang_names.get(lang, lang)}目录: {dir_path}\n")
            
            self._append_result_batch_async(
                'field_extractor',
                self._format_key_value_lines([
                    ("输出目录", output_dir),
                    ("输出格式", output_format.upper()),
                    ("递归扫描", '是' if recursive else '否'),
                ]),
                "\n",
            )
            
            # 执行多语言提取
            all_stats = self.field_extractor.process_multi_language_directories(
                directories=directories,
                output_folder=output_dir,
                output_format=output_format,
                recursive=recursive
            )
            
            # 收集所有结果
            all_results = []
            for lang_code, lang_data in all_stats['languages'].items():
                if 'stats' in lang_data and 'results' in lang_data['stats']:
                    all_results.extend(lang_data['stats']['results'])
            self.field_extraction_results = all_results
            
            # 显示统计信息
            self._append_result_batch_async(
                'field_extractor',
                self._format_banner_block("多语言提取完成!", width=60, leading_newline=True),
            )
            
            # 分语言显示统计
            for lang_code, lang_data in all_stats['languages'].items():
                stats = lang_data.get('stats', {})
                self._append_result_async(
                    'field_extractor',
                    f"\n【{lang_data['name']}】文件数: {stats.get('total_files', 0)}, 工作表: {stats.get('total_sheets', 0)}, 字段数: {stats.get('total_fields', 0)}\n"
                )
            
            self._append_result_batch_async(
                'field_extractor',
                '\n',
                self._format_key_value_lines([
                    ("总文件数", all_stats['total_files']),
                    ("总工作表数", all_stats['total_sheets']),
                    ("总字段数", all_stats['total_fields']),
                ]),
                "\n输出文件:\n",
                self._format_prefixed_lines(all_stats.get('output_files', [])),
            )

            self._call_on_ui_thread(
                self._complete_task_tracking,
                'field_extractor',
                'success',
                '字段导出完成',
                [
                    ('语言数', len(all_stats['languages'])),
                    ('字段数', all_stats['total_fields']),
                    ('输出文件', len(all_stats.get('output_files', []))),
                ],
                '输出文件和详细统计已生成。',
            )
            
            output_files_str = '\n'.join(all_stats.get('output_files', []))
            self._finish_background_task_async(
                widgets_to_enable=(self.field_extract_button,),
                status_message="字段提取完成",
                dialog_kind='info',
                dialog_title="完成",
                dialog_message=(
                    f"多语言字段提取完成!\n\n"
                    f"处理语言数: {len(all_stats['languages'])}\n"
                    f"总文件数: {all_stats['total_files']}\n"
                    f"总工作表数: {all_stats['total_sheets']}\n"
                    f"总字段数: {all_stats['total_fields']}\n\n"
                    f"输出文件:\n{output_files_str}"
                ),
            )
            return
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            self._append_result_async('field_extractor', f"\n错误: {str(e)}\n")
            self._append_result_async('field_extractor', error_msg + "\n")
            self._call_on_ui_thread(
                self._complete_task_tracking,
                'field_extractor',
                'error',
                '字段导出失败',
                [('错误', 1)],
                str(e),
            )
            self._finish_background_task_async(
                widgets_to_enable=(self.field_extract_button,),
                status_message="字段提取失败",
                dialog_kind='error',
                dialog_title="错误",
                dialog_message=f"处理失败:\n{str(e)}",
            )
    
    def _log_field_result(self, message):
        """记录字段提取结果"""
        self.append_result('field_extractor', message + "\n")
    
    def clear_field_results(self):
        """清空字段提取结果"""
        self.clear_result('field_extractor')
        self.field_extraction_results = None
        # 清除提取器的日志
        self.field_extractor.clear_logs()
        self._set_task_panel_state(
            'field_extractor',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
    
    def show_field_error_logs(self):
        """显示字段提取的错误和警告日志"""
        logs = self.field_extractor.get_all_logs()
        errors = logs['errors']
        warnings = logs['warnings']
        
        if not errors and not warnings:
            messagebox.showinfo("日志信息", "没有错误或警告日志")
            return
        
        # 创建新窗口显示日志
        log_window = tk.Toplevel(self.root)
        log_window.title("字段提取 - 错误与警告日志")
        log_window.geometry("900x600")
        
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(log_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 错误日志标签页
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text=f"错误日志 ({len(errors)})")
        
        error_text = scrolledtext.ScrolledText(error_frame, 
                                               wrap=tk.WORD,
                                               font=('Consolas', 9))
        error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if errors:
            for i, error in enumerate(errors, 1):
                error_text.insert(tk.END, f"{i}. {error}\n\n")
        else:
            error_text.insert(tk.END, "无错误日志")
        
        error_text.config(state='disabled')
        
        # 警告日志标签页
        warning_frame = ttk.Frame(notebook)
        notebook.add(warning_frame, text=f"警告日志 ({len(warnings)})")
        
        warning_text = scrolledtext.ScrolledText(warning_frame,
                                                 wrap=tk.WORD,
                                                 font=('Consolas', 9))
        warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if warnings:
            for i, warning in enumerate(warnings, 1):
                warning_text.insert(tk.END, f"{i}. {warning}\n\n")
        else:
            warning_text.insert(tk.END, "无警告日志")
        
        warning_text.config(state='disabled')
        
        # 底部按钮
        button_frame = ttk.Frame(log_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 保存日志按钮
        def save_logs():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="保存日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                if self.field_extractor.save_logs_to_file(Path(file_path)):
                    messagebox.showinfo("成功", f"日志已保存到:\n{file_path}")
        
        ttk.Button(button_frame, text="保存日志", command=save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=log_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 统计信息
        stats_label = ttk.Label(
            button_frame,
            text=f"总计: {len(errors)} 个错误, {len(warnings)} 个警告",
            style='Info.TLabel',
        )
        stats_label.pack(side=tk.LEFT, padx=20)
    
    def copy_field_json_result(self):
        """复制字段提取的JSON结果到剪贴板"""
        if not self.field_extraction_results:
            messagebox.showwarning("警告", "没有可复制的结果，请先执行字段提取")
            return
        
        try:
            import json
            # 构建JSON数据
            json_data = [{
                "table_name": r['excel_file'],
                "sheet_name": r['sheet_name'],
                "fields_with_examples": r.get('fields_with_examples', []),
                "field_count": r['field_count']
            } for r in self.field_extraction_results]
            
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(json_str)
            self.root.update()
            
            messagebox.showinfo("成功", f"JSON结果已复制到剪贴板\n共 {len(json_data)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败:\n{str(e)}")
    
    # ==================== 多语言翻译提取相关方法 ====================
    
    def browse_trt_merged_json(self):
        """浏览合并的JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择合并的JSON配置文件（可含 ZH/VN/TH/EN 等）",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_merged_json_var.set(file_path)
            # 检测JSON中的语言配置
            self._detect_merged_json_languages(file_path)
    
    def _detect_merged_json_languages(self, json_path):
        """检测合并JSON中包含的语言配置"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            detected_langs = []
            for lang_key in MERGED_JSON_LANGUAGE_KEYS:
                if lang_key in config:
                    text_count = len(config[lang_key].get('text_tables', []))
                    name = SUPPORTED_LANGUAGES.get(lang_key.lower(), {}).get('name', lang_key)
                    detected_langs.append(f"{name}({text_count}表)")
            
            if detected_langs:
                self.trt_json_lang_label.config(text=f"✓ 检测到: {', '.join(detected_langs)}")
            else:
                keys_hint = '/'.join(MERGED_JSON_LANGUAGE_KEYS)
                self.trt_json_lang_label.config(text=f"⚠️ 未检测到有效语言配置（期望顶层键之一: {keys_hint}）")
        except Exception as e:
            self.trt_json_lang_label.config(text=f"⚠️ 读取失败: {str(e)[:50]}")
    
    def browse_trt_lang_json(self, lang_code):
        """浏览特定语言的JSON配置文件（兼容旧方法）"""
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        file_path = filedialog.askopenfilename(
            title=f"选择{lang_names.get(lang_code, '')}JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            if lang_code == 'zh':
                self.trt_zh_json_var.set(file_path)
            elif lang_code == 'vn':
                self.trt_vn_json_var.set(file_path)
            elif lang_code == 'th':
                self.trt_th_json_var.set(file_path)
            elif lang_code == 'en':
                self.trt_en_json_var.set(file_path)
    
    def browse_trt_json_file(self):
        """浏览JSON配置文件（兼容旧方法）"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_json_var.set(file_path)
    
    def browse_trt_vn_directory(self):
        """浏览越南文文件目录"""
        dir_path = filedialog.askdirectory(title="选择越南文Excel文件目录")
        if dir_path:
            self.trt_vn_dir_var.set(dir_path)
    
    def browse_trt_zh_directory(self):
        """浏览中文文件目录"""
        dir_path = filedialog.askdirectory(title="选择中文Excel文件目录（_zh后缀）")
        if dir_path:
            self.trt_zh_dir_var.set(dir_path)
    
    def browse_trt_th_directory(self):
        """浏览泰文文件目录"""
        dir_path = filedialog.askdirectory(title="选择泰文Excel文件目录（_th后缀）")
        if dir_path:
            self.trt_th_dir_var.set(dir_path)
    
    def browse_trt_en_directory(self):
        """浏览英语文件目录"""
        dir_path = filedialog.askdirectory(title="选择英语Excel文件目录（_en后缀）")
        if dir_path:
            self.trt_en_dir_var.set(dir_path)
    
    def browse_trt_output_directory(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择CSV输出目录")
        if dir_path:
            self.trt_output_dir_var.set(dir_path)
    
    def browse_trt_output_file(self):
        """浏览输出文件位置（兼容旧方法）"""
        file_path = filedialog.asksaveasfilename(
            title="保存翻译总表",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_output_var.set(file_path)
    
    def start_table_range_translation(self):
        """开始多语言翻译提取"""
        # 获取合并的JSON配置文件
        merged_json = self.trt_merged_json_var.get().strip()
        
        # 收集语言目录
        zh_dir = self.trt_zh_dir_var.get().strip()
        vn_dir = self.trt_vn_dir_var.get().strip()
        th_dir = self.trt_th_dir_var.get().strip()
        en_dir = self.trt_en_dir_var.get().strip()
        output_dir = self.trt_output_dir_var.get().strip()

        valid, message, tone = self._validate_trt_inputs(strict=True)
        self._set_inline_message('table_range_translator', message, tone)
        if not valid:
            return
        
        # 构建语言目录字典
        lang_dirs = {}
        if zh_dir:
            lang_dirs['zh'] = zh_dir
        if vn_dir:
            lang_dirs['vn'] = vn_dir
        if th_dir:
            lang_dirs['th'] = th_dir
        if en_dir:
            lang_dirs['en'] = en_dir
        
        # 如果未指定输出目录，使用第一个语言目录
        if not output_dir:
            output_dir = list(lang_dirs.values())[0]
            self.trt_output_dir_var.set(output_dir)
        
        # 自动生成输出文件名
        output_file = self.table_range_translator.generate_output_filename(output_dir)

        self._begin_task_tracking(
            'table_range_translator',
            '正在提取多语言翻译...',
            {
                'trt.merged_json': merged_json,
                'trt.zh_dir': zh_dir,
                'trt.vn_dir': vn_dir,
                'trt.th_dir': th_dir,
                'trt.en_dir': en_dir,
                'trt.output_dir': output_dir,
                'trt.output_file': output_file,
            },
        )
        
        # 在新线程中执行提取
        self._start_background_task(
            self._table_range_translation_thread,
            args=(merged_json, lang_dirs, output_file),
            status_message="正在提取翻译内容...",
            widgets_to_disable=(self.trt_process_button,),
        )
    
    def _table_range_translation_thread(self, merged_json, lang_dirs, output_file):
        """多语言翻译提取线程 - 使用合并的JSON配置"""
        try:
            # 清空结果
            self._call_on_ui_thread(self.clear_result, 'table_range_translator')
            
            # 开始处理
            self._append_result_batch_async(
                'table_range_translator',
                self._format_banner_block("开始多语言翻译提取（合并JSON配置）...", width=70),
            )
            
            lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
            
            # 显示JSON配置
            self._append_result_async('table_range_translator', f"合并JSON: {merged_json}\n")
            
            # 显示各语言目录
            for lang, dir_path in lang_dirs.items():
                self._append_result_async('table_range_translator', f"{lang_names.get(lang, lang)}目录: {dir_path}\n")
            
            self._append_result_batch_async(
                'table_range_translator',
                self._format_key_value_lines([
                    ("输出文件", output_file),
                ]),
                "\n",
            )
            
            # 定义进度回调函数
            def progress_callback(msg):
                """进度回调，将消息显示到界面"""
                self._append_result_async('table_range_translator', msg + "\n")
                self._call_on_ui_thread(self._update_task_progress, 'table_range_translator', msg)
            
            # 使用新的合并JSON处理方法
            results = self.table_range_translator.process_with_merged_json(
                merged_json, lang_dirs, progress_callback=progress_callback)
            
            if results:
                self._append_result_async('table_range_translator', f"✓ 成功提取 {len(results)} 条数据\n\n")
                
                # 生成翻译CSV
                self._append_result_async('table_range_translator', "正在生成翻译CSV...\n")
                
                success = self.table_range_translator.generate_translation_csv(output_file)
                
                if success:
                    self._append_result_async('table_range_translator', f"✓ 翻译CSV已生成: {output_file}\n\n")
                    
                    # 显示处理报告
                    report = self.table_range_translator.get_processing_report()
                    self._append_result_async('table_range_translator', report + "\n")
                    
                    # 显示成功消息
                    stats = self.table_range_translator.processing_stats
                    self._call_on_ui_thread(
                        self._complete_task_tracking,
                        'table_range_translator',
                        'success',
                        '多语言翻译提取完成',
                        [
                            ('处理表', f"{stats['processed_tables']}/{stats['total_tables']}"),
                            ('导出字段', stats['exported_fields']),
                            ('提取行数', stats['total_rows']),
                        ],
                        os.path.basename(output_file),
                    )
                    msg = (f"多语言翻译提取完成！\n\n"
                          f"处理表格: {stats['processed_tables']}/{stats['total_tables']}\n"
                          f"导出字段: {stats['exported_fields']} 个\n"
                          f"提取数据: {stats['total_rows']} 行\n\n"
                          f"翻译CSV已生成:\n{output_file}")
                    self._finish_background_task_async(
                        widgets_to_enable=(self.trt_process_button,),
                        status_message="翻译提取完成",
                        dialog_kind='info',
                        dialog_title="完成",
                        dialog_message=msg,
                    )
                    return
                else:
                    self._append_result_async('table_range_translator', "✗ 生成翻译CSV失败\n")
                    self._call_on_ui_thread(
                        self._complete_task_tracking,
                        'table_range_translator',
                        'error',
                        '翻译 CSV 生成失败',
                        [('错误', 1)],
                        '请检查输出目录与处理日志。',
                    )
                    self._finish_background_task_async(
                        widgets_to_enable=(self.trt_process_button,),
                        status_message="翻译提取失败",
                        dialog_kind='error',
                        dialog_title="错误",
                        dialog_message="生成翻译CSV失败",
                    )
                    return
            else:
                self._append_result_async('table_range_translator', "✗ 没有提取到数据\n")
                self._call_on_ui_thread(
                    self._complete_task_tracking,
                    'table_range_translator',
                    'warning',
                    '没有提取到可导出数据',
                    [('提取结果', 0)],
                    '请检查 JSON 配置和源目录。',
                )
                self._finish_background_task_async(
                    widgets_to_enable=(self.trt_process_button,),
                    status_message="未提取到数据",
                    dialog_kind='warning',
                    dialog_title="警告",
                    dialog_message="没有提取到数据，请检查JSON配置和Excel文件",
                )
                return
        
        except Exception as e:
            details = str(e) or e.__class__.__name__
            error_msg = f"处理过程中发生错误: {details}"
            self._append_result_async('table_range_translator', f"\n✗ {error_msg}\n")
            self._call_on_ui_thread(
                self._complete_task_tracking,
                'table_range_translator',
                'error',
                '多语言翻译提取失败',
                [('错误', 1)],
                error_msg,
            )
            self._finish_background_task_async(
                widgets_to_enable=(self.trt_process_button,),
                status_message="翻译提取失败",
                dialog_kind='error',
                dialog_title="错误",
                dialog_message=error_msg,
            )
    
    def clear_trt_results(self):
        """清空多语言翻译提取结果"""
        self.clear_result('table_range_translator')
        self._set_task_panel_state(
            'table_range_translator',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
    
    # 批量改表相关方法
    def browse_batch_mapping_file(self):
        """浏览批量改表映射文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射表文件",
            filetypes=[("Excel和CSV文件", "*.xlsx *.xls *.csv"), ("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_mapping_var.set(file_path)
            # 自动刷新语言列表
            self.refresh_batch_languages()
            # 自动设置输出报告路径
            if not self.batch_report_var.get():
                report_path = os.path.splitext(file_path)[0] + "_修改报告.xlsx"
                self.batch_report_var.set(report_path)
    
    def refresh_batch_sheets(self):
        """刷新映射表的工作表列表（保留兼容性，实际调用刷新语言）"""
        self.refresh_batch_languages()

    def refresh_batch_languages(self):
        """刷新可用的语言列表"""
        mapping_file = self.batch_mapping_var.get().strip()
        
        if not mapping_file or not os.path.exists(mapping_file):
            messagebox.showwarning("警告", "请先选择有效的映射表文件")
            return
        
        try:
            import pandas as pd
            
            # 检查文件扩展名
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            if file_ext == '.csv':
                # CSV文件，直接读取列名
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, nrows=0, encoding=encoding)
                        columns = df.columns.tolist()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, nrows=0, encoding='utf-8', errors='ignore')
                    columns = df.columns.tolist()
            else:
                # Excel文件
                with pd.ExcelFile(mapping_file) as xl:
                    # 跳过汇总信息等非数据工作表，找到第一个数据工作表
                    skip_sheets = ['汇总信息', '汇总', 'Summary', 'summary', '说明', 'Info']
                    data_sheet = None
                    for sheet in xl.sheet_names:
                        if sheet not in skip_sheets:
                            data_sheet = sheet
                            break

                    if not data_sheet:
                        data_sheet = xl.sheet_names[0] if xl.sheet_names else None

                    if data_sheet:
                        df = pd.read_excel(xl, sheet_name=data_sheet, nrows=0)
                        columns = df.columns.tolist()
                    else:
                        columns = []
            
            # 排除一些常见的非语言列
            exclude_cols = ['Classification', 'classification', 'ID', 'id', 'Field', 'field', 
                           '字段', '字段名', '表名', 'Table', 'table', '项目', '值', 'Name', 'name']
            lang_cols = [c for c in columns if c not in exclude_cols]
            
            if lang_cols:
                self.batch_language_combo['values'] = lang_cols
                # 保持当前选择，如果当前值有效的话
                current = self.batch_language_var.get()
                if current not in lang_cols:
                    self.batch_language_combo.set(lang_cols[0])
                # 更新JSON语言标签以反映当前选择的语言
                self._update_batch_json_language_for_selected_lang()
            else:
                messagebox.showwarning("警告", f"未找到语言列")
        except Exception as e:
            messagebox.showerror("错误", f"获取语言列表失败: {e}")
    
    def _update_batch_json_language_for_selected_lang(self):
        """根据选择的语言更新JSON语言标签"""
        selected_lang = self.batch_language_var.get().strip()
        if selected_lang:
            # 语言名称映射
            lang_names = {
                'VN': '越南语', 'TH': '泰语', 'EN': '英语', 'ZH': '中文', 'CN': '中文',
                'JP': '日语', 'KR': '韩语', 'TW': '繁体中文', 'Support-CH': '中文(Support)',
                'Polish-CH': '中文(Polish)', 'VN.1': '越南语(VN.1)'
            }
            lang_name = lang_names.get(selected_lang, selected_lang)
            self.batch_json_lang_label.config(text=f"🎯 {lang_name} ({selected_lang})")
        else:
            self.batch_json_lang_label.config(text="")
    
    def _on_batch_language_changed(self, event=None):
        """当语言选择变化时更新JSON语言标签"""
        self._update_batch_json_language_for_selected_lang()
    
    def browse_batch_json_file(self):
        """浏览批量改表JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_json_var.set(file_path)
            # 读取JSON并显示语言标记
            self._update_batch_json_language_label(file_path)
    
    def _update_batch_json_language_label(self, json_path):
        """更新批量改表JSON语言标记显示"""
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 格式1和2：检查language字段
            if 'language' in config and isinstance(config['language'], dict):
                lang_name = config['language'].get('name', '')
                lang_code = config['language'].get('code', '')
                self.batch_json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
            else:
                # 格式3：检测语言代码作为顶层key
                lang_code_keys = ['ZH', 'VN', 'TH', 'EN', 'JP', 'KR', 'TW', 'CN',
                                 'zh', 'vn', 'th', 'en', 'jp', 'kr', 'tw', 'cn']
                detected_lang_key = None
                for key in config.keys():
                    if key.upper() in [k.upper() for k in lang_code_keys]:
                        detected_lang_key = key
                        break
                
                if detected_lang_key and isinstance(config.get(detected_lang_key), dict):
                    lang_code = detected_lang_key.lower()
                    lang_names = {
                        'zh': '中文', 'cn': '中文', 'vn': '越南语', 'th': '泰语',
                        'en': '英语', 'jp': '日语', 'kr': '韩语', 'tw': '繁体中文'
                    }
                    lang_name = lang_names.get(lang_code, detected_lang_key)
                    self.batch_json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
                else:
                    self.batch_json_lang_label.config(text="⚠️ 无语言标记")
        except Exception as e:
            self.batch_json_lang_label.config(text=f"⚠️ 读取失败: {str(e)}")
    
    def browse_batch_excel_directory(self):
        """浏览要修改的Excel文件目录"""
        directory = filedialog.askdirectory(title="选择Excel文件目录")
        if directory:
            self.batch_excel_dir_var.set(directory)
    
    def browse_batch_report_file(self):
        """浏览修改报告保存位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_report_var.set(file_path)
    
    def preview_batch_mapping(self):
        """预览映射表内容"""
        mapping_file = self.batch_mapping_var.get().strip()
        sheet_name = self.batch_sheet_var.get().strip()
        
        if not mapping_file:
            messagebox.showerror("错误", "请先选择映射表文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射表文件不存在")
            return
        
        try:
            import pandas as pd
            
            # 检查文件扩展名
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            # 读取前20行数据预览
            if file_ext == '.csv':
                # 尝试多种编码读取CSV
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, header=0, nrows=20, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, header=0, nrows=20, encoding='utf-8', errors='ignore')
                sheet_display = 'CSV文件'
            else:
                # Excel文件
                df = pd.read_excel(mapping_file, sheet_name=sheet_name if sheet_name else 0, 
                                  header=0, nrows=20)
                sheet_display = sheet_name or '第一个'
            
            # 创建预览对话框
            preview_dialog = tk.Toplevel(self.root)
            preview_dialog.title(f"映射表预览 - {os.path.basename(mapping_file)}")
            preview_dialog.geometry("900x500")
            
            # 信息标签
            info_label = ttk.Label(preview_dialog, 
                                  text=f"工作表: {sheet_display} | 列数: {len(df.columns)} | 显示前20行")
            info_label.pack(pady=10)
            
            # 创建表格框架
            table_frame = ttk.Frame(preview_dialog)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 创建文本框显示数据
            text_widget = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, 
                                                   font=("Consolas", 9))
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # 格式化显示数据
            header_line = " | ".join([f"{col:<20}" for col in df.columns])
            text_widget.insert(tk.END, header_line + "\n")
            text_widget.insert(tk.END, "-" * len(header_line) + "\n")
            
            for idx, row in df.iterrows():
                row_line = " | ".join([f"{str(val)[:20]:<20}" for val in row])
                text_widget.insert(tk.END, row_line + "\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # 关闭按钮
            close_button = ttk.Button(preview_dialog, text="关闭", 
                                     command=preview_dialog.destroy)
            close_button.pack(pady=10)
            
            preview_dialog.transient(self.root)
            preview_dialog.grab_set()
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {e}")
    
    def start_batch_modification(self):
        """开始批量修改"""
        json_file = self.batch_json_var.get().strip()
        mapping_file = self.batch_mapping_var.get().strip()
        excel_dir = self.batch_excel_dir_var.get().strip()
        report_file = self.batch_report_var.get().strip()
        target_language = self.batch_language_var.get().strip()

        valid, message, tone = self._validate_batch_inputs(strict=True)
        self._set_inline_message('batch_modifier', message, tone)
        if not valid:
            return
        
        backup = self.batch_backup_var.get()

        try:
            field_row = int(self.batch_field_row_var.get().strip())
        except ValueError:
            field_row = 5

        try:
            data_start_row = int(self.batch_data_start_row_var.get().strip())
        except ValueError:
            data_start_row = 7

        # 确认操作
        confirm_msg = f"""确认开始批量修改？

JSON配置: {os.path.basename(json_file)}
映射表: {os.path.basename(mapping_file)}
Excel目录: {excel_dir}
目标语言: {target_language}

定位模式（自动识别）:
• 有Position列 → Position直接定位（如B7、E24）
• 无Position列 → ID值作为行号（如ID=7→第7行）

备份: {'是' if backup else '否'}

提示：建议先用少量数据测试"""
        
        if not messagebox.askyesno("确认", confirm_msg):
            return

        self._begin_task_tracking(
            'batch_modifier',
            '正在批量修改 Excel 文件...',
            {
                'batch.json': json_file,
                'batch.mapping': mapping_file,
                'batch.excel_dir': excel_dir,
                'batch.report': report_file,
                'batch.language': target_language,
                'batch.backup': backup,
                'batch.field_row': field_row,
                'batch.data_start_row': data_start_row,
            },
        )

        # 开始处理
        self._start_background_task(
            self._batch_modification_thread,
            args=(
                mapping_file,
                excel_dir,
                report_file,
                json_file,
                target_language,
                backup,
                field_row,
                data_start_row,
            ),
            status_message="正在批量修改...",
            widgets_to_disable=(self.batch_process_button,),
        )
    
    def _batch_modification_thread(self, mapping_file, excel_dir, report_file, 
                                   json_file, target_language, backup,
                                   field_row, data_start_row):
        """批量修改处理线程"""
        try:
            # 清空结果
            self._call_on_ui_thread(self.clear_result, 'batch_modifier')
            
            # 初始化 batch_modifier（使用 xlwings 引擎）
            modifier = self._replace_processor('batch_modifier', BatchExcelModifier)
            
            # 显示开始信息
            self._append_result_batch_async(
                'batch_modifier',
                self._format_banner_block("开始批量修改Excel文件...", width=70),
                self._format_key_value_lines([
                    ("JSON配置", json_file),
                    ("映射表", mapping_file),
                    ("Excel目录", excel_dir),
                    ("目标语言列", target_language),
                    ("自动识别", "工作表名=文件名, ID列=ID, 字段列=Classification"),
                    ("备份", '是' if backup else '否'),
                    ("处理引擎", "xlwings (Excel原生引擎)"),
                ]),
                "\n",
            )
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self._append_result_async('batch_modifier', msg + "\n")
                self._call_on_ui_thread(self._update_task_progress, 'batch_modifier', msg, percentage)
            
            modifier.set_progress_callback(progress_callback)
            
            # 加载JSON配置
            self._append_result_async('batch_modifier', "正在加载JSON配置...\n")
            
            field_config = modifier.load_json_config(json_file)
            
            if not field_config:
                self._append_result_async('batch_modifier', "✗ JSON配置加载失败或为空\n")
                self._finish_background_task_async(
                    widgets_to_enable=(self.batch_process_button,),
                    status_message="批量修改失败",
                    dialog_kind='error',
                    dialog_title="错误",
                    dialog_message="JSON配置加载失败",
                )
                return
            
            self._append_result_async('batch_modifier', f"✓ 已加载 {len(field_config)//2} 个表的字段配置\n\n")
            
            self._append_result_async('batch_modifier', f"字段行: {field_row}, 数据起始行: {data_start_row} (小于此行号的将被跳过)\n\n")
            
            # 使用手动指定语言列方式
            stats = modifier.process_batch_modification_by_language(
                mapping_path=mapping_file,
                excel_directory=excel_dir,
                id_col="ID",
                target_language=target_language,
                field_col=None,  # 自动检测
                backup=backup,
                field_row=field_row,
                data_start_row=data_start_row
            )
            
            # 显示统计信息
            summary = modifier.get_stats_summary()
            self._append_result_batch_async('batch_modifier', "\n", summary, "\n")
            
            # 显示跳过的表（不在JSON配置中）
            if stats.get('skipped_no_config', 0) > 0:
                self._append_result_async('batch_modifier', f"\n⚠️ 跳过了 {stats['skipped_no_config']} 个工作表（表名不在JSON配置中）\n")
            
            # 显示跳过的文件（文件不存在）
            if stats.get('skipped_no_file', 0) > 0:
                self._append_result_async('batch_modifier', f"⚠️ 跳过了 {stats['skipped_no_file']} 个工作表（对应Excel文件不存在）\n")
            
            # 显示字段不匹配的跳过数（CSV字段不在JSON配置中）
            if stats.get('skipped_field_mismatch', 0) > 0:
                self._append_result_async('batch_modifier', f"⚠️ 跳过了 {stats['skipped_field_mismatch']} 行（CSV字段名不在JSON配置中）\n")
            
            # 显示值相同跳过的数量
            if stats.get('skipped_same_value', 0) > 0:
                self._append_result_async('batch_modifier', f"✓ 跳过了 {stats['skipped_same_value']} 处（原值与新值相同，无需修改）\n")
            
            # 生成报告
            if report_file:
                self._append_result_async('batch_modifier', "\n正在生成修改报告...\n")
                
                if modifier.generate_modification_report(report_file):
                    self._append_result_async('batch_modifier', f"✓ 修改报告已生成: {report_file}\n")
                else:
                    self._append_result_async('batch_modifier', "✗ 生成修改报告失败\n")
            
            # 显示错误日志
            if modifier.error_logs:
                error_lines = [f"✗ {error}" for error in modifier.error_logs[:20]]
                if len(modifier.error_logs) > 20:
                    error_lines.append(f"... 还有 {len(modifier.error_logs) - 20} 条错误")
                self._append_result_batch_async(
                    'batch_modifier',
                    "\n错误日志:\n",
                    self._format_prefixed_lines(error_lines),
                )
            
            # 显示成功消息
            msg = f"""批量修改完成！

修改的文件数: {stats['modified_files']}
修改的单元格数: {stats['modified_cells']}
错误数: {stats['errors']}

定位模式: {'Position直接定位' if stats.get('used_position_mode') else '行号直接定位'}
报告已保存: {report_file if report_file else '未生成'}

提示：如有错误请查看结果详情"""

            self._call_on_ui_thread(
                self._complete_task_tracking,
                'batch_modifier',
                'success',
                '批量改表完成',
                [
                    ('修改文件', stats['modified_files']),
                    ('改单元格', stats['modified_cells']),
                    ('错误数', stats['errors']),
                ],
                os.path.basename(report_file) if report_file else '未生成报告',
            )
            
            self._finish_background_task_async(
                widgets_to_enable=(self.batch_process_button,),
                status_message="批量修改完成",
                dialog_kind='info',
                dialog_title="完成",
                dialog_message=msg,
            )
            return
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self._append_result_async('batch_modifier', f"\n✗ {error_msg}\n")
            self._call_on_ui_thread(
                self._complete_task_tracking,
                'batch_modifier',
                'error',
                '批量改表失败',
                [('错误', 1)],
                error_msg,
            )
            self._finish_background_task_async(
                widgets_to_enable=(self.batch_process_button,),
                status_message="批量修改失败",
                dialog_kind='error',
                dialog_title="错误",
                dialog_message=error_msg,
            )
        
        finally:
            modifier = self._processors.get('batch_modifier')
            if modifier is not None:
                try:
                    modifier.close()
                except Exception:
                    pass
    
    def clear_batch_results(self):
        """清空批量改表结果"""
        self.clear_result('batch_modifier')
        self._set_task_panel_state(
            'batch_modifier',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
    
    def preview_batch_json_config(self):
        """预览JSON配置内容"""
        json_file = self.batch_json_var.get().strip()
        
        if not json_file:
            messagebox.showwarning("提示", "请先选择JSON配置文件")
            return
        
        if not os.path.exists(json_file):
            messagebox.showerror("错误", f"文件不存在: {json_file}")
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 构建预览内容
            preview_lines = []
            preview_lines.append("=" * 60)
            preview_lines.append(f"JSON配置文件: {os.path.basename(json_file)}")
            preview_lines.append("=" * 60)
            
            text_tables = config.get('text_tables', [])
            if not text_tables:
                preview_lines.append("\n⚠️ 未找到 text_tables 配置")
            else:
                preview_lines.append(f"\n共 {len(text_tables)} 个表配置:\n")
                
                for i, table in enumerate(text_tables, 1):
                    table_name = table.get('table_name', '未知')
                    sheet_name = table.get('sheet_name', '')
                    fields = table.get('fields', [])
                    fields_with_examples = table.get('fields_with_examples', [])
                    
                    preview_lines.append(f"[{i}] {table_name}")
                    if sheet_name:
                        preview_lines.append(f"    工作表: {sheet_name}")
                    
                    # 显示字段
                    all_fields = list(set(fields + fields_with_examples))
                    if all_fields:
                        preview_lines.append(f"    字段 ({len(all_fields)}): {', '.join(all_fields)}")
                    else:
                        preview_lines.append("    字段: (无)")
                    preview_lines.append("")
            
            preview_lines.append("-" * 60)
            preview_lines.append("注: 映射表中的列名需要与上述字段名完全匹配才会被处理")
            
            # 显示预览
            preview_text = "\n".join(preview_lines)
            
            # 创建预览窗口
            preview_window = tk.Toplevel(self.root)
            preview_window.title("JSON配置预览")
            preview_window.geometry("600x500")
            
            # 文本框
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_widget.insert(1.0, preview_text)
            text_widget.config(state='disabled')
            
            # 关闭按钮
            close_btn = ttk.Button(preview_window, text="关闭", 
                                  command=preview_window.destroy)
            close_btn.pack(pady=10)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败: {str(e)}")


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