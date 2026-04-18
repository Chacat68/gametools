import os
import sys
import tkinter as tk
from tkinter import ttk

# 环境清理与设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['FTP_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

# 添加路径
sys.path.insert(0, r'F:\webserver\public\tools\gametools')
sys.path.insert(0, r'F:\webserver\public\tools\gametools\gui')

try:
    from gui.gametools_unified import GameToolsUnified
    
    root = tk.Tk()
    root.withdraw() # 隐藏窗口以防干扰，但仍需实例化
    
    app = GameToolsUnified(root)
    root.update_idletasks()
    
    # 1) 页签数量
    tabs = app.notebook.tabs()
    print(f"Tab count: {len(tabs)}")
    
    # 2) 每个主要功能页顶层直接子控件数量
    for meta in app.tab_registry:
        print(f"Page '{meta['title']}' child count: {len(meta['frame'].winfo_children())}")
        
    # 3) 跨项目页 (cross_project_translator)、JSON页 (json_detector)、数据处理页 (excel_data_processor)
    # 的第一个直接子控件的子框架数量
    keys_to_check = ['cross_project_translator', 'json_detector', 'excel_data_processor']
    for key in keys_to_check:
        meta = app.tab_lookup.get(key)
        if meta:
            frame = meta['frame']
            children = frame.winfo_children()
            if children:
                sub_count = len(children[0].winfo_children())
                print(f"Key '{key}' first child sub-frame count: {sub_count}")
            else:
                print(f"Key '{key}' has no children")
                
    # 4) 跨项目页主按钮文本列表
    # 根据源代码，这些按钮存储在 app 实例变量中
    cp_buttons = []
    if hasattr(app, 'cpt_process_button'): cp_buttons.append(app.cpt_process_button.cget('text'))
    if hasattr(app, 'cpt_clear_button'): cp_buttons.append(app.cpt_clear_button.cget('text'))
    if hasattr(app, 'cpt_export_button'): cp_buttons.append(app.cpt_export_button.cget('text'))
    if hasattr(app, 'cpt_view_results_button'): cp_buttons.append(app.cpt_view_results_button.cget('text'))
    print(f"CP buttons: {cp_buttons}")
    
    root.destroy()
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
