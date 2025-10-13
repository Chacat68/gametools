#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重新设计的跨项目翻译对应功能
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.cross_project_translator import CrossProjectTranslator


def test_cross_project_translation():
    """测试跨项目翻译对应功能"""
    print("测试跨项目翻译对应功能")
    print("=" * 60)
    
    # 创建翻译对应工具实例
    translator = CrossProjectTranslator()
    
    # 测试文件路径
    mapping_file = "test_excel_files/mixed_test.xlsx"
    project_directory = "test_excel_files/新建文件夹"
    
    print(f"映射文件: {mapping_file}")
    print(f"项目目录: {project_directory}")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(mapping_file):
        print(f"错误: 映射文件不存在 - {mapping_file}")
        return
    
    if not os.path.exists(project_directory):
        print(f"错误: 项目目录不存在 - {project_directory}")
        return
    
    # 处理翻译映射
    results = translator.process_translation_mapping(mapping_file, project_directory)
    
    if results:
        # 显示处理报告
        print("处理报告:")
        print(translator.get_processing_report())
        print()
        
        # 显示详细结果
        print("详细结果:")
        print("-" * 60)
        for result in results:
            status_icon = "[OK]" if result['status'] == 'success' else "[ERR]"
            print(f"{status_icon} 第{result['index']}行: {result['file_name']} ({result['cell_reference']}) -> {result['content']}")
            if result['status'] == 'error':
                print(f"    错误: {result['error_message']}")
        print()
        
        # 导出结果
        output_file = "test_cross_project_results.xlsx"
        if translator.export_results(output_file):
            print(f"结果已导出到: {output_file}")
        else:
            print("导出失败")
        
        # 显示预期结果
        print("\n预期结果:")
        print("根据mixed_test.xlsx的内容，应该返回:")
        print("- 金庸 (vietnamese_test.xlsx的C2位置)")
        print("- 你好 (vietnamese_test.xlsx的C4位置)")  
        print("- 电视 (vietnamese_test1.xlsx的C3位置)")
        print("- 三国 (vietnamese_test1.xlsx的C1位置)")
        
    else:
        print("处理失败，没有生成结果")


if __name__ == "__main__":
    test_cross_project_translation()
