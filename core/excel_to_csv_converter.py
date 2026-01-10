#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel转CSV转换器
将Excel文件转换为CSV格式，保持内容不丢失
支持多工作表、特殊字符、多行文本等
"""

import os
import csv
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
import pandas as pd

# 尝试导入openpyxl
try:
    from openpyxl import load_workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExcelToCsvConverter:
    """Excel转CSV转换器 - 保持内容完整性"""
    
    # 支持的编码格式
    SUPPORTED_ENCODINGS = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
    
    def __init__(self):
        """初始化转换器"""
        self.supported_extensions = {'.xlsx', '.xls'}
        
        # 处理统计
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'success_files': 0,
            'failed_files': 0,
            'total_sheets': 0,
            'total_rows': 0
        }
        
        # 错误日志
        self.error_logs = []
        
        # 进度回调
        self.progress_callback = None
        
        # 转换结果
        self.conversion_results = []
    
    def set_progress_callback(self, callback: Callable[[str, Optional[float]], None]):
        """
        设置进度回调函数
        
        Args:
            callback: 回调函数，接收 (message, percentage) 参数
        """
        self.progress_callback = callback
    
    def _report_progress(self, message: str, percentage: float = None):
        """统一进度报告"""
        logger.info(message)
        if self.progress_callback:
            self.progress_callback(message, percentage)
    
    def _reset_stats(self):
        """重置统计信息"""
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'success_files': 0,
            'failed_files': 0,
            'total_sheets': 0,
            'total_rows': 0
        }
        self.error_logs = []
        self.conversion_results = []
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        获取Excel文件中的所有工作表名称
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            工作表名称列表
        """
        try:
            xl = pd.ExcelFile(file_path)
            return xl.sheet_names
        except Exception as e:
            logger.error(f"获取工作表名称失败: {str(e)}")
            return []
    
    def convert_excel_to_csv(
        self,
        excel_path: str,
        output_dir: str = None,
        encoding: str = 'utf-8-sig',
        sheet_names: List[str] = None,
        merge_sheets: bool = False,
        include_sheet_column: bool = True,
        delimiter: str = ',',
        quoting: int = csv.QUOTE_ALL,
        preserve_empty_rows: bool = True,
        add_bom: bool = True
    ) -> Dict:
        """
        将单个Excel文件转换为CSV
        
        Args:
            excel_path: Excel文件路径
            output_dir: 输出目录，默认与Excel文件同目录
            encoding: 输出编码，默认utf-8-sig（带BOM，兼容Excel打开）
            sheet_names: 要转换的工作表名称列表，None表示全部
            merge_sheets: 是否合并所有工作表到一个CSV
            include_sheet_column: 合并时是否包含工作表名称列
            delimiter: CSV分隔符
            quoting: 引用模式 (csv.QUOTE_ALL, csv.QUOTE_MINIMAL等)
            preserve_empty_rows: 是否保留空行
            add_bom: 是否添加BOM（针对UTF-8编码）
            
        Returns:
            转换结果字典
        """
        result = {
            'success': False,
            'source_file': excel_path,
            'output_files': [],
            'sheets_processed': 0,
            'total_rows': 0,
            'error': None
        }
        
        try:
            # 检查文件是否存在
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"文件不存在: {excel_path}")
            
            # 检查文件扩展名
            file_ext = Path(excel_path).suffix.lower()
            if file_ext not in self.supported_extensions:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 确定输出目录
            if output_dir is None:
                output_dir = os.path.dirname(excel_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取文件名（不含扩展名）
            file_stem = Path(excel_path).stem
            
            # 读取Excel文件
            self._report_progress(f"正在读取: {excel_path}")
            
            xl = pd.ExcelFile(excel_path)
            all_sheet_names = xl.sheet_names
            
            # 确定要处理的工作表
            if sheet_names is None:
                sheets_to_process = all_sheet_names
            else:
                sheets_to_process = [s for s in sheet_names if s in all_sheet_names]
                if not sheets_to_process:
                    raise ValueError(f"指定的工作表均不存在: {sheet_names}")
            
            self._report_progress(f"找到 {len(sheets_to_process)} 个工作表")
            
            if merge_sheets:
                # 合并所有工作表到一个CSV
                output_file = self._convert_merged_sheets(
                    xl, sheets_to_process, file_stem, output_dir,
                    encoding, delimiter, quoting, include_sheet_column,
                    preserve_empty_rows, add_bom
                )
                result['output_files'].append(output_file)
            else:
                # 每个工作表单独输出CSV
                for sheet_name in sheets_to_process:
                    output_file = self._convert_single_sheet(
                        xl, sheet_name, file_stem, output_dir,
                        encoding, delimiter, quoting,
                        preserve_empty_rows, add_bom,
                        len(sheets_to_process) > 1
                    )
                    result['output_files'].append(output_file)
                    result['total_rows'] += output_file['rows']
            
            result['sheets_processed'] = len(sheets_to_process)
            result['success'] = True
            
            self._report_progress(f"✅ 转换完成: {excel_path}")
            
        except Exception as e:
            result['error'] = str(e)
            self.error_logs.append({
                'file': excel_path,
                'error': str(e)
            })
            self._report_progress(f"❌ 转换失败: {excel_path} - {str(e)}")
        
        return result
    
    def _convert_single_sheet(
        self,
        xl: pd.ExcelFile,
        sheet_name: str,
        file_stem: str,
        output_dir: str,
        encoding: str,
        delimiter: str,
        quoting: int,
        preserve_empty_rows: bool,
        add_bom: bool,
        include_sheet_in_name: bool
    ) -> Dict:
        """转换单个工作表"""
        result = {
            'sheet_name': sheet_name,
            'file_path': '',
            'rows': 0
        }
        
        # 读取工作表数据，保持原始格式
        # 使用 dtype=str 确保所有数据以字符串形式读取，避免数据类型转换导致的丢失
        df = pd.read_excel(
            xl, 
            sheet_name=sheet_name, 
            dtype=str,
            header=None,  # 不将第一行作为标题，保留完整数据
            na_filter=False  # 不将空值转换为NaN
        )
        
        # 生成输出文件名
        if include_sheet_in_name:
            # 清理工作表名称中的非法字符
            safe_sheet_name = self._sanitize_filename(sheet_name)
            output_filename = f"{file_stem}_{safe_sheet_name}.csv"
        else:
            output_filename = f"{file_stem}.csv"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # 处理空行
        if not preserve_empty_rows:
            # 移除全空行
            df = df.dropna(how='all')
        
        # 写入CSV
        self._write_csv(df, output_path, encoding, delimiter, quoting, add_bom)
        
        result['file_path'] = output_path
        result['rows'] = len(df)
        
        self._report_progress(f"  工作表 '{sheet_name}': {len(df)} 行 -> {output_filename}")
        
        return result
    
    def _convert_merged_sheets(
        self,
        xl: pd.ExcelFile,
        sheet_names: List[str],
        file_stem: str,
        output_dir: str,
        encoding: str,
        delimiter: str,
        quoting: int,
        include_sheet_column: bool,
        preserve_empty_rows: bool,
        add_bom: bool
    ) -> Dict:
        """合并多个工作表到一个CSV"""
        result = {
            'sheet_name': '合并',
            'file_path': '',
            'rows': 0,
            'sheets_merged': sheet_names
        }
        
        merged_data = []
        max_columns = 0
        
        for sheet_name in sheet_names:
            # 读取工作表
            df = pd.read_excel(
                xl, 
                sheet_name=sheet_name, 
                dtype=str,
                header=None,
                na_filter=False
            )
            
            if not preserve_empty_rows:
                df = df.dropna(how='all')
            
            # 记录最大列数
            max_columns = max(max_columns, len(df.columns))
            
            # 添加工作表名称列
            if include_sheet_column:
                df.insert(0, '_Sheet', sheet_name)
            
            merged_data.append(df)
        
        # 合并所有数据
        if merged_data:
            merged_df = pd.concat(merged_data, ignore_index=True)
        else:
            merged_df = pd.DataFrame()
        
        # 生成输出文件名
        output_filename = f"{file_stem}_merged.csv"
        output_path = os.path.join(output_dir, output_filename)
        
        # 写入CSV
        self._write_csv(merged_df, output_path, encoding, delimiter, quoting, add_bom)
        
        result['file_path'] = output_path
        result['rows'] = len(merged_df)
        
        self._report_progress(f"  合并 {len(sheet_names)} 个工作表: {len(merged_df)} 行 -> {output_filename}")
        
        return result
    
    def _write_csv(
        self,
        df: pd.DataFrame,
        output_path: str,
        encoding: str,
        delimiter: str,
        quoting: int,
        add_bom: bool
    ):
        """写入CSV文件，确保内容完整"""
        # 选择编码
        actual_encoding = encoding
        if add_bom and encoding.lower() in ['utf-8', 'utf8']:
            actual_encoding = 'utf-8-sig'
        
        # 写入CSV
        df.to_csv(
            output_path,
            index=False,
            header=False,  # 数据已包含原始表头
            encoding=actual_encoding,
            sep=delimiter,
            quoting=quoting,
            quotechar='"',
            escapechar='\\',
            lineterminator='\n'
        )
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名中的非法字符"""
        # Windows文件名非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            name = name.replace(char, '_')
        return name.strip()
    
    def batch_convert(
        self,
        source_path: str,
        output_dir: str = None,
        recursive: bool = False,
        encoding: str = 'utf-8-sig',
        merge_sheets: bool = False,
        include_sheet_column: bool = True,
        delimiter: str = ',',
        preserve_empty_rows: bool = True
    ) -> Dict:
        """
        批量转换Excel文件为CSV
        
        Args:
            source_path: 源路径（文件或目录）
            output_dir: 输出目录
            recursive: 是否递归处理子目录
            encoding: 输出编码
            merge_sheets: 是否合并工作表
            include_sheet_column: 合并时是否包含工作表列
            delimiter: CSV分隔符
            preserve_empty_rows: 是否保留空行
            
        Returns:
            批量转换结果
        """
        self._reset_stats()
        
        results = {
            'success': True,
            'files': [],
            'summary': {}
        }
        
        # 收集要处理的文件
        excel_files = []
        
        if os.path.isfile(source_path):
            # 单个文件
            if Path(source_path).suffix.lower() in self.supported_extensions:
                excel_files.append(source_path)
        elif os.path.isdir(source_path):
            # 目录
            if recursive:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        if Path(file).suffix.lower() in self.supported_extensions:
                            excel_files.append(os.path.join(root, file))
            else:
                for file in os.listdir(source_path):
                    if Path(file).suffix.lower() in self.supported_extensions:
                        excel_files.append(os.path.join(source_path, file))
        
        if not excel_files:
            self._report_progress("未找到Excel文件")
            results['success'] = False
            results['summary'] = self.processing_stats
            return results
        
        self.processing_stats['total_files'] = len(excel_files)
        self._report_progress(f"找到 {len(excel_files)} 个Excel文件")
        
        # 确定输出目录
        if output_dir is None:
            if os.path.isfile(source_path):
                output_dir = os.path.dirname(source_path)
            else:
                output_dir = source_path
        
        # 处理每个文件
        for i, excel_file in enumerate(excel_files):
            progress = (i + 1) / len(excel_files) * 100
            self._report_progress(f"处理 ({i+1}/{len(excel_files)}): {os.path.basename(excel_file)}", progress)
            
            # 确定相对输出路径
            if os.path.isdir(source_path) and recursive:
                rel_path = os.path.relpath(os.path.dirname(excel_file), source_path)
                file_output_dir = os.path.join(output_dir, rel_path)
            else:
                file_output_dir = output_dir
            
            result = self.convert_excel_to_csv(
                excel_file,
                output_dir=file_output_dir,
                encoding=encoding,
                merge_sheets=merge_sheets,
                include_sheet_column=include_sheet_column,
                delimiter=delimiter,
                preserve_empty_rows=preserve_empty_rows
            )
            
            results['files'].append(result)
            self.processing_stats['processed_files'] += 1
            
            if result['success']:
                self.processing_stats['success_files'] += 1
                self.processing_stats['total_sheets'] += result['sheets_processed']
                self.processing_stats['total_rows'] += result['total_rows']
            else:
                self.processing_stats['failed_files'] += 1
        
        results['summary'] = self.processing_stats.copy()
        results['errors'] = self.error_logs.copy()
        
        self._report_progress(
            f"\n转换完成! 成功: {self.processing_stats['success_files']}, "
            f"失败: {self.processing_stats['failed_files']}, "
            f"共 {self.processing_stats['total_rows']} 行"
        )
        
        return results
    
    def get_stats(self) -> Dict:
        """获取处理统计信息"""
        return self.processing_stats.copy()
    
    def get_errors(self) -> List[Dict]:
        """获取错误日志"""
        return self.error_logs.copy()


# 便捷函数
def convert_excel_to_csv(excel_path: str, output_dir: str = None, **kwargs) -> Dict:
    """便捷函数：转换单个Excel文件为CSV"""
    converter = ExcelToCsvConverter()
    return converter.convert_excel_to_csv(excel_path, output_dir, **kwargs)


def batch_convert_excel_to_csv(source_path: str, output_dir: str = None, **kwargs) -> Dict:
    """便捷函数：批量转换Excel文件为CSV"""
    converter = ExcelToCsvConverter()
    return converter.batch_convert(source_path, output_dir, **kwargs)


if __name__ == '__main__':
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        
        converter = ExcelToCsvConverter()
        converter.set_progress_callback(lambda msg, pct: print(msg))
        
        result = converter.batch_convert(source, output)
        
        print("\n处理结果:")
        print(f"  总文件数: {result['summary']['total_files']}")
        print(f"  成功: {result['summary']['success_files']}")
        print(f"  失败: {result['summary']['failed_files']}")
        print(f"  总行数: {result['summary']['total_rows']}")
    else:
        print("用法: python excel_to_csv_converter.py <Excel文件或目录> [输出目录]")
