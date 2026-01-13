# -*- coding: utf-8 -*-
"""
GameTools 现代化侧边栏组件
提供左侧导航栏，支持动态切换页面、分组折叠和滚动
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
        self.buttons: Dict[str, dict] = {}
        self.groups: Dict[str, dict] = {}  # 分组信息
        self.current_group = None  # 当前正在添加的分组
        
        # 配置样式
        self.configure(
            bg=theme.colors["bg_sidebar"],
            width=theme.SIZES["sidebar_width"]
        )
        self.pack_propagate(False)  # 固定宽度
        
        # 创建内部容器
        self._create_header()
        self._create_scrollable_nav()
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
    
    def _create_scrollable_nav(self):
        """创建可滚动的导航区域"""
        # 创建 Canvas 用于滚动
        self.canvas = tk.Canvas(
            self,
            bg=self.theme.colors["bg_sidebar"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=0)
        
        # 创建滚动条（仅在需要时显示）
        self.scrollbar = ttk.Scrollbar(
            self.canvas,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # 创建内部容器
        self.nav_container = tk.Frame(
            self.canvas,
            bg=self.theme.colors["bg_sidebar"]
        )
        
        # 将容器放入 Canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.nav_container,
            anchor="nw"
        )
        
        # 配置滚动
        self.canvas.configure(yscrollcommand=self._on_scroll)
        self.nav_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # 绑定鼠标滚轮
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
    
    def _on_scroll(self, *args):
        """滚动条回调"""
        self.scrollbar.set(*args)
        # 检查是否需要显示滚动条
        if float(args[0]) <= 0 and float(args[1]) >= 1:
            self.scrollbar.place_forget()
        else:
            self.scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
    
    def _on_frame_configure(self, event):
        """内容变化时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Canvas 大小变化时调整内容宽度"""
        # 让内容填满 Canvas 宽度
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _bind_mousewheel(self, event):
        """绑定鼠标滚轮"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        """解绑鼠标滚轮"""
        self.canvas.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
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
        """添加可折叠的分组标签"""
        group_key = text.lower().replace(" ", "_")
        self.current_group = group_key
        
        # 分组容器
        group_frame = tk.Frame(
            self.nav_container,
            bg=self.theme.colors["bg_sidebar"]
        )
        group_frame.pack(fill=tk.X, pady=(12, 0))
        
        # 标签行（可点击）
        label_row = tk.Frame(
            group_frame,
            bg=self.theme.colors["bg_sidebar"],
            cursor="hand2"
        )
        label_row.pack(fill=tk.X, padx=8, pady=(0, 6))
        
        # 分组标题
        label = tk.Label(
            label_row,
            text=text.upper(),
            font=("Microsoft YaHei", 8, "bold"),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 折叠/展开按钮
        toggle_btn = tk.Label(
            label_row,
            text="▼",
            font=("Microsoft YaHei", 8),
            bg=self.theme.colors["bg_sidebar"],
            fg=self.theme.colors["text_muted"],
            cursor="hand2"
        )
        toggle_btn.pack(side=tk.RIGHT, padx=(4, 0))
        
        # 子项容器
        items_frame = tk.Frame(
            group_frame,
            bg=self.theme.colors["bg_sidebar"]
        )
        items_frame.pack(fill=tk.X)
        
        # 保存分组信息
        self.groups[group_key] = {
            "frame": group_frame,
            "label_row": label_row,
            "label": label,
            "toggle_btn": toggle_btn,
            "items_frame": items_frame,
            "collapsed": False,
            "items": []
        }
        
        # 绑定点击事件
        for widget in [label_row, label, toggle_btn]:
            widget.bind("<Button-1>", lambda e, k=group_key: self._toggle_group(k))
            widget.bind("<Enter>", lambda e, k=group_key: self._on_group_enter(k))
            widget.bind("<Leave>", lambda e, k=group_key: self._on_group_leave(k))
    
    def _on_group_enter(self, group_key: str):
        """分组标签鼠标进入效果"""
        group = self.groups.get(group_key)
        if group:
            bg = self.theme.colors["sidebar_hover"]
            group["label_row"].configure(bg=bg)
            group["label"].configure(bg=bg)
            group["toggle_btn"].configure(bg=bg)
    
    def _on_group_leave(self, group_key: str):
        """分组标签鼠标离开效果"""
        group = self.groups.get(group_key)
        if group:
            bg = self.theme.colors["bg_sidebar"]
            group["label_row"].configure(bg=bg)
            group["label"].configure(bg=bg)
            group["toggle_btn"].configure(bg=bg)
    
    def _toggle_group(self, group_key: str):
        """切换分组的折叠/展开状态"""
        group = self.groups.get(group_key)
        if not group:
            return
        
        if group["collapsed"]:
            # 展开
            group["items_frame"].pack(fill=tk.X)
            group["toggle_btn"].configure(text="▼")
            group["collapsed"] = False
        else:
            # 折叠
            group["items_frame"].pack_forget()
            group["toggle_btn"].configure(text="▶")
            group["collapsed"] = True
        
        # 更新滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def add_item(self, item: SidebarItem):
        """添加导航项"""
        # 确定父容器（如果有当前分组，添加到分组的items_frame中）
        if self.current_group and self.current_group in self.groups:
            parent = self.groups[self.current_group]["items_frame"]
            self.groups[self.current_group]["items"].append(item.key)
        else:
            parent = self.nav_container
        
        # 创建按钮容器
        btn_frame = tk.Frame(
            parent,
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
            "item": item,
            "group": self.current_group
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
