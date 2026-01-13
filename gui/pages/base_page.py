# -*- coding: utf-8 -*-
"""
GameTools 现代化页面基类
所有功能页面都继承此类
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Callable, Optional, Any, Dict
from pathlib import Path


class ModernPage(tk.Frame):
    """现代化页面基类"""
    
    # 页面配置（子类需要覆盖）
    PAGE_KEY = ""
    PAGE_TITLE = ""
    PAGE_ICON = ""
    PAGE_DESCRIPTION = ""
    
    def __init__(self, parent, app, theme):
        """
        初始化页面
        
        Args:
            parent: 父容器
            app: 主应用实例
            theme: ModernTheme 主题实例
        """
        super().__init__(parent)
        self.app = app
        self.theme = theme
        self.is_initialized = False
        
        # 配置背景
        self.configure(bg=theme.colors["bg_main"])
        
        # 延迟初始化（首次显示时才创建UI）
        self._init_placeholder()
    
    def _init_placeholder(self):
        """创建占位符（延迟加载时显示）"""
        self.placeholder = tk.Label(
            self,
            text=f"{self.PAGE_ICON}\n\n加载中...",
            font=("Microsoft YaHei", 14),
            bg=self.theme.colors["bg_main"],
            fg=self.theme.colors["text_muted"]
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def initialize(self):
        """初始化页面UI（延迟调用）"""
        if self.is_initialized:
            return
        
        # 移除占位符
        if hasattr(self, 'placeholder'):
            self.placeholder.destroy()
        
        # 创建页面内容
        self._create_header()
        self._create_content()
        
        self.is_initialized = True
    
    def _create_header(self):
        """创建页面头部"""
        header = tk.Frame(self, bg=self.theme.colors["bg_main"])
        header.pack(fill=tk.X, padx=24, pady=(24, 16))
        
        # 标题行
        title_row = tk.Frame(header, bg=self.theme.colors["bg_main"])
        title_row.pack(fill=tk.X)
        
        # 图标和标题
        icon_label = tk.Label(
            title_row,
            text=self.PAGE_ICON,
            font=("Segoe UI Emoji", 24),
            bg=self.theme.colors["bg_main"],
            fg=self.theme.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
        
        title_text = tk.Frame(title_row, bg=self.theme.colors["bg_main"])
        title_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = tk.Label(
            title_text,
            text=self.PAGE_TITLE,
            font=self.theme.FONTS["title"],
            bg=self.theme.colors["bg_main"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X)
        
        if self.PAGE_DESCRIPTION:
            desc_label = tk.Label(
                title_text,
                text=self.PAGE_DESCRIPTION,
                font=self.theme.FONTS["small"],
                bg=self.theme.colors["bg_main"],
                fg=self.theme.colors["text_secondary"],
                anchor=tk.W
            )
            desc_label.pack(fill=tk.X, pady=(4, 0))
    
    def _create_content(self):
        """创建页面内容（子类需要覆盖）"""
        # 内容区域容器
        self.content = tk.Frame(self, bg=self.theme.colors["bg_main"])
        self.content.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        # 子类实现具体内容
        self.create_widgets()
    
    def create_widgets(self):
        """创建页面控件（子类必须实现）"""
        raise NotImplementedError("子类必须实现 create_widgets 方法")
    
    # ==================== 状态更新方法 ====================
    
    def update_status(self, message: str, status_type: str = "normal"):
        """更新状态栏"""
        if hasattr(self.app, 'status_bar'):
            self.app.status_bar.set_status(message, status_type)
    
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
        """浏览选择文件"""
        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath and var:
            var.set(filepath)
        return filepath or ""
    
    def browse_files(self, title: str, filetypes: list) -> tuple:
        """浏览选择多个文件"""
        return filedialog.askopenfilenames(title=title, filetypes=filetypes)
    
    def browse_directory(self, title: str, var: tk.StringVar = None) -> str:
        """浏览选择目录"""
        dirpath = filedialog.askdirectory(title=title)
        if dirpath and var:
            var.set(dirpath)
        return dirpath or ""
    
    def save_file(self, title: str, filetypes: list, 
                  defaultextension: str = "", var: tk.StringVar = None) -> str:
        """保存文件对话框"""
        filepath = filedialog.asksaveasfilename(
            title=title, 
            filetypes=filetypes,
            defaultextension=defaultextension
        )
        if filepath and var:
            var.set(filepath)
        return filepath or ""
    
    # ==================== 线程执行方法 ====================
    
    def run_in_thread(self, target: Callable, callback: Callable = None, 
                      error_callback: Callable = None):
        """
        在后台线程中执行任务
        
        Args:
            target: 要执行的函数
            callback: 成功后的回调函数
            error_callback: 错误时的回调函数
        """
        def wrapper():
            try:
                result = target()
                if callback:
                    self.after(0, lambda: callback(result))
            except Exception as e:
                if error_callback:
                    self.after(0, lambda: error_callback(e))
                else:
                    self.after(0, lambda: self.show_error("错误", str(e)))
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        return thread
    
    # ==================== 辅助方法 ====================
    
    def create_card(self, parent, title: str = "", padding: int = 16) -> tk.Frame:
        """创建卡片容器"""
        from gui.components.widgets import ModernCard
        return ModernCard(parent, self.theme, title=title, padding=padding)
    
    def create_button(self, parent, text: str, command: Callable = None,
                      icon: str = "", style: str = "primary"):
        """创建按钮"""
        from gui.components.widgets import ModernButton
        return ModernButton(parent, self.theme, text, command, icon, style)
    
    def create_entry(self, parent, placeholder: str = "",
                     browse_text: str = "", browse_command: Callable = None):
        """创建输入框"""
        from gui.components.widgets import ModernEntry
        return ModernEntry(parent, self.theme, placeholder, browse_text, browse_command)
    
    def create_progress(self, parent, show_label: bool = True):
        """创建进度条"""
        from gui.components.widgets import ModernProgress
        return ModernProgress(parent, self.theme, show_label)
    
    def create_textarea(self, parent, height: int = 10, readonly: bool = False):
        """创建文本区域"""
        from gui.components.widgets import ModernTextArea
        return ModernTextArea(parent, self.theme, height, readonly)
