#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试缓存版跨项目翻译对应工具的结果隔离。"""

import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cross_project_translator_cached import CrossProjectTranslatorWithCache


def test_cross_project_translation_with_cache():
    """同名工作表同坐标在不同文件中不应发生缓存串值。"""
    print("测试缓存版跨项目翻译对应功能")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_directory = temp_path / "project"
        project_directory.mkdir(parents=True, exist_ok=True)
        mapping_file = temp_path / "mapping.xlsx"

        translator = CrossProjectTranslatorWithCache(
            cache_dir=str(temp_path / ".cache"),
            enable_file_cache=False,
            memory_cache_size=32,
        )

        pd.DataFrame(
            [
                ["id", "name", "text"],
                [1, "角色1", "金庸"],
            ]
        ).to_excel(project_directory / "a.xlsx", index=False, header=False, sheet_name="Sheet1")

        pd.DataFrame(
            [
                ["id", "name", "text"],
                [1, "角色2", "三国"],
            ]
        ).to_excel(project_directory / "b.xlsx", index=False, header=False, sheet_name="Sheet1")

        pd.DataFrame(
            [
                {"Name": "a.xlsx", "Description": "Sheet1!C2"},
                {"Name": "b.xlsx", "Description": "Sheet1!C2"},
            ]
        ).to_excel(mapping_file, index=False)

        results = translator.process_translation_mapping(str(mapping_file), str(project_directory))
        actual_contents = [result['content'] for result in results]

        print(f"结果: {actual_contents}")
        expected_contents = ["金庸", "三国"]

        if actual_contents != expected_contents:
            print(f"❌ 结果不匹配: {actual_contents}")
            return False

        print("✅ 缓存未发生跨文件串值")
        return True


if __name__ == "__main__":
    sys.exit(0 if test_cross_project_translation_with_cache() else 1)