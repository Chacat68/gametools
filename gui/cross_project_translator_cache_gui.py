#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译对应工具缓存管理界面
集成缓存统计和管理功能的GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cross_project_translator_cached import CrossProjectTranslatorWithCache


class CacheManagementGUI:
    """翻译对应工具缓存管理界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("翻译对应工具 - 缓存管理版")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 初始化翻译对应工具
        self.translator = CrossProjectTranslatorWithCache(
            cache_dir=".cache",
            enable_file_cache=True,
            memory_cache_size=2000,
            cache_ttl=86400
        )
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 处理状态
        self.is_processing = False
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Microsoft YaHei', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 11, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 9))
        style.configure('Success.TLabel', font=('Microsoft YaHei', 9), foreground='green')
        style.configure('Error.TLabel', font=('Microsoft YaHei', 9), foreground='red')
        style.configure('Accent.TButton', font=('Microsoft YaHei', 10, 'bold'))
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="翻译对应工具 - 缓存管理版", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 创建笔记本（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 页签1：翻译对应处理
        self.create_translation_tab(notebook)
        
        # 页签2：缓存管理
        self.create_cache_management_tab(notebook)
        
        # 页签3：缓存统计
        self.create_cache_stats_tab(notebook)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
    
    def create_translation_tab(self, notebook):
        """创建翻译对应处理页签"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="翻译对应处理")
        
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # 映射文件选择
        ttk.Label(frame, text="映射文件:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mapping_file_entry = ttk.Entry(frame)
        self.mapping_file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="浏览...", command=self.select_mapping_file).grid(row=0, column=2, padx=5)
        
        # 项目目录选择
        ttk.Label(frame, text="项目目录:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.project_dir_entry = ttk.Entry(frame)
        self.project_dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="浏览...", command=self.select_project_dir).grid(row=1, column=2, padx=5)
        
        # 输出文件选择
        ttk.Label(frame, text="输出文件:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_file_entry = ttk.Entry(frame)
        self.output_file_entry.insert(0, "translation_results.xlsx")
        self.output_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="浏览...", command=self.select_output_file).grid(row=2, column=2, padx=5)
        
        # 缓存配置
        cache_config_frame = ttk.LabelFrame(frame, text="缓存配置", padding="5")
        cache_config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(cache_config_frame, text="缓存大小:").pack(side=tk.LEFT, padx=5)
        self.cache_size_spin = ttk.Spinbox(cache_config_frame, from_=100, to=10000, increment=100, width=10)
        self.cache_size_spin.set(2000)
        self.cache_size_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(cache_config_frame, text="过期时间(小时):").pack(side=tk.LEFT, padx=5)
        self.cache_ttl_spin = ttk.Spinbox(cache_config_frame, from_=1, to=720, increment=1, width=10)
        self.cache_ttl_spin.set(24)
        self.cache_ttl_spin.pack(side=tk.LEFT, padx=5)
        
        self.enable_file_cache_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cache_config_frame, text="启用文件缓存", 
                       variable=self.enable_file_cache_var).pack(side=tk.LEFT, padx=5)
        
        # 处理按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        
        ttk.Button(button_frame, text="开始处理", command=self.start_processing, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出结果", command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看报告", command=self.show_report).pack(side=tk.LEFT, padx=5)
        
        # 处理日志
        ttk.Label(frame, text="处理日志:", style='Heading.TLabel').grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(frame, height=15, font=('Courier New', 9))
        self.log_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 进度条
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(frame, text="就绪", style='Info.TLabel')
        self.progress_label.grid(row=8, column=0, columnspan=3, sticky=tk.W)
    
    def create_cache_management_tab(self, notebook):
        """创建缓存管理页签"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="缓存管理")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        # 缓存目录
        ttk.Label(frame, text="缓存目录:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cache_dir_entry = ttk.Entry(frame)
        self.cache_dir_entry.insert(0, ".cache")
        self.cache_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(frame, text="浏览...", command=self.select_cache_dir).grid(row=0, column=2, padx=5)
        
        # 缓存操作按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="刷新统计", command=self.refresh_cache_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清理过期", command=self.cleanup_expired).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空所有", command=self.clear_all_cache).pack(side=tk.LEFT, padx=5)
        
        # 缓存信息显示
        ttk.Label(frame, text="缓存详情:", style='Heading.TLabel').grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.cache_info_text = scrolledtext.ScrolledText(frame, height=20, font=('Courier New', 9))
        self.cache_info_text.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    
    def create_cache_stats_tab(self, notebook):
        """创建缓存统计页签"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="缓存统计")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # 统计刷新按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="刷新统计", command=self.refresh_stats).pack(side=tk.LEFT, padx=5)
        
        # 统计信息显示
        self.stats_text = scrolledtext.ScrolledText(frame, height=30, font=('Courier New', 9))
        self.stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    
    def create_status_bar(self, main_frame):
        """创建底部状态栏"""
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="就绪", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.cache_status_label = ttk.Label(status_frame, text="缓存: 就绪", relief=tk.SUNKEN)
        self.cache_status_label.pack(side=tk.LEFT, padx=5)
    
    def select_mapping_file(self):
        """选择映射文件"""
        filepath = filedialog.askopenfilename(
            title="选择映射文件",
            filetypes=[("Excel文件", "*.xlsx;*.xls"), ("所有文件", "*.*")]
        )
        if filepath:
            self.mapping_file_entry.delete(0, tk.END)
            self.mapping_file_entry.insert(0, filepath)
    
    def select_project_dir(self):
        """选择项目目录"""
        dirpath = filedialog.askdirectory(title="选择项目目录")
        if dirpath:
            self.project_dir_entry.delete(0, tk.END)
            self.project_dir_entry.insert(0, dirpath)
    
    def select_output_file(self):
        """选择输出文件"""
        filepath = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filepath:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, filepath)
    
    def select_cache_dir(self):
        """选择缓存目录"""
        dirpath = filedialog.askdirectory(title="选择缓存目录")
        if dirpath:
            self.cache_dir_entry.delete(0, tk.END)
            self.cache_dir_entry.insert(0, dirpath)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()
    
    def start_processing(self):
        """开始处理"""
        if self.is_processing:
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return
        
        mapping_file = self.mapping_file_entry.get().strip()
        project_dir = self.project_dir_entry.get().strip()
        
        if not mapping_file or not os.path.exists(mapping_file):
            messagebox.showerror("错误", "请选择有效的映射文件")
            return
        
        if not project_dir or not os.path.exists(project_dir):
            messagebox.showerror("错误", "请选择有效的项目目录")
            return
        
        # 在线程中执行处理
        thread = threading.Thread(
            target=self._process_thread,
            args=(mapping_file, project_dir)
        )
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, mapping_file, project_dir):
        """处理线程"""
        try:
            self.is_processing = True
            self.progress_label.config(text="处理中...")
            self.status_label.config(text="处理中...")
            
            # 更新缓存配置
            cache_ttl = int(self.cache_ttl_spin.get()) * 3600
            memory_size = int(self.cache_size_spin.get())
            
            self.translator = CrossProjectTranslatorWithCache(
                cache_dir=self.cache_dir_entry.get(),
                enable_file_cache=self.enable_file_cache_var.get(),
                memory_cache_size=memory_size,
                cache_ttl=cache_ttl
            )
            
            self.log_message(f"开始处理: {mapping_file}")
            self.log_message(f"项目目录: {project_dir}")
            
            # 处理翻译映射
            results = self.translator.process_translation_mapping(mapping_file, project_dir)
            
            self.log_message(f"处理完成: {len(results)} 条结果")
            
            # 获取缓存统计
            stats = self.translator.get_cache_stats()
            self.log_message(f"缓存命中: {stats['custom']['cache_hits']}")
            self.log_message(f"缓存未命中: {stats['custom']['cache_misses']}")
            self.log_message(f"命中率: {stats['custom']['hit_rate']}")
            
            self.progress_var.set(100)
            self.progress_label.config(text="处理完成！")
            self.status_label.config(text="就绪")
            
            messagebox.showinfo("成功", "处理完成！")
        
        except Exception as e:
            self.log_message(f"错误: {str(e)}")
            self.status_label.config(text="错误")
            messagebox.showerror("错误", str(e))
        
        finally:
            self.is_processing = False
    
    def export_results(self):
        """导出结果"""
        output_file = self.output_file_entry.get().strip()
        
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件路径")
            return
        
        if self.translator.translation_results:
            if self.translator.export_results(output_file):
                messagebox.showinfo("成功", f"结果已导出到: {output_file}")
                self.log_message(f"结果已导出到: {output_file}")
            else:
                messagebox.showerror("错误", "导出失败")
        else:
            messagebox.showwarning("提示", "没有可导出的结果")
    
    def show_report(self):
        """显示处理报告"""
        report = self.translator.get_processing_report()
        
        # 创建新窗口显示报告
        report_window = tk.Toplevel(self.root)
        report_window.title("处理报告")
        report_window.geometry("600x400")
        
        report_text = scrolledtext.ScrolledText(report_window, font=('Courier New', 10))
        report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        report_text.insert(tk.END, report)
        report_text.config(state=tk.DISABLED)
    
    def refresh_cache_stats(self):
        """刷新缓存统计"""
        self.cache_info_text.delete(1.0, tk.END)
        
        stats = self.translator.get_cache_stats()
        
        info_lines = [
            "=== 缓存统计信息 ===",
            "",
            "内存缓存:",
            f"  当前大小: {stats['memory']['size']}/{stats['memory']['max_size']}",
            f"  总请求数: {stats['memory']['total_requests']}",
            f"  缓存命中: {stats['memory']['hit_count']}",
            f"  缓存未命中: {stats['memory']['miss_count']}",
            f"  命中率: {stats['memory']['hit_rate']}",
        ]
        
        if stats['use_file_cache']:
            info_lines.extend([
                "",
                "文件缓存:",
                f"  缓存文件数: {stats['file']['count']}",
            ])
        
        info_lines.extend([
            "",
            "自定义统计:",
            f"  缓存命中次数: {stats['custom']['cache_hits']}",
            f"  缓存未命中次数: {stats['custom']['cache_misses']}",
            f"  缓存命中率: {stats['custom']['hit_rate']}",
        ])
        
        self.cache_info_text.insert(tk.END, "\n".join(info_lines))
    
    def cleanup_expired(self):
        """清理过期缓存"""
        result = messagebox.askyesno("确认", "确定要清理过期缓存吗？")
        if result:
            self.translator.cleanup_expired_cache()
            messagebox.showinfo("成功", "过期缓存已清理")
            self.log_message("过期缓存已清理")
            self.refresh_cache_stats()
    
    def clear_all_cache(self):
        """清空所有缓存"""
        result = messagebox.askyesno("确认", "确定要清空所有缓存吗？这个操作无法撤销。")
        if result:
            self.translator.clear_cache()
            messagebox.showinfo("成功", "所有缓存已清空")
            self.log_message("所有缓存已清空")
            self.refresh_cache_stats()
    
    def refresh_stats(self):
        """刷新统计信息"""
        self.stats_text.delete(1.0, tk.END)
        
        stats = self.translator.get_cache_stats()
        
        stats_lines = [
            "╔════════════════════════════════════════════╗",
            "║            缓存系统统计信息                ║",
            "╚════════════════════════════════════════════╝",
            "",
            "【内存缓存】",
            f"  当前大小:  {stats['memory']['size']}/{stats['memory']['max_size']}",
            f"  总请求数:  {stats['memory']['total_requests']}",
            f"  命中次数:  {stats['memory']['hit_count']}",
            f"  未命中次数: {stats['memory']['miss_count']}",
            f"  命中率:    {stats['memory']['hit_rate']}",
            "",
        ]
        
        if stats['use_file_cache']:
            stats_lines.extend([
                "【文件缓存】",
                f"  缓存文件数: {stats['file']['count']}",
                "",
            ])
        
        stats_lines.extend([
            "【查询统计】",
            f"  总命中次数:   {stats['custom']['cache_hits']}",
            f"  总未命中次数: {stats['custom']['cache_misses']}",
            f"  整体命中率:   {stats['custom']['hit_rate']}",
            "",
            "╔════════════════════════════════════════════╗",
        ])
        
        self.stats_text.insert(tk.END, "\n".join(stats_lines))
        self.stats_text.config(state=tk.DISABLED)


def main():
    """主函数"""
    root = tk.Tk()
    app = CacheManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
