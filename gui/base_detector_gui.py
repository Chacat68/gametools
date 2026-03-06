#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测工具GUI基类
提供公共的UI组件和方法，供各种检测工具GUI继承使用
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from abc import ABC, abstractmethod

try:
    from .ui_theme import apply_ui_theme
except ImportError:
    from gui.ui_theme import apply_ui_theme


class BaseDetectorGUI(ABC):
    """检测工具GUI基类"""
    
    def __init__(self, root, title="检测工具", geometry="800x600", min_size=(600, 400)):
        self.root = root
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.minsize(*min_size)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        self.palette, self.style = apply_ui_theme(self.root)
        
        # 初始化检测器（子类实现）
        self.detector = self._create_detector()
        
        # 创建主框架
        self._create_main_frame()
        self._create_widgets()
        self._create_buttons()
        self._create_result_area()
        self._create_status_bar()
    
    @abstractmethod
    def _create_detector(self):
        """创建检测器实例（子类必须实现）"""
        pass
    
    @abstractmethod
    def _create_widgets(self):
        """创建特定的输入组件（子类必须实现）"""
        pass
    
    @abstractmethod
    def _get_detection_params(self):
        """获取检测参数，返回元组 (is_valid, params_dict, error_msg)"""
        pass
    
    @abstractmethod
    def _run_detection(self, params):
        """执行检测，返回报告字符串（子类必须实现）"""
        pass
    
    def _create_main_frame(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(self.root, padding="10", style='App.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
    
    def _create_buttons(self):
        """创建控制按钮区域"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10))
        
        self.detect_button = ttk.Button(button_frame, text="开始检测", 
                                       command=self.start_detection, style="Accent.TButton")
        self.detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清空结果", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="保存报告", 
                                     command=self.save_report, state="disabled")
        self.save_button.pack(side=tk.LEFT)
    
    def _create_result_area(self):
        """创建结果显示区域"""
        result_frame = ttk.LabelFrame(self.main_frame, text="检测结果", padding="10")
        result_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, 
                                                    wrap=tk.WORD, 
                                                    font=("Consolas", 10),
                                                    height=20,
                                                    background=self.palette['surface_alt'],
                                                    foreground=self.palette['text'],
                                                    insertbackground=self.palette['text'])
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 进度条
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def start_detection(self):
        """开始检测"""
        is_valid, params, error_msg = self._get_detection_params()
        
        if not is_valid:
            messagebox.showerror("错误", error_msg)
            return
        
        # 在新线程中执行检测，避免界面卡顿
        self.detect_button.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._detect_thread, args=(params,))
        thread.daemon = True
        thread.start()
    
    def _detect_thread(self, params):
        """检测线程"""
        try:
            report = self._run_detection(params)
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


def run_detector_gui(gui_class, title="检测工具"):
    """通用的GUI启动函数"""
    root = tk.Tk()
    
    app = gui_class(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
