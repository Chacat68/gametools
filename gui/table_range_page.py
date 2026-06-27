#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多语言翻译提取页签。

该模块承载「多语言提取」页签的 UI、校验与后台任务编排，主界面只负责装配与共享变量。
"""

import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from core.constants import MERGED_JSON_LANGUAGE_KEYS, SUPPORTED_LANGUAGES


class TableRangePage:
    """多语言翻译提取页签控制器。"""

    TAB_KEY = 'table_range_translator'

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建多语言翻译提取页签。"""
        trt_frame = self.app._register_tab(
            self.TAB_KEY,
            '多语言提取',
            self._tab_descriptions[self.TAB_KEY],
        )

        left_column, right_column = self.app._build_tab_columns(trt_frame)

        json_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(1, "合并 JSON 路径显示"),
            padding="10",
        )
        json_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        json_frame.columnconfigure(1, weight=1)

        ttk.Label(json_frame, text="JSON:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            json_frame,
            self.app.trt_merged_json_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        self.app.trt_json_lang_label = ttk.Label(json_frame, text="", style='AccentInfo.TLabel')
        self.app.trt_json_lang_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))

        dir_frame = ttk.LabelFrame(
            right_column,
            text=self.app._format_section_title(2, "语言目录显示"),
            padding="10",
        )
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="中文:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.trt_zh_dir_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(dir_frame, text="越南语:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.trt_vn_dir_var,
            row=1,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(dir_frame, text="泰语:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.trt_th_dir_var,
            row=2,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        ttk.Label(dir_frame, text="英语:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.app._workspace_path_display(
            dir_frame,
            self.app.trt_en_dir_var,
            row=3,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 8),
        )

        output_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(3, "输出目录显示"),
            padding="10",
        )
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.app._workspace_path_display(
            output_frame,
            self.app.trt_output_dir_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
        )

        self.app.inline_messages[self.TAB_KEY] = self.app._create_inline_message(output_frame, row=1)

        action_panel = self.app._create_action_panel(right_column, 1)
        self.app._decorate_action_panel(
            action_panel,
            '4. 执行与结果',
            '路径请在「工作台」选择；此处为只读展示。提取后可直接查看输出结果。',
        )

        self.app.trt_process_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_extraction'],
            command=self.start_translation,
            style='Accent.TButton',
        )
        self.app.trt_process_button.pack(fill=tk.X)

        self.app.trt_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_results,
            style='Danger.TButton',
        )
        self.app.trt_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.app.trt_view_results_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog(self.TAB_KEY),
            style='Quiet.TButton',
        )
        self.app.trt_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self.app._create_task_panel(action_panel, self.TAB_KEY)

    def validate_inputs(self, strict=False):
        merged_json = self.app.trt_merged_json_var.get().strip()
        if not merged_json:
            return False, '请选择合并 JSON 配置文件。', 'error' if strict else 'warning'
        if not os.path.exists(merged_json):
            return False, 'JSON 配置文件不存在，请重新选择。', 'error'

        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        lang_dirs = [
            (lang_names['zh'], self.app.trt_zh_dir_var.get().strip()),
            (lang_names['vn'], self.app.trt_vn_dir_var.get().strip()),
            (lang_names['th'], self.app.trt_th_dir_var.get().strip()),
            (lang_names['en'], self.app.trt_en_dir_var.get().strip()),
        ]
        valid_dirs = [(label, path) for label, path in lang_dirs if path]
        if not valid_dirs:
            return False, '请至少填写一个语言目录。', 'error' if strict else 'warning'

        for label, path in valid_dirs:
            if not os.path.exists(path):
                return False, f'{label}目录不存在，请重新选择。', 'error'

        output_dir = self.app.trt_output_dir_var.get().strip()
        if output_dir and not os.path.exists(output_dir):
            return False, '输出目录不存在，请重新选择。', 'error'
        if not output_dir:
            return True, '未填写输出目录时，将自动使用首个语言目录。', 'info'
        return True, f'将从 {len(valid_dirs)} 个语言目录提取并输出到: {output_dir}', 'success'

    def refresh_validation(self):
        _, text, tone = self.validate_inputs(strict=False)
        self.app._set_inline_message(self.TAB_KEY, text, tone)

    def detect_merged_json_languages(self, json_path):
        """更新合并 JSON 语言检测标签（页签未创建或无标签时跳过）。"""
        label = getattr(self.app, 'trt_json_lang_label', None)
        if label is None:
            return
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
                label.config(text=f"✓ 检测到: {', '.join(detected_langs)}")
            else:
                keys_hint = '/'.join(MERGED_JSON_LANGUAGE_KEYS)
                label.config(text=f"⚠️ 未检测到有效语言配置（期望顶层键之一: {keys_hint}）")
        except FileNotFoundError:
            label.config(text="⚠️ 文件不存在")
        except json.JSONDecodeError as e:
            label.config(text=f"⚠️ JSON格式错误: {str(e)[:40]}")
        except Exception as e:
            label.config(text=f"⚠️ 读取失败: {str(e)[:50]}")

    def browse_merged_json(self):
        file_path = filedialog.askopenfilename(
            title="选择合并的JSON配置文件（可含 ZH/VN/TH/EN 等）",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )
        if file_path:
            self.app.trt_merged_json_var.set(file_path)
            self.detect_merged_json_languages(file_path)

    def browse_lang_json(self, lang_code):
        lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}
        file_path = filedialog.askopenfilename(
            title=f"选择{lang_names.get(lang_code, '')}JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )
        if file_path:
            if lang_code == 'zh':
                self.app.trt_zh_json_var.set(file_path)
            elif lang_code == 'vn':
                self.app.trt_vn_json_var.set(file_path)
            elif lang_code == 'th':
                self.app.trt_th_json_var.set(file_path)
            elif lang_code == 'en':
                self.app.trt_en_json_var.set(file_path)

    def browse_json_file(self):
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )
        if file_path:
            self.app.trt_json_var.set(file_path)

    def browse_vn_directory(self):
        dir_path = filedialog.askdirectory(title="选择越南文Excel文件目录")
        if dir_path:
            self.app.trt_vn_dir_var.set(dir_path)

    def browse_zh_directory(self):
        dir_path = filedialog.askdirectory(title="选择中文Excel文件目录（_zh后缀）")
        if dir_path:
            self.app.trt_zh_dir_var.set(dir_path)

    def browse_th_directory(self):
        dir_path = filedialog.askdirectory(title="选择泰文Excel文件目录（_th后缀）")
        if dir_path:
            self.app.trt_th_dir_var.set(dir_path)

    def browse_en_directory(self):
        dir_path = filedialog.askdirectory(title="选择英语Excel文件目录（_en后缀）")
        if dir_path:
            self.app.trt_en_dir_var.set(dir_path)

    def browse_output_directory(self):
        dir_path = filedialog.askdirectory(title="选择CSV输出目录")
        if dir_path:
            self.app.trt_output_dir_var.set(dir_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="保存翻译总表",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
        )
        if file_path:
            self.app.trt_output_var.set(file_path)

    def start_translation(self):
        merged_json = self.app.trt_merged_json_var.get().strip()
        zh_dir = self.app.trt_zh_dir_var.get().strip()
        vn_dir = self.app.trt_vn_dir_var.get().strip()
        th_dir = self.app.trt_th_dir_var.get().strip()
        en_dir = self.app.trt_en_dir_var.get().strip()
        output_dir = self.app.trt_output_dir_var.get().strip()

        valid, message, tone = self.validate_inputs(strict=True)
        self.app._set_inline_message(self.TAB_KEY, message, tone)
        if not valid:
            return

        lang_dirs = {}
        if zh_dir:
            lang_dirs['zh'] = zh_dir
        if vn_dir:
            lang_dirs['vn'] = vn_dir
        if th_dir:
            lang_dirs['th'] = th_dir
        if en_dir:
            lang_dirs['en'] = en_dir

        if not output_dir:
            output_dir = list(lang_dirs.values())[0]
            self.app.trt_output_dir_var.set(output_dir)

        output_file = self.app.table_range_translator.generate_output_filename(output_dir)

        self.app._begin_task_tracking(
            self.TAB_KEY,
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

        self.app._start_background_task(
            self.run_translation_thread,
            args=(merged_json, lang_dirs, output_file),
            status_message="正在提取翻译内容...",
            widgets_to_disable=(self.app.trt_process_button,),
        )

    def run_translation_thread(self, merged_json, lang_dirs, output_file):
        try:
            self.app._call_on_ui_thread(self.app.clear_result, self.TAB_KEY)

            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_banner_block("开始多语言翻译提取（合并JSON配置）...", width=70),
            )

            lang_names = {code: SUPPORTED_LANGUAGES[code]['name'] for code in SUPPORTED_LANGUAGES}

            self.app._append_result_async(self.TAB_KEY, f"合并JSON: {merged_json}\n")

            for lang, dir_path in lang_dirs.items():
                self.app._append_result_async(
                    self.TAB_KEY, f"{lang_names.get(lang, lang)}目录: {dir_path}\n"
                )

            self.app._append_result_batch_async(
                self.TAB_KEY,
                self.app._format_key_value_lines([("输出文件", output_file)]),
                "\n",
            )

            def progress_callback(msg):
                self.app._append_result_async(self.TAB_KEY, msg + "\n")
                self.app._call_on_ui_thread(
                    self.app._update_task_progress, self.TAB_KEY, msg
                )

            results = self.app.table_range_translator.process_with_merged_json(
                merged_json, lang_dirs, progress_callback=progress_callback
            )

            if results:
                self.app._append_result_async(
                    self.TAB_KEY, f"✓ 成功提取 {len(results)} 条数据\n\n"
                )

                self.app._append_result_async(self.TAB_KEY, "正在生成翻译CSV...\n")

                success = self.app.table_range_translator.generate_translation_csv(output_file)

                if success:
                    self.app._append_result_async(
                        self.TAB_KEY, f"✓ 翻译CSV已生成: {output_file}\n\n"
                    )

                    report = self.app.table_range_translator.get_processing_report()
                    self.app._append_result_async(self.TAB_KEY, report + "\n")

                    stats = self.app.table_range_translator.processing_stats
                    self.app._call_on_ui_thread(
                        self.app._complete_task_tracking,
                        self.TAB_KEY,
                        'success',
                        '多语言翻译提取完成',
                        [
                            ('处理表', f"{stats['processed_tables']}/{stats['total_tables']}"),
                            ('导出字段', stats['exported_fields']),
                            ('提取行数', stats['total_rows']),
                        ],
                        os.path.basename(output_file),
                    )
                    msg = (
                        f"多语言翻译提取完成！\n\n"
                        f"处理表格: {stats['processed_tables']}/{stats['total_tables']}\n"
                        f"导出字段: {stats['exported_fields']} 个\n"
                        f"提取数据: {stats['total_rows']} 行\n\n"
                        f"翻译CSV已生成:\n{output_file}"
                    )
                    self.app._finish_background_task_async(
                        widgets_to_enable=(self.app.trt_process_button,),
                        status_message="翻译提取完成",
                        dialog_kind='info',
                        dialog_title="完成",
                        dialog_message=msg,
                    )
                    return

                self.app._append_result_async(self.TAB_KEY, "✗ 生成翻译CSV失败\n")
                self.app._call_on_ui_thread(
                    self.app._complete_task_tracking,
                    self.TAB_KEY,
                    'error',
                    '翻译 CSV 生成失败',
                    [('错误', 1)],
                    '请检查输出目录与处理日志。',
                )
                self.app._finish_background_task_async(
                    widgets_to_enable=(self.app.trt_process_button,),
                    status_message="翻译提取失败",
                    dialog_kind='error',
                    dialog_title="错误",
                    dialog_message="生成翻译CSV失败",
                )
                return

            self.app._append_result_async(self.TAB_KEY, "✗ 没有提取到数据\n")
            self.app._call_on_ui_thread(
                self.app._complete_task_tracking,
                self.TAB_KEY,
                'warning',
                '没有提取到可导出数据',
                [('提取结果', 0)],
                '请检查 JSON 配置和源目录。',
            )
            self.app._finish_background_task_async(
                widgets_to_enable=(self.app.trt_process_button,),
                status_message="未提取到数据",
                dialog_kind='warning',
                dialog_title="警告",
                dialog_message="没有提取到数据，请检查JSON配置和Excel文件",
            )

        except Exception as e:
            details = str(e) or e.__class__.__name__
            error_msg = f"处理过程中发生错误: {details}"
            self.app._append_result_async(self.TAB_KEY, f"\n✗ {error_msg}\n")
            self.app._call_on_ui_thread(
                self.app._complete_task_tracking,
                self.TAB_KEY,
                'error',
                '多语言翻译提取失败',
                [('错误', 1)],
                error_msg,
            )
            self.app._finish_background_task_async(
                widgets_to_enable=(self.app.trt_process_button,),
                status_message="翻译提取失败",
                dialog_kind='error',
                dialog_title="错误",
                dialog_message=error_msg,
            )

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
