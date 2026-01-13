# -*- coding: utf-8 -*-
"""
GameTools 现代化侧边栏组件
提供左侧导航栏，支持动态切换页面
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional


class SidebarItem:
    """侧边栏项目配置"""
    
    def __init__(self, key: str, title: str, icon: str, 
                 description: str = "", group: str = "main"):
        self.key = key
        self.title = title
        self.icon = icon
        self.description = description
        self.group = group


class ModernSidebar(tk.Frame):
    """现代化侧边栏组件"""
    
    def __init__(self, parent, theme, on_select: Callable[[str], None], **kwargs):
        """
        初始化侧边栏
        
        Args:
            parent: 父容器
            theme: ModernTheme 主题实例
            on_select: 选中回调函数，参数为选中项的 key
        """
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.on_select = on_select
        self.current_key = None
        self.buttons: Dict[str, tk.Frame] = {}
        
        # 配置样式
        self.configure(
            bg=theme.colors["bg_sidebar"],
            width=theme.SIZES["sidebar_width"]
        )
        self.pack_propagate(False)  # 固定宽度
        
        # 创建内部容器
        self._create_header()
        self._create_nav_container()
        self._create_footer()
    
    def _create_header(self):
        """创建顶部 Logo 区域"""
        header = tk.Frame(self, bg=self.theme.colors["bg_sidebar"])
        header.pack(fill=tk.X, padx=16, pady=20)
        
        # Logo 和标题
        title_frame = tk.Frame(header, bg=self.theme.colors["bg_sidebar"])
        title_frame.pack(fill=tk.X)
        
        # Logo 图标
        logo_label = tk.Label(
            title_frame,
            text="🎮",
            font=("Segoe UI Emoji", 24),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["primary"]
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 标题文字
        title_text = tk.Frame(title_frame, bg=self.theme.colors["bg_sidebar"])
        title_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        name_label = tk.Label(
            title_text,
            text="GameTools",
            font=("Microsoft YaHei", 14, "bold"),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_sidebar_active"]
        )
        name_label.pack(anchor=tk.W)
        
        version_label = tk.Label(
            title_text,
            text="游戏策划工具集",
            font=("Microsoft YaHei", 9),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_muted"]
        )
        version_label.pack(anchor=tk.W)
        
        # 分隔线
        separator = tk.Frame(
            self, 
            bg=self.theme.colors["sidebar_hover"],
            height=1
        )
        separator.pack(fill=tk.X, padx=16, pady=(0, 10))
    
    def _create_nav_container(self):
        """创建导航按钮容器"""
        # 滚动容器
        self.nav_container = tk.Frame(self, bg=self.theme.colors["bg_sidebar"])
        self.nav_container.pack(fill=tk.BOTH, expand=True, padx=8)
    
    def _create_footer(self):
        """创建底部区域"""
        footer = tk.Frame(self, bg=self.theme.colors["bg_sidebar"])
        footer.pack(fill=tk.X, padx=16, pady=16, side=tk.BOTTOM)
        
        # 分隔线
        separator = tk.Frame(
            footer,
            bg=self.theme.colors["sidebar_hover"],
            height=1
        )
        separator.pack(fill=tk.X, pady=(0, 12))
        
        # 版本信息
        try:
            from version import get_version
            version_text = f"v{get_version()}"
        except:
            version_text = "v1.44.0"
        
        version_label = tk.Label(
            footer,
            text=version_text,
            font=("Microsoft YaHei", 9),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_muted"]
        )
        version_label.pack(anchor=tk.W)
    
    def add_group_label(self, text: str):
        """添加分组标签"""
        label = tk.Label(
            self.nav_container,
            text=text.upper(),
            font=("Microsoft YaHei", 8, "bold"),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        )
        label.pack(fill=tk.X, padx=8, pady=(16, 6))
    
    def add_item(self, item: SidebarItem):
        """添加导航项"""
        # 创建按钮容器
        btn_frame = tk.Frame(
            self.nav_container,
            bg=self.theme.colors["bg_sidebar"],
            cursor="hand2"
        )
        btn_frame.pack(fill=tk.X, pady=2)
        
        # 内部内容区
        content = tk.Frame(btn_frame, bg=self.theme.colors["bg_sidebar"])
        content.pack(fill=tk.X, padx=8, pady=8)
        
        # 图标
        icon_label = tk.Label(
            content,
            text=item.icon,
            font=("Segoe UI Emoji", 14),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_sidebar"],
            width=2
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 标题
        title_label = tk.Label(
            content,
            text=item.title,
            font=("Microsoft YaHei", 10),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_sidebar"],
            anchor=tk.W
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 保存引用
        self.buttons[item.key] = {
            "frame": btn_frame,
            "content": content,
            "icon": icon_label,
            "title": title_label,
            "item": item
        }
        
        # 绑定点击事件
        for widget in [btn_frame, content, icon_label, title_label]:
            widget.bind("<Button-1>", lambda e, k=item.key: self._on_click(k))
            widget.bind("<Enter>", lambda e, k=item.key: self._on_enter(k))
            widget.bind("<Leave>", lambda e, k=item.key: self._on_leave(k))
    
    def _on_click(self, key: str):
        """处理点击事件"""
        if key != self.current_key:
            self.select(key)
            if self.on_select:
                self.on_select(key)
    
    def _on_enter(self, key: str):
        """鼠标进入效果"""
        if key != self.current_key:
            self._set_button_hover(key)
    
    def _on_leave(self, key: str):
        """鼠标离开效果"""
        if key != self.current_key:
            self._set_button_normal(key)
    
    def _set_button_normal(self, key: str):
        """设置按钮为普通状态"""
        btn = self.buttons.get(key)
        if btn:
            bg = self.theme.colors["bg_sidebar"]
            fg = self.theme.colors["text_sidebar"]
            btn["frame"].configure(bg=bg)
            btn["content"].configure(bg=bg)
            btn["icon"].configure(bg=bg, fg=fg)
            btn["title"].configure(bg=bg, fg=fg)
    
    def _set_button_hover(self, key: str):
        """设置按钮为悬停状态"""
        btn = self.buttons.get(key)
        if btn:
            bg = self.theme.colors["sidebar_hover"]
            fg = self.theme.colors["text_sidebar_active"]
            btn["frame"].configure(bg=bg)
            btn["content"].configure(bg=bg)
            btn["icon"].configure(bg=bg, fg=fg)
            btn["title"].configure(bg=bg, fg=fg)
    
    def _set_button_active(self, key: str):
        """设置按钮为激活状态"""
        btn = self.buttons.get(key)
        if btn:
            bg = self.theme.colors["sidebar_active"]
            fg = self.theme.colors["text_sidebar_active"]
            btn["frame"].configure(bg=bg)
            btn["content"].configure(bg=bg)
            btn["icon"].configure(bg=bg, fg=fg)
            btn["title"].configure(bg=bg, fg=fg)
    
    def select(self, key: str):
        """选中指定项"""
        # 取消之前的选中
        if self.current_key and self.current_key in self.buttons:
            self._set_button_normal(self.current_key)
        
        # 设置新选中
        self.current_key = key
        if key in self.buttons:
            self._set_button_active(key)
    
    def add_separator(self):
        """添加分隔线"""
        separator = tk.Frame(
            self.nav_container,
            bg=self.theme.colors["sidebar_hover"],
            height=1
        )
        separator.pack(fill=tk.X, padx=16, pady=8)
