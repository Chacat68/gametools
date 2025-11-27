#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量Excel修改器
根据映射表和JSON配置文件，批量修改指定文件夹中的Excel文件
"""

import os
import re
import json
import copy
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import pandas as pd
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter, column_index_from_string
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BatchExcelModifier:
    """批量Excel修改器"""
    
    def __init__(self):
        """初始化批量修改器"""
        self.supported_extensions = {'.xlsx', '.xls'}
        
        # 处理统计
        self.processing_stats = {
            'total_rows': 0,           # 映射表总行数
            'processed_rows': 0,       # 已处理行数
            'modified_files': 0,       # 修改的文件数
            'modified_cells': 0,       # 修改的单元格数
            'skipped_rows': 0,         # 跳过的行数
            'errors': 0                # 错误数
        }
        
        # 错误日志
        self.error_logs = []
        
        # 修改日志
        self.modification_logs = []
        
        # JSON配置中的字段信息
        self.field_config = {}
        
        # 进度回调
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def _report_progress(self, message: str, percentage: float = None):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(message, percentage)
        logger.info(message)
    
    def load_json_config(self, json_path: str) -> Dict:
        """
        加载JSON配置文件，提取字段信息
        
        JSON格式示例:
        {
            "text_tables": [
                {
                    "table_name": "armor_ancient.xlsx",
                    "sheet_name": "armor_ancient",
                    "fields": ["c_armor_ancient", "level_id", ...],
                    "fields_with_examples": ["c_armor_ancient,前后端", "level_id,前端", ...]
                }
            ]
        }
        
        Args:
            json_path: JSON配置文件路径
            
        Returns:
            Dict: 表名到字段信息的映射
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 构建表名到字段的映射
            field_config = {}
            
            # 处理text_tables
            text_tables = config.get('text_tables', [])
            for table_info in text_tables:
                table_name = table_info.get('table_name', '')
                sheet_name = table_info.get('sheet_name', '')
                fields = table_info.get('fields', [])
                fields_with_examples = table_info.get('fields_with_examples', [])
                
                # 解析fields_with_examples获取字段类型
                field_types = {}
                for field_str in fields_with_examples:
                    if ',' in field_str:
                        parts = field_str.split(',', 1)
                        field_name = parts[0].strip()
                        field_type = parts[1].strip() if len(parts) > 1 else ''
                        field_types[field_name] = field_type
                
                # 使用完整表名作为key
                field_config[table_name] = {
                    'table_name': table_name,
                    'sheet_name': sheet_name,
                    'fields': fields,
                    'fields_with_examples': fields_with_examples,
                    'field_types': field_types
                }
                
                # 同时用不含扩展名的表名作为key（兼容）
                table_key = Path(table_name).stem
                field_config[table_key] = field_config[table_name]
            
            self.field_config = field_config
            logger.info(f"成功加载JSON配置: {json_path}")
            logger.info(f"  - 包含 {len(text_tables)} 个表的字段配置")
            
            return field_config
        
        except Exception as e:
            error_msg = f"加载JSON配置失败: {e}"
            logger.error(error_msg)
            self.error_logs.append(error_msg)
            return {}
    
    def get_table_fields(self, table_name: str) -> List[str]:
        """
        获取指定表的字段列表
        
        Args:
            table_name: 表名（可以带或不带扩展名）
            
        Returns:
            List[str]: 字段名列表（合并 fields 和 fields_with_examples）
        """
        table_config = None
        
        # 尝试直接匹配
        if table_name in self.field_config:
            table_config = self.field_config[table_name]
        else:
            # 尝试不带扩展名匹配
            table_key = Path(table_name).stem
            if table_key in self.field_config:
                table_config = self.field_config[table_key]
        
        if not table_config:
            return []
        
        # 合并 fields 和 fields_with_examples 中的字段名
        all_fields = set()
        
        # 从 fields 列表获取
        fields = table_config.get('fields', [])
        all_fields.update(fields)
        
        # 从 fields_with_examples 列表获取（格式可能是 "字段名,类型" 或纯字段名）
        fields_with_examples = table_config.get('fields_with_examples', [])
        for field_entry in fields_with_examples:
            if isinstance(field_entry, str):
                # 取第一个逗号前的部分作为字段名
                field_name = field_entry.split(',')[0].strip()
                if field_name:
                    all_fields.add(field_name)
        
        return list(all_fields)
    
    def load_mapping_table(self, mapping_path: str, sheet_name: str = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        加载映射表Excel文件
        
        映射表格式:
        A列: 表名（如 act_20206_shilian_0.xlsx）
        B列: Classification (如 des)
        C列: ID
        D列: VN（越南文内容）
        E列及之后: 其他语言列
        
        Args:
            mapping_path: 映射表Excel文件路径
            sheet_name: 工作表名称（可选，默认读取第一个）
            
        Returns:
            Tuple[pd.DataFrame, List[str]]: (DataFrame, 列名列表)
        """
        try:
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(mapping_path, sheet_name=sheet_name, header=0)
            else:
                df = pd.read_excel(mapping_path, header=0)
            
            columns = df.columns.tolist()
            
            logger.info(f"成功加载映射表: {mapping_path}")
            logger.info(f"  - 行数: {len(df)}")
            logger.info(f"  - 列名: {columns}")
            
            self.processing_stats['total_rows'] = len(df)
            
            return df, columns
        
        except Exception as e:
            error_msg = f"加载映射表失败: {e}"
            logger.error(error_msg)
            self.error_logs.append(error_msg)
            return pd.DataFrame(), []
    
    def get_mapping_sheets(self, mapping_path: str) -> List[str]:
        """
        获取映射表中的所有工作表名称
        
        Args:
            mapping_path: 映射表Excel文件路径
            
        Returns:
            List[str]: 工作表名称列表
        """
        try:
            xl = pd.ExcelFile(mapping_path)
            return xl.sheet_names
        except Exception as e:
            logger.error(f"获取工作表列表失败: {e}")
            return []
    
    def parse_mapping_row(self, row: pd.Series, columns: List[str], 
                         table_col: str, id_col: str, 
                         modify_cols: List[str]) -> Dict:
        """
        解析映射表中的一行数据
        
        Args:
            row: DataFrame行
            columns: 列名列表
            table_col: 表名列名
            id_col: ID列名
            modify_cols: 要修改的列名列表
            
        Returns:
            Dict: 解析后的行信息
        """
        try:
            table_name = str(row[table_col]).strip() if pd.notna(row[table_col]) else ''
            id_value = row[id_col] if pd.notna(row[id_col]) else ''
            
            # 获取要修改的值
            modify_values = {}
            for col in modify_cols:
                if col in row.index:
                    value = row[col]
                    if pd.notna(value):
                        modify_values[col] = str(value).strip()
            
            return {
                'table_name': table_name,
                'id': id_value,
                'modify_values': modify_values
            }
        
        except Exception as e:
            logger.error(f"解析行数据失败: {e}")
            return {}
    
    def find_field_column(self, ws, field_name: str, field_row: int = 5) -> Optional[int]:
        """
        在Excel工作表中查找字段名对应的列号
        
        Args:
            ws: openpyxl工作表对象
            field_name: 字段名
            field_row: 字段名所在行（默认第5行）
            
        Returns:
            Optional[int]: 列号（从1开始），未找到返回None
        """
        for col in range(1, ws.max_column + 1):
            cell_value = ws.cell(row=field_row, column=col).value
            if cell_value and str(cell_value).strip() == field_name:
                return col
        return None
    
    def find_id_row(self, ws, id_value, id_col: int = 1, data_start_row: int = 7) -> Optional[int]:
        """
        在Excel工作表中查找ID对应的行号
        
        Args:
            ws: openpyxl工作表对象
            id_value: 要查找的ID值
            id_col: ID所在列（默认A列，即第1列）
            data_start_row: 数据起始行（默认第7行）
            
        Returns:
            Optional[int]: 行号（从1开始），未找到返回None
        """
        # 将ID值转换为可比较的格式
        target_id = str(id_value).strip()
        
        # 尝试转换为数字进行比较
        try:
            target_id_num = float(target_id)
        except ValueError:
            target_id_num = None
        
        for row in range(data_start_row, ws.max_row + 1):
            cell_value = ws.cell(row=row, column=id_col).value
            if cell_value is not None:
                cell_str = str(cell_value).strip()
                
                # 字符串比较
                if cell_str == target_id:
                    return row
                
                # 数字比较
                if target_id_num is not None:
                    try:
                        if float(cell_str) == target_id_num:
                            return row
                    except ValueError:
                        pass
        
        return None
    
    def get_field_name_for_column(self, mapping_col: str, table_key: str) -> Optional[str]:
        """
        根据映射表列名和表配置，获取对应的Excel字段名
        
        这个方法根据JSON配置中的字段列表，找到与映射表列名对应的字段
        
        Args:
            mapping_col: 映射表中的列名（如 "VN", "Support-CH"等）
            table_key: 表名key
            
        Returns:
            Optional[str]: Excel中的字段名，未找到返回None
        """
        # 获取表的字段配置
        if table_key not in self.field_config:
            return None
        
        fields = self.field_config[table_key].get('fields', [])
        
        # 常见映射规则
        column_field_mapping = {
            'VN': ['vn', 'VN', 'vietnamese', 'name_vn'],
            'EN': ['en', 'EN', 'english', 'name_en'],
            'Support-CH': ['support_ch', 'Support-CH', 'chinese', 'name_ch', 'zh'],
            'Polish-CH': ['polish_ch', 'Polish-CH'],
            'VN.1': ['vn_1', 'VN.1', 'vn1'],
            'TH': ['th', 'TH', 'thai', 'name_th'],
        }
        
        # 查找匹配的字段
        possible_names = column_field_mapping.get(mapping_col, [mapping_col.lower()])
        
        for field in fields:
            field_lower = field.lower()
            for possible in possible_names:
                if possible.lower() == field_lower or field_lower.endswith(possible.lower()):
                    return field
        
        # 如果没找到精确匹配，返回列名本身（让用户在GUI中指定映射）
        return None
    
    def modify_excel_file(self, excel_path: str, modifications: List[Dict], 
                         field_mapping: Dict[str, str] = None,
                         id_col: int = 1, 
                         field_row: int = 5,
                         data_start_row: int = 7) -> Tuple[int, List[str]]:
        """
        修改单个Excel文件
        
        Args:
            excel_path: Excel文件路径
            modifications: 修改列表，每项包含 {id, modify_values}
            field_mapping: 列名到字段名的映射 {映射表列名: Excel字段名}
            id_col: ID所在列
            field_row: 字段名所在行
            data_start_row: 数据起始行
            
        Returns:
            Tuple[int, List[str]]: (修改的单元格数, 错误列表)
        """
        modified_count = 0
        errors = []
        
        try:
            # 加载Excel文件
            wb = load_workbook(excel_path)
            ws = wb.active
            
            # 缓存字段列号
            field_columns = {}
            
            for mod in modifications:
                id_value = mod.get('id')
                modify_values = mod.get('modify_values', {})
                
                if not id_value or not modify_values:
                    continue
                
                # 查找ID对应的行
                target_row = self.find_id_row(ws, id_value, id_col, data_start_row)
                if target_row is None:
                    error_msg = f"未找到ID: {id_value}"
                    errors.append(error_msg)
                    continue
                
                # 修改每个指定的列
                for col_name, new_value in modify_values.items():
                    # 获取字段名
                    field_name = field_mapping.get(col_name) if field_mapping else col_name
                    
                    if not field_name:
                        continue
                    
                    # 查找字段对应的列
                    if field_name not in field_columns:
                        col_num = self.find_field_column(ws, field_name, field_row)
                        field_columns[field_name] = col_num
                    
                    col_num = field_columns.get(field_name)
                    
                    if col_num is None:
                        error_msg = f"未找到字段: {field_name}"
                        if error_msg not in errors:
                            errors.append(error_msg)
                        continue
                    
                    # 修改单元格
                    old_value = ws.cell(row=target_row, column=col_num).value
                    ws.cell(row=target_row, column=col_num).value = new_value
                    
                    # 记录修改日志
                    self.modification_logs.append({
                        'file': os.path.basename(excel_path),
                        'id': id_value,
                        'field': field_name,
                        'position': f"{get_column_letter(col_num)}{target_row}",
                        'old_value': old_value,
                        'new_value': new_value
                    })
                    
                    modified_count += 1
            
            # 保存文件
            if modified_count > 0:
                wb.save(excel_path)
                logger.info(f"已修改并保存: {excel_path} ({modified_count} 处修改)")
            
            wb.close()
            
        except Exception as e:
            error_msg = f"修改文件失败 {excel_path}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        return modified_count, errors
    
    def process_batch_modification_with_json(self, mapping_path: str, 
                                             excel_directory: str,
                                             table_col: str,
                                             id_col: str,
                                             mapping_sheet: str = None,
                                             backup: bool = True) -> Dict:
        """
        根据JSON配置执行批量修改（自动匹配字段）
        
        工作流程:
        1. 读取映射表中的每一行
        2. 根据表名从JSON配置中获取该表的字段列表
        3. 检查映射表中是否有同名的列
        4. 如果有，则用映射表中的值更新目标Excel
        
        Args:
            mapping_path: 映射表路径
            excel_directory: Excel文件所在目录
            table_col: 映射表中的表名列
            id_col: 映射表中的ID列
            mapping_sheet: 映射表工作表名称
            backup: 是否创建备份
            
        Returns:
            Dict: 处理结果统计
        """
        # 重置统计
        self.processing_stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'modified_files': 0,
            'modified_cells': 0,
            'skipped_rows': 0,
            'skipped_no_config': 0,
            'errors': 0
        }
        self.error_logs = []
        self.modification_logs = []
        
        if not self.field_config:
            self._report_progress("错误: 未加载JSON配置文件")
            return self.processing_stats
        
        self._report_progress("开始加载映射表...")
        
        # 加载映射表
        df, mapping_columns = self.load_mapping_table(mapping_path, mapping_sheet)
        if df.empty:
            return self.processing_stats
        
        self._report_progress(f"映射表加载完成，共 {len(df)} 行数据")
        self._report_progress(f"映射表列: {mapping_columns}")
        
        # 按表名分组修改
        grouped_modifications = {}
        
        for idx, row in df.iterrows():
            # 获取表名和ID
            table_name = str(row[table_col]).strip() if pd.notna(row[table_col]) else ''
            id_value = row[id_col] if pd.notna(row[id_col]) else ''
            
            if not table_name or not id_value:
                self.processing_stats['skipped_rows'] += 1
                continue
            
            # 从JSON配置中获取该表的字段列表
            table_fields = self.get_table_fields(table_name)
            
            if not table_fields:
                # 该表不在JSON配置中，跳过
                self.processing_stats['skipped_no_config'] += 1
                continue
            
            # 找出映射表中与JSON字段匹配的列
            modify_values = {}
            for field in table_fields:
                if field in mapping_columns and field in row.index:
                    value = row[field]
                    if pd.notna(value) and str(value).strip():
                        modify_values[field] = str(value).strip()
            
            if not modify_values:
                self.processing_stats['skipped_rows'] += 1
                continue
            
            if table_name not in grouped_modifications:
                grouped_modifications[table_name] = []
            
            grouped_modifications[table_name].append({
                'id': id_value,
                'modify_values': modify_values
            })
        
        self._report_progress(f"需要修改 {len(grouped_modifications)} 个文件")
        
        # 处理每个文件
        total_files = len(grouped_modifications)
        if total_files == 0:
            self._report_progress("没有找到需要修改的文件")
            return self.processing_stats
        
        processed_files = 0
        
        for table_name, modifications in grouped_modifications.items():
            # 构建文件路径
            excel_path = os.path.join(excel_directory, table_name)
            
            if not os.path.exists(excel_path):
                error_msg = f"文件不存在: {excel_path}"
                self.error_logs.append(error_msg)
                self.processing_stats['errors'] += 1
                logger.warning(error_msg)
                continue
            
            # 创建备份
            if backup:
                backup_path = excel_path + '.bak'
                try:
                    import shutil
                    shutil.copy2(excel_path, backup_path)
                except Exception as e:
                    logger.warning(f"创建备份失败: {e}")
            
            # 获取该表需要修改的字段（用于显示）
            first_mod = modifications[0] if modifications else {}
            fields_to_modify = list(first_mod.get('modify_values', {}).keys())
            self._report_progress(f"处理: {table_name} (字段: {', '.join(fields_to_modify)})")
            
            # 修改文件 - 字段名直接使用，不需要映射
            modified_count, errors = self.modify_excel_file(
                excel_path, 
                modifications, 
                field_mapping=None  # 字段名已经是正确的
            )
            
            if modified_count > 0:
                self.processing_stats['modified_files'] += 1
                self.processing_stats['modified_cells'] += modified_count
            
            self.processing_stats['processed_rows'] += len(modifications)
            
            if errors:
                self.error_logs.extend(errors)
                self.processing_stats['errors'] += len(errors)
            
            processed_files += 1
            progress = (processed_files / total_files) * 100
            self._report_progress(f"已处理: {processed_files}/{total_files} 文件", progress)
        
        self._report_progress("批量修改完成！", 100)
        
        return self.processing_stats

    def process_batch_modification(self, mapping_path: str, 
                                  excel_directory: str,
                                  table_col: str,
                                  id_col: str,
                                  modify_cols: List[str],
                                  field_mapping: Dict[str, str] = None,
                                  mapping_sheet: str = None,
                                  backup: bool = True) -> Dict:
        """
        执行批量修改
        
        Args:
            mapping_path: 映射表路径
            excel_directory: Excel文件所在目录
            table_col: 映射表中的表名列
            id_col: 映射表中的ID列
            modify_cols: 映射表中要用于修改的列名列表
            field_mapping: 映射表列名到Excel字段名的映射
            mapping_sheet: 映射表工作表名称
            backup: 是否创建备份
            
        Returns:
            Dict: 处理结果统计
        """
        # 重置统计
        self.processing_stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'modified_files': 0,
            'modified_cells': 0,
            'skipped_rows': 0,
            'errors': 0
        }
        self.error_logs = []
        self.modification_logs = []
        
        self._report_progress("开始加载映射表...")
        
        # 加载映射表
        df, columns = self.load_mapping_table(mapping_path, mapping_sheet)
        if df.empty:
            return self.processing_stats
        
        self._report_progress(f"映射表加载完成，共 {len(df)} 行数据")
        
        # 按表名分组修改
        grouped_modifications = {}
        
        for idx, row in df.iterrows():
            parsed = self.parse_mapping_row(row, columns, table_col, id_col, modify_cols)
            
            if not parsed or not parsed.get('table_name') or not parsed.get('modify_values'):
                self.processing_stats['skipped_rows'] += 1
                continue
            
            table_name = parsed['table_name']
            
            if table_name not in grouped_modifications:
                grouped_modifications[table_name] = []
            
            grouped_modifications[table_name].append({
                'id': parsed['id'],
                'modify_values': parsed['modify_values']
            })
        
        self._report_progress(f"需要修改 {len(grouped_modifications)} 个文件")
        
        # 处理每个文件
        total_files = len(grouped_modifications)
        processed_files = 0
        
        for table_name, modifications in grouped_modifications.items():
            # 构建文件路径
            excel_path = os.path.join(excel_directory, table_name)
            
            if not os.path.exists(excel_path):
                error_msg = f"文件不存在: {excel_path}"
                self.error_logs.append(error_msg)
                self.processing_stats['errors'] += 1
                logger.warning(error_msg)
                continue
            
            # 创建备份
            if backup:
                backup_path = excel_path + '.bak'
                try:
                    import shutil
                    shutil.copy2(excel_path, backup_path)
                except Exception as e:
                    logger.warning(f"创建备份失败: {e}")
            
            # 修改文件
            modified_count, errors = self.modify_excel_file(
                excel_path, 
                modifications, 
                field_mapping
            )
            
            if modified_count > 0:
                self.processing_stats['modified_files'] += 1
                self.processing_stats['modified_cells'] += modified_count
            
            self.processing_stats['processed_rows'] += len(modifications)
            
            if errors:
                self.error_logs.extend(errors)
                self.processing_stats['errors'] += len(errors)
            
            processed_files += 1
            progress = (processed_files / total_files) * 100
            self._report_progress(f"已处理: {processed_files}/{total_files} 文件", progress)
        
        self._report_progress("批量修改完成！", 100)
        
        return self.processing_stats
    
    def generate_modification_report(self, output_path: str) -> bool:
        """
        生成修改报告
        
        Args:
            output_path: 输出Excel路径
            
        Returns:
            bool: 成功返回True
        """
        try:
            if not self.modification_logs:
                logger.warning("没有修改记录可导出")
                return False
            
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "修改记录"
            
            # 设置表头
            headers = ['文件名', 'ID', '字段名', 'Excel位置', '原值', '新值']
            ws.append(headers)
            
            # 设置表头样式
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF', size=11)
            
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 写入数据
            for log in self.modification_logs:
                ws.append([
                    log.get('file', ''),
                    log.get('id', ''),
                    log.get('field', ''),
                    log.get('position', ''),
                    log.get('old_value', ''),
                    log.get('new_value', '')
                ])
            
            # 调整列宽
            for col_idx, header in enumerate(headers, 1):
                ws.column_dimensions[get_column_letter(col_idx)].width = 20
            
            # 添加统计页
            ws_stats = wb.create_sheet(title="统计信息")
            stats_data = [
                ['统计项', '数值'],
                ['映射表总行数', self.processing_stats['total_rows']],
                ['已处理行数', self.processing_stats['processed_rows']],
                ['跳过行数', self.processing_stats['skipped_rows']],
                ['修改的文件数', self.processing_stats['modified_files']],
                ['修改的单元格数', self.processing_stats['modified_cells']],
                ['错误数', self.processing_stats['errors']]
            ]
            
            for row_data in stats_data:
                ws_stats.append(row_data)
            
            # 设置统计页表头样式
            for col_idx in range(1, 3):
                cell = ws_stats.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
            
            # 如果有错误，添加错误日志页
            if self.error_logs:
                ws_errors = wb.create_sheet(title="错误日志")
                ws_errors.append(['错误信息'])
                ws_errors.cell(row=1, column=1).fill = PatternFill(
                    start_color='FF0000', end_color='FF0000', fill_type='solid')
                ws_errors.cell(row=1, column=1).font = Font(bold=True, color='FFFFFF')
                
                for error in self.error_logs:
                    ws_errors.append([error])
            
            wb.save(output_path)
            logger.info(f"修改报告已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return False
    
    def get_stats_summary(self) -> str:
        """
        获取统计摘要文本
        
        Returns:
            str: 统计摘要
        """
        return f"""批量修改完成！

统计信息:
- 映射表总行数: {self.processing_stats['total_rows']}
- 已处理行数: {self.processing_stats['processed_rows']}
- 跳过行数: {self.processing_stats['skipped_rows']}
- 修改的文件数: {self.processing_stats['modified_files']}
- 修改的单元格数: {self.processing_stats['modified_cells']}
- 错误数: {self.processing_stats['errors']}

修改记录数: {len(self.modification_logs)} 条"""
