# -*- coding: utf-8 -*-
"""
批量改表标签页模块

提供批量修改Excel表格内容的功能
"""

import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

from gui.tabs.base_tab import BaseTab


class BatchModifierTab(BaseTab):
    """批量改表标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'batch_modifier'
        self.batch_modifier = None
        
    def create_widgets(self):
        """创建批量改表标签页的控件"""
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.frame, text="文件配置", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # JSON配置文件（必需 - 定义表和字段）
        ttk.Label(file_frame, text="JSON配置:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.json_var = tk.StringVar()
        self.json_entry = ttk.Entry(file_frame, textvariable=self.json_var, 
                                    font=("Microsoft YaHei", 9))
        self.json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(file_frame, text="浏览", 
                   command=self.browse_json_file).grid(row=0, column=2, pady=(0, 8))
        
        # 映射表文件
        ttk.Label(file_frame, text="映射表文件:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.mapping_var = tk.StringVar()
        self.mapping_entry = ttk.Entry(file_frame, textvariable=self.mapping_var, 
                                       font=("Microsoft YaHei", 9))
        self.mapping_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(file_frame, text="浏览", 
                   command=self.browse_mapping_file).grid(row=1, column=2, pady=(0, 8))
        
        # 目标语言选择（放在映射表同一行右侧）
        ttk.Label(file_frame, text="语言:").grid(row=1, column=3, sticky=tk.W, padx=(20, 5), pady=(0, 8))
        self.language_var = tk.StringVar(value="VN")
        default_languages = ['VN', 'Support-CH', 'TH', 'EN', 'Polish-CH', 'VN.1']
        self.language_combo = ttk.Combobox(file_frame, textvariable=self.language_var, 
                                           width=12, values=default_languages, state='readonly')
        self.language_combo.grid(row=1, column=4, sticky=tk.W, pady=(0, 8))
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_changed)
        
        ttk.Button(file_frame, text="刷新", command=self.refresh_languages, 
                   width=5).grid(row=1, column=5, padx=(5, 0), pady=(0, 8))
        
        # JSON语言标记显示
        self.json_lang_label = ttk.Label(file_frame, text="", foreground='blue')
        self.json_lang_label.grid(row=0, column=3, columnspan=3, padx=(20, 0), pady=(0, 8), sticky=tk.W)
        
        # Excel文件目录
        ttk.Label(file_frame, text="Excel目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.excel_dir_var = tk.StringVar()
        self.excel_dir_entry = ttk.Entry(file_frame, textvariable=self.excel_dir_var, 
                                         font=("Microsoft YaHei", 9))
        self.excel_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(file_frame, text="浏览", 
                   command=self.browse_excel_directory).grid(row=2, column=2, pady=(0, 8))
        
        # 输出报告文件
        ttk.Label(file_frame, text="报告文件:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.report_var = tk.StringVar()
        self.report_entry = ttk.Entry(file_frame, textvariable=self.report_var, 
                                      font=("Microsoft YaHei", 9))
        self.report_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="浏览", 
                   command=self.browse_report_file).grid(row=3, column=2)
        
        # 选项设置区域
        options_frame = ttk.LabelFrame(self.frame, text="处理选项", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        options_frame.columnconfigure(0, weight=1)
        
        # 第一行：备份选项和引擎说明
        row1_frame = ttk.Frame(options_frame)
        row1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row1_frame, text="修改前创建备份文件（.bak）", 
                        variable=self.backup_var).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1_frame, text="使用xlwings引擎（完全保留文件结构）", 
                  foreground="green").pack(side=tk.LEFT)
        
        # 第二行：数据起始行设置
        row2_frame = ttk.Frame(options_frame)
        row2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(row2_frame, text="数据起始行:").pack(side=tk.LEFT, padx=(0, 5))
        self.data_start_row_var = tk.StringVar(value="7")
        ttk.Entry(row2_frame, textvariable=self.data_start_row_var, 
                  width=5, font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(row2_frame, text="⚠️ 小于此行号的将不会被修改（保护表头）", 
                  foreground="orange").pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2_frame, text="字段行:").pack(side=tk.LEFT, padx=(0, 5))
        self.field_row_var = tk.StringVar(value="5")
        ttk.Entry(row2_frame, textvariable=self.field_row_var, 
                  width=5, font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        
        # 第三行：定位模式说明
        row3_frame = ttk.Frame(options_frame)
        row3_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(row3_frame, 
                  text="💡 定位模式：有Position列→直接定位单元格 | 无Position列→ID作为行号", 
                  foreground="blue").pack(side=tk.LEFT)
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        self.process_button = ttk.Button(button_frame, text="🚀 开始修改", 
                                         command=self.start_modification)
        self.process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="👁️ 预览映射表", 
                   command=self.preview_mapping).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="🗑️ 清空结果", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(button_frame, text="📝 查看结果", 
                   command=lambda: self.show_results_dialog(self.result_key)).pack(side=tk.LEFT)
    
    def browse_json_file(self):
        """浏览JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择JSON配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.json_var.set(file_path)
            self._update_json_language_label(file_path)
    
    def _update_json_language_label(self, json_path):
        """更新JSON语言标记显示"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 格式1和2：检查language字段
            if 'language' in config and isinstance(config['language'], dict):
                lang_name = config['language'].get('name', '')
                lang_code = config['language'].get('code', '')
                self.json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
            else:
                # 格式3：检测语言代码作为顶层key
                lang_code_keys = ['ZH', 'VN', 'TH', 'EN', 'JP', 'KR', 'TW', 'CN']
                detected_lang_key = None
                for key in config.keys():
                    if key.upper() in lang_code_keys:
                        detected_lang_key = key
                        break
                
                if detected_lang_key and isinstance(config.get(detected_lang_key), dict):
                    lang_code = detected_lang_key.lower()
                    lang_names = {
                        'zh': '中文', 'cn': '中文', 'vn': '越南语', 'th': '泰语',
                        'en': '英语', 'jp': '日语', 'kr': '韩语', 'tw': '繁体中文'
                    }
                    lang_name = lang_names.get(lang_code, detected_lang_key)
                    self.json_lang_label.config(text=f"📌 {lang_name} ({lang_code})")
                else:
                    self.json_lang_label.config(text="⚠️ 无语言标记")
        except Exception as e:
            self.json_lang_label.config(text=f"⚠️ 读取失败: {str(e)}")
    
    def browse_mapping_file(self):
        """浏览映射表文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射表文件",
            filetypes=[("Excel和CSV文件", "*.xlsx *.xls *.csv"), ("Excel文件", "*.xlsx *.xls"), 
                       ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.mapping_var.set(file_path)
            # 自动刷新语言列表
            self.refresh_languages()
            # 自动设置输出报告路径
            if not self.report_var.get():
                report_path = os.path.splitext(file_path)[0] + "_修改报告.xlsx"
                self.report_var.set(report_path)
    
    def refresh_languages(self):
        """刷新可用的语言列表"""
        mapping_file = self.mapping_var.get().strip()
        
        if not mapping_file or not os.path.exists(mapping_file):
            messagebox.showwarning("警告", "请先选择有效的映射表文件")
            return
        
        try:
            import pandas as pd
            
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            if file_ext == '.csv':
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, nrows=0, encoding=encoding)
                        columns = df.columns.tolist()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, nrows=0, encoding='utf-8', errors='ignore')
                    columns = df.columns.tolist()
            else:
                xl = pd.ExcelFile(mapping_file)
                skip_sheets = ['汇总信息', '汇总', 'Summary', 'summary', '说明', 'Info']
                data_sheet = None
                for sheet in xl.sheet_names:
                    if sheet not in skip_sheets:
                        data_sheet = sheet
                        break
                
                if not data_sheet:
                    data_sheet = xl.sheet_names[0] if xl.sheet_names else None
                
                if data_sheet:
                    df = pd.read_excel(mapping_file, sheet_name=data_sheet, nrows=0)
                    columns = df.columns.tolist()
                else:
                    columns = []
            
            # 排除常见的非语言列
            exclude_cols = ['Classification', 'classification', 'ID', 'id', 'Field', 'field', 
                           '字段', '字段名', '表名', 'Table', 'table', '项目', '值', 'Name', 'name']
            lang_cols = [c for c in columns if c not in exclude_cols]
            
            if lang_cols:
                self.language_combo['values'] = lang_cols
                current = self.language_var.get()
                if current not in lang_cols:
                    self.language_combo.set(lang_cols[0])
                self._update_language_display()
            else:
                messagebox.showwarning("警告", "未找到语言列")
        except Exception as e:
            messagebox.showerror("错误", f"获取语言列表失败: {e}")
    
    def _update_language_display(self):
        """根据选择的语言更新显示"""
        selected_lang = self.language_var.get().strip()
        if selected_lang:
            lang_names = {
                'VN': '越南语', 'TH': '泰语', 'EN': '英语', 'ZH': '中文', 'CN': '中文',
                'JP': '日语', 'KR': '韩语', 'TW': '繁体中文', 'Support-CH': '中文(Support)',
                'Polish-CH': '中文(Polish)', 'VN.1': '越南语(VN.1)'
            }
            lang_name = lang_names.get(selected_lang, selected_lang)
            # 可以在这里更新一些显示
    
    def _on_language_changed(self, event=None):
        """当语言选择变化时"""
        self._update_language_display()
    
    def browse_excel_directory(self):
        """浏览Excel文件目录"""
        directory = filedialog.askdirectory(title="选择Excel文件目录")
        if directory:
            self.excel_dir_var.set(directory)
    
    def browse_report_file(self):
        """浏览报告保存位置"""
        file_path = filedialog.asksaveasfilename(
            title="选择报告保存位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.report_var.set(file_path)
    
    def preview_mapping(self):
        """预览映射表内容"""
        mapping_file = self.mapping_var.get().strip()
        
        if not mapping_file:
            messagebox.showerror("错误", "请先选择映射表文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射表文件不存在")
            return
        
        try:
            import pandas as pd
            
            file_ext = os.path.splitext(mapping_file)[1].lower()
            
            if file_ext == '.csv':
                for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                    try:
                        df = pd.read_csv(mapping_file, header=0, nrows=20, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    df = pd.read_csv(mapping_file, header=0, nrows=20, encoding='utf-8', errors='ignore')
                sheet_display = 'CSV文件'
            else:
                df = pd.read_excel(mapping_file, sheet_name=0, header=0, nrows=20)
                sheet_display = '第一个'
            
            # 创建预览对话框
            preview_dialog = tk.Toplevel(self.get_root())
            preview_dialog.title(f"映射表预览 - {os.path.basename(mapping_file)}")
            preview_dialog.geometry("900x500")
            
            # 信息标签
            ttk.Label(preview_dialog, 
                      text=f"工作表: {sheet_display} | 列数: {len(df.columns)} | 显示前20行").pack(pady=10)
            
            # 创建表格框架
            table_frame = ttk.Frame(preview_dialog)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # 创建文本框显示数据
            text_widget = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, font=("Consolas", 9))
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # 格式化显示数据
            header_line = " | ".join([f"{col:<20}" for col in df.columns])
            text_widget.insert(tk.END, header_line + "\n")
            text_widget.insert(tk.END, "-" * len(header_line) + "\n")
            
            for idx, row in df.iterrows():
                row_line = " | ".join([f"{str(val)[:20]:<20}" for val in row])
                text_widget.insert(tk.END, row_line + "\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # 关闭按钮
            ttk.Button(preview_dialog, text="关闭", 
                       command=preview_dialog.destroy).pack(pady=10)
            
            preview_dialog.transient(self.get_root())
            preview_dialog.grab_set()
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {e}")
    
    def start_modification(self):
        """开始批量修改"""
        json_file = self.json_var.get().strip()
        mapping_file = self.mapping_var.get().strip()
        excel_dir = self.excel_dir_var.get().strip()
        report_file = self.report_var.get().strip()
        target_language = self.language_var.get().strip()
        
        # 验证必要参数
        if not json_file:
            messagebox.showerror("错误", "请选择JSON配置文件")
            return
        
        if not os.path.exists(json_file):
            messagebox.showerror("错误", "JSON配置文件不存在")
            return
        
        if not mapping_file:
            messagebox.showerror("错误", "请选择映射表文件")
            return
        
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射表文件不存在")
            return
        
        if not excel_dir:
            messagebox.showerror("错误", "请选择Excel文件目录")
            return
        
        if not os.path.exists(excel_dir):
            messagebox.showerror("错误", "Excel文件目录不存在")
            return
        
        if not target_language:
            messagebox.showerror("错误", "请选择目标语言")
            return
        
        # 确认操作
        confirm_msg = f"""确认开始批量修改？

JSON配置: {os.path.basename(json_file)}
映射表: {os.path.basename(mapping_file)}
Excel目录: {excel_dir}
目标语言: {target_language}

定位模式（自动识别）:
• 有Position列 → Position直接定位（如B7、E24）
• 无Position列 → ID值作为行号（如ID=7→第7行）

备份: {'是' if self.backup_var.get() else '否'}

提示：建议先用少量数据测试"""
        
        if not messagebox.askyesno("确认", confirm_msg):
            return
        
        # 开始处理
        self.process_button.config(state="disabled")
        self.set_status("正在批量修改...")
        
        thread = threading.Thread(target=self._modification_thread, 
                                  args=(mapping_file, excel_dir, report_file, 
                                        json_file, target_language))
        thread.daemon = True
        thread.start()
    
    def _modification_thread(self, mapping_file, excel_dir, report_file, 
                             json_file, target_language):
        """批量修改处理线程"""
        try:
            # 清空结果
            self.schedule_ui(self.clear_results)
            
            # 初始化 batch_modifier
            from core.batch_excel_modifier import BatchExcelModifier
            self.batch_modifier = BatchExcelModifier()
            
            # 显示开始信息
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "开始批量修改Excel文件...\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"JSON配置: {json_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"映射表: {mapping_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"Excel目录: {excel_dir}\n"))
            self.schedule_ui(lambda tl=target_language: self.append_result(self.result_key, f"目标语言列: {tl}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"备份: {'是' if self.backup_var.get() else '否'}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, f"处理引擎: xlwings (Excel原生引擎)\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n"))
            
            # 设置进度回调
            def progress_callback(msg, percentage=None):
                self.schedule_ui(lambda m=msg: self.append_result(self.result_key, m + "\n"))
            
            self.batch_modifier.set_progress_callback(progress_callback)
            
            # 加载JSON配置
            self.schedule_ui(lambda: self.append_result(self.result_key, "正在加载JSON配置...\n"))
            
            field_config = self.batch_modifier.load_json_config(json_file)
            
            if not field_config:
                self.schedule_ui(lambda: self.append_result(self.result_key, "✗ JSON配置加载失败或为空\n"))
                self.schedule_ui(lambda: messagebox.showerror("错误", "JSON配置加载失败"))
                return
            
            self.schedule_ui(lambda: self.append_result(self.result_key, f"✓ 已加载 {len(field_config)//2} 个表的字段配置\n\n"))
            
            # 获取字段行和数据起始行配置
            try:
                field_row = int(self.field_row_var.get().strip())
            except ValueError:
                field_row = 5
            
            try:
                data_start_row = int(self.data_start_row_var.get().strip())
            except ValueError:
                data_start_row = 7
            
            self.schedule_ui(lambda fr=field_row, dsr=data_start_row: self.append_result(self.result_key, 
                f"字段行: {fr}, 数据起始行: {dsr} (小于此行号的将被跳过)\n\n"))
            
            # 执行修改
            stats = self.batch_modifier.process_batch_modification_by_language(
                mapping_path=mapping_file,
                excel_directory=excel_dir,
                id_col="ID",
                target_language=target_language,
                field_col=None,
                backup=self.backup_var.get(),
                field_row=field_row,
                data_start_row=data_start_row
            )
            
            # 显示统计信息
            summary = self.batch_modifier.get_stats_summary()
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n" + summary + "\n"))
            
            # 显示跳过信息
            if stats.get('skipped_no_config', 0) > 0:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    f"\n⚠️ 跳过了 {stats['skipped_no_config']} 个工作表（表名不在JSON配置中）\n"))
            
            if stats.get('skipped_no_file', 0) > 0:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    f"⚠️ 跳过了 {stats['skipped_no_file']} 个工作表（对应Excel文件不存在）\n"))
            
            if stats.get('skipped_field_mismatch', 0) > 0:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    f"⚠️ 跳过了 {stats['skipped_field_mismatch']} 行（CSV字段名不在JSON配置中）\n"))
            
            if stats.get('skipped_same_value', 0) > 0:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    f"✓ 跳过了 {stats['skipped_same_value']} 处（原值与新值相同，无需修改）\n"))
            
            # 生成报告
            if report_file:
                self.schedule_ui(lambda: self.append_result(self.result_key, "\n正在生成修改报告...\n"))
                
                if self.batch_modifier.generate_modification_report(report_file):
                    self.schedule_ui(lambda: self.append_result(self.result_key, 
                        f"✓ 修改报告已生成: {report_file}\n"))
                else:
                    self.schedule_ui(lambda: self.append_result(self.result_key, "✗ 生成修改报告失败\n"))
            
            # 显示错误日志
            if self.batch_modifier.error_logs:
                self.schedule_ui(lambda: self.append_result(self.result_key, "\n错误日志:\n"))
                for error in self.batch_modifier.error_logs[:20]:
                    self.schedule_ui(lambda e=error: self.append_result(self.result_key, f"  ✗ {e}\n"))
                if len(self.batch_modifier.error_logs) > 20:
                    self.schedule_ui(lambda: self.append_result(self.result_key, 
                        f"  ... 还有 {len(self.batch_modifier.error_logs) - 20} 条错误\n"))
            
            # 显示成功消息
            msg = f"""批量修改完成！

修改的文件数: {stats['modified_files']}
修改的单元格数: {stats['modified_cells']}
错误数: {stats['errors']}

定位模式: {'Position直接定位' if stats.get('used_position_mode') else '行号直接定位'}
报告已保存: {report_file if report_file else '未生成'}"""
            
            self.schedule_ui(lambda: messagebox.showinfo("完成", msg))
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.schedule_ui(lambda: self.append_result(self.result_key, f"\n✗ {error_msg}\n"))
            self.schedule_ui(lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.schedule_ui(lambda: self.process_button.config(state="normal"))
            self.schedule_ui(lambda: self.set_status("就绪"))
    
    def clear_results(self):
        """清空结果"""
        self.clear_result(self.result_key)
