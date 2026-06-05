#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一常量定义模块
集中管理项目中使用的常量，避免重复定义
"""

# ============ 支持的语言配置 ============
# 键的顺序决定合并 JSON、翻译总表/CSV 等导出列的先后（zh → vn → th → en）
SUPPORTED_LANGUAGES = {
    'zh': {'name': '中文', 'code': 'zh', 'suffix': '_zh'},
    'vn': {'name': '越南语', 'code': 'vn', 'suffix': '_vn'},
    'th': {'name': '泰语', 'code': 'th', 'suffix': '_th'},
    'en': {'name': '英语', 'code': 'en', 'suffix': '_en'},
}

# 有序语言代码，供遍历与列对齐（与 SUPPORTED_LANGUAGES 的键一致）
TRANSLATION_LANGUAGE_CODES = tuple(SUPPORTED_LANGUAGES.keys())

# 合并字段导出 JSON 等使用的顶层大写键（如 "ZH", "EN"）
MERGED_JSON_LANGUAGE_KEYS = tuple(code.upper() for code in TRANSLATION_LANGUAGE_CODES)

# 翻译提取结果行里各语言对应的内部字段名（写入 Excel/CSV 时再映射为 ZH/VN/TH/EN 表头）
TRANSLATION_ROW_VALUE_KEYS = {
    'zh': 'chinese',
    'vn': 'vietnamese',
    'th': 'thai',
    'en': 'english',
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
