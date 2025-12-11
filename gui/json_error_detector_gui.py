#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON错误检测工具 - 图形界面版本
基于tkinter的GUI界面，用于检测JSON文件中的各种错误
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from gui.base_detector_gui import BaseDetectorGUI, run_detector_gui
from tools.json_error_detector.json_error_detector import JSONErrorDetector


class JSONErrorDetectorGUI(BaseDetectorGUI):
    """JSON错误检测工具图形界面"""
    
    def __init__(self, root):
        super().__init__(
            root, 
            title="JSON错误检测工具",
            geometry="900x700",
            min_size=(700, 500)
        )
    
    def _create_detector(self):
        """创建JSON错误检测器"""
        return JSONErrorDetector()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(self.main_frame, text="JSON错误检测工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 描述
        desc_label = ttk.Label(self.main_frame, 
                              text="检测JSON文件或文件夹中的语法错误、结构错误、数据类型错误、编码错误和性能问题",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(0, 20))
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(self.main_frame, text="路径选择", padding="10")
        path_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        # 路径输入
        ttk.Label(path_frame, text="路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 浏览按钮
        self.browse_button = ttk.Button(path_frame, text="浏览文件夹", command=self._browse_folder)
        self.browse_button.grid(row=0, column=2)
        
        # 调整主框架行配置（按钮在row=3，结果在row=4）
        self.main_frame.rowconfigure(4, weight=1)
    
    def _browse_folder(self):
        """浏览文件夹对话框"""
        folder_path = filedialog.askdirectory(title="选择包含JSON文件的文件夹")
        if folder_path:
            self.path_var.set(folder_path)
    
    def _get_detection_params(self):
        """获取检测参数"""
        path = self.path_var.get().strip()
        
        if not path:
            return False, None, "请选择路径"
        
        if not os.path.exists(path):
            return False, None, "路径不存在"
        
        return True, {"path": path}, None
    
    def _run_detection(self, params):
        """执行检测"""
        path = params["path"]
        
        if os.path.isdir(path):
            return self.detector.detect_errors_in_folder(path)
        else:
            return self.detector.detect_errors(path)
    
    def _create_buttons(self):
        """重写按钮创建，调整位置"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.detect_button = ttk.Button(button_frame, text="开始检测", 
                                       command=self.start_detection, style="Accent.TButton")
        self.detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空结果", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="保存报告", 
                                     command=self.save_report, state="disabled")
        self.save_button.pack(side=tk.LEFT)
    
    def _create_result_area(self):
        """重写结果区域，调整位置"""
        result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding="10")
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    height=25)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_status_bar(self):
        """重写状态栏，调整位置"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0))


def main():
    """主函数"""
    run_detector_gui(JSONErrorDetectorGUI)


if __name__ == "__main__":
    main()
