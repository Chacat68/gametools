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

# ============ Excel 表布局规范（策划表标准）============
# 所有依赖「表头 + 数据区」的工具应使用下列常量，避免各处硬编码 5/6/7。
# 物理行号：与 Excel 界面行号一致（1-based）。
# 若将来表头行数变更，只需改此处并回归测试各模块。
#
# | Excel 行 | 含义 |
# |---------|------|
# | 1–4     | 说明/预留等（工具一般不解析） |
# | FIELD_NAME_ROW   | 字段英文名/列名 |
# | FIELD_TYPE_ROW   | 字段类型（策划/前端/后端/前后端） |
# | DATA_START_ROW 起 | 正式数据行（至含 ROW_BOUNDARY_KEYWORD 的边界行为止，见各模块） |
#
# 列范围：可选在两个「值严格等于 COLUMN_MARKER 的单元格」之间扫描，
# 字段名以 COLUMN_MARKER 开头（如 c_xxx）的列是数据列，不是边界标记。
FIELD_NAME_ROW = 5      # 字段名所在行
FIELD_TYPE_ROW = 6      # 字段类型所在行
DATA_START_ROW = 7      # 数据开始行

# pandas DataFrame 行索引（0-based），与上行物理行号一一对应
FIELD_NAME_ROW_INDEX = FIELD_NAME_ROW - 1
FIELD_TYPE_ROW_INDEX = FIELD_TYPE_ROW - 1
DATA_START_ROW_INDEX = DATA_START_ROW - 1

# ============ 字段类型 ============
EXPORTABLE_FIELD_TYPES = {'前端', '后端', '前后端'}  # 需要导出的字段类型
SKIP_FIELD_TYPE = '策划'  # 跳过的字段类型

# ============ 过滤关键字 ============
CONFIG_KEYWORDS = ('null', 'None', 'true', 'false', 'True', 'False')

# ============ 列标记 ============
COLUMN_MARKER = "c_"  # 用于标记列范围的标识符

# ============ 行边界（数据区遍历下限）============
# 当某一行的任意单元格在 strip 后、按小写比较等于 ROW_BOUNDARY_KEYWORD 时，视为「数据区结束标记行」：
# - 该行本身不再作为数据解析；
# - 从该行起向下不再遍历（立即结束行扫描循环）。
# 字段导出、多语言提取等模块在按行遍历时应遵守此规则（可先 _find_boundary_row 缩小 range，再在循环内防御性检测）。
ROW_BOUNDARY_KEYWORD = "over"

# ============ 字段导出 ============
# 多语言 JSON 导出时写入输出目录的合并配置文件名（与多语言提取页衔接）
FIELD_EXTRACTION_MERGED_JSON_NAME = "field_extraction_result_merged.json"
