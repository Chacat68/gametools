#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的JSON格式输出
验证字段名+字段类型的提取
"""

import sys
from pathlib import Path

# 添加项目根目录到路径（确保可导入 core 包）
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor

def test_json_format():
    """测试JSON格式输出"""
    print("=" * 60)
    print("测试表字段导出工具 - 新JSON格式")
    print("=" * 60)
    
    # 创建提取器实例
    extractor = ExcelFieldExtractor()
    
    # 测试目录（假设有测试文件）
    test_dir = Path("test_excel_files")
    
    if not test_dir.exists():
        print(f"⚠️ 测试目录不存在: {test_dir}")
        print("请先创建测试Excel文件")
        return
    
    # 处理目录并导出JSON
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 扫描目录: {test_dir}")
    print(f"📤 输出目录: {output_dir}")
    print(f"📋 输出格式: JSON\n")
    
    stats = extractor.process_directory(
        directory_path=str(test_dir),
        output_folder=str(output_dir),
        output_format='json',
        recursive=True
    )
    
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"✅ 扫描文件数: {stats['total_files']}")
    print(f"✅ 工作表数: {stats['total_sheets']}")
    print(f"✅ 字段总数: {stats['total_fields']}")
    print(f"✅ 输出文件: {stats['output_file']}")
    
    # 显示日志
    logs = extractor.get_all_logs()
    if logs['warnings']:
        print(f"\n⚠️ 警告数: {len(logs['warnings'])}")
    if logs['errors']:
        print(f"\n❌ 错误数: {len(logs['errors'])}")
    
    # 读取并显示JSON输出
    import json
    output_file = Path(stats['output_file'])
    if output_file.exists():
        print("\n" + "=" * 60)
        print("JSON输出预览")
        print("=" * 60)
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📊 无文本表格数: {len(data['no_text_tables'])}")
        if data['no_text_tables']:
            print("前3个示例:")
            for item in data['no_text_tables'][:3]:
                print(f"  - {item['table_name']} # {item['sheet_name']}")
        
        print(f"\n📊 包含文本表格数: {len(data['text_tables'])}")
        if data['text_tables']:
            print("前3个示例:")
            for item in data['text_tables'][:3]:
                print(f"  - {item['table_name']} # {item['sheet_name']}")
                print(f"    字段数: {item['field_count']}")
                if item['fields_with_examples']:
                    print(f"    字段+类型: {item['fields_with_examples'][:2]}")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    test_json_format()
