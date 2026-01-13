# -*- coding: utf-8 -*-
"""
GameTools 多语言提取页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json

from gui.pages.base_page import ModernPage


class TableRangePage(ModernPage):
    """多语言提取页面"""
    
    PAGE_KEY = "table_range"
    PAGE_TITLE = "多语言提取"
    PAGE_ICON = "🌐"
    PAGE_DESCRIPTION = "从Excel表格中提取多语言翻译内容"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        super().__init__(parent, app, theme)
    
    def _init_processor(self):
        """初始化处理器"""
        if self.processor is None:
            try:
                from core.table_range_translator import TableRangeTranslator
                self.processor = TableRangeTranslator()
            except ImportError as e:
                print(f"警告: 无法导入TableRangeTranslator: {e}")
    
    def create_widgets(self):
        """创建页面控件"""
        # 初始化处理器
        self._init_processor()
        
        # JSON配置卡片
        self._create_json_config_card()
        
        # 语言目录卡片
        self._create_language_dirs_card()
        
        # 输出设置卡片
        self._create_output_card()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 结果显示区域
        self._create_result_section()
    
    def _create_json_config_card(self):
        """创建JSON配置卡片"""
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
            text="📄 配置文件（合并的JSON，包含ZH/VN/TH语言配置）",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 合并JSON配置文件
        json_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        json_row.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            json_row,
            text="合并JSON",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=10,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.merged_json_var = tk.StringVar()
        entry_frame = tk.Frame(
            json_row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        tk.Entry(
            entry_frame,
            textvariable=self.merged_json_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        ).pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            json_row,
            text="浏览",
            font=self.theme.FONTS["small"],
            command=self._browse_merged_json,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
        
        # 语言检测结果
        self.json_lang_label = tk.Label(
            inner,
            text="",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["info"],
            anchor=tk.W
        )
        self.json_lang_label.pack(fill=tk.X)
    
    def _create_language_dirs_card(self):
        """创建语言目录卡片"""
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
            text="📁 对应语言目录（根据JSON中的语言配置自动匹配）",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 中文目录
        self.zh_dir_var = tk.StringVar()
        self._create_dir_row(inner, "中文目录", self.zh_dir_var, 
                             lambda: self._browse_lang_dir("中文Excel文件目录（_zh后缀）", self.zh_dir_var))
        
        # 越南语目录
        self.vn_dir_var = tk.StringVar()
        self._create_dir_row(inner, "越南语目录", self.vn_dir_var, 
                             lambda: self._browse_lang_dir("越南文Excel文件目录", self.vn_dir_var))
        
        # 泰语目录
        self.th_dir_var = tk.StringVar()
        self._create_dir_row(inner, "泰语目录", self.th_dir_var, 
                             lambda: self._browse_lang_dir("泰文Excel文件目录（_th后缀）", self.th_dir_var))
    
    def _create_output_card(self):
        """创建输出设置卡片"""
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
            text="📤 输出设置（自动生成CSV文件名）",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 输出目录
        self.output_dir_var = tk.StringVar()
        self._create_dir_row(inner, "输出目录", self.output_dir_var, 
                             lambda: self._browse_lang_dir("选择CSV输出目录", self.output_dir_var))
        
        # 输出格式说明
        tk.Label(
            inner,
            text="💡 输出格式: 翻译提取_YYYYMMDD_HHMMSS.csv",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        ).pack(fill=tk.X)
    
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
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        button_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 开始提取按钮
        self.process_button = tk.Button(
            button_frame,
            text="🚀 开始提取",
            font=self.theme.FONTS["body"],
            command=self._start_translation,
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
            text="🗑️ 清空结果",
            font=self.theme.FONTS["body"],
            command=self._clear_results,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8
        ).pack(side=tk.LEFT)
    
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
            text="📋 提取结果",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 12))
        
        # 结果文本框
        text_frame = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(
            text_frame,
            font=("Consolas", 10),
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # ==================== 事件处理方法 ====================
    
    def _browse_merged_json(self):
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
    
    def _browse_lang_dir(self, title, var):
        """浏览语言目录"""
        dir_path = filedialog.askdirectory(title=title)
        if dir_path:
            var.set(dir_path)
    
    def _start_translation(self):
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
        
        if not self.processor:
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
        output_file = self.processor.generate_output_filename(output_dir)
        
        # 在新线程中执行提取
        self.process_button.config(state="disabled")
        self.update_status("正在提取翻译内容...")
        
        thread = threading.Thread(target=self._translation_thread, 
                                  args=(merged_json, lang_dirs, output_file))
        thread.daemon = True
        thread.start()
    
    def _translation_thread(self, merged_json, lang_dirs, output_file):
        """多语言翻译提取线程"""
        try:
            # 清空结果
            self.after(0, self._clear_results)
            
            # 开始处理
            self._schedule_append("=" * 70 + "\n")
            self._schedule_append("开始多语言翻译提取（合并JSON配置）...\n")
            self._schedule_append("=" * 70 + "\n")
            
            lang_names = {'zh': '中文', 'vn': '越南语', 'th': '泰语'}
            
            # 显示JSON配置
            self._schedule_append(f"合并JSON: {merged_json}\n")
            
            # 显示各语言目录
            for lang, dir_path in lang_dirs.items():
                self._schedule_append(f"{lang_names.get(lang, lang)}目录: {dir_path}\n")
            
            self._schedule_append(f"输出文件: {output_file}\n\n")
            
            # 定义进度回调函数
            def progress_callback(msg):
                self._schedule_append(msg + "\n")
            
            # 使用新的合并JSON处理方法
            results = self.processor.process_with_merged_json(
                merged_json, lang_dirs, progress_callback=progress_callback)
            
            if results:
                self._schedule_append(f"✓ 成功提取 {len(results)} 条数据\n\n")
                
                # 生成翻译CSV
                self._schedule_append("正在生成翻译CSV...\n")
                
                success = self.processor.generate_translation_csv(output_file)
                
                if success:
                    self._schedule_append(f"✓ 翻译CSV已生成: {output_file}\n\n")
                    
                    # 显示处理报告
                    report = self.processor.get_processing_report()
                    self._schedule_append(report + "\n")
                    
                    # 显示成功消息
                    stats = self.processor.processing_stats
                    msg = (f"多语言翻译提取完成！\n\n"
                          f"处理表格: {stats['processed_tables']}/{stats['total_tables']}\n"
                          f"导出字段: {stats['exported_fields']} 个\n"
                          f"提取数据: {stats['total_rows']} 行\n\n"
                          f"翻译CSV已生成:\n{output_file}")
                    self.after(0, lambda: messagebox.showinfo("完成", msg))
                else:
                    self._schedule_append("✗ 生成翻译CSV失败\n")
                    self.after(0, lambda: messagebox.showerror("错误", "生成翻译CSV失败"))
            else:
                self._schedule_append("✗ 没有提取到数据\n")
                self.after(0, lambda: messagebox.showwarning("警告", 
                    "没有提取到数据，请检查JSON配置和Excel文件"))
        
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self._schedule_append(f"\n✗ {error_msg}\n")
            self.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            # 恢复按钮状态
            self.after(0, lambda: self.process_button.config(state="normal"))
            self.after(0, lambda: self.update_status("就绪"))
    
    def _schedule_append(self, text):
        """调度追加文本"""
        self.after(0, lambda: self._append_result(text))
    
    def _append_result(self, text):
        """追加结果文本"""
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
    
    def _clear_results(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
