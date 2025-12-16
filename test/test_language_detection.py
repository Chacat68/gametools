#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试映射表语言自动检测功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.batch_excel_modifier import BatchExcelModifier

def test_detect_language():
    """测试从映射表列名检测语言"""
    print("=" * 60)
    print("测试映射表语言自动检测")
    print("=" * 60)
    
    modifier = BatchExcelModifier()
    
    # 测试用例
    test_cases = [
        {
            'name': '越南语映射表（VN列）',
            'columns': ['表名', 'Classification', 'ID', 'VN'],
            'expected': 'vn'
        },
        {
            'name': '泰语映射表（TH列）',
            'columns': ['表名', 'Classification', 'ID', 'TH'],
            'expected': 'th'
        },
        {
            'name': '中文映射表（CH列）',
            'columns': ['表名', 'Classification', 'ID', 'CH'],
            'expected': 'zh'
        },
        {
            'name': '中文映射表（Support-CH列）',
            'columns': ['表名', 'Classification', 'ID', 'Support-CH'],
            'expected': 'zh'
        },
        {
            'name': '越南语映射表（Vietnamese列）',
            'columns': ['表名', 'Classification', 'ID', 'Vietnamese'],
            'expected': 'vn'
        },
        {
            'name': '中文列名（越南语）',
            'columns': ['表名', 'Classification', 'ID', '越南语'],
            'expected': 'vn'
        },
        {
            'name': '中文列名（泰语）',
            'columns': ['表名', 'Classification', 'ID', '泰语'],
            'expected': 'th'
        },
        {
            'name': '混合列名',
            'columns': ['表名', 'Classification', 'ID', 'VN', 'TH', 'CH'],
            'expected': 'vn'  # 优先检测VN
        },
        {
            'name': '无语言列',
            'columns': ['表名', 'Classification', 'ID', 'Value'],
            'expected': None
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['name']}")
        print(f"  列名: {test['columns']}")
        
        detected = modifier.detect_language_from_mapping_columns(test['columns'])
        expected = test['expected']
        
        if detected == expected:
            print(f"  ✅ 通过 - 检测结果: {detected}")
            passed += 1
        else:
            print(f"  ❌ 失败 - 期望: {expected}, 实际: {detected}")
            failed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ {failed} 个测试失败")
        return 1

def main():
    return test_detect_language()

if __name__ == "__main__":
    sys.exit(main())
