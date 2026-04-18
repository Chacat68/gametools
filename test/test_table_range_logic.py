#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多语言提取器纯逻辑测试，不依赖 pandas/openpyxl。"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import core.table_range_translator as table_range_module
from core.table_range_translator import TableRangeTranslator, TableRangeTranslatorError


def test_field_and_language_helpers():
    translator = TableRangeTranslator()

    assert translator.parse_field_with_type("desc,前端,C") == ("desc", "前端", "C")
    assert translator.parse_field_with_type("desc,后端") == ("desc", "后端", None)

    config = {"language": {"code": "vn", "name": "越南语"}}
    assert translator.get_json_language(config) == "vn"
    assert translator.match_directory_by_language(config, {"vn": "demo/vn"}) == "demo/vn"
    assert translator.match_directory_by_language(config, {"zh": "demo/zh"}) is None
    return True


def test_json_loading_and_output_name():
    translator = TableRangeTranslator()

    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        json_path = base / "merged.json"
        payload = {
            "ZH": {
                "language": {"code": "zh", "name": "中文"},
                "text_tables": [],
                "no_text_tables": []
            },
            "VN": {
                "language": {"code": "vn", "name": "越南语"},
                "text_tables": [],
                "no_text_tables": []
            }
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        zh_config = translator.load_json_config(str(json_path), target_language="zh")
        merged_config = translator.load_merged_json_config(str(json_path))
        output_path = translator.generate_output_filename(str(base))

        assert zh_config.get("language", {}).get("code") == "zh"
        assert set(merged_config.keys()) == {"ZH", "VN"}
        assert Path(output_path).parent == base
        assert Path(output_path).name.startswith("翻译提取_")
        assert Path(output_path).suffix == ".csv"
    return True


def test_dependency_degradation_for_processing():
    translator = TableRangeTranslator()
    original_pd = table_range_module.pd

    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        json_path = base / "merged.json"
        payload = {
            "ZH": {
                "language": {"code": "zh", "name": "中文"},
                "text_tables": [],
                "no_text_tables": []
            }
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        table_range_module.pd = None
        try:
            try:
                translator.process_with_merged_json(str(json_path), {"zh": str(base)})
            except TableRangeTranslatorError as exc:
                assert "pandas" in str(exc)
                assert translator.error_logs, "缺少依赖时应记录错误日志"
                return True
        finally:
            table_range_module.pd = original_pd

    return False


def main():
    tests = [
        ("字段与语言辅助函数", test_field_and_language_helpers),
        ("JSON加载与输出命名", test_json_loading_and_output_name),
        ("依赖降级", test_dependency_degradation_for_processing),
    ]

    all_passed = True
    print("=" * 60)
    print("多语言提取纯逻辑测试")
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