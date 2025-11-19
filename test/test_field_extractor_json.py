#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表字段导出工具 - JSON格式
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor


def main():
    """测试表字段导出工具"""
    print("=" * 60)
    print("测试表字段导出工具 - JSON格式")
    print("=" * 60)
    
    # 设置测试路径
    test_dir = Path(__file__).parent.parent / "test_excel_files"
    output_dir = Path(__file__).parent.parent / "test_output"
    
    print(f"\n扫描目录: {test_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 创建提取器
    extractor = ExcelFieldExtractor()
    
    # 测试JSON格式（新的默认格式）
    print("\n--- 测试JSON格式输出 ---")
    stats = extractor.process_directory(
        directory_path=str(test_dir),
        output_folder=str(output_dir),
        output_format='json',
        recursive=True
    )
    
    print("\n处理统计:")
    print(f"  扫描文件数: {stats['total_files']}")
    print(f"  工作表数: {stats['total_sheets']}")
    print(f"  提取字段数: {stats['total_fields']}")
    print(f"  输出文件: {stats['output_file']}")
    
    # 读取并显示JSON内容
    if stats['results']:
        print("\nJSON结果示例（前3条）:")
        print("-" * 60)
        for i, result in enumerate(stats['results'][:3], 1):
            print(f"{i}. 表名: {result['excel_file']}")
            print(f"   工作表: {result['sheet_name']}")
            print(f"   字段数: {result['field_count']}")
            print(f"   字段: {', '.join(result['fields'])}")
            print()
        
        # 验证JSON文件
        json_file = Path(stats['output_file'])
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"JSON文件验证成功，共 {len(json_data)} 条记录")
            print("\nJSON格式示例:")
            print(json.dumps(json_data[0] if json_data else {}, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
