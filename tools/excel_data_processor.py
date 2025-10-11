#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据处理工具
根据A列内容对Excel数据进行分组和处理
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ExcelDataProcessor:
    """Excel数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.supported_formats = ['.xlsx', '.xls']
        self.consolidated_data = {}
        self.original_columns = []
    
    def read_excel_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        读取Excel文件
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，None表示读取第一个工作表
            
        Returns:
            pandas DataFrame对象
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            logger.info(f"正在读取文件: {file_path}")
            
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"成功读取文件，共 {len(df)} 行，{len(df.columns)} 列")
            return df
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            raise
    
    def process_by_column_a(self, df: pd.DataFrame, group_column: str = None) -> Dict[str, pd.DataFrame]:
        """
        根据A列（或指定列）内容进行数据处理
        
        Args:
            df: 输入的DataFrame
            group_column: 分组列名，默认为第一列
            
        Returns:
            字典，键为分组值，值为对应的DataFrame
        """
        try:
            if df.empty:
                logger.warning("输入数据为空")
                return {}
            
            # 确定分组列
            if group_column is None:
                group_column = df.columns[0]  # 使用第一列（A列）
            
            if group_column not in df.columns:
                raise ValueError(f"分组列 '{group_column}' 不存在")
            
            logger.info(f"使用列 '{group_column}' 进行分组")
            
            # 保存原始列名
            self.original_columns = list(df.columns)
            
            # 按分组列进行分组
            grouped = df.groupby(group_column)
            
            # 创建拆分后的数据字典
            split_data = {}
            
            for group_value, group_df in grouped:
                # 确保分组值不为空
                if pd.isna(group_value):
                    group_key = "空值"
                else:
                    group_key = str(group_value)
                
                # 重置索引
                group_df = group_df.reset_index(drop=True)
                split_data[group_key] = group_df
                
                logger.info(f"分组 '{group_key}': {len(group_df)} 行数据")
            
            self.consolidated_data = split_data
            logger.info(f"数据处理完成，共 {len(split_data)} 个分组")
            
            return split_data
            
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            raise
    
    def create_processed_excel(self, output_path: str, 
                                include_summary: bool = True,
                                sheet_prefix: str = "") -> bool:
        """
        创建处理后的Excel文件
        
        Args:
            output_path: 输出文件路径
            include_summary: 是否包含汇总信息
            sheet_prefix: 工作表名称前缀
            
        Returns:
            是否成功创建文件
        """
        try:
            if not self.consolidated_data:
                logger.error("没有可拆分的数据")
                return False
            
            logger.info(f"正在创建处理后的Excel文件: {output_path}")
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                sheet_count = 0
                
                # 写入各个分组的数据
                for group_key, group_df in self.consolidated_data.items():
                    # 清理工作表名称（Excel工作表名称限制）
                    clean_sheet_name = self._clean_sheet_name(f"{sheet_prefix}{group_key}")
                    
                    # 如果工作表名称太长，截断并添加序号
                    if len(clean_sheet_name) > 31:
                        clean_sheet_name = clean_sheet_name[:28] + f"_{sheet_count:03d}"
                    
                    # 写入数据到工作表
                    group_df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
                    sheet_count += 1
                
                # 添加汇总信息工作表
                if include_summary:
                    summary_data = self._create_summary_data()
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name="汇总信息", index=False)
            
            logger.info(f"处理后的Excel文件创建成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建处理后的Excel文件失败: {str(e)}")
            return False
    
    def _clean_sheet_name(self, name: str) -> str:
        """
        清理工作表名称，移除Excel不支持的字符
        
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
        
        # 如果为空，使用默认名称
        if not clean_name:
            clean_name = "数据"
        
        return clean_name
    
    def _create_summary_data(self) -> List[Dict]:
        """
        创建汇总信息数据
        
        Returns:
            汇总信息列表
        """
        summary_data = []
        
        # 添加基本信息
        summary_data.append({
            "项目": "总分组数",
            "值": len(self.consolidated_data)
        })
        
        summary_data.append({
            "项目": "原始列数",
            "值": len(self.original_columns)
        })
        
        # 添加各分组统计信息
        total_rows = 0
        for group_key, group_df in self.consolidated_data.items():
            row_count = len(group_df)
            total_rows += row_count
            
            summary_data.append({
                "项目": f"分组 '{group_key}' 行数",
                "值": row_count
            })
        
        summary_data.append({
            "项目": "总行数",
            "值": total_rows
        })
        
        return summary_data
    
    def get_process_report(self) -> str:
        """
        获取处理报告
        
        Returns:
            拆分报告字符串
        """
        if not self.consolidated_data:
            return "没有可拆分的数据"
        
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("Excel数据处理报告")
        report_lines.append("=" * 50)
        report_lines.append(f"总分组数: {len(self.consolidated_data)}")
        report_lines.append(f"原始列数: {len(self.original_columns)}")
        report_lines.append("")
        
        total_rows = 0
        for group_key, group_df in self.consolidated_data.items():
            row_count = len(group_df)
            total_rows += row_count
            report_lines.append(f"分组 '{group_key}': {row_count} 行")
        
        report_lines.append("")
        report_lines.append(f"总行数: {total_rows}")
        report_lines.append("=" * 50)
        
        return "\n".join(report_lines)
    
    def _generate_filename_from_data(self, df: pd.DataFrame, group_column: str = None) -> str:
        """
        根据A列内容生成文件名
        
        Args:
            df: DataFrame数据
            group_column: 分组列名
            
        Returns:
            生成的文件名
        """
        try:
            if df.empty:
                return "处理结果.xlsx"
            
            # 确定分组列
            if group_column is None:
                group_column = df.columns[0]  # 使用第一列（A列）
            
            if group_column not in df.columns:
                return "处理结果.xlsx"
            
            # 获取A列的唯一值
            unique_values = df[group_column].unique()
            
            if len(unique_values) == 0:
                return "处理结果.xlsx"
            
            # 如果只有一个唯一值，使用该值作为文件名
            if len(unique_values) == 1:
                filename = str(unique_values[0])
            else:
                # 如果有多个唯一值，使用第一个值
                filename = str(unique_values[0])
            
            # 清理文件名，移除不合法字符
            filename = self._clean_filename(filename)
            
            # 确保文件名不为空
            if not filename:
                filename = "拆分结果"
            
            # 添加扩展名
            if not filename.endswith('.xlsx'):
                filename += ".xlsx"
            
            logger.info(f"自动生成文件名: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"生成文件名失败: {str(e)}")
            return "处理结果.xlsx"
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名，移除不合法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # Windows文件名不能包含的字符
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        
        clean_name = filename
        for char in invalid_chars:
            clean_name = clean_name.replace(char, '_')
        
        # 移除首尾空格和点
        clean_name = clean_name.strip(' .')
        
        # 限制长度（Windows文件名限制）
        if len(clean_name) > 200:  # 留一些余量
            clean_name = clean_name[:200]
        
        return clean_name
    
    def process_file(self, input_path: str, output_folder: str, output_filename: str = None,
                    group_column: str = None, 
                    include_summary: bool = True,
                    sheet_prefix: str = "",
                    auto_filename_from_column: bool = True,
                    skip_duplicates: bool = True,
                    separate_files: bool = True) -> bool:
        """
        处理单个Excel文件的完整流程
        
        Args:
            input_path: 输入文件路径
            output_folder: 输出文件夹路径
            output_filename: 输出文件名（如果为None且auto_filename_from_column为True，则使用A列内容）
            group_column: 分组列名
            include_summary: 是否包含汇总信息
            sheet_prefix: 工作表名称前缀
            auto_filename_from_column: 是否使用A列内容自动生成文件名
            skip_duplicates: 是否跳过重复文件
            separate_files: 是否为每个分组创建单独的Excel文件
            
        Returns:
            是否处理成功
        """
        try:
            # 读取Excel文件
            df = self.read_excel_file(input_path)
            
            # 处理数据
            self.process_by_column_a(df, group_column)
            
            if separate_files:
                # 为每个分组创建单独的Excel文件
                return self._create_separate_files(output_folder, skip_duplicates, include_summary, sheet_prefix)
            else:
                # 创建单个拆分的Excel文件（原有逻辑）
                return self._create_single_file(output_folder, output_filename, skip_duplicates, include_summary, sheet_prefix, auto_filename_from_column)
            
        except Exception as e:
            logger.error(f"处理文件失败: {str(e)}")
            return False
    
    def _create_separate_files(self, output_folder: str, skip_duplicates: bool, 
                              include_summary: bool, sheet_prefix: str) -> bool:
        """
        为每个分组创建单独的Excel文件
        
        Args:
            output_folder: 输出文件夹路径
            skip_duplicates: 是否跳过重复文件
            include_summary: 是否包含汇总信息
            sheet_prefix: 工作表名称前缀
            
        Returns:
            是否处理成功
        """
        try:
            created_files = []
            skipped_files = []
            
            for group_key, group_df in self.consolidated_data.items():
                # 生成文件名
                filename = self._clean_filename(str(group_key))
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                
                # 构建完整路径
                output_path = os.path.join(output_folder, filename)
                
                # 检查重复文件
                if skip_duplicates and os.path.exists(output_path):
                    logger.info(f"文件已存在，跳过: {output_path}")
                    print(f"[跳过] 文件已存在: {output_path}")
                    skipped_files.append(output_path)
                    continue
                
                # 创建单独的Excel文件
                success = self._create_single_group_file(output_path, group_df, group_key, include_summary)
                
                if success:
                    created_files.append(output_path)
                    logger.info(f"创建文件成功: {output_path}")
                else:
                    logger.error(f"创建文件失败: {output_path}")
                    return False
            
            # 显示处理结果
            print(f"\n[完成] 文件处理完成！")
            print(f"创建文件数: {len(created_files)}")
            print(f"跳过文件数: {len(skipped_files)}")
            
            if created_files:
                print(f"\n创建的文件:")
                for file_path in created_files:
                    print(f"  - {os.path.basename(file_path)}")
            
            if skipped_files:
                print(f"\n跳过的文件:")
                for file_path in skipped_files:
                    print(f"  - {os.path.basename(file_path)}")
            
            return True
            
        except Exception as e:
            logger.error(f"创建单独文件失败: {str(e)}")
            return False
    
    def _create_single_group_file(self, output_path: str, group_df: pd.DataFrame, 
                                 group_key: str, include_summary: bool) -> bool:
        """
        创建单个分组的Excel文件
        
        Args:
            output_path: 输出文件路径
            group_df: 分组数据
            group_key: 分组键名
            include_summary: 是否包含汇总信息
            
        Returns:
            是否创建成功
        """
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 写入分组数据
                group_df.to_excel(writer, sheet_name="数据", index=False)
                
                # 添加汇总信息
                if include_summary:
                    summary_data = [
                        {"项目": "分组名称", "值": group_key},
                        {"项目": "数据行数", "值": len(group_df)},
                        {"项目": "数据列数", "值": len(group_df.columns)},
                        {"项目": "列名", "值": ", ".join(group_df.columns)}
                    ]
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name="汇总信息", index=False)
            
            return True
            
        except Exception as e:
            logger.error(f"创建单个分组文件失败: {str(e)}")
            return False
    
    def _create_single_file(self, output_folder: str, output_filename: str, 
                           skip_duplicates: bool, include_summary: bool, 
                           sheet_prefix: str, auto_filename_from_column: bool) -> bool:
        """
        创建单个拆分的Excel文件（原有逻辑）
        
        Args:
            output_folder: 输出文件夹路径
            output_filename: 输出文件名
            skip_duplicates: 是否跳过重复文件
            include_summary: 是否包含汇总信息
            sheet_prefix: 工作表名称前缀
            auto_filename_from_column: 是否使用A列内容自动生成文件名
            
        Returns:
            是否处理成功
        """
        try:
            # 确定输出文件名
            if output_filename is None and auto_filename_from_column:
                # 使用第一个分组的数据来生成文件名
                if self.consolidated_data:
                    first_group_key = list(self.consolidated_data.keys())[0]
                    output_filename = self._clean_filename(str(first_group_key))
                    if not output_filename.endswith('.xlsx'):
                        output_filename += '.xlsx'
                else:
                    output_filename = "处理结果.xlsx"
            
            if output_filename is None:
                output_filename = "处理结果.xlsx"
            
            # 构建完整的输出文件路径
            output_path = os.path.join(output_folder, output_filename)
            
            # 检查重复文件
            if skip_duplicates and os.path.exists(output_path):
                logger.info(f"文件已存在，跳过: {output_path}")
                print(f"[跳过] 文件已存在: {output_path}")
                return True
            
            # 创建处理后的Excel文件
            success = self.create_processed_excel(output_path, include_summary, sheet_prefix)
            
            if success:
                logger.info("文件处理完成")
                print(self.get_process_report())
            
            return success
            
        except Exception as e:
            logger.error(f"创建单个文件失败: {str(e)}")
            return False


def main():
    """主函数 - 命令行使用示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Excel数据处理工具")
    parser.add_argument("input_file", help="输入Excel文件路径")
    parser.add_argument("output_folder", help="输出文件夹路径")
    parser.add_argument("--output-filename", help="输出文件名（留空则使用A列内容自动生成）")
    parser.add_argument("--group-column", help="分组列名（默认为第一列）")
    parser.add_argument("--no-summary", action="store_true", help="不包含汇总信息")
    parser.add_argument("--sheet-prefix", default="", help="工作表名称前缀")
    parser.add_argument("--no-auto-filename", action="store_true", help="不使用A列内容自动生成文件名")
    parser.add_argument("--no-skip-duplicates", action="store_true", help="不跳过重复文件")
    parser.add_argument("--single-file", action="store_true", help="创建单个拆分文件（默认创建多个单独文件）")
    
    args = parser.parse_args()
    
    # 创建数据处理器实例
    processor = ExcelDataProcessor()
    
    # 处理文件
    success = processor.process_file(
        input_path=args.input_file,
        output_folder=args.output_folder,
        output_filename=args.output_filename,
        group_column=args.group_column,
        include_summary=not args.no_summary,
        sheet_prefix=args.sheet_prefix,
        auto_filename_from_column=not args.no_auto_filename,
        skip_duplicates=not args.no_skip_duplicates,
        separate_files=not args.single_file
    )
    
    if success:
        print(f"\n[成功] 文件处理成功！")
        print(f"输入文件: {args.input_file}")
        print(f"输出文件夹: {args.output_folder}")
        print(f"输出文件名: {args.output_filename}")
    else:
        print(f"\n[失败] 文件处理失败！")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
