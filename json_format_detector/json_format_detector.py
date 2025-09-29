#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON文件text字段格式检测工具
用于检测JSON文件中text字段的格式一致性，找出与通用格式不一致的内容
"""

import json
import re
import argparse
import os
from typing import List, Dict, Any, Tuple, Set
from collections import Counter
import difflib


class JSONFormatDetector:
    """JSON格式检测器"""
    
    def __init__(self):
        self.text_patterns = []
        self.inconsistencies = []
        self.common_pattern = None
        
    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是单个对象，转换为列表
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise ValueError("JSON文件必须包含对象或对象数组")
                
            return data
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return []
    
    def extract_text_fields(self, data: List[Dict[str, Any]], text_key: str = "text") -> List[str]:
        """提取所有text字段的内容"""
        texts = []
        
        def extract_recursive(obj, key):
            if isinstance(obj, dict):
                if key in obj and isinstance(obj[key], str):
                    texts.append(obj[key])
                for value in obj.values():
                    extract_recursive(value, key)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, key)
        
        for item in data:
            extract_recursive(item, text_key)
        
        return texts
    
    def analyze_text_patterns(self, texts: List[str]) -> Dict[str, Any]:
        """分析文本格式模式"""
        if not texts:
            return {}
        
        # 分析各种格式特征
        patterns = {
            'lengths': [len(text) for text in texts],
            'line_counts': [text.count('\n') + 1 for text in texts],
            'has_newlines': [bool('\n' in text) for text in texts],
            'has_tabs': [bool('\t' in text) for text in texts],
            'has_spaces': [bool(' ' in text) for text in texts],
            'starts_with_space': [text.startswith(' ') for text in texts],
            'ends_with_space': [text.endswith(' ') for text in texts],
            'has_quotes': [bool('"' in text or "'" in text) for text in texts],
            'has_brackets': [bool('[' in text or ']' in text) for text in texts],
            'has_braces': [bool('{' in text or '}' in text) for text in texts],
            'has_parentheses': [bool('(' in text or ')' in text) for text in texts],
            'has_special_chars': [bool(re.search(r'[^\w\s\n\t.,!?;:()\[\]{}"\'-]', text)) for text in texts],
            'word_counts': [len(text.split()) for text in texts],
            'char_counts': [len(text.replace(' ', '').replace('\n', '').replace('\t', '')) for text in texts]
        }
        
        return patterns
    
    def find_common_pattern(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """找出通用格式模式"""
        common = {}
        
        for feature, values in patterns.items():
            if not values:
                continue
                
            # 计算最常见的值
            counter = Counter(values)
            most_common = counter.most_common(1)[0]
            
            # 如果最常见值占比超过70%，认为是通用模式
            if most_common[1] / len(values) >= 0.7:
                common[feature] = {
                    'value': most_common[0],
                    'frequency': most_common[1],
                    'percentage': most_common[1] / len(values) * 100
                }
            else:
                common[feature] = {
                    'value': 'inconsistent',
                    'frequency': most_common[1],
                    'percentage': most_common[1] / len(values) * 100,
                    'all_values': dict(counter)
                }
        
        return common
    
    def detect_inconsistencies(self, texts: List[str], common_pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测格式不一致的内容"""
        inconsistencies = []
        
        for i, text in enumerate(texts):
            issues = []
            
            # 检查各种格式特征
            if 'lengths' in common_pattern and common_pattern['lengths']['value'] != 'inconsistent':
                if len(text) != common_pattern['lengths']['value']:
                    issues.append(f"长度不一致: 期望{common_pattern['lengths']['value']}, 实际{len(text)}")
            
            if 'line_counts' in common_pattern and common_pattern['line_counts']['value'] != 'inconsistent':
                line_count = text.count('\n') + 1
                if line_count != common_pattern['line_counts']['value']:
                    issues.append(f"行数不一致: 期望{common_pattern['line_counts']['value']}, 实际{line_count}")
            
            if 'has_newlines' in common_pattern and common_pattern['has_newlines']['value'] != 'inconsistent':
                has_newlines = bool('\n' in text)
                if has_newlines != common_pattern['has_newlines']['value']:
                    issues.append(f"换行符不一致: 期望{common_pattern['has_newlines']['value']}, 实际{has_newlines}")
            
            if 'starts_with_space' in common_pattern and common_pattern['starts_with_space']['value'] != 'inconsistent':
                starts_with_space = text.startswith(' ')
                if starts_with_space != common_pattern['starts_with_space']['value']:
                    issues.append(f"开头空格不一致: 期望{common_pattern['starts_with_space']['value']}, 实际{starts_with_space}")
            
            if 'ends_with_space' in common_pattern and common_pattern['ends_with_space']['value'] != 'inconsistent':
                ends_with_space = text.endswith(' ')
                if ends_with_space != common_pattern['ends_with_space']['value']:
                    issues.append(f"结尾空格不一致: 期望{common_pattern['ends_with_space']['value']}, 实际{ends_with_space}")
            
            if 'word_counts' in common_pattern and common_pattern['word_counts']['value'] != 'inconsistent':
                word_count = len(text.split())
                if word_count != common_pattern['word_counts']['value']:
                    issues.append(f"单词数不一致: 期望{common_pattern['word_counts']['value']}, 实际{word_count}")
            
            if issues:
                inconsistencies.append({
                    'index': i,
                    'text': text,
                    'issues': issues
                })
        
        return inconsistencies
    
    def generate_report(self, texts: List[str], common_pattern: Dict[str, Any], inconsistencies: List[Dict[str, Any]]) -> str:
        """生成检测报告"""
        report = []
        report.append("=" * 60)
        report.append("JSON文件text字段格式检测报告")
        report.append("=" * 60)
        report.append(f"总文本数量: {len(texts)}")
        report.append(f"格式不一致数量: {len(inconsistencies)}")
        report.append("")
        
        # 通用格式模式
        report.append("通用格式模式:")
        report.append("-" * 30)
        for feature, info in common_pattern.items():
            if info['value'] != 'inconsistent':
                report.append(f"{feature}: {info['value']} (占比: {info['percentage']:.1f}%)")
            else:
                report.append(f"{feature}: 不一致 (最常见: {info['frequency']}次, 占比: {info['percentage']:.1f}%)")
        report.append("")
        
        # 不一致内容详情
        if inconsistencies:
            report.append("格式不一致的内容:")
            report.append("-" * 30)
            for item in inconsistencies:
                report.append(f"索引 {item['index']}:")
                report.append(f"  文本: {repr(item['text'])}")
                report.append(f"  问题: {'; '.join(item['issues'])}")
                report.append("")
        else:
            report.append("所有text字段格式一致！")
        
        return "\n".join(report)
    
    def detect_format(self, file_path: str, text_key: str = "text") -> str:
        """主检测函数"""
        # 加载JSON文件
        data = self.load_json_file(file_path)
        if not data:
            return "无法加载JSON文件"
        
        # 提取text字段
        texts = self.extract_text_fields(data, text_key)
        if not texts:
            return f"未找到'{text_key}'字段"
        
        # 分析格式模式
        patterns = self.analyze_text_patterns(texts)
        common_pattern = self.find_common_pattern(patterns)
        
        # 检测不一致内容
        inconsistencies = self.detect_inconsistencies(texts, common_pattern)
        
        # 生成报告
        return self.generate_report(texts, common_pattern, inconsistencies)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="检测JSON文件中text字段的格式一致性")
    parser.add_argument("file_path", help="JSON文件路径")
    parser.add_argument("--text-key", default="text", help="要检测的字段名 (默认: text)")
    parser.add_argument("--output", help="输出报告到文件")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"文件不存在: {args.file_path}")
        return
    
    detector = JSONFormatDetector()
    report = detector.detect_format(args.file_path, args.text_key)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
