#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版跨项目翻译对应工具 - 集成缓存机制
根据Excel表格中的B列（表格名）和C列（表内位置）查找对应的内容
支持内存缓存和文件缓存，提升性能
"""

import os
import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import time
from hashlib import md5

# 添加当前目录到路径
from .cache_manager import CacheManager, get_cache_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CrossProjectTranslatorWithCache:
    """增强版跨项目翻译对应工具 - 支持缓存"""
    
    def __init__(self, cache_dir: str = ".cache", enable_file_cache: bool = True,
                 memory_cache_size: int = 1000, cache_ttl: Optional[float] = 86400):
        """
        初始化增强版翻译对应工具
        
        Args:
            cache_dir: 缓存目录
            enable_file_cache: 是否启用文件缓存
            memory_cache_size: 内存缓存最大条目数
            cache_ttl: 缓存过期时间（秒），默认24小时
        """
        self.supported_formats = ['.xlsx', '.xls']
        self.translation_results = []
        
        # 初始化缓存管理器
        self.cache_manager = CacheManager(
            memory_size=memory_cache_size,
            cache_dir=cache_dir,
            default_ttl=cache_ttl,
            use_file_cache=enable_file_cache
        )
        
        # 缓存键前缀
        self.excel_cache_prefix = "excel_file:"
        self.query_cache_prefix = "query:"
        self.file_search_cache_prefix = "file_search:"
        
        # 统计信息
        self.cache_hits = 0
        self.cache_misses = 0
        self.query_start_time = None
    
    def parse_cell_reference(self, cell_ref: str) -> Tuple[int, int]:
        """
        解析Excel单元格引用（如A1, B5, C10等）
        
        Args:
            cell_ref: Excel单元格引用字符串
            
        Returns:
            (row, col): 行号和列号的元组
        """
        try:
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
    
    def _get_file_hash(self, file_path: str) -> str:
        """获取文件的哈希值（用于缓存键）"""
        try:
            # 使用文件路径和修改时间生成哈希
            file_stat = os.stat(file_path)
            hash_input = f"{file_path}:{file_stat.st_mtime}"
            return md5(hash_input.encode()).hexdigest()[:16]
        except Exception:
            return md5(file_path.encode()).hexdigest()[:16]
    
    def load_project_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        加载项目文件并缓存（带智能缓存）
        
        Args:
            file_path: 项目文件路径
            
        Returns:
            字典，键为工作表名，值为DataFrame
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return {}
            
            # 生成缓存键
            file_hash = self._get_file_hash(file_path)
            cache_key = f"{self.excel_cache_prefix}{file_hash}"
            
            # 尝试从缓存获取
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                logger.info(f"从缓存加载文件: {file_path}")
                self.cache_hits += 1
                return cached_data
            
            # 缓存未命中，读取文件
            logger.info(f"读取并缓存文件: {file_path}")
            self.cache_misses += 1
            
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
            
            # 将数据存入缓存
            self.cache_manager.set(cache_key, sheets_data)
            
            return sheets_data
            
        except Exception as e:
            logger.error(f"加载项目文件失败 {file_path}: {e}")
            return {}
    
    def find_content_by_reference(self, sheets_data: Dict[str, pd.DataFrame], 
                                 sheet_name: str, cell_ref: str) -> Optional[str]:
        """
        根据工作表名和单元格引用查找内容（支持缓存）
        
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
            
            # 生成查询缓存键
            query_key = f"{self.query_cache_prefix}{sheet_name}:{cell_ref}"
            
            # 尝试从缓存获取查询结果
            cached_result = self.cache_manager.get(query_key)
            if cached_result is not None:
                logger.debug(f"查询缓存命中: {query_key}")
                self.cache_hits += 1
                return cached_result
            
            self.cache_misses += 1
            
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
                result = ""
            else:
                result = str(content)
            
            # 将查询结果缓存
            self.cache_manager.set(query_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"查找内容失败 {sheet_name}!{cell_ref}: {e}")
            return None
    
    def find_project_file(self, project_directory: str, table_name: str) -> Optional[str]:
        """
        在项目目录中查找指定的表格文件（带文件搜索缓存）
        
        Args:
            project_directory: 项目目录
            table_name: 表格名称
            
        Returns:
            找到的文件路径，如果未找到返回None
        """
        try:
            # 生成文件搜索缓存键
            search_key = f"{self.file_search_cache_prefix}{project_directory}:{table_name}"
            
            # 尝试从缓存获取搜索结果
            cached_result = self.cache_manager.get(search_key)
            if cached_result is not None:
                logger.debug(f"文件搜索缓存命中: {table_name}")
                self.cache_hits += 1
                if cached_result != "NOT_FOUND":
                    return cached_result
                return None
            
            self.cache_misses += 1
            
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
                    self.cache_manager.set(search_key, file_path)
                    return file_path
            
            # 如果直接匹配失败，搜索包含该名称的文件
            for root, dirs, files in os.walk(project_directory):
                for file in files:
                    if file.lower().startswith(table_name.lower()) and file.lower().endswith(('.xlsx', '.xls')):
                        result_path = os.path.join(root, file)
                        self.cache_manager.set(search_key, result_path)
                        return result_path
            
            # 缓存未找到的结果
            self.cache_manager.set(search_key, "NOT_FOUND")
            return None
            
        except Exception as e:
            logger.error(f"查找项目文件失败 {table_name}: {e}")
            return None
    
    def process_translation_mapping(self, mapping_file: str, project_directory: str) -> List[Dict]:
        """
        处理翻译映射文件（性能增强版）
        
        Args:
            mapping_file: 映射文件路径
            project_directory: 项目文件目录
            
        Returns:
            处理结果列表
        """
        self.query_start_time = time.time()
        
        try:
            logger.info(f"开始处理翻译映射文件: {mapping_file}")
            logger.info(f"项目目录: {project_directory}")
            
            # 读取映射文件
            mapping_df = pd.read_excel(mapping_file)
            
            # 检查必要的列
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
                            'error_message': f"未找到文件: {file_name}",
                            'from_cache': False
                        })
                        continue
                    
                    # 加载项目文件（可能从缓存）
                    sheets_data = self.load_project_file(project_file_path)
                    
                    # 解析表内位置
                    if '!' in cell_reference:
                        sheet_name, cell_ref = cell_reference.split('!', 1)
                        sheet_name = sheet_name.strip()
                        cell_ref = cell_ref.strip()
                    else:
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
                        'project_file': project_file_path,
                        'from_cache': False
                    })
                    
                except Exception as e:
                    logger.error(f"处理第{index+1}行时出错: {e}")
                    results.append({
                        'index': index + 1,
                        'file_name': str(row[file_name_column]) if pd.notna(row[file_name_column]) else "",
                        'cell_reference': str(row[position_column]) if pd.notna(row[position_column]) else "",
                        'content': "",
                        'status': 'error',
                        'error_message': str(e),
                        'from_cache': False
                    })
            
            elapsed_time = time.time() - self.query_start_time
            
            logger.info(f"处理完成: 总行数 {len(mapping_df)}, 处理行数 {processed_count}, 成功找到 {found_count}")
            logger.info(f"耗时: {elapsed_time:.2f} 秒")
            logger.info(f"缓存命中: {self.cache_hits}, 缓存未命中: {self.cache_misses}")
            
            self.translation_results = results
            return results
            
        except Exception as e:
            logger.error(f"处理翻译映射文件失败: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, any]:
        """获取缓存统计信息"""
        stats = self.cache_manager.get_stats()
        stats['custom'] = {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{self.cache_hits/(self.cache_hits+self.cache_misses)*100:.1f}%" 
                       if (self.cache_hits + self.cache_misses) > 0 else "0%"
        }
        return stats
    
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
                'content', 'status', 'error_message', 'project_file', 'from_cache'
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
                'project_file': '项目文件路径',
                'from_cache': '来自缓存'
            }
            
            results_df = results_df.rename(columns=column_names)
            
            # 导出到Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
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
        """创建统计信息"""
        if not self.translation_results:
            return []
        
        total_count = len(self.translation_results)
        success_count = sum(1 for r in self.translation_results if r['status'] == 'success')
        error_count = total_count - success_count
        
        stats = [
            {'项目': '总处理数量', '值': total_count},
            {'项目': '成功找到', '值': success_count},
            {'项目': '处理失败', '值': error_count},
            {'项目': '成功率', '值': f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0%"},
            {'项目': '缓存命中次数', '值': self.cache_hits},
            {'项目': '缓存未命中次数', '值': self.cache_misses},
            {'项目': '缓存命中率', '值': f"{self.cache_hits/(self.cache_hits+self.cache_misses)*100:.1f}%" 
                                      if (self.cache_hits + self.cache_misses) > 0 else "0%"},
        ]
        
        return stats
    
    def clear_cache(self) -> None:
        """清空所有缓存"""
        self.cache_manager.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("所有缓存已清空")
    
    def cleanup_expired_cache(self) -> None:
        """清理过期缓存"""
        stats = self.cache_manager.cleanup_expired()
        logger.info(f"清理过期缓存: {stats}")
    
    def get_processing_report(self) -> str:
        """获取处理报告"""
        if not self.translation_results:
            return "没有处理结果"
        
        total_count = len(self.translation_results)
        success_count = sum(1 for r in self.translation_results if r['status'] == 'success')
        error_count = total_count - success_count
        
        elapsed_time = time.time() - self.query_start_time if self.query_start_time else 0
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("跨项目翻译对应处理报告（含缓存统计）")
        report_lines.append("=" * 60)
        report_lines.append(f"总处理数量: {total_count}")
        report_lines.append(f"成功找到: {success_count}")
        report_lines.append(f"处理失败: {error_count}")
        report_lines.append(f"成功率: {success_count/total_count*100:.1f}%" if total_count > 0 else "0%")
        report_lines.append(f"处理耗时: {elapsed_time:.2f} 秒")
        report_lines.append("")
        report_lines.append("缓存统计:")
        report_lines.append(f"  缓存命中: {self.cache_hits}")
        report_lines.append(f"  缓存未命中: {self.cache_misses}")
        report_lines.append(f"  命中率: {self.cache_hits/(self.cache_hits+self.cache_misses)*100:.1f}%" 
                          if (self.cache_hits + self.cache_misses) > 0 else "  命中率: 0%")
        report_lines.append("=" * 60)
        
        if error_count > 0:
            report_lines.append("错误详情:")
            for result in self.translation_results:
                if result['status'] == 'error':
                    report_lines.append(f"  第{result['index']}行: {result['file_name']} - {result['error_message']}")
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    # 测试增强版翻译对应工具
    translator = CrossProjectTranslatorWithCache()
    
    print("增强版跨项目翻译对应工具已创建")
    print("缓存管理器状态:", translator.get_cache_stats())
