# -*- coding: utf-8 -*-
"""
GameTools 首页/仪表盘页面
提供工具概览和快捷入口
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict
from datetime import datetime

from gui.pages.base_page import ModernPage


class HomePage(ModernPage):
    """首页/仪表盘页面"""
    
    PAGE_KEY = "home"
    PAGE_TITLE = "欢迎使用 GameTools"
    PAGE_ICON = "🏠"
    PAGE_DESCRIPTION = "游戏策划本地化工具集"
    
    def __init__(self, parent, app, theme, on_navigate: Callable[[str], None] = None):
        self.on_navigate = on_navigate
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建首页控件"""
        # 快捷入口区域
        self._create_quick_actions()
        
        # 工具分类
        self._create_tool_categories()
        
        # 底部信息
        self._create_info_section()
    
    def _create_quick_actions(self):
        """创建快捷入口"""
        section = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        section.pack(fill=tk.X, pady=(0, 24))
        
        # 标题
        title = tk.Label(
            section,
            text="⚡ 快捷入口",
            font=self.theme.FONTS["heading"],
            bg=self.theme.colors["bg_main"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 快捷按钮网格
        grid = tk.Frame(section, bg=self.theme.colors["bg_main"])
        grid.pack(fill=tk.X)
        
        quick_tools = [
            ("batch_modifier", "⚡ 批量改表", "批量修改Excel配置", self.theme.colors["primary"]),
            ("json_detector", "🔍 JSON检测", "检测JSON格式错误", self.theme.colors["info"]),
            ("field_extractor", "📋 字段导出", "提取本地化字段", self.theme.colors["success"]),
            ("csv_converter", "📄 Excel转CSV", "批量转换格式", self.theme.colors["warning"]),
        ]
        
        for i, (key, title, desc, color) in enumerate(quick_tools):
            self._create_quick_card(grid, key, title, desc, color, i)
    
    def _create_quick_card(self, parent, key: str, title: str, 
                           desc: str, accent_color: str, index: int):
        """创建快捷入口卡片"""
        card = tk.Frame(
            parent,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1,
            cursor="hand2"
        )
        card.grid(row=0, column=index, padx=(0, 12) if index < 3 else 0, sticky="nsew")
        parent.columnconfigure(index, weight=1)
        
        # 顶部色条
        accent = tk.Frame(card, bg=accent_color, height=4)
        accent.pack(fill=tk.X)
        
        # 内容
        content = tk.Frame(card, bg=self.theme.colors["bg_card"])
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        title_label = tk.Label(
            content,
            text=title,
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X)
        
        desc_label = tk.Label(
            content,
            text=desc,
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_secondary"],
            anchor=tk.W
        )
        desc_label.pack(fill=tk.X, pady=(4, 0))
        
        # 绑定点击事件
        def on_click(e, k=key):
            if self.on_navigate:
                self.on_navigate(k)
        
        for widget in [card, content, title_label, desc_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", lambda e, c=card: c.configure(
                highlightbackground=accent_color))
            widget.bind("<Leave>", lambda e, c=card: c.configure(
                highlightbackground=self.theme.colors["border"]))
    
    def _create_tool_categories(self):
        """创建工具分类区域"""
        section = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        section.pack(fill=tk.BOTH, expand=True, pady=(0, 24))
        
        # 两列布局
        section.columnconfigure(0, weight=1)
        section.columnconfigure(1, weight=1)
        
        # 左列：Excel 处理工具
        self._create_category_card(
            section, 0, 0,
            "📊 Excel 处理工具",
            [
                ("batch_modifier", "⚡", "批量改表", "批量修改Excel配置"),
                ("field_extractor", "📋", "字段导出", "提取本地化字段"),
                ("sheet_splitter", "✂️", "分页拆分", "按首列创建分页"),
                ("config_sync", "🔗", "配置同步", "同步Excel配置"),
                ("csv_converter", "📄", "Excel转CSV", "批量转换格式"),
                ("excel_processor", "📊", "数据处理", "A列分组拆分"),
            ]
        )
        
        # 右列：翻译 & 检测工具
        self._create_category_card(
            section, 0, 1,
            "🌐 翻译 & 检测工具",
            [
                ("cross_project", "🔄", "跨项目翻译", "翻译映射对照"),
                ("table_range", "🌐", "多语言提取", "按配置提取翻译"),
                ("json_detector", "🔍", "JSON检测", "检测格式错误"),
            ]
        )
    
    def _create_category_card(self, parent, row: int, col: int, 
                              title: str, tools: List[tuple]):
        """创建工具分类卡片"""
        card = tk.Frame(
            parent,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.grid(row=row, column=col, padx=(0, 12) if col == 0 else 0, 
                  sticky="nsew", pady=(0, 0))
        
        # 标题
        header = tk.Frame(card, bg=self.theme.colors["bg_card"])
        header.pack(fill=tk.X, padx=16, pady=(16, 12))
        
        title_label = tk.Label(
            header,
            text=title,
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title_label.pack(fill=tk.X)
        
        # 工具列表
        for key, icon, name, desc in tools:
            self._create_tool_item(card, key, icon, name, desc)
        
        # 底部间距
        tk.Frame(card, bg=self.theme.colors["bg_card"], height=8).pack()
    
    def _create_tool_item(self, parent, key: str, icon: str, 
                          name: str, desc: str):
        """创建工具项"""
        item = tk.Frame(
            parent,
            bg=self.theme.colors["bg_card"],
            cursor="hand2"
        )
        item.pack(fill=tk.X, padx=12, pady=2)
        
        inner = tk.Frame(item, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.X, padx=4, pady=6)
        
        # 图标
        icon_label = tk.Label(
            inner,
            text=icon,
            font=("Segoe UI Emoji", 14),
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=2
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 文本
        text_frame = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        name_label = tk.Label(
            text_frame,
            text=name,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        name_label.pack(fill=tk.X)
        
        desc_label = tk.Label(
            text_frame,
            text=desc,
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        )
        desc_label.pack(fill=tk.X)
        
        # 箭头
        arrow = tk.Label(
            inner,
            text="›",
            font=("Microsoft YaHei", 14),
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"]
        )
        arrow.pack(side=tk.RIGHT)
        
        # 绑定事件
        def on_click(e, k=key):
            if self.on_navigate:
                self.on_navigate(k)
        
        def on_enter(e):
            item.configure(bg=self.theme.colors["bg_hover"])
            for child in [inner, icon_label, text_frame, name_label, desc_label, arrow]:
                child.configure(bg=self.theme.colors["bg_hover"])
        
        def on_leave(e):
            item.configure(bg=self.theme.colors["bg_card"])
            for child in [inner, icon_label, text_frame, name_label, desc_label, arrow]:
                child.configure(bg=self.theme.colors["bg_card"])
        
        for widget in [item, inner, icon_label, text_frame, name_label, desc_label, arrow]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def _create_info_section(self):
        """创建底部信息区域"""
        section = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        section.pack(fill=tk.X)
        
        # 提示信息
        info_card = tk.Frame(
            section,
            bg=self.theme.colors["primary_light"],
            highlightbackground=self.theme.colors["primary"],
            highlightthickness=1
        )
        info_card.pack(fill=tk.X)
        
        content = tk.Frame(info_card, bg=self.theme.colors["primary_light"])
        content.pack(fill=tk.X, padx=16, pady=12)
        
        icon_label = tk.Label(
            content,
            text="💡",
            font=("Segoe UI Emoji", 16),
            bg=self.theme.colors["primary_light"]
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 12))
        
        text_label = tk.Label(
            content,
            text="提示：点击左侧导航栏选择功能，或使用快捷入口快速访问常用工具。所有操作都会在状态栏显示进度。",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["primary_light"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W,
            wraplength=600
        )
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
