#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表字段导出页签。

该模块承载字段导出页签的 UI、校验与后台任务编排，主界面只负责装配与共享变量。
"""

import json
import logging
import os
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, scrolledtext

from core.constants import FIELD_EXTRACTION_MERGED_JSON_NAME, SUPPORTED_LANGUAGES


class FieldExtractorPage:
    """表字段导出页签控制器。"""

    TAB_KEY = 'field_extractor'

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建表字段导出页签。"""
        field_frame = self.app._register_tab(
            self.TAB_KEY,
            '字段导出',
            self._tab_descriptions[self.TAB_KEY],
        )

        left_column, right_column = self.app._build_tab_columns(field_frame)

        dir_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(1, "语言目录显示"),
            padding="10",
        )
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="中文:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.field_zh_dir_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )
        ttk.Checkbutton(dir_frame, text="导出", variable=self.app.field_zh_check_var).grid(
            row=0, column=2, padx=(5, 0), pady=(0, 8)
        )

        ttk.Label(dir_frame, text="越南语:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.field_vn_dir_var,
            row=1,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )
        ttk.Checkbutton(dir_frame, text="导出", variable=self.app.field_vn_check_var).grid(
            row=1, column=2, padx=(5, 0), pady=(0, 8)
        )

        ttk.Label(dir_frame, text="泰语:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.field_th_dir_var,
            row=2,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )
        ttk.Checkbutton(dir_frame, text="导出", variable=self.app.field_th_check_var).grid(
            row=2, column=2, padx=(5, 0), pady=(0, 8)
        )

        ttk.Label(dir_frame, text="英语:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.field_en_dir_var,
            row=3,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )
        ttk.Checkbutton(dir_frame, text="导出", variable=self.app.field_en_check_var).grid(
            row=3, column=2, padx=(5, 0), pady=(0, 8)
        )

        ttk.Label(dir_frame, text="输出:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.app._workspace_path_display(
            dir_frame,
            self.app.field_output_dir_var,
            row=4,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            columnspan=2,
        )

        self.app.inline_messages[self.TAB_KEY] = self.app._create_inline_message(
            dir_frame, row=5, columnspan=3
        )

        options_frame = ttk.LabelFrame(
            right_column,
            text=self.app._format_section_title(2, "导出选项"),
            padding="10",
        )
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))

        self.app.field_recursive_check = ttk.Checkbutton(
            options_frame,
            text="递归扫描子目录",
            variable=self.app.field_recursive_var,
        )
        self.app.field_recursive_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))

        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, sticky=tk.W)

        ttk.Label(format_frame, text="格式:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            format_frame, text="JSON", variable=self.app.field_output_format_var, value="json"
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            format_frame, text="CSV", variable=self.app.field_output_format_var, value="csv"
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(
            format_frame, text="Excel", variable=self.app.field_output_format_var, value="excel"
        ).pack(side=tk.LEFT)

        action_panel = self.app._create_action_panel(right_column, 1)
        self.app._decorate_action_panel(
            action_panel,
            '3. 执行与结果',
            '路径请在「工作台」选择；此处为只读展示。JSON 导出成功后可一键带入「多语言提取」页；亦可复制结果或查看日志。',
        )

        self.app.field_extract_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_extraction'],
            command=self.start_field_extraction,
            style='Accent.TButton',
        )
        self.app.field_extract_button.pack(fill=tk.X)

        self.app.field_use_for_trt_button = ttk.Button(
            action_panel,
            text=self._button_labels['use_field_for_trt'],
            command=self.on_use_field_export_for_trt,
            state='disabled',
            style='Quiet.TButton',
        )
        self.app.field_use_for_trt_button.pack(fill=tk.X, pady=(8, 0))

        self.app.field_copy_button = ttk.Button(
            action_panel,
            text=self._button_labels['copy_results'],
            command=self.copy_field_json_result,
            style='Quiet.TButton',
        )
        self.app.field_copy_button.pack(fill=tk.X, pady=(8, 0))

        self.app.field_error_log_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_logs'],
            command=self.show_field_error_logs,
            style='Quiet.TButton',
        )
        self.app.field_error_log_button.pack(fill=tk.X, pady=(8, 0))

        self.app.field_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_field_results,
            style='Danger.TButton',
        )
        self.app.field_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.app.field_view_results_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog(self.TAB_KEY),
            style='Quiet.TButton',
        )
        self.app.field_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self.app._create_task_panel(action_panel, self.TAB_KEY)

    def validate_inputs(self, strict=False):
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        selections = [
            (lang_names['zh'], self.app.field_zh_check_var.get(), self.app.field_zh_dir_var.get().strip()),
            (lang_names['vn'], self.app.field_vn_check_var.get(), self.app.field_vn_dir_var.get().strip()),
            (lang_names['th'], self.app.field_th_check_var.get(), self.app.field_th_dir_var.get().strip()),
            (lang_names['en'], self.app.field_en_check_var.get(), self.app.field_en_dir_var.get().strip()),
        ]
        active = [(label, path) for label, enabled, path in selections if enabled]

        if not active:
            return False, '至少勾选一个语言并填写目录。', 'error' if strict else 'warning'

        for label, path in active:
            if not path:
                return False, f'{label}已勾选，但目录还未填写。', 'error' if strict else 'warning'
            if not os.path.exists(path):
                return False, f'{label}目录不存在，请重新选择。', 'error'

        output_dir = self.app.field_output_dir_var.get().strip()
        if output_dir and not os.path.exists(output_dir):
            return False, '输出目录不存在，请重新选择。', 'error'
        if not output_dir:
            return True, '未填写输出目录时，将自动使用首个有效语言目录。', 'info'
        return True, f'已选择 {len(active)} 个语言目录，结果输出到: {output_dir}', 'success'

    def refresh_validation(self):
        _, text, tone = self.validate_inputs(strict=False)
        self.app._set_inline_message(self.TAB_KEY, text, tone)

    def browse_language_dir(self, lang_code):
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        dir_path = filedialog.askdirectory(title=f"选择{lang_names.get(lang_code, '')}目录")
        if dir_path:
            if lang_code == 'zh':
                self.app.field_zh_dir_var.set(dir_path)
            elif lang_code == 'vn':
                self.app.field_vn_dir_var.set(dir_path)
            elif lang_code == 'th':
                self.app.field_th_dir_var.set(dir_path)
            elif lang_code == 'en':
                self.app.field_en_dir_var.set(dir_path)
            if not self.app.field_output_dir_var.get():
                self.app.field_output_dir_var.set(dir_path)

    def browse_scan_directory(self):
        dir_path = filedialog.askdirectory(title="选择扫描目录")
        if dir_path:
            self.app.field_zh_dir_var.set(dir_path)
            if not self.app.field_output_dir_var.get():
                self.app.field_output_dir_var.set(dir_path)

    def browse_output_directory(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.app.field_output_dir_var.set(dir_path)

    def _resolve_merged_json_path(self, output_dir, output_format, all_stats):
        if output_format != 'json':
            return None
        cand = Path(output_dir) / FIELD_EXTRACTION_MERGED_JSON_NAME
        if cand.is_file():
            return str(cand.resolve())
        for p in all_stats.get('output_files', []):
            try:
                if Path(p).name == FIELD_EXTRACTION_MERGED_JSON_NAME and Path(p).is_file():
                    return str(Path(p).resolve())
            except (OSError, TypeError, ValueError):
                continue
        return None

    def _after_extraction_for_trt_handoff(self, merged_path):
        self.app._field_last_merged_json_path = merged_path if merged_path else None
        btn = getattr(self.app, 'field_use_for_trt_button', None)
        if not btn:
            return
        if merged_path and os.path.isfile(merged_path):
            btn.config(state='normal')
        else:
            btn.config(state='disabled')

    def on_use_field_export_for_trt(self):
        path = self.app._field_last_merged_json_path
        if not path or not os.path.isfile(path):
            messagebox.showwarning(
                '无法衔接',
                f'未找到有效的合并 JSON「{FIELD_EXTRACTION_MERGED_JSON_NAME}」。\n'
                '请使用「JSON」输出格式重新执行字段导出。',
            )
            return
        self.app._apply_field_export_to_trt(path)

    def _finish_extraction_success_on_ui(self, merged_path, all_stats, output_files_str):
        self._after_extraction_for_trt_handoff(merged_path)
        self.app._complete_task_tracking(
            self.TAB_KEY,
            'success',
            '字段导出完成',
            [
                ('语言数', len(all_stats['languages'])),
                ('字段数', all_stats['total_fields']),
                ('输出文件', len(all_stats.get('output_files', []))),
            ],
            '输出文件和详细统计已生成。',
        )
        hint = ''
        if merged_path:
            hint = (
                f"\n\n合并 JSON 已生成，可点击「{self._button_labels['use_field_for_trt']}」"
                '\n自动填好多语言提取页的配置。'
            )
        self.app._finish_background_task_async(
            widgets_to_enable=(self.app.field_extract_button,),
            status_message='字段提取完成',
            dialog_kind='info',
            dialog_title='完成',
            dialog_message=(
                f'多语言字段提取完成!\n\n'
                f"处理语言数: {len(all_stats['languages'])}\n"
                f"总文件数: {all_stats['total_files']}\n"
                f"总工作表数: {all_stats['total_sheets']}\n"
                f"总字段数: {all_stats['total_fields']}\n\n"
                f'输出文件:\n{output_files_str}{hint}'
            ),
        )

    def start_field_extraction(self):
        directories = {}
        if self.app.field_zh_check_var.get() and self.app.field_zh_dir_var.get().strip():
            directories['zh'] = self.app.field_zh_dir_var.get().strip()
        if self.app.field_vn_check_var.get() and self.app.field_vn_dir_var.get().strip():
            directories['vn'] = self.app.field_vn_dir_var.get().strip()
        if self.app.field_th_check_var.get() and self.app.field_th_dir_var.get().strip():
            directories['th'] = self.app.field_th_dir_var.get().strip()
        if self.app.field_en_check_var.get() and self.app.field_en_dir_var.get().strip():
            directories['en'] = self.app.field_en_dir_var.get().strip()

        output_dir = self.app.field_output_dir_var.get().strip()

        valid, message, tone = self.validate_inputs(strict=True)
        self.app._set_inline_message(self.TAB_KEY, message, tone)
        if not valid:
            return

        if not output_dir:
            output_dir = list(directories.values())[0]
            self.app.field_output_dir_var.set(output_dir)

        output_format = self.app.field_output_format_var.get()
        recursive = self.app.field_recursive_var.get()

        handoff = getattr(self.app, 'field_use_for_trt_button', None)
        if handoff:
            handoff.config(state='disabled')
        self.app._field_last_merged_json_path = None

        extract_widgets = [self.app.field_extract_button]
        if handoff:
            extract_widgets.append(handoff)

        self.app._begin_task_tracking(
            self.TAB_KEY,
            '正在提取多语言字段...',
            {
                'field.zh_dir': self.app.field_zh_dir_var.get().strip(),
                'field.vn_dir': self.app.field_vn_dir_var.get().strip(),
                'field.th_dir': self.app.field_th_dir_var.get().strip(),
                'field.en_dir': self.app.field_en_dir_var.get().strip(),
                'field.output_dir': output_dir,
                'field.output_format': output_format,
                'field.recursive': recursive,
                'field.zh_enabled': self.app.field_zh_check_var.get(),
                'field.vn_enabled': self.app.field_vn_check_var.get(),
                'field.th_enabled': self.app.field_th_check_var.get(),
                'field.en_enabled': self.app.field_en_check_var.get(),
            },
        )

        self.app._start_background_task(
            self.run_extraction_thread,
            args=(directories, output_dir, output_format, recursive),
            status_message="正在提取表字段...",
            widgets_to_disable=tuple(extract_widgets),
        )

    def run_extraction_thread(self, directories, output_dir, output_format, recursive):
        try:
            self.app._clear_result_async(self.TAB_KEY)
            self.app.field_extractor.set_progress_callback(
                lambda msg, percentage=None: (
                    self.app._append_result_async(self.TAB_KEY, msg + "\n"),
                    self.app._call_on_ui_thread(
                        self.app._update_task_progress, self.TAB_KEY, msg, percentage
                    ),
                )
            )
            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_banner_block("开始提取多语言表字段信息...", width=60),
            )

            lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
            for lang, dir_path in directories.items():
                self.app._append_result_async(
                    self.TAB_KEY, f"{lang_names.get(lang, lang)}目录: {dir_path}\n"
                )

            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_key_value_lines([
                    ("输出目录", output_dir),
                    ("输出格式", output_format.upper()),
                    ("递归扫描", '是' if recursive else '否'),
                ]),
                "\n",
            )

            all_stats = self.app.field_extractor.process_multi_language_directories(
                directories=directories,
                output_folder=output_dir,
                output_format=output_format,
                recursive=recursive,
            )

            all_results = []
            for lang_code, lang_data in all_stats['languages'].items():
                if 'stats' in lang_data and 'results' in lang_data['stats']:
                    all_results.extend(lang_data['stats']['results'])
            self.app.field_extraction_results = all_results

            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_banner_block("多语言提取完成!", width=60, leading_newline=True),
            )

            for lang_code, lang_data in all_stats['languages'].items():
                stats = lang_data.get('stats', {})
                self.app._append_result_async(
                    self.TAB_KEY,
                    f"\n【{lang_data['name']}】文件数: {stats.get('total_files', 0)}, "
                    f"工作表: {stats.get('total_sheets', 0)}, 字段数: {stats.get('total_fields', 0)}\n",
                )

            self.app._append_result_batch_async(
                self.TAB_KEY,
                '\n',
                self.app._format_key_value_lines([
                    ("总文件数", all_stats['total_files']),
                    ("总工作表数", all_stats['total_sheets']),
                    ("总字段数", all_stats['total_fields']),
                ]),
                "\n输出文件:\n",
                self.app._format_prefixed_lines(all_stats.get('output_files', [])),
            )

            merged_path = self._resolve_merged_json_path(output_dir, output_format, all_stats)
            output_files_str = '\n'.join(all_stats.get('output_files', []))
            self.app._call_on_ui_thread(
                self._finish_extraction_success_on_ui,
                merged_path,
                all_stats,
                output_files_str,
            )
        except Exception as e:
            error_msg = traceback.format_exc()
            self.app._append_result_async(self.TAB_KEY, f"\n错误: {str(e)}\n")
            self.app._append_result_async(self.TAB_KEY, error_msg + "\n")
            self.app._call_on_ui_thread(self._after_extraction_for_trt_handoff, None)
            self.app._call_on_ui_thread(
                self.app._complete_task_tracking,
                self.TAB_KEY,
                'error',
                '字段导出失败',
                [('错误', 1)],
                str(e),
            )
            self.app._finish_background_task_async(
                widgets_to_enable=(self.app.field_extract_button,),
                status_message="字段提取失败",
                dialog_kind='error',
                dialog_title="错误",
                dialog_message=f"处理失败:\n{str(e)}",
            )

    def clear_field_results(self):
        self.app.clear_result(self.TAB_KEY)
        self.app.field_extraction_results = None
        self.app._field_last_merged_json_path = None
        handoff = getattr(self.app, 'field_use_for_trt_button', None)
        if handoff:
            handoff.config(state='disabled')
        self.app.field_extractor.clear_logs()
        self.app._set_task_panel_state(
            self.TAB_KEY,
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )

    def show_field_error_logs(self):
        logs = self.app.field_extractor.get_all_logs()
        errors = logs['errors']
        warnings = logs['warnings']

        if not errors and not warnings:
            messagebox.showinfo("日志信息", "没有错误或警告日志")
            return

        log_window = tk.Toplevel(self.app.root)
        log_window.title("字段提取 - 错误与警告日志")
        log_window.geometry("900x600")

        notebook = ttk.Notebook(log_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text=f"错误日志 ({len(errors)})")

        error_text = scrolledtext.ScrolledText(error_frame, wrap=tk.WORD, font=('Consolas', 9))
        error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if errors:
            for i, error in enumerate(errors, 1):
                error_text.insert(tk.END, f"{i}. {error}\n\n")
        else:
            error_text.insert(tk.END, "无错误日志")

        error_text.config(state='disabled')

        warning_frame = ttk.Frame(notebook)
        notebook.add(warning_frame, text=f"警告日志 ({len(warnings)})")

        warning_text = scrolledtext.ScrolledText(warning_frame, wrap=tk.WORD, font=('Consolas', 9))
        warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if warnings:
            for i, warning in enumerate(warnings, 1):
                warning_text.insert(tk.END, f"{i}. {warning}\n\n")
        else:
            warning_text.insert(tk.END, "无警告日志")

        warning_text.config(state='disabled')

        button_frame = ttk.Frame(log_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def save_logs():
            file_path = filedialog.asksaveasfilename(
                title="保存日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            )
            if file_path:
                if self.app.field_extractor.save_logs_to_file(Path(file_path)):
                    messagebox.showinfo("成功", f"日志已保存到:\n{file_path}")

        ttk.Button(button_frame, text="保存日志", command=save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=log_window.destroy).pack(side=tk.RIGHT, padx=5)

        stats_label = ttk.Label(
            button_frame,
            text=f"总计: {len(errors)} 个错误, {len(warnings)} 个警告",
            style='Info.TLabel',
        )
        stats_label.pack(side=tk.LEFT, padx=20)

    def copy_field_json_result(self):
        if not self.app.field_extraction_results:
            messagebox.showwarning("警告", "没有可复制的结果，请先执行字段提取")
            return

        try:
            json_data = [{
                "table_name": r['excel_file'],
                "sheet_name": r['sheet_name'],
                "fields_with_examples": r.get('fields_with_examples', []),
                "field_count": r['field_count']
            } for r in self.app.field_extraction_results]

            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)

            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(json_str)
            self.app.root.update()

            messagebox.showinfo("成功", f"JSON结果已复制到剪贴板\n共 {len(json_data)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败:\n{str(e)}")
