#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨项目翻译对应工具
根据Excel表格中的B列（表格名）和C列（表内位置）查找对应的内容
"""

import os
import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CrossProjectTranslator:
    """跨项目翻译对应工具"""
    
    def __init__(self):
        """初始化翻译对应工具"""
        self.supported_formats = ['.xlsx', '.xls']
        self.project_files = {}  # 存储项目文件缓存
        self.translation_results = []
    
    def parse_cell_reference(self, cell_ref: str) -> Tuple[int, int]:
        """
        解析Excel单元格引用（如A1, B5, C10等）
        
        Args:
            cell_ref: Excel单元格引用字符串
            
        Returns:
            (row, col): 行号和列号的元组
        """
        try:
            # 使用正则表达式解析单元格引用
            match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
            if not match:
                raise ValueError(f"无效的单元格引用格式: {cell_ref}")
            
            col_str, row_str = match.groups()
            
            # 将列字母转换为数字
            col_num = 0
            for char in col_str:
                col_num = col_num * 26 + (ord(char) - ord('A') + 1)
            
            row_num = int(row_str)
            
            return row_num, col_num
            
        except Exception as e:
            logger.error(f"解析单元格引用失败 {cell_ref}: {e}")
            return None, None
    
    def load_project_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        加载项目文件并缓存
        
        Args:
            file_path: 项目文件路径
            
        Returns:
            字典，键为工作表名，值为DataFrame
        """
        try:
            if file_path in self.project_files:
                return self.project_files[file_path]
            
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return {}
            
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheets_data[sheet_name] = df
                    logger.info(f"成功加载工作表: {sheet_name} ({len(df)} 行)")
                except Exception as e:
                    logger.error(f"加载工作表失败 {sheet_name}: {e}")
                    continue
            
            # 缓存文件数据
            self.project_files[file_path] = sheets_data
            return sheets_data
            
        except Exception as e:
            logger.error(f"加载项目文件失败 {file_path}: {e}")
            return {}
    
    def find_content_by_reference(self, sheets_data: Dict[str, pd.DataFrame], 
                                 sheet_name: str, cell_ref: str) -> Optional[str]:
        """
        根据工作表名和单元格引用查找内容
        
        Args:
            sheets_data: 工作表数据字典
            sheet_name: 工作表名称
            cell_ref: 单元格引用（如A1, B5等）
            
        Returns:
            找到的内容，如果未找到返回None
        """
        try:
            # 检查工作表是否存在
            if sheet_name not in sheets_data:
                logger.warning(f"工作表不存在: {sheet_name}")
                return None
            
            df = sheets_data[sheet_name]
            
            # 解析单元格引用
            row_num, col_num = self.parse_cell_reference(cell_ref)
            if row_num is None or col_num is None:
                return None
            
            # 转换为pandas索引（从0开始）
            row_idx = row_num - 1
            col_idx = col_num - 1
            
            # 检查索引是否在范围内
            if row_idx < 0 or row_idx >= len(df) or col_idx < 0 or col_idx >= len(df.columns):
                logger.warning(f"单元格引用超出范围: {sheet_name}!{cell_ref}")
                return None
            
            # 获取内容
            content = df.iloc[row_idx, col_idx]
            
            # 处理NaN值
            if pd.isna(content):
                return ""
            
            return str(content)
            
        except Exception as e:
            logger.error(f"查找内容失败 {sheet_name}!{cell_ref}: {e}")
            return None
    
    def process_translation_mapping(self, mapping_file: str, project_directory: str) -> List[Dict]:
        """
        处理翻译映射文件
        
        Args:
            mapping_file: 映射文件路径（包含Name列文件名和Description列单元格位置）
            project_directory: 项目文件目录
            
        Returns:
            处理结果列表
        """
        try:
            logger.info(f"开始处理翻译映射文件: {mapping_file}")
            logger.info(f"项目目录: {project_directory}")
            
            # 读取映射文件
            mapping_df = pd.read_excel(mapping_file)
            
            # 检查必要的列（支持多种列名格式）
            file_name_column = None
            position_column = None
            
            # 尝试找到文件名列
            for col in ['文件名列', '文件名', 'Name']:
                if col in mapping_df.columns:
                    file_name_column = col
                    break
            
            # 尝试找到位置列
            for col in ['位置列', '位置', 'Description']:
                if col in mapping_df.columns:
                    position_column = col
                    break
            
            if not file_name_column or not position_column:
                logger.error(f"映射文件缺少必要的列。支持的列名格式：")
                logger.error(f"文件名列: ['文件名列', '文件名', 'Name']")
                logger.error(f"位置列: ['位置列', '位置', 'Description']")
                logger.error(f"当前文件的列名: {list(mapping_df.columns)}")
                return []
            
            results = []
            processed_count = 0
            found_count = 0
            
            # 遍历映射文件的每一行
            for index, row in mapping_df.iterrows():
                try:
                    # 获取文件名和位置
                    file_name = str(row[file_name_column]).strip() if pd.notna(row[file_name_column]) else ""
                    cell_reference = str(row[position_column]).strip() if pd.notna(row[position_column]) else ""
                    
                    if not file_name or not cell_reference:
                        logger.warning(f"第{index+1}行数据不完整，跳过")
                        continue
                    
                    processed_count += 1
                    
                    # 构建项目文件路径
                    project_file_path = os.path.join(project_directory, file_name)
                    
                    # 如果直接路径不存在，尝试查找文件
                    if not os.path.exists(project_file_path):
                        project_file_path = self.find_project_file(project_directory, file_name)
                    
                    if not project_file_path:
                        logger.warning(f"未找到项目文件: {file_name}")
                        results.append({
                            'index': index + 1,
                            'file_name': file_name,
                            'cell_reference': cell_reference,
                            'content': "文件未找到",
                            'status': 'error',
                            'error_message': f"未找到文件: {file_name}"
                        })
                        continue
                    
                    # 加载项目文件
                    sheets_data = self.load_project_file(project_file_path)
                    
                    # 解析表内位置（格式：工作表名!单元格引用 或 直接单元格引用）
                    if '!' in cell_reference:
                        sheet_name, cell_ref = cell_reference.split('!', 1)
                        sheet_name = sheet_name.strip()
                        cell_ref = cell_ref.strip()
                    else:
                        # 如果没有指定工作表，使用第一个工作表
                        sheet_name = list(sheets_data.keys())[0] if sheets_data else ""
                        cell_ref = cell_reference
                    
                    # 查找内容
                    content = self.find_content_by_reference(sheets_data, sheet_name, cell_ref)
                    
                    if content is not None:
                        found_count += 1
                        status = 'success'
                        error_message = ""
                    else:
                        status = 'error'
                        error_message = f"未找到内容: {sheet_name}!{cell_ref}"
                    
                    results.append({
                        'index': index + 1,
                        'file_name': file_name,
                        'cell_reference': cell_reference,
                        'sheet_name': sheet_name,
                        'cell_ref': cell_ref,
                        'content': content if content is not None else "",
                        'status': status,
                        'error_message': error_message,
                        'project_file': project_file_path
                    })
                    
                except Exception as e:
                    logger.error(f"处理第{index+1}行时出错: {e}")
                    results.append({
                        'index': index + 1,
                        'file_name': str(row[file_name_column]) if pd.notna(row[file_name_column]) else "",
                        'cell_reference': str(row[position_column]) if pd.notna(row[position_column]) else "",
                        'content': "",
                        'status': 'error',
                        'error_message': str(e)
                    })
            
            logger.info(f"处理完成: 总行数 {len(mapping_df)}, 处理行数 {processed_count}, 成功找到 {found_count}")
            self.translation_results = results
            return results
            
        except Exception as e:
            logger.error(f"处理翻译映射文件失败: {e}")
            return []
    
    def find_project_file(self, project_directory: str, table_name: str) -> Optional[str]:
        """
        在项目目录中查找指定的表格文件
        
        Args:
            project_directory: 项目目录
            table_name: 表格名称
            
        Returns:
            找到的文件路径，如果未找到返回None
        """
        try:
            # 首先尝试直接匹配
            possible_names = [
                f"{table_name}.xlsx",
                f"{table_name}.xls",
                f"{table_name}.XLSX",
                f"{table_name}.XLS"
            ]
            
            for name in possible_names:
                file_path = os.path.join(project_directory, name)
                if os.path.exists(file_path):
                    return file_path
            
            # 如果直接匹配失败，搜索包含该名称的文件
            for root, dirs, files in os.walk(project_directory):
                for file in files:
                    if file.lower().startswith(table_name.lower()) and file.lower().endswith(('.xlsx', '.xls')):
                        return os.path.join(root, file)
            
            return None
            
        except Exception as e:
            logger.error(f"查找项目文件失败 {table_name}: {e}")
            return None
    
    def export_results(self, output_path: str) -> bool:
        """
        导出处理结果到Excel文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            if not self.translation_results:
                logger.warning("没有结果可导出")
                return False
            
            # 创建结果DataFrame
            results_df = pd.DataFrame(self.translation_results)
            
            # 重新排列列的顺序
            column_order = [
                'index', 'file_name', 'cell_reference', 'sheet_name', 'cell_ref', 
                'content', 'status', 'error_message', 'project_file'
            ]
            
            # 只保留存在的列
            available_columns = [col for col in column_order if col in results_df.columns]
            results_df = results_df[available_columns]
            
            # 重命名列名为中文
            column_names = {
                'index': '序号',
                'file_name': '文件名',
                'cell_reference': '单元格位置',
                'sheet_name': '工作表名',
                'cell_ref': '单元格引用',
                'content': '对应内容',
                'status': '状态',
                'error_message': '错误信息',
                'project_file': '项目文件路径'
            }
            
            results_df = results_df.rename(columns=column_names)
            
            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 写入结果数据
                results_df.to_excel(writer, sheet_name='翻译对应结果', index=False)
                
                # 创建统计信息工作表
                stats_data = self._create_statistics()
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
            
            logger.info(f"结果已导出到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出结果失败: {e}")
            return False
    
    def _create_statistics(self) -> List[Dict]:
        """
        创建统计信息
        
        Returns:
            统计信息列表
        """
        if not self.translation_results:
            return []
        
        total_count = len(self.translation_results)
        success_count = sum(1 for r in self.translation_results if r['status'] == 'success')
        error_count = total_count - success_count
        
        # 按状态分组统计
        status_stats = {}
        for result in self.translation_results:
            status = result['status']
            status_stats[status] = status_stats.get(status, 0) + 1
        
        # 按文件名分组统计
        file_stats = {}
        for result in self.translation_results:
            file_name = result['file_name']
            if file_name not in file_stats:
                file_stats[file_name] = {'total': 0, 'success': 0, 'error': 0}
            file_stats[file_name]['total'] += 1
            if result['status'] == 'success':
                file_stats[file_name]['success'] += 1
            else:
                file_stats[file_name]['error'] += 1
        
        stats = [
            {'项目': '总处理数量', '值': total_count},
            {'项目': '成功找到', '值': success_count},
            {'项目': '处理失败', '值': error_count},
            {'项目': '成功率', '值': f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0%"},
        ]
        
        # 添加状态统计
        for status, count in status_stats.items():
            stats.append({'项目': f'状态-{status}', '值': count})
        
        # 添加文件统计（只显示前10个）
        stats.append({'项目': '---文件统计---', '值': ''})
        for i, (file_name, counts) in enumerate(list(file_stats.items())[:10]):
            stats.append({
                '项目': f'文件-{file_name}',
                '值': f"总计:{counts['total']} 成功:{counts['success']} 失败:{counts['error']}"
            })
        
        return stats
    
    def get_processing_report(self) -> str:
        """
        获取处理报告
        
        Returns:
            处理报告字符串
        """
        if not self.translation_results:
            return "没有处理结果"
        
        total_count = len(self.translation_results)
        success_count = sum(1 for r in self.translation_results if r['status'] == 'success')
        error_count = total_count - success_count
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("跨项目翻译对应处理报告")
        report_lines.append("=" * 60)
        report_lines.append(f"总处理数量: {total_count}")
        report_lines.append(f"成功找到: {success_count}")
        report_lines.append(f"处理失败: {error_count}")
        report_lines.append(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        report_lines.append("=" * 60)
        
        # 显示错误详情
        if error_count > 0:
            report_lines.append("错误详情:")
            for result in self.translation_results:
                if result['status'] == 'error':
                    report_lines.append(f"  第{result['index']}行: {result['file_name']} - {result['error_message']}")
        
        return "\n".join(report_lines)


def main():
    """主函数 - 命令行使用示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="跨项目翻译对应工具")
    parser.add_argument("mapping_file", help="映射文件路径（包含B列表格名和C列表内位置）")
    parser.add_argument("project_directory", help="项目文件目录")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 创建翻译对应工具实例
    translator = CrossProjectTranslator()
    
    # 处理翻译映射
    results = translator.process_translation_mapping(args.mapping_file, args.project_directory)
    
    if results:
        # 显示处理报告
        print(translator.get_processing_report())
        
        # 导出结果
        if args.output:
            translator.export_results(args.output)
        else:
            # 默认输出文件名
            output_file = "翻译对应结果.xlsx"
            translator.export_results(output_file)
            print(f"结果已导出到: {output_file}")
    else:
        print("处理失败，没有生成结果")


if __name__ == "__main__":
    main()
