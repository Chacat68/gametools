#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Excel 表布局公共工具测试。"""

import pandas as pd

from core.constants import ROW_BOUNDARY_KEYWORD
from core.excel_layout_utils import (
    check_row_boundary_dataframe,
    check_row_boundary_openpyxl_sheet,
    find_boundary_row_dataframe,
    find_boundary_row_openpyxl_sheet,
    row_values_match_boundary,
)


class _FakeCell:
    def __init__(self, value):
        self.value = value


class _FakeSheet:
    def __init__(self, rows):
        self._rows = rows
        self.max_row = len(rows)

    def __getitem__(self, row_idx):
        return self._rows[row_idx - 1]


def test_row_values_match_boundary():
    assert row_values_match_boundary(['a', 'over', 'b'])
    assert row_values_match_boundary(['a', 'OVER ', None])
    assert not row_values_match_boundary(['a', 'overflow', None])
    assert not row_values_match_boundary(['', None])


def test_openpyxl_boundary_helpers():
    sheet = _FakeSheet([
        [_FakeCell('id'), _FakeCell('name')],
        [_FakeCell('1'), _FakeCell('hero')],
        [_FakeCell('over'), _FakeCell('')],
        [_FakeCell('9'), _FakeCell('ignored')],
    ])
    assert not check_row_boundary_openpyxl_sheet(sheet, 2)
    assert check_row_boundary_openpyxl_sheet(sheet, 3)
    assert find_boundary_row_openpyxl_sheet(sheet, 2) == 3
    assert find_boundary_row_openpyxl_sheet(sheet, 4) == sheet.max_row + 1


def test_dataframe_boundary_helpers():
    df = pd.DataFrame([
        ['id', 'name'],
        ['1', 'hero'],
        [ROW_BOUNDARY_KEYWORD, ''],
        ['9', 'ignored'],
    ])
    assert not check_row_boundary_dataframe(df, 1)
    assert check_row_boundary_dataframe(df, 2)
    assert find_boundary_row_dataframe(df, 1) == 2
    assert find_boundary_row_dataframe(df, 3) is None
