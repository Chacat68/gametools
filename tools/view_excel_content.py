#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看Excel文件内容的工具
"""

import pandas as pd
import os
from pathlib import Path


def view_excel_content(file_path):
    """查看Excel文件内容"""
    try:
        print(f"查看文件: {file_path}")
        print("=" * 60)
        
        # 读取Excel文件
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n工作表: {sheet_name}")
            print("-" * 40)
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"行数: {len(df)}, 列数: {len(df.columns)}")
            print("\n列名:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col}")
            
            print("\n前10行数据:")
            try:
                print(df.head(10).to_string())
            except UnicodeEncodeError:
                # 处理编码问题
                for i, row in df.head(10).iterrows():
                    print(f"行{i}: {dict(row)}")
            
            print("\n" + "=" * 60)
            
    except Exception as e:
        print(f"读取文件失败: {e}")


def main():
    """主函数"""
    # 查看mixed_test.xlsx
    mixed_file = "test_excel_files/mixed_test.xlsx"
    if os.path.exists(mixed_file):
        view_excel_content(mixed_file)
    
    print("\n" + "=" * 80)
    
    # 查看新建文件夹中的文件
    folder_path = "test_excel_files/新建文件夹"
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(folder_path, file)
                view_excel_content(file_path)
                print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
