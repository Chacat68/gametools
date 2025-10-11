#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
越南文检测工具
用于检测目录下包含越南文的表格文件
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set
import pandas as pd
import openpyxl
from openpyxl import load_workbook


class VietnameseDetector:
    """越南文检测器"""
    
    def __init__(self):
        # 越南文字符范围
        self.vietnamese_patterns = [
            # 基本拉丁字母 + 越南语声调符号
            r'[àáạảãâầấậẩẫăằắặẳẵ]',  # a with tones
            r'[èéẹẻẽêềếệểễ]',        # e with tones
            r'[ìíịỉĩ]',              # i with tones
            r'[òóọỏõôồốộổỗơờớợởỡ]',  # o with tones
            r'[ùúụủũưừứựửữ]',        # u with tones
            r'[ỳýỵỷỹ]',              # y with tones
            r'[đ]',                  # d with stroke
            # 大写字母
            r'[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]',
            r'[ÈÉẸẺẼÊỀẾỆỂỄ]',
            r'[ÌÍỊỈĨ]',
            r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]',
            r'[ÙÚỤỦŨƯỪỨỰỬỮ]',
            r'[ỲÝỴỶỸ]',
            r'[Đ]'
        ]
        
        # 编译正则表达式
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.vietnamese_patterns]
    
    def contains_vietnamese(self, text: str) -> bool:
        """
        检测文本中是否包含越南文字符
        
        Args:
            text: 要检测的文本
            
        Returns:
            bool: 如果包含越南文返回True，否则返回False
        """
        if not isinstance(text, str):
            return False
            
        # 检查所有越南文模式
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False


class TableChecker:
    """表格检测器"""
    
    def __init__(self):
        self.vietnamese_detector = VietnameseDetector()
        self.supported_extensions = {'.xlsx', '.xls', '.csv', '.tsv'}
    
    def is_table_file(self, file_path: Path) -> bool:
        """
        检查文件是否为支持的表格格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 如果是支持的表格格式返回True
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def read_excel_file(self, file_path: Path) -> List[str]:
        """
        读取Excel文件内容
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            List[str]: 所有单元格的文本内容
        """
        try:
            # 使用openpyxl读取Excel文件
            workbook = load_workbook(file_path, data_only=True)
            all_text = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.value is not None:
                            all_text.append(str(cell.value))
            
            return all_text
        except Exception as e:
            print(f"读取Excel文件 {file_path} 时出错: {e}")
            return []
    
    def read_csv_file(self, file_path: Path) -> List[str]:
        """
        读取CSV文件内容
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            List[str]: 所有单元格的文本内容
        """
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    all_text = []
                    
                    for column in df.columns:
                        for value in df[column].dropna():
                            all_text.append(str(value))
                    
                    return all_text
                except UnicodeDecodeError:
                    continue
            
            print(f"无法读取CSV文件 {file_path}，尝试了多种编码")
            return []
            
        except Exception as e:
            print(f"读取CSV文件 {file_path} 时出错: {e}")
            return []
    
    def check_table_has_vietnamese(self, file_path: Path) -> bool:
        """
        检查表格文件是否包含越南文
        
        Args:
            file_path: 表格文件路径
            
        Returns:
            bool: 如果包含越南文返回True
        """
        if not self.is_table_file(file_path):
            return False
        
        # 根据文件扩展名选择读取方法
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            text_content = self.read_excel_file(file_path)
        elif file_path.suffix.lower() in ['.csv', '.tsv']:
            text_content = self.read_csv_file(file_path)
        else:
            return False
        
        # 检查所有文本内容是否包含越南文
        for text in text_content:
            if self.vietnamese_detector.contains_vietnamese(text):
                return True
        
        return False


class LocalizationChecker:
    """本地化检测主类"""
    
    def __init__(self):
        self.table_checker = TableChecker()
    
    def scan_directory(self, directory_path: str, recursive: bool = False) -> List[str]:
        """
        扫描目录下的所有表格文件，检测包含越南文的文件
        
        Args:
            directory_path: 要扫描的目录路径
            recursive: 是否递归扫描子目录，默认为False
            
        Returns:
            List[str]: 包含越南文的表格文件名列表
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"错误: 目录 {directory_path} 不存在")
            return []
        
        if not directory.is_dir():
            print(f"错误: {directory_path} 不是一个目录")
            return []
        
        valid_tables = []
        
        print(f"Scanning directory: {directory_path}")
        print(f"Recursive scan: {'Yes' if recursive else 'No'}")
        print("Supported formats: .xlsx, .xls, .csv, .tsv")
        print("-" * 50)
        
        # 根据recursive参数决定扫描方式
        if recursive:
            # 递归扫描所有文件
            for file_path in directory.rglob('*'):
                if file_path.is_file() and self.table_checker.is_table_file(file_path):
                    print(f"Checking file: {file_path.name}...", end=" ")
                    
                    if self.table_checker.check_table_has_vietnamese(file_path):
                        valid_tables.append(file_path.name)
                        print("YES - Contains Vietnamese")
                    else:
                        print("NO - No Vietnamese")
        else:
            # 只扫描当前目录
            for file_path in directory.iterdir():
                if file_path.is_file() and self.table_checker.is_table_file(file_path):
                    print(f"Checking file: {file_path.name}...", end=" ")
                    
                    if self.table_checker.check_table_has_vietnamese(file_path):
                        valid_tables.append(file_path.name)
                        print("YES - Contains Vietnamese")
                    else:
                        print("NO - No Vietnamese")
        
        return valid_tables
    
    def print_results(self, valid_tables: List[str]):
        """
        打印检测结果
        
        Args:
            valid_tables: 有效表格文件名列表
        """
        print("\n" + "=" * 50)
        print("Scan Results:")
        print("=" * 50)
        
        if valid_tables:
            print(f"Found {len(valid_tables)} table files containing Vietnamese:")
            for i, table_name in enumerate(valid_tables, 1):
                print(f"{i:2d}. {table_name}")
        else:
            print("No table files containing Vietnamese found")
        
        print("=" * 50)


def main():
    """主函数"""
    print("Localization Checker - Vietnamese Table Detector")
    print("=" * 50)
    
    # 获取用户输入的目录路径
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = input("Enter directory path to scan: ").strip()
    
    if not directory_path:
        print("Error: No directory path provided")
        return
    
    # 创建检测器并开始扫描
    checker = LocalizationChecker()
    valid_tables = checker.scan_directory(directory_path)
    
    # 打印结果
    checker.print_results(valid_tables)


if __name__ == "__main__":
    main()
