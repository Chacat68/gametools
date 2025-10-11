#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的JSON错误检测脚本
"""

import sys
import os
from json_error_detector import JSONErrorDetector


def main():
    """简化的主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python detect_error.py <JSON文件路径或文件夹路径>")
        print("示例: python detect_error.py example_data.json")
        print("示例: python detect_error.py ./json_files/")
        return
    
    path = sys.argv[1]
    
    if not os.path.exists(path):
        print(f"路径不存在: {path}")
        return
    
    detector = JSONErrorDetector()
    
    # 判断是文件还是文件夹
    if os.path.isdir(path):
        print(f"正在检测文件夹: {path}")
        print()
        report = detector.detect_errors_in_folder(path)
    else:
        print(f"正在检测文件: {path}")
        print()
        report = detector.detect_errors(path)
    
    print(report)


if __name__ == "__main__":
    main()