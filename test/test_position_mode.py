#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Position模式的批量改表功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.batch_excel_modifier import BatchExcelModifier
import pandas as pd

def test_position_detection():
    """测试Position列检测"""
    print("=" * 60)
    print("测试1: Position列检测")
    print("=" * 60)
    
    modifier = BatchExcelModifier()
    
    # 创建测试CSV数据（翻译提取格式）
    test_data = {
        'Table': ['test.xlsx', 'test.xlsx', 'test.xlsx'],
        'Sheet': ['sheet1', 'sheet1', 'sheet1'],
        'Field': ['name', 'name', 'desc'],
        'Type': ['前端', '前端', '前端'],
        'Position': ['B7', 'B8', 'E7'],
        'ZH': ['测试1', '测试2', '描述1'],
        'VN': ['Test 1', 'Test 2', 'Description 1'],
        'TH': ['ทดสอบ1', 'ทดสอบ2', 'คำอธิบาย1']
    }
    
    df = pd.DataFrame(test_data)
    
    # 测试格式转换
    print("\n原始DataFrame:")
    print(df.head())
    print(f"\n列名: {df.columns.tolist()}")
    
    # 调用转换函数
    converted_df = modifier._convert_csv_format_if_needed(df)
    
    print("\n转换后DataFrame:")
    print(converted_df.head())
    print(f"\n列名: {converted_df.columns.tolist()}")
    
    # 检查是否保留了Position列
    if 'Position' in converted_df.columns:
        print("\n✓ 成功：Position列已保留")
        print(f"Position列数据: {converted_df['Position'].tolist()}")
    else:
        print("\n✗ 失败：Position列未保留")
        return False
    
    # 检查是否有Classification列
    if 'Classification' in converted_df.columns:
        print("✓ 成功：Classification列已创建")
        print(f"Classification列数据: {converted_df['Classification'].tolist()}")
    else:
        print("✗ 失败：Classification列未创建")
        return False
    
    # 检查语言列是否保留
    lang_cols = ['VN', 'TH']
    for col in lang_cols:
        if col in converted_df.columns:
            print(f"✓ 成功：{col}列已保留")
        else:
            print(f"✗ 失败：{col}列未保留")
            return False
    
    return True

def test_position_parsing():
    """测试Position字符串解析"""
    print("\n" + "=" * 60)
    print("测试2: Position字符串解析")
    print("=" * 60)
    
    from core.batch_excel_modifier import get_column_number, get_column_letter
    
    test_cases = [
        ('A', 1),
        ('B', 2),
        ('Z', 26),
        ('AA', 27),
        ('AB', 28),
        ('AZ', 52),
        ('BA', 53),
    ]
    
    all_passed = True
    for letter, expected_num in test_cases:
        result = get_column_number(letter)
        if result == expected_num:
            print(f"✓ {letter} -> {result} (期望: {expected_num})")
        else:
            print(f"✗ {letter} -> {result} (期望: {expected_num})")
            all_passed = False
    
    # 测试反向转换
    print("\n反向测试 (数字->字母):")
    for letter, num in test_cases:
        result = get_column_letter(num)
        if result == letter:
            print(f"✓ {num} -> {result} (期望: {letter})")
        else:
            print(f"✗ {num} -> {result} (期望: {letter})")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("开始测试Position模式批量改表功能\n")
    
    test1_passed = test_position_detection()
    test2_passed = test_position_parsing()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试1 (Position列检测): {'通过' if test1_passed else '失败'}")
    print(f"测试2 (Position解析): {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 有测试失败，请检查代码")
        return 1

if __name__ == '__main__':
    sys.exit(main())
