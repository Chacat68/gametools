# -*- coding: utf-8 -*-
"""
Excel配置同步标签页模块

提供将Excel配置从源目录同步到目标目录的功能
"""

import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from gui.tabs.base_tab import BaseTab


class ConfigSyncTab(BaseTab):
    """Excel配置同步标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'config_sync'
        
        # 初始化核心处理器
        self._init_processor()
        
    def _init_processor(self):
        """初始化处理器"""
        try:
            from core.excel_config_sync import ExcelConfigSync
            self.config_sync = ExcelConfigSync()
        except ImportError as e:
            self.config_sync = None
            print(f"警告: 无法导入ExcelConfigSync: {e}")
    
    def create_widgets(self):
        """创建配置同步标签页的控件"""
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(self.frame, text="目录配置（同步Excel配置到其他目录）", padding="10")
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 源目录
        ttk.Label(dir_frame, text="源目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.source_dir_var = tk.StringVar()
        self.source_dir_entry = ttk.Entry(dir_frame, textvariable=self.source_dir_var, 
                                          font=("Microsoft YaHei", 9))
        self.source_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_source_dir).grid(row=0, column=2, pady=(0, 8))
        
        # 目标目录1
        ttk.Label(dir_frame, text="目标目录1:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.target1_dir_var = tk.StringVar()
        self.target1_dir_entry = ttk.Entry(dir_frame, textvariable=self.target1_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.target1_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_target1_dir).grid(row=1, column=2, pady=(0, 8))
        
        # 目标目录2
        ttk.Label(dir_frame, text="目标目录2:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.target2_dir_var = tk.StringVar()
        self.target2_dir_entry = ttk.Entry(dir_frame, textvariable=self.target2_dir_var, 
                                           font=("Microsoft YaHei", 9))
        self.target2_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_target2_dir).grid(row=2, column=2, pady=(0, 8))
        
        # JSON配置文件
        ttk.Label(dir_frame, text="JSON配置:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.json_var = tk.StringVar()
        self.json_entry = ttk.Entry(dir_frame, textvariable=self.json_var, 
                                    font=("Microsoft YaHei", 9))
        self.json_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览JSON", 
                   command=self.browse_json_file).grid(row=3, column=2, pady=(0, 8))
        
        ttk.Label(dir_frame, text="(可选，仅用于参考)", 
                  foreground='gray').grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        # 过滤配置文件
        ttk.Label(dir_frame, text="过滤配置:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(dir_frame, textvariable=self.filter_var, 
                                      font=("Microsoft YaHei", 9))
        self.filter_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        filter_btn_frame = ttk.Frame(dir_frame)
        filter_btn_frame.grid(row=5, column=2, pady=(0, 8))
        ttk.Button(filter_btn_frame, text="浏览JSON", 
                   command=self.browse_filter_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_btn_frame, text="预览", 
                   command=self.preview_filter_config).pack(side=tk.LEFT)
        
        ttk.Label(dir_frame, text="(可选，指定要跳过同步的字段)", 
                  foreground='gray').grid(row=6, column=1, sticky=tk.W, pady=(0, 5))
        
        # 报告文件
        ttk.Label(dir_frame, text="报告文件:").grid(row=7, column=0, sticky=tk.W, padx=(0, 10))
        self.report_var = tk.StringVar()
        self.report_entry = ttk.Entry(dir_frame, textvariable=self.report_var, 
                                      font=("Microsoft YaHei", 9))
        self.report_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(dir_frame, text="选择位置", 
                   command=self.browse_report_file).grid(row=7, column=2)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(self.frame, text="同步选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 备份选项
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="同步前备份", 
                        variable=self.backup_var).grid(row=0, column=0, sticky=tk.W)
        
        # 同步值选项
        self.values_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="同步单元格值", 
                        variable=self.values_var).grid(row=0, column=1, sticky=tk.W, padx=(15, 0))
        
        # 同步公式选项
        self.formulas_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="同步公式", 
                        variable=self.formulas_var).grid(row=0, column=2, sticky=tk.W, padx=(15, 0))
        
        # 同步样式选项
        self.styles_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="同步样式", 
                        variable=self.styles_var).grid(row=0, column=3, sticky=tk.W, padx=(15, 0))
        
        # 同步列宽选项
        self.column_widths_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="同步列宽", 
                        variable=self.column_widths_var).grid(row=0, column=4, sticky=tk.W, padx=(15, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.process_button = ttk.Button(button_frame, text="🚀 开始同步", 
                                         command=self.start_sync)
        self.process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="👁️ 预览匹配", 
                   command=self.preview_matching).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="🗑️ 清空结果", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="📝 查看结果", 
                   command=lambda: self.show_results_dialog(self.result_key)).pack(side=tk.LEFT)
    
    def browse_source_dir(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择源目录")
        if directory:
            self.source_dir_var.set(directory)
    
    def browse_target1_dir(self):
        """浏览目标目录1"""
        directory = filedialog.askdirectory(title="选择目标目录1")
        if directory:
            self.target1_dir_var.set(directory)
    
    def browse_target2_dir(self):
        """浏览目标目录2"""
        directory = filedialog.askdirectory(title="选择目标目录2")
        if directory:
            self.target2_dir_var.set(directory)
    
    def browse_json_file(self):
        """浏览JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.json_var.set(file_path)
    
    def browse_filter_file(self):
        """浏览过滤配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择字段过滤配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.filter_var.set(file_path)
    
    def browse_report_file(self):
        """浏览报告输出位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.report_var.set(file_path)
    
    def preview_filter_config(self):
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
            
            # 创建预览窗口
            preview_window = tk.Toplevel(self.get_root())
            preview_window.title("过滤配置预览")
            preview_window.geometry("700x500")
            
            # 文本框
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            text_widget.insert(1.0, "\n".join(preview_lines))
            text_widget.config(state='disabled')
            
            # 关闭按钮
            ttk.Button(preview_window, text="关闭", 
                       command=preview_window.destroy).pack(pady=10)
            
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON解析错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"读取配置失败: {str(e)}")
    
    def preview_matching(self):
        """预览匹配的文件"""
        if not self.config_sync:
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
        matching_files = self.config_sync.find_matching_files(source_dir, target_dirs)
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.get_root())
        preview_window.title("文件匹配预览")
        preview_window.geometry("700x500")
        
        # 文本框
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 生成预览内容
        preview_lines = []
        preview_lines.append("=" * 60)
        preview_lines.append("文件匹配预览")
        preview_lines.append("=" * 60)
        preview_lines.append(f"\n源目录: {source_dir}")
        preview_lines.append(f"目标目录1: {target1_dir or '(未选择)'}")
        preview_lines.append(f"目标目录2: {target2_dir or '(未选择)'}")
        preview_lines.append(f"\n源目录文件数: {self.config_sync.processing_stats.get('source_files', 0)}")
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
        
        text_widget.insert(1.0, "\n".join(preview_lines))
        text_widget.config(state='disabled')
        
        # 关闭按钮
        ttk.Button(preview_window, text="关闭", 
                   command=preview_window.destroy).pack(pady=10)
    
    def start_sync(self):
        """开始配置同步"""
        if not self.config_sync:
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
        self.set_status("正在同步配置...")
        
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
            self.schedule_ui(self.clear_results)
            
            # 显示开始信息
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "开始同步Excel配置...\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"源目录: {source_dir}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"目标目录1: {target1_dir or '(未选择)'}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"目标目录2: {target2_dir or '(未选择)'}\n"))
            if json_file:
                self.schedule_ui(lambda: self.append_result(self.result_key, f"JSON配置: {json_file}\n"))
            if filter_file:
                self.schedule_ui(lambda: self.append_result(self.result_key, f"过滤配置: {filter_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n"))
            
            # 设置同步选项
            self.config_sync.sync_options['backup_before_sync'] = self.backup_var.get()
            self.config_sync.sync_options['sync_values'] = self.values_var.get()
            self.config_sync.sync_options['sync_formulas'] = self.formulas_var.get()
            self.config_sync.sync_options['sync_styles'] = self.styles_var.get()
            self.config_sync.sync_options['sync_column_widths'] = self.column_widths_var.get()
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.schedule_ui(lambda m=msg: self.append_result(self.result_key, m + "\n"))
            
            self.config_sync.set_progress_callback(progress_callback)
            
            # 加载JSON配置（如果有）
            if json_file and os.path.exists(json_file):
                self.schedule_ui(lambda: self.append_result(self.result_key, "正在加载JSON配置（仅用于参考）...\n"))
                self.config_sync.load_json_config(json_file)
                self.schedule_ui(lambda: self.append_result(self.result_key, "✓ JSON配置已加载\n\n"))
            
            # 加载过滤配置（如果有）
            if filter_file and os.path.exists(filter_file):
                self.schedule_ui(lambda: self.append_result(self.result_key, "正在加载过滤配置...\n"))
                self.config_sync.load_filter_config(filter_file)
                skip_count = len(self.config_sync.skip_fields)
                self.schedule_ui(lambda: self.append_result(self.result_key, f"✓ 过滤配置已加载，包含 {skip_count} 个表的过滤规则\n\n"))
            
            # 执行同步
            stats = self.config_sync.sync_directories(
                source_dir=source_dir,
                target_dir1=target1_dir if target1_dir else None,
                target_dir2=target2_dir if target2_dir else None
            )
            
            # 显示统计信息
            summary = self.config_sync.get_stats_summary()
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n" + summary + "\n"))
            
            # 生成报告
            if report_file:
                self.schedule_ui(lambda: self.append_result(self.result_key, f"\n正在生成报告: {report_file}\n"))
                if self.config_sync.generate_sync_report(report_file):
                    self.schedule_ui(lambda: self.append_result(self.result_key, "✓ 报告生成成功\n"))
                else:
                    self.schedule_ui(lambda: self.append_result(self.result_key, "✗ 报告生成失败\n"))
            
            # 完成
            self.schedule_ui(lambda: self.set_status("同步完成"))
            self.schedule_ui(lambda: messagebox.showinfo("完成", "配置同步完成！"))
            
        except Exception as e:
            error_msg = f"同步过程出错: {str(e)}"
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n✗ 错误: {error_msg}\n"))
            self.schedule_ui(lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.schedule_ui(lambda: self.process_button.config(state="normal"))
            self.schedule_ui(lambda: self.set_status("就绪"))
    
    def clear_results(self):
        """清空同步结果"""
        self.clear_result(self.result_key)
