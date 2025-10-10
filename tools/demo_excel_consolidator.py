#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据整合工具演示脚本
展示工具的基本使用方法
"""

import os
import sys
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent.parent))

from tools.excel_consolidator import ExcelConsolidator


def demo_excel_consolidator():
    """演示Excel数据整合工具的使用"""
    
    print("=" * 60)
    print("Excel数据整合工具演示")
    print("=" * 60)
    
    # 创建整合器实例
    consolidator = ExcelConsolidator()
    
    # 检查测试文件是否存在
    test_file = "test_data/test_data.xlsx"
    if not os.path.exists(test_file):
        print(f"[错误] 测试文件不存在: {test_file}")
        print("请先运行 python tools/create_test_excel.py 创建测试文件")
        return False
    
    print(f"[信息] 使用测试文件: {test_file}")
    
    # 读取文件
    print("\n[步骤] 正在读取Excel文件...")
    try:
        df = consolidator.read_excel_file(test_file)
        print(f"[成功] 成功读取文件，共 {len(df)} 行，{len(df.columns)} 列")
        print(f"[信息] 列名: {list(df.columns)}")
    except Exception as e:
        print(f"[错误] 读取文件失败: {str(e)}")
        return False
    
    # 显示数据预览
    print(f"\n[预览] 数据预览（前5行）:")
    try:
        print(df.head().to_string())
    except UnicodeEncodeError:
        print("数据包含特殊字符，跳过详细预览")
    
    # 显示分组信息
    first_col = df.columns[0]
    unique_values = df[first_col].unique()
    print(f"\n[分析] 第一列 '{first_col}' 的唯一值:")
    for i, value in enumerate(unique_values, 1):
        count = len(df[df[first_col] == value])
        print(f"  {i}. {value} ({count} 行)")
    
    # 执行数据整合
    print(f"\n[处理] 开始数据整合...")
    try:
        consolidated_data = consolidator.consolidate_by_column_a(df)
        print(f"[成功] 数据整合完成，共 {len(consolidated_data)} 个分组")
        
        # 显示整合报告
        print(f"\n[报告] 整合报告:")
        print(consolidator.get_consolidation_report())
        
    except Exception as e:
        print(f"[错误] 数据整合失败: {str(e)}")
        return False
    
    # 创建输出文件
    output_folder = "test_data"
    print(f"\n[保存] 正在创建输出文件到文件夹: {output_folder}")
    print(f"[信息] 将为每个A列内容创建单独的Excel文件")
    try:
        success = consolidator.process_file(
            input_path=test_file,
            output_folder=output_folder,
            output_filename=None,  # 使用自动生成
            include_summary=True,
            auto_filename_from_column=True,
            skip_duplicates=True,
            separate_files=True  # 创建多个单独文件
        )
        if success:
            # 显示所有生成的文件
            first_col = df.columns[0]
            unique_values = df[first_col].unique()
            print(f"[成功] 输出文件创建成功！")
            print(f"[信息] 共创建 {len(unique_values)} 个文件:")
            for i, value in enumerate(unique_values, 1):
                filename = str(value) + ".xlsx"
                file_path = os.path.join(output_folder, filename)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  {i}. {filename} ({file_size:,} 字节)")
                else:
                    print(f"  {i}. {filename} (已跳过)")
        else:
            print(f"[错误] 输出文件创建失败")
            return False
            
    except Exception as e:
        print(f"[错误] 创建输出文件失败: {str(e)}")
        return False
    
    print(f"\n[完成] 演示完成！")
    print(f"[文件] 输入文件: {test_file}")
    print(f"[文件] 输出文件夹: {output_folder}")
    print(f"[文件] 输出模式: 多个单独文件（每个A列内容一个文件）")
    print(f"\n[提示] 您可以使用Excel打开输出文件查看整合结果")
    
    return True


def main():
    """主函数"""
    try:
        success = demo_excel_consolidator()
        if success:
            print(f"\n[成功] 演示成功完成")
            return 0
        else:
            print(f"\n[失败] 演示失败")
            return 1
    except KeyboardInterrupt:
        print(f"\n\n[中断] 用户中断演示")
        return 1
    except Exception as e:
        print(f"\n[错误] 演示过程中发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
