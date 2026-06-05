#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 后台任务辅助封装。"""

import threading


class TaskRunner:
    """统一处理后台线程启动和主线程 UI 回调。"""

    def __init__(self, root, status_var_getter, message_handler, thread_module=None):
        self.root = root
        self._status_var_getter = status_var_getter
        self._message_handler = message_handler
        self._thread_module = thread_module or threading

    def call_on_ui_thread(self, callback, *args, **kwargs):
        """把回调调度到 Tk 主线程执行。"""
        self.root.after(0, lambda: callback(*args, **kwargs))

    def start_background_task(self, target, args=(), status_message=None, widgets_to_disable=()):
        """启动后台任务，并在启动前冻结相关控件。"""
        for widget in widgets_to_disable:
            widget.config(state="disabled")
        if status_message:
            self._set_status(status_message)

        thread = self._thread_module.Thread(target=target, args=args)
        thread.daemon = True
        thread.start()
        return thread

    def finish_background_task(self, widgets_to_enable=(), status_message=None,
                               dialog_kind=None, dialog_title=None, dialog_message=None):
        """完成后台任务后的控件恢复、状态更新和提示。"""
        for widget in widgets_to_enable:
            widget.config(state="normal")
        if status_message:
            self._set_status(status_message)
        if dialog_kind and dialog_message:
            self._message_handler(dialog_kind, dialog_title or "提示", dialog_message)

    def finish_background_task_async(self, widgets_to_enable=(), status_message=None,
                                     dialog_kind=None, dialog_title=None, dialog_message=None):
        """从后台线程安全触发任务收尾。"""
        self.call_on_ui_thread(
            self.finish_background_task,
            widgets_to_enable,
            status_message,
            dialog_kind,
            dialog_title,
            dialog_message,
        )

    def _set_status(self, text):
        status_var = self._status_var_getter()
        if status_var is not None:
            status_var.set(text)
