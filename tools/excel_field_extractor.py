#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel表字段导出工具 - 命令行版本
扫描指定目录下的所有Excel文件，提取包含文本的列的字段信息
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Excel表字段导出工具 - 扫描Excel文件并提取包含文本的列的字段信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python excel_field_extractor.py -d ./excel_files
  python excel_field_extractor.py -d ./excel_files -o ./output -f excel
  python excel_field_extractor.py -d ./excel_files --no-recursive
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        required=True,
        help='要扫描的目录路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出目录（默认为扫描目录）'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['json', 'csv', 'excel'],
        default='json',
        help='输出格式: json, csv 或 excel（默认为json）'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='不递归扫描子目录'
    )
    
    args = parser.parse_args()
    
    # 创建提取器实例
    extractor = ExcelFieldExtractor()
    
    # 处理目录
    print("=" * 60)
    print("Excel表字段导出工具")
    print("=" * 60)
    
    try:
        stats = extractor.process_directory(
            directory_path=args.directory,
            output_folder=args.output,
            output_format=args.format,
            recursive=not args.no_recursive
        )
        
        print("\n" + "=" * 60)
        print("处理完成!")
        print("=" * 60)
        print(f"扫描文件数: {stats['total_files']}")
        print(f"工作表数: {stats['total_sheets']}")
        print(f"提取字段数: {stats['total_fields']}")
        print(f"输出文件: {stats['output_file']}")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
