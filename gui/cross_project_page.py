#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨项目翻译页签。

该模块承载跨项目翻译页签的 UI 与任务编排，主界面只负责装配。
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class CrossProjectPage:
    """跨项目翻译页签控制器。"""

    TAB_KEY = 'cross_project_translator'

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建跨项目翻译对应页签。"""
        translator_frame = self.app._register_tab(
            self.TAB_KEY,
            '跨项目翻译',
            self._tab_descriptions[self.TAB_KEY],
        )

        left_column, right_column = self.app._build_tab_columns(
            translator_frame,
            left_weight=5,
            right_weight=2,
        )

        file_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(1, "输入路径显示"),
            padding="10",
        )
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="映射:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.app._workspace_path_display(
            file_frame,
            self.app.cpt_mapping_file_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 8),
            pady=2,
        )

        ttk.Label(file_frame, text="目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.app._workspace_path_display(
            file_frame,
            self.app.cpt_project_dir_var,
            row=1,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 8),
            pady=2,
        )

        ttk.Label(file_frame, text="结果:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.app._workspace_path_display(
            file_frame,
            self.app.cpt_output_file_var,
            row=2,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 8),
            pady=2,
        )

        self.app.inline_messages[self.TAB_KEY] = self.app._create_inline_message(file_frame, row=3)

        action_panel = self.app._create_action_panel(right_column, 0)
        self.app._decorate_action_panel(
            action_panel,
            '2. 执行与结果',
            '路径请在「工作台」选择；此处为只读展示。执行后可直接导出或查看翻译对应结果。',
        )

        self.app.cpt_process_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_generation'],
            command=self.start_translation,
            style='Accent.TButton',
        )
        self.app.cpt_process_button.pack(fill=tk.X)

        self.app.cpt_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_results,
            style='Danger.TButton',
        )
        self.app.cpt_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.app.cpt_export_button = ttk.Button(
            action_panel,
            text=self._button_labels['export_results'],
            command=self.export_results,
            state="disabled",
            style='Quiet.TButton',
        )
        self.app.cpt_export_button.pack(fill=tk.X, pady=(8, 0))

        self.app.cpt_view_results_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog(self.TAB_KEY),
            style='Quiet.TButton',
        )
        self.app.cpt_view_results_button.pack(fill=tk.X, pady=(8, 0))
        self.app._create_task_panel(action_panel, self.TAB_KEY)

    def validate_inputs(self, strict=False):
        mapping_file = self.app.cpt_mapping_file_var.get().strip()
        project_dir = self.app.cpt_project_dir_var.get().strip()
        output_file = self.app.cpt_output_file_var.get().strip()

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

    def refresh_validation(self):
        _, text, tone = self.validate_inputs(strict=False)
        self.app._set_inline_message(self.TAB_KEY, text, tone)

    def browse_mapping_file(self):
        file_path = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            self.app.cpt_mapping_file_var.set(file_path)
            if not self.app.cpt_output_file_var.get():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(
                    os.path.dirname(file_path),
                    f"{base_name}_翻译对应结果.xlsx",
                )
                self.app.cpt_output_file_var.set(output_path)

    def browse_project_directory(self):
        dir_path = filedialog.askdirectory(title="选择项目目录")
        if dir_path:
            self.app.cpt_project_dir_var.set(dir_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*"),
            ],
        )
        if file_path:
            self.app.cpt_output_file_var.set(file_path)

    def start_translation(self):
        mapping_file = self.app.cpt_mapping_file_var.get().strip()
        project_dir = self.app.cpt_project_dir_var.get().strip()
        output_file = self.app.cpt_output_file_var.get().strip()

        valid, message, tone = self.validate_inputs(strict=True)
        self.app._set_inline_message(self.TAB_KEY, message, tone)
        if not valid:
            return

        self.app._begin_task_tracking(
            self.TAB_KEY,
            '正在建立跨项目翻译对应...',
            {
                'cross.mapping': mapping_file,
                'cross.project_dir': project_dir,
                'cross.output_file': output_file,
            },
        )

        self.app._start_background_task(
            self._run_translation,
            args=(mapping_file, project_dir, output_file),
            status_message="正在处理翻译对应...",
            widgets_to_disable=(self.app.cpt_process_button,),
        )

    def _run_translation(self, mapping_file, project_dir, output_file):
        succeeded = False
        completion_message = "翻译对应处理失败，请查看结果详情"
        metrics = []

        try:
            self.app._call_on_ui_thread(self.app.clear_result, self.TAB_KEY)
            self.app._configure_widget_async(self.app.cpt_export_button, state="disabled")
            self.app._call_on_ui_thread(
                self.app._update_task_progress,
                self.TAB_KEY,
                f"正在分析映射表: {os.path.basename(mapping_file)}",
                24,
            )

            self.app._append_result_batch_async(
                self.TAB_KEY,
                "开始处理翻译对应...\n",
                self.app._format_key_value_lines([
                    ("映射文件", mapping_file),
                    ("项目目录", project_dir),
                    ("输出文件", output_file),
                ]),
                '=' * 60 + '\n',
            )

            translator = self.app.cross_project_translator
            results = translator.process_translation_mapping(mapping_file, project_dir)
            self.app._call_on_ui_thread(
                self.app._update_task_progress,
                self.TAB_KEY,
                '正在生成结果与导出文件...',
                72,
            )

            if results:
                report = translator.get_processing_report()
                self.app._append_result_async(self.TAB_KEY, f"{report}\n")

                if translator.export_results(output_file):
                    self.app._append_result_async(self.TAB_KEY, f"结果已导出到: {output_file}\n")
                    self.app._configure_widget_async(self.app.cpt_export_button, state="normal")
                    succeeded = True
                    completion_message = "翻译对应完成！请点击查看结果按钮查看详细报告"
                    failed_count = len([item for item in results if item.get('status') != 'success'])
                    metrics = [
                        ('结果数', len(results)),
                        ('失败项', failed_count),
                        ('导出文件', os.path.basename(output_file)),
                    ]
                    cache_stats = getattr(translator, 'get_cache_stats', None)
                    if callable(cache_stats):
                        stats = cache_stats()
                        hit_rate = stats.get('hit_rate')
                        if hit_rate:
                            metrics.append(('缓存命中率', hit_rate))
                else:
                    self.app._append_result_async(self.TAB_KEY, "导出失败！\n")
                    completion_message = "翻译对应结果导出失败，请查看结果详情"
                    metrics = [('结果数', len(results)), ('导出', '失败')]

                self.app._append_result_batch_async(
                    self.TAB_KEY,
                    "\n详细结果（前20条）:\n",
                    '=' * 60 + '\n',
                )
                for result in results[:20]:
                    status_icon = "✅" if result.get('status') == 'success' else "❌"
                    content_preview = str(result.get('content', ''))[:50]
                    self.app._append_result_async(
                        self.TAB_KEY,
                        f"{status_icon} 第{result.get('index')}行: {result.get('file_name')} -> {content_preview}...\n",
                    )
                if len(results) > 20:
                    self.app._append_result_async(
                        self.TAB_KEY,
                        f"... 还有 {len(results) - 20} 条结果，请查看导出的Excel文件\n",
                    )
            else:
                self.app._append_result_async(self.TAB_KEY, "处理失败，没有生成结果\n")
                completion_message = "处理失败，没有生成结果"

            self.app._append_result_async(self.TAB_KEY, "\n处理完成！\n")
        except Exception as exc:
            error_msg = f"处理过程中发生错误: {str(exc)}"
            self.app._append_result_async(self.TAB_KEY, f"❌ {error_msg}\n")
            completion_message = error_msg
        finally:
            self.app._call_on_ui_thread(
                self._finish_translation,
                succeeded,
                completion_message,
                metrics,
            )

    def _finish_translation(self, succeeded, completion_message, metrics=None):
        self.app._complete_task_tracking(
            self.TAB_KEY,
            'success' if succeeded else 'error',
            '跨项目翻译完成' if succeeded else '跨项目翻译失败',
            metrics=metrics or [],
            detail=completion_message,
        )
        self.app._finish_background_task(
            widgets_to_enable=(self.app.cpt_process_button,),
            status_message="翻译对应完成" if succeeded else "翻译对应失败",
            dialog_kind='info' if succeeded else 'error',
            dialog_title="完成" if succeeded else "错误",
            dialog_message=completion_message,
        )

    def clear_results(self):
        self.app.clear_result(self.TAB_KEY)
        self.app.cpt_export_button.config(state="disabled")
        self.app._set_task_panel_state(
            self.TAB_KEY,
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )

    def export_results(self):
        if not self.app.cross_project_translator.translation_results:
            messagebox.showwarning("警告", "没有结果可导出")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出翻译对应结果",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*"),
            ],
        )

        if file_path:
            if self.app.cross_project_translator.export_results(file_path):
                messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
