# -*- coding: utf-8 -*-
"""
GameTools 数据处理页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess
from pathlib import Path

from gui.pages.base_page import ModernPage


class ExcelProcessorPage(ModernPage):
    """Excel数据处理页面"""
    
    PAGE_KEY = "excel_processor"
    PAGE_TITLE = "数据处理"
    PAGE_ICON = "📊"
    PAGE_DESCRIPTION = "根据A列内容对Excel数据进行分组拆分处理"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        self._output_file = None
        self.last_result = None  # 保存最后一次执行结果
        super().__init__(parent, app, theme)
    
    def _init_processor(self):
        """初始化处理器"""
        if self.processor is None:
            try:
                from tools.excel_data_processor import ExcelDataProcessor
                self.processor = ExcelDataProcessor()
            except ImportError as e:
                print(f"警告: 无法导入ExcelDataProcessor: {e}")
    
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
            width=15
        ).pack(padx=6, pady=4)
        
        tk.Label(
            sheet_row,
            text="(默认=A列)",
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
        
        # 输出目录
        output_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        output_row.pack(fill=tk.X)
        
        tk.Label(
            output_row,
            text="输出目录",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        entry_frame = tk.Frame(
            output_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=self.output_dir_var,
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
            command=self._browse_output_dir,
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
            text="⚙️ 处理选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 选项行
        options_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        options_row.pack(fill=tk.X)
        
        self.split_files_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="拆分为多个文件",
            variable=self.split_files_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.include_header_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="包含表头",
            variable=self.include_header_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.remove_group_col_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="移除分组列",
            variable=self.remove_group_col_var,
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
        
        # 开始处理按钮
        self.process_button = tk.Button(
            button_frame,
            text="📊 开始处理",
            font=self.theme.FONTS["body"],
            command=self._start_process,
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
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 8))
        
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
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)
            # 自动设置输出目录
            if not self.output_dir_var.get():
                output_dir = os.path.dirname(file_path)
                self.output_dir_var.set(output_dir)
            # 加载工作表列表
            self._load_sheet_names(file_path)
    
    def _load_sheet_names(self, file_path):
        """加载Excel文件的工作表名称列表"""
        try:
            import pandas as pd
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names
            self.sheet_combo['values'] = sheet_names
            if sheet_names:
                self.sheet_combo.set(sheet_names[0])
        except Exception as e:
            self.sheet_combo['values'] = []
            self.sheet_combo.set('')
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def _start_process(self):
        """开始Excel数据处理"""
        input_file = self.input_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not output_dir:
            messagebox.showerror("错误", "请设置输出目录")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "输入文件不存在")
            return
        
        if not self.processor:
            messagebox.showerror("错误", "数据处理模块未正确加载")
            return
        
        # 禁用按钮
        self.process_button.config(state="disabled")
        self.open_folder_button.config(state="disabled")
        self.update_status("正在处理Excel数据...")
        
        thread = threading.Thread(target=self._process_thread, 
                                  args=(input_file, output_dir))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, input_file, output_dir):
        """Excel数据处理（后台线程）"""
        try:
            # 清空结果
            self.after(0, self._clear_results)
            
            # 显示开始信息
            self.after(0, lambda: self._append_result(f"开始处理文件: {input_file}\n"))
            self.after(0, lambda: self._append_result(f"输出目录: {output_dir}\n"))
            self.after(0, lambda: self._append_result("-" * 50 + "\n"))
            
            # 获取选项
            sheet_name = self.sheet_var.get().strip() or None
            group_column = self.group_column_var.get().strip() or None
            split_files = self.split_files_var.get()
            include_header = self.include_header_var.get()
            
            # 读取Excel文件
            df = self.processor.read_excel_file(input_file, sheet_name)
            self.after(0, lambda: self._append_result(f"读取成功，共 {len(df)} 行数据\n"))
            
            # 按列分组
            grouped_data = self.processor.process_by_column_a(df, group_column)
            
            self.after(0, lambda: self._append_result(f"分组完成，共 {len(grouped_data)} 个分组\n\n"))
            
            # 显示分组信息
            for group_name, group_df in grouped_data.items():
                self.after(0, lambda gn=group_name, gdf=group_df: 
                    self._append_result(f"  - {gn}: {len(gdf)} 行\n"))
            
            # 导出结果
            self.after(0, lambda: self._append_result("\n正在导出数据...\n"))
            
            if split_files:
                # 拆分为多个文件
                for group_name, group_df in grouped_data.items():
                    safe_name = str(group_name).replace('/', '_').replace('\\', '_')
                    output_file = os.path.join(output_dir, f"{safe_name}.xlsx")
                    group_df.to_excel(output_file, index=False)
                    self.after(0, lambda of=output_file: 
                        self._append_result(f"  ✓ 已导出: {of}\n"))
            else:
                # 导出为单个文件的多个工作表
                base_name = Path(input_file).stem
                output_file = os.path.join(output_dir, f"{base_name}_分组处理.xlsx")
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    for group_name, group_df in grouped_data.items():
                        safe_name = str(group_name)[:31].replace('/', '_').replace('\\', '_')
                        group_df.to_excel(writer, sheet_name=safe_name, index=False)
                self.after(0, lambda of=output_file: 
                    self._append_result(f"  ✓ 已导出: {of}\n"))
            
            # 计算统计信息
            total_rows = sum(len(gdf) for gdf in grouped_data.values())
            group_count = len(grouped_data)
            self.after(0, lambda: self._show_success_result(output_dir, total_rows, group_count))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.after(0, lambda: self._show_error_result(error_msg))
    
    def _show_success_result(self, output_dir, total_rows=0, group_count=0):
        """显示成功结果"""
        self.process_button.config(state="normal")
        self.open_folder_button.config(state="normal")
        self.update_status("✅ 完成（点击【显示结果】查看详情）")
        
        # 保存输出目录路径用于打开文件夹
        self._output_file = output_dir
        
        # 保存结果供后续查看
        self.last_result = {
            'output_dir': output_dir,
            'total_rows': total_rows,
            'group_count': group_count
        }
    
    def _show_error_result(self, error_msg):
        """显示错误结果"""
        self.process_button.config(state="normal")
        self.update_status("Excel数据处理失败")
        
        messagebox.showerror("错误", error_msg)
    
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
            self.show_warning("提示", "暂无执行结果，请先执行数据处理操作。")
            return
        
        result = self.last_result
        msg = f"Excel数据处理结果\n\n"
        msg += f"处理行数: {result.get('total_rows', 0)}\n"
        msg += f"分组数量: {result.get('group_count', 0)}\n\n"
        msg += f"输出目录:\n{result.get('output_dir', '未知')}"
        
        self.show_info("执行结果", msg)
    
    def _open_output_folder(self):
        """打开输出文件所在的文件夹"""
        try:
            if self._output_file and os.path.exists(self._output_file):
                folder_path = self._output_file
                if os.path.isfile(folder_path):
                    folder_path = os.path.dirname(folder_path)
                if sys.platform == 'win32':
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder_path])
                else:
                    subprocess.run(['xdg-open', folder_path])
            else:
                messagebox.showwarning("提示", "输出目录不存在，请先执行处理操作")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")


# 需要导入pandas
try:
    import pandas as pd
except ImportError:
    pd = None
