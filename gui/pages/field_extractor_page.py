# -*- coding: utf-8 -*-
"""
GameTools 字段导出页面（现代化版本）
支持多语言目录配置
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
    PAGE_DESCRIPTION = "扫描Excel文件，提取包含文本的列字段信息（支持多语言目录）"
    
    def __init__(self, parent, app, theme):
        self.extractor = None
        self.last_result = None  # 保存最后一次执行结果
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建页面控件"""
        # 目录选择卡片（多语言）
        self._create_directory_card()
        
        # 选项卡片
        self._create_options_card()
        
        # 操作按钮
        self._create_action_buttons()
        
        # 结果区域
        self._create_result_section()
    
    def _create_directory_card(self):
        """创建多语言目录选择卡片"""
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
            text="📁 多语言目录配置（从物理行第5行提取字段名）",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 16))
        
        # 中文目录
        self._create_lang_dir_row(inner, "🇨🇳 中文目录", "zh_dir_var", "zh_check_var", True)
        
        # 越南语目录
        self._create_lang_dir_row(inner, "🇻🇳 越南语目录", "vn_dir_var", "vn_check_var", True)
        
        # 泰语目录
        self._create_lang_dir_row(inner, "🇹🇭 泰语目录", "th_dir_var", "th_check_var", True)
        
        # 输出目录
        self._create_dir_row(inner, "📤 输出目录", "output_dir_var",
                             self._browse_output_dir,
                             "(结果输出目录)")
    
    def _create_lang_dir_row(self, parent, label: str, var_name: str, 
                             check_var_name: str, default_checked: bool = True):
        """创建带勾选框的语言目录选择行"""
        row = tk.Frame(parent, bg=self.theme.colors["bg_card"])
        row.pack(fill=tk.X, pady=(0, 12))
        
        # 勾选框
        check_var = tk.BooleanVar(value=default_checked)
        setattr(self, check_var_name, check_var)
        
        tk.Checkbutton(
            row,
            text="",
            variable=check_var,
            bg=self.theme.colors["bg_card"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=label,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=12,
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
            command=lambda v=var: self._browse_lang_directory(v),
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
    
    def _browse_lang_directory(self, var: tk.StringVar):
        """浏览语言目录"""
        directory = filedialog.askdirectory(title="选择Excel目录")
        if directory:
            var.set(directory)
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir_var.set(directory)
    
    def _create_dir_row(self, parent, label: str, var_name: str,
                        browse_cmd, hint: str = ""):
        """创建目录/文件选择行"""
        row = tk.Frame(parent, bg=self.theme.colors["bg_card"])
        row.pack(fill=tk.X, pady=(0, 12))
        
        # 占位符，与语言行对齐
        tk.Frame(row, width=24, bg=self.theme.colors["bg_card"]).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=label,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=12,
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
        
        # 输出格式选择
        format_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        format_row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            format_row,
            text="输出格式:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.output_format_var = tk.StringVar(value="json")
        for fmt, text in [("json", "JSON"), ("csv", "CSV"), ("excel", "Excel")]:
            tk.Radiobutton(
                format_row,
                text=text,
                variable=self.output_format_var,
                value=fmt,
                font=self.theme.FONTS["body"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_primary"],
                activebackground=self.theme.colors["bg_card"],
                selectcolor=self.theme.colors["bg_input"]
            ).pack(side=tk.LEFT, padx=(0, 16))
        
        # 提示信息
        tip_label = tk.Label(
            inner,
            text="💡 选择需要导出的语言分支，JSON格式会合并输出带语言标记的结果",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["primary"],
            anchor=tk.W
        )
        tip_label.pack(fill=tk.X)
    
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
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 显示结果按钮
        self.show_result_btn = tk.Button(
            btn_frame,
            text="📋 显示结果",
            font=self.theme.FONTS["body"],
            command=self._show_result_dialog,
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=8,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        self.show_result_btn.pack(side=tk.LEFT)
    
    def _create_result_section(self):
        """创建结果区域"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.X)
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.X, padx=20, pady=20)
        
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
    
    def _start_extraction(self):
        """开始提取"""
        # 检查至少有一个勾选的语言目录
        selected_dirs = {}
        if self.zh_check_var.get() and self.zh_dir_var.get():
            selected_dirs['zh'] = self.zh_dir_var.get()
        if self.vn_check_var.get() and self.vn_dir_var.get():
            selected_dirs['vn'] = self.vn_dir_var.get()
        if self.th_check_var.get() and self.th_dir_var.get():
            selected_dirs['th'] = self.th_dir_var.get()
        
        if not selected_dirs:
            self.show_warning("警告", "请选择至少一个语言目录")
            return
        
        # 验证目录是否存在
        for lang, dir_path in selected_dirs.items():
            if not Path(dir_path).exists():
                lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
                self.show_error("错误", f"{lang_names.get(lang, lang)}目录不存在: {dir_path}")
                return
        
        self.extract_btn.configure(state=tk.DISABLED)
        self.stats_label.configure(text="提取中...")
        
        thread = threading.Thread(target=self._do_extraction, args=(selected_dirs,), daemon=True)
        thread.start()
    
    def _do_extraction(self, selected_dirs: dict):
        """执行提取"""
        try:
            from core.excel_field_extractor import ExcelFieldExtractor
            
            if not self.extractor:
                self.extractor = ExcelFieldExtractor()
            
            # 清空之前的日志
            self.extractor.clear_logs()
            
            output_dir = self.output_dir_var.get() or None
            recursive = self.recursive_var.get()
            output_format = self.output_format_var.get()
            
            # 设置进度回调（关键！）
            def progress_callback(msg, pct=None):
                self.after(0, lambda: self._update_progress(msg, pct))
            
            self.extractor.set_progress_callback(progress_callback)
            
            # 使用多语言处理方法
            result = self.extractor.process_multi_language_directories(
                directories=selected_dirs,
                output_folder=output_dir,
                output_format=output_format,
                recursive=recursive
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
        """完成处理"""
        self.extract_btn.configure(state=tk.NORMAL)
        self.progress_fill.place(relwidth=1)
        
        # 保存结果供后续查看
        self.last_result = result
        
        if isinstance(result, dict):
            total_files = result.get('total_files', 0)
            total_sheets = result.get('total_sheets', 0)
            total_fields = result.get('total_fields', 0)
            languages = result.get('languages', {})
            output_files = result.get('output_files', [])
            
            lang_str = ", ".join([v.get('name', k) for k, v in languages.items()])
            self.stats_label.configure(
                text=f"✅ 完成：{len(languages)}个语言({lang_str})，{total_files}个文件，{total_fields}个字段", 
                fg=self.theme.colors["success"]
            )
            
            # 显示输出文件路径
            if output_files:
                self.show_info("提取完成", f"已生成 {len(output_files)} 个输出文件:\n\n" + "\n".join(output_files))
        else:
            self.stats_label.configure(text="✅ 完成", fg=self.theme.colors["success"])
    
    def _on_error(self, error_msg: str):
        """错误处理"""
        self.extract_btn.configure(state=tk.NORMAL)
        self.stats_label.configure(text="❌ 失败", fg=self.theme.colors["error"])
        self.show_error("错误", error_msg)
    
    def _clear_results(self):
        """清空结果"""
        self.stats_label.configure(text="", fg=self.theme.colors["text_muted"])
        self.progress_fill.place(relwidth=0)
        self.last_result = None
    
    def _show_result_dialog(self):
        """显示结果弹窗"""
        if self.last_result is None:
            self.show_warning("提示", "暂无执行结果，请先执行字段提取操作。")
            return
        
        result = self.last_result
        if isinstance(result, dict):
            total_files = result.get('total_files', 0)
            total_sheets = result.get('total_sheets', 0)
            total_fields = result.get('total_fields', 0)
            languages = result.get('languages', {})
            output_files = result.get('output_files', [])
            
            msg = f"字段提取结果\n\n"
            msg += f"处理语言数: {len(languages)}\n"
            msg += f"总文件数: {total_files}\n"
            msg += f"总工作表数: {total_sheets}\n"
            msg += f"总字段数: {total_fields}\n\n"
            
            # 显示各语言详情
            if languages:
                msg += "各语言详情:\n"
                for lang_code, lang_info in languages.items():
                    lang_name = lang_info.get('name', lang_code)
                    stats = lang_info.get('stats', {})
                    files = stats.get('total_files', 0)
                    fields = stats.get('total_fields', 0)
                    msg += f"  • {lang_name}: {files} 个文件, {fields} 个字段\n"
            
            # 显示输出文件
            if output_files:
                msg += f"\n输出文件:\n"
                for f in output_files:
                    msg += f"  • {f}\n"
            
            self.show_info("执行结果", msg)
        else:
            self.show_info("执行结果", "字段提取已完成！")
