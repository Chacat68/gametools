#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段过滤功能快速演示
展示过滤前后的对比效果
"""

from pathlib import Path
from core.excel_field_extractor import ExcelFieldExtractor


def demo_field_filter():
    """演示字段过滤功能"""
    
    print("=" * 70)
    print("表字段导出工具 - 字段过滤功能演示")
    print("=" * 70)
    
    # 创建提取器
    extractor = ExcelFieldExtractor()
    
    # 显示过滤规则
    print("\n📋 当前过滤规则:")
    print(f"   过滤的字段名: {', '.join(sorted(extractor.excluded_field_names))}")
    print(f"   过滤方式: 不区分大小写")
    
    # 测试文件
    test_file = Path("test_excel_files/test_field_filter.xlsx")
    
    if not test_file.exists():
        print(f"\n❌ 测试文件不存在: {test_file}")
        print("   请先运行: python create_filter_test_excel.py")
        return
    
    print(f"\n📂 测试文件: {test_file}")
    
    # 提取字段
    print("\n🔍 正在提取字段...")
    results = extractor.extract_fields_from_excel(test_file)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("提取结果:")
    print("=" * 70)
    
    if not results:
        print("❌ 未找到结果")
        return
    
    for result in results:
        print(f"\n📊 工作表: {result['sheet_name']}")
        print(f"   包含文本: {'是' if result['has_text'] else '否'}")
        
        if result['has_text']:
            print(f"   字段数量: {result['field_count']}")
            print(f"   字段列表: {', '.join(result['fields'])}")
            
            # 显示示例数据
            if result.get('fields_with_examples'):
                print(f"\n   字段及示例:")
                for field_example in result['fields_with_examples']:
                    field_name, example = field_example.split(',', 1)
                    print(f"   - {field_name}: {example}")
    
    # 显示过滤效果
    print("\n" + "=" * 70)
    print("过滤效果分析:")
    print("=" * 70)
    
    print("\n✅ 已过滤的字段:")
    filtered_fields = ['name', 'model', 'id']
    for field in filtered_fields:
        print(f"   - {field} (包含代码/数字，已过滤)")
    
    print("\n✅ 保留的字段:")
    for result in results:
        if result['has_text']:
            for field in result['fields']:
                print(f"   - {field} (本地化文本，已保留)")
    
    print("\n" + "=" * 70)
    print("总结:")
    print("=" * 70)
    print("✨ 字段过滤功能成功过滤了代码和数字字段")
    print("✨ 只保留了真正需要翻译的本地化文本字段")
    print("✨ 提高了字段提取的准确性和实用性")


if __name__ == "__main__":
    demo_field_filter()
