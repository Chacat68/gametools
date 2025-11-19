#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel表字段导出工具 - GUI版本
提供图形界面来扫描Excel文件并提取字段信息
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor


class ExcelFieldExtractorGUI:
    """Excel表字段导出工具GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Excel表字段导出工具")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 创建提取器实例
        self.extractor = ExcelFieldExtractor()
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 线程控制
        self.is_processing = False
        
        # 存储最后的结果数据
        self.last_results = None
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 按钮样式
        style.configure('Action.TButton', 
                       font=('微软雅黑', 10),
                       padding=8)
        
        # 标签样式
        style.configure('Title.TLabel',
                       font=('微软雅黑', 11, 'bold'),
                       foreground='#2c3e50')
        
        style.configure('Info.TLabel',
                       font=('微软雅黑', 9),
                       foreground='#7f8c8d')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, 
                               text="Excel表字段导出工具",
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # 说明文本
        info_text = ("此工具用于扫描Excel文件，检测包含文本内容的列，\n"
                    "并从第5行提取字段名，输出标准JSON格式")
        info_label = ttk.Label(main_frame, 
                              text=info_text,
                              style='Info.TLabel',
                              justify=tk.CENTER)
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 输入目录选择
        input_frame = ttk.LabelFrame(main_frame, text="扫描设置", padding="10")
        input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="扫描目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_dir = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_dir).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(input_frame, text="浏览...", 
                  command=self.browse_input_dir).grid(
            row=0, column=2, padx=5, pady=5)
        
        # 输出目录选择
        ttk.Label(input_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.output_dir).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(input_frame, text="浏览...", 
                  command=self.browse_output_dir).grid(
            row=1, column=2, padx=5, pady=5)
        
        # 选项设置
        options_frame = ttk.Frame(input_frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 递归扫描选项
        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, 
                       text="递归扫描子目录",
                       variable=self.recursive_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # 输出格式选择
        ttk.Label(options_frame, text="输出格式:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        self.output_format = tk.StringVar(value="json")
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(format_frame, text="JSON", 
                       variable=self.output_format, 
                       value="json").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="CSV", 
                       variable=self.output_format, 
                       value="csv").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Excel", 
                       variable=self.output_format, 
                       value="excel").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Excel", 
                       variable=self.output_format, 
                       value="excel").pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.start_button = ttk.Button(button_frame, 
                                       text="开始提取",
                                       style='Action.TButton',
                                       command=self.start_extraction)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = ttk.Button(button_frame,
                                     text="复制JSON结果",
                                     style='Action.TButton',
                                     command=self.copy_json_result)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, 
                  text="清空日志",
                  style='Action.TButton',
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                  wrap=tk.WORD,
                                                  font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, 
                              textvariable=self.status_var,
                              relief=tk.SUNKEN,
                              anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择扫描目录")
        if directory:
            self.input_dir.set(directory)
            # 如果输出目录为空，自动设置为输入目录
            if not self.output_dir.get():
                self.output_dir.set(directory)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def log(self, message):
        """输出日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.last_results = None
        self.copy_button.config(state='disabled')
    
    def copy_json_result(self):
        """复制JSON结果到剪贴板"""
        if not self.last_results:
            messagebox.showwarning("警告", "没有可复制的结果")
            return
        
        try:
            import json
            # 构建JSON数据
            json_data = [{
                "table_name": r['excel_file'],
                "sheet_name": r['sheet_name'],
                "fields": r['fields'],
                "field_count": r['field_count']
            } for r in self.last_results]
            
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
            
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(json_str)
            self.root.update()
            
            messagebox.showinfo("成功", f"JSON结果已复制到剪贴板\n共 {len(json_data)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败:\n{str(e)}")
    
    def start_extraction(self):
        """开始提取"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return
        
        # 验证输入
        input_dir = self.input_dir.get().strip()
        if not input_dir:
            messagebox.showerror("错误", "请选择扫描目录")
            return
        
        if not Path(input_dir).exists():
            messagebox.showerror("错误", "扫描目录不存在")
            return
        
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            output_dir = input_dir
            self.output_dir.set(output_dir)
        
        # 在线程中执行提取
        self.is_processing = True
        self.start_button.config(state='disabled')
        self.status_var.set("正在处理...")
        
        thread = threading.Thread(target=self.extraction_thread, 
                                 args=(input_dir, output_dir))
        thread.daemon = True
        thread.start()
    
    def extraction_thread(self, input_dir, output_dir):
        """提取线程"""
        try:
            self.log("=" * 60)
            self.log("开始提取Excel表字段信息...")
            self.log("=" * 60)
            self.log(f"扫描目录: {input_dir}")
            self.log(f"输出目录: {output_dir}")
            self.log(f"输出格式: {self.output_format.get().upper()}")
            self.log(f"递归扫描: {'是' if self.recursive_var.get() else '否'}")
            self.log("")
            
            # 重定向print输出到日志
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # 执行提取
            stats = self.extractor.process_directory(
                directory_path=input_dir,
                output_folder=output_dir,
                output_format=self.output_format.get(),
                recursive=self.recursive_var.get()
            )
            
            # 获取print输出
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # 显示输出
            for line in output.split('\n'):
                if line.strip():
                    self.log(line)
            
            # 保存结果数据
            self.last_results = stats.get('results', [])
            
            # 显示统计信息
            self.log("")
            self.log("=" * 60)
            self.log("提取完成!")
            self.log("=" * 60)
            self.log(f"扫描文件数: {stats['total_files']}")
            self.log(f"工作表数: {stats['total_sheets']}")
            self.log(f"提取字段数: {stats['total_fields']}")
            self.log(f"输出文件: {stats['output_file']}")
            self.log("")
            
            # 如果是JSON格式，显示JSON内容
            if self.output_format.get() == 'json' and self.last_results:
                self.log("JSON结果预览:")
                self.log("-" * 60)
                import json
                json_str = json.dumps([{
                    "table_name": r['excel_file'],
                    "sheet_name": r['sheet_name'],
                    "fields": r['fields'],
                    "field_count": r['field_count']
                } for r in self.last_results], ensure_ascii=False, indent=2)
                self.log(json_str)
                self.log("-" * 60)
                # 启用复制按钮
                self.root.after(0, lambda: self.copy_button.config(state='normal'))
            
            self.root.after(0, lambda: self.status_var.set("处理完成"))
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"提取完成!\n\n"
                f"扫描文件数: {stats['total_files']}\n"
                f"工作表数: {stats['total_sheets']}\n"
                f"提取字段数: {stats['total_fields']}\n\n"
                f"结果已保存到:\n{stats['output_file']}"
            ))
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            self.log(f"\n错误: {str(e)}")
            self.log(error_msg)
            self.root.after(0, lambda: self.status_var.set("处理失败"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.start_button.config(state='normal'))


def main():
    """主函数"""
    root = tk.Tk()
    app = ExcelFieldExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
