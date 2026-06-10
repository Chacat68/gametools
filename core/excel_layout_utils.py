#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 表布局公共工具。

统一 openpyxl 工作表与 pandas DataFrame 上的行边界检测逻辑，
供字段导出、多语言提取等模块共用。
"""

from typing import Any, Optional

import pandas as pd

from core.constants import DATA_START_ROW, DATA_START_ROW_INDEX, ROW_BOUNDARY_KEYWORD


def normalize_boundary_keyword(keyword: Optional[str] = None) -> str:
    """返回用于比较的行边界关键字（小写）。"""
    value = keyword if keyword is not None else ROW_BOUNDARY_KEYWORD
    return str(value).strip().lower()


def _cell_text(cell_value: Any) -> Optional[str]:
    """从单元格值或 openpyxl Cell 对象提取可比较文本。"""
    if hasattr(cell_value, 'value'):
        cell_value = cell_value.value
    if cell_value is None or (isinstance(cell_value, float) and pd.isna(cell_value)):
        return None
    return str(cell_value).strip().lower()


def row_values_match_boundary(row_values: Any, boundary_keyword: Optional[str] = None) -> bool:
    """判断一行单元格中是否存在等于边界关键字的值。"""
    keyword = normalize_boundary_keyword(boundary_keyword)
    for cell_value in row_values:
        text = _cell_text(cell_value)
        if text is not None and text == keyword:
            return True
    return False


def check_row_boundary_openpyxl_sheet(sheet, row_idx: int,
                                    boundary_keyword: Optional[str] = None) -> bool:
    """
    检查 openpyxl 工作表指定行是否为数据区下限边界行。

    Args:
        sheet: openpyxl 工作表
        row_idx: 物理行号（1-based）
    """
    if row_idx > sheet.max_row:
        return False
    return row_values_match_boundary(sheet[row_idx], boundary_keyword)


def find_boundary_row_openpyxl_sheet(sheet, start_row: int = DATA_START_ROW,
                                       boundary_keyword: Optional[str] = None) -> int:
    """
    从 start_row 起向下查找第一个边界行。

    Returns:
        边界行物理行号；未找到则返回 sheet.max_row + 1
    """
    for row_idx in range(start_row, sheet.max_row + 1):
        if check_row_boundary_openpyxl_sheet(sheet, row_idx, boundary_keyword):
            return row_idx
    return sheet.max_row + 1


def check_row_boundary_dataframe(df, row_idx: int,
                                 boundary_keyword: Optional[str] = None) -> bool:
    """
    检查 DataFrame 指定行是否为数据区下限边界行。

    Args:
        df: pandas DataFrame
        row_idx: 行索引（0-based）
    """
    if row_idx >= len(df):
        return False
    return row_values_match_boundary(df.iloc[row_idx], boundary_keyword)


def find_boundary_row_dataframe(df, start_row: int = DATA_START_ROW_INDEX,
                                boundary_keyword: Optional[str] = None) -> Optional[int]:
    """
    从 start_row 起向下查找第一个边界行。

    Returns:
        边界行 0-based 索引；未找到返回 None
    """
    for row_idx in range(start_row, len(df)):
        if check_row_boundary_dataframe(df, row_idx, boundary_keyword):
            return row_idx
    return None
