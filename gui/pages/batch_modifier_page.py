# -*- coding: utf-8 -*-
"""
GameTools 批量改表页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from pathlib import Path

from gui.pages.base_page import ModernPage


class BatchModifierPage(ModernPage):
    """批量改表页面"""
    
    PAGE_KEY = "batch_modifier"
    PAGE_TITLE = "批量改表"
    PAGE_ICON = "⚡"
    PAGE_DESCRIPTION = "根据映射表批量修改Excel配置文件"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建页面控件"""
        # 文件配置卡片
        self._create_file_config_card()
        
        # 选项配置卡片
        self._create_options_card()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 进度和结果区域
        self._create_progress_section()
    
    def _create_file_config_card(self):
        """创建文件配置卡片"""
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
        title = tk.Label(
            inner,
            text="📁 文件配置",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # JSON 配置文件
        self._create_file_row(inner, "JSON配置", "json_var", 
                              self._browse_json, "(定义表和字段)")
        
        # 映射表文件 + 语言选择
        mapping_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        mapping_row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            mapping_row,
            text="映射表文件",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.mapping_var = tk.StringVar()
        entry_frame = tk.Frame(
            mapping_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.mapping_entry = tk.Entry(
            entry_frame,
            textvariable=self.mapping_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.mapping_entry.pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            mapping_row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=self._browse_mapping,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        # 语言选择
        tk.Label(
            mapping_row,
            text="语言:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.language_var = tk.StringVar(value="VN")
        self.language_combo = ttk.Combobox(
            mapping_row,
            textvariable=self.language_var,
            values=['VN', 'Support-CH', 'TH', 'EN', 'Polish-CH', 'VN.1'],
            state='readonly',
            width=12
        )
        self.language_combo.pack(side=tk.LEFT)
        
        # Excel 目录
        self._create_file_row(inner, "Excel目录", "excel_dir_var",
                              self._browse_excel_dir, "(要修改的配置表目录)")
        
        # 报告文件
        self._create_file_row(inner, "报告文件", "report_var",
                              self._browse_report, "(输出修改报告)")
        
        # JSON 语言标记
        self.json_lang_label = tk.Label(
            inner,
            text="",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["info"],
            anchor=tk.W
        )
        self.json_lang_label.pack(fill=tk.X)
    
    def _create_file_row(self, parent, label: str, var_name: str,
                         browse_cmd, hint: str = ""):
        """创建文件选择行"""
        row = tk.Frame(parent, bg=self.theme.colors["bg_card"])
        row.pack(fill=tk.X, pady=(0, 12))
        
        # 标签
        label_text = label + (" " + hint if hint else "")
        tk.Label(
            row,
            text=label,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        # 输入框
        var = tk.StringVar()
        setattr(self, var_name, var)
        
        entry_frame = tk.Frame(
            row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        entry = tk.Entry(
            entry_frame,
            textvariable=var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        )
        entry.pack(fill=tk.X, padx=8, pady=6)
        
        # 浏览按钮
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
        
        # 提示
        if hint:
            tk.Label(
                row,
                text=hint,
                font=self.theme.FONTS["small"],
                bg=self.theme.colors["bg_card"],
                fg=self.theme.colors["text_muted"]
            ).pack(side=tk.LEFT, padx=(8, 0))
    
    def _create_options_card(self):
        """创建选项配置卡片"""
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
        title = tk.Label(
            inner,
            text="⚙️ 处理选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 第一行选项
        row1 = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row1.pack(fill=tk.X, pady=(0, 12))
        
        self.backup_var = tk.BooleanVar(value=True)
        backup_check = tk.Checkbutton(
            row1,
            text="修改前创建备份文件（.bak）",
            variable=self.backup_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        )
        backup_check.pack(side=tk.LEFT, padx=(0, 24))
        
        tk.Label(
            row1,
            text="✓ 使用 xlwings 引擎（完全保留文件结构）",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["success"]
        ).pack(side=tk.LEFT)
        
        # 第二行：行号设置
        row2 = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row2.pack(fill=tk.X, pady=(0, 8))
        
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
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        tk.Label(
            row2,
            text="字段行:",
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
            text="⚠️ 小于数据起始行的将不会被修改（保护表头）",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["warning"]
        ).pack(side=tk.LEFT)
        
        # 第三行：定位模式说明
        tk.Label(
            inner,
            text="💡 定位模式：有 Position 列 → 直接定位单元格 | 无 Position 列 → ID 作为行号",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["info"],
            anchor=tk.W
        ).pack(fill=tk.X)
    
    def _create_action_buttons(self):
        """创建操作按钮区域"""
        btn_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 开始修改按钮
        self.start_btn = tk.Button(
            btn_frame,
            text="🚀 开始修改",
            font=("Microsoft YaHei", 10, "bold"),
            command=self._start_modification,
            bg=self.theme.colors["primary"],
            fg="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 预览按钮
        tk.Button(
            btn_frame,
            text="👁️ 预览映射表",
            font=self.theme.FONTS["body"],
            command=self._preview_mapping,
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=8,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空按钮
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
    
    def _create_progress_section(self):
        """创建进度和结果区域"""
        card = tk.Frame(
            self.content,
            bg=self.theme.colors["bg_card"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        inner = tk.Frame(card, bg=self.theme.colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题和状态
        header = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        header.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            header,
            text="📊 处理结果",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            header,
            text="就绪",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"]
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress_track = tk.Frame(
            inner,
            bg=self.theme.colors["bg_hover"],
            height=6
        )
        self.progress_track.pack(fill=tk.X, pady=(0, 12))
        self.progress_track.pack_propagate(False)
        
        self.progress_fill = tk.Frame(
            self.progress_track,
            bg=self.theme.colors["primary"],
            height=6
        )
        self.progress_fill.place(x=0, y=0, relheight=1, relwidth=0)
    
    # ==================== 浏览方法 ====================
    
    def _browse_json(self):
        """浏览 JSON 配置文件"""
        filepath = filedialog.askopenfilename(
            title="选择 JSON 配置文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            self.json_var.set(filepath)
            self._update_json_lang_label(filepath)
    
    def _browse_mapping(self):
        """浏览映射表文件"""
        filepath = filedialog.askopenfilename(
            title="选择映射表文件",
            filetypes=[
                ("Excel 和 CSV", "*.xlsx *.xls *.csv"),
                ("Excel 文件", "*.xlsx *.xls"),
                ("CSV 文件", "*.csv"),
                ("所有文件", "*.*")
            ]
        )
        if filepath:
            self.mapping_var.set(filepath)
    
    def _browse_excel_dir(self):
        """浏览 Excel 目录"""
        dirpath = filedialog.askdirectory(title="选择 Excel 配置目录")
        if dirpath:
            self.excel_dir_var.set(dirpath)
    
    def _browse_report(self):
        """浏览报告输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="保存修改报告",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            defaultextension=".txt"
        )
        if filepath:
            self.report_var.set(filepath)
    
    def _update_json_lang_label(self, json_path: str):
        """更新 JSON 语言标记显示"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'language' in config and isinstance(config['language'], dict):
                lang_name = config['language'].get('name', '')
                lang_code = config['language'].get('code', '')
                self.json_lang_label.config(text=f"📌 已加载配置: {lang_name} ({lang_code})")
            else:
                self.json_lang_label.config(text="⚠️ 配置文件无语言标记")
        except Exception as e:
            self.json_lang_label.config(text=f"⚠️ 读取失败: {str(e)}")
    
    # ==================== 操作方法 ====================
    
    def _start_modification(self):
        """开始批量修改"""
        # 验证输入
        if not self.json_var.get():
            self.show_warning("警告", "请选择 JSON 配置文件")
            return
        if not self.mapping_var.get():
            self.show_warning("警告", "请选择映射表文件")
            return
        if not self.excel_dir_var.get():
            self.show_warning("警告", "请选择 Excel 目录")
            return
        
        # 确认对话框
        if not self.ask_yes_no("确认", "确定要开始批量修改吗？\n建议先预览映射表确认内容正确。"):
            return
        
        # 禁用按钮
        self.start_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="处理中...", fg=self.theme.colors["info"])
        
        # 启动线程
        thread = threading.Thread(target=self._do_modification, daemon=True)
        thread.start()
    
    def _do_modification(self):
        """执行修改（后台线程）"""
        try:
            # 导入处理器
            from core.batch_excel_modifier import BatchExcelModifier
            
            if not self.processor:
                self.processor = BatchExcelModifier()
            
            # 设置进度回调
            def progress_callback(message, percentage=None):
                self.after(0, lambda: self._update_progress(message, percentage))
            
            self.processor.set_progress_callback(progress_callback)
            
            # 执行处理
            json_path = self.json_var.get()
            mapping_path = self.mapping_var.get()
            excel_dir = self.excel_dir_var.get()
            report_path = self.report_var.get() or None
            language = self.language_var.get()
            backup = self.backup_var.get()
            data_start_row = int(self.data_start_row_var.get())
            field_row = int(self.field_row_var.get())
            
            result = self.processor.process_batch_modification(
                json_path=json_path,
                mapping_path=mapping_path,
                excel_directory=excel_dir,
                target_language=language,
                create_backup=backup,
                data_start_row=data_start_row,
                field_row=field_row,
                report_path=report_path
            )
            
            # 完成
            self.after(0, lambda: self._on_complete(result))
            
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))
    
    def _update_progress(self, message: str, percentage: float = None):
        """更新进度显示"""
        self.status_label.configure(text=message)
        if percentage is not None:
            self.progress_fill.place(relwidth=percentage / 100)
    
    def _on_complete(self, result):
        """处理完成"""
        self.start_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="✅ 处理完成", fg=self.theme.colors["success"])
        self.progress_fill.place(relwidth=1)
        
        # 显示统计
        if isinstance(result, dict):
            msg = f"批量修改已完成！\n\n修改文件数: {result.get('modified_files', 0)}\n修改单元格: {result.get('modified_cells', 0)}\n跳过记录数: {result.get('skipped', 0)}\n错误数: {result.get('errors', 0)}"
            self.show_info("完成", msg)
        else:
            self.show_info("完成", "批量修改已完成！")
    
    def _on_error(self, error_msg: str):
        """处理错误"""
        self.start_btn.configure(state=tk.NORMAL)
        self.status_label.configure(text="❌ 处理失败", fg=self.theme.colors["error"])
        self.show_error("错误", error_msg)
    
    def _preview_mapping(self):
        """预览映射表"""
        mapping_path = self.mapping_var.get()
        if not mapping_path:
            self.show_warning("警告", "请先选择映射表文件")
            return
        
        try:
            import pandas as pd
            df = pd.read_excel(mapping_path) if mapping_path.endswith(('.xlsx', '.xls')) \
                else pd.read_csv(mapping_path)
            
            preview = f"映射表预览: {Path(mapping_path).name}\n"
            preview += f"行数: {len(df)}, 列数: {len(df.columns)}\n"
            preview += f"列名: {', '.join(df.columns.tolist())}\n\n"
            preview += f"前10行数据:\n{df.head(10).to_string()}"
            
            self.show_info("映射表预览", preview)
        except Exception as e:
            self.show_error("预览失败", str(e))
    
    def _clear_results(self):
        """清空结果"""
        self.status_label.configure(text="就绪", fg=self.theme.colors["text_muted"])
        self.progress_fill.place(relwidth=0)
