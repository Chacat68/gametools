#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据处理工具 - GUI界面
提供图形化界面来使用Excel数据处理功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from tools.excel_data_processor import ExcelDataProcessor


class ExcelDataProcessorGUI:
    """Excel数据处理工具GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Excel数据处理工具")
        self.root.geometry("900x700")
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
        
        # 初始化数据处理器
        self.processor = ExcelDataProcessor()
        
        # 处理状态
        self.is_processing = False
    
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
        main_frame.rowconfigure(6, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Excel数据处理工具", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.input_file_var = tk.StringVar()
        self.input_file_entry = ttk.Entry(file_frame, textvariable=self.input_file_var, width=50)
        self.input_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.input_browse_button = ttk.Button(file_frame, text="浏览", 
                                             command=self.browse_input_file)
        self.input_browse_button.grid(row=0, column=2)
        
        # 输出文件夹
        ttk.Label(file_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = ttk.Entry(file_frame, textvariable=self.output_folder_var, width=50)
        self.output_folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        self.output_browse_button = ttk.Button(file_frame, text="浏览", 
                                              command=self.browse_output_folder)
        self.output_browse_button.grid(row=1, column=2, pady=(10, 0))
        
        # 输出文件名
        ttk.Label(file_frame, text="输出文件名:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_filename_var = tk.StringVar(value="处理结果.xlsx")
        self.output_filename_entry = ttk.Entry(file_frame, textvariable=self.output_filename_var, width=30)
        self.output_filename_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 自动文件名选项
        self.auto_filename_var = tk.BooleanVar(value=True)
        self.auto_filename_check = ttk.Checkbutton(file_frame, text="使用A列内容自动生成文件名", 
                                                  variable=self.auto_filename_var,
                                                  command=self._toggle_filename_entry)
        self.auto_filename_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 选项设置框架
        options_frame = ttk.LabelFrame(main_frame, text="选项设置", padding="10")
        options_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 分组列设置
        ttk.Label(options_frame, text="分组列:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.group_column_var = tk.StringVar()
        self.group_column_entry = ttk.Entry(options_frame, textvariable=self.group_column_var, width=20)
        self.group_column_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(options_frame, text="(留空使用第一列)", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W)
        
        # 工作表前缀
        ttk.Label(options_frame, text="工作表前缀:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.sheet_prefix_var = tk.StringVar()
        self.sheet_prefix_entry = ttk.Entry(options_frame, textvariable=self.sheet_prefix_var, width=20)
        self.sheet_prefix_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 包含汇总信息选项
        self.include_summary_var = tk.BooleanVar(value=True)
        self.include_summary_check = ttk.Checkbutton(options_frame, text="包含汇总信息工作表", 
                                                    variable=self.include_summary_var)
        self.include_summary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 文件输出模式选项
        self.separate_files_var = tk.BooleanVar(value=True)
        self.separate_files_check = ttk.Checkbutton(options_frame, text="为每个A列内容创建单独的Excel文件", 
                                                   variable=self.separate_files_var)
        self.separate_files_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="开始处理", 
                                        command=self.start_processing, 
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空结果", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_button = ttk.Button(button_frame, text="预览数据", 
                                        command=self.preview_data,
                                        state="disabled")
        self.preview_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="处理结果", padding="10")
        result_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    height=15)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 初始化文件名输入框状态
        self._toggle_filename_entry()
    
    def _toggle_filename_entry(self):
        """切换文件名输入框的启用状态"""
        if self.auto_filename_var.get():
            self.output_filename_entry.config(state="disabled")
        else:
            self.output_filename_entry.config(state="normal")
    
    def browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_file_var.set(file_path)
            # 自动设置输出文件名
            if not self.output_filename_var.get():
                self.output_filename_var.set("拆分结果.xlsx")
    
    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder_var.set(folder_path)
            # 自动设置输出文件名
            if not self.output_filename_var.get():
                self.output_filename_var.set("拆分结果.xlsx")
    
    def start_processing(self):
        """开始数据处理"""
        input_file = self.input_file_var.get().strip()
        output_folder = self.output_folder_var.get().strip()
        output_filename = self.output_filename_var.get().strip()
        
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
        
        # 确定输出文件名
        if self.auto_filename_var.get():
            output_filename = None  # 使用自动生成
        else:
            output_filename = output_filename
        
        # 在新线程中执行处理
        self.process_button.config(state="disabled")
        self.preview_button.config(state="disabled")
        self.status_var.set("正在处理...")
        
        thread = threading.Thread(target=self._processing_process, 
                                 args=(input_file, output_folder, output_filename))
        thread.daemon = True
        thread.start()
    
    def _processing_process(self, input_file, output_folder, output_filename):
        """数据处理（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_results)
            
            # 显示开始信息
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                f"开始处理文件: {input_file}\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                f"输出文件夹: {output_folder}\n"))
            if output_filename:
                self.root.after(0, lambda: self.result_text.insert(tk.END, 
                    f"输出文件名: {output_filename}\n"))
            else:
                self.root.after(0, lambda: self.result_text.insert(tk.END, 
                    "输出文件名: 自动生成\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 获取选项
            group_column = self.group_column_var.get().strip() or None
            include_summary = self.include_summary_var.get()
            sheet_prefix = self.sheet_prefix_var.get().strip()
            auto_filename = self.auto_filename_var.get()
            separate_files = self.separate_files_var.get()
            
            # 执行处理
            success = self.processor.process_file(
                input_path=input_file,
                output_folder=output_folder,
                output_filename=output_filename,
                group_column=group_column,
                include_summary=include_summary,
                sheet_prefix=sheet_prefix,
                auto_filename_from_column=auto_filename,
                skip_duplicates=True,
                separate_files=separate_files
            )
            
            # 显示结果
            if success:
                self.root.after(0, self._show_success_result)
            else:
                self.root.after(0, self._show_error_result, "处理失败")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.root.after(0, self._show_error_result, error_msg)
    
    def _show_success_result(self):
        """显示成功结果"""
        report = self.processor.get_process_report()
        self.result_text.insert(tk.END, report)
        self.result_text.insert(tk.END, "\n\n✅ 文件处理成功！")
        
        self.process_button.config(state="normal")
        self.preview_button.config(state="normal")
        self.status_var.set("处理完成")
        
        messagebox.showinfo("成功", "Excel数据处理完成！")
    
    def _show_error_result(self, error_msg):
        """显示错误结果"""
        self.result_text.insert(tk.END, f"❌ {error_msg}\n")
        
        self.process_button.config(state="normal")
        self.preview_button.config(state="normal")
        self.status_var.set("处理失败")
        
        messagebox.showerror("错误", error_msg)
    
    def preview_data(self):
        """预览数据"""
        input_file = self.input_file_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请先选择输入文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        try:
            # 读取文件
            df = self.processor.read_excel_file(input_file)
            
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
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, preview_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览数据失败: {str(e)}")
    
    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)


def main():
    """主函数"""
    root = tk.Tk()
    app = ExcelDataProcessorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
