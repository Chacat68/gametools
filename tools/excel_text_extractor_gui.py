#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文本提取器 - 图形界面版本
检测目录中的Excel文件，提取文本内容并创建同名的新Excel文件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from tools.excel_text_extractor import ExcelTextExtractor


class ExcelTextExtractorGUI:
    """Excel文本提取器图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("翻译提取")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化提取器
        self.text_extractor = ExcelTextExtractor()
    
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
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="翻译提取", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 目录选择框架
        dir_frame = ttk.LabelFrame(main_frame, text="目录选择", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        # 输入目录
        ttk.Label(dir_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(dir_frame, textvariable=self.input_var, width=50)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.input_browse_button = ttk.Button(dir_frame, text="浏览", 
                                            command=self.browse_input_directory)
        self.input_browse_button.grid(row=0, column=2)
        
        # 输出目录
        ttk.Label(dir_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(dir_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        self.output_browse_button = ttk.Button(dir_frame, text="浏览", 
                                             command=self.browse_output_directory)
        self.output_browse_button.grid(row=1, column=2, pady=(10, 0))
        
        # 选项设置框架
        options_frame = ttk.LabelFrame(main_frame, text="提取选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 递归扫描选项
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(options_frame, text="递归扫描子目录", 
                                             variable=self.recursive_var)
        self.recursive_check.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        # 文本类型过滤
        ttk.Label(options_frame, text="文本类型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.text_type_var = tk.StringVar(value="全部")
        text_type_combo = ttk.Combobox(options_frame, textvariable=self.text_type_var, 
                                      values=["全部", "中文", "英文", "中英混合"], state="readonly", width=15)
        text_type_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="开始提取", 
                                        command=self.start_extraction, 
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空结果", 
                                     command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_button = ttk.Button(button_frame, text="预览文件", 
                                        command=self.preview_files,
                                        state="disabled")
        self.preview_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="提取结果", padding="10")
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
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
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_input_directory(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择包含Excel文件的目录")
        if directory:
            self.input_var.set(directory)
            # 自动设置输出目录为输入目录
            if not self.output_var.get():
                self.output_var.set(directory)
    
    def browse_output_directory(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_var.set(directory)
    
    def start_extraction(self):
        """开始文本提取"""
        input_dir = self.input_var.get().strip()
        output_dir = self.output_var.get().strip()
        
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
        self.process_button.config(state="disabled")
        self.status_var.set("正在提取文本...")
        
        thread = threading.Thread(target=self._extraction, 
                                 args=(input_dir, output_dir))
        thread.daemon = True
        thread.start()
    
    def _extraction(self, input_dir, output_dir):
        """文本提取（后台线程）"""
        try:
            # 清空结果
            self.root.after(0, self.clear_results)
            
            # 开始提取
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                f"开始扫描目录: {input_dir}\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                f"输出目录: {output_dir}\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                "支持的格式: .xlsx, .xls\n"))
            self.root.after(0, lambda: self.result_text.insert(tk.END, 
                "-" * 50 + "\n"))
            
            # 执行提取
            success = self.text_extractor.process_directory(input_dir, output_dir)
            
            # 显示结果
            if success:
                self.root.after(0, self._show_success_result)
            else:
                self.root.after(0, self._show_error_result, "提取失败")
            
        except Exception as e:
            error_msg = f"提取过程中发生错误: {str(e)}"
            self.root.after(0, self._show_error_result, error_msg)
    
    def _show_success_result(self):
        """显示提取成功结果"""
        report = self.text_extractor.get_processing_report()
        self.result_text.insert(tk.END, report)
        self.result_text.insert(tk.END, "\n\n✅ Excel文本提取完成！")
        
        self.process_button.config(state="normal")
        self.preview_button.config(state="normal")
        self.status_var.set("文本提取完成")
        
        messagebox.showinfo("成功", "Excel文本提取完成！")
    
    def _show_error_result(self, error_msg):
        """显示提取错误结果"""
        self.result_text.insert(tk.END, f"❌ {error_msg}\n")
        
        self.process_button.config(state="normal")
        self.preview_button.config(state="normal")
        self.status_var.set("文本提取失败")
        
        messagebox.showerror("错误", error_msg)
    
    def preview_files(self):
        """预览Excel文件"""
        input_dir = self.input_var.get().strip()
        
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
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, preview_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览文件失败: {str(e)}")
    
    def clear_results(self):
        """清空提取结果"""
        self.result_text.delete(1.0, tk.END)


def main():
    """主函数"""
    root = tk.Tk()
    app = ExcelTextExtractorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
