#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一常量定义模块
集中管理项目中使用的常量，避免重复定义
"""

# ============ 支持的语言配置 ============
SUPPORTED_LANGUAGES = {
    'zh': {'name': '中文', 'code': 'zh', 'suffix': '_zh'},
    'vn': {'name': '越南语', 'code': 'vn', 'suffix': '_vn'},
    'th': {'name': '泰语', 'code': 'th', 'suffix': '_th'}
}

# ============ 支持的文件扩展名 ============
SUPPORTED_EXCEL_EXTENSIONS = {'.xlsx', '.xls'}
SUPPORTED_MAPPING_FORMATS = {'.xlsx', '.xls', '.csv'}

# ============ Excel 行号常量 ============
FIELD_NAME_ROW = 5      # 字段名所在行
FIELD_TYPE_ROW = 6      # 字段类型所在行
DATA_START_ROW = 7      # 数据开始行

# ============ 字段类型 ============
EXPORTABLE_FIELD_TYPES = {'前端', '后端', '前后端'}  # 需要导出的字段类型
SKIP_FIELD_TYPE = '策划'  # 跳过的字段类型

# ============ 过滤关键字 ============
CONFIG_KEYWORDS = ('null', 'None', 'true', 'false', 'True', 'False')

# ============ 列标记 ============
COLUMN_MARKER = "c_"  # 用于标记列范围的标识符
