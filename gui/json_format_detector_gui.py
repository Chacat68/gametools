#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON格式检测工具 - 图形界面版本
基于tkinter的GUI界面，用于检测JSON文件中text字段的格式一致性
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path

# 添加父目录到路径，以便导入json_format_detector模块
sys.path.append(str(Path(__file__).parent.parent))

from json_format_detector.json_format_detector import JSONFormatDetector


class JSONFormatDetectorGUI:
    """JSON格式检测工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JSON格式检测工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        self.create_widgets()
        
        # 初始化检测器
        self.detector = JSONFormatDetector()
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="JSON格式检测工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # JSON文件路径
        ttk.Label(file_frame, text="JSON文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)
        
        # 字段名设置
        ttk.Label(file_frame, text="检测字段:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.text_key_var = tk.StringVar(value="text")
        self.text_key_entry = ttk.Entry(file_frame, textvariable=self.text_key_var, width=20)
        self.text_key_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        self.detect_button = ttk.Button(button_frame, text="开始检测", 
                                       command=self.start_detection, style="Accent.TButton")
        self.detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空结果", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="保存报告", 
                                     command=self.save_report, state="disabled")
        self.save_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="检测结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    height=20)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_file(self):
        """浏览文件对话框"""
        file_path = filedialog.askopenfilename(
            title="选择JSON文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            
    def start_detection(self):
        """开始检测"""
        file_path = self.file_path_var.get().strip()
        text_key = self.text_key_var.get().strip()
        
        if not file_path:
            messagebox.showerror("错误", "请选择JSON文件")
            return
            
        if not text_key:
            messagebox.showerror("错误", "请输入检测字段名")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 在新线程中执行检测，避免界面卡顿
        self.detect_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._detect_format, args=(file_path, text_key))
        thread.daemon = True
        thread.start()
        
    def _detect_format(self, file_path, text_key):
        """检测格式（在后台线程中执行）"""
        try:
            report = self.detector.detect_format(file_path, text_key)
            
            # 在主线程中更新UI
            self.root.after(0, self._update_results, report)
            
        except Exception as e:
            error_msg = f"检测过程中发生错误: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
            
    def _update_results(self, report):
        """更新结果显示"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, report)
        self.result_text.see(1.0)
        
        self.detect_button.config(state="normal")
        self.save_button.config(state="normal")
        self.progress.stop()
        self.status_var.set("检测完成")
        
    def _show_error(self, error_msg):
        """显示错误信息"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, error_msg)
        
        self.detect_button.config(state="normal")
        self.progress.stop()
        self.status_var.set("检测失败")
        
        messagebox.showerror("错误", error_msg)
        
    def clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
        self.save_button.config(state="disabled")
        self.status_var.set("就绪")
        
    def save_report(self):
        """保存报告"""
        content = self.result_text.get(1.0, tk.END).strip()
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


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置主题样式
    style = ttk.Style()
    try:
        style.theme_use('clam')  # 使用现代主题
    except:
        pass
    
    app = JSONFormatDetectorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
