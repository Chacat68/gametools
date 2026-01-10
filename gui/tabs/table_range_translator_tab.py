# -*- coding: utf-8 -*-
"""
多语言翻译提取标签页模块

提供从Excel表格中提取多语言翻译内容的功能
"""

import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from gui.tabs.base_tab import BaseTab


class TableRangeTranslatorTab(BaseTab):
    """多语言翻译提取标签页"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, main_app)
        self.result_key = 'table_range_translator'
        
        # 初始化核心处理器
        self._init_processor()
        
    def _init_processor(self):
        """初始化处理器"""
        try:
            from core.table_range_translator import TableRangeTranslator
            self.translator = TableRangeTranslator()
        except ImportError as e:
            self.translator = None
            print(f"警告: 无法导入TableRangeTranslator: {e}")
    
    def create_widgets(self):
        """创建翻译提取标签页的控件"""
        # 配置网格
        self.frame.columnconfigure(0, weight=1)
        
        # JSON配置文件选择区域
        json_frame = ttk.LabelFrame(self.frame, text="配置文件（合并的JSON，包含ZH/VN/TH语言配置）", padding="10")
        json_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        json_frame.columnconfigure(1, weight=1)
        
        # 合并JSON配置文件
        ttk.Label(json_frame, text="合并JSON:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.merged_json_var = tk.StringVar()
        self.merged_json_entry = ttk.Entry(json_frame, textvariable=self.merged_json_var, 
                                           font=("Microsoft YaHei", 9))
        self.merged_json_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(json_frame, text="浏览", 
                   command=self.browse_merged_json).grid(row=0, column=2, pady=(0, 8))
        
        # JSON语言检测结果显示
        self.json_lang_label = ttk.Label(json_frame, text="", foreground='blue')
        self.json_lang_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(self.frame, text="对应语言目录（根据JSON中的语言配置自动匹配）", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        dir_frame.columnconfigure(1, weight=1)
        
        # 中文目录
        ttk.Label(dir_frame, text="中文目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.zh_dir_var = tk.StringVar()
        self.zh_dir_entry = ttk.Entry(dir_frame, textvariable=self.zh_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.zh_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_zh_directory).grid(row=0, column=2, pady=(0, 8))
        
        # 越南文目录
        ttk.Label(dir_frame, text="越南语目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.vn_dir_var = tk.StringVar()
        self.vn_dir_entry = ttk.Entry(dir_frame, textvariable=self.vn_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.vn_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_vn_directory).grid(row=1, column=2, pady=(0, 8))
        
        # 泰文目录
        ttk.Label(dir_frame, text="泰语目录:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 8))
        self.th_dir_var = tk.StringVar()
        self.th_dir_entry = ttk.Entry(dir_frame, textvariable=self.th_dir_var, 
                                      font=("Microsoft YaHei", 9))
        self.th_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 8))
        
        ttk.Button(dir_frame, text="浏览目录", 
                   command=self.browse_th_directory).grid(row=2, column=2, pady=(0, 8))
        
        # 输出设置
        output_frame = ttk.LabelFrame(self.frame, text="输出设置（自动生成CSV文件名）", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, 
                                          font=("Microsoft YaHei", 9))
        self.output_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(output_frame, text="选择目录", 
                   command=self.browse_output_directory).grid(row=0, column=2)
        
        # 输出格式说明
        ttk.Label(output_frame, text="💡 输出格式: 翻译提取_YYYYMMDD_HHMMSS.csv", 
                  foreground='gray').grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 主要操作按钮
        self.process_button = ttk.Button(button_frame, text="🚀 开始提取", 
                                         command=self.start_translation)
        self.process_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        ttk.Button(button_frame, text="🗑️ 清空结果", 
                   command=self.clear_results).pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        ttk.Button(button_frame, text="👁️ 查看结果", 
                   command=lambda: self.show_results_dialog(self.result_key)).pack(side=tk.LEFT)
    
    def browse_merged_json(self):
        """浏览合并的JSON配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择合并的JSON配置文件（包含ZH/VN/TH）",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.merged_json_var.set(file_path)
            # 检测JSON中的语言配置
            self._detect_merged_json_languages(file_path)
    
    def _detect_merged_json_languages(self, json_path):
        """检测合并JSON中包含的语言配置"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            detected_langs = []
            lang_names = {'ZH': '中文', 'VN': '越南语', 'TH': '泰语'}
            
            for lang_key in ['ZH', 'VN', 'TH']:
                if lang_key in config:
                    text_count = len(config[lang_key].get('text_tables', []))
                    detected_langs.append(f"{lang_names.get(lang_key, lang_key)}({text_count}表)")
            
            if detected_langs:
                self.json_lang_label.config(text=f"✓ 检测到: {', '.join(detected_langs)}")
            else:
                self.json_lang_label.config(text="⚠️ 未检测到有效语言配置（ZH/VN/TH）")
        except Exception as e:
            self.json_lang_label.config(text=f"⚠️ 读取失败: {str(e)[:50]}")
    
    def browse_zh_directory(self):
        """浏览中文文件目录"""
        dir_path = filedialog.askdirectory(title="选择中文Excel文件目录（_zh后缀）")
        if dir_path:
            self.zh_dir_var.set(dir_path)
    
    def browse_vn_directory(self):
        """浏览越南文文件目录"""
        dir_path = filedialog.askdirectory(title="选择越南文Excel文件目录")
        if dir_path:
            self.vn_dir_var.set(dir_path)
    
    def browse_th_directory(self):
        """浏览泰文文件目录"""
        dir_path = filedialog.askdirectory(title="选择泰文Excel文件目录（_th后缀）")
        if dir_path:
            self.th_dir_var.set(dir_path)
    
    def browse_output_directory(self):
        """浏览输出目录"""
        dir_path = filedialog.askdirectory(title="选择CSV输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def start_translation(self):
        """开始多语言翻译提取"""
        # 获取合并的JSON配置文件
        merged_json = self.merged_json_var.get().strip()
        
        # 收集语言目录
        zh_dir = self.zh_dir_var.get().strip()
        vn_dir = self.vn_dir_var.get().strip()
        th_dir = self.th_dir_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        
        # 验证输入
        if not merged_json:
            messagebox.showerror("错误", "请选择合并的JSON配置文件")
            return
        
        if not os.path.exists(merged_json):
            messagebox.showerror("错误", "JSON配置文件不存在")
            return
        
        if not self.translator:
            messagebox.showerror("错误", "翻译提取模块未正确加载")
            return
        
        # 构建语言目录字典
        lang_dirs = {}
        if zh_dir:
            lang_dirs['zh'] = zh_dir
        if vn_dir:
            lang_dirs['vn'] = vn_dir
        if th_dir:
            lang_dirs['th'] = th_dir
        
        if not lang_dirs:
            messagebox.showerror("错误", "请至少选择一个语言目录")
            return
        
        # 如果未指定输出目录，使用第一个语言目录
        if not output_dir:
            output_dir = list(lang_dirs.values())[0]
            self.output_dir_var.set(output_dir)
        
        # 验证目录存在性
        for lang, dir_path in lang_dirs.items():
            if not os.path.exists(dir_path):
                lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
                messagebox.showerror("错误", f"{lang_names[lang]}目录不存在")
                return
        
        # 自动生成输出文件名
        output_file = self.translator.generate_output_filename(output_dir)
        
        # 在新线程中执行提取
        self.process_button.config(state="disabled")
        self.set_status("正在提取翻译内容...")
        
        thread = threading.Thread(target=self._translation_thread, 
                                  args=(merged_json, lang_dirs, output_file))
        thread.daemon = True
        thread.start()
    
    def _translation_thread(self, merged_json, lang_dirs, output_file):
        """多语言翻译提取线程 - 使用合并的JSON配置"""
        try:
            # 清空结果
            self.schedule_ui(self.clear_results)
            
            # 开始处理
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                "=" * 70 + "\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                "开始多语言翻译提取（合并JSON配置）...\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                "=" * 70 + "\n"))
            
            lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
            
            # 显示JSON配置
            self.schedule_ui(lambda jp=merged_json: 
                self.append_result(self.result_key, f"合并JSON: {jp}\n"))
            
            # 显示各语言目录
            for lang, dir_path in lang_dirs.items():
                self.schedule_ui(lambda ln=lang_names.get(lang, lang), dp=dir_path: 
                    self.append_result(self.result_key, f"{ln}目录: {dp}\n"))
            
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                f"输出文件: {output_file}\n"))
            self.schedule_ui(lambda: self.append_result(self.result_key, "\n"))
            
            # 定义进度回调函数
            def progress_callback(msg):
                """进度回调，将消息显示到界面"""
                self.schedule_ui(lambda m=msg: self.append_result(self.result_key, m + "\n"))
            
            # 使用新的合并JSON处理方法
            results = self.translator.process_with_merged_json(
                merged_json, lang_dirs, progress_callback=progress_callback)
            
            if results:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    f"✓ 成功提取 {len(results)} 条数据\n\n"))
                
                # 生成翻译CSV
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    "正在生成翻译CSV...\n"))
                
                success = self.translator.generate_translation_csv(output_file)
                
                if success:
                    self.schedule_ui(lambda: self.append_result(self.result_key, 
                        f"✓ 翻译CSV已生成: {output_file}\n\n"))
                    
                    # 显示处理报告
                    report = self.translator.get_processing_report()
                    self.schedule_ui(lambda: self.append_result(self.result_key, 
                        report + "\n"))
                    
                    # 显示成功消息
                    stats = self.translator.processing_stats
                    msg = (f"多语言翻译提取完成！\n\n"
                          f"处理表格: {stats['processed_tables']}/{stats['total_tables']}\n"
                          f"导出字段: {stats['exported_fields']} 个\n"
                          f"提取数据: {stats['total_rows']} 行\n\n"
                          f"翻译CSV已生成:\n{output_file}")
                    self.schedule_ui(lambda: messagebox.showinfo("完成", msg))
                else:
                    self.schedule_ui(lambda: self.append_result(self.result_key, 
                        "✗ 生成翻译CSV失败\n"))
                    self.schedule_ui(lambda: messagebox.showerror("错误", "生成翻译CSV失败"))
            else:
                self.schedule_ui(lambda: self.append_result(self.result_key, 
                    "✗ 没有提取到数据\n"))
                self.schedule_ui(lambda: messagebox.showwarning("警告", 
                    "没有提取到数据，请检查JSON配置和Excel文件"))
        
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.schedule_ui(lambda: self.append_result(self.result_key, 
                f"\n✗ {error_msg}\n"))
            self.schedule_ui(lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            # 恢复按钮状态
            self.schedule_ui(lambda: self.process_button.config(state="normal"))
            self.schedule_ui(lambda: self.set_status("就绪"))
    
    def clear_results(self):
        """清空翻译提取结果"""
        self.clear_result(self.result_key)
