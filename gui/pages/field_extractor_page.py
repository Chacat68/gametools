# -*- coding: utf-8 -*-
"""
GameTools 字段导出页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from pathlib import Path

from gui.pages.base_page import ModernPage


class FieldExtractorPage(ModernPage):
    """字段导出页面"""
    
    PAGE_KEY = "field_extractor"
    PAGE_TITLE = "表字段导出"
    PAGE_ICON = "📋"
    PAGE_DESCRIPTION = "扫描Excel文件，提取包含文本的列字段信息"
    
    def __init__(self, parent, app, theme):
        self.extractor = None
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建页面控件"""
        # 目录选择卡片
        self._create_directory_card()
        
        # 选项卡片
        self._create_options_card()
        
        # 操作按钮
        self._create_action_buttons()
        
        # 结果区域
        self._create_result_section()
    
    def _create_directory_card(self):
        """创建目录选择卡片"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X, pady=(0, 16))
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.X, padx=20, pady=20)
        
        # 标题
        tk.Label(
            inner,
            text="📁 目录配置",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 16))
        
        # 输入目录
        self._create_dir_row(inner, "输入目录", "input_dir_var",
                             lambda: self.browse_directory("选择Excel目录", self.input_dir_var),
                             "(Excel文件所在目录)")
        
        # 输出文件
        self._create_dir_row(inner, "输出文件", "output_file_var",
                             self._browse_output_file,
                             "(字段配置JSON)")
    
    def _create_dir_row(self, parent, label: str, var_name: str,
                        browse_cmd, hint: str = ""):
        """创建目录/文件选择行"""
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
    
    def _browse_output_file(self):
        """浏览输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="保存字段配置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            defaultextension=".json"
        )
        if filepath:
            self.output_file_var.set(filepath)
    
    def _create_options_card(self):
        """创建选项卡片"""
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
            text="⚙️ 提取选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 16))
        
        # 选项行
        options_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        options_row.pack(fill=tk.X, pady=(0, 12))
        
        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="递归扫描子目录",
            variable=self.recursive_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.detect_lang_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="检测本地化文本列",
            variable=self.detect_lang_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        # 行号设置
        row2 = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row2.pack(fill=tk.X)
        
        tk.Label(
            row2,
            text="字段行号:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.field_row_var = tk.StringVar(value="5")
        tk.Entry(
            row2,
            textvariable=self.field_row_var,
            font=self.theme.FONTS["body"],
            width=5,
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        tk.Label(
            row2,
            text="数据起始行:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.data_start_row_var = tk.StringVar(value="7")
        tk.Entry(
            row2,
            textvariable=self.data_start_row_var,
            font=self.theme.FONTS["body"],
            width=5,
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        ).pack(side=tk.LEFT)
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        btn_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.extract_btn = tk.Button(
            btn_frame,
            text="📋 开始提取",
            font=("Microsoft YaHei", 10, "bold"),
            command=self._start_extraction,
            bg=self.theme.colors["primary"],
            fg="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            btn_frame,
            text="🗑️ 清空",
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
            text="📊 提取结果",
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
        
        # 结果文本
        result_frame = tk.Frame(
            inner,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(
            result_frame,
            font=self.theme.FONTS["mono"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)
    
    def _start_extraction(self):
        """开始提取"""
        input_dir = self.input_dir_var.get()
        if not input_dir:
            self.show_warning("警告", "请选择输入目录")
            return
        
        if not Path(input_dir).exists():
            self.show_error("错误", f"目录不存在: {input_dir}")
            return
        
        self.extract_btn.configure(state=tk.DISABLED)
        self.stats_label.configure(text="提取中...")
        self.result_text.delete("1.0", tk.END)
        
        thread = threading.Thread(target=self._do_extraction, daemon=True)
        thread.start()
    
    def _do_extraction(self):
        """执行提取"""
        try:
            from core.excel_field_extractor import ExcelFieldExtractor
            
            if not self.extractor:
                self.extractor = ExcelFieldExtractor()
            
            input_dir = self.input_dir_var.get()
            output_file = self.output_file_var.get() or None
            recursive = self.recursive_var.get()
            field_row = int(self.field_row_var.get())
            data_start_row = int(self.data_start_row_var.get())
            
            def progress_callback(msg, pct=None):
                self.after(0, lambda: self._update_progress(msg, pct))
            
            self.extractor.set_progress_callback(progress_callback)
            
            result = self.extractor.extract_fields(
                input_directory=input_dir,
                output_file=output_file,
                recursive=recursive,
                field_row=field_row,
                data_start_row=data_start_row
            )
            
            self.after(0, lambda: self._on_complete(result))
            
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))
    
    def _update_progress(self, message: str, percentage: float = None):
        """更新进度"""
        self.stats_label.configure(text=message)
        if percentage is not None:
            self.progress_fill.place(relwidth=percentage / 100)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
    
    def _on_complete(self, result):
        """完成处理"""
        self.extract_btn.configure(state=tk.NORMAL)
        self.progress_fill.place(relwidth=1)
        
        if isinstance(result, dict):
            tables = result.get('tables', {})
            self.stats_label.configure(text=f"✅ 完成，共 {len(tables)} 个表", fg=self.theme.colors["success"])
            
            summary = f"\n{'='*50}\n提取完成:\n"
            summary += f"  扫描表数: {len(tables)}\n"
            total_fields = sum(len(t.get('fields', [])) for t in tables.values())
            summary += f"  总字段数: {total_fields}\n"
            self.result_text.insert(tk.END, summary)
        
        self.show_info("完成", "字段提取完成！")
    
    def _on_error(self, error_msg: str):
        """错误处理"""
        self.extract_btn.configure(state=tk.NORMAL)
        self.stats_label.configure(text="❌ 失败", fg=self.theme.colors["error"])
        self.result_text.insert(tk.END, f"\n错误: {error_msg}\n")
        self.show_error("错误", error_msg)
    
    def _clear_results(self):
        """清空结果"""
        self.result_text.delete("1.0", tk.END)
        self.stats_label.configure(text="", fg=self.theme.colors["text_muted"])
        self.progress_fill.place(relwidth=0)
