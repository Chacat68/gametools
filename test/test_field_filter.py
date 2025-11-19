#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段过滤功能
验证只提取包含中文、越南文、泰文的字段
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.excel_field_extractor import ExcelFieldExtractor


def test_contains_text():
    """测试文本检测逻辑"""
    extractor = ExcelFieldExtractor()
    
    # 测试用例：[值, 期望结果, 说明]
    test_cases = [
        # 应该被提取的（包含中文、越南文、泰文）
        ("角色名称", True, "纯中文"),
        ("玩家ID", True, "中英混合"),
        ("等级123", True, "中文+数字"),
        ("Tên nhân vật", True, "越南文"),
        ("Cấp độ", True, "越南文"),
        ("ชื่อตัวละคร", True, "泰文"),
        ("角色名称_v2", True, "中文+英文+数字"),
        ("Điểm HP", True, "越南文+英文"),
        ("ระดับ123", True, "泰文+数字"),
        
        # 应该被忽略的（纯数字、英文、代码）
        ("12345", False, "纯数字"),
        ("123.456", False, "小数"),
        ("-999", False, "负数"),
        ("1.23e5", False, "科学计数法"),
        ("PlayerID", False, "纯英文"),
        ("player_id", False, "英文下划线"),
        ("CONFIG_NAME", False, "英文大写配置"),
        ("true", False, "布尔值"),
        ("false", False, "布尔值"),
        ("null", False, "空值标识"),
        ("ID_001", False, "代码标识"),
        ("", False, "空字符串"),
        (None, False, "None值"),
        ("HP_MAX", False, "纯英文常量"),
        ("position_x", False, "英文变量名"),
    ]
    
    print("=" * 60)
    print("测试字段过滤逻辑")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for value, expected, description in test_cases:
        result = extractor.contains_text(value)
        status = "✓" if result == expected else "✗"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {description:20s} | 值: {str(value):20s} | 期望: {expected:5} | 实际: {result:5}")
    
    print("=" * 60)
    print(f"测试完成: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = test_contains_text()
    sys.exit(0 if success else 1)
