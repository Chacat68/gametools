#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨项目翻译纯逻辑测试，不依赖 pandas。"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cross_project_translator import CrossProjectTranslator


def test_parse_cell_reference():
    translator = CrossProjectTranslator()

    assert translator.parse_cell_reference("A1") == (1, 1)
    assert translator.parse_cell_reference("AA10") == (10, 27)
    assert translator.parse_cell_reference("c7") == (7, 3)
    assert translator.parse_cell_reference("") == (None, None)
    assert translator.parse_cell_reference("1A") == (None, None)
    return True


def test_find_project_file():
    translator = CrossProjectTranslator()

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        direct_file = root / "dialog.xlsx"
        nested_dir = root / "sub"
        nested_dir.mkdir()
        fuzzy_file = nested_dir / "quest_config.xls"

        direct_file.touch()
        fuzzy_file.touch()

        assert translator.find_project_file(str(root), "dialog") == str(direct_file)
        assert translator.find_project_file(str(root), "quest") == str(fuzzy_file)
        assert translator.find_project_file(str(root), "missing") is None

        # 重复查询应命中运行期缓存，结果保持一致
        assert translator.find_project_file(str(root), "dialog") == str(direct_file)
        assert translator.find_project_file(str(root), "quest") == str(fuzzy_file)

        # 清理运行态缓存后，新加入的文件应可被重新索引并找到
        late_file = nested_dir / "newquest_dialog.xlsx"
        late_file.touch()
        translator.clear_runtime_cache()
        assert translator.find_project_file(str(root), "newquest_dialog") == str(late_file)

    return True


def test_process_translation_mapping_input_validation():
    translator = CrossProjectTranslator()

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        mapping_file = root / "mapping.xlsx"
        mapping_file.touch()

        assert translator.process_translation_mapping(str(root / "missing.xlsx"), str(root)) == []
        assert translator.process_translation_mapping(str(mapping_file), str(root / "missing_project")) == []

    return True


def main():
    tests = [
        ("解析单元格引用", test_parse_cell_reference),
        ("查找项目文件", test_find_project_file),
        ("映射输入校验", test_process_translation_mapping_input_validation),
    ]

    all_passed = True
    print("=" * 60)
    print("跨项目翻译纯逻辑测试")
    print("=" * 60)

    for name, test_func in tests:
        try:
            passed = test_func()
        except Exception as exc:
            passed = False
            print(f"❌ {name}: {exc}")
        else:
            print(f"✅ {name}" if passed else f"❌ {name}")

        all_passed = all_passed and passed

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())