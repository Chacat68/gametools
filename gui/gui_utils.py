# -*- coding: utf-8 -*-
"""
GUI 公共工具模块
提供通用的UI组件和辅助方法
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import Callable, Optional, List, Tuple, Any


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


# ==================== 文件浏览方法 ====================

def browse_file(title: str, filetypes: list, var: tk.StringVar = None) -> str:
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
    return filepath or ""


def browse_files(title: str, filetypes: list) -> tuple:
    """浏览选择多个文件"""
    return filedialog.askopenfilenames(title=title, filetypes=filetypes)


def browse_directory(title: str, var: tk.StringVar = None) -> str:
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
    return directory or ""


def browse_save_file(title: str, filetypes: list, 
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
    return filepath or ""


# ==================== UI组件创建方法 ====================

def create_file_selector(parent, label_text: str, var: tk.StringVar,
                        browse_command: Callable, row: int, 
                        entry_width: int = None) -> ttk.Entry:
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


def create_labeled_frame(parent, text: str, row: int, 
                        pady: tuple = (0, 8), padding: str = "8") -> ttk.LabelFrame:
    """
    创建带标题的框架
    
    Args:
        parent: 父容器
        text: 框架标题
        row: 行号
        pady: 垂直内边距
        padding: 内边距
        
    Returns:
        创建的LabelFrame
    """
    frame = ttk.LabelFrame(parent, text=text, padding=padding)
    frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=pady)
    frame.columnconfigure(1, weight=1)
    return frame


def create_action_buttons(parent, buttons: List[Tuple], row: int) -> ttk.Frame:
    """
    创建操作按钮组
    
    Args:
        parent: 父容器
        buttons: 按钮配置列表 [(text, command, style), ...]
        row: 行号
        
    Returns:
        按钮所在的Frame
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


def create_result_viewer(parent, row: int, height: int = 15) -> scrolledtext.ScrolledText:
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


def create_checkbox_option(parent, text: str, var: tk.BooleanVar, 
                          row: int, column: int = 0) -> ttk.Checkbutton:
    """
    创建复选框选项
    
    Args:
        parent: 父容器
        text: 显示文本
        var: 绑定的BooleanVar
        row: 行号
        column: 列号
        
    Returns:
        创建的Checkbutton
    """
    cb = ttk.Checkbutton(parent, text=text, variable=var)
    cb.grid(row=row, column=column, sticky=tk.W, padx=5, pady=2)
    return cb


def create_combobox(parent, label_text: str, values: list, var: tk.StringVar,
                   row: int, width: int = 20) -> ttk.Combobox:
    """
    创建下拉选择框
    
    Args:
        parent: 父容器
        label_text: 标签文本
        values: 选项列表
        var: 绑定的StringVar
        row: 行号
        width: 宽度
        
    Returns:
        创建的Combobox
    """
    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=(0, 8), pady=2)
    
    combo = ttk.Combobox(parent, textvariable=var, values=values, width=width, state="readonly")
    combo.grid(row=row, column=1, sticky=tk.W, pady=2)
    
    if values:
        combo.current(0)
    
    return combo


# ==================== 线程辅助方法 ====================

def run_in_thread(root: tk.Tk, target: Callable, args: tuple = (), 
                  kwargs: dict = None, on_complete: Callable = None, 
                  on_error: Callable = None) -> threading.Thread:
    """
    在后台线程中运行任务
    
    Args:
        root: Tk根窗口，用于调度主线程回调
        target: 目标函数
        args: 位置参数
        kwargs: 关键字参数
        on_complete: 完成回调（在主线程执行），接收结果参数
        on_error: 错误回调（在主线程执行），接收异常参数
        
    Returns:
        启动的线程对象
    """
    if kwargs is None:
        kwargs = {}
    
    def wrapper():
        try:
            result = target(*args, **kwargs)
            if on_complete:
                root.after(0, lambda: on_complete(result))
        except Exception as e:
            if on_error:
                root.after(0, lambda: on_error(e))
            else:
                root.after(0, lambda: messagebox.showerror("错误", str(e)))
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return thread


# ==================== 对话框辅助方法 ====================

def show_results_dialog(parent: tk.Tk, title: str, content: str, 
                       width: int = 800, height: int = 600):
    """
    显示结果查看对话框
    
    Args:
        parent: 父窗口
        title: 对话框标题
        content: 显示内容
        width: 窗口宽度
        height: 窗口高度
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.transient(parent)
    
    # 创建文本区域
    text_frame = ttk.Frame(dialog, padding="10")
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, content)
    text_widget.config(state=tk.DISABLED)
    
    # 关闭按钮
    ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)
    
    # 居中显示
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
    y = parent.winfo_y() + (parent.winfo_height() - height) // 2
    dialog.geometry(f"+{x}+{y}")


def confirm_action(title: str, message: str) -> bool:
    """
    显示确认对话框
    
    Args:
        title: 对话框标题
        message: 确认消息
        
    Returns:
        用户是否确认
    """
    return messagebox.askyesno(title, message)


def show_info(title: str, message: str):
    """显示信息对话框"""
    messagebox.showinfo(title, message)


def show_warning(title: str, message: str):
    """显示警告对话框"""
    messagebox.showwarning(title, message)


def show_error(title: str, message: str):
    """显示错误对话框"""
    messagebox.showerror(title, message)
