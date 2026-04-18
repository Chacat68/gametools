#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨项目翻译对应工具
根据Excel表格中的B列（表格名）和C列（表内位置）查找对应的内容
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
import logging
from zipfile import BadZipFile

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None

if TYPE_CHECKING:
    import pandas as pandas_type
    DataFrameType = pandas_type.DataFrame
else:
    DataFrameType = Any

logger = logging.getLogger(__name__)


class CrossProjectTranslator:
    """跨项目翻译对应工具"""
    
    def __init__(self):
        """初始化翻译对应工具"""
        self.supported_formats = ['.xlsx', '.xls']
        self.project_files = {}  # 存储项目文件缓存
        self.project_file_indexes = {}  # 存储目录级文件索引
        self.project_file_search_cache = {}  # 存储单次运行内的搜索结果缓存
        self.translation_results = []

    def clear_runtime_cache(self):
        """清理单次运行之外的内存缓存，避免 GUI 长时间保留大量 DataFrame。"""
        self.project_files.clear()
        self.project_file_indexes.clear()
        self.project_file_search_cache.clear()
        self.translation_results = []

    def _get_project_file_index(self, project_directory: str) -> Dict[str, Any]:
        """构建并缓存目录中的 Excel 文件索引，避免重复遍历目录树。"""
        normalized_dir = os.path.abspath(project_directory)
        cached_index = self.project_file_indexes.get(normalized_dir)
        if cached_index is not None:
            return cached_index

        exact_matches: Dict[str, str] = {}
        fuzzy_candidates: List[Tuple[str, str]] = []

        for root, dirs, files in os.walk(project_directory):
            for file_name in files:
                lower_name = file_name.lower()
                if not lower_name.endswith(('.xlsx', '.xls')):
                    continue

                file_path = os.path.join(root, file_name)
                exact_matches.setdefault(lower_name, file_path)
                fuzzy_candidates.append((lower_name, file_path))

        index = {
            'exact_matches': exact_matches,
            'fuzzy_candidates': fuzzy_candidates,
        }
        self.project_file_indexes[normalized_dir] = index
        return index

    def _require_pandas(self, action: str) -> bool:
        """在真正需要 DataFrame 能力前检查 pandas 依赖。"""
        if pd is None:
            logger.error(f"{action}失败: 缺少依赖 pandas")
            return False
        return True

    def _is_empty_cell(self, value: Any) -> bool:
        """统一处理单元格空值判断，兼容缺少 pandas 的环境。"""
        if value is None:
            return True
        if pd is None:
            return False
        try:
            return bool(pd.isna(value))
        except Exception:
            return False
    
    def parse_cell_reference(self, cell_ref: str) -> Tuple[int, int]:
        """
        解析Excel单元格引用（如A1, B5, C10等）
        
        Args:
            cell_ref: Excel单元格引用字符串
            
        Returns:
            (row, col): 行号和列号的元组
        """
        if not isinstance(cell_ref, str) or not cell_ref.strip():
            logger.error("解析单元格引用失败: 空引用")
            return None, None

        match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.strip().upper())
        if not match:
            logger.error(f"解析单元格引用失败，无效格式: {cell_ref}")
            return None, None

        col_str, row_str = match.groups()

        col_num = 0
        for char in col_str:
            col_num = col_num * 26 + (ord(char) - ord('A') + 1)

        return int(row_str), col_num
    
    def load_project_file(self, file_path: str) -> Dict[str, DataFrameType]:
        """
        加载项目文件并缓存
        
        Args:
            file_path: 项目文件路径
            
        Returns:
            字典，键为工作表名，值为DataFrame
        """
        if file_path in self.project_files:
            return self.project_files[file_path]

        if not self._require_pandas("加载项目文件"):
            return {}

        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return {}

        sheets_data = {}

        try:
            # 读取Excel文件的所有工作表。使用 header=None 保留物理行号，
            # 使 C2 这类坐标与 Excel 中看到的位置一致。
            with pd.ExcelFile(file_path) as excel_file:
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                        sheets_data[sheet_name] = df
                        logger.info(f"成功加载工作表: {sheet_name} ({len(df)} 行)")
                    except (ValueError, OSError, BadZipFile) as e:
                        logger.error(f"加载工作表失败 {file_path}!{sheet_name}: {e}")
                        continue
        except (ImportError, OSError, ValueError, BadZipFile) as e:
            logger.error(f"加载项目文件失败 {file_path}: {e}")
            return {}

        self.project_files[file_path] = sheets_data
        return sheets_data
    
    def find_content_by_reference(self, sheets_data: Dict[str, DataFrameType], 
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
        if sheet_name not in sheets_data:
            logger.warning(f"工作表不存在: {sheet_name}")
            return None

        df = sheets_data[sheet_name]

        row_num, col_num = self.parse_cell_reference(cell_ref)
        if row_num is None or col_num is None:
            return None

        row_idx = row_num - 1
        col_idx = col_num - 1

        if row_idx < 0 or row_idx >= len(df) or col_idx < 0 or col_idx >= len(df.columns):
            logger.warning(f"单元格引用超出范围: {sheet_name}!{cell_ref}")
            return None

        content = df.iloc[row_idx, col_idx]
        if self._is_empty_cell(content):
            return ""

        return str(content)
    
    def process_translation_mapping(self, mapping_file: str, project_directory: str) -> List[Dict]:
        """
        处理翻译映射文件
        
        Args:
            mapping_file: 映射文件路径（包含Name列文件名和Description列单元格位置）
            project_directory: 项目文件目录
            
        Returns:
            处理结果列表
        """
        logger.info(f"开始处理翻译映射文件: {mapping_file}")
        logger.info(f"项目目录: {project_directory}")

        if not os.path.exists(mapping_file):
            logger.error(f"映射文件不存在: {mapping_file}")
            return []

        if not os.path.isdir(project_directory):
            logger.error(f"项目目录不存在: {project_directory}")
            return []

        if not self._require_pandas("处理翻译映射文件"):
            return []

        # 每次新任务开始前释放上一次运行保留的 DataFrame 引用。
        self.clear_runtime_cache()

        try:
            mapping_df = pd.read_excel(mapping_file)
        except (ImportError, OSError, ValueError, BadZipFile) as e:
            logger.error(f"读取映射文件失败 {mapping_file}: {e}")
            return []

        file_name_column = None
        position_column = None

        for col in ['文件名列', '文件名', 'Name']:
            if col in mapping_df.columns:
                file_name_column = col
                break

        for col in ['位置列', '位置', 'Description']:
            if col in mapping_df.columns:
                position_column = col
                break

        if not file_name_column or not position_column:
            logger.error("映射文件缺少必要的列")
            logger.error("文件名列: ['文件名列', '文件名', 'Name']")
            logger.error("位置列: ['位置列', '位置', 'Description']")
            logger.error(f"当前文件的列名: {list(mapping_df.columns)}")
            return []

        results = []
        processed_count = 0
        found_count = 0

        for index, row in mapping_df.iterrows():
            file_name = ""
            cell_reference = ""

            try:
                file_name = str(row[file_name_column]).strip() if pd.notna(row[file_name_column]) else ""
                cell_reference = str(row[position_column]).strip() if pd.notna(row[position_column]) else ""

                if not file_name or not cell_reference:
                    logger.warning(f"第{index+1}行数据不完整，跳过")
                    continue

                processed_count += 1
                project_file_path = os.path.join(project_directory, file_name)

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

                sheets_data = self.load_project_file(project_file_path)

                if '!' in cell_reference:
                    sheet_name, cell_ref = cell_reference.split('!', 1)
                    sheet_name = sheet_name.strip()
                    cell_ref = cell_ref.strip()
                else:
                    sheet_name = list(sheets_data.keys())[0] if sheets_data else ""
                    cell_ref = cell_reference

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
                logger.exception(
                    "处理第%d行时出错 (file=%s, ref=%s): %s",
                    index + 1,
                    file_name or "<empty>",
                    cell_reference or "<empty>",
                    e,
                )
                results.append({
                    'index': index + 1,
                    'file_name': file_name,
                    'cell_reference': cell_reference,
                    'content': "",
                    'status': 'error',
                    'error_message': str(e)
                })

        logger.info(f"处理完成: 总行数 {len(mapping_df)}, 处理行数 {processed_count}, 成功找到 {found_count}")
        self.translation_results = results
        return results
    
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
            search_key = (os.path.abspath(project_directory), table_name.lower())
            if search_key in self.project_file_search_cache:
                return self.project_file_search_cache[search_key]

            possible_names = [
                f"{table_name}.xlsx",
                f"{table_name}.xls",
                f"{table_name}.XLSX",
                f"{table_name}.XLS"
            ]

            for name in possible_names:
                file_path = os.path.join(project_directory, name)
                if os.path.exists(file_path):
                    self.project_file_search_cache[search_key] = file_path
                    return file_path

            file_index = self._get_project_file_index(project_directory)

            for name in possible_names:
                indexed_path = file_index['exact_matches'].get(name.lower())
                if indexed_path:
                    self.project_file_search_cache[search_key] = indexed_path
                    return indexed_path

            table_name_lower = table_name.lower()
            for lower_file_name, file_path in file_index['fuzzy_candidates']:
                if lower_file_name.startswith(table_name_lower):
                    self.project_file_search_cache[search_key] = file_path
                    return file_path
        except OSError as e:
            logger.error(f"查找项目文件失败 {table_name}: {e}")
            return None

        self.project_file_search_cache[search_key] = None
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

            if not self._require_pandas("导出翻译对应结果"):
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
