#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON错误检测工具
用于检测JSON文件中的语法错误、结构错误、编码错误等
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class JSONErrorDetector:
    """JSON错误检测器"""

    _ENCODINGS = ('utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1')
    _TRAILING_COMMA_RE = re.compile(r',\s*([}\]])')
    _SINGLE_QUOTE_STRING_RE = re.compile(r"'([^'\\]|\\.)*'")
    _LINE_COMMENT_RE = re.compile(r'//')

    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []

    def _make_issue(
        self,
        issue_type: str,
        message: str,
        line: Any = '未知',
        column: Any = '未知',
        severity: str = 'error',
    ) -> Dict[str, Any]:
        return {
            'type': issue_type,
            'message': message,
            'line': line,
            'column': column,
            'severity': severity,
        }

    def _position_at(self, content: str, index: int) -> Tuple[int, int]:
        line = content.count('\n', 0, index) + 1
        last_newline = content.rfind('\n', 0, index)
        column = index - last_newline if last_newline >= 0 else index + 1
        return line, column

    def _outside_string_spans(self, content: str) -> List[Tuple[int, int]]:
        """返回不在 JSON 双引号字符串内的文本区间。"""
        spans: List[Tuple[int, int]] = []
        index = 0
        length = len(content)
        segment_start = 0
        in_string = False
        escaped = False

        while index < length:
            char = content[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == '"':
                    in_string = False
            elif char == '"':
                if segment_start < index:
                    spans.append((segment_start, index))
                in_string = True
                segment_start = index + 1
            index += 1

        if not in_string and segment_start < length:
            spans.append((segment_start, length))
        return spans

    def _read_file(self, file_path: str) -> Tuple[Optional[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """读取文件并返回内容、错误和编码警告。"""
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        path = Path(file_path)

        for encoding in self._ENCODINGS:
            try:
                content = path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except OSError as exc:
                errors.append(self._make_issue('文件读取错误', str(exc)))
                return None, errors, warnings

            if encoding not in ('utf-8', 'utf-8-sig') and any(ord(char) > 127 for char in content):
                warnings.append(self._make_issue(
                    '编码警告',
                    '文件包含非ASCII字符，建议使用UTF-8编码',
                    severity='warning',
                ))
            return content, errors, warnings

        errors.append(self._make_issue('编码错误', '无法使用常见编码读取文件'))
        return None, errors, warnings

    def _detect_heuristic_issues(self, content: str) -> List[Dict[str, Any]]:
        """在字符串外部检测常见非标准 JSON 写法。"""
        issues: List[Dict[str, Any]] = []
        seen: set[Tuple[str, int, int]] = set()

        def add_issue(issue_type: str, message: str, index: int) -> None:
            line, column = self._position_at(content, index)
            key = (issue_type, line, column)
            if key in seen:
                return
            seen.add(key)
            issues.append(self._make_issue(issue_type, message, line, column))

        for start, end in self._outside_string_spans(content):
            segment = content[start:end]

            for match in self._TRAILING_COMMA_RE.finditer(segment):
                add_issue(
                    '尾随逗号',
                    f'第{self._position_at(content, start + match.start())[0]}行存在尾随逗号',
                    start + match.start(),
                )

            for match in self._SINGLE_QUOTE_STRING_RE.finditer(segment):
                add_issue(
                    '单引号错误',
                    f'第{self._position_at(content, start + match.start())[0]}行使用了单引号，JSON标准要求使用双引号',
                    start + match.start(),
                )

            for match in self._LINE_COMMENT_RE.finditer(segment):
                add_issue(
                    '注释错误',
                    f'第{self._position_at(content, start + match.start())[0]}行包含注释，JSON标准不支持注释',
                    start + match.start(),
                )

        return issues

    def load_json_file(self, file_path: str) -> Tuple[Any, List[Dict[str, Any]]]:
        """加载JSON文件并检测基本语法错误。"""
        content, read_errors, _warnings = self._read_file(file_path)
        if content is None:
            return None, read_errors

        try:
            data = json.loads(content)
            return data, read_errors
        except json.JSONDecodeError as exc:
            errors = list(read_errors)
            errors.append(self._make_issue(
                'JSON解析错误',
                str(exc),
                getattr(exc, 'lineno', '未知'),
                getattr(exc, 'colno', '未知'),
            ))
            errors.extend(self._detect_heuristic_issues(content))
            return None, errors

    def detect_encoding_errors(self, file_path: str) -> List[Dict[str, Any]]:
        """检测编码错误。"""
        _content, errors, warnings = self._read_file(file_path)
        return errors + warnings

    def detect_file(self, file_path: str) -> Dict[str, Any]:
        """检测单个文件并返回结构化结果。"""
        path = Path(file_path)
        content, read_errors, encoding_warnings = self._read_file(file_path)

        errors = list(read_errors)
        warnings = list(encoding_warnings)
        parsed = False

        if content is not None:
            try:
                json.loads(content)
                parsed = True
            except json.JSONDecodeError as exc:
                errors.append(self._make_issue(
                    'JSON解析错误',
                    str(exc),
                    getattr(exc, 'lineno', '未知'),
                    getattr(exc, 'colno', '未知'),
                ))
                errors.extend(self._detect_heuristic_issues(content))

        return {
            'file_path': str(path),
            'file_name': path.name,
            'parsed': parsed,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings),
        }

    def generate_report(self, errors: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> str:
        """生成检测报告。"""
        report = [
            "=" * 60,
            "JSON错误检测报告",
            "=" * 60,
            f"错误数量: {len(errors)}",
            f"警告数量: {len(warnings)}",
            "",
        ]

        if errors:
            report.append("错误详情:")
            report.append("-" * 30)
            for index, error in enumerate(errors, 1):
                report.extend([
                    f"{index}. {error['type']}",
                    f"   消息: {error['message']}",
                    f"   位置: 第{error['line']}行, 第{error['column']}列",
                    f"   严重程度: {error['severity']}",
                    "",
                ])

        if warnings:
            report.append("警告详情:")
            report.append("-" * 30)
            for index, warning in enumerate(warnings, 1):
                report.extend([
                    f"{index}. {warning['type']}",
                    f"   消息: {warning['message']}",
                    f"   位置: 第{warning['line']}行, 第{warning['column']}列",
                    f"   严重程度: {warning['severity']}",
                    "",
                ])

        if not errors and not warnings:
            report.append("JSON文件没有发现错误！")

        return "\n".join(report)

    def _format_file_section(self, file_result: Dict[str, Any], index: int) -> List[str]:
        section = [
            f"[{index}] 问题文件: {file_result['file_name']}",
            f"文件路径: {file_result['file_path']}",
            "-" * 60,
        ]
        for issue in file_result['errors'] + file_result['warnings']:
            section.append(
                f"  {issue['type']}: {issue['message']} "
                f"(第{issue['line']}行, 第{issue['column']}列)"
            )
        section.append("")
        return section

    def detect_folder(self, folder_path: str) -> Dict[str, Any]:
        """检测文件夹中所有 JSON 文件并返回结构化结果。"""
        root = Path(folder_path)
        json_files = sorted({path for path in root.rglob('*.json') if path.is_file()})

        file_results: List[Dict[str, Any]] = []
        total_errors = 0
        total_warnings = 0

        for json_file in json_files:
            result = self.detect_file(str(json_file))
            total_errors += result['error_count']
            total_warnings += result['warning_count']
            if result['error_count'] or result['warning_count']:
                file_results.append(result)

        return {
            'folder_path': str(root),
            'total_files': len(json_files),
            'processed_files': len(json_files),
            'problem_files': len(file_results),
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'files': file_results,
        }

    def generate_folder_report(self, folder_result: Dict[str, Any]) -> str:
        """根据结构化文件夹检测结果生成文本报告。"""
        if folder_result['total_files'] == 0:
            return "在指定文件夹中未找到JSON文件"

        report = [
            "=" * 80,
            "JSON文件夹错误检测报告",
            "=" * 80,
            f"检测文件夹: {folder_result['folder_path']}",
            f"找到JSON文件数量: {folder_result['total_files']}",
            "",
        ]

        for index, file_result in enumerate(folder_result['files'], 1):
            report.extend(self._format_file_section(file_result, index))

        report.extend([
            "=" * 80,
            "检测总结",
            "=" * 80,
            f"处理文件数量: {folder_result['processed_files']}/{folder_result['total_files']}",
            f"问题文件数量: {folder_result['problem_files']}",
            f"总错误数量: {folder_result['total_errors']}",
            f"总警告数量: {folder_result['total_warnings']}",
        ])

        if folder_result['total_errors'] == 0 and folder_result['total_warnings'] == 0:
            report.append("所有JSON文件都没有发现错误！")
        else:
            report.append(
                "发现 "
                f"{folder_result['problem_files']} 个问题文件，包含 "
                f"{folder_result['total_errors']} 个错误和 "
                f"{folder_result['total_warnings']} 个警告"
            )

        return "\n".join(report)

    def detect_errors(self, file_path: str) -> str:
        """主检测函数（单文件文本报告）。"""
        result = self.detect_file(file_path)
        return self.generate_report(result['errors'], result['warnings'])

    def detect_errors_in_folder(self, folder_path: str) -> str:
        """检测文件夹中所有JSON文件的错误（文本报告）。"""
        return self.generate_folder_report(self.detect_folder(folder_path))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="检测JSON文件或文件夹中的错误")
    parser.add_argument("path", help="JSON文件路径或文件夹路径")
    parser.add_argument("--output", help="输出报告到文件")

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"路径不存在: {args.path}")
        return

    detector = JSONErrorDetector()

    if os.path.isdir(args.path):
        report = detector.detect_errors_in_folder(args.path)
    else:
        report = detector.detect_errors(args.path)

    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
