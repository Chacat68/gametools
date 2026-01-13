# -*- coding: utf-8 -*-
"""
GameTools JSON检测页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from pathlib import Path

from gui.pages.base_page import ModernPage


class JsonDetectorPage(ModernPage):
    """JSON 检测页面"""
    
    PAGE_KEY = "json_detector"
    PAGE_TITLE = "JSON 格式检测"
    PAGE_ICON = "🔍"
    PAGE_DESCRIPTION = "检测 JSON 文件中的语法、结构和编码错误"
    
    def __init__(self, parent, app, theme):
        self.detector = None
        super().__init__(parent, app, theme)
    
    def create_widgets(self):
        """创建页面控件"""
        # 路径选择卡片
        self._create_path_card()
        
        # 检测选项卡片
        self._create_options_card()
        
        # 操作按钮
        self._create_action_buttons()
        
        # 结果区域
        self._create_result_section()
    
    def _create_path_card(self):
        """创建路径选择卡片"""
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
            text="📁 检测路径",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 路径输入行
        row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        row.pack(fill=tk.X)
        
        tk.Label(
            row,
            text="路径:",
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            width=8,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar()
        entry_frame = tk.Frame(
            row,
            bg=self.theme.colors["bg_input"],
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1
        )
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.path_entry = tk.Entry(
            entry_frame,
            textvariable=self.path_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_input"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            highlightthickness=0
        )
        self.path_entry.pack(fill=tk.X, padx=8, pady=6)
        
        tk.Button(
            row,
            text="选择文件夹",
            font=self.theme.FONTS["small"],
            command=self._browse_folder,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        tk.Button(
            row,
            text="选择文件",
            font=self.theme.FONTS["small"],
            command=self._browse_file,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)
        
        # 提示
        tip = tk.Label(
            inner,
            text="💡 支持选择单个文件或整个文件夹进行批量检测",
            font=self.theme.FONTS["small"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_muted"],
            anchor=tk.W
        )
        tip.pack(fill=tk.X, pady=(12, 0))
    
    def _create_options_card(self):
        """创建检测选项卡片"""
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
            text="⚙️ 检测选项",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 选项行
        options_row = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        options_row.pack(fill=tk.X)
        
        self.recursive_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_row,
            text="递归检测子文件夹",
            variable=self.recursive_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT, padx=(0, 24))
        
        self.strict_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_row,
            text="严格模式（检测更多潜在问题）",
            variable=self.strict_var,
            font=self.theme.FONTS["body"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            activebackground=self.theme.colors["bg_card"],
            selectcolor=self.theme.colors["bg_input"]
        ).pack(side=tk.LEFT)
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        btn_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 开始检测
        self.detect_btn = tk.Button(
            btn_frame,
            text="🔍 开始检测",
            font=("Microsoft YaHei", 10, "bold"),
            command=self._start_detection,
            bg=self.theme.colors["primary"],
            fg="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.detect_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空结果
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
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        # 保存报告
        self.save_btn = tk.Button(
            btn_frame,
            text="💾 保存报告",
            font=self.theme.FONTS["body"],
            command=self._save_report,
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=8,
            highlightbackground=self.theme.colors["border"],
            highlightthickness=1,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT)
    
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
        
        # 标题和统计
        header = tk.Frame(inner, bg=self.theme.colors["bg_card"])
        header.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            header,
            text="📊 检测结果",
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
        self.progress_track = tk.Frame(
            inner,
            bg=self.theme.colors["bg_hover"],
            height=4
        )
        self.progress_track.pack(fill=tk.X, pady=(0, 12))
        self.progress_track.pack_propagate(False)
        
        self.progress_fill = tk.Frame(
            self.progress_track,
            bg=self.theme.colors["primary"],
            height=4
        )
        self.progress_fill.place(x=0, y=0, relheight=1, relwidth=0)
        
        # 结果列表
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
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL,
                                   command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # 配置文本标签颜色
        self.result_text.tag_configure("error", foreground=self.theme.colors["error"])
        self.result_text.tag_configure("warning", foreground=self.theme.colors["warning"])
        self.result_text.tag_configure("success", foreground=self.theme.colors["success"])
        self.result_text.tag_configure("info", foreground=self.theme.colors["info"])
    
    # ==================== 浏览方法 ====================
    
    def _browse_folder(self):
        """浏览选择文件夹"""
        path = filedialog.askdirectory(title="选择要检测的文件夹")
        if path:
            self.path_var.set(path)
    
    def _browse_file(self):
        """浏览选择文件"""
        path = filedialog.askopenfilename(
            title="选择要检测的 JSON 文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if path:
            self.path_var.set(path)
    
    # ==================== 操作方法 ====================
    
    def _start_detection(self):
        """开始检测"""
        path = self.path_var.get()
        if not path:
            self.show_warning("警告", "请选择要检测的文件或文件夹")
            return
        
        if not Path(path).exists():
            self.show_error("错误", f"路径不存在: {path}")
            return
        
        # 禁用按钮，清空结果
        self.detect_btn.configure(state=tk.DISABLED)
        self.save_btn.configure(state=tk.DISABLED)
        self.result_text.delete("1.0", tk.END)
        self.stats_label.configure(text="检测中...")
        
        # 启动检测线程
        thread = threading.Thread(target=self._do_detection, daemon=True)
        thread.start()
    
    def _do_detection(self):
        """执行检测（后台线程）"""
        try:
            from tools.json_error_detector.json_error_detector import JSONErrorDetector
            
            if not self.detector:
                self.detector = JSONErrorDetector()
            
            path = self.path_var.get()
            recursive = self.recursive_var.get()
            
            # 检测
            if Path(path).is_file():
                results = [self.detector.detect_file(path)]
            else:
                results = self.detector.detect_directory(path, recursive=recursive)
            
            # 处理结果
            self.after(0, lambda: self._display_results(results))
            
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))
    
    def _display_results(self, results):
        """显示检测结果"""
        self.detect_btn.configure(state=tk.NORMAL)
        self.progress_fill.place(relwidth=1)
        
        total_files = len(results)
        error_count = sum(1 for r in results if r.get('has_error', False))
        
        # 统计信息
        if error_count > 0:
            self.stats_label.configure(
                text=f"共 {total_files} 个文件，{error_count} 个有错误",
                fg=self.theme.colors["error"]
            )
        else:
            self.stats_label.configure(
                text=f"共 {total_files} 个文件，全部正常",
                fg=self.theme.colors["success"]
            )
        
        # 显示详细结果
        for result in results:
            filepath = result.get('file', 'unknown')
            filename = Path(filepath).name
            
            if result.get('has_error', False):
                self.result_text.insert(tk.END, f"❌ {filename}\n", "error")
                errors = result.get('errors', [])
                for error in errors:
                    self.result_text.insert(tk.END, f"   {error}\n")
            else:
                self.result_text.insert(tk.END, f"✓ {filename}\n", "success")
        
        # 启用保存按钮
        if results:
            self.save_btn.configure(state=tk.NORMAL)
            self._detection_results = results
    
    def _on_error(self, error_msg: str):
        """处理错误"""
        self.detect_btn.configure(state=tk.NORMAL)
        self.stats_label.configure(text="检测失败", fg=self.theme.colors["error"])
        self.result_text.insert(tk.END, f"错误: {error_msg}\n", "error")
        self.show_error("检测错误", error_msg)
    
    def _clear_results(self):
        """清空结果"""
        self.result_text.delete("1.0", tk.END)
        self.stats_label.configure(text="", fg=self.theme.colors["text_muted"])
        self.progress_fill.place(relwidth=0)
        self.save_btn.configure(state=tk.DISABLED)
        self._detection_results = None
    
    def _save_report(self):
        """保存检测报告"""
        if not hasattr(self, '_detection_results') or not self._detection_results:
            self.show_warning("警告", "没有可保存的检测结果")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="保存检测报告",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            defaultextension=".txt"
        )
        
        if filepath:
            try:
                content = self.result_text.get("1.0", tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.show_info("保存成功", f"报告已保存到:\n{filepath}")
            except Exception as e:
                self.show_error("保存失败", str(e))
