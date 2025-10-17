#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查mixed_test.xlsx文件内容
"""

import pandas as pd
import os


def check_mixed_test():
    """检查mixed_test.xlsx文件内容"""
    file_path = "test_excel_files/mixed_test.xlsx"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        print(f"文件: {file_path}")
        print(f"列名: {list(df.columns)}")
        print(f"行数: {len(df)}")
        print("\n内容:")
        print(df.to_string())
        
        # 检查是否有必要的列
        required_columns = ['文件名列', '位置列']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"\n缺少必要的列: {missing_columns}")
            print("需要将列名改为: 文件名列, 位置列")
        else:
            print("\n列名正确!")
            
    except Exception as e:
        print(f"读取文件失败: {e}")


if __name__ == "__main__":
    check_mixed_test()
