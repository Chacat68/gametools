# -*- coding: utf-8 -*-
"""
Excel转CSV标签页模块

提供将Excel文件转换为CSV格式的功能
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from gui.tabs.base_tab import BaseTab


class CsvConverterTab(BaseTab):
    """Excel转CSV标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'csv_converter'
        self._output_dir = None
        
        # 初始化核心处理器
        self._init_processor()
        
    def _init_processor(self):
        """初始化处理器"""
        try:
            from core.excel_to_csv_converter import ExcelToCsvConverter
            self.converter = ExcelToCsvConverter()
        except ImportError as e:
            self.converter = None
            print(f"警告: 无法导入ExcelToCsvConverter: {e}")
    
    def create_widgets(self):
        """创建Excel转CSV标签页的控件"""
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # 输入设置区域
        input_frame = ttk.LabelFrame(self.frame, text="输入设置", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        input_frame.columnconfigure(1, weight=1)
        
        # 输入文件/目录
        ttk.Label(input_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, 
                                     font=("Microsoft YaHei", 9))
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.grid(row=0, column=2, pady=(0, 5))
        ttk.Button(input_btn_frame, text="选择文件", 
                   command=self.browse_input_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_btn_frame, text="选择目录", 
                   command=self.browse_input_dir).pack(side=tk.LEFT)
        
        # 输出目录
        ttk.Label(input_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(input_frame, textvariable=self.output_var, 
                                      font=("Microsoft YaHei", 9))
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        ttk.Button(input_frame, text="浏览", 
                   command=self.browse_output_dir).grid(row=1, column=2, pady=(0, 5))
        
        ttk.Label(input_frame, text="(留空则输出到源文件同目录)", 
                  foreground='gray').grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        # 转换选项区域
        options_frame = ttk.LabelFrame(self.frame, text="转换选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_frame.columnconfigure(1, weight=1)
        
        # 编码选择
        ttk.Label(options_frame, text="输出编码:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.encoding_var = tk.StringVar(value="utf-8-sig")
        ttk.Combobox(options_frame, textvariable=self.encoding_var, 
                     values=["utf-8-sig", "utf-8", "gbk", "gb2312"],
                     state="readonly", width=15).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(options_frame, text="(utf-8-sig带BOM，Excel可直接打开)", 
                  foreground='gray').grid(row=0, column=2, sticky=tk.W)
        
        # 分隔符选择
        ttk.Label(options_frame, text="分隔符:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(8, 0))
        self.delimiter_var = tk.StringVar(value=",")
        delimiter_frame = ttk.Frame(options_frame)
        delimiter_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(8, 0))
        
        ttk.Radiobutton(delimiter_frame, text="逗号 (,)", variable=self.delimiter_var, 
                        value=",").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(delimiter_frame, text="制表符 (Tab)", variable=self.delimiter_var, 
                        value="\t").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(delimiter_frame, text="分号 (;)", variable=self.delimiter_var, 
                        value=";").pack(side=tk.LEFT)
        
        # 复选框选项
        check_frame = ttk.Frame(options_frame)
        check_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="递归处理子目录", 
                        variable=self.recursive_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.merge_sheets_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(check_frame, text="合并所有工作表", 
                        variable=self.merge_sheets_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.include_sheet_col_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="合并时添加工作表名称列", 
                        variable=self.include_sheet_col_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.preserve_empty_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="保留空行", 
                        variable=self.preserve_empty_var).pack(side=tk.LEFT)
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(self.frame, text="转换进度", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                            maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 进度文本
        self.progress_text = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.progress_text, 
                  foreground='gray').grid(row=1, column=0, sticky=tk.W)
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.convert_button = ttk.Button(button_frame, text="📄 开始转换", 
                                         command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="🗑️ 清空结果", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=(0, 8))
        
        self.open_folder_button = ttk.Button(button_frame, text="📂 打开输出目录", 
                                              command=self.open_output_folder, 
                                              state="disabled")
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="📝 查看结果", 
                   command=lambda: self.show_results_dialog(self.result_key)).pack(side=tk.LEFT)
    
    def browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)
            if not self.output_var.get():
                self.output_var.set(os.path.dirname(file_path))
    
    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择Excel文件目录")
        if directory:
            self.input_var.set(directory)
            if not self.output_var.get():
                self.output_var.set(directory)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_var.set(directory)
    
    def start_conversion(self):
        """开始转换"""
        input_path = self.input_var.get().strip()
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", "输入路径不存在")
            return
        
        if not self.converter:
            messagebox.showerror("错误", "转换器模块未正确加载")
            return
        
        # 禁用按钮
        self.convert_button.config(state="disabled")
        self.open_folder_button.config(state="disabled")
        self.set_status("正在转换Excel文件...")
        
        # 在新线程中执行转换
        thread = threading.Thread(target=self._conversion_process)
        thread.daemon = True
        thread.start()
    
    def _conversion_process(self):
        """转换处理（后台线程）"""
        try:
            # 清空结果
            self.schedule_ui(self.clear_results)
            
            # 获取参数
            input_path = self.input_var.get().strip()
            output_dir = self.output_var.get().strip() or None
            encoding = self.encoding_var.get()
            delimiter = self.delimiter_var.get()
            recursive = self.recursive_var.get()
            merge_sheets = self.merge_sheets_var.get()
            include_sheet_column = self.include_sheet_col_var.get()
            preserve_empty_rows = self.preserve_empty_var.get()
            
            # 显示开始信息
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "开始Excel转CSV转换...\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"输入路径: {input_path}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"输出目录: {output_dir or '(源文件同目录)'}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"编码: {encoding}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"分隔符: {repr(delimiter)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                f"选项: 递归={recursive}, 合并工作表={merge_sheets}, 保留空行={preserve_empty_rows}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "-" * 70 + "\n\n"))
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.schedule_ui(lambda m=msg: self.append_result(self.result_key, m + "\n"))
                if percentage is not None:
                    self.schedule_ui(lambda p=percentage: self.progress_var.set(p))
                    self.schedule_ui(lambda m=msg: self.progress_text.set(m))
            
            self.converter.set_progress_callback(progress_callback)
            
            # 执行转换
            result = self.converter.batch_convert(
                source_path=input_path,
                output_dir=output_dir,
                recursive=recursive,
                encoding=encoding,
                merge_sheets=merge_sheets,
                include_sheet_column=include_sheet_column,
                delimiter=delimiter,
                preserve_empty_rows=preserve_empty_rows
            )
            
            # 显示结果
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n" + "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "转换统计:\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            
            summary = result.get('summary', {})
            self.schedule_ui(lambda: self.append_result(self.result_key, f"  总文件数: {summary.get('total_files', 0)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"  成功: {summary.get('success_files', 0)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"  失败: {summary.get('failed_files', 0)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"  总工作表: {summary.get('total_sheets', 0)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"  总行数: {summary.get('total_rows', 0)}\n"))
            
            # 显示输出文件列表
            if result.get('files'):
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    "\n输出文件:\n" + "-" * 40 + "\n"))
                for file_result in result['files']:
                    if file_result.get('success'):
                        for output_file in file_result.get('output_files', []):
                            file_path = output_file.get('file_path', '')
                            rows = output_file.get('rows', 0)
                            self.schedule_ui(lambda fp=file_path, r=rows: 
                                self.append_result(self.result_key, f"  ✅ {fp} ({r}行)\n"))
                    else:
                        self.schedule_ui(lambda f=file_result: 
                            self.append_result(self.result_key, 
                                f"  ❌ {f.get('source_file', '未知')}: {f.get('error', '未知错误')}\n"))
            
            # 显示错误（如果有）
            if result.get('errors'):
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    "\n错误列表:\n" + "-" * 40 + "\n"))
                for error in result['errors']:
                    self.schedule_ui(lambda e=error: 
                        self.append_result(self.result_key, 
                            f"  ⚠️ {e.get('file', '未知')}: {e.get('error', '未知错误')}\n"))
            
            # 完成
            self.schedule_ui(lambda: self.progress_var.set(100))
            self.schedule_ui(lambda: self.progress_text.set("转换完成"))
            self.schedule_ui(lambda: self.set_status("Excel转CSV完成"))
            self.schedule_ui(lambda: self.open_folder_button.config(state="normal"))
            
            # 保存输出目录
            final_output = output_dir or (os.path.dirname(self.input_var.get().strip()) 
                                          if os.path.isfile(self.input_var.get().strip()) 
                                          else self.input_var.get().strip())
            self._output_dir = final_output
            
            success_count = summary.get('success_files', 0)
            fail_count = summary.get('failed_files', 0)
            self.schedule_ui(lambda: messagebox.showinfo("完成", 
                f"Excel转CSV完成！\n\n成功: {success_count} 个文件\n失败: {fail_count} 个文件"))
            
        except Exception as e:
            error_msg = f"转换过程出错: {str(e)}"
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n❌ 错误: {error_msg}\n"))
            self.schedule_ui(lambda: self.progress_text.set("转换失败"))
            self.schedule_ui(lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.schedule_ui(lambda: self.convert_button.config(state="normal"))
            self.schedule_ui(lambda: self.set_status("就绪"))
    
    def clear_results(self):
        """清空结果"""
        self.clear_result(self.result_key)
        self.progress_var.set(0)
        self.progress_text.set("就绪")
    
    def open_output_folder(self):
        """打开输出文件夹"""
        if self._output_dir and os.path.exists(self._output_dir):
            if os.name == 'nt':  # Windows
                os.startfile(self._output_dir)
            else:
                subprocess.run(['open', self._output_dir])
        else:
            messagebox.showwarning("提示", "输出目录不存在")
