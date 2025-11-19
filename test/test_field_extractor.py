#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试表字段导出工具
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor


def test_field_extraction():
    """测试字段提取功能"""
    print("=" * 60)
    print("测试表字段导出工具")
    print("=" * 60)
    
    # 创建提取器实例
    extractor = ExcelFieldExtractor()
    
    # 测试目录
    test_dir = Path(__file__).parent.parent / "test_excel_files"
    
    if not test_dir.exists():
        print(f"测试目录不存在: {test_dir}")
        print("请创建测试目录并添加一些Excel文件进行测试")
        return
    
    # 创建输出目录
    output_dir = Path(__file__).parent.parent / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n扫描目录: {test_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 测试CSV输出
    print("\n--- 测试CSV格式输出 ---")
    try:
        stats = extractor.process_directory(
            directory_path=str(test_dir),
            output_folder=str(output_dir),
            output_format='csv',
            recursive=True
        )
        
        print(f"\n处理统计:")
        print(f"  扫描文件数: {stats['total_files']}")
        print(f"  工作表数: {stats['total_sheets']}")
        print(f"  提取字段数: {stats['total_fields']}")
        print(f"  输出文件: {stats['output_file']}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试Excel输出
    print("\n--- 测试Excel格式输出 ---")
    try:
        stats = extractor.process_directory(
            directory_path=str(test_dir),
            output_folder=str(output_dir),
            output_format='excel',
            recursive=True
        )
        
        print(f"\n处理统计:")
        print(f"  扫描文件数: {stats['total_files']}")
        print(f"  工作表数: {stats['total_sheets']}")
        print(f"  提取字段数: {stats['total_fields']}")
        print(f"  输出文件: {stats['output_file']}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_field_extraction()
