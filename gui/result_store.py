#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 结果内容存储。

集中管理各功能页的文本结果，避免主界面继续直接维护结果字典。
"""


class ResultStore:
    """按结果类型保存、追加和读取文本内容。"""

    def __init__(self, initial_keys=None):
        self.storage = {key: "" for key in (initial_keys or [])}

    def append(self, result_type, text):
        """追加指定类型的结果文本。"""
        if result_type not in self.storage:
            self.storage[result_type] = ""
        self.storage[result_type] += text

    def clear(self, result_type):
        """清空指定类型的结果文本。"""
        self.storage[result_type] = ""

    def get(self, result_type, default=""):
        """读取指定类型的结果文本。"""
        return self.storage.get(result_type, default)
