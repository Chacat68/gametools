#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
越南文Excel处理器
合并越南文检测和Excel扫描导出功能，支持文件夹输出
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from localization_checker import VietnameseDetector


class VietnameseExcelProcessor:
    """越南文Excel处理器 - 合并检测和导出功能"""
    
    def __init__(self):
        self.vietnamese_detector = VietnameseDetector()
        self.supported_extensions = {'.xlsx', '.xls', '.csv', '.tsv'}
    
    def is_supported_file(self, file_path: Path) -> bool:
        """
        检查文件是否为支持的格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 如果是支持的格式返回True
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def scan_excel_file(self, file_path: Path) -> List[Dict]:
        """
        扫描单个Excel文件中的越南文
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            List[Dict]: 包含越南文的位置信息列表
        """
        results = []
        
        try:
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                try:
                    # 读取工作表
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # 扫描每个单元格
                    for row_idx, row in df.iterrows():
                        for col_idx, value in enumerate(row):
                            if pd.notna(value) and self.vietnamese_detector.contains_vietnamese(str(value)):
                                results.append({
                                    'excel_file': file_path.name,
                                    'sheet_name': sheet_name,
                                    'row': row_idx + 2,  # +2 因为pandas从0开始，且Excel有标题行
                                    'col': col_idx + 1,  # +1 因为pandas从0开始
                                    'column_name': df.columns[col_idx] if col_idx < len(df.columns) else f'Column_{col_idx + 1}',
                                    'content': str(value),
                                    'position': f"第{row_idx + 2}行第{col_idx + 1}列",
                                    'file_path': str(file_path)
                                })
                
                except Exception as e:
                    print(f"读取工作表 '{sheet_name}' 时出错: {e}")
                    continue
        
        except Exception as e:
            print(f"读取Excel文件 {file_path} 时出错: {e}")
        
        return results
    
    def scan_csv_file(self, file_path: Path) -> List[Dict]:
        """
        扫描单个CSV文件中的越南文
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            List[Dict]: 包含越南文的位置信息列表
        """
        results = []
        
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    
                    # 扫描每个单元格
                    for row_idx, row in df.iterrows():
                        for col_idx, value in enumerate(row):
                            if pd.notna(value) and self.vietnamese_detector.contains_vietnamese(str(value)):
                                results.append({
                                    'excel_file': file_path.name,
                                    'sheet_name': 'CSV数据',
                                    'row': row_idx + 2,  # +2 因为pandas从0开始，且CSV有标题行
                                    'col': col_idx + 1,  # +1 因为pandas从0开始
                                    'column_name': df.columns[col_idx] if col_idx < len(df.columns) else f'Column_{col_idx + 1}',
                                    'content': str(value),
                                    'position': f"第{row_idx + 2}行第{col_idx + 1}列",
                                    'file_path': str(file_path)
                                })
                    break  # 成功读取后跳出循环
                    
                except UnicodeDecodeError:
                    continue
            
        except Exception as e:
            print(f"读取CSV文件 {file_path} 时出错: {e}")
        
        return results
    
    def scan_single_file(self, file_path: Path) -> List[Dict]:
        """
        扫描单个文件中的越南文
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict]: 包含越南文的位置信息列表
        """
        if not self.is_supported_file(file_path):
            return []
        
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            return self.scan_excel_file(file_path)
        elif file_path.suffix.lower() in ['.csv', '.tsv']:
            return self.scan_csv_file(file_path)
        
        return []
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[Dict]:
        """
        扫描目录下的所有支持文件
        
        Args:
            directory_path: 要扫描的目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            List[Dict]: 所有文件中越南文的位置信息
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"错误: 目录 {directory_path} 不存在")
            return []
        
        if not directory.is_dir():
            print(f"错误: {directory_path} 不是一个目录")
            return []
        
        all_results = []
        supported_files = []
        
        # 收集所有支持的文件
        if recursive:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and self.is_supported_file(file_path):
                    supported_files.append(file_path)
        else:
            for file_path in directory.iterdir():
                if file_path.is_file() and self.is_supported_file(file_path):
                    supported_files.append(file_path)
        
        print(f"找到 {len(supported_files)} 个支持的文件")
        
        # 扫描每个文件
        for i, file_path in enumerate(supported_files, 1):
            print(f"正在扫描 ({i}/{len(supported_files)}): {file_path.name}")
            
            file_results = self.scan_single_file(file_path)
            all_results.extend(file_results)
            
            if file_results:
                print(f"  - 找到 {len(file_results)} 个越南文位置")
            else:
                print(f"  - 未找到越南文")
        
        return all_results
    
    def create_output_excel(self, results: List[Dict], output_folder: str, filename: str = "越南文检测结果.xlsx") -> str:
        """
        创建输出Excel文件
        
        Args:
            results: 扫描结果列表
            output_folder: 输出文件夹路径
            filename: 输出文件名
            
        Returns:
            str: 输出文件的完整路径
        """
        try:
            # 确保输出文件夹存在
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 构建完整的输出文件路径
            full_output_path = output_path / filename
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "越南文检测结果"
            
            # 设置标题行
            headers = ['序号', '文件名', '工作表', '位置', '列名', '越南文内容', '文件路径']
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # 添加数据
            for row_idx, result in enumerate(results, 2):
                ws.cell(row=row_idx, column=1, value=row_idx - 1)  # 序号
                ws.cell(row=row_idx, column=2, value=result['excel_file'])
                ws.cell(row=row_idx, column=3, value=result['sheet_name'])
                ws.cell(row=row_idx, column=4, value=result['position'])
                ws.cell(row=row_idx, column=5, value=result['column_name'])
                ws.cell(row=row_idx, column=6, value=result['content'])
                ws.cell(row=row_idx, column=7, value=result['file_path'])
            
            # 设置列宽
            column_widths = [8, 25, 15, 15, 20, 50, 60]
            for col, width in enumerate(column_widths, 1):
                ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = width
            
            # 设置边框
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for row in ws.iter_rows():
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            
            # 冻结首行
            ws.freeze_panes = "A2"
            
            # 保存文件
            wb.save(full_output_path)
            return str(full_output_path)
            
        except Exception as e:
            print(f"创建输出Excel文件时出错: {e}")
            return ""
    
    def create_summary_report(self, results: List[Dict], output_folder: str, filename: str = "检测汇总报告.txt") -> str:
        """
        创建汇总报告文件
        
        Args:
            results: 扫描结果列表
            output_folder: 输出文件夹路径
            filename: 报告文件名
            
        Returns:
            str: 报告文件的完整路径
        """
        try:
            # 确保输出文件夹存在
            output_path = Path(output_folder)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 构建完整的报告文件路径
            full_report_path = output_path / filename
            
            # 统计信息
            total_files = len(set(result['excel_file'] for result in results))
            total_locations = len(results)
            
            # 按文件分组统计
            file_stats = {}
            for result in results:
                file_name = result['excel_file']
                if file_name not in file_stats:
                    file_stats[file_name] = 0
                file_stats[file_name] += 1
            
            # 生成报告内容
            report_content = f"""越南文检测汇总报告
{'=' * 50}

检测时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

统计信息:
- 包含越南文的文件总数: {total_files}
- 越南文位置总数: {total_locations}

文件详情:
"""
            
            for file_name, count in sorted(file_stats.items()):
                report_content += f"- {file_name}: {count} 个位置\n"
            
            if results:
                report_content += f"\n详细位置信息:\n"
                report_content += f"{'=' * 50}\n"
                
                for i, result in enumerate(results, 1):
                    report_content += f"{i}. 文件: {result['excel_file']}\n"
                    report_content += f"   工作表: {result['sheet_name']}\n"
                    report_content += f"   位置: {result['position']}\n"
                    report_content += f"   列名: {result['column_name']}\n"
                    report_content += f"   内容: {result['content']}\n"
                    report_content += f"   路径: {result['file_path']}\n"
                    report_content += f"   {'-' * 40}\n"
            else:
                report_content += "\n未发现任何越南文内容。\n"
            
            # 写入报告文件
            with open(full_report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return str(full_report_path)
            
        except Exception as e:
            print(f"创建汇总报告时出错: {e}")
            return ""
    
    def process_directory(self, directory_path: str, output_folder: str, recursive: bool = True, 
                         create_excel: bool = True, create_report: bool = True) -> Dict:
        """
        处理目录并导出结果
        
        Args:
            directory_path: 要扫描的目录路径
            output_folder: 输出文件夹路径
            recursive: 是否递归扫描子目录
            create_excel: 是否创建Excel结果文件
            create_report: 是否创建汇总报告
            
        Returns:
            Dict: 包含处理统计信息的字典
        """
        print("开始扫描文件中的越南文...")
        print("=" * 50)
        
        # 扫描目录
        results = self.scan_directory(directory_path, recursive)
        
        # 统计信息
        stats = {
            'total_files_scanned': len(list(Path(directory_path).rglob('*.xlsx'))) + 
                                 len(list(Path(directory_path).rglob('*.xls'))) +
                                 len(list(Path(directory_path).rglob('*.csv'))) +
                                 len(list(Path(directory_path).rglob('*.tsv'))),
            'files_with_vietnamese': len(set(result['excel_file'] for result in results)),
            'total_vietnamese_locations': len(results),
            'results': results,
            'output_files': []
        }
        
        print("\n" + "=" * 50)
        print("扫描完成！")
        print(f"扫描的文件总数: {stats['total_files_scanned']}")
        print(f"包含越南文的文件数: {stats['files_with_vietnamese']}")
        print(f"越南文位置总数: {stats['total_vietnamese_locations']}")
        
        # 创建输出文件
        if results:
            print(f"\n正在创建输出文件到: {output_folder}")
            
            if create_excel:
                excel_path = self.create_output_excel(results, output_folder)
                if excel_path:
                    print(f"Excel结果文件创建成功: {excel_path}")
                    stats['output_files'].append(excel_path)
                    stats['excel_success'] = True
                else:
                    print("Excel结果文件创建失败！")
                    stats['excel_success'] = False
            
            if create_report:
                report_path = self.create_summary_report(results, output_folder)
                if report_path:
                    print(f"汇总报告创建成功: {report_path}")
                    stats['output_files'].append(report_path)
                    stats['report_success'] = True
                else:
                    print("汇总报告创建失败！")
                    stats['report_success'] = False
        else:
            print("未找到任何越南文内容，不创建输出文件。")
            stats['excel_success'] = False
            stats['report_success'] = False
        
        return stats


def main():
    """主函数 - 命令行版本"""
    import sys
    
    print("越南文Excel处理器")
    print("=" * 50)
    
    # 获取用户输入
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
    else:
        directory_path = input("请输入要扫描的目录路径: ").strip()
    
    if not directory_path:
        print("错误: 未提供目录路径")
        return
    
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    else:
        output_folder = input("请输入输出文件夹路径: ").strip()
    
    if not output_folder:
        print("错误: 未提供输出文件夹路径")
        return
    
    # 创建处理器并执行处理
    processor = VietnameseExcelProcessor()
    stats = processor.process_directory(directory_path, output_folder)
    
    print("\n按任意键退出...")
    input()


if __name__ == "__main__":
    main()
