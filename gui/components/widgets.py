# -*- coding: utf-8 -*-
"""
GameTools 现代化UI组件库
提供通用的现代风格UI组件
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Any


class ModernCard(tk.Frame):
    """现代卡片组件"""
    
    def __init__(self, parent, theme, title: str = "", padding: int = 16, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        self.configure(
            bg=theme.colors["bg_card"],
            highlightbackground=theme.colors["border"],
            highlightthickness=1,
            padx=padding,
            pady=padding
        )
        
        if title:
            self._create_title(title)
            # 内容区域
            self.content = tk.Frame(self, bg=theme.colors["bg_card"])
            self.content.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        else:
            self.content = self
    
    def _create_title(self, title: str):
        """创建标题区域"""
        title_label = tk.Label(
            self,
            text=title,
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X)


class ModernButton(tk.Frame):
    """现代按钮组件"""
    
    def __init__(self, parent, theme, text: str, command: Callable = None,
                 icon: str = "", style: str = "primary", **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.command = command
        self.style = style
        self._disabled = False
        
        # 根据样式设置颜色
        if style == "primary":
            self.bg_normal = theme.colors["primary"]
            self.bg_hover = theme.colors["primary_hover"]
            self.fg = "#ffffff"
        elif style == "secondary":
            self.bg_normal = theme.colors["bg_card"]
            self.bg_hover = theme.colors["bg_hover"]
            self.fg = theme.colors["text_primary"]
        elif style == "success":
            self.bg_normal = theme.colors["success"]
            self.bg_hover = "#16a34a"
            self.fg = "#ffffff"
        elif style == "danger":
            self.bg_normal = theme.colors["error"]
            self.bg_hover = "#dc2626"
            self.fg = "#ffffff"
        else:
            self.bg_normal = theme.colors["bg_hover"]
            self.bg_hover = theme.colors["border"]
            self.fg = theme.colors["text_primary"]
        
        self.configure(bg=self.bg_normal, cursor="hand2")
        
        # 内容
        display_text = f"{icon} {text}".strip() if icon else text
        self.label = tk.Label(
            self,
            text=display_text,
            font=theme.FONTS["body"],
            bg=self.bg_normal,
            fg=self.fg,
            padx=16,
            pady=8
        )
        self.label.pack()
        
        # 绑定事件
        for widget in [self, self.label]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event=None):
        if not self._disabled and self.command:
            self.command()
    
    def _on_enter(self, event=None):
        if not self._disabled:
            self.configure(bg=self.bg_hover)
            self.label.configure(bg=self.bg_hover)
    
    def _on_leave(self, event=None):
        if not self._disabled:
            self.configure(bg=self.bg_normal)
            self.label.configure(bg=self.bg_normal)
    
    def set_state(self, enabled: bool):
        """设置按钮状态"""
        self._disabled = not enabled
        if enabled:
            self.configure(cursor="hand2", bg=self.bg_normal)
            self.label.configure(bg=self.bg_normal, fg=self.fg)
        else:
            self.configure(cursor="", bg=self.theme.colors["bg_hover"])
            self.label.configure(
                bg=self.theme.colors["bg_hover"],
                fg=self.theme.colors["text_muted"]
            )


class ModernEntry(tk.Frame):
    """现代输入框组件"""
    
    def __init__(self, parent, theme, placeholder: str = "",
                 browse_text: str = "", browse_command: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.placeholder = placeholder
        
        self.configure(bg=theme.colors["bg_card"])
        
        # 输入框容器
        entry_container = tk.Frame(
            self,
            bg=theme.colors["bg_input"],
            highlightbackground=theme.colors["border"],
            highlightthickness=1,
            highlightcolor=theme.colors["border_focus"]
        )
        entry_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 输入框
        self.var = tk.StringVar()
        self.entry = tk.Entry(
            entry_container,
            textvariable=self.var,
            font=theme.FONTS["body"],
            bg=theme.colors["bg_input"],
            fg=theme.colors["text_primary"],
            insertbackground=theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.entry.pack(fill=tk.X, padx=10, pady=8)
        
        # 浏览按钮
        if browse_text:
            self.browse_btn = ModernButton(
                self, theme, browse_text,
                command=browse_command,
                style="secondary"
            )
            self.browse_btn.pack(side=tk.RIGHT, padx=(8, 0))
    
    def get(self) -> str:
        return self.var.get()
    
    def set(self, value: str):
        self.var.set(value)
    
    def clear(self):
        self.var.set("")


class ModernProgress(tk.Frame):
    """现代进度条组件"""
    
    def __init__(self, parent, theme, show_label: bool = True, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        self.configure(bg=theme.colors["bg_card"])
        
        if show_label:
            # 状态标签
            self.label = tk.Label(
                self,
                text="就绪",
                font=theme.FONTS["small"],
                bg=theme.colors["bg_card"],
                fg=theme.colors["text_secondary"],
                anchor=tk.W
            )
            self.label.pack(fill=tk.X, pady=(0, 4))
        else:
            self.label = None
        
        # 进度条背景
        self.track = tk.Frame(
            self,
            bg=theme.colors["bg_hover"],
            height=6
        )
        self.track.pack(fill=tk.X)
        self.track.pack_propagate(False)
        
        # 进度条填充
        self.fill = tk.Frame(
            self.track,
            bg=theme.colors["primary"],
            height=6
        )
        self.fill.place(x=0, y=0, relheight=1, relwidth=0)
    
    def set_progress(self, value: float, text: str = None):
        """设置进度（0-100）"""
        value = max(0, min(100, value))
        self.fill.place(relwidth=value/100)
        
        if text and self.label:
            self.label.configure(text=text)
    
    def set_text(self, text: str):
        """设置状态文本"""
        if self.label:
            self.label.configure(text=text)
    
    def reset(self):
        """重置进度"""
        self.fill.place(relwidth=0)
        if self.label:
            self.label.configure(text="就绪")


class ModernStatusBar(tk.Frame):
    """现代状态栏组件"""
    
    def __init__(self, parent, theme, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        self.configure(
            bg=theme.colors["bg_card"],
            height=32
        )
        self.pack_propagate(False)
        
        # 左侧状态
        self.status_label = tk.Label(
            self,
            text="就绪",
            font=theme.FONTS["small"],
            bg=theme.colors["bg_card"],
            fg=theme.colors["text_secondary"],
            padx=12
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.Y)
        
        # 右侧信息
        self.info_label = tk.Label(
            self,
            text="",
            font=theme.FONTS["small"],
            bg=theme.colors["bg_card"],
            fg=theme.colors["text_muted"],
            padx=12
        )
        self.info_label.pack(side=tk.RIGHT, fill=tk.Y)
    
    def set_status(self, text: str, status_type: str = "normal"):
        """设置状态"""
        color_map = {
            "normal": self.theme.colors["text_secondary"],
            "success": self.theme.colors["success"],
            "warning": self.theme.colors["warning"],
            "error": self.theme.colors["error"],
            "info": self.theme.colors["info"],
        }
        self.status_label.configure(
            text=text,
            fg=color_map.get(status_type, self.theme.colors["text_secondary"])
        )
    
    def set_info(self, text: str):
        """设置右侧信息"""
        self.info_label.configure(text=text)


class ModernListBox(tk.Frame):
    """现代列表框组件"""
    
    def __init__(self, parent, theme, height: int = 10, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        self.configure(
            bg=theme.colors["bg_card"],
            highlightbackground=theme.colors["border"],
            highlightthickness=1
        )
        
        # 列表区域
        self.listbox = tk.Listbox(
            self,
            font=theme.FONTS["body"],
            bg=theme.colors["bg_input"],
            fg=theme.colors["text_primary"],
            selectbackground=theme.colors["primary"],
            selectforeground="#ffffff",
            relief=tk.FLAT,
            highlightthickness=0,
            height=height,
            activestyle='none'
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=scrollbar.set)
    
    def add_item(self, text: str):
        """添加项目"""
        self.listbox.insert(tk.END, text)
    
    def clear(self):
        """清空列表"""
        self.listbox.delete(0, tk.END)
    
    def get_selected(self) -> Optional[str]:
        """获取选中项"""
        selection = self.listbox.curselection()
        if selection:
            return self.listbox.get(selection[0])
        return None


class ModernTextArea(tk.Frame):
    """现代文本区域组件"""
    
    def __init__(self, parent, theme, height: int = 10, readonly: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        
        self.configure(
            bg=theme.colors["bg_card"],
            highlightbackground=theme.colors["border"],
            highlightthickness=1
        )
        
        # 文本区域
        self.text = tk.Text(
            self,
            font=theme.FONTS["mono"],
            bg=theme.colors["bg_input"],
            fg=theme.colors["text_primary"],
            insertbackground=theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0,
            height=height,
            wrap=tk.WORD,
            padx=10,
            pady=8
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if readonly:
            self.text.configure(state=tk.DISABLED)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)
    
    def get_text(self) -> str:
        """获取文本"""
        return self.text.get("1.0", tk.END).strip()
    
    def set_text(self, text: str):
        """设置文本"""
        state = self.text.cget('state')
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", text)
        self.text.configure(state=state)
    
    def append(self, text: str):
        """追加文本"""
        state = self.text.cget('state')
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, text)
        self.text.see(tk.END)
        self.text.configure(state=state)
    
    def clear(self):
        """清空文本"""
        state = self.text.cget('state')
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=state)
