#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON格式检测工具 - 图形界面版本
基于tkinter的GUI界面，用于检测JSON文件中text字段的格式一致性
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from gui.base_detector_gui import BaseDetectorGUI, run_detector_gui
from tools.json_format_detector.json_format_detector import JSONFormatDetector


class JSONFormatDetectorGUI(BaseDetectorGUI):
    """JSON格式检测工具图形界面"""
    
    def __init__(self, root):
        super().__init__(
            root, 
            title="JSON格式检测工具",
            geometry="800x600",
            min_size=(600, 400)
        )
    
    def _create_detector(self):
        """创建JSON格式检测器"""
        return JSONFormatDetector()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self.main_frame, text="JSON格式检测工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # JSON文件路径
        ttk.Label(file_frame, text="JSON文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(file_frame, text="浏览", command=self._browse_file)
        self.browse_button.grid(row=0, column=2)
        
        # 字段名设置
        ttk.Label(file_frame, text="检测字段:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.text_key_var = tk.StringVar(value="text")
        self.text_key_entry = ttk.Entry(file_frame, textvariable=self.text_key_var, width=20)
        self.text_key_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
    
    def _browse_file(self):
        """浏览文件对话框"""
        file_path = filedialog.askopenfilename(
            title="选择JSON文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def _get_detection_params(self):
        """获取检测参数"""
        file_path = self.file_path_var.get().strip()
        text_key = self.text_key_var.get().strip()
        
        if not file_path:
            return False, None, "请选择JSON文件"
        
        if not text_key:
            return False, None, "请输入检测字段名"
        
        if not os.path.exists(file_path):
            return False, None, "文件不存在"
        
        return True, {"file_path": file_path, "text_key": text_key}, None
    
    def _run_detection(self, params):
        """执行检测"""
        return self.detector.detect_format(params["file_path"], params["text_key"])


def main():
    """主函数"""
    run_detector_gui(JSONFormatDetectorGUI)


if __name__ == "__main__":
    main()
