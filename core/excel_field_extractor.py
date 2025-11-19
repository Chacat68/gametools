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
        # 错误日志列表
        self.error_logs = []
        self.extraction_warnings = []  # 提取警告（例如第6行数据为空）
        # 无文本内容的表格列表
        self.empty_tables = []  # 存储没有检测到文本内容的表格
    
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
    
    def find_column_range_between_markers(self, sheet, marker: str = "c_classic_battle") -> Tuple[int, int]:
        """
        查找两个标记之间的列范围（不包含标记本身）
        
        Args:
            sheet: openpyxl工作表对象
            marker: 要查找的标记文本（默认为 "c_classic_battle"）
            
        Returns:
            Tuple[int, int]: (起始列号, 结束列号)，如果未找到返回 (1, sheet.max_column)
        """
        marker_columns = []
        
        # 在第5行查找标记（字段名行）
        field_row = 5
        if sheet.max_row >= field_row:
            for cell in sheet[field_row]:
                if cell.value and marker in str(cell.value):
                    marker_columns.append(cell.column)
        
        # 如果找到至少两个标记，返回它们之间的范围（不包含标记列本身）
        if len(marker_columns) >= 2:
            start_col = marker_columns[0] + 1  # 第一个标记的下一列
            end_col = marker_columns[1] - 1    # 第二个标记的上一列
            # 确保范围有效
            if start_col <= end_col:
                return (start_col, end_col)
        
        # 如果没有找到两个标记，返回整个表格范围
        return (1, sheet.max_column)
    
    def extract_fields_from_excel(self, file_path) -> List[Dict]:
        """
        从Excel文件中提取包含文本内容的列的字段信息
        仅扫描两个 c_classic_battle 标记之间的列范围
        
        Args:
            file_path: Excel文件路径（可以是字符串或Path对象）
            
        Returns:
            List[Dict]: 每个工作表的字段信息列表
        """
        results = []
        
        # 确保file_path是Path对象
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        try:
            # 使用openpyxl读取，以便精确访问物理行
            wb = openpyxl.load_workbook(file_path, data_only=True)
            
            for sheet_name in wb.sheetnames:
                try:
                    sheet = wb[sheet_name]
                    
                    # 查找两个 c_classic_battle 之间的列范围
                    start_col, end_col = self.find_column_range_between_markers(sheet)
                    
                    # 检测包含本地化文本内容的列
                    text_columns = set()
                    
                    # 只扫描数据行（从第6行开始），忽略表头和字段行
                    # 这样可以过滤掉ID、配置列等纯代码/数字列
                    data_start_row = 6  # 第6行开始是数据
                    
                    if sheet.max_row >= data_start_row:
                        # 只扫描指定列范围内的单元格
                        for row in sheet.iter_rows(min_row=data_start_row, max_row=sheet.max_row, 
                                                   min_col=start_col, max_col=end_col):
                            for cell in row:
                                if cell.value is not None and self.contains_text(cell.value):
                                    text_columns.add(cell.column)
                    
                    if not text_columns:
                        # 如果没有找到包含本地化文本的列，记录到空表列表
                        self.empty_tables.append({
                            'excel_file': file_path.name,
                            'sheet_name': sheet_name,
                            'file_path': str(file_path)
                        })
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
                                
                                # 检查示例数据是否为空
                                if not example_value or example_value.strip() == "":
                                    warning_msg = (
                                        f"⚠️ 示例数据为空 | "
                                        f"文件: {file_path.name} | "
                                        f"工作表: {sheet_name} | "
                                        f"字段: {field_name} | "
                                        f"位置: 第6行,第{col_num}列({get_column_letter(col_num)}6)"
                                    )
                                    self.extraction_warnings.append(warning_msg)
                                    print(warning_msg)
                                
                                field_with_example = f"{field_name},{example_value}"
                            else:
                                # 表格行数不足6行
                                warning_msg = (
                                    f"⚠️ 表格行数不足 | "
                                    f"文件: {file_path.name} | "
                                    f"工作表: {sheet_name} | "
                                    f"字段: {field_name} | "
                                    f"当前行数: {sheet.max_row} (需要至少6行)"
                                )
                                self.extraction_warnings.append(warning_msg)
                                print(warning_msg)
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
                    error_msg = f"❌ 读取工作表失败 | 文件: {file_path.name} | 工作表: {sheet_name} | 错误: {str(e)}"
                    self.error_logs.append(error_msg)
                    print(error_msg)
            
            wb.close()
        
        except Exception as e:
            error_msg = f"❌ 读取文件失败 | 文件: {file_path} | 错误: {str(e)}"
            self.error_logs.append(error_msg)
            print(error_msg)
        
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
            # 构建JSON结构，分为两部分
            json_output = {
                "empty_tables": [],  # 无文本内容的表格（放在前面）
                "tables_with_text": []  # 有文本内容的表格
            }
            
            # 添加无文本内容的表格
            for empty_table in self.empty_tables:
                json_output["empty_tables"].append({
                    "table_name": empty_table['excel_file'],
                    "sheet_name": empty_table['sheet_name']
                })
            
            # 添加有文本内容的表格
            for result in results:
                json_output["tables_with_text"].append({
                    "table_name": result['excel_file'],
                    "sheet_name": result['sheet_name'],
                    "fields_with_examples": result.get('fields_with_examples', []),
                    "field_count": result['field_count']
                })
            
            # 写入JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            
            print(f"结果已导出到: {output_file}")
            print(f"  - 无文本表格数: {len(json_output['empty_tables'])}")
            print(f"  - 有文本表格数: {len(json_output['tables_with_text'])}")
            return output_file
        
        except Exception as e:
            print(f"导出到JSON时出错: {e}")
            return None
    
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
                # 第一部分：写入无文本内容的表格
                f.write("=== 无文本内容的表格 ===\n")
                for empty_table in self.empty_tables:
                    table_name = f"{empty_table['excel_file']}#{empty_table['sheet_name']}"
                    f.write(f"{table_name}\n")
                
                # 分隔符
                f.write("\n=== 有文本内容的表格 ===\n")
                
                # 第二部分：写入有文本内容的表格
                for result in results:
                    table_name = f"{result['excel_file']}#{result['sheet_name']}"
                    # 使用带示例的字段列表
                    fields_with_examples = result.get('fields_with_examples', result.get('fields', []))
                    if isinstance(fields_with_examples, list) and len(fields_with_examples) > 0:
                        fields_str = ','.join(fields_with_examples)
                    else:
                        fields_str = ''
                    f.write(f"{table_name},{fields_str}\n")
            
            print(f"结果已导出到: {output_file}")
            print(f"  - 无文本表格数: {len(self.empty_tables)}")
            print(f"  - 有文本表格数: {len(results)}")
            return output_file
        
        except Exception as e:
            print(f"导出到CSV时出错: {e}")
            return None
    
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
            header_font = Font(bold=True, size=11, color='FFFFFF')
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            section_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
            empty_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            current_row = 1
            
            # 第一部分：无文本内容的表格
            if self.empty_tables:
                # 分类标题
                ws.merge_cells(f'A{current_row}:B{current_row}')
                section_cell = ws[f'A{current_row}']
                section_cell.value = '=== 无文本内容的表格 ==='
                section_cell.font = Font(bold=True, size=12)
                section_cell.fill = section_fill
                section_cell.alignment = header_alignment
                current_row += 1
                
                # 表头
                ws[f'A{current_row}'] = '表名'
                ws[f'B{current_row}'] = '工作表'
                for col in ['A', 'B']:
                    cell = ws[f'{col}{current_row}']
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                    cell.border = border
                current_row += 1
                
                # 数据
                for empty_table in self.empty_tables:
                    ws[f'A{current_row}'] = empty_table['excel_file']
                    ws[f'B{current_row}'] = empty_table['sheet_name']
                    for col in ['A', 'B']:
                        ws[f'{col}{current_row}'].border = border
                        ws[f'{col}{current_row}'].fill = empty_fill
                    current_row += 1
                
                current_row += 1  # 空行分隔
            
            # 第二部分：有文本内容的表格
            if results:
                # 分类标题
                ws.merge_cells(f'A{current_row}:D{current_row}')
                section_cell = ws[f'A{current_row}']
                section_cell.value = '=== 有文本内容的表格 ==='
                section_cell.font = Font(bold=True, size=12)
                section_cell.fill = section_fill
                section_cell.alignment = header_alignment
                current_row += 1
                
                # 表头
                ws[f'A{current_row}'] = '表名'
                ws[f'B{current_row}'] = '工作表'
                ws[f'C{current_row}'] = '字段数量'
                ws[f'D{current_row}'] = '字段+示例'
                
                for col in ['A', 'B', 'C', 'D']:
                    cell = ws[f'{col}{current_row}']
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                    cell.border = border
                current_row += 1
                
                # 数据
                for result in results:
                    ws[f'A{current_row}'] = result['excel_file']
                    ws[f'B{current_row}'] = result['sheet_name']
                    ws[f'C{current_row}'] = result['field_count']
                    # 字段+示例列
                    fields_with_examples = result.get('fields_with_examples', [])
                    ws[f'D{current_row}'] = ', '.join(fields_with_examples) if fields_with_examples else ''
                    
                    # 设置边框
                    for col in ['A', 'B', 'C', 'D']:
                        ws[f'{col}{current_row}'].border = border
                    
                    # 居中对齐
                    ws[f'C{current_row}'].alignment = Alignment(horizontal="center")
                    current_row += 1
            
            # 设置列宽
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 100
            
            wb.save(output_file)
            print(f"结果已导出到: {output_file}")
            return output_file
        
        except Exception as e:
            print(f"导出到Excel时出错: {e}")
            return None
    
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
        
        # 显示日志统计
        if self.error_logs:
            print(f"错误日志数: {len(self.error_logs)}")
        if self.extraction_warnings:
            print(f"警告日志数: {len(self.extraction_warnings)}")
        
        return stats
    
    def get_error_logs(self) -> List[str]:
        """
        获取所有错误日志
        
        Returns:
            List[str]: 错误日志列表
        """
        return self.error_logs.copy()
    
    def get_warning_logs(self) -> List[str]:
        """
        获取所有警告日志（提取失败警告）
        
        Returns:
            List[str]: 警告日志列表
        """
        return self.extraction_warnings.copy()
    
    def get_all_logs(self) -> Dict[str, List[str]]:
        """
        获取所有日志（错误+警告）
        
        Returns:
            Dict: 包含errors和warnings的字典
        """
        return {
            'errors': self.error_logs.copy(),
            'warnings': self.extraction_warnings.copy()
        }
    
    def clear_logs(self):
        """清除所有日志"""
        self.error_logs.clear()
        self.extraction_warnings.clear()
    
    def save_logs_to_file(self, output_file: Path):
        """
        保存日志到文件
        
        Args:
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("Excel字段提取 - 错误与警告日志\n")
                f.write("="*70 + "\n\n")
                
                if self.error_logs:
                    f.write(f"【错误日志】 共 {len(self.error_logs)} 条\n")
                    f.write("-"*70 + "\n")
                    for i, log in enumerate(self.error_logs, 1):
                        f.write(f"{i}. {log}\n")
                    f.write("\n")
                else:
                    f.write("【错误日志】 无错误\n\n")
                
                if self.extraction_warnings:
                    f.write(f"【警告日志】 共 {len(self.extraction_warnings)} 条\n")
                    f.write("-"*70 + "\n")
                    for i, log in enumerate(self.extraction_warnings, 1):
                        f.write(f"{i}. {log}\n")
                    f.write("\n")
                else:
                    f.write("【警告日志】 无警告\n\n")
                
                f.write("="*70 + "\n")
                f.write(f"总计: {len(self.error_logs)} 个错误, {len(self.extraction_warnings)} 个警告\n")
            
            print(f"日志已保存到: {output_file}")
            return True
        
        except Exception as e:
            print(f"保存日志文件失败: {e}")
            return False


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
