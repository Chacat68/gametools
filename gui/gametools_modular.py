#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools - 统一用户界面（模块化版本）
使用拆分的标签页模块，代码更清晰
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入core模块
import core
from version import get_version

# 导入标签页模块
from gui.tabs import (
    CrossProjectTranslatorTab, 
    JsonDetectorTab, 
    AboutTab,
    SheetSplitterTab,
    FieldExtractorTab,
    TableRangeTranslatorTab,
    BatchModifierTab,
    ConfigSyncTab,
    CsvConverterTab
)


class GameToolsModular:
    """gametools统一界面（模块化版本）"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"gametools v{get_version()}")
        self.root.geometry("950x700")
        self.root.minsize(850, 600)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 设置样式
        self._setup_styles()
        
        # 结果存储
        self.results_storage = {
            'cross_project_translator': '',
            'json_detector': '',
            'excel_processor': '',
            'field_extractor': '',
            'table_range_translator': '',
            'sheet_splitter': '',
            'batch_modifier': '',
            'config_sync': '',
            'csv_converter': ''
        }
        
        # 创建界面
        self._create_widgets()
    
    def _setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Microsoft YaHei', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Microsoft YaHei', 11, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei', 9))
        style.configure('Success.TLabel', font=('Microsoft YaHei', 9), foreground='green')
        style.configure('Error.TLabel', font=('Microsoft YaHei', 9), foreground='red')
        style.configure('Accent.TButton', font=('Microsoft YaHei', 9, 'bold'))
    
    def _create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # 创建笔记本控件（页签）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 使用模块化的标签页 - 按功能组织
        self.tabs = {}
        
        # 翻译提取相关
        self.tabs['field_extractor'] = FieldExtractorTab(self.notebook, self)
        self.notebook.add(self.tabs['field_extractor'].frame, text="字段导出")
        
        self.tabs['table_range_translator'] = TableRangeTranslatorTab(self.notebook, self)
        self.notebook.add(self.tabs['table_range_translator'].frame, text="翻译提取")
        
        self.tabs['cross_project'] = CrossProjectTranslatorTab(self.notebook, self)
        self.notebook.add(self.tabs['cross_project'].frame, text="跨项目翻译")
        
        # Excel处理相关
        self.tabs['batch_modifier'] = BatchModifierTab(self.notebook, self)
        self.notebook.add(self.tabs['batch_modifier'].frame, text="批量改表")
        
        self.tabs['sheet_splitter'] = SheetSplitterTab(self.notebook, self)
        self.notebook.add(self.tabs['sheet_splitter'].frame, text="分页拆分")
        
        self.tabs['config_sync'] = ConfigSyncTab(self.notebook, self)
        self.notebook.add(self.tabs['config_sync'].frame, text="配置同步")
        
        self.tabs['csv_converter'] = CsvConverterTab(self.notebook, self)
        self.notebook.add(self.tabs['csv_converter'].frame, text="Excel转CSV")
        
        # 辅助工具
        self.tabs['json_detector'] = JsonDetectorTab(self.notebook, self)
        self.notebook.add(self.tabs['json_detector'].frame, text="JSON检测")
        
        # 关于页面
        self.tabs['about'] = AboutTab(self.notebook, self)
        self.notebook.add(self.tabs['about'].frame, text="关于")
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding="3")
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
    
    # ==================== 结果存储方法 ====================
    
    def append_result(self, result_type: str, text: str):
        """追加文本到结果存储"""
        self.results_storage[result_type] += text
    
    def clear_result(self, result_type: str):
        """清空结果存储"""
        self.results_storage[result_type] = ''
    
    def get_result(self, result_type: str) -> str:
        """获取结果存储内容"""
        return self.results_storage.get(result_type, '')
    
    def show_results_dialog(self, result_type: str):
        """显示结果查看对话框"""
        result_content = self.results_storage.get(result_type, '')
        
        if not result_content.strip():
            messagebox.showinfo("提示", "暂无处理结果")
            return
        
        # 创建对话框窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("查看处理结果")
        dialog.geometry("900x700")
        dialog.minsize(700, 500)
        
        # 结果标题映射
        title_map = {
            'cross_project_translator': '跨项目翻译对应结果',
            'json_detector': 'JSON错误检测结果',
            'excel_processor': 'Excel数据处理结果',
            'field_extractor': '表字段导出结果',
            'table_range_translator': '多语言翻译提取结果',
            'batch_modifier': '批量改表结果',
            'config_sync': 'Excel配置同步结果',
            'csv_converter': 'Excel转CSV结果'
        }
        
        # 标题
        title_frame = ttk.Frame(dialog, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, 
                               text=title_map.get(result_type, '处理结果'),
                               style='Heading.TLabel')
        title_label.pack()
        
        # 结果显示区域
        result_frame = ttk.Frame(dialog, padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        result_text = scrolledtext.ScrolledText(result_frame, 
                                               wrap=tk.WORD, 
                                               font=("Consolas", 9))
        result_text.pack(fill=tk.BOTH, expand=True)
        result_text.insert(tk.END, result_content)
        result_text.config(state='disabled')
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(result_content)
            messagebox.showinfo("成功", "结果已复制到剪贴板")
        
        ttk.Button(button_frame, text="📋 复制到剪贴板", 
                  command=copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 5))
        
        def save_to_file():
            file_path = filedialog.asksaveasfilename(
                title="保存结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result_content)
                    messagebox.showinfo("成功", f"结果已保存到: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
        
        ttk.Button(button_frame, text="💾 保存到文件", 
                  command=save_to_file).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="关闭", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
        
        dialog.transient(self.root)
        dialog.grab_set()


def main():
    """主入口（模块化版本）"""
    root = tk.Tk()
    app = GameToolsModular(root)
    root.mainloop()


if __name__ == "__main__":
    main()
