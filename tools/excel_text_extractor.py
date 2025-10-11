#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文本提取器
检测目录中的Excel文件，提取文本内容并创建同名的新Excel文件
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import logging
import re
from collections import defaultdict

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExcelTextExtractor:
    """Excel文本提取器"""
    
    def __init__(self, progress_callback=None):
        """
        初始化文本提取器
        
        Args:
            progress_callback: 进度回调函数，接收 (current, total, filename, message) 参数
        """
        self.supported_formats = ['.xlsx', '.xls']
        self.extracted_texts = {}
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_texts': 0
        }
        self.progress_callback = progress_callback
    
    def _report_progress(self, current: int, total: int, filename: str, message: str):
        """
        报告处理进度
        
        Args:
            current: 当前处理的文件索引
            total: 总文件数
            filename: 当前处理的文件名
            message: 处理消息
        """
        if self.progress_callback:
            self.progress_callback(current, total, filename, message)
        
        # 同时输出到日志
        percentage = (current / total * 100) if total > 0 else 0
        logger.info(f"[{current}/{total}] ({percentage:.1f}%) {filename}: {message}")
    
    def scan_directory(self, directory_path: str) -> List[str]:
        """
        扫描目录中的Excel文件
        
        Args:
            directory_path: 目录路径
            
        Returns:
            Excel文件路径列表
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"目录不存在: {directory_path}")
            
            if not os.path.isdir(directory_path):
                raise ValueError(f"路径不是目录: {directory_path}")
            
            excel_files = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    if file_ext in self.supported_formats:
                        excel_files.append(file_path)
            
            logger.info(f"在目录 {directory_path} 中找到 {len(excel_files)} 个Excel文件")
            return excel_files
            
        except Exception as e:
            logger.error(f"扫描目录失败: {str(e)}")
            raise
    
    def extract_text_from_excel(self, file_path: str, current: int = 0, total: int = 0) -> Dict[str, List[Dict]]:
        """
        从Excel文件中提取文本内容
        
        Args:
            file_path: Excel文件路径
            current: 当前文件索引（用于进度显示）
            total: 总文件数（用于进度显示）
            
        Returns:
            字典，键为工作表名，值为包含文本和A列内容的字典列表
        """
        filename = os.path.basename(file_path)
        
        try:
            self._report_progress(current, total, filename, "开始读取文件")
            
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            self._report_progress(current, total, filename, f"发现 {len(sheet_names)} 个工作表")
            
            extracted_data = {}
            total_texts = 0
            
            for i, sheet_name in enumerate(sheet_names):
                try:
                    self._report_progress(current, total, filename, f"处理工作表 '{sheet_name}' ({i+1}/{len(sheet_names)})")
                    
                    # 读取工作表数据
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    self._report_progress(current, total, filename, f"工作表 '{sheet_name}' 读取完成，共 {len(df)} 行")
                    
                    # 提取文本内容
                    sheet_data = self._extract_texts_from_dataframe(df)
                    if sheet_data and sheet_data['items']:
                        extracted_data[sheet_name] = sheet_data
                        total_texts += len(sheet_data['items'])
                        self._report_progress(current, total, filename, f"工作表 '{sheet_name}' 提取到 {len(sheet_data['items'])} 个文本")
                    else:
                        self._report_progress(current, total, filename, f"工作表 '{sheet_name}' 未提取到文本")
                    
                except Exception as e:
                    self._report_progress(current, total, filename, f"处理工作表 '{sheet_name}' 失败: {str(e)}")
                    logger.warning(f"处理工作表 '{sheet_name}' 失败: {str(e)}")
                    continue
            
            self._report_progress(current, total, filename, f"文件处理完成，共提取 {total_texts} 个文本")
            return extracted_data
            
        except Exception as e:
            self._report_progress(current, total, filename, f"文件处理失败: {str(e)}")
            logger.error(f"提取Excel文件文本失败: {str(e)}")
            return {}
    
    def _extract_texts_from_dataframe(self, df: pd.DataFrame) -> Dict:
        """
        从DataFrame中提取文本内容，从第7行开始检测
        
        Args:
            df: pandas DataFrame
            
        Returns:
            包含提取数据和元信息的字典
        """
        extracted_items = []
        
        try:
            # 检查第7行（索引为6）是否为策划，如果是则跳过提取
            if self._is_planner_row(df):
                logger.info("检测到第7行为策划，跳过文本提取")
                return {'items': [], 'headers': [], 'a_column': None}
            
            # 获取A列（第一列）的列名
            a_column = df.columns[0] if len(df.columns) > 0 else None
            if a_column is None:
                logger.warning("未找到A列，无法提取A列内容")
                return {'items': [], 'headers': [], 'a_column': None}
            
            # 获取第5行作为字段名（索引为4）
            headers = []
            if len(df) >= 5:
                header_row = df.iloc[4]  # 第5行，索引为4
                headers = [str(header_row[col]).strip() if pd.notna(header_row[col]) else col for col in df.columns]
            else:
                headers = list(df.columns)
            
            # 从第7行开始遍历（索引从6开始）
            for row_idx in range(6, len(df)):  # 从第7行开始（索引6）
                row_data = df.iloc[row_idx]
                a_column_value = str(row_data[a_column]).strip() if pd.notna(row_data[a_column]) else ""
                
                # 遍历该行的所有列
                for col_idx, col in enumerate(df.columns):
                    value = row_data[col]
                    if pd.notna(value):  # 跳过空值
                        text = str(value).strip()
                        if text and self._is_text_content(text):
                            # 生成Excel物理位置（如F5）
                            excel_position = self._get_excel_position(col_idx, row_idx + 1)
                            extracted_items.append({
                                'text': text,
                                'a_column': a_column_value,
                                'row': row_idx + 1,  # 实际行号（从1开始）
                                'column': col,
                                'column_index': col_idx,
                                'excel_row_ref': excel_position  # Excel物理位置（如F5）
                            })
            
            # 去重并保持顺序（基于文本内容去重）
            seen_texts = set()
            unique_items = []
            for item in extracted_items:
                if item['text'] not in seen_texts:
                    seen_texts.add(item['text'])
                    unique_items.append(item)
            
            return {
                'items': unique_items,
                'headers': headers,
                'a_column': a_column
            }
            
        except Exception as e:
            logger.error(f"从DataFrame提取文本失败: {str(e)}")
            return {'items': [], 'headers': [], 'a_column': None}
    
    def _is_planner_row(self, df: pd.DataFrame) -> bool:
        """
        检查第6行（索引为5）是否为策划
        
        Args:
            df: pandas DataFrame
            
        Returns:
            如果第6行包含"策划"则返回True，否则返回False
        """
        try:
            # 检查DataFrame是否有足够的行数（至少6行）
            if len(df) < 6:
                return False
            
            # 获取第6行（索引为5）的所有值
            row_6 = df.iloc[5]  # 第6行，索引为5
            
            # 检查第6行的任何单元格是否包含"策划"
            for value in row_6:
                if pd.notna(value):
                    text = str(value).strip()
                    if "策划" in text:
                        logger.info(f"第6行检测到策划标识: {text}")
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"检查第7行策划标识失败: {str(e)}")
            return False
    
    def _is_text_content(self, text: str) -> bool:
        """
        判断是否为文本内容，支持中文和越南文，跳过纯英文
        
        Args:
            text: 待判断的文本
            
        Returns:
            是否为文本内容
        """
        if not text or len(text.strip()) == 0:
            return False
        
        # 跳过纯数字
        if text.isdigit():
            return False
        
        # 跳过纯日期格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
            return False
        
        # 跳过纯时间格式
        if re.match(r'^\d{2}:\d{2}:\d{2}$', text):
            return False
        
        # 跳过纯浮点数
        try:
            float(text)
            return False
        except ValueError:
            pass
        
        # 跳过数值表达式（如：1+2, 3*4, 5-6等）
        if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', text):
            return False
        
        # 跳过数组格式（如：[1,2,3], {1,2,3}, (1,2,3)等）
        if re.match(r'^[\[\{\(][\d\s,\.]+\]?\}?\)?$', text):
            return False
        
        # 跳过JSON数组格式（如：["a","b"], [1,2,3]等）
        if re.match(r'^\[[\s\S]*\]$', text) and not re.search(r'[\u4e00-\u9fff\u1e00-\u1eff\u1f00-\u1fff\u0100-\u017f\u0180-\u024f]', text):
            return False
        
        # 跳过对象格式（如：{"a":1}, {1,2,3}等）
        if re.match(r'^\{[\s\S]*\}$', text) and not re.search(r'[\u4e00-\u9fff\u1e00-\u1eff\u1f00-\u1fff\u0100-\u017f\u0180-\u024f]', text):
            return False
        
        # 跳过纯数值列表（如：1,2,3 或 1;2;3 等）
        if re.match(r'^[\d\s,;\.]+$', text):
            return False
        
        # 检查是否包含中文字符
        has_chinese = re.search(r'[\u4e00-\u9fff]', text)
        
        # 检查是否包含越南文字符
        has_vietnamese = re.search(r'[\u1e00-\u1eff\u1f00-\u1fff\u0100-\u017f\u0180-\u024f]', text)
        
        # 检查是否包含英文字符
        has_english = re.search(r'[a-zA-Z]', text)
        
        # 只提取包含中文或越南文的文本，跳过纯英文
        if has_chinese or has_vietnamese:
            return True
        
        # 如果是纯英文，跳过提取
        if has_english and not has_chinese and not has_vietnamese:
            return False
        
        # 包含特殊字符或标点符号（但不包含英文字母）
        if re.search(r'[^\w\s\d]', text) and not has_english:
            return True
        
        return False
    
    def _get_excel_position(self, col_index: int, row_number: int) -> str:
        """
        根据列索引和行号生成Excel物理位置（如F5）
        
        Args:
            col_index: 列索引（从0开始）
            row_number: 行号（从1开始）
            
        Returns:
            Excel物理位置字符串（如F5）
        """
        # 将列索引转换为Excel列字母
        col_letter = self._index_to_excel_column(col_index)
        return f"{col_letter}{row_number}"
    
    def _index_to_excel_column(self, index: int) -> str:
        """
        将数字索引转换为Excel列字母
        
        Args:
            index: 列索引（从0开始）
            
        Returns:
            Excel列字母（如A, B, C, ..., Z, AA, AB等）
        """
        result = ""
        while index >= 0:
            result = chr(index % 26 + ord('A')) + result
            index = index // 26 - 1
        return result
    
    def _get_original_field_name(self, column_index: int, headers: List[str]) -> str:
        """
        根据列索引获取原Excel第五行的字段名
        
        Args:
            column_index: 列索引（从0开始）
            headers: 原Excel第五行的字段名列表
            
        Returns:
            对应的字段名
        """
        if headers and 0 <= column_index < len(headers):
            return headers[column_index]
        else:
            # 如果索引超出范围，返回默认的列名
            return f"Column_{column_index + 1}"
    
    def create_text_excel(self, output_path: str, extracted_data: Dict[str, Dict], 
                         source_file: str) -> bool:
        """
        创建包含提取文本的新Excel文件
        
        Args:
            output_path: 输出文件路径
            extracted_data: 提取的文本数据
            source_file: 源文件路径
            
        Returns:
            是否创建成功
        """
        try:
            logger.info(f"正在创建文本Excel文件: {output_path}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 创建汇总工作表
                summary_data = self._create_summary_data(extracted_data, source_file)
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="提取汇总", index=False)
                
                # 为每个工作表创建文本列表
                for sheet_name, sheet_data in extracted_data.items():
                    if sheet_data and sheet_data['items']:
                        # 清理工作表名称
                        clean_sheet_name = self._clean_sheet_name(sheet_name)
                        
                        # 获取字段名（第5行内容）
                        headers = sheet_data['headers']
                        a_column = sheet_data['a_column']
                        
                        # 创建新的数据结构，参考用户提供的格式
                        # A列：id（原文件的A列内容）
                        # B列：位置（提取文本在Excel的行号，如B4）
                        # C列：字段名（原Excel第五行的字段名）
                        # D列：doc（文本类型或描述）
                        # E列：name（提取的文本内容）
                        text_data = []
                        
                        # 第一行：字段名（参考用户格式）
                        header_row = {
                            'id': headers[0] if headers else a_column,  # A列：原字段名
                            '位置': '位置',  # B列：位置标题
                            '字段名': '字段名',  # C列：字段名标题
                            'doc': 'doc',  # D列：doc标题
                            'name': 'name'  # E列：name标题
                        }
                        text_data.append(header_row)
                        
                        # 数据行
                        for item in sheet_data['items']:
                            # 获取该文本对应的原Excel第五行字段名
                            original_field_name = self._get_original_field_name(item['column_index'], headers)
                            
                            data_row = {
                                'id': item['a_column'],  # A列：原文件的A列内容
                                '位置': item['excel_row_ref'],  # B列：Excel行号引用（如B4）
                                '字段名': original_field_name,  # C列：原Excel第五行字段名
                                'doc': self._analyze_text_type(item['text']),  # D列：文本类型分析
                                'name': item['text']  # E列：提取的文本内容
                            }
                            text_data.append(data_row)
                        
                        # 创建DataFrame
                        text_df = pd.DataFrame(text_data)
                        text_df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
            
            logger.info(f"文本Excel文件创建成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建文本Excel文件失败: {str(e)}")
            return False
    
    def _create_summary_data(self, extracted_data: Dict[str, Dict], 
                           source_file: str) -> List[Dict]:
        """
        创建汇总数据
        
        Args:
            extracted_data: 提取的文本数据
            source_file: 源文件路径
            
        Returns:
            汇总数据列表
        """
        summary_data = []
        
        # 基本信息
        summary_data.append({
            '项目': '源文件',
            '值': os.path.basename(source_file)
        })
        
        summary_data.append({
            '项目': '源文件路径',
            '值': source_file
        })
        
        summary_data.append({
            '项目': '工作表数量',
            '值': len(extracted_data)
        })
        
        # 统计信息
        total_texts = sum(len(sheet_data['items']) for sheet_data in extracted_data.values())
        summary_data.append({
            '项目': '提取文本总数',
            '值': total_texts
        })
        
        # 各工作表统计
        for sheet_name, sheet_data in extracted_data.items():
            summary_data.append({
                '项目': f"工作表 '{sheet_name}' 文本数",
                '值': len(sheet_data['items']) if sheet_data else 0
            })
        
        return summary_data
    
    def _clean_sheet_name(self, name: str) -> str:
        """
        清理工作表名称
        
        Args:
            name: 原始名称
            
        Returns:
            清理后的名称
        """
        # Excel工作表名称不能包含的字符
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        
        clean_name = name
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        
        # 移除首尾空格
        clean_name = clean_name.strip()
        
        # 限制长度
        if len(clean_name) > 31:
            clean_name = clean_name[:31]
        
        # 如果为空，使用默认名称
        if not clean_name:
            clean_name = "文本数据"
        
        return clean_name
    
    def _analyze_text_type(self, text: str) -> str:
        """
        分析文本类型，支持中文和越南文，跳过纯英文
        
        Args:
            text: 文本内容
            
        Returns:
            文本类型描述
        """
        has_chinese = re.search(r'[\u4e00-\u9fff]', text)
        has_vietnamese = re.search(r'[\u1e00-\u1eff\u1f00-\u1fff\u0100-\u017f\u0180-\u024f]', text)
        has_english = re.search(r'[a-zA-Z]', text)
        
        if has_chinese and has_vietnamese:
            return "中越混合"
        elif has_chinese and has_english:
            return "中英混合"
        elif has_vietnamese and has_english:
            return "越英混合"
        elif has_chinese:
            return "中文"
        elif has_vietnamese:
            return "越南文"
        else:
            # 由于跳过了纯英文，这里不会返回"英文"类型
            return "其他"
    
    def process_directory(self, input_directory: str, output_directory: str = None) -> bool:
        """
        处理目录中的所有Excel文件
        
        Args:
            input_directory: 输入目录路径
            output_directory: 输出目录路径（默认为输入目录）
            
        Returns:
            是否处理成功
        """
        try:
            # 设置输出目录
            if output_directory is None:
                output_directory = input_directory
            
            # 确保输出目录存在
            os.makedirs(output_directory, exist_ok=True)
            
            # 扫描Excel文件
            excel_files = self.scan_directory(input_directory)
            self.processing_stats['total_files'] = len(excel_files)
            
            if not excel_files:
                logger.warning("未找到Excel文件")
                return True
            
            processed_files = []
            failed_files = []
            
            # 处理每个Excel文件
            for i, file_path in enumerate(excel_files, 1):
                try:
                    # 提取文本
                    extracted_data = self.extract_text_from_excel(file_path, i, len(excel_files))
                    
                    # 检查是否提取到内容
                    total_texts = sum(len(sheet_data['items']) for sheet_data in extracted_data.values()) if extracted_data else 0
                    
                    if extracted_data and total_texts > 0:
                        # 生成输出文件名
                        base_name = Path(file_path).stem
                        output_filename = f"{base_name}.xlsx"
                        output_path = os.path.join(output_directory, output_filename)
                        
                        filename = os.path.basename(file_path)
                        self._report_progress(i, len(excel_files), filename, f"创建输出文件: {output_filename}")
                        
                        # 创建文本Excel文件
                        success = self.create_text_excel(output_path, extracted_data, file_path)
                        
                        if success:
                            processed_files.append(output_path)
                            self.processing_stats['processed_files'] += 1
                            self._report_progress(i, len(excel_files), filename, "处理成功")
                            logger.info(f"处理成功: {output_path}")
                        else:
                            failed_files.append(file_path)
                            self.processing_stats['failed_files'] += 1
                            self._report_progress(i, len(excel_files), filename, "创建输出文件失败")
                    else:
                        filename = os.path.basename(file_path)
                        if total_texts == 0:
                            self._report_progress(i, len(excel_files), filename, "未提取到文本内容，跳过文件创建")
                            logger.info(f"未提取到文本内容，跳过文件创建: {file_path}")
                        else:
                            self._report_progress(i, len(excel_files), filename, "未提取到文本内容")
                            logger.warning(f"未提取到文本内容: {file_path}")
                        # 不将空文件添加到失败列表，因为这是正常情况
                
                except Exception as e:
                    filename = os.path.basename(file_path)
                    self._report_progress(i, len(excel_files), filename, f"处理失败: {str(e)}")
                    logger.error(f"处理文件失败 {file_path}: {str(e)}")
                    failed_files.append(file_path)
                    self.processing_stats['failed_files'] += 1
            
            # 显示处理结果
            self._display_processing_results(processed_files, failed_files)
            
            return True
            
        except Exception as e:
            logger.error(f"处理目录失败: {str(e)}")
            return False
    
    def _display_processing_results(self, processed_files: List[str], failed_files: List[str]):
        """
        显示处理结果
        
        Args:
            processed_files: 成功处理的文件列表
            failed_files: 失败的文件列表
        """
        print(f"\n{'='*60}")
        print("Excel文本提取处理报告")
        print(f"{'='*60}")
        print(f"总文件数: {self.processing_stats['total_files']}")
        print(f"成功处理: {len(processed_files)}")
        print(f"处理失败: {len(failed_files)}")
        print(f"提取文本总数: {self.processing_stats['total_texts']}")
        
        if processed_files:
            print(f"\n成功创建的文件:")
            for file_path in processed_files:
                print(f"  ✓ {os.path.basename(file_path)}")
        
        if failed_files:
            print(f"\n处理失败的文件:")
            for file_path in failed_files:
                print(f"  ✗ {os.path.basename(file_path)}")
        
        print(f"{'='*60}")
    
    def get_processing_report(self) -> str:
        """
        获取处理报告
        
        Returns:
            处理报告字符串
        """
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("Excel文本提取处理报告")
        report_lines.append("=" * 50)
        report_lines.append(f"总文件数: {self.processing_stats['total_files']}")
        report_lines.append(f"成功处理: {self.processing_stats['processed_files']}")
        report_lines.append(f"处理失败: {self.processing_stats['failed_files']}")
        report_lines.append(f"提取文本总数: {self.processing_stats['total_texts']}")
        report_lines.append("=" * 50)
        
        return "\n".join(report_lines)


def main():
    """主函数 - 命令行使用示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Excel文本提取器")
    parser.add_argument("input_directory", help="输入目录路径")
    parser.add_argument("--output-directory", help="输出目录路径（默认为输入目录）")
    parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    
    args = parser.parse_args()
    
    # 创建文本提取器实例
    extractor = ExcelTextExtractor()
    
    # 处理目录
    success = extractor.process_directory(
        input_directory=args.input_directory,
        output_directory=args.output_directory
    )
    
    if success:
        print(f"\n[成功] 文本提取完成！")
        print(extractor.get_processing_report())
    else:
        print(f"\n[失败] 文本提取失败！")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
