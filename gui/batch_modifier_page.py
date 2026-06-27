#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量改表页签。

承载批量改表页签的 UI、校验、预览与后台任务编排；路径型 StringVar 与主程序工作台共用。
"""

import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

import pandas as pd

from core.batch_excel_modifier import BatchExcelModifier
from core.constants import DATA_START_ROW, FIELD_NAME_ROW


class BatchModifierPage:
    """批量改表页签控制器。"""

    TAB_KEY = 'batch_modifier'

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建批量改表页签。"""
        batch_frame = self.app._register_tab(
            self.TAB_KEY,
            '批量改表',
            self._tab_descriptions[self.TAB_KEY],
        )

        left_column, right_column = self.app._build_tab_columns(batch_frame, left_weight=5, right_weight=3)

        basic_frame = ttk.LabelFrame(
            left_column,
            text="1. 基础配置（JSON / 映射路径在「工作台」选择，本页只读显示）",
            padding='12',
        )
        basic_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        basic_frame.columnconfigure(1, weight=1)

        ttk.Label(basic_frame, text='JSON 配置:').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            basic_frame,
            self.app.batch_json_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        self.app.batch_json_lang_label = ttk.Label(basic_frame, text='', style='AccentInfo.TLabel')
        self.app.batch_json_lang_label.grid(row=1, column=1, columnspan=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(basic_frame, text='映射表:').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            basic_frame,
            self.app.batch_mapping_var,
            row=2,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(basic_frame, text='目标语言:').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        language_row = ttk.Frame(basic_frame)
        language_row.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        language_row.columnconfigure(0, weight=1)

        default_languages = ['VN', 'Support-CH', 'TH', 'EN', 'Polish-CH', 'VN.1']
        self.app.batch_language_combo = ttk.Combobox(
            language_row,
            textvariable=self.app.batch_language_var,
            values=default_languages,
            state='readonly',
        )
        self.app.batch_language_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.app.batch_language_combo.bind('<<ComboboxSelected>>', self._on_language_changed)

        self.app.batch_refresh_lang_button = ttk.Button(
            language_row,
            text=self._button_labels['refresh_languages'],
            command=self.refresh_languages,
            style='Subtle.TButton',
        )
        self.app.batch_refresh_lang_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(
            basic_frame,
            text='语言列表会根据映射表自动刷新，默认优先沿用当前选择。',
            style='Info.TLabel',
        ).grid(row=4, column=1, columnspan=2, sticky=tk.W)

        target_frame = ttk.LabelFrame(left_column, text='2. 执行目标（目录与报告路径在「工作台」选择）', padding='12')
        target_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        target_frame.columnconfigure(1, weight=1)

        ttk.Label(target_frame, text='Excel 目录:').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            target_frame,
            self.app.batch_excel_dir_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(target_frame, text='报告文件:').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            target_frame,
            self.app.batch_report_var,
            row=1,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(
            target_frame,
            text='报告文件可选。若留空，批量修改仍会执行，但不会额外生成 Excel 报告。',
            style='Info.TLabel',
        ).grid(row=2, column=1, columnspan=2, sticky=tk.W)

        self.app.inline_messages[self.TAB_KEY] = self.app._create_inline_message(target_frame, row=3, columnspan=3)

        advanced_frame = ttk.LabelFrame(left_column, text='3. 高级选项', padding='12')
        advanced_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N))
        advanced_frame.columnconfigure(0, weight=1)

        advanced_header = ttk.Frame(advanced_frame)
        advanced_header.grid(row=0, column=0, sticky=(tk.W, tk.E))
        advanced_header.columnconfigure(1, weight=1)

        ttk.Button(
            advanced_header,
            textvariable=self.app.batch_advanced_toggle_var,
            style='Quiet.TButton',
            command=self.app._toggle_batch_advanced_options,
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            advanced_header,
            text='默认值适用于大多数策划表，只有遇到特殊表结构时再调整。',
            style='Info.TLabel',
        ).grid(row=0, column=1, sticky=tk.W, padx=(12, 0))

        self.app.batch_advanced_body = ttk.Frame(advanced_frame)
        self.app.batch_advanced_body.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(12, 0))
        self.app.batch_advanced_body.columnconfigure(1, weight=1)
        self.app.batch_advanced_body.columnconfigure(3, weight=1)

        self.app.batch_backup_check = ttk.Checkbutton(
            self.app.batch_advanced_body,
            text='生成 .bak 备份，便于回滚已修改文件',
            variable=self.app.batch_backup_var,
        )
        self.app.batch_backup_check.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        ttk.Label(self.app.batch_advanced_body, text='数据起始行:').grid(row=1, column=0, sticky=tk.W, padx=(0, 8))
        self.app.batch_data_start_row_entry = ttk.Entry(
            self.app.batch_advanced_body,
            textvariable=self.app.batch_data_start_row_var,
            width=6,
            font=('Microsoft YaHei', 9),
        )
        self.app.batch_data_start_row_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 12))

        ttk.Label(self.app.batch_advanced_body, text='字段行:').grid(row=1, column=2, sticky=tk.W, padx=(0, 8))
        self.app.batch_field_row_entry = ttk.Entry(
            self.app.batch_advanced_body,
            textvariable=self.app.batch_field_row_var,
            width=6,
            font=('Microsoft YaHei', 9),
        )
        self.app.batch_field_row_entry.grid(row=1, column=3, sticky=tk.W)

        ttk.Label(
            self.app.batch_advanced_body,
            text='Position 列会优先定位单元格；若没有 Position，则使用 ID 作为行号。',
            style='Info.TLabel',
        ).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        self.set_advanced_visibility(False)

        guide_frame = ttk.LabelFrame(
            right_column,
            text=self.app._format_section_title(4, '执行流程'),
            padding='12',
        )
        guide_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        ttk.Label(guide_frame, text='建议先预览，再批量写入', style='Heading.TLabel').pack(anchor=tk.W)
        for step_text in (
            '1. 在「工作台」选好 JSON、映射表、Excel 目录与报告路径；本页只读显示。',
            '2. 刷新目标语言列表，按需调整高级选项。',
            '3. 用预览核对映射内容，再执行批量修改。',
        ):
            ttk.Label(guide_frame, text=step_text, style='Info.TLabel').pack(anchor=tk.W, pady=(6, 0))

        action_panel = self.app._create_action_panel(right_column, 1)
        self.app._decorate_action_panel(
            action_panel,
            '5. 执行与结果',
            '路径在「工作台」选择。修改会直接写入原 Excel；建议先用预览确认映射与目录。',
        )

        self.app.batch_process_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_batch_modifier'],
            command=self.start_modification,
            style='Accent.TButton',
        )
        self.app.batch_process_button.pack(fill=tk.X)

        secondary_actions = ttk.Frame(action_panel)
        secondary_actions.pack(fill=tk.X, pady=(10, 0))
        secondary_actions.columnconfigure((0, 1), weight=1)

        self.app.batch_preview_button = ttk.Button(
            secondary_actions,
            text=self._button_labels['preview_mapping'],
            command=self.preview_mapping,
            style='Quiet.TButton',
        )
        self.app.batch_preview_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 6))

        self.app.batch_view_results_button = ttk.Button(
            secondary_actions,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog(self.TAB_KEY),
            style='Quiet.TButton',
        )
        self.app.batch_view_results_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(6, 0))

        self.app.batch_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_results,
            style='Danger.TButton',
        )
        self.app.batch_clear_button.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(
            action_panel,
            text='执行前会再次弹出确认信息，并显示 Position 或 ID 的定位方式。',
            style='Info.TLabel',
        ).pack(anchor=tk.W, pady=(10, 0))

        self.app._create_task_panel(action_panel, self.TAB_KEY)

    def validate_inputs(self, strict=False):
        """校验批量改表输入；返回 (ok, message, tone)。"""
        json_file = self.app.batch_json_var.get().strip()
        mapping_file = self.app.batch_mapping_var.get().strip()
        excel_dir = self.app.batch_excel_dir_var.get().strip()
        target_language = self.app.batch_language_var.get().strip()

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

        for value, label in (
            (self.app.batch_field_row_var.get().strip(), '字段行'),
            (self.app.batch_data_start_row_var.get().strip(), '数据起始行'),
        ):
            if value and not value.isdigit():
                return False, f'{label}需要是整数。', 'error' if strict else 'warning'

        report_file = self.app.batch_report_var.get().strip()
        if report_file:
            return True, f'将按 {target_language} 批量修改，并写出报告: {report_file}', 'success'
        return True, f'将按 {target_language} 批量修改，报告文件可选。', 'info'

    def refresh_validation(self):
        _, text, tone = self.validate_inputs(strict=False)
        self.app._set_inline_message(self.TAB_KEY, text, tone)

    def set_advanced_visibility(self, expanded):
        """切换高级选项区域显示。"""
        frame = getattr(self.app, 'batch_advanced_body', None)
        if frame is None:
            return

        self.app._batch_advanced_expanded = bool(expanded)
        if self.app._batch_advanced_expanded:
            frame.grid()
        else:
            frame.grid_remove()

        if hasattr(self.app, 'batch_advanced_toggle_var'):
            self.app.batch_advanced_toggle_var.set(
                '收起高级选项' if self.app._batch_advanced_expanded else '展开高级选项'
            )

        self.app.root.after_idle(lambda: self.app._update_tab_scrollregion(self.TAB_KEY))

    def toggle_advanced_options(self):
        self.set_advanced_visibility(not getattr(self.app, '_batch_advanced_expanded', False))

    def browse_mapping_file(self):
        file_path = filedialog.askopenfilename(
            title='选择映射表文件',
            filetypes=[
                ('Excel和CSV文件', '*.xlsx *.xls *.csv'),
                ('Excel文件', '*.xlsx *.xls'),
                ('CSV文件', '*.csv'),
                ('所有文件', '*.*'),
            ],
        )
        if file_path:
            self.app.batch_mapping_var.set(file_path)
            self.refresh_languages()
            if not self.app.batch_report_var.get():
                report_path = os.path.splitext(file_path)[0] + '_修改报告.xlsx'
                self.app.batch_report_var.set(report_path)

    def refresh_sheets(self):
        """保留兼容：实际刷新语言列。"""
        self.refresh_languages()

    def refresh_languages(self):
        mapping_file = self.app.batch_mapping_var.get().strip()

        if not mapping_file or not os.path.exists(mapping_file):
            messagebox.showwarning('警告', '请先选择有效的映射表文件')
            return

        try:
            file_ext = os.path.splitext(mapping_file)[1].lower()

            if file_ext == '.csv':
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
                with pd.ExcelFile(mapping_file) as xl:
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

            exclude_cols = [
                'Classification',
                'classification',
                'ID',
                'id',
                'Field',
                'field',
                '字段',
                '字段名',
                '表名',
                'Table',
                'table',
                '项目',
                '值',
                'Name',
                'name',
            ]
            lang_cols = [c for c in columns if c not in exclude_cols]

            combo = getattr(self.app, 'batch_language_combo', None)
            if lang_cols:
                if combo is not None:
                    combo['values'] = lang_cols
                current = self.app.batch_language_var.get()
                if current not in lang_cols and combo is not None:
                    combo.set(lang_cols[0])
                self._update_json_language_for_selected_lang()
            else:
                messagebox.showwarning('警告', '未找到语言列')
        except Exception as e:
            messagebox.showerror('错误', f'获取语言列表失败: {e}')

    def _update_json_language_for_selected_lang(self):
        selected_lang = self.app.batch_language_var.get().strip()
        label = getattr(self.app, 'batch_json_lang_label', None)
        if label is None:
            return
        if selected_lang:
            lang_names = {
                'VN': '越南语',
                'TH': '泰语',
                'EN': '英语',
                'ZH': '中文',
                'CN': '中文',
                'JP': '日语',
                'KR': '韩语',
                'TW': '繁体中文',
                'Support-CH': '中文(Support)',
                'Polish-CH': '中文(Polish)',
                'VN.1': '越南语(VN.1)',
            }
            lang_name = lang_names.get(selected_lang, selected_lang)
            label.config(text=f'🎯 {lang_name} ({selected_lang})')
        else:
            label.config(text='')

    def _on_language_changed(self, event=None):
        self._update_json_language_for_selected_lang()

    def browse_json_file(self):
        file_path = filedialog.askopenfilename(
            title='选择JSON配置文件',
            filetypes=[('JSON文件', '*.json'), ('所有文件', '*.*')],
        )
        if file_path:
            self.app.batch_json_var.set(file_path)
            self.update_json_language_label(file_path)

    def update_json_language_label(self, json_path):
        """根据 JSON 内容更新语言标记（页签未创建时安全跳过）。"""
        label = getattr(self.app, 'batch_json_lang_label', None)
        if label is None:
            return
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if 'language' in config and isinstance(config['language'], dict):
                lang_name = config['language'].get('name', '')
                lang_code = config['language'].get('code', '')
                label.config(text=f'📌 {lang_name} ({lang_code})')
            else:
                lang_code_keys = [
                    'ZH',
                    'VN',
                    'TH',
                    'EN',
                    'JP',
                    'KR',
                    'TW',
                    'CN',
                    'zh',
                    'vn',
                    'th',
                    'en',
                    'jp',
                    'kr',
                    'tw',
                    'cn',
                ]
                detected_lang_key = None
                for key in config.keys():
                    if key.upper() in [k.upper() for k in lang_code_keys]:
                        detected_lang_key = key
                        break

                if detected_lang_key and isinstance(config.get(detected_lang_key), dict):
                    lang_code = detected_lang_key.lower()
                    lang_names = {
                        'zh': '中文',
                        'cn': '中文',
                        'vn': '越南语',
                        'th': '泰语',
                        'en': '英语',
                        'jp': '日语',
                        'kr': '韩语',
                        'tw': '繁体中文',
                    }
                    lang_name = lang_names.get(lang_code, detected_lang_key)
                    label.config(text=f'📌 {lang_name} ({lang_code})')
                else:
                    label.config(text='⚠️ 无语言标记')
        except FileNotFoundError:
            label.config(text='⚠️ 文件不存在')
        except json.JSONDecodeError as e:
            label.config(text=f'⚠️ JSON格式错误: {str(e)[:40]}')
        except Exception as e:
            label.config(text=f'⚠️ 读取失败: {str(e)}')

    def browse_excel_directory(self):
        directory = filedialog.askdirectory(title='选择Excel文件目录')
        if directory:
            self.app.batch_excel_dir_var.set(directory)

    def browse_report_file(self):
        file_path = filedialog.asksaveasfilename(
            title='选择报告保存位置',
            defaultextension='.xlsx',
            filetypes=[('Excel文件', '*.xlsx'), ('所有文件', '*.*')],
        )
        if file_path:
            self.app.batch_report_var.set(file_path)

    def preview_mapping(self):
        mapping_file = self.app.batch_mapping_var.get().strip()
        sheet_name = self.app.batch_sheet_var.get().strip()

        if not mapping_file:
            messagebox.showerror('错误', '请先选择映射表文件')
            return

        if not os.path.exists(mapping_file):
            messagebox.showerror('错误', '映射表文件不存在')
            return

        try:
            file_ext = os.path.splitext(mapping_file)[1].lower()

            if file_ext == '.csv':
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
                df = pd.read_excel(
                    mapping_file,
                    sheet_name=sheet_name if sheet_name else 0,
                    header=0,
                    nrows=20,
                )
                sheet_display = sheet_name or '第一个'

            preview_dialog = tk.Toplevel(self.app.root)
            preview_dialog.title(f'映射表预览 - {os.path.basename(mapping_file)}')
            preview_dialog.geometry('900x500')

            info_label = ttk.Label(
                preview_dialog,
                text=f'工作表: {sheet_display} | 列数: {len(df.columns)} | 显示前20行',
            )
            info_label.pack(pady=10)

            table_frame = ttk.Frame(preview_dialog)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            text_widget = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, font=('Consolas', 9))
            text_widget.pack(fill=tk.BOTH, expand=True)

            header_line = ' | '.join([f'{col:<20}' for col in df.columns])
            text_widget.insert(tk.END, header_line + '\n')
            text_widget.insert(tk.END, '-' * len(header_line) + '\n')

            for _idx, row in df.iterrows():
                row_line = ' | '.join([f'{str(val)[:20]:<20}' for val in row])
                text_widget.insert(tk.END, row_line + '\n')

            text_widget.config(state=tk.DISABLED)

            close_button = ttk.Button(preview_dialog, text='关闭', command=preview_dialog.destroy)
            close_button.pack(pady=10)

            preview_dialog.transient(self.app.root)
            preview_dialog.grab_set()

        except Exception as e:
            messagebox.showerror('错误', f'预览失败: {e}')

    def start_modification(self):
        json_file = self.app.batch_json_var.get().strip()
        mapping_file = self.app.batch_mapping_var.get().strip()
        excel_dir = self.app.batch_excel_dir_var.get().strip()
        report_file = self.app.batch_report_var.get().strip()
        target_language = self.app.batch_language_var.get().strip()

        valid, message, tone = self.validate_inputs(strict=True)
        self.app._set_inline_message(self.TAB_KEY, message, tone)
        if not valid:
            return

        backup = self.app.batch_backup_var.get()

        try:
            field_row = int(self.app.batch_field_row_var.get().strip())
        except ValueError:
            field_row = FIELD_NAME_ROW

        try:
            data_start_row = int(self.app.batch_data_start_row_var.get().strip())
        except ValueError:
            data_start_row = DATA_START_ROW

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

        if not messagebox.askyesno('确认', confirm_msg):
            return

        self.app._begin_task_tracking(
            self.TAB_KEY,
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

        self.app._start_background_task(
            self._modification_thread,
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
            status_message='正在批量修改...',
            widgets_to_disable=(self.app.batch_process_button,),
        )

    def _modification_thread(
        self,
        mapping_file,
        excel_dir,
        report_file,
        json_file,
        target_language,
        backup,
        field_row,
        data_start_row,
    ):
        try:
            self.app._call_on_ui_thread(self.app.clear_result, self.TAB_KEY)

            modifier = self.app._replace_processor(self.TAB_KEY, BatchExcelModifier)

            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_banner_block('开始批量修改Excel文件...', width=70),
                self.app._format_key_value_lines(
                    [
                        ('JSON配置', json_file),
                        ('映射表', mapping_file),
                        ('Excel目录', excel_dir),
                        ('目标语言列', target_language),
                        ('自动识别', '工作表名=文件名, ID列=ID, 字段列=Classification'),
                        ('备份', '是' if backup else '否'),
                        ('处理引擎', 'xlwings (Excel原生引擎)'),
                    ]
                ),
                '\n',
            )

            def progress_callback(msg, percentage=None):
                self.app._append_result_async(self.TAB_KEY, msg + '\n')
                self.app._call_on_ui_thread(self.app._update_task_progress, self.TAB_KEY, msg, percentage)

            modifier.set_progress_callback(progress_callback)

            self.app._append_result_async(self.TAB_KEY, '正在加载JSON配置...\n')

            field_config = modifier.load_json_config(json_file)

            if not field_config:
                self.app._append_result_async(self.TAB_KEY, '✗ JSON配置加载失败或为空\n')
                self.app._finish_background_task_async(
                    widgets_to_enable=(self.app.batch_process_button,),
                    status_message='批量修改失败',
                    dialog_kind='error',
                    dialog_title='错误',
                    dialog_message='JSON配置加载失败',
                )
                return

            self.app._append_result_async(
                self.TAB_KEY,
                f'✓ 已加载 {len(field_config) // 2} 个表的字段配置\n\n',
            )

            self.app._append_result_async(
                self.TAB_KEY,
                f'字段行: {field_row}, 数据起始行: {data_start_row} (小于此行号的将被跳过)\n\n',
            )

            stats = modifier.process_batch_modification_by_language(
                mapping_path=mapping_file,
                excel_directory=excel_dir,
                id_col='ID',
                target_language=target_language,
                field_col=None,
                backup=backup,
                field_row=field_row,
                data_start_row=data_start_row,
            )

            summary = modifier.get_stats_summary()
            self.app._append_result_batch_async(self.TAB_KEY, '\n', summary, '\n')

            if stats.get('skipped_no_config', 0) > 0:
                self.app._append_result_async(
                    self.TAB_KEY,
                    f"\n⚠️ 跳过了 {stats['skipped_no_config']} 个工作表（表名不在JSON配置中）\n",
                )

            if stats.get('skipped_no_file', 0) > 0:
                self.app._append_result_async(
                    self.TAB_KEY,
                    f"⚠️ 跳过了 {stats['skipped_no_file']} 个工作表（对应Excel文件不存在）\n",
                )

            if stats.get('skipped_field_mismatch', 0) > 0:
                self.app._append_result_async(
                    self.TAB_KEY,
                    f"⚠️ 跳过了 {stats['skipped_field_mismatch']} 行（CSV字段名不在JSON配置中）\n",
                )

            if stats.get('skipped_same_value', 0) > 0:
                self.app._append_result_async(
                    self.TAB_KEY,
                    f"✓ 跳过了 {stats['skipped_same_value']} 处（原值与新值相同，无需修改）\n",
                )

            if report_file:
                self.app._append_result_async(self.TAB_KEY, '\n正在生成修改报告...\n')

                if modifier.generate_modification_report(report_file):
                    self.app._append_result_async(self.TAB_KEY, f'✓ 修改报告已生成: {report_file}\n')
                else:
                    self.app._append_result_async(self.TAB_KEY, '✗ 生成修改报告失败\n')

            if modifier.error_logs:
                error_lines = [f'✗ {error}' for error in modifier.error_logs[:20]]
                if len(modifier.error_logs) > 20:
                    error_lines.append(f'... 还有 {len(modifier.error_logs) - 20} 条错误')
                self.app._append_result_batch_async(
                    self.TAB_KEY,
                    '\n错误日志:\n',
                    self.app._format_prefixed_lines(error_lines),
                )

            msg = f"""批量修改完成！

修改的文件数: {stats['modified_files']}
修改的单元格数: {stats['modified_cells']}
错误数: {stats['errors']}

定位模式: {'Position直接定位' if stats.get('used_position_mode') else '行号直接定位'}
报告已保存: {report_file if report_file else '未生成'}

提示：如有错误请查看结果详情"""

            self.app._call_on_ui_thread(
                self.app._complete_task_tracking,
                self.TAB_KEY,
                'success',
                '批量改表完成',
                [
                    ('修改文件', stats['modified_files']),
                    ('改单元格', stats['modified_cells']),
                    ('错误数', stats['errors']),
                ],
                os.path.basename(report_file) if report_file else '未生成报告',
            )

            self.app._finish_background_task_async(
                widgets_to_enable=(self.app.batch_process_button,),
                status_message='批量修改完成',
                dialog_kind='info',
                dialog_title='完成',
                dialog_message=msg,
            )
            return

        except Exception as e:
            error_msg = f'处理过程中发生错误: {str(e)}'
            self.app._append_result_async(self.TAB_KEY, f'\n✗ {error_msg}\n')
            self.app._call_on_ui_thread(
                self.app._complete_task_tracking,
                self.TAB_KEY,
                'error',
                '批量改表失败',
                [('错误', 1)],
                error_msg,
            )
            self.app._finish_background_task_async(
                widgets_to_enable=(self.app.batch_process_button,),
                status_message='批量修改失败',
                dialog_kind='error',
                dialog_title='错误',
                dialog_message=error_msg,
            )

        finally:
            modifier = self.app._processors.get(self.TAB_KEY)
            if modifier is not None:
                try:
                    modifier.close()
                except Exception:
                    pass

    def clear_results(self):
        self.app.clear_result(self.TAB_KEY)
        self.app._set_task_panel_state(
            self.TAB_KEY,
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )

    def preview_json_config(self):
        json_file = self.app.batch_json_var.get().strip()

        if not json_file:
            messagebox.showwarning('提示', '请先选择JSON配置文件')
            return

        if not os.path.exists(json_file):
            messagebox.showerror('错误', f'文件不存在: {json_file}')
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            preview_lines = []
            preview_lines.append('=' * 60)
            preview_lines.append(f'JSON配置文件: {os.path.basename(json_file)}')
            preview_lines.append('=' * 60)

            text_tables = config.get('text_tables', [])
            if not text_tables:
                preview_lines.append('\n⚠️ 未找到 text_tables 配置')
            else:
                preview_lines.append(f'\n共 {len(text_tables)} 个表配置:\n')

                for i, table in enumerate(text_tables, 1):
                    table_name = table.get('table_name', '未知')
                    sheet_name = table.get('sheet_name', '')
                    fields = table.get('fields', [])
                    fields_with_examples = table.get('fields_with_examples', [])

                    preview_lines.append(f'[{i}] {table_name}')
                    if sheet_name:
                        preview_lines.append(f'    工作表: {sheet_name}')

                    all_fields = list(set(fields + fields_with_examples))
                    if all_fields:
                        preview_lines.append(f'    字段 ({len(all_fields)}): {", ".join(all_fields)}')
                    else:
                        preview_lines.append('    字段: (无)')
                    preview_lines.append('')

            preview_lines.append('-' * 60)
            preview_lines.append('注: 映射表中的列名需要与上述字段名完全匹配才会被处理')

            preview_text = '\n'.join(preview_lines)

            preview_window = tk.Toplevel(self.app.root)
            preview_window.title('JSON配置预览')
            preview_window.geometry('600x500')

            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Consolas', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            text_widget.insert(1.0, preview_text)
            text_widget.config(state='disabled')

            close_btn = ttk.Button(preview_window, text='关闭', command=preview_window.destroy)
            close_btn.pack(pady=10)

        except json.JSONDecodeError as e:
            messagebox.showerror('错误', f'JSON解析错误: {str(e)}')
        except Exception as e:
            messagebox.showerror('错误', f'读取配置失败: {str(e)}')
