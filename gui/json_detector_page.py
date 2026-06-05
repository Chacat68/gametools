#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON 检测页签。

该模块承载 JSON 检测页签的 UI 创建和页面动作，主界面只负责装配。
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class JsonDetectorPage:
    """JSON 检测页签控制器。"""

    def __init__(self, app, tab_descriptions, button_labels):
        self.app = app
        self._tab_descriptions = tab_descriptions
        self._button_labels = button_labels

    def build(self):
        """创建 JSON 错误检测工具页签。"""
        json_frame = self.app._register_tab(
            'json_detector',
            'JSON检测',
            self._tab_descriptions['json_detector']
        )

        left_column, right_column = self.app._build_tab_columns(
            json_frame,
            left_weight=5,
            right_weight=2,
        )

        path_frame = ttk.LabelFrame(
            left_column,
            text=self.app._format_section_title(1, "检测目标"),
            padding="10",
        )
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 8))
        path_frame.columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="路径:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(0, 10),
            pady=(0, 5),
        )
        if not hasattr(self.app, 'json_path_var') or self.app.json_path_var is None:
            self.app.json_path_var = tk.StringVar()
        self.app.json_path_entry = ttk.Entry(
            path_frame,
            textvariable=self.app.json_path_var,
            font=("Microsoft YaHei", 9),
        )
        self.app.json_path_entry.grid(
            row=0,
            column=1,
            sticky=(tk.W, tk.E),
            padx=(0, 10),
            pady=(0, 5),
        )

        self.app.json_browse_button = ttk.Button(
            path_frame,
            text="选择",
            command=self.browse_folder,
            style='Subtle.TButton',
        )
        self.app.json_browse_button.grid(row=0, column=2, pady=(0, 5))

        self.app.inline_messages['json_detector'] = self.app._create_inline_message(path_frame, row=1)

        action_panel = self.app._create_action_panel(right_column, 0)
        self.app._decorate_action_panel(
            action_panel,
            '2. 执行与结果',
            '检测后可直接保存报告或查看问题结果。',
        )

        self.app.json_detect_button = ttk.Button(
            action_panel,
            text=self._button_labels['start_detection'],
            command=self.start_detection,
            style='Accent.TButton',
        )
        self.app.json_detect_button.pack(fill=tk.X)

        self.app.json_clear_button = ttk.Button(
            action_panel,
            text=self._button_labels['clear_results'],
            command=self.clear_results,
            style='Danger.TButton',
        )
        self.app.json_clear_button.pack(fill=tk.X, pady=(8, 0))

        self.app.json_save_button = ttk.Button(
            action_panel,
            text=self._button_labels['save_report'],
            command=self.save_report,
            state="disabled",
            style='Quiet.TButton',
        )
        self.app.json_save_button.pack(fill=tk.X, pady=(8, 0))

        self.app.json_view_results_button = ttk.Button(
            action_panel,
            text=self._button_labels['view_results'],
            command=lambda: self.app.show_results_dialog('json_detector'),
            style='Quiet.TButton',
        )
        self.app.json_view_results_button.pack(fill=tk.X, pady=(8, 0))
        self.app._create_task_panel(action_panel, 'json_detector')

    def browse_folder(self):
        """选择 JSON 文件夹。"""
        folder_path = filedialog.askdirectory(title="选择包含JSON文件的文件夹")
        if folder_path:
            self.app.json_path_var.set(folder_path)

    def start_detection(self):
        """开始 JSON 错误检测。"""
        path = self.app.json_path_var.get().strip()

        valid, message, tone = self.app._validate_json_inputs(strict=True)
        self.app._set_inline_message('json_detector', message, tone)
        if not valid:
            return

        self.app._begin_task_tracking(
            'json_detector',
            '正在扫描 JSON 文件...',
            {'json_detector.path': path},
        )

        self.app._start_background_task(
            self._run_detection,
            args=(path,),
            status_message="正在检测...",
            widgets_to_disable=(self.app.json_detect_button,),
        )

    def _run_detection(self, path):
        """后台执行 JSON 检测。"""
        try:
            self.app._call_on_ui_thread(
                self.app._update_task_progress,
                'json_detector',
                f"正在检查: {os.path.basename(path) or path}",
                30,
            )
            if os.path.isdir(path):
                report = self.app.json_detector.detect_errors_in_folder(path)
            else:
                report = self.app.json_detector.detect_errors(path)

            self.app._call_on_ui_thread(self._update_results, report)
        except Exception as e:
            error_msg = f"检测过程中发生错误: {str(e)}"
            self.app._call_on_ui_thread(self._show_error, error_msg)

    def _update_results(self, report):
        """更新 JSON 检测结果。"""
        self.app.clear_result('json_detector')
        self.app.append_result('json_detector', report)

        self.app._complete_task_tracking(
            'json_detector',
            'success',
            'JSON 检测完成',
            metrics=[('报告行数', len([line for line in report.splitlines() if line.strip()]))],
            detail='详细报告可在结果窗口中查看或导出。',
        )

        self.app.json_save_button.config(state="normal")
        self.app._finish_background_task(
            widgets_to_enable=(self.app.json_detect_button,),
            status_message="检测完成",
            dialog_kind='info',
            dialog_title="完成",
            dialog_message="JSON检测完成！请点击查看结果按钮查看详细报告",
        )

    def _show_error(self, error_msg):
        """显示 JSON 检测错误。"""
        self.app.clear_result('json_detector')
        self.app.append_result('json_detector', error_msg)

        self.app._complete_task_tracking(
            'json_detector',
            'error',
            'JSON 检测失败',
            metrics=[('错误', 1)],
            detail=error_msg,
        )

        self.app._finish_background_task(
            widgets_to_enable=(self.app.json_detect_button,),
            status_message="检测失败",
            dialog_kind='error',
            dialog_title="错误",
            dialog_message=error_msg,
        )

    def clear_results(self):
        """清空 JSON 检测结果。"""
        self.app.clear_result('json_detector')
        self.app.json_save_button.config(state="disabled")
        self.app._set_task_panel_state(
            'json_detector',
            '尚未开始',
            message='结果已清空',
            progress=0,
            summary='最近结果已清空。',
            tone='muted',
        )

    def save_report(self):
        """保存 JSON 检测报告。"""
        content = self.app.get_result('json_detector').strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存检测报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"报告已保存到: {file_path}")
                self.app.status_var.set(f"报告已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
