#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON错误检测工具
用于检测JSON文件中的语法错误、结构错误、编码错误等
"""

import json
import re
import argparse
import os
from typing import List, Dict, Any, Tuple, Set
from collections import Counter
import difflib


class JSONErrorDetector:
    """JSON错误检测器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def load_json_file(self, file_path: str) -> Tuple[Any, List[Dict[str, Any]]]:
        """加载JSON文件并检测基本语法错误"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检测基本语法错误
            syntax_errors = self._detect_syntax_errors(content)
            errors.extend(syntax_errors)
            
            if not syntax_errors:
                # 尝试解析JSON
                try:
                    data = json.loads(content)
                    return data, errors
                except json.JSONDecodeError as e:
                    errors.append({
                        'type': 'JSON解析错误',
                        'message': str(e),
                        'line': getattr(e, 'lineno', '未知'),
                        'column': getattr(e, 'colno', '未知'),
                        'severity': 'error'
                    })
            else:
                return None, errors
                
        except Exception as e:
            errors.append({
                'type': '文件读取错误',
                'message': str(e),
                'line': '未知',
                'column': '未知',
                'severity': 'error'
            })
            return None, errors
    
    def _detect_syntax_errors(self, content: str) -> List[Dict[str, Any]]:
        """检测JSON语法错误"""
        errors = []
        lines = content.split('\n')
        
        # 检测常见的语法错误
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
                
            # 检测单引号（JSON标准不支持单引号）
            if "'" in line and not line.startswith('//'):
                errors.append({
                    'type': '单引号错误',
                    'message': f'第{i}行使用了单引号，JSON标准要求使用双引号',
                    'line': i,
                    'column': line.find("'") + 1,
                    'severity': 'error'
                })
            
            # 检测注释（JSON标准不支持注释）
            if '//' in line and not line.strip().startswith('//'):
                errors.append({
                    'type': '注释错误',
                    'message': f'第{i}行包含注释，JSON标准不支持注释',
                    'line': i,
                    'column': line.find('//') + 1,
                    'severity': 'error'
                })
        
        # 检测尾随逗号（更精确的检测）
        trailing_comma_errors = self._detect_trailing_commas(content)
        errors.extend(trailing_comma_errors)
        
        return errors
    
    def _detect_trailing_commas(self, content: str) -> List[Dict[str, Any]]:
        """检测尾随逗号"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检测对象中的尾随逗号
            if re.search(r',\s*}', line):
                comma_pos = line.rfind(',')
                if comma_pos != -1:
                    errors.append({
                        'type': '尾随逗号',
                        'message': f'第{i}行对象中存在尾随逗号',
                        'line': i,
                        'column': comma_pos + 1,
                        'severity': 'error'
                    })
            
            # 检测数组中的尾随逗号
            if re.search(r',\s*]', line):
                comma_pos = line.rfind(',')
                if comma_pos != -1:
                    errors.append({
                        'type': '尾随逗号',
                        'message': f'第{i}行数组中存在尾随逗号',
                        'line': i,
                        'column': comma_pos + 1,
                        'severity': 'error'
                    })
        
        return errors
    
    def detect_structure_errors(self, data: Any) -> List[Dict[str, Any]]:
        """检测JSON结构错误"""
        errors = []
        
        if isinstance(data, dict):
            # 检测重复键
            keys = list(data.keys())
            if len(keys) != len(set(keys)):
                duplicates = [k for k in set(keys) if keys.count(k) > 1]
                errors.append({
                    'type': '重复键',
                    'message': f'发现重复的键: {duplicates}',
                    'line': '未知',
                    'column': '未知',
                    'severity': 'error'
                })
            
            # 递归检测嵌套结构
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    errors.extend(self.detect_structure_errors(value))
        
        elif isinstance(data, list):
            # 检测数组中的结构不一致
            if data:
                first_type = type(data[0])
                for i, item in enumerate(data[1:], 1):
                    if type(item) != first_type:
                        errors.append({
                            'type': '数组类型不一致',
                            'message': f'数组第{i+1}个元素类型与第一个元素不一致',
                            'line': '未知',
                            'column': '未知',
                            'severity': 'warning'
                        })
                        break
            
            # 递归检测嵌套结构
            for item in data:
                if isinstance(item, (dict, list)):
                    errors.extend(self.detect_structure_errors(item))
        
        return errors
    
    
    def detect_encoding_errors(self, file_path: str) -> List[Dict[str, Any]]:
        """检测编码错误"""
        errors = []
        
        try:
            # 尝试不同的编码方式读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    # 如果能成功读取，检查是否包含非ASCII字符
                    if encoding != 'utf-8' and any(ord(c) > 127 for c in content):
                        errors.append({
                            'type': '编码警告',
                            'message': f'文件包含非ASCII字符，建议使用UTF-8编码',
                            'line': '未知',
                            'column': '未知',
                            'severity': 'warning'
                        })
                    break
                except UnicodeDecodeError:
                    continue
            else:
                errors.append({
                    'type': '编码错误',
                    'message': '无法使用常见编码读取文件',
                    'line': '未知',
                    'column': '未知',
                    'severity': 'error'
                })
                
        except Exception as e:
            errors.append({
                'type': '编码检测错误',
                'message': str(e),
                'line': '未知',
                'column': '未知',
                'severity': 'error'
            })
        
        return errors
    
    
    def generate_report(self, errors: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> str:
        """生成检测报告"""
        report = []
        report.append("=" * 60)
        report.append("JSON错误检测报告")
        report.append("=" * 60)
        report.append(f"错误数量: {len(errors)}")
        report.append(f"警告数量: {len(warnings)}")
        report.append("")
        
        # 错误详情
        if errors:
            report.append("错误详情:")
            report.append("-" * 30)
            for i, error in enumerate(errors, 1):
                report.append(f"{i}. {error['type']}")
                report.append(f"   消息: {error['message']}")
                report.append(f"   位置: 第{error['line']}行, 第{error['column']}列")
                report.append(f"   严重程度: {error['severity']}")
                report.append("")
        
        # 警告详情
        if warnings:
            report.append("警告详情:")
            report.append("-" * 30)
            for i, warning in enumerate(warnings, 1):
                report.append(f"{i}. {warning['type']}")
                report.append(f"   消息: {warning['message']}")
                report.append(f"   位置: 第{warning['line']}行, 第{warning['column']}列")
                report.append(f"   严重程度: {warning['severity']}")
                report.append("")
        
        if not errors and not warnings:
            report.append("JSON文件没有发现错误！")
        
        return "\n".join(report)
    
    def detect_errors(self, file_path: str) -> str:
        """主检测函数"""
        all_errors = []
        all_warnings = []
        
        # 检测编码错误
        encoding_errors = self.detect_encoding_errors(file_path)
        all_errors.extend([e for e in encoding_errors if e['severity'] == 'error'])
        all_warnings.extend([e for e in encoding_errors if e['severity'] == 'warning'])
        
        # 加载JSON文件
        data, load_errors = self.load_json_file(file_path)
        all_errors.extend(load_errors)
        
        if data is not None:
            # 检测结构错误
            structure_errors = self.detect_structure_errors(data)
            all_errors.extend([e for e in structure_errors if e['severity'] == 'error'])
            all_warnings.extend([e for e in structure_errors if e['severity'] == 'warning'])
        
        # 生成报告
        return self.generate_report(all_errors, all_warnings)
    
    def detect_errors_in_folder(self, folder_path: str) -> str:
        """检测文件夹中所有JSON文件的错误"""
        import glob
        
        # 查找文件夹中的所有JSON文件
        json_files = glob.glob(os.path.join(folder_path, "*.json"))
        json_files.extend(glob.glob(os.path.join(folder_path, "**", "*.json"), recursive=True))
        
        if not json_files:
            return "在指定文件夹中未找到JSON文件"
        
        # 生成文件夹检测报告
        report = []
        report.append("=" * 80)
        report.append("JSON文件夹错误检测报告")
        report.append("=" * 80)
        report.append(f"检测文件夹: {folder_path}")
        report.append(f"找到JSON文件数量: {len(json_files)}")
        report.append("")
        
        total_errors = 0
        total_warnings = 0
        processed_files = 0
        problem_files = 0
        
        for i, json_file in enumerate(json_files, 1):
            try:
                # 检测单个文件
                file_report = self.detect_errors(json_file)
                
                # 解析文件报告中的错误和警告数量
                lines = file_report.split('\n')
                file_errors = 0
                file_warnings = 0
                
                for line in lines:
                    if "错误数量:" in line:
                        file_errors = int(line.split(":")[1].strip())
                    elif "警告数量:" in line:
                        file_warnings = int(line.split(":")[1].strip())
                
                total_errors += file_errors
                total_warnings += file_warnings
                processed_files += 1
                
                # 只显示有问题的文件
                if file_errors > 0 or file_warnings > 0:
                    problem_files += 1
                    report.append(f"[{problem_files}] 问题文件: {os.path.basename(json_file)}")
                    report.append(f"文件路径: {json_file}")
                    report.append("-" * 60)
                    
                    # 提取错误详情部分
                    error_section = False
                    warning_section = False
                    for line in lines:
                        if "错误详情:" in line:
                            error_section = True
                            continue
                        elif "警告详情:" in line:
                            error_section = False
                            warning_section = True
                            continue
                        elif line.startswith("JSON文件没有发现错误"):
                            break
                        
                        if error_section or warning_section:
                            if line.strip() and not line.startswith("-"):
                                report.append(f"  {line}")
                    
                    report.append("")
                
            except Exception as e:
                # 即使检测过程中出错，也要记录这个文件
                problem_files += 1
                report.append(f"[{problem_files}] 检测失败文件: {os.path.basename(json_file)}")
                report.append(f"文件路径: {json_file}")
                report.append(f"错误信息: {str(e)}")
                report.append("")
        
        # 添加总结
        report.append("=" * 80)
        report.append("检测总结")
        report.append("=" * 80)
        report.append(f"处理文件数量: {processed_files}/{len(json_files)}")
        report.append(f"问题文件数量: {problem_files}")
        report.append(f"总错误数量: {total_errors}")
        report.append(f"总警告数量: {total_warnings}")
        
        if total_errors == 0 and total_warnings == 0:
            report.append("所有JSON文件都没有发现错误！")
        else:
            report.append(f"发现 {problem_files} 个问题文件，包含 {total_errors} 个错误和 {total_warnings} 个警告")
        
        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="检测JSON文件或文件夹中的错误")
    parser.add_argument("path", help="JSON文件路径或文件夹路径")
    parser.add_argument("--output", help="输出报告到文件")
    parser.add_argument("--folder", action="store_true", help="指定路径为文件夹")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"路径不存在: {args.path}")
        return
    
    detector = JSONErrorDetector()
    
    # 判断是文件还是文件夹
    if os.path.isdir(args.path) or args.folder:
        # 文件夹模式
        report = detector.detect_errors_in_folder(args.path)
    else:
        # 文件模式
        report = detector.detect_errors(args.path)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
