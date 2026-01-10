# -*- coding: utf-8 -*-
"""
跨项目翻译对应标签页
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os


class CrossProjectTranslatorTab:
    """跨项目翻译对应标签页"""
    
    def __init__(self, app, notebook: ttk.Notebook):
        """
        初始化标签页
        
        Args:
            app: 主应用实例（GameToolsUnified）
            notebook: ttk.Notebook实例
        """
        self.app = app
        self.notebook = notebook
        
        # 创建标签页框架
        self.frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame, text="跨项目翻译")
        
        self.frame.columnconfigure(0, weight=1)
        
        # 创建UI
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面控件"""
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.frame, text="文件选择", padding="8")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # 映射文件选择
        ttk.Label(file_frame, text="映射文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.mapping_file_var = tk.StringVar()
        self.mapping_file_entry = ttk.Entry(file_frame, textvariable=self.mapping_file_var)
        self.mapping_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        ttk.Button(file_frame, text="浏览", command=self._browse_mapping_file).grid(row=0, column=2, pady=2)
        
        # 项目目录选择
        ttk.Label(file_frame, text="项目目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.project_dir_var = tk.StringVar()
        self.project_dir_entry = ttk.Entry(file_frame, textvariable=self.project_dir_var)
        self.project_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        ttk.Button(file_frame, text="浏览", command=self._browse_project_directory).grid(row=1, column=2, pady=2)
        
        # 输出文件选择
        ttk.Label(file_frame, text="输出文件:").grid(row=2, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.output_file_var = tk.StringVar()
        self.output_file_entry = ttk.Entry(file_frame, textvariable=self.output_file_var)
        self.output_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 8), pady=2)
        ttk.Button(file_frame, text="浏览", command=self._browse_output_file).grid(row=2, column=2, pady=2)
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        
        self.process_button = ttk.Button(button_frame, text="开始对应", 
                                        command=self._start_translation, style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="清空", command=self._clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_button = ttk.Button(button_frame, text="导出", 
                                       command=self._export_results, state="disabled")
        self.export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.view_button = ttk.Button(button_frame, text="查看结果", 
                                     command=lambda: self.app.show_results_dialog('cross_project_translator'))
        self.view_button.pack(side=tk.LEFT)
    
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
    
    def _browse_project_directory(self):
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
        
        # 在新线程中执行翻译对应
        self.process_button.config(state="disabled")
        self.app.status_var.set("正在处理翻译对应...")
        
        thread = threading.Thread(target=self._translation_thread, 
                                 args=(mapping_file, project_dir, output_file))
        thread.daemon = True
        thread.start()
    
    def _translation_thread(self, mapping_file, project_dir, output_file):
        """跨项目翻译对应（后台线程）"""
        try:
            # 清空结果
            self.app.root.after(0, self._clear_results)
            
            # 开始处理
            self._append_result(f"开始处理翻译对应...\n")
            self._append_result(f"映射文件: {mapping_file}\n")
            self._append_result(f"项目目录: {project_dir}\n")
            self._append_result(f"输出文件: {output_file}\n")
            self._append_result(f"{'='*60}\n")
            
            # 处理翻译映射
            results = self.app.cross_project_translator.process_translation_mapping(
                mapping_file, project_dir)
            
            if results:
                # 显示处理报告
                report = self.app.cross_project_translator.get_processing_report()
                self._append_result(f"{report}\n")
                
                # 导出结果
                if self.app.cross_project_translator.export_results(output_file):
                    self._append_result(f"结果已导出到: {output_file}\n")
                    self.app.root.after(0, lambda: self.export_button.config(state="normal"))
                else:
                    self._append_result(f"导出失败！\n")
                
                # 显示详细结果（前20条）
                self._append_result(f"\n详细结果（前20条）:\n")
                self._append_result(f"{'='*60}\n")
                
                for i, result in enumerate(results[:20]):
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    content_preview = result['content'][:50] if result['content'] else ""
                    self._append_result(f"{status_icon} 第{result['index']}行: {result['file_name']} -> {content_preview}...\n")
                
                if len(results) > 20:
                    self._append_result(f"... 还有 {len(results) - 20} 条结果，请查看导出的Excel文件\n")
            else:
                self._append_result(f"处理失败，没有生成结果\n")
            
            self._append_result(f"\n处理完成！\n")
            
        except Exception as e:
            self._append_result(f"❌ 处理过程中发生错误: {str(e)}\n")
        
        # 恢复按钮状态
        self.app.root.after(0, lambda: self.process_button.config(state="normal"))
        self.app.root.after(0, lambda: self.app.status_var.set("翻译对应完成"))
        self.app.root.after(0, lambda: messagebox.showinfo("完成", "翻译对应完成！请点击查看结果按钮查看详细报告"))
    
    def _append_result(self, text):
        """追加结果文本"""
        self.app.root.after(0, lambda: self.app.append_result('cross_project_translator', text))
    
    def _clear_results(self):
        """清空结果"""
        self.app.clear_result('cross_project_translator')
        self.export_button.config(state="disabled")
    
    def _export_results(self):
        """导出结果"""
        if not self.app.cross_project_translator.translation_results:
            messagebox.showwarning("警告", "没有结果可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="选择导出位置",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if file_path:
            if self.app.cross_project_translator.export_results(file_path):
                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出失败")
    
    # 兼容旧API的属性映射
    @property
    def cpt_mapping_file_var(self):
        return self.mapping_file_var
    
    @property
    def cpt_project_dir_var(self):
        return self.project_dir_var
    
    @property
    def cpt_output_file_var(self):
        return self.output_file_var
    
    @property
    def cpt_process_button(self):
        return self.process_button
    
    @property
    def cpt_export_button(self):
        return self.export_button
