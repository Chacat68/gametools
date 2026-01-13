# -*- coding: utf-8 -*-
"""
GameTools Excel转CSV页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from pathlib import Path

from gui.pages.base_page import ModernPage


class CsvConverterPage(ModernPage):
    """Excel转CSV页面"""
    
    PAGE_KEY = "csv_converter"
    PAGE_TITLE = "Excel 转 CSV"
    PAGE_ICON = "📄"
    PAGE_DESCRIPTION = "批量将Excel文件转换为CSV格式"
    
    def __init__(self, parent, app, theme):
        self.converter = None
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建页面控件"""
        # 路径配置卡片
        self._create_path_card()
        
        # 转换选项卡片
        self._create_options_card()
        
        # 操作按钮
        self._create_action_buttons()
        
        # 结果区域
        self._create_result_section()
    
    def _create_path_card(self):
        """创建路径配置卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 16))
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            inner,
            text="📁 路径配置",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 16))
        
        # 输入目录/文件
        self._create_path_row(inner, "输入路径", "input_path_var",
                              self._browse_input, "(Excel文件或目录)")
        
        # 输出目录
        self._create_path_row(inner, "输出目录", "output_dir_var",
                              self._browse_output_dir, "(CSV输出目录)")
    
    def _create_path_row(self, parent, label: str, var_name: str,
                         browse_cmd, hint: str = ""):
        """创建路径选择行"""
        row = tk.Frame(parent, bg=self.theme.colors["bg_card"])
        row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            row,
            text=label,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        var = tk.StringVar()
        setattr(self, var_name, var)
        
        entry_frame = tk.Frame(
            row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=browse_cmd,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
        
        if hint:
            tk.Label(
                row,
                text=hint,
                font=self.theme.FONTS["small"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_muted"]
            ).pack(side=tk.LEFT, padx=(8, 0))
    
    def _browse_input(self):
        """浏览输入路径"""
        # 弹出选择对话框
        choice = tk.messagebox.askquestion(
            "选择类型",
            "选择文件夹进行批量转换？\n\n是 = 选择文件夹\n否 = 选择单个文件"
        )
        
        if choice == 'yes':
            path = filedialog.askdirectory(title="选择Excel文件目录")
        else:
            path = filedialog.askopenfilename(
                title="选择Excel文件",
                filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
            )
        
        if path:
            self.input_path_var.set(path)
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        path = filedialog.askdirectory(title="选择CSV输出目录")
        if path:
            self.output_dir_var.set(path)
    
    def _create_options_card(self):
        """创建转换选项卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 16))
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            inner,
            text="⚙️ 转换选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 16))
        
        # 第一行选项
        row1 = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row1.pack(fill=tk.X, pady=(0, 12))
        
        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            row1,
            text="递归处理子目录",
            variable=self.recursive_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.all_sheets_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            row1,
            text="转换所有工作表",
            variable=self.all_sheets_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT)
        
        # 第二行：编码选择
        row2 = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row2.pack(fill=tk.X)
        
        tk.Label(
            row2,
            text="输出编码:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.encoding_var = tk.StringVar(value="utf-8-sig")
        encoding_combo = ttk.Combobox(
            row2,
            textvariable=self.encoding_var,
            values=['utf-8-sig', 'utf-8', 'gbk', 'gb2312'],
            state='readonly',
            width=12
        )
        encoding_combo.pack(side=tk.LEFT, padx=(0, 16))
        
        tk.Label(
            row2,
            text="💡 utf-8-sig 推荐用于Excel打开",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"]
        ).pack(side=tk.LEFT)
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        btn_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.convert_btn = tk.Button(
            btn_frame,
            text="📄 开始转换",
            font=("Microsoft YaHei", 10, "bold"),
            command=self._start_conversion,
            bg=self.theme.colors["primary"],
            fg="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            btn_frame,
            text="🗑️ 清空结果",
            font=self.theme.FONTS["body"],
            command=self._clear_results,
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=8,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        ).pack(side=tk.LEFT)
    
    def _create_result_section(self):
        """创建结果区域"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        header = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        header.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            header,
            text="📊 转换结果",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(
            header,
            text="",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"]
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_track = tk.Frame(inner, bg=self.theme.colors["bg_hover"], height=4)
        self.progress_track.pack(fill=tk.X, pady=(0, 12))
        self.progress_track.pack_propagate(False)
        
        self.progress_fill = tk.Frame(self.progress_track, bg=self.theme.colors["primary"], height=4)
        self.progress_fill.place(x=0, y=0, relheight=1, relwidth=0)
    
    def _start_conversion(self):
        """开始转换"""
        input_path = self.input_path_var.get()
        output_dir = self.output_dir_var.get()
        
        if not input_path:
            self.show_warning("警告", "请选择输入路径")
            return
        
        if not Path(input_path).exists():
            self.show_error("错误", f"路径不存在: {input_path}")
            return
        
        if not output_dir:
            # 使用输入路径的父目录
            if Path(input_path).is_file():
                output_dir = str(Path(input_path).parent)
            else:
                output_dir = input_path
            self.output_dir_var.set(output_dir)
        
        self.convert_btn.configure(state=tk.DISABLED)
        self.stats_label.configure(text="转换中...")
        
        thread = threading.Thread(target=self._do_conversion, daemon=True)
        thread.start()
    
    def _do_conversion(self):
        """执行转换"""
        try:
            from core.excel_to_csv_converter import ExcelToCsvConverter
            
            if not self.converter:
                self.converter = ExcelToCsvConverter()
            
            input_path = self.input_path_var.get()
            output_dir = self.output_dir_var.get()
            recursive = self.recursive_var.get()
            all_sheets = self.all_sheets_var.get()
            encoding = self.encoding_var.get()
            
            def progress_callback(msg, pct=None):
                self.after(0, lambda: self._update_progress(msg, pct))
            
            self.converter.set_progress_callback(progress_callback)
            
            result = self.converter.convert(
                input_path=input_path,
                output_dir=output_dir,
                recursive=recursive,
                all_sheets=all_sheets,
                encoding=encoding
            )
            
            self.after(0, lambda: self._on_complete(result))
            
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))
    
    def _update_progress(self, message: str, percentage: float = None):
        """更新进度"""
        self.stats_label.configure(text=message)
        if percentage is not None:
            self.progress_fill.place(relwidth=percentage / 100)
    
    def _on_complete(self, result):
        """完成转换"""
        self.convert_btn.configure(state=tk.NORMAL)
        self.progress_fill.place(relwidth=1)
        
        if isinstance(result, dict):
            converted = result.get('converted', 0)
            self.stats_label.configure(
                text=f"✅ 完成，共转换 {converted} 个文件",
                fg=self.theme.colors["success"]
            )
        
        self.show_info("完成", "Excel转CSV完成！")
    
    def _on_error(self, error_msg: str):
        """错误处理"""
        self.convert_btn.configure(state=tk.NORMAL)
        self.stats_label.configure(text="❌ 失败", fg=self.theme.colors["error"])
        self.show_error("错误", error_msg)
    
    def _clear_results(self):
        """清空结果"""
        self.stats_label.configure(text="", fg=self.theme.colors["text_muted"])
        self.progress_fill.place(relwidth=0)
