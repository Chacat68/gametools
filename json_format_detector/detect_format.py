#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的JSON格式检测脚本
"""

import sys
import os
from json_format_detector import JSONFormatDetector


def main():
    """简化的主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python detect_format.py <JSON文件路径> [字段名]")
        print("示例: python detect_format.py example_data.json text")
        return
    
    file_path = sys.argv[1]
    text_key = sys.argv[2] if len(sys.argv) > 2 else "text"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    print(f"正在检测文件: {file_path}")
    print(f"检测字段: {text_key}")
    print()
    
    detector = JSONFormatDetector()
    report = detector.detect_format(file_path, text_key)
    print(report)


if __name__ == "__main__":
    main()
