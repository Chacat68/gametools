#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Excel 数据处理（整合）页签。

承载「数据处理」页签的 UI、校验、预览与后台整合任务；源/输出路径与工作台共用 StringVar。
"""

import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox


class ExcelDataProcessorPage:
    """Excel 数据处理页签控制器。"""

    TAB_KEY = 'excel_data_processor'
    RESULT_KEY = 'excel_processor'

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建 Excel 数据处理页签。"""
        excel_frame = self.app._register_tab(
            self.TAB_KEY,
            '数据处理',
            self._tab_descriptions[self.TAB_KEY],
        )

        left_column, right_column = self.app._build_tab_columns(excel_frame)

        file_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(1, '源文件路径显示'),
            padding='10',
        )
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text='源文件:').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.app._workspace_path_display(
            file_frame,
            self.app.excel_input_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 5),
        )

        output_frame = ttk.LabelFrame(
            right_column,
            text=self.app._format_section_title(2, '输出目录显示'),
            padding='10',
        )
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 12))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text='目录:').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.app._workspace_path_display(
            output_frame,
            self.app.excel_output_folder_var,
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 5),
        )

        ttk.Label(output_frame, text='文件名:').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.app.excel_output_filename_entry = ttk.Entry(
            output_frame,
            textvariable=self.app.excel_output_filename_var,
            width=25,
            font=('Microsoft YaHei', 9),
        )
        self.app.excel_output_filename_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))

        options_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(3, '处理选项'),
            padding='10',
        )
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N))
        options_frame.columnconfigure(1, weight=1)

        ttk.Label(options_frame, text='分组列:').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.app.excel_group_column_entry = ttk.Entry(
            options_frame,
            textvariable=self.app.excel_group_column_var,
            width=15,
            font=('Microsoft YaHei', 9),
        )
        self.app.excel_group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        ttk.Label(options_frame, text='工作表前缀:').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.app.excel_sheet_prefix_entry = ttk.Entry(
            options_frame,
            textvariable=self.app.excel_sheet_prefix_var,
            width=15,
            font=('Microsoft YaHei', 9),
        )
        self.app.excel_sheet_prefix_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))

        self.app.excel_include_summary_check = ttk.Checkbutton(
            options_frame,
            text='汇总工作表',
            variable=self.app.excel_include_summary_var,
        )
        self.app.excel_include_summary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        self.app.inline_messages[self.TAB_KEY] = self.app._create_inline_message(
            left_column,
            row=2,
            columnspan=1,
        )

        action_panel = self.app._create_action_panel(right_column, 1)
        self.app._decorate_action_panel(
            action_panel,
            '4. 执行与结果',
            '源文件与输出目录请在「工作台」选择；此处为只读展示。整合后可预览数据或查看结果摘要。',
        )

        self.app.excel_process_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_consolidation'],
            command=self.start_consolidation,
            style='Accent.TButton',
        )
        self.app.excel_process_button.pack(fill=tk.X)

        self.app.excel_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_results,
            style='Danger.TButton',
        )
        self.app.excel_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.app.excel_preview_button = ttk.Button(
            action_panel,
            text=self._button_labels['preview_data'],
            command=self.preview_data,
            state='disabled',
            style='Quiet.TButton',
        )
        self.app.excel_preview_button.pack(fill=tk.X, pady=(8, 0))

        self.app.excel_view_results_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog(self.RESULT_KEY),
            style='Quiet.TButton',
        )
        self.app.excel_view_results_button.pack(fill=tk.X, pady=(8, 0))

        self.app._create_task_panel(action_panel, self.TAB_KEY)

    def validate_inputs(self, strict=False):
        input_file = self.app.excel_input_var.get().strip()
        output_folder = self.app.excel_output_folder_var.get().strip()
        output_filename = self.app.excel_output_filename_var.get().strip()

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

    def refresh_validation(self):
        _, text, tone = self.validate_inputs(strict=False)
        self.app._set_inline_message(self.TAB_KEY, text, tone)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title='选择输入Excel文件',
            filetypes=[('Excel文件', '*.xlsx *.xls'), ('所有文件', '*.*')],
        )
        if file_path:
            self.app.excel_input_var.set(file_path)
            if not self.app.excel_output_folder_var.get():
                self.app.excel_output_folder_var.set(str(Path(file_path).parent))
            if (
                not self.app.excel_output_filename_var.get()
                or self.app.excel_output_filename_var.get() == '整合结果.xlsx'
            ):
                input_path = Path(file_path)
                self.app.excel_output_filename_var.set(f'{input_path.stem}_整合{input_path.suffix}')

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title='选择输出文件夹')
        if folder_path:
            self.app.excel_output_folder_var.set(folder_path)
            if not self.app.excel_output_filename_var.get():
                self.app.excel_output_filename_var.set('整合结果.xlsx')

    def start_consolidation(self):
        input_file = self.app.excel_input_var.get().strip()
        output_folder = self.app.excel_output_folder_var.get().strip()
        output_filename = self.app.excel_output_filename_var.get().strip()

        valid, message, tone = self.validate_inputs(strict=True)
        self.app._set_inline_message(self.TAB_KEY, message, tone)
        if not valid:
            return

        output_file = os.path.join(output_folder, output_filename)

        self.app._begin_task_tracking(
            self.TAB_KEY,
            '正在整合 Excel 数据...',
            {
                'excel.input': input_file,
                'excel.output_folder': output_folder,
                'excel.output_filename': output_filename,
                'excel.output_file': output_file,
            },
        )

        group_column = self.app.excel_group_column_var.get().strip() or None
        include_summary = self.app.excel_include_summary_var.get()
        sheet_prefix = self.app.excel_sheet_prefix_var.get().strip()

        self.app._start_background_task(
            self._consolidation_process,
            args=(input_file, output_file, group_column, include_summary, sheet_prefix),
            status_message='正在处理Excel数据...',
            widgets_to_disable=(self.app.excel_process_button, self.app.excel_preview_button),
        )

    def _consolidation_process(self, input_file, output_file, group_column, include_summary, sheet_prefix):
        try:
            self.app._call_on_ui_thread(
                self.app._update_task_progress,
                self.TAB_KEY,
                f'正在处理: {os.path.basename(input_file)}',
                35,
            )
            self.app._call_on_ui_thread(self.app.clear_result, self.RESULT_KEY)

            self.app._append_result_batch_async(
                self.RESULT_KEY,
                self.app._format_key_value_lines(
                    [
                        ('开始处理文件', input_file),
                        ('输出文件', output_file),
                    ]
                ),
                '-' * 50 + '\n',
            )

            success = self.app.excel_processor.process_file(
                input_path=input_file,
                output_folder=os.path.dirname(output_file),
                output_filename=os.path.basename(output_file),
                group_column=group_column,
                include_summary=include_summary,
                sheet_prefix=sheet_prefix,
            )

            if success:
                self.app._call_on_ui_thread(self._show_success_result)
            else:
                self.app._call_on_ui_thread(self._show_error_result, '处理失败')

        except Exception as e:
            error_msg = f'处理过程中发生错误: {str(e)}'
            self.app._call_on_ui_thread(self._show_error_result, error_msg)

    def _show_success_result(self):
        report = self.app.excel_processor.get_process_report()
        self.app.append_result(self.RESULT_KEY, report)
        self.app.append_result(self.RESULT_KEY, '\n\n✅ Excel数据处理完成！')

        output_file = self.app.task_state.get(self.TAB_KEY, {}).get('inputs', {}).get('excel.output_file', '')
        self.app._complete_task_tracking(
            self.TAB_KEY,
            'success',
            'Excel 数据整合完成',
            metrics=[('输出文件', os.path.basename(output_file) if output_file else '已生成')],
            detail='预览和详细报告已可查看。',
        )
        self.app._finish_background_task(
            widgets_to_enable=(self.app.excel_process_button, self.app.excel_preview_button),
            status_message='Excel处理完成',
            dialog_kind='info',
            dialog_title='成功',
            dialog_message='Excel数据处理完成！请点击查看结果按钮查看详细报告',
        )

    def _show_error_result(self, error_msg):
        self.app.append_result(self.RESULT_KEY, f'❌ {error_msg}\n')
        self.app._complete_task_tracking(
            self.TAB_KEY,
            'error',
            'Excel 数据整合失败',
            metrics=[('错误', 1)],
            detail=error_msg,
        )
        self.app._finish_background_task(
            widgets_to_enable=(self.app.excel_process_button, self.app.excel_preview_button),
            status_message='Excel处理失败',
            dialog_kind='error',
            dialog_title='错误',
            dialog_message=error_msg,
        )

    def preview_data(self):
        input_file = self.app.excel_input_var.get().strip()

        if not input_file:
            messagebox.showerror('错误', '请先选择输入文件')
            return

        if not os.path.exists(input_file):
            messagebox.showerror('错误', '输入文件不存在')
            return

        try:
            df = self.app.excel_processor.read_excel_file(input_file)

            preview_text = f'文件预览: {os.path.basename(input_file)}\n'
            preview_text += f'总行数: {len(df)}\n'
            preview_text += f'总列数: {len(df.columns)}\n'
            preview_text += f'列名: {list(df.columns)}\n\n'

            preview_text += '前5行数据:\n'
            preview_text += df.head().to_string()

            if len(df) > 0:
                first_col = df.columns[0]
                unique_values = df[first_col].unique()
                preview_text += f"\n\n第一列 '{first_col}' 的唯一值:\n"
                for i, value in enumerate(unique_values[:10]):
                    preview_text += f'{i + 1}. {value}\n'
                if len(unique_values) > 10:
                    preview_text += f'... 还有 {len(unique_values) - 10} 个值\n'

            self.app.clear_result(self.RESULT_KEY)
            self.app.append_result(self.RESULT_KEY, preview_text)
            messagebox.showinfo('预览', '预览数据加载完成！请点击查看结果按钮查看')

        except Exception as e:
            messagebox.showerror('错误', f'预览数据失败: {str(e)}')

    def clear_results(self):
        self.app.clear_result(self.RESULT_KEY)
        self.app._set_task_panel_state(
            self.TAB_KEY,
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )
