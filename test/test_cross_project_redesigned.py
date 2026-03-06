#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试重新设计的跨项目翻译对应功能
"""

import sys
import tempfile
from pathlib import Path

import pandas as pd

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.cross_project_translator import CrossProjectTranslator


def test_cross_project_translation():
    """测试跨项目翻译对应功能"""
    print("测试跨项目翻译对应功能")
    print("=" * 60)
    
    # 创建翻译对应工具实例
    translator = CrossProjectTranslator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_directory = temp_path / "project"
        project_directory.mkdir(parents=True, exist_ok=True)
        mapping_file = temp_path / "mixed_test.xlsx"
        output_file = temp_path / "test_cross_project_results.xlsx"

        print(f"映射文件: {mapping_file}")
        print(f"项目目录: {project_directory}")
        print()

        file1 = project_directory / "vietnamese_test.xlsx"
        file2 = project_directory / "vietnamese_test1.xlsx"

        pd.DataFrame(
            [
                ["id", "name", "text"],
                [1, "角色1", "金庸"],
                [2, "角色2", "占位"],
                [3, "角色3", "你好"],
            ]
        ).to_excel(file1, index=False, header=False, sheet_name="Sheet1")

        pd.DataFrame(
            [
                ["id", "name", "text"],
                [1, "场景1", "三国"],
                [2, "场景2", "占位"],
                [3, "场景3", "电视"],
            ]
        ).to_excel(file2, index=False, header=False, sheet_name="Sheet1")

        pd.DataFrame(
            [
                {"Name": "vietnamese_test.xlsx", "Description": "Sheet1!C2"},
                {"Name": "vietnamese_test.xlsx", "Description": "Sheet1!C4"},
                {"Name": "vietnamese_test1.xlsx", "Description": "Sheet1!C4"},
                {"Name": "vietnamese_test1.xlsx", "Description": "Sheet1!C2"},
            ]
        ).to_excel(mapping_file, index=False)

        # 处理翻译映射
        results = translator.process_translation_mapping(str(mapping_file), str(project_directory))
    
        if results:
            expected_contents = ["金庸", "你好", "电视", "三国"]
            actual_contents = [result['content'] for result in results]

            if actual_contents != expected_contents:
                print(f"❌ 对应内容不匹配: {actual_contents}")
                return False

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
            if translator.export_results(str(output_file)) and output_file.exists():
                print(f"结果已导出到: {output_file}")
            else:
                print("导出失败")
                return False
        
        # 显示预期结果
            print("\n预期结果:")
            print("根据mixed_test.xlsx的内容，应该返回:")
            print("- 金庸 (vietnamese_test.xlsx的C2位置)")
            print("- 你好 (vietnamese_test.xlsx的C4位置)")
            print("- 电视 (vietnamese_test1.xlsx的C4位置)")
            print("- 三国 (vietnamese_test1.xlsx的C2位置)")
        
            return True

        print("处理失败，没有生成结果")
        return False


if __name__ == "__main__":
    success = test_cross_project_translation()
    sys.exit(0 if success else 1)
