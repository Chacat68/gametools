# -*- coding: utf-8 -*-
"""
关于页面标签页
"""

import tkinter as tk
from tkinter import ttk

from version import get_version, format_version_string, get_description, get_latest_changes


class AboutTab:
    """关于页面标签页"""
    
    def __init__(self, app, notebook: ttk.Notebook):
        """
        初始化标签页
        
        Args:
            app: 主应用实例（GameToolsUnified）
            notebook: ttk.Notebook实例
        """
        self.app = app
        self.notebook = notebook
        
        # 创建标签页框架
        self.frame = ttk.Frame(notebook, padding="20")
        notebook.add(self.frame, text="关于")
        
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=0)
        
        # 创建UI
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面控件"""
        # 标题区域
        title_frame = ttk.Frame(self.frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        # 主标题
        title_label = ttk.Label(title_frame, text="gametools - 游戏工具集", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # 版本信息
        version_label = ttk.Label(title_frame, text=format_version_string(), style='Info.TLabel')
        version_label.grid(row=1, column=0, pady=(0, 20))
        
        # 内容区域（左右两栏）
        content_frame = ttk.Frame(self.frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1, minsize=360)
        content_frame.columnconfigure(1, weight=1, minsize=360)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧：功能模块
        self._create_features_panel(content_frame)
        
        # 右侧：技术信息
        self._create_tech_panel(content_frame)
        
        # 底部信息
        self._create_footer()
    
    def _create_features_panel(self, parent):
        """创建功能模块面板"""
        left_frame = ttk.LabelFrame(parent, text="功能模块", padding=12)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        left_frame.columnconfigure(0, weight=1)
        
        features_text = (
            "📊 JSON格式检测工具\n"
            "  检测JSON文件中text字段的格式一致性\n\n"
            "📈 Excel数据处理工具\n"
            "  根据指定列对Excel数据进行分组和处理\n\n"
            "📄 Excel分页拆分工具\n"
            "  根据第一列文件名将数据拆分到新表格的对应分页\n\n"
            "📋 表字段导出工具\n"
            "  扫描Excel文件，提取包含文本的列的字段信息\n\n"
            "🌐 多语言翻译提取工具\n"
            "  根据字段导出的JSON配置，智能提取多语言翻译内容\n\n"
            "🔄 Excel配置同步工具\n"
            "  将源目录的Excel配置同步到其他目录的同名文件\n\n"
            f"📋 版本信息\n  当前版本: v{get_version()}\n  项目描述: {get_description()}"
        )
        
        textbox = tk.Text(left_frame, wrap='word', height=15, padx=6, pady=6,
                         font=("Microsoft YaHei", 10), relief='flat',
                         background='SystemButtonFace')
        textbox.insert('1.0', features_text)
        textbox.configure(state='disabled')
        textbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=textbox.yview)
        textbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_tech_panel(self, parent):
        """创建技术信息面板"""
        right_frame = ttk.LabelFrame(parent, text="技术信息", padding=12)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        right_frame.columnconfigure(0, weight=1)
        
        latest_changes = get_latest_changes()
        changes_text = "\n".join([f"• {change}" for change in latest_changes])
        
        tech_text = (
            "🛠️ 技术栈:\n"
            "• Python 3.7+\n"
            "• Tkinter (GUI界面)\n"
            "• pandas (数据处理)\n"
            "• xlwings (Excel修改引擎，需要安装Excel)\n\n"
            "✨ 主要特性:\n"
            "• 支持多种文件格式\n"
            "• 图形化界面，操作简单\n"
            "• 多线程处理，界面响应流畅\n"
            "• 支持exe文件打包和分发\n\n"
            f"🆕 最新更新 (v{get_version()}):\n{changes_text}\n\n"
            "⚠️ 注意事项:\n"
            "• 确保文件格式正确\n"
            "• 大文件处理可能需要较长时间\n"
            "• 建议在检测前备份重要文件"
        )
        
        textbox = tk.Text(right_frame, wrap='word', height=15, padx=6, pady=6,
                         font=("Microsoft YaHei", 10), relief='flat',
                         background='SystemButtonFace')
        textbox.insert('1.0', tech_text)
        textbox.configure(state='disabled')
        textbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=textbox.yview)
        textbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_footer(self):
        """创建底部信息"""
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # 使用方法
        usage_text = "📖 使用方法: 选择相应的功能页签 → 按照界面提示操作 → 查看检测结果"
        usage_label = ttk.Label(bottom_frame, text=usage_text, 
                               font=("Microsoft YaHei", 10), style='Info.TLabel')
        usage_label.grid(row=0, column=0, pady=(0, 10))
        
        # 版权信息
        copyright_text = "💬 技术支持: 如有问题或建议，请联系开发团队\n© 2024 gametools - 版权所有"
        copyright_label = ttk.Label(bottom_frame, text=copyright_text, 
                                   font=("Microsoft YaHei", 9), style='Info.TLabel')
        copyright_label.grid(row=1, column=0)
