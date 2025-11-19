#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel表字段导出器
扫描Excel文件，检测包含本地化文本内容（中文、越南文、泰文）的列，
从第5行提取字段名。忽略纯数字、英文代码和配置项。
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelFieldExtractor:
    """Excel表字段导出器"""
    
    def __init__(self):
        self.supported_extensions = {'.xlsx', '.xls'}
        # 定义文本模式：只匹配中文、越南文、泰文
        # 中文：\u4e00-\u9fff (CJK统一汉字), \u3400-\u4dbf (CJK扩展A)
        # 越南文：\u00C0-\u1EF9 (包含带音标的拉丁字母)
        # 泰文：\u0E00-\u0E7F
        self.text_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u00C0-\u1EF9\u0E00-\u0E7F]')
    
    def is_excel_file(self, file_path: Path) -> bool:
        """
        检查文件是否为支持的Excel格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 如果是Excel格式返回True
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def contains_text(self, value) -> bool:
        """
        检查值是否包含本地化文本内容（仅限中文、越南文、泰文）
        排除：纯数字、英文代码、配置项等
        
        Args:
            value: 要检查的值
            
        Returns:
            bool: 包含本地化文本返回True
        """
        if pd.isna(value):
            return False
        
        value_str = str(value).strip()
        
        # 排除空值
        if not value_str:
            return False
        
        # 排除纯数字（包括小数、负数、科学计数法）
        if value_str.replace('.', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '').isdigit():
            return False
        
        # 排除看起来像代码或配置的内容（包含特殊符号但不含目标文字）
        # 例如：ID_001, CONFIG_NAME, true, false, null 等
        if not self.text_pattern.search(value_str):
            return False
        
        # 检查是否包含中文、越南文或泰文字符
        return True
    
    def extract_fields_from_excel(self, file_path: Path) -> List[Dict]:
        """
        从Excel文件中提取包含文本内容的列的字段信息
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            List[Dict]: 每个工作表的字段信息列表
        """
        results = []
        
        try:
            # 使用openpyxl读取，以便精确访问物理行
            wb = openpyxl.load_workbook(file_path, data_only=True)
            
            for sheet_name in wb.sheetnames:
                try:
                    sheet = wb[sheet_name]
                    
                    # 检测包含本地化文本内容的列
                    text_columns = set()
                    
                    # 只扫描数据行（从第6行开始），忽略表头和字段行
                    # 这样可以过滤掉ID、配置列等纯代码/数字列
                    data_start_row = 6  # 第6行开始是数据
                    
                    if sheet.max_row >= data_start_row:
                        for row in sheet.iter_rows(min_row=data_start_row, max_row=sheet.max_row):
                            for cell in row:
                                if cell.value is not None and self.contains_text(cell.value):
                                    text_columns.add(cell.column)
                    
                    if not text_columns:
                        # 如果没有找到包含本地化文本的列，跳过这个工作表
                        continue
                    
                    # 从第5行提取字段名，从第6行提取示例数据
                    fields = []
                    field_with_examples = []  # 新增：字段名+示例的组合列表
                    field_row = 5  # 物理行第5行
                    example_row = 6  # 物理行第6行（前端示例）
                    
                    if sheet.max_row >= field_row:
                        for col_num in sorted(text_columns):
                            # 提取字段名
                            field_cell = sheet.cell(row=field_row, column=col_num)
                            field_name = str(field_cell.value) if field_cell.value is not None else f"列{col_num}"
                            fields.append(field_name)
                            
                            # 提取第6行的示例数据
                            if sheet.max_row >= example_row:
                                example_cell = sheet.cell(row=example_row, column=col_num)
                                example_value = str(example_cell.value) if example_cell.value is not None else ""
                                field_with_example = f"{field_name},{example_value}"
                            else:
                                field_with_example = f"{field_name},"
                            
                            field_with_examples.append(field_with_example)
                    else:
                        # 如果表格行数不足5行，使用列号
                        for col_num in sorted(text_columns):
                            fields.append(f"列{col_num}")
                            field_with_examples.append(f"列{col_num},")
                    
                    if fields:
                        results.append({
                            'excel_file': file_path.name,
                            'sheet_name': sheet_name,
                            'fields': fields,
                            'fields_with_examples': field_with_examples,  # 新增：带示例的字段列表
                            'field_count': len(fields),
                            'text_columns': sorted(text_columns)
                        })
                
                except Exception as e:
                    print(f"读取工作表 '{sheet_name}' 时出错: {e}")
            
            wb.close()
        
        except Exception as e:
            print(f"读取文件 '{file_path}' 时出错: {e}")
        
        return results
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict]:
        """
        扫描目录中的所有Excel文件
        
        Args:
            directory: 要扫描的目录
            recursive: 是否递归扫描子目录
            
        Returns:
            List[Dict]: 所有Excel文件的字段信息
        """
        all_results = []
        
        if not directory.exists():
            print(f"目录不存在: {directory}")
            return all_results
        
        # 获取所有Excel文件
        if recursive:
            excel_files = [f for f in directory.rglob("*") if self.is_excel_file(f)]
        else:
            excel_files = [f for f in directory.glob("*") if self.is_excel_file(f)]
        
        print(f"找到 {len(excel_files)} 个Excel文件")
        
        for idx, file_path in enumerate(excel_files, 1):
            print(f"处理文件 {idx}/{len(excel_files)}: {file_path.name}")
            results = self.extract_fields_from_excel(file_path)
            all_results.extend(results)
        
        return all_results
    
    def export_to_json(self, results: List[Dict], output_file: Path):
        """
        导出结果到JSON文件
        
        Args:
            results: 字段信息列表
            output_file: 输出文件路径
        """
        try:
            # 构建JSON结构
            json_output = []
            for result in results:
                json_output.append({
                    "table_name": result['excel_file'],
                    "sheet_name": result['sheet_name'],
                    "fields": result['fields'],
                    "fields_with_examples": result.get('fields_with_examples', []),  # 新增：带示例的字段
                    "field_count": result['field_count']
                })
            
            # 写入JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            
            print(f"结果已导出到: {output_file}")
        
        except Exception as e:
            print(f"导出到JSON时出错: {e}")
    
    def export_to_csv(self, results: List[Dict], output_file: Path):
        """
        导出结果到CSV文件
        格式：表名,字段1,字段2,...
        
        Args:
            results: 字段信息列表
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                for result in results:
                    table_name = f"{result['excel_file']}#{result['sheet_name']}"
                    # 使用带示例的字段列表
                    fields_with_examples = result.get('fields_with_examples', result['fields'])
                    if isinstance(fields_with_examples, list) and len(fields_with_examples) > 0:
                        # 如果有示例数据，使用它
                        if ',' in str(fields_with_examples[0]):
                            fields_str = ','.join(fields_with_examples)
                        else:
                            # 否则使用普通字段
                            fields_str = ','.join(result['fields'])
                    else:
                        fields_str = ','.join(result['fields'])
                    f.write(f"{table_name},{fields_str}\n")
            
            print(f"结果已导出到: {output_file}")
        
        except Exception as e:
            print(f"导出到CSV时出错: {e}")
    
    def export_to_excel(self, results: List[Dict], output_file: Path):
        """
        导出结果到Excel文件，带格式
        
        Args:
            results: 字段信息列表
            output_file: 输出文件路径
        """
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "字段导出结果"
            
            # 设置样式
            header_font = Font(bold=True, size=11)
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # 写入表头
            ws['A1'] = '表名'
            ws['B1'] = '工作表'
            ws['C1'] = '字段数量'
            ws['D1'] = '字段列表'
            ws['E1'] = '字段+示例'
            
            for col in ['A', 'B', 'C', 'D', 'E']:
                cell = ws[f'{col}1']
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
            
            # 设置列宽
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 60
            ws.column_dimensions['E'].width = 80
            
            # 写入数据
            for idx, result in enumerate(results, start=2):
                ws[f'A{idx}'] = result['excel_file']
                ws[f'B{idx}'] = result['sheet_name']
                ws[f'C{idx}'] = result['field_count']
                ws[f'D{idx}'] = ', '.join(result['fields'])
                # 新增：字段+示例列
                fields_with_examples = result.get('fields_with_examples', [])
                ws[f'E{idx}'] = ', '.join(fields_with_examples) if fields_with_examples else ''
                
                # 设置边框
                for col in ['A', 'B', 'C', 'D', 'E']:
                    ws[f'{col}{idx}'].border = border
                
                # 居中对齐
                ws[f'C{idx}'].alignment = Alignment(horizontal="center")
            
            wb.save(output_file)
            print(f"结果已导出到: {output_file}")
        
        except Exception as e:
            print(f"导出到Excel时出错: {e}")
    
    def process_directory(self, 
                         directory_path: str, 
                         output_folder: str = None,
                         output_format: str = 'json',
                         recursive: bool = True) -> Dict:
        """
        处理目录并导出结果
        
        Args:
            directory_path: 要扫描的目录路径
            output_folder: 输出文件夹（如果为None，使用扫描目录）
            output_format: 输出格式 ('json', 'csv' 或 'excel')
            recursive: 是否递归扫描
            
        Returns:
            Dict: 处理统计信息，包含results数据
        """
        directory = Path(directory_path)
        
        if output_folder:
            output_dir = Path(output_folder)
        else:
            output_dir = directory
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描目录
        print(f"开始扫描目录: {directory}")
        results = self.scan_directory(directory, recursive=recursive)
        
        if not results:
            print("未找到包含文本内容的Excel表格")
            return {
                'total_files': 0,
                'total_sheets': 0,
                'total_fields': 0,
                'results': []
            }
        
        # 导出结果
        if output_format == 'json':
            output_file = output_dir / "field_extraction_result.json"
            self.export_to_json(results, output_file)
        elif output_format == 'csv':
            output_file = output_dir / "field_extraction_result.csv"
            self.export_to_csv(results, output_file)
        else:
            output_file = output_dir / "field_extraction_result.xlsx"
            self.export_to_excel(results, output_file)
        
        # 统计信息
        total_files = len(set(r['excel_file'] for r in results))
        total_sheets = len(results)
        total_fields = sum(r['field_count'] for r in results)
        
        stats = {
            'total_files': total_files,
            'total_sheets': total_sheets,
            'total_fields': total_fields,
            'output_file': str(output_file),
            'results': results
        }
        
        print(f"\n处理完成!")
        print(f"总文件数: {total_files}")
        print(f"总工作表数: {total_sheets}")
        print(f"总字段数: {total_fields}")
        
        return stats


if __name__ == "__main__":
    # 测试代码
    extractor = ExcelFieldExtractor()
    
    # 示例用法
    test_dir = Path("test_excel_files")
    if test_dir.exists():
        stats = extractor.process_directory(
            directory_path=str(test_dir),
            output_format='excel',
            recursive=True
        )
        print(f"\n统计信息: {stats}")
    else:
        print(f"测试目录不存在: {test_dir}")
