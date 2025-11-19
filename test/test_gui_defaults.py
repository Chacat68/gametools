#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证GUI默认设置
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from gui.gametools_unified import GameToolsUnified


def test_default_values():
    """测试GUI的默认值"""
    
    print("=" * 60)
    print("测试GUI默认设置")
    print("=" * 60)
    
    # 创建主窗口（但不显示）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建应用实例
    app = GameToolsUnified(root)
    
    # 检查各个tab的递归扫描默认值
    tests = [
        ("越南语处理器", app.vp_recursive_var.get(), False),
        ("文本提取器", app.extractor_recursive_var.get(), False),
        ("字段导出器", app.field_recursive_var.get(), False),
    ]
    
    passed = 0
    failed = 0
    
    for name, actual, expected in tests:
        if actual == expected:
            print(f"✓ {name}: 递归扫描默认值 = {actual} (期望: {expected})")
            passed += 1
        else:
            print(f"✗ {name}: 递归扫描默认值 = {actual} (期望: {expected})")
            failed += 1
    
    print("=" * 60)
    print(f"测试完成: 通过 {passed}/{len(tests)}, 失败 {failed}/{len(tests)}")
    print("=" * 60)
    
    # 清理
    root.destroy()
    
    return failed == 0


if __name__ == "__main__":
    success = test_default_values()
    sys.exit(0 if success else 1)
