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
        # 设置按钮
        self._create_settings_button()
        
        # 快捷入口区域
        self._create_quick_actions()
        
        # 工具分类
        self._create_tool_categories()
        
        # 底部信息
        self._create_info_section()

    def _load_visible_pages(self) -> Dict[str, bool]:
        """加载页面可见性配置（用于首页内容过滤）"""
        # 优先复用主应用的实现，避免重复逻辑
        if hasattr(self.app, '_load_visible_pages'):
            try:
                visible = self.app._load_visible_pages()
                return visible if isinstance(visible, dict) else {}
            except Exception:
                return {}

        # 兜底：直接读 config.json
        import json
        from pathlib import Path

        config_path = Path("config.json")
        if not config_path.exists():
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            visible_pages = config.get("visible_pages", {})
            return visible_pages if isinstance(visible_pages, dict) else {}
        except Exception:
            return {}

    def _is_page_visible(self, page_key: str) -> bool:
        """判断页面是否可见（首页始终可见）"""
        if page_key == "home":
            return True
        visible_pages = self._load_visible_pages()
        return bool(visible_pages.get(page_key, True))

    def refresh_home_content(self):
        """刷新首页内容：设置变更后立即生效"""
        if not hasattr(self, 'content'):
            return

        for child in list(self.content.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass

        # 重新创建首页内容
        self._create_settings_button()
        self._create_quick_actions()
        self._create_tool_categories()
        self._create_info_section()

        # 更新滚动条可见性
        if hasattr(self, '_refresh_vscroll_visibility'):
            try:
                self.after(0, self._refresh_vscroll_visibility)
            except Exception:
                pass
    
    def _create_settings_button(self):
        """创建设置按钮"""
        btn_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 12))
        
        settings_btn = tk.Button(
            btn_frame,
            text="⚙️ 功能显示设置",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["primary"],
            fg="white",
            activebackground=self.theme.colors["primary_hover"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            command=self._show_settings_dialog
        )
        settings_btn.pack(side=tk.RIGHT)
        
    def _show_settings_dialog(self):
        """显示设置对话框"""
        from tkinter import messagebox
        import json
        from pathlib import Path
        
        # 创建对话框
        dialog = tk.Toplevel(self.app.root)
        dialog.title("功能显示设置")
        dialog.geometry("500x600")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # 加载当前配置
        config_path = Path("config.json")
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                pass
        
        if "visible_pages" not in config:
            config["visible_pages"] = {}
        
        # 主框架
        main_frame = tk.Frame(dialog, bg=self.theme.colors["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title = tk.Label(
            main_frame,
            text="选择要在侧边栏显示的功能",
            font=self.theme.FONTS["heading"],
            bg=self.theme.colors["bg_main"],
            fg=self.theme.colors["text_primary"]
        )
        title.pack(pady=(0, 16))
        
        # 滚动区域
        canvas = tk.Canvas(main_frame, bg=self.theme.colors["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.colors["bg_main"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 复选框变量
        check_vars = {}
        
        # 获取所有页面配置
        from gui.gametools_modern import GameToolsModern
        page_config = GameToolsModern.PAGE_CONFIG
        
        # 按分组显示
        groups = {
            "main": "主要",
            "excel": "📊 Excel工具",
            "translate": "🌐 翻译工具",
            "tools": "🔧 其他工具",
            "other": "其他"
        }
        
        for group_key, group_name in groups.items():
            # 分组标题
            group_items = [p for p in page_config if p[3] == group_key]
            if not group_items:
                continue
                
            group_label = tk.Label(
                scrollable_frame,
                text=group_name,
                font=self.theme.FONTS["subheading"],
                bg=self.theme.colors["bg_main"],
                fg=self.theme.colors["text_primary"],
                anchor=tk.W
            )
            group_label.pack(fill=tk.X, pady=(12 if group_key != "main" else 0, 8))
            
            # 分组项
            for key, title, icon, group, _ in group_items:
                # 首页必须显示，不可取消
                if key == "home":
                    continue
                    
                var = tk.BooleanVar(value=config["visible_pages"].get(key, True))
                check_vars[key] = var
                
                # 使用卡片样式的复选框项
                check_card = tk.Frame(
                    scrollable_frame,
                    bg=self.theme.colors["bg_card"],
                    highlightbackground=self.theme.colors["border"],
                    highlightthickness=1,
                    cursor="hand2"
                )
                check_card.pack(fill=tk.X, pady=4, padx=8)
                
                # 内容框架
                content_frame = tk.Frame(check_card, bg=self.theme.colors["bg_card"])
                content_frame.pack(fill=tk.X, padx=12, pady=10)
                
                # 自定义复选框 - 使用Label实现更好的样式
                checkbox_container = tk.Frame(content_frame, bg=self.theme.colors["bg_card"])
                checkbox_container.pack(side=tk.LEFT, padx=(0, 12))
                
                # 复选框指示器
                check_indicator = tk.Label(
                    checkbox_container,
                    text="✓" if var.get() else "",
                    font=("Segoe UI", 12, "bold"),
                    bg=self.theme.colors["primary"] if var.get() else self.theme.colors["bg_main"],
                    fg="white",
                    width=2,
                    height=1,
                    relief=tk.FLAT,
                    borderwidth=2,
                    highlightthickness=1,
                    highlightbackground=self.theme.colors["primary"] if var.get() else self.theme.colors["border"]
                )
                check_indicator.pack()
                
                # 文本区域
                text_frame = tk.Frame(content_frame, bg=self.theme.colors["bg_card"])
                text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # 标题（图标 + 名称）
                title_label = tk.Label(
                    text_frame,
                    text=f"{icon} {title}",
                    font=self.theme.FONTS["subheading"],
                    bg=self.theme.colors["bg_card"],
                    fg=self.theme.colors["text_primary"],
                    anchor=tk.W
                )
                title_label.pack(fill=tk.X)
                
                # 切换函数
                def toggle_check(e=None, v=var, ind=check_indicator, k=key):
                    v.set(not v.get())
                    ind.config(
                        text="✓" if v.get() else "",
                        bg=self.theme.colors["primary"] if v.get() else self.theme.colors["bg_main"],
                        highlightbackground=self.theme.colors["primary"] if v.get() else self.theme.colors["border"]
                    )
                
                # 悬停效果
                def on_enter(e, card=check_card, frame=content_frame, txt=text_frame, lbl=title_label):
                    card.config(highlightbackground=self.theme.colors["primary"])
                
                def on_leave(e, card=check_card, frame=content_frame, txt=text_frame, lbl=title_label):
                    card.config(highlightbackground=self.theme.colors["border"])
                
                # 绑定点击事件
                for widget in [check_card, content_frame, checkbox_container, check_indicator, text_frame, title_label]:
                    widget.bind("<Button-1>", toggle_check)
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        btn_frame = tk.Frame(dialog, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        def save_settings():
            # 保存配置
            for key, var in check_vars.items():
                config["visible_pages"][key] = var.get()
            
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                # 即时刷新侧边栏 + 首页内容
                if hasattr(self.app, 'refresh_sidebar'):
                    self.app.refresh_sidebar()
                    self.refresh_home_content()
                    messagebox.showinfo("成功", "设置已保存并生效！", parent=dialog)
                else:
                    # 没有侧边栏刷新能力时，首页仍可根据最新配置刷新
                    self.refresh_home_content()
                    messagebox.showinfo("成功", "设置已保存！\n部分界面可能需要重启后完全生效。", parent=dialog)
                
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败：{e}", parent=dialog)
        
        save_btn = tk.Button(
            btn_frame,
            text="保存设置",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["primary"],
            fg="white",
            activebackground=self.theme.colors["primary_hover"],
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=save_settings
        )
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["border"],
            activeforeground=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT)
    
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

        # 根据可见性过滤
        visible_quick_tools = [t for t in quick_tools if self._is_page_visible(t[0])]

        if not visible_quick_tools:
            empty_label = tk.Label(
                grid,
                text="（快捷入口已全部隐藏，可在功能显示设置中开启）",
                font=self.theme.FONTS["small"],
                bg=self.theme.colors["bg_main"],
                fg=self.theme.colors["text_muted"],
                anchor=tk.W
            )
            empty_label.pack(fill=tk.X)
            return

        for i, (key, title, desc, color) in enumerate(visible_quick_tools):
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
        
        excel_tools = [
            ("batch_modifier", "⚡", "批量改表", "批量修改Excel配置"),
            ("field_extractor", "📋", "字段导出", "提取本地化字段"),
            ("sheet_splitter", "✂️", "分页拆分", "按首列创建分页"),
            ("config_sync", "🔗", "配置同步", "同步Excel配置"),
            ("csv_converter", "📄", "Excel转CSV", "批量转换格式"),
            ("excel_processor", "📊", "数据处理", "A列分组拆分"),
        ]

        translate_tools = [
            ("cross_project", "🔄", "跨项目翻译", "翻译映射对照"),
            ("table_range", "🌐", "多语言提取", "按配置提取翻译"),
            ("json_detector", "🔍", "JSON检测", "检测格式错误"),
        ]

        excel_tools = [t for t in excel_tools if self._is_page_visible(t[0])]
        translate_tools = [t for t in translate_tools if self._is_page_visible(t[0])]

        # 左列：Excel 处理工具
        self._create_category_card(section, 0, 0, "📊 Excel 处理工具", excel_tools)

        # 右列：翻译 & 检测工具
        self._create_category_card(section, 0, 1, "🌐 翻译 & 检测工具", translate_tools)
    
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
        if tools:
            for key, icon, name, desc in tools:
                self._create_tool_item(card, key, icon, name, desc)
        else:
            empty = tk.Label(
                card,
                text="（此分类已全部隐藏）",
                font=self.theme.FONTS["small"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_muted"],
                anchor=tk.W
            )
            empty.pack(fill=tk.X, padx=16, pady=(0, 8))
        
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
