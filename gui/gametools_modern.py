# -*- coding: utf-8 -*-
"""
GameTools 现代化统一界面
采用侧边栏导航 + 内容区布局

特性：
- 现代化扁平设计风格
- 左侧导航栏，右侧内容区
- 页面延迟加载，启动速度快
- 支持主题切换
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 修复 PyInstaller 环境下的导入问题
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    from gui.import_helper import fix_pyinstaller_imports
else:
    try:
        from .import_helper import fix_pyinstaller_imports
    except ImportError:
        from gui.import_helper import fix_pyinstaller_imports

fix_pyinstaller_imports()

# 添加模块路径
if not hasattr(sys, 'frozen'):
    sys.path.append(str(Path(__file__).parent.parent))

# 导入主题和组件
from gui.modern_theme import ModernTheme
from gui.components.sidebar import ModernSidebar, SidebarItem
from gui.components.widgets import ModernStatusBar

# 导入版本信息
try:
    from version import get_version
except ImportError:
    def get_version():
        return "1.44.0"


class GameToolsModern:
    """GameTools 现代化界面主类"""
    
    # 功能页面配置
    PAGE_CONFIG = [
        # (key, title, icon, group, page_class_name)
        ("home", "首页", "🏠", "main", "HomePage"),
        ("batch_modifier", "批量改表", "⚡", "excel", "BatchModifierPage"),
        ("field_extractor", "字段导出", "📋", "excel", "FieldExtractorPage"),
        ("sheet_splitter", "分页拆分", "✂️", "excel", "SheetSplitterPage"),
        ("config_sync", "配置同步", "🔗", "excel", "ConfigSyncPage"),
        ("csv_converter", "Excel转CSV", "📄", "excel", "CsvConverterPage"),
        ("excel_processor", "数据处理", "📊", "excel", "ExcelProcessorPage"),
        ("cross_project", "跨项目翻译", "🔄", "translate", "CrossProjectPage"),
        ("table_range", "多语言提取", "🌐", "translate", "TableRangePage"),
        ("json_detector", "JSON检测", "🔍", "tools", "JsonDetectorPage"),
        ("about", "关于", "ℹ️", "other", "AboutPage"),
    ]
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"GameTools v{get_version()}")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # 初始化主题
        self.theme = ModernTheme(is_dark=False)
        self.theme.apply_to_root(root)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 页面缓存
        self._pages = {}
        self._current_page_key = None
        
        # 创建界面
        self._create_layout()
        
        # 显示首页
        self._navigate_to("home")
    
    def _create_layout(self):
        """创建主布局"""
        # 配置根窗口
        self.root.configure(bg=self.theme.colors["bg_main"])
        self.root.columnconfigure(0, weight=0)  # 侧边栏固定宽度
        self.root.columnconfigure(1, weight=1)  # 内容区自适应
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)     # 状态栏固定高度
        
        # 创建侧边栏
        self._create_sidebar()
        
        # 创建内容区
        self._create_content_area()
        
        # 创建状态栏
        self._create_status_bar()
    
    def _create_sidebar(self):
        """创建侧边栏"""
        self.sidebar = ModernSidebar(
            self.root,
            self.theme,
            on_select=self._navigate_to
        )
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # 加载可见性配置
        visible_pages = self._load_visible_pages()
        
        # 添加导航项
        current_group = None
        group_labels = {
            "main": "主页",
            "excel": "Excel 工具",
            "translate": "翻译工具",
            "tools": "其他工具",
            "other": "更多",
        }
        
        for key, title, icon, group, _ in self.PAGE_CONFIG:
            # 检查是否应该显示此页面
            if key != "home" and not visible_pages.get(key, True):
                continue
                
            # 添加分组标签
            if group != current_group:
                if current_group is not None:
                    pass  # 可以添加分隔线
                self.sidebar.add_group_label(group_labels.get(group, group))
                current_group = group
            
            # 添加导航项
            item = SidebarItem(key=key, title=title, icon=icon, group=group)
            self.sidebar.add_item(item)
    
    def _load_visible_pages(self):
        """加载页面可见性配置"""
        import json
        from pathlib import Path
        
        config_path = Path("config.json")
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("visible_pages", {})
        except:
            return {}
    
    def _create_content_area(self):
        """创建内容区域"""
        self.content_area = tk.Frame(
            self.root,
            bg=self.theme.colors["bg_main"]
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ModernStatusBar(self.root, self.theme)
        self.status_bar.grid(row=1, column=1, sticky="ew")
        
        # 设置初始状态
        self.status_bar.set_info(f"v{get_version()}")
    
    def _navigate_to(self, page_key: str):
        """导航到指定页面"""
        if page_key == self._current_page_key:
            return
        
        # 隐藏当前页面
        if self._current_page_key and self._current_page_key in self._pages:
            self._pages[self._current_page_key].pack_forget()
        
        # 获取或创建页面
        page = self._get_or_create_page(page_key)
        if page:
            page.pack(fill=tk.BOTH, expand=True)
            page.initialize()  # 延迟初始化
            self._current_page_key = page_key
            self.sidebar.select(page_key)
            
            # 更新状态栏
            page_title = self._get_page_title(page_key)
            self.status_bar.set_status(f"当前: {page_title}")
    
    def _get_or_create_page(self, page_key: str):
        """获取或创建页面实例"""
        if page_key in self._pages:
            return self._pages[page_key]
        
        # 查找页面配置
        page_config = None
        for config in self.PAGE_CONFIG:
            if config[0] == page_key:
                page_config = config
                break
        
        if not page_config:
            return None
        
        key, title, icon, group, page_class_name = page_config
        
        # 创建页面实例
        page = None
        try:
            if page_class_name:
                page = self._create_page_by_class(page_key, page_class_name)
            else:
                # 使用占位页面
                page = self._create_placeholder_page(page_key, title, icon)
        except Exception as e:
            print(f"创建页面 {page_key} 失败: {e}")
            page = self._create_placeholder_page(page_key, title, icon, str(e))
        
        if page:
            self._pages[page_key] = page
        
        return page
    
    def _create_page_by_class(self, page_key: str, class_name: str):
        """根据类名创建页面"""
        # 动态导入页面类
        if class_name == "HomePage":
            from gui.pages.home_page import HomePage
            return HomePage(self.content_area, self, self.theme, 
                          on_navigate=self._navigate_to)
        elif class_name == "AboutPage":
            from gui.pages.about_page import AboutPage
            return AboutPage(self.content_area, self, self.theme)
        elif class_name == "BatchModifierPage":
            from gui.pages.batch_modifier_page import BatchModifierPage
            return BatchModifierPage(self.content_area, self, self.theme)
        elif class_name == "JsonDetectorPage":
            from gui.pages.json_detector_page import JsonDetectorPage
            return JsonDetectorPage(self.content_area, self, self.theme)
        elif class_name == "FieldExtractorPage":
            from gui.pages.field_extractor_page import FieldExtractorPage
            return FieldExtractorPage(self.content_area, self, self.theme)
        elif class_name == "CsvConverterPage":
            from gui.pages.csv_converter_page import CsvConverterPage
            return CsvConverterPage(self.content_area, self, self.theme)
        elif class_name == "SheetSplitterPage":
            from gui.pages.sheet_splitter_page import SheetSplitterPage
            return SheetSplitterPage(self.content_area, self, self.theme)
        elif class_name == "ConfigSyncPage":
            from gui.pages.config_sync_page import ConfigSyncPage
            return ConfigSyncPage(self.content_area, self, self.theme)
        elif class_name == "ExcelProcessorPage":
            from gui.pages.excel_processor_page import ExcelProcessorPage
            return ExcelProcessorPage(self.content_area, self, self.theme)
        elif class_name == "CrossProjectPage":
            from gui.pages.cross_project_page import CrossProjectPage
            return CrossProjectPage(self.content_area, self, self.theme)
        elif class_name == "TableRangePage":
            from gui.pages.table_range_page import TableRangePage
            return TableRangePage(self.content_area, self, self.theme)
        else:
            return None
    
    def _create_placeholder_page(self, page_key: str, title: str, 
                                  icon: str, error_msg: str = None):
        """创建占位页面（功能待实现）"""
        from gui.pages.base_page import ModernPage
        
        class PlaceholderPage(ModernPage):
            PAGE_KEY = page_key
            PAGE_TITLE = title
            PAGE_ICON = icon
            PAGE_DESCRIPTION = "此功能页面正在开发中"
            
            def __init__(self, parent, app, theme, error=None):
                self.error = error
                super().__init__(parent, app, theme)
            
            def create_widgets(self):
                # 居中提示
                center_frame = tk.Frame(self.content, bg=self.theme.colors["bg_main"])
                center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                icon_label = tk.Label(
                    center_frame,
                    text=self.PAGE_ICON,
                    font=("Segoe UI Emoji", 48),
                    bg=self.theme.colors["bg_main"],
                    fg=self.theme.colors["text_muted"]
                )
                icon_label.pack()
                
                title_label = tk.Label(
                    center_frame,
                    text=self.PAGE_TITLE,
                    font=self.theme.FONTS["heading"],
                    bg=self.theme.colors["bg_main"],
                    fg=self.theme.colors["text_secondary"]
                )
                title_label.pack(pady=(16, 8))
                
                if self.error:
                    msg = f"加载错误: {self.error}"
                    fg = self.theme.colors["error"]
                else:
                    msg = "此功能正在开发中，敬请期待..."
                    fg = self.theme.colors["text_muted"]
                
                desc_label = tk.Label(
                    center_frame,
                    text=msg,
                    font=self.theme.FONTS["body"],
                    bg=self.theme.colors["bg_main"],
                    fg=fg
                )
                desc_label.pack()
        
        return PlaceholderPage(self.content_area, self, self.theme, error_msg)
    
    def _get_page_title(self, page_key: str) -> str:
        """获取页面标题"""
        for config in self.PAGE_CONFIG:
            if config[0] == page_key:
                return config[1]
        return page_key


def main():
    """主函数"""
    root = tk.Tk()
    app = GameToolsModern(root)
    root.mainloop()


if __name__ == "__main__":
    main()
