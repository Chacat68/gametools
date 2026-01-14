# -*- coding: utf-8 -*-
"""
GameTools 配置同步页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json

from gui.pages.base_page import ModernPage


class ConfigSyncPage(ModernPage):
    """配置同步页面"""
    
    PAGE_KEY = "config_sync"
    PAGE_TITLE = "配置同步"
    PAGE_ICON = "🔗"
    PAGE_DESCRIPTION = "将Excel配置从源目录同步到目标目录"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        self.last_result = None  # 保存最后一次执行结果
        super().__init__(parent, app, theme)
    
    def _init_processor(self):
        """初始化处理器"""
        if self.processor is None:
            try:
                from core.excel_config_sync import ExcelConfigSync
                self.processor = ExcelConfigSync()
            except ImportError as e:
                print(f"警告: 无法导入ExcelConfigSync: {e}")
    
    def create_widgets(self):
        """创建页面控件"""
        # 初始化处理器
        self._init_processor()
        
        # 目录配置卡片
        self._create_directory_card()
        
        # 选项配置卡片
        self._create_options_card()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 结果显示区域
        self._create_result_section()
    
    def _create_directory_card(self):
        """创建目录配置卡片"""
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
            text="📁 目录配置（同步Excel配置到其他目录）",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 源目录
        self.source_dir_var = tk.StringVar()
        self._create_dir_row(inner, "源目录", self.source_dir_var, self._browse_source_dir)
        
        # 目标目录1
        self.target1_dir_var = tk.StringVar()
        self._create_dir_row(inner, "目标目录1", self.target1_dir_var, self._browse_target1_dir)
        
        # 目标目录2
        self.target2_dir_var = tk.StringVar()
        self._create_dir_row(inner, "目标目录2", self.target2_dir_var, self._browse_target2_dir)
        
        # JSON配置文件
        self.json_var = tk.StringVar()
        self._create_file_row(inner, "JSON配置", self.json_var, self._browse_json_file, "(可选，仅用于参考)")
        
        # 过滤配置文件
        filter_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        filter_row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            filter_row,
            text="过滤配置",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar()
        entry_frame = tk.Frame(
            filter_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=self.filter_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            filter_row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=self._browse_filter_file,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            filter_row,
            text="预览",
            font=self.theme.FONTS["small"],
            command=self._preview_filter_config,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
        
        # 过滤配置说明
        tk.Label(
            inner,
            text="💡 过滤配置：可选，指定要跳过同步的字段",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 12))
        
        # 报告文件
        self.report_var = tk.StringVar()
        self._create_file_row(inner, "报告文件", self.report_var, self._browse_report_file, "(输出同步报告)")
    
    def _create_dir_row(self, parent, label, var, browse_cmd):
        """创建目录选择行"""
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
    
    def _create_file_row(self, parent, label, var, browse_cmd, hint=""):
        """创建文件选择行"""
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
            text="⚙️ 同步选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 选项行
        options_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        options_row.pack(fill=tk.X)
        
        self.backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="同步前备份",
            variable=self.backup_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        self.values_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="同步单元格值",
            variable=self.values_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        self.formulas_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="同步公式",
            variable=self.formulas_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        self.styles_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="同步样式",
            variable=self.styles_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        self.column_widths_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="同步列宽",
            variable=self.column_widths_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT)
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        button_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 开始同步按钮
        self.process_button = tk.Button(
            button_frame,
            text="🚀 开始同步",
            font=self.theme.FONTS["body"],
            command=self._start_sync,
            bg=self.theme.colors["primary"],
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 预览匹配按钮
        tk.Button(
            button_frame,
            text="👁️ 预览匹配",
            font=self.theme.FONTS["body"],
            command=self._preview_matching,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空按钮
        tk.Button(
            button_frame,
            text="🗑️ 清空结果",
            font=self.theme.FONTS["body"],
            command=self._clear_results,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 显示结果按钮
        self.show_result_btn = tk.Button(
            button_frame,
            text="📋 显示结果",
            font=self.theme.FONTS["body"],
            command=self._show_result_dialog,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8
        )
        self.show_result_btn.pack(side=tk.LEFT)
    
    def _create_result_section(self):
        """创建结果显示区域"""
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
        title = tk.Label(
            inner,
            text="📋 同步结果",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 状态标签
        self.status_info_label = tk.Label(
            inner,
            text="就绪",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        )
        self.status_info_label.pack(fill=tk.X)
    
    # ==================== 事件处理方法 ====================
    
    def _browse_source_dir(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_dir_var.set(directory)
    
    def _browse_target1_dir(self):
        """浏览目标目录1"""
        directory = filedialog.askdirectory(title="选择目标目录1")
        if directory:
            self.target1_dir_var.set(directory)
    
    def _browse_target2_dir(self):
        """浏览目标目录2"""
        directory = filedialog.askdirectory(title="选择目标目录2")
        if directory:
            self.target2_dir_var.set(directory)
    
    def _browse_json_file(self):
        """浏览JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.json_var.set(file_path)
    
    def _browse_filter_file(self):
        """浏览过滤配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择字段过滤配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.filter_var.set(file_path)
    
    def _browse_report_file(self):
        """浏览报告输出位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.report_var.set(file_path)
    
    def _preview_filter_config(self):
        """预览过滤配置"""
        filter_file = self.filter_var.get().strip()
        
        if not filter_file:
            messagebox.showwarning("提示", "请先选择过滤配置文件")
            return
        
        if not os.path.exists(filter_file):
            messagebox.showerror("错误", "过滤配置文件不存在")
            return
        
        try:
            with open(filter_file, 'r', encoding='utf-8') as f:
                filter_config = json.load(f)
            
            # 解析过滤配置
            skip_fields = {}
            
            if 'skip_fields' in filter_config:
                skip_fields = filter_config['skip_fields']
            elif 'text_tables' in filter_config:
                for table_info in filter_config['text_tables']:
                    table_name = table_info.get('table_name', '')
                    fields = table_info.get('skip_fields', [])
                    if table_name and fields:
                        skip_fields[table_name] = fields
            
            # 生成预览内容
            preview_lines = []
            preview_lines.append("=" * 60)
            preview_lines.append("字段过滤配置预览")
            preview_lines.append("=" * 60)
            preview_lines.append(f"\n配置文件: {os.path.basename(filter_file)}")
            preview_lines.append(f"包含表数: {len(skip_fields)}")
            preview_lines.append("\n" + "-" * 60)
            preview_lines.append("过滤详情:")
            preview_lines.append("-" * 60)
            
            if skip_fields:
                for table_name, fields in skip_fields.items():
                    preview_lines.append(f"\n📄 {table_name}")
                    preview_lines.append(f"   跳过字段 ({len(fields)}): {', '.join(fields)}")
            else:
                preview_lines.append("\n⚠️ 没有配置过滤字段")
            
            # 显示在结果区
            self._clear_results()
            self._append_result("\n".join(preview_lines))
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败: {str(e)}")
    
    def _preview_matching(self):
        """预览匹配的文件"""
        if not self.processor:
            messagebox.showerror("错误", "配置同步模块未正确加载")
            return
        
        source_dir = self.source_dir_var.get().strip()
        target1_dir = self.target1_dir_var.get().strip()
        target2_dir = self.target2_dir_var.get().strip()
        
        if not source_dir:
            messagebox.showerror("错误", "请选择源目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        if not target1_dir and not target2_dir:
            messagebox.showerror("错误", "请至少选择一个目标目录")
            return
        
        # 构建目标目录列表
        target_dirs = []
        if target1_dir and os.path.exists(target1_dir):
            target_dirs.append(target1_dir)
        if target2_dir and os.path.exists(target2_dir):
            target_dirs.append(target2_dir)
        
        if not target_dirs:
            messagebox.showerror("错误", "没有有效的目标目录")
            return
        
        # 查找匹配的文件
        matching_files = self.processor.find_matching_files(source_dir, target_dirs)
        
        # 生成预览内容
        preview_lines = []
        preview_lines.append("=" * 60)
        preview_lines.append("文件匹配预览")
        preview_lines.append("=" * 60)
        preview_lines.append(f"\n源目录: {source_dir}")
        preview_lines.append(f"目标目录1: {target1_dir or '(未选择)'}")
        preview_lines.append(f"目标目录2: {target2_dir or '(未选择)'}")
        preview_lines.append(f"\n源目录文件数: {self.processor.processing_stats.get('source_files', 0)}")
        preview_lines.append(f"匹配的文件数: {len(matching_files)}")
        preview_lines.append("\n" + "-" * 60)
        preview_lines.append("匹配详情:")
        preview_lines.append("-" * 60)
        
        for filename, info in matching_files.items():
            preview_lines.append(f"\n📄 {filename}")
            preview_lines.append(f"   源文件: {info['source']}")
            for idx, target in enumerate(info['targets'], 1):
                preview_lines.append(f"   目标{idx}: {target}")
        
        if not matching_files:
            preview_lines.append("\n⚠️ 没有找到匹配的文件")
        
        # 显示在结果区
        self._clear_results()
        self._append_result("\n".join(preview_lines))
    
    def _start_sync(self):
        """开始配置同步"""
        if not self.processor:
            messagebox.showerror("错误", "配置同步模块未正确加载")
            return
        
        source_dir = self.source_dir_var.get().strip()
        target1_dir = self.target1_dir_var.get().strip()
        target2_dir = self.target2_dir_var.get().strip()
        json_file = self.json_var.get().strip()
        filter_file = self.filter_var.get().strip()
        report_file = self.report_var.get().strip()
        
        # 验证参数
        if not source_dir:
            messagebox.showerror("错误", "请选择源目录")
            return
        
        if not os.path.exists(source_dir):
            messagebox.showerror("错误", "源目录不存在")
            return
        
        if not target1_dir and not target2_dir:
            messagebox.showerror("错误", "请至少选择一个目标目录")
            return
        
        if target1_dir and not os.path.exists(target1_dir):
            messagebox.showerror("错误", "目标目录1不存在")
            return
        
        if target2_dir and not os.path.exists(target2_dir):
            messagebox.showerror("错误", "目标目录2不存在")
            return
        
        # 确认操作
        confirm_msg = f"""确认开始同步配置？

源目录: {source_dir}
目标目录1: {target1_dir or '(未选择)'}
目标目录2: {target2_dir or '(未选择)'}
JSON配置: {os.path.basename(json_file) if json_file else '(未选择)'}
过滤配置: {os.path.basename(filter_file) if filter_file else '(未选择)'}

同步选项:
- 备份: {'是' if self.backup_var.get() else '否'}
- 同步值: {'是' if self.values_var.get() else '否'}
- 同步公式: {'是' if self.formulas_var.get() else '否'}
- 同步样式: {'是' if self.styles_var.get() else '否'}
- 同步列宽: {'是' if self.column_widths_var.get() else '否'}"""
        
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        # 开始处理
        self.process_button.config(state="disabled")
        self.update_status("正在同步配置...")
        
        thread = threading.Thread(target=self._sync_thread, 
                                  args=(source_dir, target1_dir, target2_dir, 
                                        json_file, filter_file, report_file))
        thread.daemon = True
        thread.start()
    
    def _sync_thread(self, source_dir, target1_dir, target2_dir, 
                     json_file, filter_file, report_file):
        """配置同步处理线程"""
        try:
            # 清空结果
            self.after(0, self._clear_results)
            
            # 显示开始信息
            self.after(0, lambda: self._append_result("=" * 70 + "\n"))
            self.after(0, lambda: self._append_result("开始同步Excel配置...\n"))
            self.after(0, lambda: self._append_result("=" * 70 + "\n"))
            self.after(0, lambda: self._append_result(f"源目录: {source_dir}\n"))
            self.after(0, lambda: self._append_result(f"目标目录1: {target1_dir or '(未选择)'}\n"))
            self.after(0, lambda: self._append_result(f"目标目录2: {target2_dir or '(未选择)'}\n"))
            if json_file:
                self.after(0, lambda: self._append_result(f"JSON配置: {json_file}\n"))
            if filter_file:
                self.after(0, lambda: self._append_result(f"过滤配置: {filter_file}\n"))
            self.after(0, lambda: self._append_result("\n"))
            
            # 设置同步选项
            self.processor.sync_options['backup_before_sync'] = self.backup_var.get()
            self.processor.sync_options['sync_values'] = self.values_var.get()
            self.processor.sync_options['sync_formulas'] = self.formulas_var.get()
            self.processor.sync_options['sync_styles'] = self.styles_var.get()
            self.processor.sync_options['sync_column_widths'] = self.column_widths_var.get()
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.after(0, lambda m=msg: self._append_result(m + "\n"))
            
            self.processor.set_progress_callback(progress_callback)
            
            # 加载JSON配置（如果有）
            if json_file and os.path.exists(json_file):
                self.after(0, lambda: self._append_result("正在加载JSON配置（仅用于参考）...\n"))
                self.processor.load_json_config(json_file)
                self.after(0, lambda: self._append_result("✓ JSON配置已加载\n\n"))
            
            # 加载过滤配置（如果有）
            if filter_file and os.path.exists(filter_file):
                self.after(0, lambda: self._append_result("正在加载过滤配置...\n"))
                self.processor.load_filter_config(filter_file)
                skip_count = len(self.processor.skip_fields)
                self.after(0, lambda: self._append_result(f"✓ 过滤配置已加载，包含 {skip_count} 个表的过滤规则\n\n"))
            
            # 执行同步
            stats = self.processor.sync_directories(
                source_dir=source_dir,
                target_dir1=target1_dir if target1_dir else None,
                target_dir2=target2_dir if target2_dir else None
            )
            
            # 显示统计信息
            summary = self.processor.get_stats_summary()
            self.after(0, lambda: self._append_result("\n" + summary + "\n"))
            
            # 保存结果供后续查看
            self.after(0, lambda: self._save_result({
                'stats': stats.copy() if stats else {},
                'summary': summary,
                'report_file': report_file
            }))
            
            # 生成报告
            if report_file:
                self.after(0, lambda: self._append_result(f"\n正在生成报告: {report_file}\n"))
                if self.processor.generate_sync_report(report_file):
                    self.after(0, lambda: self._append_result("✓ 报告生成成功\n"))
                else:
                    self.after(0, lambda: self._append_result("✗ 报告生成失败\n"))
            
            # 完成
            self.after(0, lambda: self.update_status("✅ 完成（点击【显示结果】查看详情）"))
            
        except Exception as e:
            error_msg = f"同步过程出错: {str(e)}"
            self.after(0, lambda: self._append_result(f"\n✗ 错误: {error_msg}\n"))
            self.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.after(0, lambda: self.process_button.config(state="normal"))
    
    def _save_result(self, result):
        """保存结果"""
        self.last_result = result
    
    def _append_result(self, text):
        """追加结果文本"""
        # 结果文本框已移除，此方法保留但不执行操作
        pass
    
    def _clear_results(self):
        """清空结果"""
        if hasattr(self, 'status_info_label'):
            self.status_info_label.configure(text="就绪")
        self.last_result = None
    
    def _show_result_dialog(self):
        """显示结果弹窗"""
        if self.last_result is None:
            self.show_warning("提示", "暂无执行结果，请先执行配置同步操作。")
            return
        
        result = self.last_result
        stats = result.get('stats', {})
        
        msg = f"配置同步结果\n\n"
        msg += f"源文件数: {stats.get('source_files', 0)}\n"
        msg += f"同步文件数: {stats.get('synced_files', 0)}\n"
        msg += f"同步单元格: {stats.get('synced_cells', 0)}\n"
        msg += f"跳过单元格: {stats.get('skipped_cells', 0)}\n"
        msg += f"错误数: {stats.get('errors', 0)}\n"
        
        if result.get('report_file'):
            msg += f"\n报告文件:\n{result['report_file']}"
        
        self.show_info("执行结果", msg)
