#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools - 统一用户界面
集成JSON格式检测和Excel处理工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
from pathlib import Path
import subprocess
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from core.cross_project_translator import CrossProjectTranslator
from core.excel_field_extractor import ExcelFieldExtractor
from core.table_range_translator import TableRangeTranslator
from core.excel_sheet_splitter import ExcelSheetSplitter
from core.batch_excel_modifier import BatchExcelModifier
from core.excel_config_sync import ExcelConfigSync
from tools.json_error_detector.json_error_detector import JSONErrorDetector
from tools.excel_data_processor import ExcelDataProcessor
from version import get_version, format_version_string, get_description, get_latest_changes


class GameToolsUnified:
    """gametools统一界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"gametools v{get_version()}")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        
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
        self.cross_project_translator = CrossProjectTranslator()
        self.json_detector = JSONErrorDetector()
        self.excel_processor = ExcelDataProcessor()
        self.field_extractor = ExcelFieldExtractor()
        self.table_range_translator = TableRangeTranslator()
        self.sheet_splitter = ExcelSheetSplitter()
        self.batch_modifier = BatchExcelModifier()
        self.config_sync = ExcelConfigSync()
        
        # 扫描状态
        self.is_scanning = False
        
        # 结果存储字典
        self.results_storage = {
            'cross_project_translator': '',
            'json_detector': '',
            'excel_processor': '',
            'field_extractor': '',
            'table_range_translator': '',
            'sheet_splitter': '',
            'batch_modifier': '',
            'config_sync': ''
        }
        
        # 字段提取结果数据
        self.field_extraction_results = None
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 11, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 9))
        style.configure('Success.TLabel', font=('Microsoft YaHei', 9), foreground='green')
        style.configure('Error.TLabel', font=('Microsoft YaHei', 9), foreground='red')
        style.configure('Accent.TButton', font=('Microsoft YaHei', 9, 'bold'))
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 创建笔记本控件（页签）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建各个功能页签
        self.create_cross_project_translator_tab()
        self.create_json_detector_tab()
        self.create_excel_data_processor_tab()
        self.create_sheet_splitter_tab()
        self.create_field_extractor_tab()
        self.create_table_range_translator_tab()
        self.create_batch_modifier_tab()
        self.create_config_sync_tab()
        self.create_about_tab()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding="3")
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
    
    def create_cross_project_translator_tab(self):
        """创建跨项目翻译对应页签"""
        translator_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(translator_frame, text="跨项目翻译")
        
        translator_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(translator_frame, text="文件选择", padding="8")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # 映射文件选择
        ttk.Label(file_frame, text="映射文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_mapping_file_var = tk.StringVar()
        self.cpt_mapping_file_entry = ttk.Entry(file_frame, textvariable=self.cpt_mapping_file_var)
        self.cpt_mapping_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_mapping_browse_button = ttk.Button(file_frame, text="浏览", command=self.browse_cpt_mapping_file)
        self.cpt_mapping_browse_button.grid(row=0, column=2, pady=2)
        
        # 项目目录选择
        ttk.Label(file_frame, text="项目目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_project_dir_var = tk.StringVar()
        self.cpt_project_dir_entry = ttk.Entry(file_frame, textvariable=self.cpt_project_dir_var)
        self.cpt_project_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_project_browse_button = ttk.Button(file_frame, text="浏览", command=self.browse_cpt_project_directory)
        self.cpt_project_browse_button.grid(row=1, column=2, pady=2)
        
        # 输出文件选择
        ttk.Label(file_frame, text="输出文件:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.cpt_output_file_var = tk.StringVar()
        self.cpt_output_file_entry = ttk.Entry(file_frame, textvariable=self.cpt_output_file_var)
        self.cpt_output_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        self.cpt_output_browse_button = ttk.Button(file_frame, text="浏览", command=self.browse_cpt_output_file)
        self.cpt_output_browse_button.grid(row=2, column=2, pady=2)
        
        # 操作按钮区域
        button_frame = ttk.Frame(translator_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        
        self.cpt_process_button = ttk.Button(button_frame, text="开始对应", command=self.start_cross_project_translation, style='Accent.TButton')
        self.cpt_process_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cpt_clear_button = ttk.Button(button_frame, text="清空", command=self.clear_cpt_results)
        self.cpt_clear_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cpt_export_button = ttk.Button(button_frame, text="导出", command=self.export_cpt_results, state="disabled")
        self.cpt_export_button.pack(side=tk.LEFT, padx=(0, 5))
        self.cpt_view_results_button = ttk.Button(button_frame, text="查看结果", command=lambda: self.show_results_dialog('cross_project_translator'))
        self.cpt_view_results_button.pack(side=tk.LEFT)
    
    
    def create_json_detector_tab(self):
        """创建JSON错误检测工具页签"""
        # JSON检测工具框架
        json_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(json_frame, text="JSON检测")
        
        # 配置网格
        json_frame.columnconfigure(0, weight=1)
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(json_frame, text="检测路径（检测JSON语法/结构/编码错误）", padding="10")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
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
        button_frame = ttk.Frame(json_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
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
        self.json_save_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        self.json_view_results_button = ttk.Button(button_frame, text="👁️ 查看结果", 
                                                  command=lambda: self.show_results_dialog('json_detector'))
        self.json_view_results_button.pack(side=tk.LEFT)
    
    def create_excel_data_processor_tab(self):
        """创建Excel数据处理工具页签"""
        # Excel数据处理工具框架
        excel_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(excel_frame, text="Excel数据处理")
        
        # 配置网格
        excel_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(excel_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
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
        output_frame = ttk.LabelFrame(excel_frame, text="输出设置", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
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
        options_frame = ttk.LabelFrame(excel_frame, text="处理选项（按列分组输出多工作表）", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
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
        button_frame = ttk.Frame(excel_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
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
        self.excel_preview_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        self.excel_view_results_button = ttk.Button(button_frame, text="📊 查看结果", 
                                                   command=lambda: self.show_results_dialog('excel_processor'))
        self.excel_view_results_button.pack(side=tk.LEFT)
    
    def create_sheet_splitter_tab(self):
        """创建Excel分页拆分工具页签"""
        # Excel分页拆分工具框架
        splitter_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(splitter_frame, text="分页拆分")
        
        # 配置网格
        splitter_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(splitter_frame, text="文件选择（按第一列拆分到对应分页）", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.splitter_input_var = tk.StringVar()
        self.splitter_input_entry = ttk.Entry(file_frame, textvariable=self.splitter_input_var, 
                                             font=("Microsoft YaHei", 9))
        self.splitter_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.splitter_input_browse_button = ttk.Button(file_frame, text="浏览文件", 
                                                       command=self.browse_splitter_input_file)
        self.splitter_input_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 工作表选择
        ttk.Label(file_frame, text="工作表:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 5))
        self.splitter_sheet_var = tk.StringVar()
        self.splitter_sheet_combo = ttk.Combobox(file_frame, textvariable=self.splitter_sheet_var, 
                                                 font=("Microsoft YaHei", 9), state="readonly")
        self.splitter_sheet_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 5))
        ttk.Label(file_frame, text="(留空读取第一个)", style='Info.TLabel').grid(row=1, column=2, sticky=tk.W, pady=(5, 5))
        
        # 输出设置
        output_frame = ttk.LabelFrame(splitter_frame, text="输出设置", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        output_frame.columnconfigure(1, weight=1)
        
        # 输出文件
        ttk.Label(output_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.splitter_output_var = tk.StringVar()
        self.splitter_output_entry = ttk.Entry(output_frame, textvariable=self.splitter_output_var, 
                                              font=("Microsoft YaHei", 9))
        self.splitter_output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        self.splitter_output_browse_button = ttk.Button(output_frame, text="保存为...", 
                                                        command=self.browse_splitter_output_file)
        self.splitter_output_browse_button.grid(row=0, column=2, pady=(0, 5))
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(splitter_frame, text="处理选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_frame.columnconfigure(1, weight=1)
        
        # 分组列设置
        ttk.Label(options_frame, text="分组列:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.splitter_group_column_var = tk.StringVar()
        self.splitter_group_column_entry = ttk.Entry(options_frame, textvariable=self.splitter_group_column_var, 
                                                     width=20, font=("Microsoft YaHei", 9))
        self.splitter_group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(options_frame, text="(留空使用第一列)", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W)
        
        # 选项复选框
        options_check_frame = ttk.Frame(options_frame)
        options_check_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 提取文件名选项
        self.splitter_extract_filename_var = tk.BooleanVar(value=True)
        self.splitter_extract_filename_check = ttk.Checkbutton(options_check_frame, 
                                                               text="从路径中提取文件名（去除路径和扩展名）", 
                                                               variable=self.splitter_extract_filename_var)
        self.splitter_extract_filename_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 包含汇总信息选项
        self.splitter_include_summary_var = tk.BooleanVar(value=True)
        self.splitter_include_summary_check = ttk.Checkbutton(options_check_frame, 
                                                              text="包含汇总工作表", 
                                                              variable=self.splitter_include_summary_var)
        self.splitter_include_summary_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 移除第一列选项
        self.splitter_remove_first_col_var = tk.BooleanVar(value=False)
        self.splitter_remove_first_col_check = ttk.Checkbutton(options_check_frame, 
                                                               text="输出时移除第一列", 
                                                               variable=self.splitter_remove_first_col_var)
        self.splitter_remove_first_col_check.pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = ttk.Frame(splitter_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 主要操作按钮
        self.splitter_process_button = ttk.Button(button_frame, text="📄 开始拆分", 
                                                  command=self.start_sheet_split, 
                                                  style='Accent.TButton')
        self.splitter_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.splitter_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                                command=self.clear_splitter_results)
        self.splitter_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 打开输出文件夹按钮
        self.splitter_open_folder_button = ttk.Button(button_frame, text="📂 打开输出文件夹", 
                                                      command=self.open_splitter_output_folder,
                                                      state="disabled")
        self.splitter_open_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        self.splitter_view_results_button = ttk.Button(button_frame, text="👁️ 查看结果", 
                                                       command=lambda: self.show_results_dialog('sheet_splitter'))
        self.splitter_view_results_button.pack(side=tk.LEFT)
    
    def create_field_extractor_tab(self):
        """创建表字段导出页签"""
        # 字段导出器框架
        field_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(field_frame, text="字段导出")
        
        # 配置网格
        field_frame.columnconfigure(0, weight=1)
        
        # 目录选择区域 - 多语言分支
        dir_frame = ttk.LabelFrame(field_frame, text="多语言目录配置（从物理行第5行提取字段名）", padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_zh_dir_var = tk.StringVar()
        self.field_zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_zh_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_zh_browse_button = ttk.Button(dir_frame, text="浏览", 
                                                command=lambda: self.browse_field_language_dir('zh'))
        self.field_zh_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        self.field_zh_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_zh_check_var).grid(row=0, column=3, padx=(5, 0), pady=(0, 8))
        
        # 越南语目录
        ttk.Label(dir_frame, text="越南语目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_vn_dir_var = tk.StringVar()
        self.field_vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_vn_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_vn_browse_button = ttk.Button(dir_frame, text="浏览", 
                                                command=lambda: self.browse_field_language_dir('vn'))
        self.field_vn_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        self.field_vn_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_vn_check_var).grid(row=1, column=3, padx=(5, 0), pady=(0, 8))
        
        # 泰语目录
        ttk.Label(dir_frame, text="泰语目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.field_th_dir_var = tk.StringVar()
        self.field_th_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_th_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.field_th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.field_th_browse_button = ttk.Button(dir_frame, text="浏览", 
                                                command=lambda: self.browse_field_language_dir('th'))
        self.field_th_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        self.field_th_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.field_th_check_var).grid(row=2, column=3, padx=(5, 0), pady=(0, 8))
        
        # 输出文件夹
        ttk.Label(dir_frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.field_output_dir_var = tk.StringVar()
        self.field_output_dir_entry = ttk.Entry(dir_frame, textvariable=self.field_output_dir_var, 
                                               font=("Microsoft YaHei", 9))
        self.field_output_dir_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.field_output_browse_button = ttk.Button(dir_frame, text="选择输出目录", 
                                                    command=self.browse_field_output_directory)
        self.field_output_browse_button.grid(row=3, column=2)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(field_frame, text="处理选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 递归扫描选项
        self.field_recursive_var = tk.BooleanVar(value=False)
        self.field_recursive_check = ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                                                    variable=self.field_recursive_var)
        self.field_recursive_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # 输出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT, padx=(0, 10))
        self.field_output_format_var = tk.StringVar(value="json")
        ttk.Radiobutton(format_frame, text="JSON格式", 
                       variable=self.field_output_format_var, 
                       value="json").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="CSV格式", 
                       variable=self.field_output_format_var, 
                       value="csv").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Excel格式", 
                       variable=self.field_output_format_var, 
                       value="excel").pack(side=tk.LEFT)
        
        # 说明信息
        info_label = ttk.Label(options_frame, 
                              text="💡 选择需要导出的语言分支，输出JSON带语言标记", 
                              style='Info.TLabel', foreground='blue')
        info_label.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(field_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.field_extract_button = ttk.Button(button_frame, text="📊 开始提取", 
                                              command=self.start_field_extraction, 
                                              style='Accent.TButton')
        self.field_extract_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.field_copy_button = ttk.Button(button_frame, text="📋 复制JSON", 
                                           command=self.copy_field_json_result)
        self.field_copy_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.field_error_log_button = ttk.Button(button_frame, text="⚠️ 错误日志", 
                                                command=self.show_field_error_logs)
        self.field_error_log_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.field_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                            command=self.clear_field_results)
        self.field_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.field_view_results_button = ttk.Button(button_frame, text="📝 查看结果", 
                                                   command=lambda: self.show_results_dialog('field_extractor'))
        self.field_view_results_button.pack(side=tk.LEFT)
    
    def create_table_range_translator_tab(self):
        """创建多语言翻译提取页签"""
        # 多语言翻译提取器框架
        trt_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(trt_frame, text="翻译提取")
        
        # 配置网格
        trt_frame.columnconfigure(0, weight=1)
        
        # JSON配置文件选择区域
        json_frame = ttk.LabelFrame(trt_frame, text="配置文件（合并的JSON，包含ZH/VN/TH语言配置）", padding="10")
        json_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        json_frame.columnconfigure(1, weight=1)
        
        # 合并JSON配置文件
        ttk.Label(json_frame, text="合并JSON:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_merged_json_var = tk.StringVar()
        self.trt_merged_json_entry = ttk.Entry(json_frame, textvariable=self.trt_merged_json_var, 
                                               font=("Microsoft YaHei", 9))
        self.trt_merged_json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_merged_json_browse_button = ttk.Button(json_frame, text="浏览", 
                                                        command=self.browse_trt_merged_json)
        self.trt_merged_json_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # JSON语言检测结果显示
        self.trt_json_lang_label = ttk.Label(json_frame, text="", foreground='blue')
        self.trt_json_lang_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(trt_frame, text="对应语言目录（根据JSON中的语言配置自动匹配）", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_zh_dir_var = tk.StringVar()
        self.trt_zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_zh_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_zh_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                              command=self.browse_trt_zh_directory)
        self.trt_zh_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # 越南文目录
        ttk.Label(dir_frame, text="越南语目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_vn_dir_var = tk.StringVar()
        self.trt_vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_vn_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_vn_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                              command=self.browse_trt_vn_directory)
        self.trt_vn_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        # 泰文目录
        ttk.Label(dir_frame, text="泰语目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.trt_th_dir_var = tk.StringVar()
        self.trt_th_dir_entry = ttk.Entry(dir_frame, textvariable=self.trt_th_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.trt_th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.trt_th_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                              command=self.browse_trt_th_directory)
        self.trt_th_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        # 输出设置
        output_frame = ttk.LabelFrame(trt_frame, text="输出设置（自动生成CSV文件名）", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.trt_output_dir_var = tk.StringVar()
        self.trt_output_dir_entry = ttk.Entry(output_frame, textvariable=self.trt_output_dir_var, 
                                              font=("Microsoft YaHei", 9))
        self.trt_output_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.trt_output_dir_browse_button = ttk.Button(output_frame, text="选择目录", 
                                                       command=self.browse_trt_output_directory)
        self.trt_output_dir_browse_button.grid(row=0, column=2)
        
        # 输出格式说明
        ttk.Label(output_frame, text="💡 输出格式: 翻译提取_YYYYMMDD_HHMMSS.csv", 
                 foreground='gray').grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 兼容旧变量
        self.trt_output_var = tk.StringVar()
        self.trt_zh_json_var = tk.StringVar()
        self.trt_vn_json_var = tk.StringVar()
        self.trt_th_json_var = tk.StringVar()
        self.trt_json_var = self.trt_merged_json_var
        
        # 操作按钮区域
        button_frame = ttk.Frame(trt_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 主要操作按钮
        self.trt_process_button = ttk.Button(button_frame, text="🚀 开始提取", 
                                            command=self.start_table_range_translation, 
                                            style='Accent.TButton')
        self.trt_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.trt_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                          command=self.clear_trt_results)
        self.trt_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        self.trt_view_results_button = ttk.Button(button_frame, text="👁️ 查看结果", 
                                                 command=lambda: self.show_results_dialog('table_range_translator'))
        self.trt_view_results_button.pack(side=tk.LEFT)
    
    def create_batch_modifier_tab(self):
        """创建批量改表页签"""
        # 批量改表框架
        batch_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(batch_frame, text="批量改表")
        
        # 配置网格
        batch_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(batch_frame, text="文件配置", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # JSON配置文件（必需 - 定义表和字段）
        ttk.Label(file_frame, text="JSON配置:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_json_var = tk.StringVar()
        self.batch_json_entry = ttk.Entry(file_frame, textvariable=self.batch_json_var, 
                                         font=("Microsoft YaHei", 9))
        self.batch_json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.batch_json_browse_button = ttk.Button(file_frame, text="浏览", 
                                                  command=self.browse_batch_json_file)
        self.batch_json_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # 映射表文件（如 p9-3t_分页.xlsx）
        ttk.Label(file_frame, text="映射表文件:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_mapping_var = tk.StringVar()
        self.batch_mapping_entry = ttk.Entry(file_frame, textvariable=self.batch_mapping_var, 
                                            font=("Microsoft YaHei", 9))
        self.batch_mapping_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.batch_mapping_browse_button = ttk.Button(file_frame, text="浏览", 
                                                     command=self.browse_batch_mapping_file)
        self.batch_mapping_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        # 目标语言选择（放在映射表同一行右侧）
        ttk.Label(file_frame, text="语言:").grid(row=1, column=3, sticky=tk.W, padx=(20, 5), pady=(0, 8))
        self.batch_language_var = tk.StringVar(value="VN")
        default_languages = ['VN', 'Support-CH', 'TH', 'EN', 'Polish-CH', 'VN.1']
        self.batch_language_combo = ttk.Combobox(file_frame, textvariable=self.batch_language_var, 
                                                 width=12, values=default_languages, state='readonly')
        self.batch_language_combo.grid(row=1, column=4, sticky=tk.W, pady=(0, 8))
        self.batch_language_combo.bind('<<ComboboxSelected>>', self._on_batch_language_changed)
        
        self.batch_refresh_lang_button = ttk.Button(file_frame, text="刷新", 
                                                   command=self.refresh_batch_languages, width=5)
        self.batch_refresh_lang_button.grid(row=1, column=5, padx=(5, 0), pady=(0, 8))
        
        # JSON语言标记显示（放在JSON配置同一行右侧）
        self.batch_json_lang_label = ttk.Label(file_frame, text="", foreground='blue')
        self.batch_json_lang_label.grid(row=0, column=3, columnspan=3, padx=(20, 0), pady=(0, 8), sticky=tk.W)
        
        # 映射表工作表选择（隐藏，保留变量兼容性）
        self.batch_sheet_var = tk.StringVar()
        
        # Excel文件目录（要修改的文件所在目录）
        ttk.Label(file_frame, text="Excel目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.batch_excel_dir_var = tk.StringVar()
        self.batch_excel_dir_entry = ttk.Entry(file_frame, textvariable=self.batch_excel_dir_var, 
                                              font=("Microsoft YaHei", 9))
        self.batch_excel_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.batch_excel_dir_browse_button = ttk.Button(file_frame, text="浏览", 
                                                       command=self.browse_batch_excel_directory)
        self.batch_excel_dir_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        # 输出报告文件
        ttk.Label(file_frame, text="报告文件:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.batch_report_var = tk.StringVar()
        self.batch_report_entry = ttk.Entry(file_frame, textvariable=self.batch_report_var, 
                                           font=("Microsoft YaHei", 9))
        self.batch_report_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.batch_report_browse_button = ttk.Button(file_frame, text="浏览", 
                                                    command=self.browse_batch_report_file)
        self.batch_report_browse_button.grid(row=3, column=2)
        
        # 隐藏的变量（保持代码兼容性）
        self.batch_auto_match_var = tk.BooleanVar(value=False)  # 默认关闭自动匹配
        self.batch_table_col_var = tk.StringVar(value="")
        self.batch_id_col_var = tk.StringVar(value="ID")
        self.batch_field_col_var = tk.StringVar(value="Classification")
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(batch_frame, text="处理选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_frame.columnconfigure(0, weight=1)
        
        # 第一行：备份选项和引擎说明
        row1_frame = ttk.Frame(options_frame)
        row1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.batch_backup_var = tk.BooleanVar(value=True)
        self.batch_backup_check = ttk.Checkbutton(row1_frame, text="修改前创建备份文件（.bak）", 
                                                 variable=self.batch_backup_var)
        self.batch_backup_check.pack(side=tk.LEFT, padx=(0, 20))
        
        engine_label = ttk.Label(row1_frame, text="使用xlwings引擎（完全保留文件结构）", 
                                foreground="green")
        engine_label.pack(side=tk.LEFT)
        
        # 第二行：定位模式说明
        row2_frame = ttk.Frame(options_frame)
        row2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        mode_label = ttk.Label(row2_frame, 
                              text="💡 定位模式：有Position列→直接定位单元格 | 无Position列→ID作为行号", 
                              foreground="blue")
        mode_label.pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = ttk.Frame(batch_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.batch_process_button = ttk.Button(button_frame, text="🚀 开始修改", 
                                              command=self.start_batch_modification, 
                                              style='Accent.TButton')
        self.batch_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.batch_preview_button = ttk.Button(button_frame, text="👁️ 预览映射表", 
                                              command=self.preview_batch_mapping)
        self.batch_preview_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.batch_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                            command=self.clear_batch_results)
        self.batch_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.batch_view_results_button = ttk.Button(button_frame, text="📝 查看结果", 
                                                   command=lambda: self.show_results_dialog('batch_modifier'))
        self.batch_view_results_button.pack(side=tk.LEFT)
    
    def create_config_sync_tab(self):
        """创建Excel配置同步页签"""
        # 配置同步框架
        sync_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(sync_frame, text="配置同步")
        
        # 配置网格
        sync_frame.columnconfigure(0, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(sync_frame, text="目录配置（同步Excel配置到其他目录）", padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 源目录
        ttk.Label(dir_frame, text="源目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.sync_source_dir_var = tk.StringVar()
        self.sync_source_dir_entry = ttk.Entry(dir_frame, textvariable=self.sync_source_dir_var, 
                                              font=("Microsoft YaHei", 9))
        self.sync_source_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.sync_source_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                                   command=self.browse_sync_source_dir)
        self.sync_source_browse_button.grid(row=0, column=2, pady=(0, 8))
        
        # 目标目录1
        ttk.Label(dir_frame, text="目标目录1:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.sync_target1_dir_var = tk.StringVar()
        self.sync_target1_dir_entry = ttk.Entry(dir_frame, textvariable=self.sync_target1_dir_var, 
                                               font=("Microsoft YaHei", 9))
        self.sync_target1_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.sync_target1_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                                    command=self.browse_sync_target1_dir)
        self.sync_target1_browse_button.grid(row=1, column=2, pady=(0, 8))
        
        # 目标目录2
        ttk.Label(dir_frame, text="目标目录2:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.sync_target2_dir_var = tk.StringVar()
        self.sync_target2_dir_entry = ttk.Entry(dir_frame, textvariable=self.sync_target2_dir_var, 
                                               font=("Microsoft YaHei", 9))
        self.sync_target2_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        self.sync_target2_browse_button = ttk.Button(dir_frame, text="浏览目录", 
                                                    command=self.browse_sync_target2_dir)
        self.sync_target2_browse_button.grid(row=2, column=2, pady=(0, 8))
        
        # JSON配置文件（可选，仅用于参考）
        ttk.Label(dir_frame, text="JSON配置:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.sync_json_var = tk.StringVar()
        self.sync_json_entry = ttk.Entry(dir_frame, textvariable=self.sync_json_var, 
                                        font=("Microsoft YaHei", 9))
        self.sync_json_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        json_btn_frame = ttk.Frame(dir_frame)
        json_btn_frame.grid(row=3, column=2, pady=(0, 8))
        self.sync_json_browse_button = ttk.Button(json_btn_frame, text="浏览JSON", 
                                                 command=self.browse_sync_json_file)
        self.sync_json_browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 提示信息
        json_hint = ttk.Label(dir_frame, text="(可选，仅用于参考，不会被修改)", 
                             foreground='gray')
        json_hint.grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        # 字段过滤配置文件（可选）
        ttk.Label(dir_frame, text="过滤配置:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.sync_filter_var = tk.StringVar()
        self.sync_filter_entry = ttk.Entry(dir_frame, textvariable=self.sync_filter_var, 
                                          font=("Microsoft YaHei", 9))
        self.sync_filter_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        filter_btn_frame = ttk.Frame(dir_frame)
        filter_btn_frame.grid(row=5, column=2, pady=(0, 8))
        self.sync_filter_browse_button = ttk.Button(filter_btn_frame, text="浏览JSON", 
                                                   command=self.browse_sync_filter_file)
        self.sync_filter_browse_button.pack(side=tk.LEFT, padx=(0, 5))
        self.sync_filter_preview_button = ttk.Button(filter_btn_frame, text="预览", 
                                                    command=self.preview_sync_filter_config)
        self.sync_filter_preview_button.pack(side=tk.LEFT)
        
        # 过滤提示信息
        filter_hint = ttk.Label(dir_frame, text="(可选，指定要跳过同步的字段)", 
                               foreground='gray')
        filter_hint.grid(row=6, column=1, sticky=tk.W, pady=(0, 5))
        
        # 报告文件
        ttk.Label(dir_frame, text="报告文件:").grid(row=7, column=0, sticky=tk.W, padx=(0, 10))
        self.sync_report_var = tk.StringVar()
        self.sync_report_entry = ttk.Entry(dir_frame, textvariable=self.sync_report_var, 
                                          font=("Microsoft YaHei", 9))
        self.sync_report_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.sync_report_browse_button = ttk.Button(dir_frame, text="选择位置", 
                                                   command=self.browse_sync_report_file)
        self.sync_report_browse_button.grid(row=7, column=2)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(sync_frame, text="同步选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 备份选项
        self.sync_backup_var = tk.BooleanVar(value=True)
        self.sync_backup_check = ttk.Checkbutton(options_frame, text="同步前备份", 
                                                variable=self.sync_backup_var)
        self.sync_backup_check.grid(row=0, column=0, sticky=tk.W)
        
        # 同步值选项
        self.sync_values_var = tk.BooleanVar(value=True)
        self.sync_values_check = ttk.Checkbutton(options_frame, text="同步单元格值", 
                                                variable=self.sync_values_var)
        self.sync_values_check.grid(row=0, column=1, sticky=tk.W, padx=(15, 0))
        
        # 同步公式选项
        self.sync_formulas_var = tk.BooleanVar(value=True)
        self.sync_formulas_check = ttk.Checkbutton(options_frame, text="同步公式", 
                                                  variable=self.sync_formulas_var)
        self.sync_formulas_check.grid(row=0, column=2, sticky=tk.W, padx=(15, 0))
        
        # 同步样式选项
        self.sync_styles_var = tk.BooleanVar(value=False)
        self.sync_styles_check = ttk.Checkbutton(options_frame, text="同步样式", 
                                                variable=self.sync_styles_var)
        self.sync_styles_check.grid(row=0, column=3, sticky=tk.W, padx=(15, 0))
        
        # 同步列宽选项
        self.sync_column_widths_var = tk.BooleanVar(value=False)
        self.sync_column_widths_check = ttk.Checkbutton(options_frame, text="同步列宽", 
                                                       variable=self.sync_column_widths_var)
        self.sync_column_widths_check.grid(row=0, column=4, sticky=tk.W, padx=(15, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(sync_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.sync_process_button = ttk.Button(button_frame, text="🚀 开始同步", 
                                             command=self.start_config_sync, 
                                             style='Accent.TButton')
        self.sync_process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.sync_preview_button = ttk.Button(button_frame, text="👁️ 预览匹配", 
                                             command=self.preview_sync_matching)
        self.sync_preview_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.sync_clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", 
                                           command=self.clear_sync_results)
        self.sync_clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.sync_view_results_button = ttk.Button(button_frame, text="📝 查看结果", 
                                                  command=lambda: self.show_results_dialog('config_sync'))
        self.sync_view_results_button.pack(side=tk.LEFT)
    
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
        
        # 内容区域（改为左右两栏可滚动文本，提升可读性与自适应）
        content_frame = ttk.Frame(about_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1, minsize=360)
        content_frame.columnconfigure(1, weight=1, minsize=360)
        content_frame.rowconfigure(0, weight=1)

        # 左侧：功能模块（使用 Text + Scrollbar 以便内容较多时可滚动）
        left_frame = ttk.LabelFrame(content_frame, text="功能模块", padding=12)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        left_frame.columnconfigure(0, weight=1)

        features_text = (
            "📊 JSON格式检测工具\n"
            "  检测JSON文件中text字段的格式一致性\n\n"
            "📈 Excel数据处理工具\n"
            "  根据指定列对Excel数据进行分组和处理\n\n"
            "📄 Excel分页拆分工具\n"
            "  根据第一列文件名将数据拆分到新表格的对应分页\n\n"
            "📋 表字段导出工具\n"
            "  扫描Excel文件，提取包含文本的列的字段信息\n\n"
            "🌐 多语言翻译提取工具\n"
            "  根据字段导出的JSON配置，智能提取多语言翻译内容\n\n"
            "🔄 Excel配置同步工具\n"
            "  将源目录的Excel配置同步到其他目录的同名文件\n\n"
            f"📋 版本信息\n  当前版本: v{get_version()}\n  项目描述: {get_description()}"
        )

        features_textbox = tk.Text(left_frame, wrap='word', height=15, padx=6, pady=6,
                                   font=("Microsoft YaHei", 10), relief='flat',
                                   background='SystemButtonFace')
        features_textbox.insert('1.0', features_text)
        features_textbox.configure(state='disabled')
        features_textbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        left_scroll = ttk.Scrollbar(left_frame, orient='vertical', command=features_textbox.yview)
        features_textbox['yscrollcommand'] = left_scroll.set
        left_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 右侧：技术信息（同样使用 Text + Scrollbar）
        right_frame = ttk.LabelFrame(content_frame, text="技术信息", padding=12)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        right_frame.columnconfigure(0, weight=1)

        latest_changes = get_latest_changes()
        changes_text = "\n".join([f"• {change}" for change in latest_changes])

        tech_text = (
            "🛠️ 技术栈:\n"
            "• Python 3.7+\n"
            "• Tkinter (GUI界面)\n"
            "• pandas (数据处理)\n"
            "• xlwings (Excel修改引擎，需要安装Excel)\n\n"
            "✨ 主要特性:\n"
            "• 支持多种文件格式\n"
            "• 图形化界面，操作简单\n"
            "• 多线程处理，界面响应流畅\n"
            "• 支持exe文件打包和分发\n\n"
            f"🆕 最新更新 (v{get_version()}):\n{changes_text}\n\n"
            "⚠️ 注意事项:\n"
            "• 确保文件格式正确\n"
            "• 大文件处理可能需要较长时间\n"
            "• 建议在检测前备份重要文件"
        )

        tech_textbox = tk.Text(right_frame, wrap='word', height=15, padx=6, pady=6,
                               font=("Microsoft YaHei", 10), relief='flat',
                               background='SystemButtonFace')
        tech_textbox.insert('1.0', tech_text)
        tech_textbox.configure(state='disabled')
        tech_textbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        right_scroll = ttk.Scrollbar(right_frame, orient='vertical', command=tech_textbox.yview)
        tech_textbox['yscrollcommand'] = right_scroll.set
        right_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
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
    
    # 结果存储辅助函数
    def append_result(self, result_type, text):
        """追加文本到结果存储（所有结果只在查看结果弹窗中显示）"""
        self.results_storage[result_type] += text
    
    def clear_result(self, result_type):
        """清空结果存储"""
        self.results_storage[result_type] = ''
    
    def get_result(self, result_type):
        """获取结果存储内容"""
        return self.results_storage.get(result_type, '')
    
    # 统一的结果查看对话框
    def show_results_dialog(self, result_type):
        """显示结果查看对话框（二级菜单）"""
        # 获取对应的结果内容
        result_content = self.results_storage.get(result_type, '')
        
        if not result_content.strip():
            messagebox.showinfo("提示", "暂无处理结果")
            return
        
        # 创建对话框窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("查看处理结果")
        dialog.geometry("900x700")
        dialog.minsize(700, 500)
        
        # 结果标题映射
        title_map = {
            'cross_project_translator': '跨项目翻译对应结果',
            'json_detector': 'JSON错误检测结果',
            'excel_processor': 'Excel数据处理结果',
            'field_extractor': '表字段导出结果',
            'table_range_translator': '多语言翻译提取结果',
            'batch_modifier': '批量改表结果',
            'config_sync': 'Excel配置同步结果'
        }
        
        # 标题
        title_frame = ttk.Frame(dialog, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, 
                               text=title_map.get(result_type, '处理结果'),
                               style='Heading.TLabel')
        title_label.pack()
        
        # 结果显示区域
        result_frame = ttk.Frame(dialog, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        result_text = scrolledtext.ScrolledText(result_frame, 
                                               wrap=tk.WORD, 
                                               font=("Consolas", 9))
        result_text.pack(fill=tk.BOTH, expand=True)
        result_text.insert(tk.END, result_content)
        result_text.config(state='disabled')  # 只读
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        # 复制按钮
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(result_content)
            messagebox.showinfo("成功", "结果已复制到剪贴板")
        
        copy_button = ttk.Button(button_frame, text="📋 复制到剪贴板", 
                                command=copy_to_clipboard)
        copy_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 保存按钮
        def save_to_file():
            file_path = filedialog.asksaveasfilename(
                title="保存结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_content)
                    messagebox.showinfo("成功", f"结果已保存到: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        save_button = ttk.Button(button_frame, text="💾 保存到文件", 
                                command=save_to_file)
        save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭", 
                                 command=dialog.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # 设置对话框为模态
        dialog.transient(self.root)
        dialog.grab_set()
    
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
        self.clear_result('json_detector')
        self.append_result('json_detector', report)
        
        self.json_detect_button.config(state="normal")
        self.json_save_button.config(state="normal")
        self.status_var.set("检测完成")
        messagebox.showinfo("完成", "JSON检测完成！请点击查看结果按钮查看详细报告")
    
    def _show_json_error(self, error_msg):
        """显示JSON错误检测错误"""
        self.clear_result('json_detector')
        self.append_result('json_detector', error_msg)
        
        self.json_detect_button.config(state="normal")
        self.status_var.set("检测失败")
        messagebox.showerror("错误", error_msg)
    
    def clear_json_results(self):
        """清空JSON检测结果"""
        self.clear_result('json_detector')
        self.json_save_button.config(state="disabled")
    
    def save_json_report(self):
        """保存JSON检测报告"""
        content = self.get_result('json_detector').strip()
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
            self.root.after(0, lambda: self.append_result('excel_processor', 
                f"开始处理文件: {input_file}\n"))
            self.root.after(0, lambda: self.append_result('excel_processor', 
                f"输出文件: {output_file}\n"))
            self.root.after(0, lambda: self.append_result('excel_processor', 
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
        self.append_result('excel_processor', report)
        self.append_result('excel_processor', "\n\n✅ Excel数据处理完成！")
        
        self.excel_process_button.config(state="normal")
        self.excel_preview_button.config(state="normal")
        self.status_var.set("Excel处理完成")
        
        messagebox.showinfo("成功", "Excel数据处理完成！请点击查看结果按钮查看详细报告")
    
    def _show_excel_error_result(self, error_msg):
        """显示Excel处理错误结果"""
        self.append_result('excel_processor', f"❌ {error_msg}\n")
        
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
            self.clear_result('excel_processor')
            self.append_result('excel_processor', preview_text)
            messagebox.showinfo("预览", "预览数据加载完成！请点击查看结果按钮查看")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览数据失败: {str(e)}")
    
    def clear_excel_results(self):
        """清空Excel整合结果"""
        self.clear_result('excel_processor')
    
    # ==================== Excel分页拆分相关方法 ====================
    
    def browse_splitter_input_file(self):
        """浏览分页拆分输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.splitter_input_var.set(file_path)
            # 自动设置输出文件名
            if not self.splitter_output_var.get():
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_分页拆分.xlsx"
                self.splitter_output_var.set(str(output_path))
            # 加载工作表列表
            self._load_splitter_sheet_names(file_path)
    
    def _load_splitter_sheet_names(self, file_path):
        """加载Excel文件的工作表名称列表"""
        try:
            sheet_names = self.sheet_splitter.get_sheet_names(file_path)
            self.splitter_sheet_combo['values'] = sheet_names
            if sheet_names:
                self.splitter_sheet_combo.set(sheet_names[0])
        except Exception as e:
            self.splitter_sheet_combo['values'] = []
            self.splitter_sheet_combo.set('')
    
    def browse_splitter_output_file(self):
        """浏览分页拆分输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存拆分后的Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.splitter_output_var.set(file_path)
    
    def start_sheet_split(self):
        """开始Excel分页拆分"""
        input_file = self.splitter_input_var.get().strip()
        output_file = self.splitter_output_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请设置输出文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        # 在新线程中执行拆分
        self.splitter_process_button.config(state="disabled")
        self.splitter_open_folder_button.config(state="disabled")
        self.status_var.set("正在拆分Excel数据...")
        
        thread = threading.Thread(target=self._sheet_split_process, 
                                 args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _sheet_split_process(self, input_file, output_file):
        """Excel分页拆分处理（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_splitter_results)
            
            # 显示开始信息
            self.root.after(0, lambda: self.append_result('sheet_splitter', 
                f"开始处理文件: {input_file}\n"))
            self.root.after(0, lambda: self.append_result('sheet_splitter', 
                f"输出文件: {output_file}\n"))
            self.root.after(0, lambda: self.append_result('sheet_splitter', 
                "-" * 50 + "\n"))
            
            # 获取选项
            sheet_name = self.splitter_sheet_var.get().strip() or None
            group_column = self.splitter_group_column_var.get().strip() or None
            extract_filename = self.splitter_extract_filename_var.get()
            include_summary = self.splitter_include_summary_var.get()
            remove_first_column = self.splitter_remove_first_col_var.get()
            
            # 执行处理
            success, report = self.sheet_splitter.process_file(
                input_path=input_file,
                output_path=output_file,
                sheet_name=sheet_name,
                group_column=group_column,
                extract_filename=extract_filename,
                include_summary=include_summary,
                remove_first_column=remove_first_column
            )
            
            # 显示结果
            if success:
                self.root.after(0, lambda: self._show_splitter_success_result(report, output_file))
            else:
                self.root.after(0, lambda: self._show_splitter_error_result(report))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self._show_splitter_error_result(error_msg))
    
    def _show_splitter_success_result(self, report, output_file):
        """显示分页拆分成功结果"""
        self.append_result('sheet_splitter', report)
        self.append_result('sheet_splitter', "\n\n✅ Excel分页拆分完成！")
        self.append_result('sheet_splitter', f"\n输出文件: {output_file}")
        
        self.splitter_process_button.config(state="normal")
        self.splitter_open_folder_button.config(state="normal")
        self.status_var.set("Excel分页拆分完成")
        
        # 保存输出文件路径用于打开文件夹
        self._splitter_output_file = output_file
        
        messagebox.showinfo("成功", f"Excel分页拆分完成！\n\n输出文件: {output_file}")
    
    def _show_splitter_error_result(self, error_msg):
        """显示分页拆分错误结果"""
        self.append_result('sheet_splitter', f"❌ {error_msg}\n")
        
        self.splitter_process_button.config(state="normal")
        self.status_var.set("Excel分页拆分失败")
        
        messagebox.showerror("错误", error_msg)
    
    def clear_splitter_results(self):
        """清空分页拆分结果"""
        self.clear_result('sheet_splitter')
    
    def open_splitter_output_folder(self):
        """打开输出文件所在的文件夹"""
        try:
            output_file = getattr(self, '_splitter_output_file', None)
            if output_file and os.path.exists(output_file):
                folder_path = os.path.dirname(output_file)
                if sys.platform == 'win32':
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            else:
                messagebox.showwarning("提示", "输出文件不存在，请先执行拆分操作")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
    # ==================== 跨项目翻译对应相关方法 ====================
    
    def browse_cpt_mapping_file(self):
        """浏览映射文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.cpt_mapping_file_var.set(file_path)
            # 自动设置输出文件名
            if not self.cpt_output_file_var.get():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(os.path.dirname(file_path), f"{base_name}_翻译对应结果.xlsx")
                self.cpt_output_file_var.set(output_path)
    
    def browse_cpt_project_directory(self):
        """浏览项目目录"""
        dir_path = filedialog.askdirectory(title="选择项目目录")
        if dir_path:
            self.cpt_project_dir_var.set(dir_path)
    
    def browse_cpt_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.cpt_output_file_var.set(file_path)
    
    def start_cross_project_translation(self):
        """开始跨项目翻译对应"""
        mapping_file = self.cpt_mapping_file_var.get().strip()
        project_dir = self.cpt_project_dir_var.get().strip()
        output_file = self.cpt_output_file_var.get().strip()
        
        # 验证输入
        if not mapping_file:
            messagebox.showerror("错误", "请选择映射文件")
            return
        
        if not project_dir:
            messagebox.showerror("错误", "请选择项目目录")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请设置输出文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射文件不存在")
            return
        
        if not os.path.exists(project_dir):
            messagebox.showerror("错误", "项目目录不存在")
            return
        
        # 在新线程中执行翻译对应
        self.cpt_process_button.config(state="disabled")
        self.status_var.set("正在处理翻译对应...")
        
        thread = threading.Thread(target=self._cross_project_translation, 
                                 args=(mapping_file, project_dir, output_file))
        thread.daemon = True
        thread.start()
    
    def _cross_project_translation(self, mapping_file, project_dir, output_file):
        """跨项目翻译对应（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_cpt_results)
            
            # 开始处理
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"开始处理翻译对应...\n"))
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"映射文件: {mapping_file}\n"))
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"项目目录: {project_dir}\n"))
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"输出文件: {output_file}\n"))
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"{'='*60}\n"))
            
            # 处理翻译映射
            results = self.cross_project_translator.process_translation_mapping(
                mapping_file, project_dir)
            
            if results:
                # 显示处理报告
                report = self.cross_project_translator.get_processing_report()
                self.root.after(0, lambda: self.append_result('cross_project_translator', 
                    f"{report}\n"))
                
                # 导出结果
                if self.cross_project_translator.export_results(output_file):
                    self.root.after(0, lambda: self.append_result('cross_project_translator', 
                        f"结果已导出到: {output_file}\n"))
                    # 启用导出按钮
                    self.root.after(0, lambda: self.cpt_export_button.config(state="normal"))
                else:
                    self.root.after(0, lambda: self.append_result('cross_project_translator', 
                        f"导出失败！\n"))
                
                # 显示详细结果（前20条）
                self.root.after(0, lambda: self.append_result('cross_project_translator', 
                    f"\n详细结果（前20条）:\n"))
                self.root.after(0, lambda: self.append_result('cross_project_translator', 
                    f"{'='*60}\n"))
                
                for i, result in enumerate(results[:20]):
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    self.root.after(0, lambda r=result, icon=status_icon: 
                        self.append_result('cross_project_translator', 
                            f"{icon} 第{r['index']}行: {r['file_name']} -> {r['content'][:50]}...\n"))
                
                if len(results) > 20:
                    self.root.after(0, lambda: self.append_result('cross_project_translator', 
                        f"... 还有 {len(results) - 20} 条结果，请查看导出的Excel文件\n"))
                
            else:
                self.root.after(0, lambda: self.append_result('cross_project_translator', 
                    f"处理失败，没有生成结果\n"))
            
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"\n处理完成！\n"))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self.append_result('cross_project_translator', 
                f"❌ {error_msg}\n"))
        
        # 恢复按钮状态
        self.root.after(0, lambda: self.cpt_process_button.config(state="normal"))
        self.root.after(0, lambda: self.status_var.set("翻译对应完成"))
        self.root.after(0, lambda: messagebox.showinfo("完成", "翻译对应完成！请点击查看结果按钮查看详细报告"))
    
    def clear_cpt_results(self):
        """清空跨项目翻译对应结果"""
        self.clear_result('cross_project_translator')
        self.cpt_export_button.config(state="disabled")
    
    def export_cpt_results(self):
        """导出跨项目翻译对应结果"""
        if not self.cross_project_translator.translation_results:
            messagebox.showwarning("警告", "没有结果可导出")
            return
        
        # 选择导出文件
        file_path = filedialog.asksaveasfilename(
            title="导出翻译对应结果",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.cross_project_translator.export_results(file_path):
                messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
    
    # ==================== 表字段导出相关方法 ====================
    
    def browse_field_language_dir(self, lang_code):
        """浏览特定语言的目录"""
        lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
        dir_path = filedialog.askdirectory(title=f"选择{lang_names.get(lang_code, '')}目录")
        if dir_path:
            if lang_code == 'zh':
                self.field_zh_dir_var.set(dir_path)
            elif lang_code == 'vn':
                self.field_vn_dir_var.set(dir_path)
            elif lang_code == 'th':
                self.field_th_dir_var.set(dir_path)
            # 如果输出目录为空，自动设置为该目录的父目录
            if not self.field_output_dir_var.get():
                self.field_output_dir_var.set(dir_path)
    
    def browse_field_scan_directory(self):
        """浏览字段提取扫描目录（兼容旧方法）"""
        dir_path = filedialog.askdirectory(title="选择扫描目录")
        if dir_path:
            # 默认设置为中文目录
            self.field_zh_dir_var.set(dir_path)
            if not self.field_output_dir_var.get():
                self.field_output_dir_var.set(dir_path)
    
    def browse_field_output_directory(self):
        """浏览字段提取输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.field_output_dir_var.set(dir_path)
    
    def start_field_extraction(self):
        """开始字段提取"""
        # 收集选中的语言目录
        directories = {}
        if self.field_zh_check_var.get() and self.field_zh_dir_var.get().strip():
            directories['zh'] = self.field_zh_dir_var.get().strip()
        if self.field_vn_check_var.get() and self.field_vn_dir_var.get().strip():
            directories['vn'] = self.field_vn_dir_var.get().strip()
        if self.field_th_check_var.get() and self.field_th_dir_var.get().strip():
            directories['th'] = self.field_th_dir_var.get().strip()
        
        output_dir = self.field_output_dir_var.get().strip()
        
        # 验证输入
        if not directories:
            messagebox.showerror("错误", "请至少选择一个语言目录并勾选导出")
            return
        
        # 验证目录存在性
        for lang, dir_path in directories.items():
            if not os.path.exists(dir_path):
                lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
                messagebox.showerror("错误", f"{lang_names[lang]}目录不存在: {dir_path}")
                return
        
        if not output_dir:
            # 使用第一个有效目录作为输出目录
            output_dir = list(directories.values())[0]
            self.field_output_dir_var.set(output_dir)
        
        # 在新线程中执行提取
        self.field_extract_button.config(state="disabled")
        self.status_var.set("正在提取表字段...")
        
        thread = threading.Thread(target=self._field_extraction_thread, 
                                 args=(directories, output_dir))
        thread.daemon = True
        thread.start()
    
    def _field_extraction_thread(self, directories, output_dir):
        """字段提取线程 - 支持多语言"""
        try:
            # 清空结果存储
            self.root.after(0, lambda: self.clear_result('field_extractor'))
            self.root.after(0, lambda: self.append_result('field_extractor', "=" * 60 + "\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "开始提取多语言表字段信息...\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "=" * 60 + "\n"))
            
            lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
            for lang, dir_path in directories.items():
                self.root.after(0, lambda l=lang, d=dir_path: self.append_result(
                    'field_extractor', f"{lang_names[l]}目录: {d}\n"))
            
            self.root.after(0, lambda: self.append_result('field_extractor', f"输出目录: {output_dir}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', f"输出格式: {self.field_output_format_var.get().upper()}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', f"递归扫描: {'是' if self.field_recursive_var.get() else '否'}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "\n"))
            
            # 执行多语言提取
            all_stats = self.field_extractor.process_multi_language_directories(
                directories=directories,
                output_folder=output_dir,
                output_format=self.field_output_format_var.get(),
                recursive=self.field_recursive_var.get()
            )
            
            # 保存输出文件路径
            self.results_storage['field_extractor'] = ', '.join(all_stats.get('output_files', []))
            
            # 收集所有结果
            all_results = []
            for lang_code, lang_data in all_stats['languages'].items():
                if 'stats' in lang_data and 'results' in lang_data['stats']:
                    all_results.extend(lang_data['stats']['results'])
            self.field_extraction_results = all_results
            
            # 显示统计信息
            self.root.after(0, lambda: self.append_result('field_extractor', "\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "=" * 60 + "\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "多语言提取完成!\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', "=" * 60 + "\n"))
            
            # 分语言显示统计
            for lang_code, lang_data in all_stats['languages'].items():
                stats = lang_data.get('stats', {})
                self.root.after(0, lambda n=lang_data['name'], s=stats: self.append_result(
                    'field_extractor', 
                    f"\n【{n}】文件数: {s.get('total_files', 0)}, "
                    f"工作表: {s.get('total_sheets', 0)}, "
                    f"字段数: {s.get('total_fields', 0)}\n"
                ))
            
            self.root.after(0, lambda: self.append_result('field_extractor', f"\n总文件数: {all_stats['total_files']}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', f"总工作表数: {all_stats['total_sheets']}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', f"总字段数: {all_stats['total_fields']}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', f"\n输出文件:\n"))
            for f in all_stats.get('output_files', []):
                self.root.after(0, lambda file=f: self.append_result('field_extractor', f"  - {file}\n"))
            
            # 显示完成消息
            self.root.after(0, lambda: self.status_var.set("字段提取完成"))
            
            output_files_str = '\n'.join(all_stats.get('output_files', []))
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"多语言字段提取完成!\n\n"
                f"处理语言数: {len(all_stats['languages'])}\n"
                f"总文件数: {all_stats['total_files']}\n"
                f"总工作表数: {all_stats['total_sheets']}\n"
                f"总字段数: {all_stats['total_fields']}\n\n"
                f"输出文件:\n{output_files_str}"
            ))
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            self.root.after(0, lambda: self.append_result('field_extractor', f"\n错误: {str(e)}\n"))
            self.root.after(0, lambda: self.append_result('field_extractor', error_msg + "\n"))
            self.root.after(0, lambda: self.status_var.set("字段提取失败"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.field_extract_button.config(state="normal"))
    
    def _log_field_result(self, message):
        """记录字段提取结果"""
        self.append_result('field_extractor', message + "\n")
    
    def clear_field_results(self):
        """清空字段提取结果"""
        self.clear_result('field_extractor')
        self.field_extraction_results = None
        # 清除提取器的日志
        self.field_extractor.clear_logs()
    
    def show_field_error_logs(self):
        """显示字段提取的错误和警告日志"""
        logs = self.field_extractor.get_all_logs()
        errors = logs['errors']
        warnings = logs['warnings']
        
        if not errors and not warnings:
            messagebox.showinfo("日志信息", "没有错误或警告日志")
            return
        
        # 创建新窗口显示日志
        log_window = tk.Toplevel(self.root)
        log_window.title("字段提取 - 错误与警告日志")
        log_window.geometry("900x600")
        
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(log_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 错误日志标签页
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text=f"错误日志 ({len(errors)})")
        
        error_text = scrolledtext.ScrolledText(error_frame, 
                                               wrap=tk.WORD,
                                               font=('Consolas', 9))
        error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if errors:
            for i, error in enumerate(errors, 1):
                error_text.insert(tk.END, f"{i}. {error}\n\n")
        else:
            error_text.insert(tk.END, "无错误日志")
        
        error_text.config(state='disabled')
        
        # 警告日志标签页
        warning_frame = ttk.Frame(notebook)
        notebook.add(warning_frame, text=f"警告日志 ({len(warnings)})")
        
        warning_text = scrolledtext.ScrolledText(warning_frame,
                                                 wrap=tk.WORD,
                                                 font=('Consolas', 9))
        warning_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if warnings:
            for i, warning in enumerate(warnings, 1):
                warning_text.insert(tk.END, f"{i}. {warning}\n\n")
        else:
            warning_text.insert(tk.END, "无警告日志")
        
        warning_text.config(state='disabled')
        
        # 底部按钮
        button_frame = ttk.Frame(log_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 保存日志按钮
        def save_logs():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="保存日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                if self.field_extractor.save_logs_to_file(Path(file_path)):
                    messagebox.showinfo("成功", f"日志已保存到:\n{file_path}")
        
        ttk.Button(button_frame, text="保存日志", command=save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=log_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 统计信息
        stats_label = ttk.Label(button_frame, 
                               text=f"总计: {len(errors)} 个错误, {len(warnings)} 个警告",
                               foreground='#7f8c8d')
        stats_label.pack(side=tk.LEFT, padx=20)
    
    def copy_field_json_result(self):
        """复制字段提取的JSON结果到剪贴板"""
        if not self.field_extraction_results:
            messagebox.showwarning("警告", "没有可复制的结果，请先执行字段提取")
            return
        
        try:
            import json
            # 构建JSON数据
            json_data = [{
                "table_name": r['excel_file'],
                "sheet_name": r['sheet_name'],
                "fields_with_examples": r.get('fields_with_examples', []),
                "field_count": r['field_count']
            } for r in self.field_extraction_results]
            
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(json_str)
            self.root.update()
            
            messagebox.showinfo("成功", f"JSON结果已复制到剪贴板\n共 {len(json_data)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败:\n{str(e)}")
    
    # ==================== 多语言翻译提取相关方法 ====================
    
    def browse_trt_merged_json(self):
        """浏览合并的JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择合并的JSON配置文件（包含ZH/VN/TH）",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_merged_json_var.set(file_path)
            # 检测JSON中的语言配置
            self._detect_merged_json_languages(file_path)
    
    def _detect_merged_json_languages(self, json_path):
        """检测合并JSON中包含的语言配置"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            detected_langs = []
            lang_names = {'ZH': '中文', 'VN': '越南语', 'TH': '泰语'}
            
            for lang_key in ['ZH', 'VN', 'TH']:
                if lang_key in config:
                    text_count = len(config[lang_key].get('text_tables', []))
                    detected_langs.append(f"{lang_names.get(lang_key, lang_key)}({text_count}表)")
            
            if detected_langs:
                self.trt_json_lang_label.config(text=f"✓ 检测到: {', '.join(detected_langs)}")
            else:
                self.trt_json_lang_label.config(text="⚠️ 未检测到有效语言配置（ZH/VN/TH）")
        except Exception as e:
            self.trt_json_lang_label.config(text=f"⚠️ 读取失败: {str(e)[:50]}")
    
    def browse_trt_lang_json(self, lang_code):
        """浏览特定语言的JSON配置文件（兼容旧方法）"""
        lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
        file_path = filedialog.askopenfilename(
            title=f"选择{lang_names.get(lang_code, '')}JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            if lang_code == 'zh':
                self.trt_zh_json_var.set(file_path)
            elif lang_code == 'vn':
                self.trt_vn_json_var.set(file_path)
            elif lang_code == 'th':
                self.trt_th_json_var.set(file_path)
    
    def browse_trt_json_file(self):
        """浏览JSON配置文件（兼容旧方法）"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_json_var.set(file_path)
    
    def browse_trt_vn_directory(self):
        """浏览越南文文件目录"""
        dir_path = filedialog.askdirectory(title="选择越南文Excel文件目录")
        if dir_path:
            self.trt_vn_dir_var.set(dir_path)
    
    def browse_trt_zh_directory(self):
        """浏览中文文件目录"""
        dir_path = filedialog.askdirectory(title="选择中文Excel文件目录（_zh后缀）")
        if dir_path:
            self.trt_zh_dir_var.set(dir_path)
    
    def browse_trt_th_directory(self):
        """浏览泰文文件目录"""
        dir_path = filedialog.askdirectory(title="选择泰文Excel文件目录（_th后缀）")
        if dir_path:
            self.trt_th_dir_var.set(dir_path)
    
    def browse_trt_output_directory(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择CSV输出目录")
        if dir_path:
            self.trt_output_dir_var.set(dir_path)
    
    def browse_trt_output_file(self):
        """浏览输出文件位置（兼容旧方法）"""
        file_path = filedialog.asksaveasfilename(
            title="保存翻译总表",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.trt_output_var.set(file_path)
    
    def start_table_range_translation(self):
        """开始多语言翻译提取"""
        # 获取合并的JSON配置文件
        merged_json = self.trt_merged_json_var.get().strip()
        
        # 收集语言目录
        zh_dir = self.trt_zh_dir_var.get().strip()
        vn_dir = self.trt_vn_dir_var.get().strip()
        th_dir = self.trt_th_dir_var.get().strip()
        output_dir = self.trt_output_dir_var.get().strip()
        
        # 验证输入
        if not merged_json:
            messagebox.showerror("错误", "请选择合并的JSON配置文件")
            return
        
        if not os.path.exists(merged_json):
            messagebox.showerror("错误", "JSON配置文件不存在")
            return
        
        # 构建语言目录字典
        lang_dirs = {}
        if zh_dir:
            lang_dirs['zh'] = zh_dir
        if vn_dir:
            lang_dirs['vn'] = vn_dir
        if th_dir:
            lang_dirs['th'] = th_dir
        
        if not lang_dirs:
            messagebox.showerror("错误", "请至少选择一个语言目录")
            return
        
        # 如果未指定输出目录，使用第一个语言目录
        if not output_dir:
            output_dir = list(lang_dirs.values())[0]
            self.trt_output_dir_var.set(output_dir)
        
        # 验证目录存在性
        for lang, dir_path in lang_dirs.items():
            if not os.path.exists(dir_path):
                lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
                messagebox.showerror("错误", f"{lang_names[lang]}目录不存在")
                return
        
        # 自动生成输出文件名
        output_file = self.table_range_translator.generate_output_filename(output_dir)
        
        # 在新线程中执行提取
        self.trt_process_button.config(state="disabled")
        self.status_var.set("正在提取翻译内容...")
        
        thread = threading.Thread(target=self._table_range_translation_thread, 
                                 args=(merged_json, lang_dirs, output_file))
        thread.daemon = True
        thread.start()
    
    def _table_range_translation_thread(self, merged_json, lang_dirs, output_file):
        """多语言翻译提取线程 - 使用合并的JSON配置"""
        try:
            # 清空结果
            self.root.after(0, self.clear_trt_results)
            
            # 开始处理
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                "=" * 70 + "\n"))
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                "开始多语言翻译提取（合并JSON配置）...\n"))
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                "=" * 70 + "\n"))
            
            lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
            
            # 显示JSON配置
            self.root.after(0, lambda jp=merged_json: 
                self.append_result('table_range_translator', f"合并JSON: {jp}\n"))
            
            # 显示各语言目录
            for lang, dir_path in lang_dirs.items():
                self.root.after(0, lambda ln=lang_names.get(lang, lang), dp=dir_path: 
                    self.append_result('table_range_translator', f"{ln}目录: {dp}\n"))
            
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                f"输出文件: {output_file}\n"))
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                "\n"))
            
            # 定义进度回调函数
            def progress_callback(msg):
                """进度回调，将消息显示到界面"""
                self.root.after(0, lambda m=msg: self.append_result('table_range_translator', m + "\n"))
            
            # 使用新的合并JSON处理方法
            results = self.table_range_translator.process_with_merged_json(
                merged_json, lang_dirs, progress_callback=progress_callback)
            
            if results:
                self.root.after(0, lambda: self.append_result('table_range_translator', 
                    f"✓ 成功提取 {len(results)} 条数据\n\n"))
                
                # 生成翻译CSV
                self.root.after(0, lambda: self.append_result('table_range_translator', 
                    "正在生成翻译CSV...\n"))
                
                success = self.table_range_translator.generate_translation_csv(output_file)
                
                if success:
                    self.root.after(0, lambda: self.append_result('table_range_translator', 
                        f"✓ 翻译CSV已生成: {output_file}\n\n"))
                    
                    # 显示处理报告
                    report = self.table_range_translator.get_processing_report()
                    self.root.after(0, lambda: self.append_result('table_range_translator', 
                        report + "\n"))
                    
                    # 显示成功消息
                    stats = self.table_range_translator.processing_stats
                    msg = (f"多语言翻译提取完成！\n\n"
                          f"处理表格: {stats['processed_tables']}/{stats['total_tables']}\n"
                          f"导出字段: {stats['exported_fields']} 个\n"
                          f"提取数据: {stats['total_rows']} 行\n\n"
                          f"翻译CSV已生成:\n{output_file}")
                    self.root.after(0, lambda: messagebox.showinfo("完成", msg))
                else:
                    self.root.after(0, lambda: self.append_result('table_range_translator', 
                        "✗ 生成翻译CSV失败\n"))
                    self.root.after(0, lambda: messagebox.showerror("错误", "生成翻译CSV失败"))
            else:
                self.root.after(0, lambda: self.append_result('table_range_translator', 
                    "✗ 没有提取到数据\n"))
                self.root.after(0, lambda: messagebox.showwarning("警告", 
                    "没有提取到数据，请检查JSON配置和Excel文件"))
        
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self.append_result('table_range_translator', 
                f"\n✗ {error_msg}\n"))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.trt_process_button.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("就绪"))
    
    def clear_trt_results(self):
        """清空多语言翻译提取结果"""
        self.clear_result('table_range_translator')
    
    # 批量改表相关方法
    def browse_batch_mapping_file(self):
        """浏览批量改表映射文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射表文件",
            filetypes=[("Excel和CSV文件", "*.xlsx *.xls *.csv"), ("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_mapping_var.set(file_path)
            # 自动刷新语言列表
            self.refresh_batch_languages()
            # 自动设置输出报告路径
            if not self.batch_report_var.get():
                report_path = os.path.splitext(file_path)[0] + "_修改报告.xlsx"
                self.batch_report_var.set(report_path)
    
    def refresh_batch_sheets(self):
        """刷新映射表的工作表列表（保留兼容性，实际调用刷新语言）"""
        self.refresh_batch_languages()

    def refresh_batch_languages(self):
        """刷新可用的语言列表"""
        mapping_file = self.batch_mapping_var.get().strip()
        
        if not mapping_file or not os.path.exists(mapping_file):
            messagebox.showwarning("警告", "请先选择有效的映射表文件")
            return
        
        try:
            import pandas as pd
            
            # 检查文件扩展名
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            if file_ext == '.csv':
                # CSV文件，直接读取列名
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, nrows=0, encoding=encoding)
                        columns = df.columns.tolist()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, nrows=0, encoding='utf-8', errors='ignore')
                    columns = df.columns.tolist()
            else:
                # Excel文件
                xl = pd.ExcelFile(mapping_file)
                
                # 跳过汇总信息等非数据工作表，找到第一个数据工作表
                skip_sheets = ['汇总信息', '汇总', 'Summary', 'summary', '说明', 'Info']
                data_sheet = None
                for sheet in xl.sheet_names:
                    if sheet not in skip_sheets:
                        data_sheet = sheet
                        break
                
                if not data_sheet:
                    data_sheet = xl.sheet_names[0] if xl.sheet_names else None
                
                if data_sheet:
                    df = pd.read_excel(mapping_file, sheet_name=data_sheet, nrows=0)
                    columns = df.columns.tolist()
                else:
                    columns = []
            
            # 排除一些常见的非语言列
            exclude_cols = ['Classification', 'classification', 'ID', 'id', 'Field', 'field', 
                           '字段', '字段名', '表名', 'Table', 'table', '项目', '值', 'Name', 'name']
            lang_cols = [c for c in columns if c not in exclude_cols]
            
            if lang_cols:
                self.batch_language_combo['values'] = lang_cols
                # 保持当前选择，如果当前值有效的话
                current = self.batch_language_var.get()
                if current not in lang_cols:
                    self.batch_language_combo.set(lang_cols[0])
                # 更新JSON语言标签以反映当前选择的语言
                self._update_batch_json_language_for_selected_lang()
            else:
                messagebox.showwarning("警告", f"未找到语言列")
        except Exception as e:
            messagebox.showerror("错误", f"获取语言列表失败: {e}")
    
    def _update_batch_json_language_for_selected_lang(self):
        """根据选择的语言更新JSON语言标签"""
        selected_lang = self.batch_language_var.get().strip()
        if selected_lang:
            # 语言名称映射
            lang_names = {
                'VN': '越南语', 'TH': '泰语', 'EN': '英语', 'ZH': '中文', 'CN': '中文',
                'JP': '日语', 'KR': '韩语', 'TW': '繁体中文', 'Support-CH': '中文(Support)',
                'Polish-CH': '中文(Polish)', 'VN.1': '越南语(VN.1)'
            }
            lang_name = lang_names.get(selected_lang, selected_lang)
            self.batch_json_lang_label.config(text=f"🎯 {lang_name} ({selected_lang})")
        else:
            self.batch_json_lang_label.config(text="")
    
    def _on_batch_language_changed(self, event=None):
        """当语言选择变化时更新JSON语言标签"""
        self._update_batch_json_language_for_selected_lang()
    
    def browse_batch_json_file(self):
        """浏览批量改表JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_json_var.set(file_path)
            # 读取JSON并显示语言标记
            self._update_batch_json_language_label(file_path)
    
    def _update_batch_json_language_label(self, json_path):
        """更新批量改表JSON语言标记显示"""
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 格式1和2：检查language字段
            if 'language' in config and isinstance(config['language'], dict):
                lang_name = config['language'].get('name', '')
                lang_code = config['language'].get('code', '')
                self.batch_json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
            else:
                # 格式3：检测语言代码作为顶层key
                lang_code_keys = ['ZH', 'VN', 'TH', 'EN', 'JP', 'KR', 'TW', 'CN',
                                 'zh', 'vn', 'th', 'en', 'jp', 'kr', 'tw', 'cn']
                detected_lang_key = None
                for key in config.keys():
                    if key.upper() in [k.upper() for k in lang_code_keys]:
                        detected_lang_key = key
                        break
                
                if detected_lang_key and isinstance(config.get(detected_lang_key), dict):
                    lang_code = detected_lang_key.lower()
                    lang_names = {
                        'zh': '中文', 'cn': '中文', 'vn': '越南语', 'th': '泰语',
                        'en': '英语', 'jp': '日语', 'kr': '韩语', 'tw': '繁体中文'
                    }
                    lang_name = lang_names.get(lang_code, detected_lang_key)
                    self.batch_json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
                else:
                    self.batch_json_lang_label.config(text="⚠️ 无语言标记")
        except Exception as e:
            self.batch_json_lang_label.config(text=f"⚠️ 读取失败: {str(e)}")
    
    def browse_batch_excel_directory(self):
        """浏览要修改的Excel文件目录"""
        directory = filedialog.askdirectory(title="选择Excel文件目录")
        if directory:
            self.batch_excel_dir_var.set(directory)
    
    def browse_batch_report_file(self):
        """浏览修改报告保存位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.batch_report_var.set(file_path)
    
    def preview_batch_mapping(self):
        """预览映射表内容"""
        mapping_file = self.batch_mapping_var.get().strip()
        sheet_name = self.batch_sheet_var.get().strip()
        
        if not mapping_file:
            messagebox.showerror("错误", "请先选择映射表文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射表文件不存在")
            return
        
        try:
            import pandas as pd
            
            # 检查文件扩展名
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            # 读取前20行数据预览
            if file_ext == '.csv':
                # 尝试多种编码读取CSV
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, header=0, nrows=20, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, header=0, nrows=20, encoding='utf-8', errors='ignore')
                sheet_display = 'CSV文件'
            else:
                # Excel文件
                df = pd.read_excel(mapping_file, sheet_name=sheet_name if sheet_name else 0, 
                                  header=0, nrows=20)
                sheet_display = sheet_name or '第一个'
            
            # 创建预览对话框
            preview_dialog = tk.Toplevel(self.root)
            preview_dialog.title(f"映射表预览 - {os.path.basename(mapping_file)}")
            preview_dialog.geometry("900x500")
            
            # 信息标签
            info_label = ttk.Label(preview_dialog, 
                                  text=f"工作表: {sheet_display} | 列数: {len(df.columns)} | 显示前20行")
            info_label.pack(pady=10)
            
            # 创建表格框架
            table_frame = ttk.Frame(preview_dialog)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 创建文本框显示数据
            text_widget = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, 
                                                   font=("Consolas", 9))
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # 格式化显示数据
            header_line = " | ".join([f"{col:<20}" for col in df.columns])
            text_widget.insert(tk.END, header_line + "\n")
            text_widget.insert(tk.END, "-" * len(header_line) + "\n")
            
            for idx, row in df.iterrows():
                row_line = " | ".join([f"{str(val)[:20]:<20}" for val in row])
                text_widget.insert(tk.END, row_line + "\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # 关闭按钮
            close_button = ttk.Button(preview_dialog, text="关闭", 
                                     command=preview_dialog.destroy)
            close_button.pack(pady=10)
            
            preview_dialog.transient(self.root)
            preview_dialog.grab_set()
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {e}")
    
    def start_batch_modification(self):
        """开始批量修改"""
        json_file = self.batch_json_var.get().strip()
        mapping_file = self.batch_mapping_var.get().strip()
        excel_dir = self.batch_excel_dir_var.get().strip()
        report_file = self.batch_report_var.get().strip()
        target_language = self.batch_language_var.get().strip()
        
        # 验证必要参数
        if not json_file:
            messagebox.showerror("错误", "请选择JSON配置文件")
            return
        
        if not os.path.exists(json_file):
            messagebox.showerror("错误", "JSON配置文件不存在")
            return
        
        if not mapping_file:
            messagebox.showerror("错误", "请选择映射表文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射表文件不存在")
            return
        
        if not excel_dir:
            messagebox.showerror("错误", "请选择Excel文件目录")
            return
        
        if not os.path.exists(excel_dir):
            messagebox.showerror("错误", "Excel文件目录不存在")
            return
        
        if not target_language:
            messagebox.showerror("错误", "请选择目标语言")
            return
        
        # 确认操作
        confirm_msg = f"""确认开始批量修改？

JSON配置: {os.path.basename(json_file)}
映射表: {os.path.basename(mapping_file)}
Excel目录: {excel_dir}
目标语言: {target_language}

定位模式（自动识别）:
• 有Position列 → Position直接定位（如B7、E24）
• 无Position列 → ID值作为行号（如ID=7→第7行）

备份: {'是' if self.batch_backup_var.get() else '否'}

提示：建议先用少量数据测试"""
        
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        # 开始处理
        self.batch_process_button.config(state="disabled")
        self.status_var.set("正在批量修改...")
        
        thread = threading.Thread(target=self._batch_modification_thread, 
                                 args=(mapping_file, excel_dir, report_file, 
                                       json_file, target_language))
        thread.daemon = True
        thread.start()
    
    def _batch_modification_thread(self, mapping_file, excel_dir, report_file, 
                                   json_file, target_language):
        """批量修改处理线程"""
        try:
            # 清空结果
            self.root.after(0, self.clear_batch_results)
            
            # 初始化 batch_modifier（使用 xlwings 引擎）
            self.batch_modifier = BatchExcelModifier()
            
            # 显示开始信息
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "=" * 70 + "\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "开始批量修改Excel文件...\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "=" * 70 + "\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"JSON配置: {json_file}\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"映射表: {mapping_file}\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"Excel目录: {excel_dir}\n"))
            self.root.after(0, lambda tl=target_language: self.append_result('batch_modifier', 
                f"目标语言列: {tl}\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"自动识别: 工作表名=文件名, ID列=ID, 字段列=Classification\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"备份: {'是' if self.batch_backup_var.get() else '否'}\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"处理引擎: xlwings (Excel原生引擎)\n"))
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "\n"))
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.root.after(0, lambda m=msg: self.append_result('batch_modifier', m + "\n"))
            
            self.batch_modifier.set_progress_callback(progress_callback)
            
            # 加载JSON配置
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "正在加载JSON配置...\n"))
            
            field_config = self.batch_modifier.load_json_config(json_file)
            
            if not field_config:
                self.root.after(0, lambda: self.append_result('batch_modifier', 
                    "✗ JSON配置加载失败或为空\n"))
                self.root.after(0, lambda: messagebox.showerror("错误", "JSON配置加载失败"))
                return
            
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"✓ 已加载 {len(field_config)//2} 个表的字段配置\n\n"))
            
            # 使用手动指定语言列方式
            stats = self.batch_modifier.process_batch_modification_by_language(
                mapping_path=mapping_file,
                excel_directory=excel_dir,
                id_col="ID",
                target_language=target_language,
                field_col=None,  # 自动检测
                backup=self.batch_backup_var.get()
            )
            
            # 显示统计信息
            summary = self.batch_modifier.get_stats_summary()
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                "\n" + summary + "\n"))
            
            # 显示跳过的表（不在JSON配置中）
            if stats.get('skipped_no_config', 0) > 0:
                self.root.after(0, lambda: self.append_result('batch_modifier', 
                    f"\n⚠️ 跳过了 {stats['skipped_no_config']} 个工作表（表名不在JSON配置中）\n"))
            
            # 显示跳过的文件（文件不存在）
            if stats.get('skipped_no_file', 0) > 0:
                self.root.after(0, lambda: self.append_result('batch_modifier', 
                    f"⚠️ 跳过了 {stats['skipped_no_file']} 个工作表（对应Excel文件不存在）\n"))
            
            # 生成报告
            if report_file:
                self.root.after(0, lambda: self.append_result('batch_modifier', 
                    f"\n正在生成修改报告...\n"))
                
                if self.batch_modifier.generate_modification_report(report_file):
                    self.root.after(0, lambda: self.append_result('batch_modifier', 
                        f"✓ 修改报告已生成: {report_file}\n"))
                else:
                    self.root.after(0, lambda: self.append_result('batch_modifier', 
                        "✗ 生成修改报告失败\n"))
            
            # 显示错误日志
            if self.batch_modifier.error_logs:
                self.root.after(0, lambda: self.append_result('batch_modifier', 
                    "\n错误日志:\n"))
                for error in self.batch_modifier.error_logs[:20]:  # 最多显示20条
                    self.root.after(0, lambda e=error: self.append_result('batch_modifier', 
                        f"  ✗ {e}\n"))
                if len(self.batch_modifier.error_logs) > 20:
                    self.root.after(0, lambda: self.append_result('batch_modifier', 
                        f"  ... 还有 {len(self.batch_modifier.error_logs) - 20} 条错误\n"))
            
            # 显示成功消息
            msg = f"""批量修改完成！

修改的文件数: {stats['modified_files']}
修改的单元格数: {stats['modified_cells']}
错误数: {stats['errors']}

定位模式: {'Position直接定位' if stats.get('used_position_mode') else '行号直接定位'}
报告已保存: {report_file if report_file else '未生成'}

提示：如有错误请查看结果详情"""
            
            self.root.after(0, lambda: messagebox.showinfo("完成", msg))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, lambda: self.append_result('batch_modifier', 
                f"\n✗ {error_msg}\n"))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.batch_process_button.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("就绪"))
    
    def clear_batch_results(self):
        """清空批量改表结果"""
        self.clear_result('batch_modifier')
    
    def preview_batch_json_config(self):
        """预览JSON配置内容"""
        json_file = self.batch_json_var.get().strip()
        
        if not json_file:
            messagebox.showwarning("提示", "请先选择JSON配置文件")
            return
        
        if not os.path.exists(json_file):
            messagebox.showerror("错误", f"文件不存在: {json_file}")
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 构建预览内容
            preview_lines = []
            preview_lines.append("=" * 60)
            preview_lines.append(f"JSON配置文件: {os.path.basename(json_file)}")
            preview_lines.append("=" * 60)
            
            text_tables = config.get('text_tables', [])
            if not text_tables:
                preview_lines.append("\n⚠️ 未找到 text_tables 配置")
            else:
                preview_lines.append(f"\n共 {len(text_tables)} 个表配置:\n")
                
                for i, table in enumerate(text_tables, 1):
                    table_name = table.get('table_name', '未知')
                    sheet_name = table.get('sheet_name', '')
                    fields = table.get('fields', [])
                    fields_with_examples = table.get('fields_with_examples', [])
                    
                    preview_lines.append(f"[{i}] {table_name}")
                    if sheet_name:
                        preview_lines.append(f"    工作表: {sheet_name}")
                    
                    # 显示字段
                    all_fields = list(set(fields + fields_with_examples))
                    if all_fields:
                        preview_lines.append(f"    字段 ({len(all_fields)}): {', '.join(all_fields)}")
                    else:
                        preview_lines.append("    字段: (无)")
                    preview_lines.append("")
            
            preview_lines.append("-" * 60)
            preview_lines.append("注: 映射表中的列名需要与上述字段名完全匹配才会被处理")
            
            # 显示预览
            preview_text = "\n".join(preview_lines)
            
            # 创建预览窗口
            preview_window = tk.Toplevel(self.root)
            preview_window.title("JSON配置预览")
            preview_window.geometry("600x500")
            
            # 文本框
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_widget.insert(1.0, preview_text)
            text_widget.config(state='disabled')
            
            # 关闭按钮
            close_btn = ttk.Button(preview_window, text="关闭", 
                                  command=preview_window.destroy)
            close_btn.pack(pady=10)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败: {str(e)}")
    
    # ==================== Excel配置同步相关方法 ====================
    
    def browse_sync_source_dir(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.sync_source_dir_var.set(directory)
    
    def browse_sync_target1_dir(self):
        """浏览目标目录1"""
        directory = filedialog.askdirectory(title="选择目标目录1")
        if directory:
            self.sync_target1_dir_var.set(directory)
    
    def browse_sync_target2_dir(self):
        """浏览目标目录2"""
        directory = filedialog.askdirectory(title="选择目标目录2")
        if directory:
            self.sync_target2_dir_var.set(directory)
    
    def browse_sync_json_file(self):
        """浏览JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.sync_json_var.set(file_path)
    
    def browse_sync_filter_file(self):
        """浏览字段过滤配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择字段过滤配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.sync_filter_var.set(file_path)
    
    def browse_sync_report_file(self):
        """浏览报告输出位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.sync_report_var.set(file_path)
    
    def clear_sync_results(self):
        """清空同步结果"""
        self.clear_result('config_sync')
    
    def preview_sync_filter_config(self):
        """预览过滤配置"""
        filter_file = self.sync_filter_var.get().strip()
        
        if not filter_file:
            messagebox.showwarning("提示", "请先选择过滤配置文件")
            return
        
        if not os.path.exists(filter_file):
            messagebox.showerror("错误", "过滤配置文件不存在")
            return
        
        try:
            with open(filter_file, 'r', encoding='utf-8') as f:
                filter_config = json.load(f)
            
            # 解析过滤配置
            skip_fields = {}
            
            if 'skip_fields' in filter_config:
                skip_fields = filter_config['skip_fields']
            elif 'text_tables' in filter_config:
                for table_info in filter_config['text_tables']:
                    table_name = table_info.get('table_name', '')
                    fields = table_info.get('skip_fields', [])
                    if table_name and fields:
                        skip_fields[table_name] = fields
            
            # 生成预览内容
            preview_lines = []
            preview_lines.append("=" * 60)
            preview_lines.append("字段过滤配置预览")
            preview_lines.append("=" * 60)
            preview_lines.append(f"\n配置文件: {os.path.basename(filter_file)}")
            preview_lines.append(f"包含表数: {len(skip_fields)}")
            preview_lines.append("\n" + "-" * 60)
            preview_lines.append("过滤详情:")
            preview_lines.append("-" * 60)
            
            if skip_fields:
                for table_name, fields in skip_fields.items():
                    preview_lines.append(f"\n📄 {table_name}")
                    preview_lines.append(f"   跳过字段 ({len(fields)}): {', '.join(fields)}")
            else:
                preview_lines.append("\n⚠️ 没有配置过滤字段")
            
            # 创建预览窗口
            preview_window = tk.Toplevel(self.root)
            preview_window.title("过滤配置预览")
            preview_window.geometry("700x500")
            
            # 文本框
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_widget.insert(1.0, "\n".join(preview_lines))
            text_widget.config(state='disabled')
            
            # 关闭按钮
            close_btn = ttk.Button(preview_window, text="关闭", 
                                  command=preview_window.destroy)
            close_btn.pack(pady=10)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败: {str(e)}")
    
    def preview_sync_matching(self):
        """预览匹配的文件"""
        source_dir = self.sync_source_dir_var.get().strip()
        target1_dir = self.sync_target1_dir_var.get().strip()
        target2_dir = self.sync_target2_dir_var.get().strip()
        
        if not source_dir:
            messagebox.showerror("错误", "请选择源目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        if not target1_dir and not target2_dir:
            messagebox.showerror("错误", "请至少选择一个目标目录")
            return
        
        # 构建目标目录列表
        target_dirs = []
        if target1_dir and os.path.exists(target1_dir):
            target_dirs.append(target1_dir)
        if target2_dir and os.path.exists(target2_dir):
            target_dirs.append(target2_dir)
        
        if not target_dirs:
            messagebox.showerror("错误", "没有有效的目标目录")
            return
        
        # 查找匹配的文件
        matching_files = self.config_sync.find_matching_files(source_dir, target_dirs)
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("文件匹配预览")
        preview_window.geometry("700x500")
        
        # 文本框
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 生成预览内容
        preview_lines = []
        preview_lines.append("=" * 60)
        preview_lines.append("文件匹配预览")
        preview_lines.append("=" * 60)
        preview_lines.append(f"\n源目录: {source_dir}")
        preview_lines.append(f"目标目录1: {target1_dir or '(未选择)'}")
        preview_lines.append(f"目标目录2: {target2_dir or '(未选择)'}")
        preview_lines.append(f"\n源目录文件数: {self.config_sync.processing_stats['source_files']}")
        preview_lines.append(f"匹配的文件数: {len(matching_files)}")
        preview_lines.append("\n" + "-" * 60)
        preview_lines.append("匹配详情:")
        preview_lines.append("-" * 60)
        
        for filename, info in matching_files.items():
            preview_lines.append(f"\n📄 {filename}")
            preview_lines.append(f"   源文件: {info['source']}")
            for idx, target in enumerate(info['targets'], 1):
                preview_lines.append(f"   目标{idx}: {target}")
        
        if not matching_files:
            preview_lines.append("\n⚠️ 没有找到匹配的文件")
        
        text_widget.insert(1.0, "\n".join(preview_lines))
        text_widget.config(state='disabled')
        
        # 关闭按钮
        close_btn = ttk.Button(preview_window, text="关闭", 
                              command=preview_window.destroy)
        close_btn.pack(pady=10)
    
    def start_config_sync(self):
        """开始配置同步"""
        source_dir = self.sync_source_dir_var.get().strip()
        target1_dir = self.sync_target1_dir_var.get().strip()
        target2_dir = self.sync_target2_dir_var.get().strip()
        json_file = self.sync_json_var.get().strip()
        filter_file = self.sync_filter_var.get().strip()
        report_file = self.sync_report_var.get().strip()
        
        # 验证参数
        if not source_dir:
            messagebox.showerror("错误", "请选择源目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        if not target1_dir and not target2_dir:
            messagebox.showerror("错误", "请至少选择一个目标目录")
            return
        
        # 检查目标目录
        if target1_dir and not os.path.exists(target1_dir):
            messagebox.showerror("错误", "目标目录1不存在")
            return
        
        if target2_dir and not os.path.exists(target2_dir):
            messagebox.showerror("错误", "目标目录2不存在")
            return
        
        # 确认操作
        confirm_msg = f"""确认开始同步配置？

源目录: {source_dir}
目标目录1: {target1_dir or '(未选择)'}
目标目录2: {target2_dir or '(未选择)'}
JSON配置: {os.path.basename(json_file) if json_file else '(未选择)'}
过滤配置: {os.path.basename(filter_file) if filter_file else '(未选择)'}

同步选项:
- 备份: {'是' if self.sync_backup_var.get() else '否'}
- 同步值: {'是' if self.sync_values_var.get() else '否'}
- 同步公式: {'是' if self.sync_formulas_var.get() else '否'}
- 同步样式: {'是' if self.sync_styles_var.get() else '否'}
- 同步列宽: {'是' if self.sync_column_widths_var.get() else '否'}"""
        
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        # 开始处理
        self.sync_process_button.config(state="disabled")
        self.status_var.set("正在同步配置...")
        
        thread = threading.Thread(target=self._config_sync_thread, 
                                 args=(source_dir, target1_dir, target2_dir, 
                                       json_file, filter_file, report_file))
        thread.daemon = True
        thread.start()
    
    def _config_sync_thread(self, source_dir, target1_dir, target2_dir, 
                           json_file, filter_file, report_file):
        """配置同步处理线程"""
        try:
            # 清空结果
            self.root.after(0, self.clear_sync_results)
            
            # 显示开始信息
            self.root.after(0, lambda: self.append_result('config_sync', 
                "=" * 70 + "\n"))
            self.root.after(0, lambda: self.append_result('config_sync', 
                "开始同步Excel配置...\n"))
            self.root.after(0, lambda: self.append_result('config_sync', 
                "=" * 70 + "\n"))
            self.root.after(0, lambda: self.append_result('config_sync', 
                f"源目录: {source_dir}\n"))
            self.root.after(0, lambda: self.append_result('config_sync', 
                f"目标目录1: {target1_dir or '(未选择)'}\n"))
            self.root.after(0, lambda: self.append_result('config_sync', 
                f"目标目录2: {target2_dir or '(未选择)'}\n"))
            if json_file:
                self.root.after(0, lambda: self.append_result('config_sync', 
                    f"JSON配置: {json_file}\n"))
            if filter_file:
                self.root.after(0, lambda: self.append_result('config_sync', 
                    f"过滤配置: {filter_file}\n"))
            self.root.after(0, lambda: self.append_result('config_sync', "\n"))
            
            # 设置同步选项
            self.config_sync.sync_options['backup_before_sync'] = self.sync_backup_var.get()
            self.config_sync.sync_options['sync_values'] = self.sync_values_var.get()
            self.config_sync.sync_options['sync_formulas'] = self.sync_formulas_var.get()
            self.config_sync.sync_options['sync_styles'] = self.sync_styles_var.get()
            self.config_sync.sync_options['sync_column_widths'] = self.sync_column_widths_var.get()
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.root.after(0, lambda m=msg: self.append_result('config_sync', m + "\n"))
            
            self.config_sync.set_progress_callback(progress_callback)
            
            # 加载JSON配置（如果有）
            if json_file and os.path.exists(json_file):
                self.root.after(0, lambda: self.append_result('config_sync', 
                    "正在加载JSON配置（仅用于参考）...\n"))
                self.config_sync.load_json_config(json_file)
                self.root.after(0, lambda: self.append_result('config_sync', 
                    "✓ JSON配置已加载\n\n"))
            
            # 加载过滤配置（如果有）
            if filter_file and os.path.exists(filter_file):
                self.root.after(0, lambda: self.append_result('config_sync', 
                    "正在加载过滤配置...\n"))
                self.config_sync.load_filter_config(filter_file)
                skip_count = len(self.config_sync.skip_fields)
                self.root.after(0, lambda: self.append_result('config_sync', 
                    f"✓ 过滤配置已加载，包含 {skip_count} 个表的过滤规则\n\n"))
            
            # 执行同步
            stats = self.config_sync.sync_directories(
                source_dir=source_dir,
                target_dir1=target1_dir if target1_dir else None,
                target_dir2=target2_dir if target2_dir else None
            )
            
            # 显示统计信息
            summary = self.config_sync.get_stats_summary()
            self.root.after(0, lambda: self.append_result('config_sync', "\n" + summary + "\n"))
            
            # 生成报告
            if report_file:
                self.root.after(0, lambda: self.append_result('config_sync', 
                    f"\n正在生成报告: {report_file}\n"))
                if self.config_sync.generate_sync_report(report_file):
                    self.root.after(0, lambda: self.append_result('config_sync', 
                        "✓ 报告生成成功\n"))
                else:
                    self.root.after(0, lambda: self.append_result('config_sync', 
                        "✗ 报告生成失败\n"))
            
            # 完成
            self.root.after(0, lambda: self.status_var.set("同步完成"))
            self.root.after(0, lambda: messagebox.showinfo("完成", "配置同步完成！"))
            
        except Exception as e:
            error_msg = f"同步过程出错: {str(e)}"
            self.root.after(0, lambda: self.append_result('config_sync', 
                f"\n✗ 错误: {error_msg}\n"))
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.root.after(0, lambda: self.sync_process_button.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("就绪"))


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