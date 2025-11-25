#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel分页拆分工具 - 命令行快速入口
根据第一列的文件名，将同一文件名的行数据拆分到新表格的对应分页中
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.excel_sheet_splitter import ExcelSheetSplitter


def main():
    """命令行快速入口"""
    print("=" * 60)
    print("Excel分页拆分工具")
    print("根据第一列的文件名，将数据拆分到新表格的对应分页")
    print("=" * 60)
    print()
    
    # 获取输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("请输入Excel文件路径: ").strip().strip('"')
    
    if not input_file or not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        return 1
    
    # 生成输出文件路径
    input_path = Path(input_file)
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = str(input_path.parent / f"{input_path.stem}_分页拆分.xlsx")
        print(f"输出文件: {output_file}")
    
    # 创建处理器并执行
    splitter = ExcelSheetSplitter()
    
    print()
    print("正在处理...")
    
    success, report = splitter.process_file(
        input_path=input_file,
        output_path=output_file,
        extract_filename=True,
        include_summary=True
    )
    
    print()
    print(report)
    
    if success:
        print(f"\n✓ 文件已成功保存到: {output_file}")
        return 0
    else:
        print(f"\n✗ 处理失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
