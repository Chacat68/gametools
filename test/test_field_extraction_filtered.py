#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的字段提取功能（带过滤）
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.excel_field_extractor import ExcelFieldExtractor


def test_extraction_with_filter():
    """测试带过滤的字段提取"""
    
    # 测试文件路径
    test_file = Path(__file__).parent / "test_excel_files" / "field_filter_test.xlsx"
    
    if not test_file.exists():
        print(f"错误: 测试文件不存在 {test_file}")
        print("请先运行 create_field_filter_test_excel.py 创建测试文件")
        return False
    
    print("=" * 60)
    print("测试字段提取（带过滤）")
    print("=" * 60)
    print(f"测试文件: {test_file}\n")
    
    # 创建提取器
    extractor = ExcelFieldExtractor()
    
    # 提取字段
    results = extractor.extract_fields_from_excel(test_file)
    
    # 显示结果
    print(f"找到 {len(results)} 个包含本地化文本的工作表\n")
    
    for idx, result in enumerate(results, 1):
        print(f"工作表 {idx}: {result['sheet_name']}")
        print(f"  文件: {result['excel_file']}")
        print(f"  字段数量: {result['field_count']}")
        print(f"  字段列表: {', '.join(result['fields'])}")
        print(f"  文本列号: {result['text_columns']}")
        print()
    
    # 验证结果
    print("=" * 60)
    print("验证结果:")
    print("=" * 60)
    
    expected = {
        "角色数据": ["角色名称", "Tên nhân vật", "等级", "ชื่อ"],
        "道具数据": ["道具名称", "Tên vật phẩm", "描述"]
    }
    
    passed = 0
    failed = 0
    
    # 检查是否提取了正确的工作表
    extracted_sheets = {r['sheet_name']: r['fields'] for r in results}
    
    for sheet_name, expected_fields in expected.items():
        if sheet_name in extracted_sheets:
            actual_fields = extracted_sheets[sheet_name]
            if actual_fields == expected_fields:
                print(f"✓ {sheet_name}: 字段匹配")
                passed += 1
            else:
                print(f"✗ {sheet_name}: 字段不匹配")
                print(f"  期望: {expected_fields}")
                print(f"  实际: {actual_fields}")
                failed += 1
        else:
            print(f"✗ {sheet_name}: 未提取到此工作表")
            failed += 1
    
    # 检查是否忽略了SystemConfig工作表
    if "SystemConfig" not in extracted_sheets:
        print(f"✓ SystemConfig: 正确忽略（纯英文配置）")
        passed += 1
    else:
        print(f"✗ SystemConfig: 不应该被提取")
        failed += 1
    
    print("=" * 60)
    print(f"验证完成: 通过 {passed}, 失败 {failed}")
    print("=" * 60)
    
    # 测试JSON导出
    output_dir = Path(__file__).parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "field_filter_result.json"
    
    extractor.export_to_json(results, output_file)
    
    # 读取并显示JSON内容
    print("\n导出的JSON内容:")
    print("=" * 60)
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    return failed == 0


if __name__ == "__main__":
    success = test_extraction_with_filter()
    sys.exit(0 if success else 1)
