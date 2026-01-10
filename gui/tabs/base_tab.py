# -*- coding: utf-8 -*-
"""
GUI标签页基础类
提供共用的浏览、状态更新、线程执行等方法
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path


class BaseTab:
    """标签页基础类，提供共用功能"""
    
    def __init__(self, parent_app, notebook: ttk.Notebook, tab_name: str):
        """
        初始化标签页
        
        Args:
            parent_app: 父应用实例（GameToolsUnified）
            notebook: ttk.Notebook实例
            tab_name: 标签页显示名称
        """
        self.app = parent_app
        self.notebook = notebook
        self.tab_name = tab_name
        
        # 创建标签页框架
        self.frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame, text=tab_name)
        
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # 子类实现的结果存储键名
        self.result_key = None
        
        # 创建UI
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面控件 - 子类必须重写"""
        raise NotImplementedError("子类必须实现 create_widgets 方法")
    
    # ==================== 状态更新方法 ====================
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.app.status_var.set(message)
        self.app.root.update_idletasks()
    
    def show_info(self, title: str, message: str):
        """显示信息对话框"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """显示警告对话框"""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """显示错误对话框"""
        messagebox.showerror(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """显示确认对话框"""
        return messagebox.askyesno(title, message)
    
    # ==================== 文件浏览方法 ====================
    
    def browse_file(self, title: str, filetypes: list, var: tk.StringVar = None) -> str:
        """
        浏览选择文件
        
        Args:
            title: 对话框标题
            filetypes: 文件类型过滤器，如 [("Excel文件", "*.xlsx;*.xls")]
            var: 可选的StringVar，自动设置选中的路径
            
        Returns:
            选中的文件路径，取消返回空字符串
        """
        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath and var:
            var.set(filepath)
        return filepath
    
    def browse_files(self, title: str, filetypes: list) -> tuple:
        """浏览选择多个文件"""
        return filedialog.askopenfilenames(title=title, filetypes=filetypes)
    
    def browse_directory(self, title: str, var: tk.StringVar = None) -> str:
        """
        浏览选择目录
        
        Args:
            title: 对话框标题
            var: 可选的StringVar，自动设置选中的路径
            
        Returns:
            选中的目录路径，取消返回空字符串
        """
        directory = filedialog.askdirectory(title=title)
        if directory and var:
            var.set(directory)
        return directory
    
    def browse_save_file(self, title: str, filetypes: list, 
                         defaultextension: str = None, var: tk.StringVar = None) -> str:
        """
        浏览保存文件位置
        
        Args:
            title: 对话框标题
            filetypes: 文件类型过滤器
            defaultextension: 默认扩展名
            var: 可选的StringVar，自动设置选中的路径
            
        Returns:
            选中的保存路径，取消返回空字符串
        """
        filepath = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=defaultextension
        )
        if filepath and var:
            var.set(filepath)
        return filepath
    
    # ==================== 线程执行方法 ====================
    
    def run_in_thread(self, target, args=(), kwargs=None, 
                      on_complete=None, on_error=None):
        """
        在后台线程中运行任务
        
        Args:
            target: 目标函数
            args: 位置参数
            kwargs: 关键字参数
            on_complete: 完成回调（在主线程执行）
            on_error: 错误回调（在主线程执行）
        """
        if kwargs is None:
            kwargs = {}
        
        def wrapper():
            try:
                result = target(*args, **kwargs)
                if on_complete:
                    self.app.root.after(0, lambda: on_complete(result))
            except Exception as e:
                if on_error:
                    self.app.root.after(0, lambda: on_error(e))
                else:
                    self.app.root.after(0, lambda: self.show_error("错误", str(e)))
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        return thread
    
    # ==================== 结果存储方法 ====================
    
    def store_result(self, result: str):
        """存储结果到应用的结果存储字典"""
        if self.result_key and self.result_key in self.app.results_storage:
            self.app.results_storage[self.result_key] = result
    
    def get_stored_result(self) -> str:
        """获取存储的结果"""
        if self.result_key and self.result_key in self.app.results_storage:
            return self.app.results_storage[self.result_key]
        return ""
    
    # ==================== UI辅助方法 ====================
    
    def create_file_selector(self, parent, label_text: str, var: tk.StringVar,
                            browse_command, row: int, entry_width: int = None) -> ttk.Entry:
        """
        创建文件选择器（标签 + 输入框 + 浏览按钮）
        
        Args:
            parent: 父容器
            label_text: 标签文本
            var: 绑定的StringVar
            browse_command: 浏览按钮命令
            row: 行号
            entry_width: 输入框宽度（可选）
            
        Returns:
            创建的Entry控件
        """
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        
        entry = ttk.Entry(parent, textvariable=var)
        if entry_width:
            entry.config(width=entry_width)
        entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        
        ttk.Button(parent, text="浏览", command=browse_command).grid(
            row=row, column=2, sticky=tk.E, pady=2
        )
        
        return entry
    
    def create_labeled_frame(self, parent, text: str, row: int, 
                            pady: tuple = (0, 8)) -> ttk.LabelFrame:
        """
        创建带标题的框架
        
        Args:
            parent: 父容器
            text: 框架标题
            row: 行号
            pady: 垂直内边距
            
        Returns:
            创建的LabelFrame
        """
        frame = ttk.LabelFrame(parent, text=text, padding="8")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=pady)
        frame.columnconfigure(1, weight=1)
        return frame
    
    def create_action_buttons(self, parent, buttons: list, row: int):
        """
        创建操作按钮组
        
        Args:
            parent: 父容器
            buttons: 按钮配置列表 [(text, command, style), ...]
            row: 行号
        """
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, pady=(8, 0))
        
        for i, btn_config in enumerate(buttons):
            text = btn_config[0]
            command = btn_config[1]
            style = btn_config[2] if len(btn_config) > 2 else None
            
            btn = ttk.Button(button_frame, text=text, command=command)
            if style:
                btn.configure(style=style)
            btn.grid(row=0, column=i, padx=5)
        
        return button_frame
    
    def create_result_viewer(self, parent, row: int, height: int = 15) -> scrolledtext.ScrolledText:
        """
        创建结果查看区域
        
        Args:
            parent: 父容器
            row: 行号
            height: 高度（行数）
            
        Returns:
            创建的ScrolledText控件
        """
        result_frame = ttk.LabelFrame(parent, text="结果", padding="5")
        result_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(8, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        result_text = scrolledtext.ScrolledText(result_frame, height=height, wrap=tk.WORD)
        result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        return result_text
    
    # ==================== 常用文件类型 ====================
    
    EXCEL_FILETYPES = [("Excel文件", "*.xlsx;*.xls"), ("所有文件", "*.*")]
    JSON_FILETYPES = [("JSON文件", "*.json"), ("所有文件", "*.*")]
    CSV_FILETYPES = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
    MAPPING_FILETYPES = [
        ("映射文件", "*.xlsx;*.xls;*.csv"),
        ("Excel文件", "*.xlsx;*.xls"),
        ("CSV文件", "*.csv"),
        ("所有文件", "*.*")
    ]
