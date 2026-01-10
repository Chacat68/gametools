# -*- coding: utf-8 -*-
"""
Excel分页拆分标签页模块

提供Excel工作表按条件拆分到多个sheet的功能
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from gui.tabs.base_tab import BaseTab


class SheetSplitterTab(BaseTab):
    """Excel分页拆分标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'sheet_splitter'
        self._output_file = None
        
        # 初始化核心处理器
        self._init_processor()
        
    def _init_processor(self):
        """初始化处理器"""
        try:
            from core.excel_sheet_splitter import ExcelSheetSplitter
            self.sheet_splitter = ExcelSheetSplitter()
        except ImportError as e:
            self.sheet_splitter = None
            print(f"警告: 无法导入ExcelSheetSplitter: {e}")
    
    def create_widgets(self):
        """创建分页拆分标签页的控件"""
        # 输入文件选择
        input_frame = self.create_labeled_frame("输入文件", self.frame)
        
        # 输入文件路径
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(file_frame, text="Excel文件:").pack(side=tk.LEFT)
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_var, width=60)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(file_frame, text="浏览...", 
                   command=self.browse_input_file).pack(side=tk.LEFT)
        
        # 工作表选择
        sheet_frame = ttk.Frame(input_frame)
        sheet_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sheet_frame, text="工作表:").pack(side=tk.LEFT)
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(sheet_frame, textvariable=self.sheet_var, 
                                        width=30, state="readonly")
        self.sheet_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(sheet_frame, text="分组列:").pack(side=tk.LEFT, padx=(20, 0))
        self.group_column_var = tk.StringVar()
        ttk.Entry(sheet_frame, textvariable=self.group_column_var, 
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(sheet_frame, text="(留空=自动检测)", 
                  foreground="gray").pack(side=tk.LEFT)
        
        # 输出设置
        output_frame = self.create_labeled_frame("输出设置", self.frame)
        
        output_file_frame = ttk.Frame(output_frame)
        output_file_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(output_file_frame, text="输出文件:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_file_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(output_file_frame, text="浏览...", 
                   command=self.browse_output_file).pack(side=tk.LEFT)
        
        # 选项
        options_frame = self.create_labeled_frame("选项", self.frame)
        
        self.extract_filename_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="从文件名提取信息", 
                        variable=self.extract_filename_var).pack(side=tk.LEFT, padx=10)
        
        self.include_summary_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含汇总页", 
                        variable=self.include_summary_var).pack(side=tk.LEFT, padx=10)
        
        self.remove_first_col_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="移除第一列", 
                        variable=self.remove_first_col_var).pack(side=tk.LEFT, padx=10)
        
        # 按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="开始拆分", 
                                         command=self.start_split)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        self.open_folder_button = ttk.Button(button_frame, text="打开输出目录", 
                                              command=self.open_output_folder, 
                                              state="disabled")
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = self.create_labeled_frame("处理结果", self.frame)
        self.create_result_text(result_frame, self.result_key)
        
    def browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)
            # 自动设置输出文件名
            if not self.output_var.get():
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_分页拆分.xlsx"
                self.output_var.set(str(output_path))
            # 加载工作表列表
            self._load_sheet_names(file_path)
    
    def _load_sheet_names(self, file_path):
        """加载Excel文件的工作表名称列表"""
        if not self.sheet_splitter:
            return
        try:
            sheet_names = self.sheet_splitter.get_sheet_names(file_path)
            self.sheet_combo['values'] = sheet_names
            if sheet_names:
                self.sheet_combo.set(sheet_names[0])
        except Exception as e:
            self.sheet_combo['values'] = []
            self.sheet_combo.set('')
    
    def browse_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存拆分后的Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_var.set(file_path)
    
    def start_split(self):
        """开始Excel分页拆分"""
        input_file = self.input_var.get().strip()
        output_file = self.output_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请设置输出文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        if not self.sheet_splitter:
            messagebox.showerror("错误", "分页拆分模块未正确加载")
            return
        
        # 禁用按钮
        self.process_button.config(state="disabled")
        self.open_folder_button.config(state="disabled")
        self.set_status("正在拆分Excel数据...")
        
        thread = threading.Thread(target=self._split_process, 
                                  args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _split_process(self, input_file, output_file):
        """Excel分页拆分处理（后台线程）"""
        try:
            # 清空结果
            self.schedule_ui(self.clear_results)
            
            # 显示开始信息
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                f"开始处理文件: {input_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                f"输出文件: {output_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                "-" * 50 + "\n"))
            
            # 获取选项
            sheet_name = self.sheet_var.get().strip() or None
            group_column = self.group_column_var.get().strip() or None
            extract_filename = self.extract_filename_var.get()
            include_summary = self.include_summary_var.get()
            remove_first_column = self.remove_first_col_var.get()
            
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
                self.schedule_ui(lambda: self._show_success_result(report, output_file))
            else:
                self.schedule_ui(lambda: self._show_error_result(report))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.schedule_ui(lambda: self._show_error_result(error_msg))
    
    def _show_success_result(self, report, output_file):
        """显示成功结果"""
        self.append_result(self.result_key, report)
        self.append_result(self.result_key, "\n\n✅ Excel分页拆分完成！")
        self.append_result(self.result_key, f"\n输出文件: {output_file}")
        
        self.process_button.config(state="normal")
        self.open_folder_button.config(state="normal")
        self.set_status("Excel分页拆分完成")
        
        # 保存输出文件路径用于打开文件夹
        self._output_file = output_file
        
        messagebox.showinfo("成功", f"Excel分页拆分完成！\n\n输出文件: {output_file}")
    
    def _show_error_result(self, error_msg):
        """显示错误结果"""
        self.append_result(self.result_key, f"❌ {error_msg}\n")
        
        self.process_button.config(state="normal")
        self.set_status("Excel分页拆分失败")
        
        messagebox.showerror("错误", error_msg)
    
    def clear_results(self):
        """清空结果"""
        self.clear_result(self.result_key)
    
    def open_output_folder(self):
        """打开输出文件所在的文件夹"""
        try:
            if self._output_file and os.path.exists(self._output_file):
                folder_path = os.path.dirname(self._output_file)
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
