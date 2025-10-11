#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools - 统一用户界面
集成策划本地化工具和JSON格式检测工具
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
from tools.json_format_detector.json_format_detector import JSONFormatDetector
from tools.excel_data_processor import ExcelDataProcessor


class GameToolsUnified:
    """gametools统一界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("gametools - 游戏工具集")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
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
        self.json_detector = JSONFormatDetector()
        self.excel_processor = ExcelDataProcessor()
        
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
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="gametools - 游戏工具集", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 创建笔记本控件（页签）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 创建各个功能页签
        self.create_localization_tab()
        self.create_json_detector_tab()
        self.create_excel_data_processor_tab()
        self.create_about_tab()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_localization_tab(self):
        """创建策划本地化工具页签"""
        # 本地化工具框架
        loc_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(loc_frame, text="策划本地化工具")
        
        # 配置网格
        loc_frame.columnconfigure(1, weight=1)
        loc_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(loc_frame, text="越南文表格检测器", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 功能选择框架
        func_frame = ttk.LabelFrame(loc_frame, text="功能选择", padding="10")
        func_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        func_frame.columnconfigure(1, weight=1)
        
        # 批量扫描
        ttk.Label(func_frame, text="批量扫描:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.loc_directory_var = tk.StringVar()
        self.loc_directory_entry = ttk.Entry(func_frame, textvariable=self.loc_directory_var, width=50)
        self.loc_directory_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.loc_browse_button = ttk.Button(func_frame, text="浏览", 
                                           command=self.browse_localization_directory)
        self.loc_browse_button.grid(row=0, column=2)
        
        # 递归扫描选项
        self.loc_recursive_var = tk.BooleanVar(value=True)
        self.loc_recursive_check = ttk.Checkbutton(func_frame, text="递归扫描子目录", 
                                                  variable=self.loc_recursive_var)
        self.loc_recursive_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(loc_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.loc_scan_button = ttk.Button(button_frame, text="开始扫描", 
                                         command=self.start_localization_scan, 
                                         style='Accent.TButton')
        self.loc_scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.loc_clear_button = ttk.Button(button_frame, text="清空结果", 
                                          command=self.clear_localization_results)
        self.loc_clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.loc_demo_button = ttk.Button(button_frame, text="创建演示文件", 
                                         command=self.create_demo_files)
        self.loc_demo_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(loc_frame, text="扫描结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.loc_result_text = scrolledtext.ScrolledText(result_frame, 
                                                        wrap=tk.WORD, 
                                                        font=("Consolas", 10),
                                                        height=15)
        self.loc_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_json_detector_tab(self):
        """创建JSON格式检测工具页签"""
        # JSON检测工具框架
        json_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(json_frame, text="JSON格式检测工具")
        
        # 配置网格
        json_frame.columnconfigure(1, weight=1)
        json_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(json_frame, text="JSON格式一致性检测器", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(json_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # JSON文件路径
        ttk.Label(file_frame, text="JSON文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.json_file_var = tk.StringVar()
        self.json_file_entry = ttk.Entry(file_frame, textvariable=self.json_file_var, width=50)
        self.json_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.json_browse_button = ttk.Button(file_frame, text="浏览", 
                                            command=self.browse_json_file)
        self.json_browse_button.grid(row=0, column=2)
        
        # 字段名设置
        ttk.Label(file_frame, text="检测字段:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.json_field_var = tk.StringVar(value="text")
        self.json_field_entry = ttk.Entry(file_frame, textvariable=self.json_field_var, width=20)
        self.json_field_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(json_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.json_detect_button = ttk.Button(button_frame, text="开始检测", 
                                            command=self.start_json_detection, 
                                            style='Accent.TButton')
        self.json_detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.json_clear_button = ttk.Button(button_frame, text="清空结果", 
                                           command=self.clear_json_results)
        self.json_clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.json_save_button = ttk.Button(button_frame, text="保存报告", 
                                          command=self.save_json_report, 
                                          state="disabled")
        self.json_save_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(json_frame, text="检测结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.json_result_text = scrolledtext.ScrolledText(result_frame, 
                                                         wrap=tk.WORD, 
                                                         font=("Consolas", 10),
                                                         height=15)
        self.json_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_excel_data_processor_tab(self):
        """创建Excel数据处理工具页签"""
        # Excel数据处理工具框架
        excel_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(excel_frame, text="Excel数据处理工具")
        
        # 配置网格
        excel_frame.columnconfigure(1, weight=1)
        excel_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(excel_frame, text="Excel数据处理工具", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(excel_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.excel_input_var = tk.StringVar()
        self.excel_input_entry = ttk.Entry(file_frame, textvariable=self.excel_input_var, width=50)
        self.excel_input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.excel_input_browse_button = ttk.Button(file_frame, text="浏览", 
                                                    command=self.browse_excel_input_file)
        self.excel_input_browse_button.grid(row=0, column=2)
        
        # 输出文件夹
        ttk.Label(file_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.excel_output_folder_var = tk.StringVar()
        self.excel_output_folder_entry = ttk.Entry(file_frame, textvariable=self.excel_output_folder_var, width=50)
        self.excel_output_folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        self.excel_output_browse_button = ttk.Button(file_frame, text="浏览", 
                                                     command=self.browse_excel_output_folder)
        self.excel_output_browse_button.grid(row=1, column=2, pady=(10, 0))
        
        # 输出文件名
        ttk.Label(file_frame, text="输出文件名:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.excel_output_filename_var = tk.StringVar(value="整合结果.xlsx")
        self.excel_output_filename_entry = ttk.Entry(file_frame, textvariable=self.excel_output_filename_var, width=30)
        self.excel_output_filename_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 选项设置框架
        options_frame = ttk.LabelFrame(excel_frame, text="选项设置", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 分组列设置
        ttk.Label(options_frame, text="分组列:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.excel_group_column_var = tk.StringVar()
        self.excel_group_column_entry = ttk.Entry(options_frame, textvariable=self.excel_group_column_var, width=20)
        self.excel_group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(options_frame, text="(留空使用第一列)", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W)
        
        # 工作表前缀
        ttk.Label(options_frame, text="工作表前缀:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.excel_sheet_prefix_var = tk.StringVar()
        self.excel_sheet_prefix_entry = ttk.Entry(options_frame, textvariable=self.excel_sheet_prefix_var, width=20)
        self.excel_sheet_prefix_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 包含汇总信息选项
        self.excel_include_summary_var = tk.BooleanVar(value=True)
        self.excel_include_summary_check = ttk.Checkbutton(options_frame, text="包含汇总信息工作表", 
                                                          variable=self.excel_include_summary_var)
        self.excel_include_summary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 控制按钮框架
        button_frame = ttk.Frame(excel_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        self.excel_process_button = ttk.Button(button_frame, text="开始整合", 
                                               command=self.start_excel_consolidation, 
                                               style='Accent.TButton')
        self.excel_process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.excel_clear_button = ttk.Button(button_frame, text="清空结果", 
                                             command=self.clear_excel_results)
        self.excel_clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.excel_preview_button = ttk.Button(button_frame, text="预览数据", 
                                               command=self.preview_excel_data,
                                               state="disabled")
        self.excel_preview_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(excel_frame, text="处理结果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.excel_result_text = scrolledtext.ScrolledText(result_frame, 
                                                          wrap=tk.WORD, 
                                                          font=("Consolas", 10),
                                                          height=15)
        self.excel_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_about_tab(self):
        """创建关于页签"""
        about_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(about_frame, text="关于")
        
        # 关于信息
        about_text = """
gametools - 游戏工具集

版本: v1.3.0
开发日期: 2024年

功能模块:
• 策划本地化工具 - 检测表格文件中的越南文内容
• JSON格式检测工具 - 检测JSON文件中text字段的格式一致性
• Excel数据处理工具 - 根据A列内容对Excel数据进行分组和处理

主要特性:
• 支持多种文件格式 (Excel, CSV, JSON)
• 图形化界面，操作简单
• 多线程处理，界面响应流畅
• 支持exe文件打包和分发

技术栈:
• Python 3.7+
• Tkinter (GUI界面)
• pandas (数据处理)
• openpyxl (Excel文件处理)

使用方法:
1. 选择相应的功能页签
2. 按照界面提示操作
3. 查看检测结果

注意事项:
• 确保文件格式正确
• 大文件处理可能需要较长时间
• 建议在检测前备份重要文件

技术支持:
如有问题或建议，请联系开发团队。

版权所有 © 2024 gametools
        """
        
        about_label = ttk.Label(about_frame, text=about_text, 
                               font=("Microsoft YaHei", 10), 
                               justify=tk.LEFT)
        about_label.pack(anchor=tk.W)
    
    # 策划本地化工具相关方法
    def browse_localization_directory(self):
        """浏览本地化工具目录"""
        directory = filedialog.askdirectory(title="选择要扫描的目录")
        if directory:
            self.loc_directory_var.set(directory)
    
    def start_localization_scan(self):
        """开始本地化扫描"""
        directory = self.loc_directory_var.get().strip()
        if not directory:
            messagebox.showerror("错误", "请选择要扫描的目录")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("错误", "目录不存在")
            return
        
        # 在新线程中执行扫描
        self.loc_scan_button.config(state="disabled")
        self.status_var.set("正在扫描...")
        
        thread = threading.Thread(target=self._localization_scan, 
                                 args=(directory, self.loc_recursive_var.get()))
        thread.daemon = True
        thread.start()
    
    def _localization_scan(self, directory, recursive):
        """本地化扫描（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_localization_results)
            
            # 开始扫描
            self.root.after(0, lambda: self.loc_result_text.insert(tk.END, 
                f"开始扫描目录: {directory}\n"))
            self.root.after(0, lambda: self.loc_result_text.insert(tk.END, 
                f"递归扫描: {'是' if recursive else '否'}\n"))
            self.root.after(0, lambda: self.loc_result_text.insert(tk.END, 
                "支持的格式: .xlsx, .xls, .csv, .tsv\n"))
            self.root.after(0, lambda: self.loc_result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 执行扫描
            results = self.localization_checker.scan_directory(directory, recursive)
            
            # 显示结果
            self.root.after(0, self._update_localization_results, results)
            
        except Exception as e:
            error_msg = f"扫描过程中发生错误: {str(e)}"
            self.root.after(0, self._show_localization_error, error_msg)
    
    def _update_localization_results(self, results):
        """更新本地化扫描结果"""
        if results:
            self.loc_result_text.insert(tk.END, f"找到 {len(results)} 个包含越南文的文件:\n\n")
            for i, file_path in enumerate(results, 1):
                self.loc_result_text.insert(tk.END, f"{i}. {file_path}\n")
        else:
            self.loc_result_text.insert(tk.END, "未找到包含越南文的文件。\n")
        
        self.loc_scan_button.config(state="normal")
        self.status_var.set("扫描完成")
    
    def _show_localization_error(self, error_msg):
        """显示本地化扫描错误"""
        self.loc_result_text.insert(tk.END, f"错误: {error_msg}\n")
        self.loc_scan_button.config(state="normal")
        self.status_var.set("扫描失败")
        messagebox.showerror("错误", error_msg)
    
    def clear_localization_results(self):
        """清空本地化扫描结果"""
        self.loc_result_text.delete(1.0, tk.END)
    
    def create_demo_files(self):
        """创建演示文件"""
        try:
            # 运行演示脚本
            result = subprocess.run([sys.executable, "tools/demo.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                self.loc_result_text.insert(tk.END, "演示文件创建成功！\n")
                self.loc_result_text.insert(tk.END, "文件位置: demo_tables/\n")
                self.loc_result_text.insert(tk.END, "现在可以使用批量扫描功能测试这些文件。\n")
                self.status_var.set("演示文件创建成功")
            else:
                self.loc_result_text.insert(tk.END, f"创建演示文件失败: {result.stderr}\n")
                self.status_var.set("演示文件创建失败")
        except Exception as e:
            self.loc_result_text.insert(tk.END, f"创建演示文件时发生错误: {str(e)}\n")
            self.status_var.set("演示文件创建失败")
    
    # JSON格式检测工具相关方法
    def browse_json_file(self):
        """浏览JSON文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.json_file_var.set(file_path)
    
    def start_json_detection(self):
        """开始JSON格式检测"""
        file_path = self.json_file_var.get().strip()
        field_name = self.json_field_var.get().strip()
        
        if not file_path:
            messagebox.showerror("错误", "请选择JSON文件")
            return
        
        if not field_name:
            messagebox.showerror("错误", "请输入检测字段名")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 在新线程中执行检测
        self.json_detect_button.config(state="disabled")
        self.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._json_detection, 
                                 args=(file_path, field_name))
        thread.daemon = True
        thread.start()
    
    def _json_detection(self, file_path, field_name):
        """JSON格式检测（后台线程）"""
        try:
            report = self.json_detector.detect_format(file_path, field_name)
            self.root.after(0, self._update_json_results, report)
        except Exception as e:
            error_msg = f"检测过程中发生错误: {str(e)}"
            self.root.after(0, self._show_json_error, error_msg)
    
    def _update_json_results(self, report):
        """更新JSON检测结果"""
        self.json_result_text.delete(1.0, tk.END)
        self.json_result_text.insert(1.0, report)
        self.json_result_text.see(1.0)
        
        self.json_detect_button.config(state="normal")
        self.json_save_button.config(state="normal")
        self.status_var.set("检测完成")
    
    def _show_json_error(self, error_msg):
        """显示JSON检测错误"""
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