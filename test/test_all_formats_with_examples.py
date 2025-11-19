#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段+示例的所有输出格式
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.excel_field_extractor import ExcelFieldExtractor


def test_all_formats():
    """测试所有输出格式"""
    
    # 测试文件路径
    test_file = Path(__file__).parent / "test_excel_files" / "field_filter_test.xlsx"
    
    if not test_file.exists():
        print(f"错误: 测试文件不存在 {test_file}")
        return False
    
    print("=" * 60)
    print("测试所有输出格式（带示例数据）")
    print("=" * 60)
    print(f"测试文件: {test_file}\n")
    
    # 创建提取器
    extractor = ExcelFieldExtractor()
    
    # 提取字段
    results = extractor.extract_fields_from_excel(test_file)
    
    # 输出目录
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    # 测试JSON格式
    print("\n1. JSON格式输出:")
    print("-" * 60)
    json_file = output_dir / "fields_with_examples.json"
    extractor.export_to_json(results, json_file)
    with open(json_file, 'r', encoding='utf-8') as f:
        print(f.read())
    
    # 测试CSV格式
    print("\n2. CSV格式输出:")
    print("-" * 60)
    csv_file = output_dir / "fields_with_examples.csv"
    extractor.export_to_csv(results, csv_file)
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        print(f.read())
    
    # 测试Excel格式
    print("\n3. Excel格式输出:")
    print("-" * 60)
    excel_file = output_dir / "fields_with_examples.xlsx"
    extractor.export_to_excel(results, excel_file)
    print(f"Excel文件已创建: {excel_file}")
    
    # 显示结果详情
    print("\n4. 详细结果:")
    print("-" * 60)
    for result in results:
        print(f"\n工作表: {result['sheet_name']}")
        print(f"字段列表:")
        for field in result['fields']:
            print(f"  - {field}")
        print(f"\n字段+示例:")
        for field_example in result.get('fields_with_examples', []):
            print(f"  - {field_example}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_all_formats()
    sys.exit(0 if success else 1)
