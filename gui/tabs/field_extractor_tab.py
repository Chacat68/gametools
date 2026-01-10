# -*- coding: utf-8 -*-
"""
表字段导出标签页模块

提供Excel表字段信息提取功能，支持多语言
"""

import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path

from gui.tabs.base_tab import BaseTab


class FieldExtractorTab(BaseTab):
    """表字段导出标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'field_extractor'
        self.extraction_results = None
        
        # 初始化核心处理器
        self._init_processor()
        
    def _init_processor(self):
        """初始化处理器"""
        try:
            from core.excel_field_extractor import ExcelFieldExtractor
            self.field_extractor = ExcelFieldExtractor()
        except ImportError as e:
            self.field_extractor = None
            print(f"警告: 无法导入ExcelFieldExtractor: {e}")
    
    def create_widgets(self):
        """创建字段导出标签页的控件"""
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # 目录选择区域 - 多语言分支
        dir_frame = ttk.LabelFrame(self.frame, text="多语言目录配置（从物理行第5行提取字段名）", padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.zh_dir_var = tk.StringVar()
        self.zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.zh_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览", 
                   command=lambda: self.browse_language_dir('zh')).grid(row=0, column=2, pady=(0, 8))
        
        self.zh_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.zh_check_var).grid(row=0, column=3, padx=(5, 0), pady=(0, 8))
        
        # 越南语目录
        ttk.Label(dir_frame, text="越南语目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.vn_dir_var = tk.StringVar()
        self.vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.vn_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览", 
                   command=lambda: self.browse_language_dir('vn')).grid(row=1, column=2, pady=(0, 8))
        
        self.vn_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.vn_check_var).grid(row=1, column=3, padx=(5, 0), pady=(0, 8))
        
        # 泰语目录
        ttk.Label(dir_frame, text="泰语目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.th_dir_var = tk.StringVar()
        self.th_dir_entry = ttk.Entry(dir_frame, textvariable=self.th_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览", 
                   command=lambda: self.browse_language_dir('th')).grid(row=2, column=2, pady=(0, 8))
        
        self.th_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dir_frame, text="导出", variable=self.th_check_var).grid(row=2, column=3, padx=(5, 0), pady=(0, 8))
        
        # 输出文件夹
        ttk.Label(dir_frame, text="输出目录:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, 
                                          font=("Microsoft YaHei", 9))
        self.output_dir_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(dir_frame, text="选择输出目录", 
                   command=self.browse_output_directory).grid(row=3, column=2)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(self.frame, text="处理选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 递归扫描选项
        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                        variable=self.recursive_var).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # 输出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT, padx=(0, 10))
        self.output_format_var = tk.StringVar(value="json")
        ttk.Radiobutton(format_frame, text="JSON格式", 
                        variable=self.output_format_var, 
                        value="json").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="CSV格式", 
                        variable=self.output_format_var, 
                        value="csv").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Excel格式", 
                        variable=self.output_format_var, 
                        value="excel").pack(side=tk.LEFT)
        
        # 说明信息
        info_label = ttk.Label(options_frame, 
                               text="💡 选择需要导出的语言分支，输出JSON带语言标记", 
                               foreground='blue')
        info_label.grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.extract_button = ttk.Button(button_frame, text="📊 开始提取", 
                                         command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="📋 复制JSON", 
                   command=self.copy_json_result).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="⚠️ 错误日志", 
                   command=self.show_error_logs).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="🗑️ 清空结果", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="📝 查看结果", 
                   command=lambda: self.show_results_dialog(self.result_key)).pack(side=tk.LEFT)
    
    def browse_language_dir(self, lang_code):
        """浏览特定语言的目录"""
        lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
        dir_path = filedialog.askdirectory(title=f"选择{lang_names.get(lang_code, '')}目录")
        if dir_path:
            if lang_code == 'zh':
                self.zh_dir_var.set(dir_path)
            elif lang_code == 'vn':
                self.vn_dir_var.set(dir_path)
            elif lang_code == 'th':
                self.th_dir_var.set(dir_path)
            # 如果输出目录为空，自动设置为该目录的父目录
            if not self.output_dir_var.get():
                self.output_dir_var.set(dir_path)
    
    def browse_output_directory(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def start_extraction(self):
        """开始字段提取"""
        if not self.field_extractor:
            messagebox.showerror("错误", "字段提取模块未正确加载")
            return
        
        # 收集选中的语言目录
        directories = {}
        if self.zh_check_var.get() and self.zh_dir_var.get().strip():
            directories['zh'] = self.zh_dir_var.get().strip()
        if self.vn_check_var.get() and self.vn_dir_var.get().strip():
            directories['vn'] = self.vn_dir_var.get().strip()
        if self.th_check_var.get() and self.th_dir_var.get().strip():
            directories['th'] = self.th_dir_var.get().strip()
        
        output_dir = self.output_dir_var.get().strip()
        
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
            self.output_dir_var.set(output_dir)
        
        # 在新线程中执行提取
        self.extract_button.config(state="disabled")
        self.set_status("正在提取表字段...")
        
        thread = threading.Thread(target=self._extraction_thread, 
                                  args=(directories, output_dir))
        thread.daemon = True
        thread.start()
    
    def _extraction_thread(self, directories, output_dir):
        """字段提取线程 - 支持多语言"""
        try:
            # 清空结果存储
            self.schedule_ui(lambda: self.clear_result(self.result_key))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 60 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "开始提取多语言表字段信息...\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 60 + "\n"))
            
            lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
            for lang, dir_path in directories.items():
                self.schedule_ui(lambda l=lang, d=dir_path: self.append_result(
                    self.result_key, f"{lang_names[l]}目录: {d}\n"))
            
            self.schedule_ui(lambda: self.append_result(self.result_key, f"输出目录: {output_dir}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"输出格式: {self.output_format_var.get().upper()}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"递归扫描: {'是' if self.recursive_var.get() else '否'}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n"))
            
            # 执行多语言提取
            all_stats = self.field_extractor.process_multi_language_directories(
                directories=directories,
                output_folder=output_dir,
                output_format=self.output_format_var.get(),
                recursive=self.recursive_var.get()
            )
            
            # 保存输出文件路径
            self.store_result(self.result_key, ', '.join(all_stats.get('output_files', [])))
            
            # 收集所有结果
            all_results = []
            for lang_code, lang_data in all_stats['languages'].items():
                if 'stats' in lang_data and 'results' in lang_data['stats']:
                    all_results.extend(lang_data['stats']['results'])
            self.extraction_results = all_results
            
            # 显示统计信息
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 60 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "多语言提取完成!\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 60 + "\n"))
            
            # 分语言显示统计
            for lang_code, lang_data in all_stats['languages'].items():
                stats = lang_data.get('stats', {})
                self.schedule_ui(lambda n=lang_data['name'], s=stats: self.append_result(
                    self.result_key, 
                    f"\n【{n}】文件数: {s.get('total_files', 0)}, "
                    f"工作表: {s.get('total_sheets', 0)}, "
                    f"字段数: {s.get('total_fields', 0)}\n"
                ))
            
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n总文件数: {all_stats['total_files']}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"总工作表数: {all_stats['total_sheets']}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"总字段数: {all_stats['total_fields']}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n输出文件:\n"))
            for f in all_stats.get('output_files', []):
                self.schedule_ui(lambda file=f: self.append_result(self.result_key, f"  - {file}\n"))
            
            # 显示完成消息
            self.schedule_ui(lambda: self.set_status("字段提取完成"))
            
            output_files_str = '\n'.join(all_stats.get('output_files', []))
            self.schedule_ui(lambda: messagebox.showinfo(
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
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n错误: {str(e)}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, error_msg + "\n"))
            self.schedule_ui(lambda: self.set_status("字段提取失败"))
            self.schedule_ui(lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))
        
        finally:
            self.schedule_ui(lambda: self.extract_button.config(state="normal"))
    
    def clear_results(self):
        """清空字段提取结果"""
        self.clear_result(self.result_key)
        self.extraction_results = None
        if self.field_extractor:
            self.field_extractor.clear_logs()
    
    def show_error_logs(self):
        """显示字段提取的错误和警告日志"""
        if not self.field_extractor:
            messagebox.showwarning("警告", "字段提取模块未加载")
            return
        
        logs = self.field_extractor.get_all_logs()
        errors = logs['errors']
        warnings = logs['warnings']
        
        if not errors and not warnings:
            messagebox.showinfo("日志信息", "没有错误或警告日志")
            return
        
        # 创建新窗口显示日志
        log_window = tk.Toplevel(self.get_root())
        log_window.title("字段提取 - 错误与警告日志")
        log_window.geometry("900x600")
        
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(log_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 错误日志标签页
        error_frame = ttk.Frame(notebook)
        notebook.add(error_frame, text=f"错误日志 ({len(errors)})")
        
        error_text = scrolledtext.ScrolledText(error_frame, wrap=tk.WORD, font=('Consolas', 9))
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
        
        warning_text = scrolledtext.ScrolledText(warning_frame, wrap=tk.WORD, font=('Consolas', 9))
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
    
    def copy_json_result(self):
        """复制字段提取的JSON结果到剪贴板"""
        if not self.extraction_results:
            messagebox.showwarning("警告", "没有可复制的结果，请先执行字段提取")
            return
        
        try:
            # 构建JSON数据
            json_data = [{
                "table_name": r['excel_file'],
                "sheet_name": r['sheet_name'],
                "fields_with_examples": r.get('fields_with_examples', []),
                "field_count": r['field_count']
            } for r in self.extraction_results]
            
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # 复制到剪贴板
            root = self.get_root()
            root.clipboard_clear()
            root.clipboard_append(json_str)
            root.update()
            
            messagebox.showinfo("成功", f"JSON结果已复制到剪贴板\n共 {len(json_data)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败:\n{str(e)}")
