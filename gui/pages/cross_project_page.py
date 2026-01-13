# -*- coding: utf-8 -*-
"""
GameTools 跨项目翻译页面（现代化版本）
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path

from gui.pages.base_page import ModernPage


class CrossProjectPage(ModernPage):
    """跨项目翻译页面"""
    
    PAGE_KEY = "cross_project"
    PAGE_TITLE = "跨项目翻译"
    PAGE_ICON = "🔄"
    PAGE_DESCRIPTION = "在不同项目间进行翻译内容对照映射"
    
    def __init__(self, parent, app, theme):
        self.processor = None
        super().__init__(parent, app, theme)
    
    def _init_processor(self):
        """初始化处理器"""
        if self.processor is None:
            try:
                from core.cross_project_translator import CrossProjectTranslator
                self.processor = CrossProjectTranslator()
            except ImportError as e:
                print(f"警告: 无法导入CrossProjectTranslator: {e}")
    
    def create_widgets(self):
        """创建页面控件"""
        # 初始化处理器
        self._init_processor()
        
        # 文件配置卡片
        self._create_file_config_card()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 结果显示区域
        self._create_result_section()
    
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
            text="📁 文件选择",
            font=self.theme.FONTS["subheading"],
            bg=self.theme.colors["bg_card"],
            fg=self.theme.colors["text_primary"],
            anchor=tk.W
        )
        title.pack(fill=tk.X, pady=(0, 16))
        
        # 映射文件
        self.mapping_file_var = tk.StringVar()
        self._create_file_row(inner, "映射文件", self.mapping_file_var, 
                              self._browse_mapping_file, "(包含翻译对照的Excel)")
        
        # 项目目录
        self.project_dir_var = tk.StringVar()
        self._create_dir_row(inner, "项目目录", self.project_dir_var, 
                             self._browse_project_dir)
        
        # 输出文件
        self.output_file_var = tk.StringVar()
        self._create_save_row(inner, "输出文件", self.output_file_var, 
                              self._browse_output_file, "(翻译对应结果)")
    
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
    
    def _create_save_row(self, parent, label, var, browse_cmd, hint=""):
        """创建保存文件选择行"""
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
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        button_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
        button_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 开始对应按钮
        self.process_button = tk.Button(
            button_frame,
            text="🔄 开始对应",
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
        
        # 导出按钮
        self.export_button = tk.Button(
            button_frame,
            text="📤 导出",
            font=self.theme.FONTS["body"],
            command=self._export_results,
            bg=self.theme.colors["bg_hover"],
            fg=self.theme.colors["text_primary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            state="disabled"
        )
        self.export_button.pack(side=tk.LEFT)
    
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
            text="📋 翻译对应结果",
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
    
    def _browse_mapping_file(self):
        """浏览映射文件"""
        file_path = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if file_path:
            self.mapping_file_var.set(file_path)
            # 自动设置输出文件名
            if not self.output_file_var.get():
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(os.path.dirname(file_path), f"{base_name}_翻译对应结果.xlsx")
                self.output_file_var.set(output_path)
    
    def _browse_project_dir(self):
        """浏览项目目录"""
        dir_path = filedialog.askdirectory(title="选择项目目录")
        if dir_path:
            self.project_dir_var.set(dir_path)
    
    def _browse_output_file(self):
        """浏览输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_file_var.set(file_path)
    
    def _start_translation(self):
        """开始跨项目翻译对应"""
        mapping_file = self.mapping_file_var.get().strip()
        project_dir = self.project_dir_var.get().strip()
        output_file = self.output_file_var.get().strip()
        
        # 验证输入
        if not mapping_file:
            messagebox.showerror("错误", "请选择映射文件")
            return
        if not project_dir:
            messagebox.showerror("错误", "请选择项目目录")
            return
        if not output_file:
            messagebox.showerror("错误", "请设置输出文件")
            return
        if not os.path.exists(mapping_file):
            messagebox.showerror("错误", "映射文件不存在")
            return
        if not os.path.exists(project_dir):
            messagebox.showerror("错误", "项目目录不存在")
            return
        
        if not self.processor:
            messagebox.showerror("错误", "跨项目翻译模块未正确加载")
            return
        
        # 在新线程中执行翻译对应
        self.process_button.config(state="disabled")
        self.update_status("正在处理翻译对应...")
        
        thread = threading.Thread(target=self._translation_thread, 
                                 args=(mapping_file, project_dir, output_file))
        thread.daemon = True
        thread.start()
    
    def _translation_thread(self, mapping_file, project_dir, output_file):
        """跨项目翻译对应（后台线程）"""
        try:
            # 清空结果
            self.after(0, self._clear_results)
            
            # 开始处理
            self._schedule_append(f"开始处理翻译对应...\n")
            self._schedule_append(f"映射文件: {mapping_file}\n")
            self._schedule_append(f"项目目录: {project_dir}\n")
            self._schedule_append(f"输出文件: {output_file}\n")
            self._schedule_append(f"{'='*60}\n")
            
            # 处理翻译映射
            results = self.processor.process_translation_mapping(
                mapping_file, project_dir)
            
            if results:
                # 显示处理报告
                report = self.processor.get_processing_report()
                self._schedule_append(f"{report}\n")
                
                # 导出结果
                if self.processor.export_results(output_file):
                    self._schedule_append(f"结果已导出到: {output_file}\n")
                    self.after(0, lambda: self.export_button.config(state="normal"))
                else:
                    self._schedule_append(f"导出失败！\n")
                
                # 显示详细结果（前20条）
                self._schedule_append(f"\n详细结果（前20条）:\n")
                self._schedule_append(f"{'='*60}\n")
                
                for i, result in enumerate(results[:20]):
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    content_preview = result['content'][:50] if result['content'] else ""
                    self._schedule_append(f"{status_icon} 第{result['index']}行: {result['file_name']} -> {content_preview}...\n")
                
                if len(results) > 20:
                    self._schedule_append(f"... 还有 {len(results) - 20} 条结果，请查看导出的Excel文件\n")
            else:
                self._schedule_append(f"处理失败，没有生成结果\n")
            
            self._schedule_append(f"\n处理完成！\n")
            
        except Exception as e:
            self._schedule_append(f"❌ 处理过程中发生错误: {str(e)}\n")
        
        # 恢复按钮状态
        self.after(0, lambda: self.process_button.config(state="normal"))
        self.after(0, lambda: self.update_status("翻译对应完成"))
        self.after(0, lambda: messagebox.showinfo("完成", "翻译对应完成！请点击查看结果按钮查看详细报告"))
    
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
        self.export_button.config(state="disabled")
    
    def _export_results(self):
        """导出结果"""
        if not self.processor or not self.processor.translation_results:
            messagebox.showwarning("警告", "没有结果可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="选择导出位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            if self.processor.export_results(file_path):
                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
