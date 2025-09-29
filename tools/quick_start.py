#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 策划本地化工具
"""

import os
import sys
from pathlib import Path


def main():
    """快速启动主函数"""
    print("=" * 60)
    print("策划本地化工具 - 越南文表格检测器")
    print("=" * 60)
    print()
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    print()
    
    # 询问用户是否扫描当前目录
    choice = input("是否扫描当前目录? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是', '']:
        directory_path = current_dir
    else:
        directory_path = input("请输入要扫描的目录路径: ").strip()
        if not directory_path:
            print("未提供目录路径，退出程序")
            return
    
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 目录 '{directory_path}' 不存在")
        return
    
    if not os.path.isdir(directory_path):
        print(f"错误: '{directory_path}' 不是一个目录")
        return
    
    print()
    print("开始扫描...")
    print("-" * 40)
    
    # 导入并运行检测器
    try:
        from localization_checker import LocalizationChecker
        checker = LocalizationChecker()
        valid_tables = checker.scan_directory(directory_path)
        checker.print_results(valid_tables)
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保 localization_checker.py 文件存在")
    except Exception as e:
        print(f"运行错误: {e}")
    
    print()
    try:
        input("按回车键退出...")
    except EOFError:
        # 在自动化环境中忽略EOF错误
        pass


if __name__ == "__main__":
    main()
