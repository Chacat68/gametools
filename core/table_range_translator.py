#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表范围翻译提取器
根据字段导出的JSON配置文件，智能提取多语言翻译内容
只提取前端、后端、前后端的字段，忽略策划字段
生成多语言翻译总表，支持中文、越南文、泰文
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import pandas as pd
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TableRangeTranslator:
    """表范围翻译提取器"""
    
    def __init__(self):
        """初始化翻译提取器"""
        self.supported_extensions = {'.xlsx', '.xls'}
        
        # 文本模式：中文、越南文、泰文
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
        self.vietnamese_pattern = re.compile(r'[\u00C0-\u1EF9]')
        self.thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
        
        # 需要导出的字段类型（忽略"策划"）
        self.exportable_field_types = {'前端', '后端', '前后端'}
        
        # 结果存储
        self.translation_results = []
        self.processing_stats = {
            'total_tables': 0,
            'processed_tables': 0,
            'skipped_tables': 0,
            'total_fields': 0,
            'exported_fields': 0,
            'skipped_fields': 0,
            'total_rows': 0
        }
        
        self.error_logs = []
    
    def load_json_config(self, json_path: str) -> Dict:
        """
        加载JSON配置文件
        
        Args:
            json_path: JSON配置文件路径
            
        Returns:
            Dict: JSON配置内容
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"成功加载JSON配置: {json_path}")
            logger.info(f"  - no_text_tables: {len(config.get('no_text_tables', []))} 个")
            logger.info(f"  - text_tables: {len(config.get('text_tables', []))} 个")
            
            return config
        
        except Exception as e:
            logger.error(f"加载JSON配置失败: {e}")
            return {}
    
    def parse_field_with_type(self, field_str: str) -> Tuple[str, str]:
        """
        解析字段字符串，提取字段名和字段类型
        格式: "field_name,field_type" 或 "field_name,"
        
        Args:
            field_str: 字段字符串
            
        Returns:
            Tuple[str, str]: (字段名, 字段类型)
        """
        if ',' in field_str:
            parts = field_str.split(',', 1)
            field_name = parts[0].strip()
            field_type = parts[1].strip() if len(parts) > 1 else ''
            return field_name, field_type
        else:
            return field_str.strip(), ''
    
    def is_exportable_field(self, field_type: str) -> bool:
        """
        判断字段类型是否需要导出
        
        Args:
            field_type: 字段类型（前端、后端、前后端、策划等）
            
        Returns:
            bool: True表示需要导出
        """
        return field_type in self.exportable_field_types
    
    def detect_language_type(self, text: str) -> str:
        """
        检测文本语言类型
        
        Args:
            text: 待检测文本
            
        Returns:
            str: 语言类型（中文、越南文、泰文、中越混合等）
        """
        if pd.isna(text) or not str(text).strip():
            return "空"
        
        text_str = str(text).strip()
        
        has_chinese = bool(self.chinese_pattern.search(text_str))
        has_vietnamese = bool(self.vietnamese_pattern.search(text_str))
        has_thai = bool(self.thai_pattern.search(text_str))
        
        # 判断语言类型
        if has_chinese and has_vietnamese:
            return "中越混合"
        elif has_chinese and has_thai:
            return "中泰混合"
        elif has_vietnamese and has_thai:
            return "越泰混合"
        elif has_chinese:
            return "中文"
        elif has_vietnamese:
            return "越南文"
        elif has_thai:
            return "泰文"
        else:
            return "其他"
    
    def column_index_to_letter(self, col_idx: int) -> str:
        """
        将列索引转换为Excel列字母（A, B, C, ..., Z, AA, AB, ...）
        
        Args:
            col_idx: 列索引（从0开始）
            
        Returns:
            str: Excel列字母
        """
        result = ""
        col_num = col_idx + 1  # Excel列从1开始
        
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord('A')) + result
            col_num //= 26
        
        return result
    
    def find_column_index_by_name(self, df: pd.DataFrame, field_name: str) -> Optional[int]:
        """
        在DataFrame的第5行（索引4）中查找字段名对应的列索引
        
        Args:
            df: pandas DataFrame
            field_name: 要查找的字段名
            
        Returns:
            Optional[int]: 列索引，未找到返回None
        """
        if len(df) < 5:
            return None
        
        # 第5行是字段名行（索引为4）
        field_row = df.iloc[4]
        
        for col_idx, cell_value in enumerate(field_row):
            if pd.notna(cell_value) and str(cell_value).strip() == field_name:
                return col_idx
        
        return None
    
    def extract_table_data(self, excel_path: str, table_info: Dict) -> List[Dict]:
        """
        从Excel表格中提取指定字段的数据
        
        Args:
            excel_path: Excel文件路径
            table_info: 表格信息（包含 table_name, sheet_name, fields_with_examples）
            
        Returns:
            List[Dict]: 提取的数据行列表
        """
        try:
            table_name = table_info.get('table_name', '')
            sheet_name = table_info.get('sheet_name', '')
            fields_with_examples = table_info.get('fields_with_examples', [])
            
            logger.info(f"开始提取表格: {table_name} - {sheet_name}")
            
            # 解析字段信息，过滤出需要导出的字段
            exportable_fields = []
            for field_str in fields_with_examples:
                field_name, field_type = self.parse_field_with_type(field_str)
                if self.is_exportable_field(field_type):
                    exportable_fields.append((field_name, field_type))
                else:
                    self.processing_stats['skipped_fields'] += 1
                    logger.debug(f"跳过字段: {field_name} (类型: {field_type})")
            
            if not exportable_fields:
                logger.info(f"表格 {table_name} 没有需要导出的字段，跳过")
                return []
            
            logger.info(f"可导出字段: {len(exportable_fields)} 个")
            self.processing_stats['exported_fields'] += len(exportable_fields)
            
            # 读取Excel文件
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
            
            # 从第7行开始提取数据（索引6）
            if len(df) < 7:
                logger.warning(f"表格 {table_name} 数据行不足，跳过")
                return []
            
            extracted_rows = []
            
            # 遍历每个需要导出的字段
            for field_name, field_type in exportable_fields:
                # 查找字段对应的列索引
                col_idx = self.find_column_index_by_name(df, field_name)
                
                if col_idx is None:
                    logger.warning(f"未找到字段: {field_name}")
                    continue
                
                # 从第7行开始提取数据
                for row_idx in range(6, len(df)):  # 从索引6开始（第7行）
                    cell_value = df.iloc[row_idx, col_idx]
                    
                    # 跳过空值
                    if pd.isna(cell_value) or not str(cell_value).strip():
                        continue
                    
                    # 检测语言类型
                    lang_type = self.detect_language_type(cell_value)
                    
                    # 只提取包含中文、越南文、泰文的内容
                    if lang_type not in ["中文", "越南文", "泰文", "中越混合", "中泰混合", "越泰混合"]:
                        continue
                    
                    # 提取A列的ID值
                    id_value = df.iloc[row_idx, 0] if len(df.columns) > 0 else ''
                    
                    # 生成Excel物理位置（如F8）
                    col_letter = self.column_index_to_letter(col_idx)
                    excel_position = f"{col_letter}{row_idx + 1}"
                    
                    extracted_rows.append({
                        'table_name': table_name,
                        'sheet_name': sheet_name,
                        'field_name': field_name,
                        'field_type': field_type,
                        'excel_position': excel_position,  # Excel物理位置（如F8）
                        'id': id_value,
                        'content': str(cell_value).strip(),
                        'language_type': lang_type
                    })
                    
                    self.processing_stats['total_rows'] += 1
            
            logger.info(f"提取完成: {len(extracted_rows)} 行数据")
            return extracted_rows
        
        except Exception as e:
            error_msg = f"提取表格数据失败 {table_name}: {e}"
            logger.error(error_msg)
            self.error_logs.append(error_msg)
            return []
    
    def process_with_json_config(self, json_path: str, excel_directory: str) -> List[Dict]:
        """
        根据JSON配置处理Excel文件
        
        Args:
            json_path: JSON配置文件路径
            excel_directory: Excel文件所在目录
            
        Returns:
            List[Dict]: 所有提取的数据
        """
        try:
            # 加载JSON配置
            config = self.load_json_config(json_path)
            if not config:
                return []
            
            # 获取text_tables列表（跳过no_text_tables）
            text_tables = config.get('text_tables', [])
            self.processing_stats['total_tables'] = len(text_tables)
            
            logger.info(f"开始处理 {len(text_tables)} 个包含文本的表格")
            
            all_data = []
            
            # 处理每个表格
            for table_info in text_tables:
                table_name = table_info.get('table_name', '')
                
                # 构建Excel文件路径
                excel_path = os.path.join(excel_directory, table_name)
                
                if not os.path.exists(excel_path):
                    logger.warning(f"文件不存在: {excel_path}")
                    self.processing_stats['skipped_tables'] += 1
                    continue
                
                # 提取表格数据
                table_data = self.extract_table_data(excel_path, table_info)
                all_data.extend(table_data)
                
                self.processing_stats['processed_tables'] += 1
            
            self.translation_results = all_data
            logger.info(f"处理完成，共提取 {len(all_data)} 条数据")
            
            return all_data
        
        except Exception as e:
            logger.error(f"处理失败: {e}")
            return []
    
    def generate_translation_master_table(self, output_path: str, 
                                          chinese_dir: str = None,
                                          vietnamese_dir: str = None,
                                          thai_dir: str = None):
        """
        生成多语言翻译总表
        每个表格文件对应一个工作表标签
        列格式: 文本字段 | 中文内容 | 越南文 | 泰文
        
        Args:
            output_path: 输出Excel文件路径
            chinese_dir: 中文版Excel文件目录
            vietnamese_dir: 越南文版Excel文件目录
            thai_dir: 泰文版Excel文件目录
        """
        try:
            if not self.translation_results:
                logger.warning("没有数据可导出")
                return False
            
            logger.info(f"开始生成翻译总表: {output_path}")
            
            # 按表格名称分组
            tables_data = {}
            for row in self.translation_results:
                table_name = row['table_name']
                if table_name not in tables_data:
                    tables_data[table_name] = []
                tables_data[table_name].append(row)
            
            # 创建Excel工作簿
            wb = Workbook()
            
            # 删除默认工作表
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # 为每个表格创建一个工作表
            for table_name, rows in tables_data.items():
                # 工作表名称（去除扩展名）
                sheet_name = Path(table_name).stem
                # Excel工作表名称限制31字符
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:28] + '...'
                
                ws = wb.create_sheet(title=sheet_name)
                
                # 设置表头
                headers = ['字段名', '字段类型', 'Excel位置', '中文内容', '越南文', '泰文']
                ws.append(headers)
                
                # 设置表头样式
                header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                header_font = Font(bold=True, color='FFFFFF', size=11)
                header_alignment = Alignment(horizontal='center', vertical='center')
                
                for col_idx, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col_idx)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = header_alignment
                
                # 写入数据行
                for row_data in rows:
                    ws.append([
                        row_data.get('field_name', ''),
                        row_data.get('field_type', ''),
                        row_data.get('excel_position', ''),  # Excel物理位置
                        row_data.get('content', '') if row_data.get('language_type', '') in ['中文', '中越混合', '中泰混合'] else '',
                        '',  # 越南文列（待填充）
                        ''   # 泰文列（待填充）
                    ])
                
                # 设置列宽
                column_widths = [20, 12, 12, 40, 40, 40]
                for col_idx, width in enumerate(column_widths, 1):
                    ws.column_dimensions[get_column_letter(col_idx)].width = width
                
                # 冻结首行
                ws.freeze_panes = 'A2'
                
                # 添加边框
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=len(headers)):
                    for cell in row:
                        cell.border = thin_border
                        if cell.row > 1:  # 数据行
                            cell.alignment = Alignment(vertical='center', wrap_text=True)
            
            # 保存工作簿
            wb.save(output_path)
            logger.info(f"翻译总表已生成: {output_path}")
            logger.info(f"  - 工作表数量: {len(tables_data)}")
            logger.info(f"  - 总数据行数: {len(self.translation_results)}")
            
            return True
        
        except Exception as e:
            logger.error(f"生成翻译总表失败: {e}")
            return False
    
    def get_processing_report(self) -> str:
        """
        获取处理报告
        
        Returns:
            str: 处理报告文本
        """
        report_lines = [
            "=" * 70,
            "表范围翻译提取处理报告",
            "=" * 70,
            f"总表格数: {self.processing_stats['total_tables']}",
            f"已处理: {self.processing_stats['processed_tables']}",
            f"已跳过: {self.processing_stats['skipped_tables']}",
            "",
            f"总字段数: {self.processing_stats['total_fields']}",
            f"已导出字段: {self.processing_stats['exported_fields']}",
            f"已跳过字段（策划）: {self.processing_stats['skipped_fields']}",
            "",
            f"提取数据行数: {self.processing_stats['total_rows']}",
            "=" * 70
        ]
        
        if self.error_logs:
            report_lines.append("")
            report_lines.append("错误日志:")
            for error in self.error_logs:
                report_lines.append(f"  - {error}")
            report_lines.append("=" * 70)
        
        return "\n".join(report_lines)


def main():
    """命令行测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="表范围翻译提取器")
    parser.add_argument("json_config", help="JSON配置文件路径")
    parser.add_argument("excel_directory", help="Excel文件目录")
    parser.add_argument("--output", default="翻译总表.xlsx", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 创建提取器
    translator = TableRangeTranslator()
    
    # 处理数据
    results = translator.process_with_json_config(args.json_config, args.excel_directory)
    
    if results:
        # 生成翻译总表
        translator.generate_translation_master_table(args.output)
        
        # 显示报告
        print(translator.get_processing_report())
    else:
        print("处理失败，没有数据")


if __name__ == "__main__":
    main()
