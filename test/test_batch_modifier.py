#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量改表功能测试脚本
测试 BatchExcelModifier 的核心功能
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from openpyxl import Workbook


def create_test_mapping_table(output_path):
    """创建测试用的映射表"""
    # 创建映射表数据
    data = {
        '表名': ['test_table_1.xlsx', 'test_table_1.xlsx', 'test_table_2.xlsx'],
        'Classification': ['des', 'des', 'des'],
        'ID': [1001, 1002, 2001],
        'VN': ['Nội dung mới 1', 'Nội dung mới 2', 'Nội dung mới 3'],
        'Support-CH': ['中文内容1', '中文内容2', '中文内容3'],
        'EN': ['New content 1', 'New content 2', 'New content 3']
    }
    
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False, sheet_name='Sheet1')
    print(f"创建映射表: {output_path}")
    return df


def create_test_excel_files(output_dir):
    """创建测试用的Excel文件"""
    # 创建 test_table_1.xlsx
    wb1 = Workbook()
    ws1 = wb1.active
    ws1.title = "test_table_1"
    
    # 设置数据结构（模拟标准表结构）
    # 第1-4行：其他信息
    # 第5行：字段名
    # 第6行：字段类型
    # 第7行开始：数据
    
    ws1['A1'] = '表名'
    ws1['A2'] = 'test_table_1'
    ws1['A3'] = ''
    ws1['A4'] = ''
    
    # 第5行：字段名
    ws1['A5'] = 'id'
    ws1['B5'] = 'name'
    ws1['C5'] = 'VN'
    ws1['D5'] = 'Support-CH'
    ws1['E5'] = 'EN'
    
    # 第6行：字段类型
    ws1['A6'] = '前后端'
    ws1['B6'] = '前端'
    ws1['C6'] = '前端'
    ws1['D6'] = '前端'
    ws1['E6'] = '前端'
    
    # 数据行（从第7行开始）
    ws1['A7'] = 1001
    ws1['B7'] = 'Item 1'
    ws1['C7'] = 'Nội dung cũ 1'
    ws1['D7'] = '旧中文1'
    ws1['E7'] = 'Old content 1'
    
    ws1['A8'] = 1002
    ws1['B8'] = 'Item 2'
    ws1['C8'] = 'Nội dung cũ 2'
    ws1['D8'] = '旧中文2'
    ws1['E8'] = 'Old content 2'
    
    path1 = os.path.join(output_dir, 'test_table_1.xlsx')
    wb1.save(path1)
    print(f"创建测试表1: {path1}")
    
    # 创建 test_table_2.xlsx
    wb2 = Workbook()
    ws2 = wb2.active
    ws2.title = "test_table_2"
    
    ws2['A1'] = '表名'
    ws2['A2'] = 'test_table_2'
    ws2['A3'] = ''
    ws2['A4'] = ''
    
    # 第5行：字段名
    ws2['A5'] = 'id'
    ws2['B5'] = 'name'
    ws2['C5'] = 'VN'
    ws2['D5'] = 'Support-CH'
    ws2['E5'] = 'EN'
    
    # 第6行：字段类型
    ws2['A6'] = '前后端'
    ws2['B6'] = '前端'
    ws2['C6'] = '前端'
    ws2['D6'] = '前端'
    ws2['E6'] = '前端'
    
    # 数据行
    ws2['A7'] = 2001
    ws2['B7'] = 'Item A'
    ws2['C7'] = 'Nội dung cũ A'
    ws2['D7'] = '旧中文A'
    ws2['E7'] = 'Old content A'
    
    path2 = os.path.join(output_dir, 'test_table_2.xlsx')
    wb2.save(path2)
    print(f"创建测试表2: {path2}")
    
    return [path1, path2]


def create_test_json_config(output_path):
    """创建测试用的JSON配置文件"""
    config = {
        "no_text_tables": [],
        "text_tables": [
            {
                "table_name": "test_table_1.xlsx",
                "sheet_name": "test_table_1",
                "fields": ["id", "name", "VN", "Support-CH", "EN"],
                "fields_with_examples": [
                    "id,前后端",
                    "name,前端",
                    "VN,前端",
                    "Support-CH,前端",
                    "EN,前端"
                ]
            },
            {
                "table_name": "test_table_2.xlsx",
                "sheet_name": "test_table_2",
                "fields": ["id", "name", "VN", "Support-CH", "EN"],
                "fields_with_examples": [
                    "id,前后端",
                    "name,前端",
                    "VN,前端",
                    "Support-CH,前端",
                    "EN,前端"
                ]
            }
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"创建JSON配置: {output_path}")
    return config


def test_batch_modifier():
    """测试批量改表功能"""
    print("=" * 60)
    print("批量改表功能测试")
    print("=" * 60)
    
    # 创建临时目录
    test_dir = os.path.join(tempfile.gettempdir(), 'batch_modifier_test')
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    excel_dir = os.path.join(test_dir, 'excel_files')
    os.makedirs(excel_dir)
    
    try:
        # 创建测试文件
        print("\n1. 创建测试文件...")
        mapping_path = os.path.join(test_dir, 'mapping_table.xlsx')
        json_path = os.path.join(test_dir, 'config.json')
        report_path = os.path.join(test_dir, 'modification_report.xlsx')
        
        create_test_mapping_table(mapping_path)
        create_test_excel_files(excel_dir)
        create_test_json_config(json_path)
        
        # 导入批量改表模块
        print("\n2. 导入批量改表模块...")
        from core.batch_excel_modifier import BatchExcelModifier
        
        modifier = BatchExcelModifier()
        
        # 加载JSON配置
        print("\n3. 加载JSON配置...")
        field_config = modifier.load_json_config(json_path)
        print(f"   加载了 {len(field_config)} 个表的配置")
        
        # 执行批量修改
        print("\n4. 执行批量修改...")
        stats = modifier.process_batch_modification(
            mapping_path=mapping_path,
            excel_directory=excel_dir,
            table_col='表名',
            id_col='ID',
            modify_cols=['VN', 'Support-CH'],
            field_mapping={'VN': 'VN', 'Support-CH': 'Support-CH'},
            mapping_sheet=None,
            backup=True
        )
        
        # 显示统计信息
        print("\n5. 统计信息:")
        print(modifier.get_stats_summary())
        
        # 生成报告
        print("\n6. 生成修改报告...")
        modifier.generate_modification_report(report_path)
        print(f"   报告已保存: {report_path}")
        
        # 验证修改结果
        print("\n7. 验证修改结果...")
        df1 = pd.read_excel(os.path.join(excel_dir, 'test_table_1.xlsx'), header=None)
        print(f"   test_table_1.xlsx 第7行 VN列: {df1.iloc[6, 2]}")  # C7
        print(f"   test_table_1.xlsx 第8行 VN列: {df1.iloc[7, 2]}")  # C8
        
        df2 = pd.read_excel(os.path.join(excel_dir, 'test_table_2.xlsx'), header=None)
        print(f"   test_table_2.xlsx 第7行 VN列: {df2.iloc[6, 2]}")  # C7
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理临时文件（可选）
        # shutil.rmtree(test_dir)
        print(f"\n测试文件目录: {test_dir}")


if __name__ == '__main__':
    test_batch_modifier()
