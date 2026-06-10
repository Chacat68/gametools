#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JSON 错误检测器单元测试。"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.json_error_detector.json_error_detector import JSONErrorDetector


def _write_temp_json(content: str) -> Path:
    handle = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
    handle.write(content)
    handle.close()
    return Path(handle.name)


def test_valid_json_has_no_errors():
    detector = JSONErrorDetector()
    sample_dir = Path(__file__).parent.parent / 'tools' / 'json_error_detector'
    result = detector.detect_file(sample_dir / 'valid_example.json')
    assert result['error_count'] == 0
    assert result['warning_count'] == 0


def test_syntax_errors_are_detected():
    detector = JSONErrorDetector()
    sample_dir = Path(__file__).parent.parent / 'tools' / 'json_error_detector'
    result = detector.detect_file(sample_dir / 'syntax_error_example.json')
    types = {item['type'] for item in result['errors']}
    assert '单引号错误' in types or 'JSON解析错误' in types
    assert result['error_count'] > 0


def test_url_with_double_slash_is_not_false_positive():
    detector = JSONErrorDetector()
    path = _write_temp_json('{"url": "http://example.com/path"}')
    try:
        result = detector.detect_file(path)
        assert result['error_count'] == 0, result
    finally:
        path.unlink()


def test_apostrophe_inside_string_is_not_false_positive():
    detector = JSONErrorDetector()
    path = _write_temp_json('{"text": "it\'s fine"}')
    try:
        result = detector.detect_file(path)
        assert result['error_count'] == 0, result
    finally:
        path.unlink()


def test_trailing_comma_is_detected():
    detector = JSONErrorDetector()
    path = _write_temp_json('{"items": [1, 2, 3,]}')
    try:
        result = detector.detect_file(path)
        assert result['error_count'] > 0
        assert any(item['type'] in ('尾随逗号', 'JSON解析错误') for item in result['errors'])
    finally:
        path.unlink()


def test_folder_detection_returns_structured_summary():
    detector = JSONErrorDetector()
    sample_dir = Path(__file__).parent.parent / 'tools' / 'json_error_detector'
    result = detector.detect_folder(sample_dir)
    assert result['total_files'] >= 3
    assert result['processed_files'] == result['total_files']
    assert isinstance(result['files'], list)


if __name__ == '__main__':
    tests = [
        test_valid_json_has_no_errors,
        test_syntax_errors_are_detected,
        test_url_with_double_slash_is_not_false_positive,
        test_apostrophe_inside_string_is_not_false_positive,
        test_trailing_comma_is_detected,
        test_folder_detection_returns_structured_summary,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f'OK {test.__name__}')
        except Exception as exc:
            failed += 1
            print(f'FAIL {test.__name__}: {exc}')
    sys.exit(1 if failed else 0)
