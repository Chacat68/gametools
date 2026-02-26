#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新布局的简单脚本
非阻塞模式：创建窗口后自动验证并关闭，不进入mainloop
手动模式：传入 --interactive 参数可进入交互式主循环
"""

import sys
import os
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))


def test_layout(interactive: bool = False):
    """
    测试新布局
    
    Args:
        interactive: 是否进入交互式主循环（默认False，自动化测试用）
    """
    try:
        from gui.gametools_unified import GameToolsUnified
        import tkinter as tk
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖模块都已正确安装")
        return False

    try:
        print("正在启动GUI测试...")
        
        root = tk.Tk()
        app = GameToolsUnified(root)
        
        # 显示窗口信息
        root.update_idletasks()
        print(f"窗口大小: {root.winfo_reqwidth()}x{root.winfo_reqheight()}")
        print("GUI布局测试启动成功！")
        
        if interactive:
            # 交互模式：进入主循环
            def on_closing():
                print("GUI测试完成")
                root.quit()
                root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()
        else:
            # 自动化模式：验证窗口创建成功后立即关闭
            print("✅ GUI创建验证通过（自动化模式，窗口已自动关闭）")
            root.destroy()
        
        return True
    except Exception as e:
        print(f"运行错误: {e}")
        return False


if __name__ == "__main__":
    interactive = "--interactive" in sys.argv
    success = test_layout(interactive=interactive)
    sys.exit(0 if success else 1)
