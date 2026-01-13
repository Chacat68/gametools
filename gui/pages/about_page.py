# -*- coding: utf-8 -*-
"""
GameTools 关于页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk

from gui.pages.base_page import ModernPage


class AboutPage(ModernPage):
    """关于页面"""
    
    PAGE_KEY = "about"
    PAGE_TITLE = "关于 GameTools"
    PAGE_ICON = "ℹ️"
    PAGE_DESCRIPTION = "版本信息和帮助文档"
    
    def create_widgets(self):
        """创建关于页面控件"""
        # 两列布局
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        
        # 左列：版本信息
        self._create_version_card()
        
        # 右列：技术信息
        self._create_tech_card()
        
        # 底部：更新日志
        self._create_changelog_card()
    
    def _create_version_card(self):
        """创建版本信息卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 16))
        
        # 内容
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo 区域
        logo_frame = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        logo_frame.pack(fill=tk.X, pady=(0, 20))
        
        logo = tk.Label(
            logo_frame,
            text="🎮",
            font=("Segoe UI Emoji", 48),
            bg=self.theme.colors["bg_card"]
        )
        logo.pack()
        
        name = tk.Label(
            logo_frame,
            text="GameTools",
            font=("Microsoft YaHei", 20, "bold"),
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        )
        name.pack(pady=(8, 0))
        
        subtitle = tk.Label(
            logo_frame,
            text="游戏策划本地化工具集",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_secondary"]
        )
        subtitle.pack()
        
        # 版本信息
        try:
            from version import get_version, get_build_date, get_author
            version = get_version()
            build_date = get_build_date()
            author = get_author()
        except:
            version = "1.44.0"
            build_date = "2026-01-12"
            author = "GameTools 开发团队"
        
        info_items = [
            ("版本", f"v{version}"),
            ("构建日期", build_date),
            ("开发者", author),
        ]
        
        for label, value in info_items:
            row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(
                row,
                text=label,
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_secondary"],
                width=10,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_primary"],
                anchor=tk.W
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_tech_card(self):
        """创建技术信息卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.grid(row=0, column=1, sticky="nsew", pady=(0, 16))
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title = tk.Label(
            inner,
            text="🛠️ 技术栈",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        tech_items = [
            ("Python", "3.7+ 运行环境"),
            ("Tkinter", "GUI 界面框架"),
            ("pandas", "数据处理引擎"),
            ("xlwings", "Excel 修改引擎"),
            ("openpyxl", "Excel 读取引擎"),
        ]
        
        for name, desc in tech_items:
            row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
            row.pack(fill=tk.X, pady=6)
            
            # 圆点
            dot = tk.Label(
                row,
                text="•",
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["primary"]
            )
            dot.pack(side=tk.LEFT, padx=(0, 8))
            
            tk.Label(
                row,
                text=name,
                font=("Microsoft YaHei", 10, "bold"),
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_primary"],
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=f" - {desc}",
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_secondary"],
                anchor=tk.W
            ).pack(side=tk.LEFT)
        
        # 特性
        features_title = tk.Label(
            inner,
            text="✨ 主要特性",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        features_title.pack(fill=tk.X, pady=(24, 16))
        
        features = [
            "多线程处理，界面响应流畅",
            "延迟加载，启动速度快",
            "支持 exe 打包分发",
            "完整保留 Excel 文件结构",
        ]
        
        for feature in features:
            row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(
                row,
                text="✓",
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["success"]
            ).pack(side=tk.LEFT, padx=(0, 8))
            
            tk.Label(
                row,
                text=feature,
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_primary"],
                anchor=tk.W
            ).pack(side=tk.LEFT)
    
    def _create_changelog_card(self):
        """创建更新日志卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title = tk.Label(
            inner,
            text="🆕 最近更新",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 获取更新日志
        try:
            from version import get_latest_changes, get_version
            changes = get_latest_changes()
            version = get_version()
        except:
            changes = ["暂无更新日志"]
            version = "1.44.0"
        
        # 版本标签
        version_badge = tk.Frame(inner, bg=self.theme.colors["primary"])
        version_badge.pack(anchor=tk.W, pady=(0, 12))
        
        tk.Label(
            version_badge,
            text=f" v{version} ",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["primary"],
            fg="#ffffff"
        ).pack(padx=8, pady=4)
        
        # 更新列表
        for change in changes[:6]:  # 最多显示6条
            row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
            row.pack(fill=tk.X, pady=4)
            
            tk.Label(
                row,
                text="•",
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_muted"]
            ).pack(side=tk.LEFT, padx=(0, 8))
            
            tk.Label(
                row,
                text=change,
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_primary"],
                anchor=tk.W
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
