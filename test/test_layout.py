#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新布局的简单脚本
"""

import sys
import os
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from gui.gametools_unified import GameToolsUnified
    import tkinter as tk
    
    def test_layout():
        """测试新布局"""
        print("正在启动GUI测试...")
        
        root = tk.Tk()
        app = GameToolsUnified(root)
        
        # 设置窗口关闭事件
        def on_closing():
            print("GUI测试完成")
            root.quit()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 显示窗口信息
        print(f"窗口大小: {root.winfo_reqwidth()}x{root.winfo_reqheight()}")
        print("GUI布局测试启动成功！")
        
        # 启动主循环
        root.mainloop()
    
    if __name__ == "__main__":
        test_layout()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖模块都已正确安装")
except Exception as e:
    print(f"运行错误: {e}")
