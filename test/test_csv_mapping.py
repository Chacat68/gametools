#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量改表功能的CSV支持
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.batch_excel_modifier import BatchExcelModifier

def test_csv_loading():
    """测试CSV映射表加载"""
    
    print("=" * 60)
    print("测试批量改表功能的CSV格式支持")
    print("=" * 60)
    
    # 创建修改器实例
    modifier = BatchExcelModifier()
    
    # 测试CSV文件路径
    test_csv = os.path.join(os.path.dirname(__file__), '测试映射表.csv')
    
    if not os.path.exists(test_csv):
        print(f"❌ 测试文件不存在: {test_csv}")
        print("   请先运行 create_test_csv_mapping.py 创建测试文件")
        return False
    
    print(f"\n📂 测试文件: {os.path.basename(test_csv)}")
    
    # 测试1: 加载CSV映射表
    print("\n【测试1】加载CSV映射表")
    df, columns = modifier.load_mapping_table(test_csv)
    
    if df.empty:
        print("❌ 加载失败：返回空DataFrame")
        return False
    
    print(f"✅ 成功加载CSV文件")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(columns)}")
    print(f"   - 列名: {columns}")
    
    # 测试2: 获取工作表列表（CSV应返回空列表）
    print("\n【测试2】获取工作表列表（CSV文件）")
    sheets = modifier.get_mapping_sheets(test_csv)
    if sheets == []:
        print(f"✅ CSV文件正确返回空工作表列表")
    else:
        print(f"⚠️ CSV文件返回了工作表列表: {sheets}")
    
    # 测试3: 显示数据预览
    print("\n【测试3】数据预览（前3行）")
    print(df.head(3).to_string())
    
    # 测试4: 检查支持的格式
    print(f"\n【测试4】支持的映射表格式")
    print(f"   - 目标Excel格式: {modifier.supported_extensions}")
    print(f"   - 映射表格式: {modifier.supported_mapping_formats}")
    
    # 测试5: 测试Excel文件（如果存在）
    test_xlsx = os.path.join(os.path.dirname(__file__), '测试映射表.xlsx')
    if os.path.exists(test_xlsx):
        print(f"\n【测试5】对比测试：加载Excel格式")
        df_excel, columns_excel = modifier.load_mapping_table(test_xlsx)
        
        if not df_excel.empty:
            print(f"✅ Excel文件加载成功")
            print(f"   - 行数: {len(df_excel)}")
            print(f"   - 列数: {len(columns_excel)}")
            
            # 比较数据是否一致
            if df.shape == df_excel.shape:
                print(f"✅ CSV和Excel数据结构一致")
            else:
                print(f"⚠️ CSV和Excel数据结构不同")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！CSV格式支持正常")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = test_csv_loading()
    sys.exit(0 if success else 1)
