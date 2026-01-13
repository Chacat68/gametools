# -*- coding: utf-8 -*-
"""
GameTools 现代主题配置
提供统一的颜色方案和样式定义
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class ThemeColors:
    """主题颜色定义"""
    
    # ========== 浅色主题 ==========
    LIGHT = {
        # 主色调
        "primary": "#2563eb",           # 蓝色主色
        "primary_hover": "#1d4ed8",     # 主色悬停
        "primary_light": "#dbeafe",     # 主色浅色背景
        
        # 背景色
        "bg_main": "#f8fafc",           # 主背景
        "bg_sidebar": "#1e293b",        # 侧边栏背景（深色）
        "bg_card": "#ffffff",           # 卡片背景
        "bg_input": "#ffffff",          # 输入框背景
        "bg_hover": "#f1f5f9",          # 悬停背景
        
        # 文字颜色
        "text_primary": "#1e293b",      # 主要文字
        "text_secondary": "#64748b",    # 次要文字
        "text_muted": "#94a3b8",        # 淡化文字
        "text_sidebar": "#e2e8f0",      # 侧边栏文字
        "text_sidebar_active": "#ffffff",
        
        # 边框颜色
        "border": "#e2e8f0",            # 边框
        "border_focus": "#2563eb",      # 聚焦边框
        
        # 状态颜色
        "success": "#22c55e",           # 成功
        "warning": "#f59e0b",           # 警告
        "error": "#ef4444",             # 错误
        "info": "#3b82f6",              # 信息
        
        # 侧边栏选中
        "sidebar_active": "#3b82f6",
        "sidebar_hover": "#334155",
    }
    
    # ========== 深色主题 ==========
    DARK = {
        "primary": "#3b82f6",
        "primary_hover": "#2563eb",
        "primary_light": "#1e3a5f",
        
        "bg_main": "#0f172a",
        "bg_sidebar": "#020617",
        "bg_card": "#1e293b",
        "bg_input": "#334155",
        "bg_hover": "#334155",
        
        "text_primary": "#f1f5f9",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "text_sidebar": "#94a3b8",
        "text_sidebar_active": "#ffffff",
        
        "border": "#334155",
        "border_focus": "#3b82f6",
        
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        
        "sidebar_active": "#3b82f6",
        "sidebar_hover": "#1e293b",
    }


class ModernTheme:
    """现代主题管理器"""
    
    # 字体配置
    FONTS = {
        "title": ("Microsoft YaHei", 16, "bold"),
        "heading": ("Microsoft YaHei", 12, "bold"),
        "subheading": ("Microsoft YaHei", 11, "bold"),
        "body": ("Microsoft YaHei", 10),
        "small": ("Microsoft YaHei", 9),
        "mono": ("Consolas", 10),
        "icon": ("Segoe UI Emoji", 12),
    }
    
    # 尺寸配置
    SIZES = {
        "sidebar_width": 220,
        "padding_xs": 4,
        "padding_sm": 8,
        "padding_md": 12,
        "padding_lg": 16,
        "padding_xl": 24,
        "border_radius": 8,
        "button_height": 36,
        "input_height": 32,
    }
    
    # 功能图标映射
    ICONS = {
        "cross_project": "🔄",
        "json_detector": "🔍",
        "excel_processor": "📊",
        "field_extractor": "📋",
        "table_range": "🌐",
        "sheet_splitter": "✂️",
        "batch_modifier": "⚡",
        "config_sync": "🔗",
        "csv_converter": "📄",
        "about": "ℹ️",
        "settings": "⚙️",
        "home": "🏠",
        "folder": "📁",
        "file": "📄",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "💡",
        "run": "▶️",
        "stop": "⏹️",
        "clear": "🗑️",
        "export": "💾",
        "view": "👁️",
        "refresh": "🔄",
    }
    
    def __init__(self, is_dark: bool = False):
        self.is_dark = is_dark
        self.colors = ThemeColors.DARK if is_dark else ThemeColors.LIGHT
    
    def apply_to_root(self, root: tk.Tk):
        """应用主题到根窗口"""
        root.configure(bg=self.colors["bg_main"])
        
        # 配置 ttk 样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # ========== 基础样式 ==========
        style.configure(".", 
            font=self.FONTS["body"],
            background=self.colors["bg_main"],
            foreground=self.colors["text_primary"]
        )
        
        # ========== Frame 样式 ==========
        style.configure("TFrame", background=self.colors["bg_main"])
        style.configure("Card.TFrame", background=self.colors["bg_card"])
        style.configure("Sidebar.TFrame", background=self.colors["bg_sidebar"])
        
        # ========== Label 样式 ==========
        style.configure("TLabel", 
            background=self.colors["bg_main"],
            foreground=self.colors["text_primary"]
        )
        style.configure("Title.TLabel", 
            font=self.FONTS["title"],
            foreground=self.colors["text_primary"]
        )
        style.configure("Heading.TLabel", 
            font=self.FONTS["heading"],
            foreground=self.colors["text_primary"]
        )
        style.configure("Subheading.TLabel",
            font=self.FONTS["subheading"],
            foreground=self.colors["text_primary"]
        )
        style.configure("Secondary.TLabel",
            foreground=self.colors["text_secondary"]
        )
        style.configure("Muted.TLabel",
            foreground=self.colors["text_muted"],
            font=self.FONTS["small"]
        )
        style.configure("Success.TLabel", foreground=self.colors["success"])
        style.configure("Warning.TLabel", foreground=self.colors["warning"])
        style.configure("Error.TLabel", foreground=self.colors["error"])
        style.configure("Info.TLabel", foreground=self.colors["info"])
        
        # 卡片内的 Label
        style.configure("Card.TLabel", background=self.colors["bg_card"])
        style.configure("CardHeading.TLabel", 
            background=self.colors["bg_card"],
            font=self.FONTS["heading"]
        )
        
        # ========== Button 样式 ==========
        style.configure("TButton",
            font=self.FONTS["body"],
            padding=(12, 6)
        )
        
        # 主要按钮
        style.configure("Primary.TButton",
            font=self.FONTS["body"],
            padding=(16, 8),
            background=self.colors["primary"],
            foreground="#ffffff"
        )
        style.map("Primary.TButton",
            background=[("active", self.colors["primary_hover"]),
                       ("pressed", self.colors["primary_hover"])]
        )
        
        # 次要按钮（轮廓）
        style.configure("Secondary.TButton",
            font=self.FONTS["body"],
            padding=(12, 6),
            background=self.colors["bg_card"],
            foreground=self.colors["text_primary"]
        )
        
        # 小按钮
        style.configure("Small.TButton",
            font=self.FONTS["small"],
            padding=(8, 4)
        )
        
        # ========== Entry 样式 ==========
        style.configure("TEntry",
            font=self.FONTS["body"],
            fieldbackground=self.colors["bg_input"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"]
        )
        style.map("TEntry",
            bordercolor=[("focus", self.colors["border_focus"])],
            lightcolor=[("focus", self.colors["border_focus"])]
        )
        
        # ========== Combobox 样式 ==========
        style.configure("TCombobox",
            font=self.FONTS["body"],
            fieldbackground=self.colors["bg_input"],
            background=self.colors["bg_input"]
        )
        
        # ========== LabelFrame 样式 ==========
        style.configure("TLabelframe",
            background=self.colors["bg_card"],
            bordercolor=self.colors["border"]
        )
        style.configure("TLabelframe.Label",
            font=self.FONTS["subheading"],
            foreground=self.colors["text_primary"],
            background=self.colors["bg_card"]
        )
        
        # ========== Checkbutton 样式 ==========
        style.configure("TCheckbutton",
            font=self.FONTS["body"],
            background=self.colors["bg_card"]
        )
        
        # ========== Progressbar 样式 ==========
        style.configure("TProgressbar",
            background=self.colors["primary"],
            troughcolor=self.colors["bg_hover"]
        )
        
        # ========== Scrollbar 样式 ==========
        style.configure("TScrollbar",
            background=self.colors["bg_hover"],
            troughcolor=self.colors["bg_main"],
            arrowcolor=self.colors["text_muted"]
        )
    
    def get_sidebar_button_style(self, is_active: bool = False) -> Dict[str, Any]:
        """获取侧边栏按钮样式"""
        if is_active:
            return {
                "bg": self.colors["sidebar_active"],
                "fg": self.colors["text_sidebar_active"],
                "activebackground": self.colors["sidebar_active"],
                "activeforeground": self.colors["text_sidebar_active"],
            }
        return {
            "bg": self.colors["bg_sidebar"],
            "fg": self.colors["text_sidebar"],
            "activebackground": self.colors["sidebar_hover"],
            "activeforeground": self.colors["text_sidebar_active"],
        }
