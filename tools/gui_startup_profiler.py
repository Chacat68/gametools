#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI启动性能诊断脚本
用于测试当前GUI启动耗时和各个部分的耗时分析
"""

import time
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def profile_import_time():
    """测试导入各模块的耗时"""
    print("\n" + "="*60)
    print("导入性能分析")
    print("="*60)
    
    modules_to_test = [
        ('tkinter', 'tkinter'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('xlwings', 'xlwings'),
        ('openpyxl', 'openpyxl'),
        ('core', 'core'),
        ('JSONErrorDetector', 'tools.json_error_detector.json_error_detector'),
    ]
    
    for display_name, module_name in modules_to_test:
        start = time.time()
        try:
            __import__(module_name)
            elapsed = (time.time() - start) * 1000
            print(f"✓ {display_name:25s}: {elapsed:8.2f}ms")
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            print(f"✗ {display_name:25s}: {elapsed:8.2f}ms (错误: {e})")


def profile_gui_startup():
    """测试GUI启动耗时"""
    print("\n" + "="*60)
    print("GUI启动性能分析")
    print("="*60)
    
    # 添加项目路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 测试总启动时间
    start_total = time.time()
    
    # 1. 导入GUI模块
    print("\n1. 导入GUI模块...")
    start = time.time()
    from gui.gametools_unified import GameToolsUnified
    elapsed = (time.time() - start) * 1000
    print(f"   导入耗时: {elapsed:.2f}ms")
    
    # 2. 初始化Tkinter
    print("\n2. 初始化Tkinter...")
    start = time.time()
    import tkinter as tk
    root = tk.Tk()
    elapsed = (time.time() - start) * 1000
    print(f"   初始化耗时: {elapsed:.2f}ms")
    
    # 3. 创建GUI实例
    print("\n3. 创建GUI实例...")
    start = time.time()
    gui = GameToolsUnified(root)
    elapsed = (time.time() - start) * 1000
    print(f"   创建耗时: {elapsed:.2f}ms")
    
    # 4. 总耗时
    total_elapsed = (time.time() - start_total) * 1000
    print(f"\n📊 总启动耗时: {total_elapsed:.2f}ms ({total_elapsed/1000:.2f}s)")
    
    # 5. 分析Tab创建状态
    print(f"\n5. Tab创建状态:")
    print(f"   已创建的Tab: {sum(1 for v in gui._created_tabs.values() if v)}")
    print(f"   未创建的Tab: {sum(1 for v in gui._created_tabs.values() if not v)}")
    
    # 6. 模块缓存状态
    print(f"\n6. 模块缓存状态:")
    print(f"   已加载的处理器: {list(gui._processors.keys())}")
    
    return root, gui, total_elapsed


def profile_tab_creation():
    """测试各Tab创建耗时"""
    print("\n" + "="*60)
    print("Tab创建性能分析")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    import tkinter as tk
    from gui.gametools_unified import GameToolsUnified
    
    root = tk.Tk()
    gui = GameToolsUnified(root)
    
    # 模拟切换到各个Tab
    tab_keys = list(gui.tab_configs.keys())
    
    print(f"\n总共{len(tab_keys)}个Tab，按顺序加载：\n")
    
    for idx, tab_key in enumerate(tab_keys):
        print(f"{idx+1}. 切换到 '{gui.tab_configs[tab_key]['label']}'...")
        
        start = time.time()
        
        # 模拟Tab切换
        gui.notebook.select(idx)
        gui._on_tab_changed(None)
        root.update_idletasks()
        
        elapsed = (time.time() - start) * 1000
        print(f"   加载耗时: {elapsed:.2f}ms\n")
    
    return root, gui


def main():
    """主诊断程序"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "gametools GUI 性能诊断工具" + " "*16 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # 1. 导入性能
        profile_import_time()
        
        # 2. GUI启动性能
        root, gui, startup_time = profile_gui_startup()
        
        # 3. 性能建议
        print("\n" + "="*60)
        print("性能分析和建议")
        print("="*60)
        
        if startup_time > 2000:
            print("\n⚠️  启动时间 > 2秒，建议进行优化：")
            print("   - 实施延迟Tab加载（推荐）")
            print("   - 优化模块导入时间")
            print("   - 后台预加载常用处理器")
        elif startup_time > 1000:
            print("\n⚡ 启动时间 > 1秒，可进行优化：")
            print("   - 考虑实施延迟Tab加载")
        else:
            print("\n✓ 启动时间优良，无需优化")
        
        print("\n📖 详细优化方案请参考: docs/GUI_STARTUP_OPTIMIZATION.md")
        print("📝 实现示例代码请参考: docs/GUI_OPTIMIZATION_IMPLEMENTATION.py")
        
        # 4. 清理
        root.quit()
        root.destroy()
        
    except Exception as e:
        logger.error(f"诊断失败: {e}", exc_info=True)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
