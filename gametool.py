#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
越南文检测 - 图形界面版本
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import pandas as pd
from core.localization_checker import LocalizationChecker
from version import get_version, format_version_string, get_description


class LocalizationGUI:
    """本地化工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"越南文检测 - 越南文表格检测器 v{get_version()}")
        self.root.geometry("1000x800")
        self.root.minsize(900, 750)
        self.root.resizable(True, True)
        
        # 设置窗口图标和样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化检测器
        self.checker = LocalizationChecker()
        
        # 扫描状态
        self.is_scanning = False
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 12, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 10))
        style.configure('Success.TLabel', font=('Microsoft YaHei', 10), foreground='green')
        style.configure('Error.TLabel', font=('Microsoft YaHei', 10), foreground='red')
    
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
        title_label = ttk.Label(main_frame, text="越南文检测", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # 版本信息
        version_label = ttk.Label(main_frame, text=format_version_string(), style='Info.TLabel')
        version_label.grid(row=1, column=0, pady=(0, 10))
        
        # 创建页签控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建两个页签
        self.create_scan_tab()
        self.create_locate_tab()
    
    def create_scan_tab(self):
        """创建扫描页签"""
        # 扫描页签
        scan_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(scan_frame, text="批量扫描")
        
        # 配置网格权重
        scan_frame.columnconfigure(1, weight=1)
        scan_frame.rowconfigure(6, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(scan_frame, text="选择扫描目录", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="目录路径:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_btn = ttk.Button(dir_frame, text="浏览...", command=self.browse_directory)
        self.browse_btn.grid(row=0, column=2)
        
        # 扫描选项
        options_frame = ttk.LabelFrame(scan_frame, text="扫描选项", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归扫描子目录", variable=self.recursive_var).grid(row=0, column=0, sticky=tk.W)
        
        # 支持的文件格式说明
        format_label = ttk.Label(options_frame, text="支持格式: .xlsx, .xls, .csv, .tsv", style='Info.TLabel')
        format_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 控制按钮
        button_frame = ttk.Frame(scan_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.scan_btn = ttk.Button(button_frame, text="开始扫描", command=self.start_scan)
        self.scan_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="停止扫描", command=self.stop_scan, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="清空结果", command=self.clear_results)
        self.clear_btn.grid(row=0, column=2)
        
        # 进度条
        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(scan_frame, textvariable=self.progress_var, style='Info.TLabel')
        self.progress_label.grid(row=3, column=0, columnspan=3, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(scan_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(scan_frame, text="扫描结果", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建结果显示的文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=80, font=('Consolas', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(scan_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_locate_tab(self):
        """创建定位页签"""
        # 定位页签
        locate_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(locate_frame, text="精确定位")
        
        # 配置网格权重
        locate_frame.columnconfigure(1, weight=1)
        locate_frame.rowconfigure(5, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(locate_frame, text="选择表格文件", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="文件路径:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.file_browse_btn = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        self.file_browse_btn.grid(row=0, column=2)
        
        # 表名输入区域
        sheet_frame = ttk.LabelFrame(locate_frame, text="工作表设置", padding="10")
        sheet_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        sheet_frame.columnconfigure(1, weight=1)
        
        ttk.Label(sheet_frame, text="工作表名:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.sheet_var = tk.StringVar()
        self.sheet_entry = ttk.Entry(sheet_frame, textvariable=self.sheet_var, width=30)
        self.sheet_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(sheet_frame, text="(留空则使用第一个工作表)", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # 控制按钮
        locate_button_frame = ttk.Frame(locate_frame)
        locate_button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.locate_btn = ttk.Button(locate_button_frame, text="开始定位", command=self.start_locate)
        self.locate_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_locate_btn = ttk.Button(locate_button_frame, text="清空结果", command=self.clear_locate_results)
        self.clear_locate_btn.grid(row=0, column=1)
        
        # 进度显示
        self.locate_progress_var = tk.StringVar(value="就绪")
        self.locate_progress_label = ttk.Label(locate_frame, textvariable=self.locate_progress_var, style='Info.TLabel')
        self.locate_progress_label.grid(row=3, column=0, columnspan=3, pady=(0, 5))
        
        # 结果显示区域
        locate_result_frame = ttk.LabelFrame(locate_frame, text="定位结果", padding="10")
        locate_result_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        locate_result_frame.columnconfigure(0, weight=1)
        locate_result_frame.rowconfigure(0, weight=1)
        
        # 创建结果显示的文本框
        self.locate_result_text = scrolledtext.ScrolledText(locate_result_frame, height=15, width=80, font=('Consolas', 10))
        self.locate_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.locate_status_var = tk.StringVar(value="就绪")
        locate_status_bar = ttk.Label(locate_frame, textvariable=self.locate_status_var, relief=tk.SUNKEN, anchor=tk.W)
        locate_status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择要扫描的目录")
        if directory:
            self.dir_var.set(directory)
            self.update_status(f"已选择目录: {directory}")
    
    def browse_file(self):
        """浏览选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择表格文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("CSV文件", "*.csv *.tsv"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.file_var.set(file_path)
            self.update_locate_status(f"已选择文件: {os.path.basename(file_path)}")
    
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_progress(self, message):
        """更新进度显示"""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def update_locate_status(self, message):
        """更新定位页签状态栏"""
        self.locate_status_var.set(message)
        self.root.update_idletasks()
    
    def update_locate_progress(self, message):
        """更新定位页签进度显示"""
        self.locate_progress_var.set(message)
        self.root.update_idletasks()
    
    
    def log_message(self, message, level="INFO"):
        """在结果区域记录消息"""
        self.result_text.insert(tk.END, f"[{level}] {message}\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def log_locate_message(self, message, level="INFO"):
        """在定位结果区域记录消息"""
        self.locate_result_text.insert(tk.END, f"[{level}] {message}\n")
        self.locate_result_text.see(tk.END)
        self.root.update_idletasks()
    
    
    def start_scan(self):
        """开始扫描"""
        directory = self.dir_var.get().strip()
        
        if not directory:
            messagebox.showwarning("警告", "请先选择要扫描的目录")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("错误", "选择的目录不存在")
            return
        
        if not os.path.isdir(directory):
            messagebox.showerror("错误", "选择的路径不是一个目录")
            return
        
        # 禁用扫描按钮，启用停止按钮
        self.scan_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.is_scanning = True
        
        # 清空之前的结果
        self.result_text.delete(1.0, tk.END)
        
        # 开始进度条
        self.progress_bar.start()
        
        # 在新线程中执行扫描
        scan_thread = threading.Thread(target=self.scan_directory_thread, args=(directory,))
        scan_thread.daemon = True
        scan_thread.start()
    
    def stop_scan(self):
        """停止扫描"""
        self.is_scanning = False
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_bar.stop()
        self.update_progress("扫描已停止")
        self.update_status("扫描已停止")
        self.log_message("用户停止了扫描", "WARN")
    
    def scan_directory_thread(self, directory):
        """在后台线程中执行扫描"""
        try:
            self.update_progress("正在扫描目录...")
            self.update_status("正在扫描中...")
            self.log_message(f"开始扫描目录: {directory}", "INFO")
            
            # 获取目录中的所有表格文件
            directory_path = Path(directory)
            table_files = []
            
            if self.recursive_var.get():
                # 递归扫描
                for file_path in directory_path.rglob('*'):
                    if file_path.is_file() and self.checker.table_checker.is_table_file(file_path):
                        table_files.append(file_path)
            else:
                # 只扫描当前目录
                for file_path in directory_path.iterdir():
                    if file_path.is_file() and self.checker.table_checker.is_table_file(file_path):
                        table_files.append(file_path)
            
            if not table_files:
                self.log_message("未找到任何表格文件", "WARN")
                self.scan_complete([])
                return
            
            self.log_message(f"找到 {len(table_files)} 个表格文件", "INFO")
            self.log_message("-" * 50, "INFO")
            
            valid_tables = []
            total_files = len(table_files)
            
            for i, file_path in enumerate(table_files, 1):
                if not self.is_scanning:
                    break
                
                self.update_progress(f"正在检测文件 {i}/{total_files}: {file_path.name}")
                
                try:
                    has_vietnamese = self.checker.table_checker.check_table_has_vietnamese(file_path)
                    
                    if has_vietnamese:
                        valid_tables.append(file_path.name)
                        self.log_message(f"✓ {file_path.name} - 包含越南文", "SUCCESS")
                    else:
                        self.log_message(f"✗ {file_path.name} - 不包含越南文", "INFO")
                        
                except Exception as e:
                    self.log_message(f"✗ {file_path.name} - 检测失败: {str(e)}", "ERROR")
            
            self.scan_complete(valid_tables)
            
        except Exception as e:
            self.log_message(f"扫描过程中发生错误: {str(e)}", "ERROR")
            self.scan_complete([])
    
    def scan_complete(self, valid_tables):
        """扫描完成处理"""
        self.is_scanning = False
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.progress_bar.stop()
        
        # 显示结果
        self.log_message("=" * 50, "INFO")
        self.log_message("扫描完成！", "INFO")
        self.log_message("=" * 50, "INFO")
        
        if valid_tables:
            self.log_message(f"找到 {len(valid_tables)} 个包含越南文的表格文件:", "SUCCESS")
            for i, table_name in enumerate(valid_tables, 1):
                self.log_message(f"  {i:2d}. {table_name}", "SUCCESS")
        else:
            self.log_message("未找到包含越南文的表格文件", "INFO")
        
        self.update_progress("扫描完成")
        self.update_status(f"扫描完成 - 找到 {len(valid_tables)} 个有效文件")
    
    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
        self.update_progress("就绪")
        self.update_status("就绪")
    
    def clear_locate_results(self):
        """清空定位结果"""
        self.locate_result_text.delete(1.0, tk.END)
        self.update_locate_progress("就绪")
        self.update_locate_status("就绪")
    
    
    def start_locate(self):
        """开始定位越南文"""
        file_path = self.file_var.get().strip()
        sheet_name = self.sheet_var.get().strip()
        
        if not file_path:
            messagebox.showwarning("警告", "请先选择要分析的表格文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "选择的文件不存在")
            return
        
        if not os.path.isfile(file_path):
            messagebox.showerror("错误", "选择的路径不是一个文件")
            return
        
        # 清空之前的结果
        self.locate_result_text.delete(1.0, tk.END)
        
        # 在新线程中执行定位
        locate_thread = threading.Thread(target=self.locate_vietnamese_thread, args=(file_path, sheet_name))
        locate_thread.daemon = True
        locate_thread.start()
    
    def locate_vietnamese_thread(self, file_path, sheet_name):
        """在后台线程中执行越南文定位"""
        try:
            self.update_locate_progress("正在分析文件...")
            self.update_locate_status("正在定位中...")
            self.log_locate_message(f"开始分析文件: {os.path.basename(file_path)}", "INFO")
            
            # 读取表格文件
            if file_path.lower().endswith(('.xlsx', '.xls')):
                # Excel文件
                if sheet_name:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        self.log_locate_message(f"使用工作表: {sheet_name}", "INFO")
                    except Exception as e:
                        self.log_locate_message(f"无法读取工作表 '{sheet_name}': {str(e)}", "ERROR")
                        self.log_locate_message("尝试使用第一个工作表...", "WARN")
                        df = pd.read_excel(file_path)
                else:
                    df = pd.read_excel(file_path)
                    self.log_locate_message("使用第一个工作表", "INFO")
            else:
                # CSV文件
                encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        self.log_locate_message(f"使用编码: {encoding}", "INFO")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    self.log_locate_message("无法读取CSV文件，尝试了多种编码", "ERROR")
                    return
            
            self.log_locate_message(f"表格尺寸: {df.shape[0]} 行 x {df.shape[1]} 列", "INFO")
            self.log_locate_message("-" * 50, "INFO")
            
            # 检测越南文位置
            vietnamese_locations = []
            detector = self.checker.table_checker.vietnamese_detector
            
            for col_idx, column in enumerate(df.columns):
                for row_idx, value in enumerate(df[column]):
                    if pd.notna(value) and detector.contains_vietnamese(str(value)):
                        vietnamese_locations.append({
                            'row': row_idx + 2,  # +2 因为pandas从0开始，且Excel有标题行
                            'col': col_idx + 1,  # +1 因为pandas从0开始
                            'column_name': column,
                            'content': str(value)
                        })
            
            # 显示结果
            self.log_locate_message("=" * 50, "INFO")
            self.log_locate_message("定位完成！", "INFO")
            self.log_locate_message("=" * 50, "INFO")
            
            if vietnamese_locations:
                self.log_locate_message(f"找到 {len(vietnamese_locations)} 个包含越南文的位置:", "SUCCESS")
                self.log_locate_message("", "INFO")
                
                for i, location in enumerate(vietnamese_locations, 1):
                    self.log_locate_message(f"{i:2d}. 位置: 第{location['row']}行, 第{location['col']}列 ({location['column_name']})", "SUCCESS")
                    self.log_locate_message(f"    内容: {location['content']}", "INFO")
                    self.log_locate_message("", "INFO")
            else:
                self.log_locate_message("未找到包含越南文的内容", "INFO")
            
            self.update_locate_progress("定位完成")
            self.update_locate_status(f"定位完成 - 找到 {len(vietnamese_locations)} 个位置")
            
        except Exception as e:
            self.log_locate_message(f"定位过程中发生错误: {str(e)}", "ERROR")
            self.update_locate_progress("定位失败")
            self.update_locate_status("定位失败")
    
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_scanning:
            if messagebox.askokcancel("退出", "正在扫描中，确定要退出吗？"):
                self.is_scanning = False
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = LocalizationGUI(root)
    
    # 设置窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 设置窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # 启动界面
    root.mainloop()


if __name__ == "__main__":
    main()
