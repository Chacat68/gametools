# -*- coding: utf-8 -*-
"""
JSON错误检测标签页
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os


class JsonDetectorTab:
    """JSON错误检测标签页"""
    
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
        notebook.add(self.frame, text="JSON检测")
        
        self.frame.columnconfigure(0, weight=1)
        
        # 创建UI
        self._create_widgets()
    
    def _create_widgets(self):
        """创建界面控件"""
        # 路径选择区域
        path_frame = ttk.LabelFrame(self.frame, text="检测路径（检测JSON语法/结构/编码错误）", padding="10")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        path_frame.columnconfigure(1, weight=1)
        
        # 路径输入
        ttk.Label(path_frame, text="路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=("Microsoft YaHei", 9))
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(0, 5))
        
        ttk.Button(path_frame, text="浏览文件夹", command=self._browse_folder).grid(row=0, column=2, pady=(0, 5))
        
        # 操作按钮区域
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 主要操作按钮
        self.detect_button = ttk.Button(button_frame, text="🔍 开始检测", 
                                       command=self._start_detection, style='Accent.TButton')
        self.detect_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 辅助操作按钮
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清空结果", command=self._clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.save_button = ttk.Button(button_frame, text="💾 保存报告", 
                                     command=self._save_report, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 查看结果按钮
        self.view_button = ttk.Button(button_frame, text="👁️ 查看结果", 
                                     command=lambda: self.app.show_results_dialog('json_detector'))
        self.view_button.pack(side=tk.LEFT)
    
    def _browse_folder(self):
        """浏览JSON文件夹"""
        folder_path = filedialog.askdirectory(title="选择包含JSON文件的文件夹")
        if folder_path:
            self.path_var.set(folder_path)
    
    def _start_detection(self):
        """开始JSON错误检测"""
        path = self.path_var.get().strip()
        
        if not path:
            messagebox.showerror("错误", "请选择路径")
            return
        
        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在")
            return
        
        # 在新线程中执行检测
        self.detect_button.config(state="disabled")
        self.app.status_var.set("正在检测...")
        
        thread = threading.Thread(target=self._detection_thread, args=(path,))
        thread.daemon = True
        thread.start()
    
    def _detection_thread(self, path):
        """JSON错误检测（后台线程）"""
        try:
            # 自动检测：如果是文件夹则检测文件夹，如果是文件则检测单个文件
            if os.path.isdir(path):
                report = self.app.json_detector.detect_errors_in_folder(path)
            else:
                report = self.app.json_detector.detect_errors(path)
            
            self.app.root.after(0, self._update_results, report)
        except Exception as e:
            error_msg = f"检测过程中发生错误: {str(e)}"
            self.app.root.after(0, self._show_error, error_msg)
    
    def _update_results(self, report):
        """更新检测结果"""
        self.app.clear_result('json_detector')
        self.app.append_result('json_detector', report)
        
        self.detect_button.config(state="normal")
        self.save_button.config(state="normal")
        self.app.status_var.set("检测完成")
        messagebox.showinfo("完成", "JSON检测完成！请点击查看结果按钮查看详细报告")
    
    def _show_error(self, error_msg):
        """显示错误"""
        self.app.clear_result('json_detector')
        self.app.append_result('json_detector', error_msg)
        
        self.detect_button.config(state="normal")
        self.app.status_var.set("检测失败")
        messagebox.showerror("错误", error_msg)
    
    def _clear_results(self):
        """清空结果"""
        self.app.clear_result('json_detector')
        self.save_button.config(state="disabled")
    
    def _save_report(self):
        """保存检测报告"""
        content = self.app.get_result('json_detector').strip()
        if not content:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存检测报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"报告已保存到: {file_path}")
                self.app.status_var.set(f"报告已保存: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # 兼容旧API的属性映射
    @property
    def json_path_var(self):
        return self.path_var
    
    @property
    def json_detect_button(self):
        return self.detect_button
    
    @property
    def json_save_button(self):
        return self.save_button
