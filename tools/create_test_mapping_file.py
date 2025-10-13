#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试映射文件，使用正确的列名
"""

import pandas as pd
import os


def create_test_mapping_file():
    """创建测试映射文件"""
    # 创建测试数据
    mapping_data = {
        '序号': [1, 2, 3, 4],
        '文件名列': ['vietnamese_test.xlsx', 'vietnamese_test.xlsx', 'vietnamese_test1.xlsx', 'vietnamese_test1.xlsx'],
        '位置列': ['C2', 'C4', 'C3', 'C1'],
        '说明': ['物品名称', '物品价格', '技能描述', '角色名称']
    }
    
    # 创建DataFrame
    mapping_df = pd.DataFrame(mapping_data)
    
    # 保存到文件
    output_file = "test_excel_files/mixed_test_new.xlsx"
    mapping_df.to_excel(output_file, index=False)
    
    print(f"测试映射文件已创建: {output_file}")
    print("\n文件内容:")
    print(mapping_df.to_string())
    
    print(f"\n列名: {list(mapping_df.columns)}")
    print("预期结果:")
    print("- 第1行: vietnamese_test.xlsx (C2) -> 金庸")
    print("- 第2行: vietnamese_test.xlsx (C4) -> 你好")
    print("- 第3行: vietnamese_test1.xlsx (C3) -> 电视")
    print("- 第4行: vietnamese_test1.xlsx (C1) -> 三国")


if __name__ == "__main__":
    create_test_mapping_file()
