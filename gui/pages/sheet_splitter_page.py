# -*- coding: utf-8 -*-
"""
GameTools 分页拆分页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess
from pathlib import Path

from gui.pages.base_page import ModernPage


class SheetSplitterPage(ModernPage):
    """分页拆分页面"""
    
    PAGE_KEY = "sheet_splitter"
    PAGE_TITLE = "分页拆分"
    PAGE_ICON = "✂️"
    PAGE_DESCRIPTION = "按首列分组将Excel数据拆分到多个工作表"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        self._output_file = None
        super().__init__(parent, app, theme)
    
    def _init_processor(self):
        """初始化处理器"""
        if self.processor is None:
            try:
                from core.excel_sheet_splitter import ExcelSheetSplitter
                self.processor = ExcelSheetSplitter()
            except ImportError as e:
                print(f"警告: 无法导入ExcelSheetSplitter: {e}")
    
    def create_widgets(self):
        """创建页面控件"""
        # 初始化处理器
        self._init_processor()
        
        # 输入文件配置卡片
        self._create_input_card()
        
        # 输出配置卡片
        self._create_output_card()
        
        # 选项配置卡片
        self._create_options_card()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 结果显示区域
        self._create_result_section()
    
    def _create_input_card(self):
        """创建输入文件配置卡片"""
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
            text="📁 输入文件",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # Excel文件选择
        file_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        file_row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            file_row,
            text="Excel文件",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.input_var = tk.StringVar()
        entry_frame = tk.Frame(
            file_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=self.input_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            file_row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=self._browse_input_file,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
        
        # 工作表选择
        sheet_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        sheet_row.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            sheet_row,
            text="工作表",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.sheet_var = tk.StringVar()
        self.sheet_combo = ttk.Combobox(
            sheet_row,
            textvariable=self.sheet_var,
            state="readonly",
            width=30
        )
        self.sheet_combo.pack(side=tk.LEFT, padx=(0, 16))
        
        tk.Label(
            sheet_row,
            text="分组列:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.group_column_var = tk.StringVar()
        group_entry = tk.Frame(
            sheet_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        group_entry.pack(side=tk.LEFT)
        
        tk.Entry(
            group_entry,
            textvariable=self.group_column_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            width=10
        ).pack(padx=6, pady=4)
        
        tk.Label(
            sheet_row,
            text="(留空=自动检测)",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"]
        ).pack(side=tk.LEFT, padx=(8, 0))
    
    def _create_output_card(self):
        """创建输出配置卡片"""
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
            text="📤 输出设置",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 输出文件
        output_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        output_row.pack(fill=tk.X)
        
        tk.Label(
            output_row,
            text="输出文件",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.output_var = tk.StringVar()
        entry_frame = tk.Frame(
            output_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=self.output_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            output_row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=self._browse_output_file,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
    
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
            text="⚙️ 选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 选项行
        options_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        options_row.pack(fill=tk.X)
        
        self.extract_filename_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="从文件名提取信息",
            variable=self.extract_filename_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.include_summary_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="包含汇总页",
            variable=self.include_summary_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.remove_first_col_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="移除第一列",
            variable=self.remove_first_col_var,
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
        
        # 开始拆分按钮
        self.process_button = tk.Button(
            button_frame,
            text="✂️ 开始拆分",
            font=self.theme.FONTS["body"],
            command=self._start_split,
            bg=self.theme.colors["primary"],
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空按钮
        tk.Button(
            button_frame,
            text="🗑️ 清空",
            font=self.theme.FONTS["body"],
            command=self._clear_results,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 打开输出目录按钮
        self.open_folder_button = tk.Button(
            button_frame,
            text="📂 打开输出目录",
            font=self.theme.FONTS["body"],
            command=self._open_output_folder,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            state="disabled"
        )
        self.open_folder_button.pack(side=tk.LEFT)
    
    def _create_result_section(self):
        """创建结果显示区域"""
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
        title = tk.Label(
            inner,
            text="📋 处理结果",
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
    
    def _browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)
            # 自动设置输出文件名
            if not self.output_var.get():
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_分页拆分.xlsx"
                self.output_var.set(str(output_path))
            # 加载工作表列表
            self._load_sheet_names(file_path)
    
    def _load_sheet_names(self, file_path):
        """加载Excel文件的工作表名称列表"""
        if not self.processor:
            return
        try:
            sheet_names = self.processor.get_sheet_names(file_path)
            self.sheet_combo['values'] = sheet_names
            if sheet_names:
                self.sheet_combo.set(sheet_names[0])
        except Exception as e:
            self.sheet_combo['values'] = []
            self.sheet_combo.set('')
    
    def _browse_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存拆分后的Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_var.set(file_path)
    
    def _start_split(self):
        """开始Excel分页拆分"""
        input_file = self.input_var.get().strip()
        output_file = self.output_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请设置输出文件")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        if not self.processor:
            messagebox.showerror("错误", "分页拆分模块未正确加载")
            return
        
        # 禁用按钮
        self.process_button.config(state="disabled")
        self.open_folder_button.config(state="disabled")
        self.update_status("正在拆分Excel数据...")
        
        thread = threading.Thread(target=self._split_process, 
                                  args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _split_process(self, input_file, output_file):
        """Excel分页拆分处理（后台线程）"""
        try:
            # 清空结果
            self.after(0, self._clear_results)
            
            # 显示开始信息
            self.after(0, lambda: self._append_result(f"开始处理文件: {input_file}\n"))
            self.after(0, lambda: self._append_result(f"输出文件: {output_file}\n"))
            self.after(0, lambda: self._append_result("-" * 50 + "\n"))
            
            # 获取选项
            sheet_name = self.sheet_var.get().strip() or None
            group_column = self.group_column_var.get().strip() or None
            extract_filename = self.extract_filename_var.get()
            include_summary = self.include_summary_var.get()
            remove_first_column = self.remove_first_col_var.get()
            
            # 执行处理
            success, report = self.processor.process_file(
                input_path=input_file,
                output_path=output_file,
                sheet_name=sheet_name,
                group_column=group_column,
                extract_filename=extract_filename,
                include_summary=include_summary,
                remove_first_column=remove_first_column
            )
            
            # 显示结果
            if success:
                self.after(0, lambda: self._show_success_result(report, output_file))
            else:
                self.after(0, lambda: self._show_error_result(report))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.after(0, lambda: self._show_error_result(error_msg))
    
    def _show_success_result(self, report, output_file):
        """显示成功结果"""
        self.process_button.config(state="normal")
        self.open_folder_button.config(state="normal")
        self.update_status("Excel分页拆分完成")
        
        # 保存输出文件路径用于打开文件夹
        self._output_file = output_file
        
        messagebox.showinfo("成功", f"Excel分页拆分完成！\n\n输出文件: {output_file}")
    
    def _show_error_result(self, error_msg):
        """显示错误结果"""
        self.process_button.config(state="normal")
        self.update_status("Excel分页拆分失败")
        
        messagebox.showerror("错误", error_msg)
    
    def _append_result(self, text):
        """追加结果文本"""
        # 结果文本框已移除，此方法保留但不执行操作
        pass
    
    def _clear_results(self):
        """清空结果"""
        if hasattr(self, 'status_info_label'):
            self.status_info_label.configure(text="就绪")
    
    def _open_output_folder(self):
        """打开输出文件所在的文件夹"""
        try:
            if self._output_file and os.path.exists(self._output_file):
                folder_path = os.path.dirname(self._output_file)
                if sys.platform == 'win32':
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            else:
                messagebox.showwarning("提示", "输出文件不存在，请先执行拆分操作")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
