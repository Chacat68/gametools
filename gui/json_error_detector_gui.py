#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON错误检测工具 - 图形界面版本
基于tkinter的GUI界面，用于检测JSON文件中的各种错误
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path

# 添加父目录到路径，以便导入json_error_detector模块
sys.path.append(str(Path(__file__).parent.parent))

from tools.json_error_detector.json_error_detector import JSONErrorDetector


class JSONErrorDetectorGUI:
    """JSON错误检测工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JSON错误检测工具")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        self.create_widgets()
        
        # 初始化检测器
        self.detector = JSONErrorDetector()
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="JSON错误检测工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 描述
        desc_label = ttk.Label(main_frame, 
                              text="检测JSON文件或文件夹中的语法错误、结构错误、数据类型错误、编码错误和性能问题",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(0, 20))
        
        # 路径选择区域
        path_frame = ttk.LabelFrame(main_frame, text="路径选择", padding="10")
        path_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        # 路径输入
        ttk.Label(path_frame, text="路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 浏览按钮
        self.browse_button = ttk.Button(path_frame, text="浏览文件夹", command=self.browse_folder)
        self.browse_button.grid(row=0, column=2)
        
        # 检测模式选择
        mode_frame = ttk.Frame(path_frame)
        mode_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        self.mode_var = tk.StringVar(value="auto")
        ttk.Radiobutton(mode_frame, text="自动检测", variable=self.mode_var, value="auto").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="仅检测文件", variable=self.mode_var, value="file").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="仅检测文件夹", variable=self.mode_var, value="folder").pack(side=tk.LEFT)
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))
        
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
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    height=25)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_folder(self):
        """浏览文件夹对话框"""
        folder_path = filedialog.askdirectory(
            title="选择包含JSON文件的文件夹"
        )
        if folder_path:
            self.path_var.set(folder_path)
            
    def start_detection(self):
        """开始检测"""
        path = self.path_var.get().strip()
        mode = self.mode_var.get()
        
        if not path:
            messagebox.showerror("错误", "请选择路径")
            return
            
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在")
            return
        
        # 在新线程中执行检测，避免界面卡顿
        self.detect_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._detect_errors, args=(path, mode))
        thread.daemon = True
        thread.start()
        
    def _detect_errors(self, path, mode):
        """检测错误（在后台线程中执行）"""
        try:
            # 根据模式选择检测方法
            if mode == "folder" or (mode == "auto" and os.path.isdir(path)):
                report = self.detector.detect_errors_in_folder(path)
            else:
                report = self.detector.detect_errors(path)
            
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
    
    app = JSONErrorDetectorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
