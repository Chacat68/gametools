#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools - 统一用户界面
集成越南文检测和JSON格式检测工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import subprocess

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from core.localization_checker import LocalizationChecker
from core.excel_vietnamese_scanner import ExcelVietnameseScanner
from core.vietnamese_excel_processor import VietnameseExcelProcessor
from tools.json_error_detector.json_error_detector import JSONErrorDetector
from tools.excel_data_processor import ExcelDataProcessor
from tools.excel_text_extractor import ExcelTextExtractor
from version import get_version, format_version_string, get_description, get_latest_changes


class GameToolsUnified:
    """gametools统一界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"gametools - 游戏工具集 v{get_version()}")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 800)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化检测器
        self.localization_checker = LocalizationChecker()
        self.excel_scanner = ExcelVietnameseScanner()
        self.vietnamese_processor = VietnameseExcelProcessor()
        self.json_detector = JSONErrorDetector()
        self.excel_processor = ExcelDataProcessor()
        self.text_extractor = ExcelTextExtractor()
        
        # 扫描状态
        self.is_scanning = False
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 18, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 10))
        style.configure('Success.TLabel', font=('Microsoft YaHei', 10), foreground='green')
        style.configure('Error.TLabel', font=('Microsoft YaHei', 10), foreground='red')
        style.configure('Accent.TButton', font=('Microsoft YaHei', 10, 'bold'))
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题区域（隐藏）
        # title_frame = ttk.Frame(main_frame)
        # title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        # title_frame.columnconfigure(0, weight=1)
        
        # # 主标题
        # title_label = ttk.Label(title_frame, text="gametools - 游戏工具集", 
        #                        style='Title.TLabel')
        # title_label.grid(row=0, column=0, pady=(0, 5))
        
        # # 副标题
        # subtitle_label = ttk.Label(title_frame, text="集成策划本地化、JSON检测、Excel处理、翻译提取等功能", 
        #                           style='Info.TLabel')
        # subtitle_label.grid(row=1, column=0)
        
        # 创建笔记本控件（页签）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # 创建各个功能页签
        self.create_vietnamese_processor_tab()
        self.create_json_detector_tab()
        self.create_excel_data_processor_tab()
        self.create_excel_text_extractor_tab()
        self.create_about_tab()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding="3")
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
    
    def create_vietnamese_processor_tab(self):
        """创建越南文检测和导出页签"""
        # 越南文处理器框架
        processor_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(processor_frame, text="越南文检测导出")
        
        # 配置网格
        processor_frame.columnconfigure(0, weight=1)
        processor_frame.rowconfigure(2, weight=1)
        
        # 标题和描述
        header_frame = ttk.Frame(processor_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="越南文检测和导出工具", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        desc_label = ttk.Label(header_frame, text="检测Excel和CSV文件中的越南文内容，并导出详细结果到Excel文件", 
                              style='Info.TLabel')
        desc_label.grid(row=1, column=0)
        
        # 控制面板
        control_frame = ttk.Frame(processor_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(control_frame, text="扫描设置", padding="12")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # 扫描目录
        ttk.Label(dir_frame, text="扫描目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.vp_scan_dir_var = tk.StringVar()
        self.vp_scan_dir_entry = ttk.Entry(dir_frame, textvariable=self.vp_scan_dir_var, 
                                          font=("Microsoft YaHei", 9))
        self.vp_scan_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.vp_scan_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                               command=self.browse_vp_scan_directory)
        self.vp_scan_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出文件夹
        ttk.Label(dir_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.vp_output_folder_var = tk.StringVar()
        self.vp_output_folder_entry = ttk.Entry(dir_frame, textvariable=self.vp_output_folder_var, 
                                               font=("Microsoft YaHei", 9))
        self.vp_output_folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        self.vp_output_browse_button = ttk.Button(dir_frame, text="选择输出文件夹", 
                                                 command=self.browse_vp_output_folder)
        self.vp_output_browse_button.grid(row=1, column=2, pady=(5, 0))
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(control_frame, text="处理选项", padding="12")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 递归扫描选项
        self.vp_recursive_var = tk.BooleanVar(value=True)
        self.vp_recursive_check = ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                                                 variable=self.vp_recursive_var)
        self.vp_recursive_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # 输出文件选项
        output_options_frame = ttk.Frame(options_frame)
        output_options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.vp_create_excel_var = tk.BooleanVar(value=True)
        self.vp_create_excel_check = ttk.Checkbutton(output_options_frame, text="创建Excel结果文件", 
                                                    variable=self.vp_create_excel_var)
        self.vp_create_excel_check.pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 主要操作按钮
        self.vp_process_button = ttk.Button(button_frame, text="🔍 开始检测导出", 
                                           command=self.start_vietnamese_processing, 
                                           style='Accent.TButton')
        self.vp_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.vp_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                         command=self.clear_vp_results)
        self.vp_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.vp_demo_button = ttk.Button(button_frame, text="📁 创建演示文件", 
                                        command=self.create_demo_files)
        self.vp_demo_button.pack(side=tk.LEFT)
        
        # 进度条
        progress_frame = ttk.Frame(control_frame)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.vp_progress_var = tk.StringVar(value="就绪")
        self.vp_progress_label = ttk.Label(progress_frame, textvariable=self.vp_progress_var)
        self.vp_progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.vp_progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.vp_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(processor_frame, text="处理结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.vp_result_text = scrolledtext.ScrolledText(result_frame, 
                                                       wrap=tk.WORD, 
                                                       font=("Consolas", 9),
                                                       height=12)
        self.vp_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    
    def create_json_detector_tab(self):
        """创建JSON错误检测工具页签"""
        # JSON检测工具框架
        json_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(json_frame, text="JSON错误检测工具")
        
        # 配置网格
        json_frame.columnconfigure(0, weight=1)
        json_frame.rowconfigure(2, weight=1)
        
        # 标题和描述
        header_frame = ttk.Frame(json_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="JSON错误检测器", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        desc_label = ttk.Label(header_frame, text="检测JSON文件中的语法错误、结构错误、数据类型错误、编码错误和性能问题", 
                              style='Info.TLabel')
        desc_label.grid(row=1, column=0)
        
        # 控制面板
        control_frame = ttk.Frame(json_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(control_frame, text="路径选择", padding="12")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        # 路径输入
        ttk.Label(path_frame, text="路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.json_path_var = tk.StringVar()
        self.json_path_entry = ttk.Entry(path_frame, textvariable=self.json_path_var, 
                                       font=("Microsoft YaHei", 9))
        self.json_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.json_browse_button = ttk.Button(path_frame, text="浏览文件夹", 
                                            command=self.browse_json_folder)
        self.json_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        
        # 操作按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 主要操作按钮
        self.json_detect_button = ttk.Button(button_frame, text="🔍 开始检测", 
                                            command=self.start_json_detection, 
                                            style='Accent.TButton')
        self.json_detect_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.json_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                           command=self.clear_json_results)
        self.json_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.json_save_button = ttk.Button(button_frame, text="💾 保存报告", 
                                          command=self.save_json_report, 
                                          state="disabled")
        self.json_save_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(json_frame, text="检测结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.json_result_text = scrolledtext.ScrolledText(result_frame, 
                                                         wrap=tk.WORD, 
                                                         font=("Consolas", 9),
                                                         height=12)
        self.json_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_excel_data_processor_tab(self):
        """创建Excel数据处理工具页签"""
        # Excel数据处理工具框架
        excel_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(excel_frame, text="Excel数据处理工具")
        
        # 配置网格
        excel_frame.columnconfigure(0, weight=1)
        excel_frame.rowconfigure(2, weight=1)
        
        # 标题和描述
        header_frame = ttk.Frame(excel_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="Excel数据处理工具", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        desc_label = ttk.Label(header_frame, text="根据指定列对Excel数据进行分组处理，支持多工作表输出", 
                              style='Info.TLabel')
        desc_label.grid(row=1, column=0)
        
        # 控制面板
        control_frame = ttk.Frame(excel_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(control_frame, text="文件选择", padding="12")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.excel_input_var = tk.StringVar()
        self.excel_input_entry = ttk.Entry(file_frame, textvariable=self.excel_input_var, 
                                         font=("Microsoft YaHei", 9))
        self.excel_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.excel_input_browse_button = ttk.Button(file_frame, text="浏览文件", 
                                                    command=self.browse_excel_input_file)
        self.excel_input_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出设置
        output_frame = ttk.LabelFrame(control_frame, text="输出设置", padding="12")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        # 输出文件夹
        ttk.Label(output_frame, text="输出文件夹:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.excel_output_folder_var = tk.StringVar()
        self.excel_output_folder_entry = ttk.Entry(output_frame, textvariable=self.excel_output_folder_var, 
                                                 font=("Microsoft YaHei", 9))
        self.excel_output_folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.excel_output_browse_button = ttk.Button(output_frame, text="浏览文件夹", 
                                                     command=self.browse_excel_output_folder)
        self.excel_output_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出文件名
        ttk.Label(output_frame, text="输出文件名:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.excel_output_filename_var = tk.StringVar(value="整合结果.xlsx")
        self.excel_output_filename_entry = ttk.Entry(output_frame, textvariable=self.excel_output_filename_var, 
                                                   width=25, font=("Microsoft YaHei", 9))
        self.excel_output_filename_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(control_frame, text="处理选项", padding="12")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 分组列设置
        ttk.Label(options_frame, text="分组列:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.excel_group_column_var = tk.StringVar()
        self.excel_group_column_entry = ttk.Entry(options_frame, textvariable=self.excel_group_column_var, 
                                                width=15, font=("Microsoft YaHei", 9))
        self.excel_group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(options_frame, text="(留空使用第一列)", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W)
        
        # 工作表前缀
        ttk.Label(options_frame, text="工作表前缀:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.excel_sheet_prefix_var = tk.StringVar()
        self.excel_sheet_prefix_entry = ttk.Entry(options_frame, textvariable=self.excel_sheet_prefix_var, 
                                                width=15, font=("Microsoft YaHei", 9))
        self.excel_sheet_prefix_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        # 包含汇总信息选项
        self.excel_include_summary_var = tk.BooleanVar(value=True)
        self.excel_include_summary_check = ttk.Checkbutton(options_frame, text="包含汇总信息工作表", 
                                                          variable=self.excel_include_summary_var)
        self.excel_include_summary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # 主要操作按钮
        self.excel_process_button = ttk.Button(button_frame, text="⚙️ 开始整合", 
                                               command=self.start_excel_consolidation, 
                                               style='Accent.TButton')
        self.excel_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.excel_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                             command=self.clear_excel_results)
        self.excel_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.excel_preview_button = ttk.Button(button_frame, text="👁️ 预览数据", 
                                               command=self.preview_excel_data,
                                               state="disabled")
        self.excel_preview_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(excel_frame, text="处理结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.excel_result_text = scrolledtext.ScrolledText(result_frame, 
                                                          wrap=tk.WORD, 
                                                          font=("Consolas", 9),
                                                          height=12)
        self.excel_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_excel_text_extractor_tab(self):
        """创建Excel文本提取器页签"""
        # Excel文本提取器框架
        extractor_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(extractor_frame, text="翻译提取")
        
        # 配置网格
        extractor_frame.columnconfigure(0, weight=1)
        extractor_frame.rowconfigure(2, weight=1)
        
        # 标题和描述
        header_frame = ttk.Frame(extractor_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="翻译提取工具", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        desc_label = ttk.Label(header_frame, text="批量提取Excel文件中的文本内容，支持中文、越南文（跳过纯英文），从第7行开始检测，同时提取A列内容", 
                              style='Info.TLabel')
        desc_label.grid(row=1, column=0)
        
        # 控制面板
        control_frame = ttk.Frame(extractor_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(control_frame, text="目录选择", padding="12")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # 输入目录
        ttk.Label(dir_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.extractor_input_var = tk.StringVar()
        self.extractor_input_entry = ttk.Entry(dir_frame, textvariable=self.extractor_input_var, 
                                             font=("Microsoft YaHei", 9))
        self.extractor_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.extractor_input_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                                       command=self.browse_extractor_input_directory)
        self.extractor_input_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 输出目录
        ttk.Label(dir_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.extractor_output_var = tk.StringVar()
        self.extractor_output_entry = ttk.Entry(dir_frame, textvariable=self.extractor_output_var, 
                                              font=("Microsoft YaHei", 9))
        self.extractor_output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        self.extractor_output_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                                        command=self.browse_extractor_output_directory)
        self.extractor_output_browse_button.grid(row=1, column=2, pady=(5, 0))
        
        # 提取选项区域
        options_frame = ttk.LabelFrame(control_frame, text="提取选项", padding="12")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 递归扫描选项
        self.extractor_recursive_var = tk.BooleanVar(value=True)
        self.extractor_recursive_check = ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                                                         variable=self.extractor_recursive_var)
        self.extractor_recursive_check.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # 文本类型过滤
        ttk.Label(options_frame, text="文本类型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.extractor_text_type_var = tk.StringVar(value="全部")
        text_type_combo = ttk.Combobox(options_frame, textvariable=self.extractor_text_type_var, 
                                      values=["全部", "中文", "英文", "中英混合"], state="readonly", 
                                      width=15, font=("Microsoft YaHei", 9))
        text_type_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(options_frame, text="(选择要提取的文本类型)", style='Info.TLabel').grid(row=1, column=2, sticky=tk.W)
        
        # 操作按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # 主要操作按钮
        self.extractor_process_button = ttk.Button(button_frame, text="📄 开始提取", 
                                                   command=self.start_text_extraction, 
                                                   style='Accent.TButton')
        self.extractor_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.extractor_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                                command=self.clear_extractor_results)
        self.extractor_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.extractor_preview_button = ttk.Button(button_frame, text="👁️ 预览文件", 
                                                  command=self.preview_extractor_files,
                                                  state="disabled")
        self.extractor_preview_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(extractor_frame, text="提取结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.extractor_result_text = scrolledtext.ScrolledText(result_frame, 
                                                              wrap=tk.WORD, 
                                                              font=("Consolas", 9),
                                                              height=12)
        self.extractor_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_about_tab(self):
        """创建关于页签"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(about_frame, text="关于")
        
        # 配置网格
        about_frame.columnconfigure(0, weight=1)
        about_frame.rowconfigure(1, weight=1)
        about_frame.rowconfigure(2, weight=0)  # 底部信息不扩展
        
        # 标题区域
        title_frame = ttk.Frame(about_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        # 主标题
        title_label = ttk.Label(title_frame, text="gametools - 游戏工具集", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 版本信息
        version_label = ttk.Label(title_frame, text=format_version_string(), 
                                 style='Info.TLabel')
        version_label.grid(row=1, column=0, pady=(0, 20))
        
        # 内容区域
        content_frame = ttk.Frame(about_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        
        # 左侧：功能模块
        left_frame = ttk.LabelFrame(content_frame, text="功能模块", padding="15")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        features_text = f"""🔍 越南文检测导出
   检测Excel和CSV文件中的越南文内容并导出详细结果

📊 JSON格式检测工具  
   检测JSON文件中text字段的格式一致性

📈 Excel数据处理工具
   根据指定列对Excel数据进行分组和处理

📄 翻译提取工具
   批量提取Excel文件中的文本内容

📋 版本信息
   当前版本: v{get_version()}
   项目描述: {get_description()}"""
        
        features_label = ttk.Label(left_frame, text=features_text, 
                                  font=("Microsoft YaHei", 10), 
                                  justify=tk.LEFT)
        features_label.pack(anchor=tk.W)
        
        # 右侧：技术信息
        right_frame = ttk.LabelFrame(content_frame, text="技术信息", padding="15")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # 获取最新更新内容
        latest_changes = get_latest_changes()
        changes_text = "\n".join([f"• {change}" for change in latest_changes])
        
        tech_text = f"""🛠️ 技术栈:
• Python 3.7+
• Tkinter (GUI界面)
• pandas (数据处理)
• openpyxl (Excel文件处理)

✨ 主要特性:
• 支持多种文件格式
• 图形化界面，操作简单
• 多线程处理，界面响应流畅
• 支持exe文件打包和分发

🆕 最新更新 (v{get_version()}):
{changes_text}

⚠️ 注意事项:
• 确保文件格式正确
• 大文件处理可能需要较长时间
• 建议在检测前备份重要文件"""
        
        tech_label = ttk.Label(right_frame, text=tech_text, 
                              font=("Microsoft YaHei", 10), 
                              justify=tk.LEFT)
        tech_label.pack(anchor=tk.W)
        
        # 底部信息
        bottom_frame = ttk.Frame(about_frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # 使用方法
        usage_text = "📖 使用方法: 选择相应的功能页签 → 按照界面提示操作 → 查看检测结果"
        usage_label = ttk.Label(bottom_frame, text=usage_text, 
                               font=("Microsoft YaHei", 10), 
                               style='Info.TLabel')
        usage_label.grid(row=0, column=0, pady=(0, 10))
        
        # 版权信息
        copyright_text = "💬 技术支持: 如有问题或建议，请联系开发团队\n© 2024 gametools - 版权所有"
        copyright_label = ttk.Label(bottom_frame, text=copyright_text, 
                                   font=("Microsoft YaHei", 9), 
                                   style='Info.TLabel')
        copyright_label.grid(row=1, column=0)
    
    # 越南文处理器相关方法
    def browse_vp_scan_directory(self):
        """浏览越南文处理器扫描目录"""
        directory = filedialog.askdirectory(title="选择要扫描的目录")
        if directory:
            self.vp_scan_dir_var.set(directory)
            # 自动设置输出文件夹为扫描目录下的子文件夹
            if not self.vp_output_folder_var.get():
                output_folder = os.path.join(directory, "越南文检测结果")
                self.vp_output_folder_var.set(output_folder)
    
    def browse_vp_output_folder(self):
        """浏览越南文处理器输出文件夹"""
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.vp_output_folder_var.set(folder)
    
    def start_vietnamese_processing(self):
        """开始越南文处理"""
        scan_dir = self.vp_scan_dir_var.get().strip()
        output_folder = self.vp_output_folder_var.get().strip()
        
        if not scan_dir:
            messagebox.showerror("错误", "请选择要扫描的目录")
            return
        
        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        if not os.path.exists(scan_dir):
            messagebox.showerror("错误", "扫描目录不存在")
            return
        
        # 在新线程中执行处理
        self.vp_process_button.config(state="disabled")
        self.vp_progress_bar.start()
        self.vp_progress_var.set("正在处理...")
        self.status_var.set("正在处理越南文检测...")
        
        thread = threading.Thread(target=self._vietnamese_processing_thread, 
                                 args=(scan_dir, output_folder))
        thread.daemon = True
        thread.start()
    
    def _vietnamese_processing_thread(self, scan_dir, output_folder):
        """越南文处理线程"""
        try:
            # 清空结果
            self.root.after(0, self.clear_vp_results)
            
            # 开始处理
            self.root.after(0, lambda: self.vp_result_text.insert(tk.END, 
                f"开始扫描目录: {scan_dir}\n"))
            self.root.after(0, lambda: self.vp_result_text.insert(tk.END, 
                f"输出文件夹: {output_folder}\n"))
            self.root.after(0, lambda: self.vp_result_text.insert(tk.END, 
                f"递归扫描: {'是' if self.vp_recursive_var.get() else '否'}\n"))
            self.root.after(0, lambda: self.vp_result_text.insert(tk.END, 
                "支持的格式: .xlsx, .xls, .csv, .tsv\n"))
            self.root.after(0, lambda: self.vp_result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 执行处理
            stats = self.vietnamese_processor.process_directory(
                directory_path=scan_dir,
                output_folder=output_folder,
                recursive=self.vp_recursive_var.get(),
                create_excel=self.vp_create_excel_var.get(),
                create_report=False
            )
            
            # 显示结果
            self.root.after(0, self._show_vp_result, stats)
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, self._show_vp_error, error_msg)
        finally:
            # 恢复界面状态
            self.root.after(0, self._vp_finished)
    
    def _show_vp_result(self, stats):
        """显示越南文处理结果"""
        self.vp_result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.vp_result_text.insert(tk.END, "处理完成！\n")
        self.vp_result_text.insert(tk.END, "=" * 50 + "\n")
        self.vp_result_text.insert(tk.END, f"扫描的文件总数: {stats['total_files_scanned']}\n")
        self.vp_result_text.insert(tk.END, f"包含越南文的文件数: {stats['files_with_vietnamese']}\n")
        self.vp_result_text.insert(tk.END, f"越南文位置总数: {stats['total_vietnamese_locations']}\n")
        
        if stats['output_files']:
            self.vp_result_text.insert(tk.END, "\n✓ 输出文件创建成功！\n")
            self.vp_result_text.insert(tk.END, "生成的文件:\n")
            for output_file in stats['output_files']:
                self.vp_result_text.insert(tk.END, f"  - {output_file}\n")
        else:
            self.vp_result_text.insert(tk.END, "\n✗ 未找到越南文内容，未创建输出文件\n")
        
        # 滚动到底部
        self.vp_result_text.see(tk.END)
        
        # 显示成功消息
        if stats['output_files']:
            messagebox.showinfo("成功", f"越南文检测完成！\n找到 {stats['total_vietnamese_locations']} 个越南文位置\n已生成 {len(stats['output_files'])} 个输出文件")
        else:
            messagebox.showinfo("完成", "扫描完成，未发现越南文内容")
    
    def _show_vp_error(self, error_msg):
        """显示越南文处理错误"""
        self.vp_result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
        self.vp_result_text.insert(tk.END, f"错误: {error_msg}\n")
        self.vp_result_text.insert(tk.END, "=" * 50 + "\n")
        self.vp_result_text.see(tk.END)
        messagebox.showerror("错误", error_msg)
    
    def _vp_finished(self):
        """越南文处理完成后的界面恢复"""
        self.vp_process_button.config(state="normal")
        self.vp_progress_bar.stop()
        self.vp_progress_var.set("处理完成")
        self.status_var.set("就绪")
    
    def clear_vp_results(self):
        """清空越南文处理结果"""
        self.vp_result_text.delete(1.0, tk.END)
        self.vp_progress_var.set("就绪")
    
    def create_demo_files(self):
        """创建演示文件"""
        try:
            # 运行演示脚本
            result = subprocess.run([sys.executable, "tools/demo.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.vp_result_text.insert(tk.END, "演示文件创建成功！\n")
                self.vp_result_text.insert(tk.END, "文件位置: demo_tables/\n")
                self.vp_result_text.insert(tk.END, "现在可以使用批量扫描功能测试这些文件。\n")
                self.status_var.set("演示文件创建成功")
            else:
                self.vp_result_text.insert(tk.END, f"创建演示文件失败: {result.stderr}\n")
                self.status_var.set("演示文件创建失败")
        except Exception as e:
            self.vp_result_text.insert(tk.END, f"创建演示文件时发生错误: {str(e)}\n")
            self.status_var.set("演示文件创建失败")
    
    # JSON格式检测工具相关方法
    def browse_json_folder(self):
        """浏览JSON文件夹"""
        folder_path = filedialog.askdirectory(
            title="选择包含JSON文件的文件夹"
        )
        if folder_path:
            self.json_path_var.set(folder_path)
    
    def start_json_detection(self):
        """开始JSON错误检测"""
        path = self.json_path_var.get().strip()
        
        if not path:
            messagebox.showerror("错误", "请选择路径")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在")
            return
        
        # 在新线程中执行检测
        self.json_detect_button.config(state="disabled")
        self.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._json_detection, 
                                 args=(path,))
        thread.daemon = True
        thread.start()
    
    def _json_detection(self, path):
        """JSON错误检测（后台线程）"""
        try:
            # 自动检测：如果是文件夹则检测文件夹，如果是文件则检测单个文件
            if os.path.isdir(path):
                report = self.json_detector.detect_errors_in_folder(path)
            else:
                report = self.json_detector.detect_errors(path)
            
            self.root.after(0, self._update_json_results, report)
        except Exception as e:
            error_msg = f"检测过程中发生错误: {str(e)}"
            self.root.after(0, self._show_json_error, error_msg)
    
    def _update_json_results(self, report):
        """更新JSON错误检测结果"""
        self.json_result_text.delete(1.0, tk.END)
        self.json_result_text.insert(1.0, report)
        self.json_result_text.see(1.0)
        
        self.json_detect_button.config(state="normal")
        self.json_save_button.config(state="normal")
        self.status_var.set("检测完成")
    
    def _show_json_error(self, error_msg):
        """显示JSON错误检测错误"""
        self.json_result_text.delete(1.0, tk.END)
        self.json_result_text.insert(1.0, error_msg)
        
        self.json_detect_button.config(state="normal")
        self.status_var.set("检测失败")
        messagebox.showerror("错误", error_msg)
    
    def clear_json_results(self):
        """清空JSON检测结果"""
        self.json_result_text.delete(1.0, tk.END)
        self.json_save_button.config(state="disabled")
    
    def save_json_report(self):
        """保存JSON检测报告"""
        content = self.json_result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存检测报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"报告已保存到: {file_path}")
                self.status_var.set(f"报告已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # Excel数据处理工具相关方法
    def browse_excel_input_file(self):
        """浏览Excel输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.excel_input_var.set(file_path)
            # 自动设置输出文件名
            if not self.excel_output_var.get():
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_整合{input_path.suffix}"
                self.excel_output_var.set(str(output_path))
    
    def browse_excel_output_folder(self):
        """浏览Excel输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.excel_output_folder_var.set(folder_path)
            # 自动设置输出文件名
            if not self.excel_output_filename_var.get():
                self.excel_output_filename_var.set("整合结果.xlsx")
    
    def start_excel_consolidation(self):
        """开始Excel数据整合"""
        input_file = self.excel_input_var.get().strip()
        output_folder = self.excel_output_folder_var.get().strip()
        output_filename = self.excel_output_filename_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_folder:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        if not output_filename:
            messagebox.showerror("错误", "请输入输出文件名")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        if not os.path.exists(output_folder):
            messagebox.showerror("错误", "输出文件夹不存在")
            return
        
        # 构建完整的输出文件路径
        output_file = os.path.join(output_folder, output_filename)
        
        # 在新线程中执行整合
        self.excel_process_button.config(state="disabled")
        self.excel_preview_button.config(state="disabled")
        self.status_var.set("正在处理Excel数据...")
        
        thread = threading.Thread(target=self._excel_consolidation_process, 
                                 args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _excel_consolidation_process(self, input_file, output_file):
        """Excel数据整合处理（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_excel_results)
            
            # 显示开始信息
            self.root.after(0, lambda: self.excel_result_text.insert(tk.END, 
                f"开始处理文件: {input_file}\n"))
            self.root.after(0, lambda: self.excel_result_text.insert(tk.END, 
                f"输出文件: {output_file}\n"))
            self.root.after(0, lambda: self.excel_result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 获取选项
            group_column = self.excel_group_column_var.get().strip() or None
            include_summary = self.excel_include_summary_var.get()
            sheet_prefix = self.excel_sheet_prefix_var.get().strip()
            
            # 执行处理
            success = self.excel_processor.process_file(
                input_path=input_file,
                output_folder=os.path.dirname(output_file),
                output_filename=os.path.basename(output_file),
                group_column=group_column,
                include_summary=include_summary,
                sheet_prefix=sheet_prefix
            )
            
            # 显示结果
            if success:
                self.root.after(0, self._show_excel_success_result)
            else:
                self.root.after(0, self._show_excel_error_result, "处理失败")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, self._show_excel_error_result, error_msg)
    
    def _show_excel_success_result(self):
        """显示Excel整合成功结果"""
        report = self.excel_processor.get_process_report()
        self.excel_result_text.insert(tk.END, report)
        self.excel_result_text.insert(tk.END, "\n\n✅ Excel数据处理完成！")
        
        self.excel_process_button.config(state="normal")
        self.excel_preview_button.config(state="normal")
        self.status_var.set("Excel处理完成")
        
        messagebox.showinfo("成功", "Excel数据处理完成！")
    
    def _show_excel_error_result(self, error_msg):
        """显示Excel处理错误结果"""
        self.excel_result_text.insert(tk.END, f"❌ {error_msg}\n")
        
        self.excel_process_button.config(state="normal")
        self.excel_preview_button.config(state="normal")
        self.status_var.set("Excel处理失败")
        
        messagebox.showerror("错误", error_msg)
    
    def preview_excel_data(self):
        """预览Excel数据"""
        input_file = self.excel_input_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请先选择输入文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        try:
            # 读取文件
            df = self.excel_processor.read_excel_file(input_file)
            
            # 显示预览信息
            preview_text = f"文件预览: {os.path.basename(input_file)}\n"
            preview_text += f"总行数: {len(df)}\n"
            preview_text += f"总列数: {len(df.columns)}\n"
            preview_text += f"列名: {list(df.columns)}\n\n"
            
            # 显示前几行数据
            preview_text += "前5行数据:\n"
            preview_text += df.head().to_string()
            
            # 显示A列的唯一值
            if len(df) > 0:
                first_col = df.columns[0]
                unique_values = df[first_col].unique()
                preview_text += f"\n\n第一列 '{first_col}' 的唯一值:\n"
                for i, value in enumerate(unique_values[:10]):  # 只显示前10个
                    preview_text += f"{i+1}. {value}\n"
                if len(unique_values) > 10:
                    preview_text += f"... 还有 {len(unique_values) - 10} 个值\n"
            
            # 清空并显示预览
            self.excel_result_text.delete(1.0, tk.END)
            self.excel_result_text.insert(1.0, preview_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览数据失败: {str(e)}")
    
    def clear_excel_results(self):
        """清空Excel整合结果"""
        self.excel_result_text.delete(1.0, tk.END)
    
    # Excel文本提取器相关方法
    def browse_extractor_input_directory(self):
        """浏览文本提取器输入目录"""
        directory = filedialog.askdirectory(title="选择包含Excel文件的目录")
        if directory:
            self.extractor_input_var.set(directory)
            # 自动设置输出目录为输入目录
            if not self.extractor_output_var.get():
                self.extractor_output_var.set(directory)
    
    def browse_extractor_output_directory(self):
        """浏览文本提取器输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.extractor_output_var.set(directory)
    
    def start_text_extraction(self):
        """开始文本提取"""
        input_dir = self.extractor_input_var.get().strip()
        output_dir = self.extractor_output_var.get().strip()
        
        if not input_dir:
            messagebox.showerror("错误", "请选择输入目录")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("错误", "输入目录不存在")
            return
        
        # 设置输出目录
        if not output_dir:
            output_dir = input_dir
        
        # 在新线程中执行提取
        self.extractor_process_button.config(state="disabled")
        self.status_var.set("正在提取文本...")
        
        thread = threading.Thread(target=self._text_extraction, 
                                 args=(input_dir, output_dir))
        thread.daemon = True
        thread.start()
    
    def _text_extraction(self, input_dir, output_dir):
        """文本提取（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_extractor_results)
            
            # 开始提取
            self.root.after(0, lambda: self.extractor_result_text.insert(tk.END, 
                f"开始扫描目录: {input_dir}\n"))
            self.root.after(0, lambda: self.extractor_result_text.insert(tk.END, 
                f"输出目录: {output_dir}\n"))
            self.root.after(0, lambda: self.extractor_result_text.insert(tk.END, 
                "支持的格式: .xlsx, .xls\n"))
            self.root.after(0, lambda: self.extractor_result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 执行提取
            success = self.text_extractor.process_directory(input_dir, output_dir)
            
            # 显示结果
            if success:
                self.root.after(0, self._show_extractor_success_result)
            else:
                self.root.after(0, self._show_extractor_error_result, "提取失败")
            
        except Exception as e:
            error_msg = f"提取过程中发生错误: {str(e)}"
            self.root.after(0, self._show_extractor_error_result, error_msg)
    
    def _show_extractor_success_result(self):
        """显示文本提取成功结果"""
        report = self.text_extractor.get_processing_report()
        self.extractor_result_text.insert(tk.END, report)
        self.extractor_result_text.insert(tk.END, "\n\n✅ Excel文本提取完成！")
        
        self.extractor_process_button.config(state="normal")
        self.extractor_preview_button.config(state="normal")
        self.status_var.set("文本提取完成")
        
        messagebox.showinfo("成功", "Excel文本提取完成！")
    
    def _show_extractor_error_result(self, error_msg):
        """显示文本提取错误结果"""
        self.extractor_result_text.insert(tk.END, f"❌ {error_msg}\n")
        
        self.extractor_process_button.config(state="normal")
        self.extractor_preview_button.config(state="normal")
        self.status_var.set("文本提取失败")
        
        messagebox.showerror("错误", error_msg)
    
    def preview_extractor_files(self):
        """预览Excel文件"""
        input_dir = self.extractor_input_var.get().strip()
        
        if not input_dir:
            messagebox.showerror("错误", "请先选择输入目录")
            return
        
        if not os.path.exists(input_dir):
            messagebox.showerror("错误", "输入目录不存在")
            return
        
        try:
            # 扫描Excel文件
            excel_files = self.text_extractor.scan_directory(input_dir)
            
            # 显示预览信息
            preview_text = f"目录预览: {input_dir}\n"
            preview_text += f"找到Excel文件: {len(excel_files)} 个\n\n"
            
            if excel_files:
                preview_text += "Excel文件列表:\n"
                for i, file_path in enumerate(excel_files[:20]):  # 只显示前20个
                    preview_text += f"{i+1}. {os.path.basename(file_path)}\n"
                if len(excel_files) > 20:
                    preview_text += f"... 还有 {len(excel_files) - 20} 个文件\n"
            else:
                preview_text += "未找到Excel文件\n"
            
            # 清空并显示预览
            self.extractor_result_text.delete(1.0, tk.END)
            self.extractor_result_text.insert(1.0, preview_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览文件失败: {str(e)}")
    
    def clear_extractor_results(self):
        """清空文本提取结果"""
        self.extractor_result_text.delete(1.0, tk.END)
    


def main():
    """主函数"""
    root = tk.Tk()
    app = GameToolsUnified(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()