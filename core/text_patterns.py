#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一文本模式模块
集中管理项目中使用的正则表达式与单元格内容过滤规则，避免重复定义。

各工具（字段导出、多语言提取、批量改表等）判断「是否为待翻译文本」时，
应统一使用 is_translatable_text() 或 is_filterable_content()，勿在各模块重复实现。
"""

import re
from typing import Optional


# ============ Unicode 范围定义 ============
# 中文：CJK统一汉字 + CJK扩展A
CHINESE_UNICODE_RANGE = r'\u4e00-\u9fff\u3400-\u4dbf'
# 越南文：带音标的拉丁字母
VIETNAMESE_UNICODE_RANGE = r'\u00C0-\u1EF9'
# 泰文
THAI_UNICODE_RANGE = r'\u0E00-\u0E7F'


# ============ 预编译的正则表达式 ============

# 语言检测模式
CHINESE_PATTERN = re.compile(rf'[{CHINESE_UNICODE_RANGE}]')
VIETNAMESE_PATTERN = re.compile(rf'[{VIETNAMESE_UNICODE_RANGE}]')
THAI_PATTERN = re.compile(rf'[{THAI_UNICODE_RANGE}]')

# 拉丁字母（用于识别英语等拉丁文案）
LATIN_LETTERS_PATTERN = re.compile(r'[A-Za-z]')

# 综合文本模式：匹配中文、越南文、泰文或拉丁字母
TEXT_PATTERN = re.compile(
    rf'[{CHINESE_UNICODE_RANGE}{VIETNAMESE_UNICODE_RANGE}{THAI_UNICODE_RANGE}]|[A-Za-z]'
)

# ============ 内容过滤模式 ============

# 空括号: {} 或 []
EMPTY_BRACES_PATTERN = re.compile(r'^\s*[\{\[]\s*[\}\]]\s*$')

# 数组格式: [2,99] 或 {2,99} 或 [] 或 {}
ARRAY_PATTERN = re.compile(r'^\s*[\[\{]\s*[\d\s,\.\-]*\s*[\]\}]\s*$')

# 对象数组: [{},{}] 或 [{22},{333}]
OBJECT_ARRAY_PATTERN = re.compile(r'^\s*\[\s*(\{\s*[\d\s,\.\-]*\s*\}\s*,?\s*)+\]\s*$')

# 纯数字（包括负数和小数）
PURE_NUMBER_PATTERN = re.compile(r'^\s*[\-]?[\d\.]+\s*$')

# 游戏资源/配置标识符: 由「英文/数字 + 下划线」片段组成
# 示例: ass_icon_001, ass_sss_, npc104_ui
ASSET_IDENTIFIER_PATTERN = re.compile(r'^(?:[A-Za-z0-9]+_)+[A-Za-z0-9]*$')

# Excel单元格引用: A1, B5, AA100 等
CELL_REFERENCE_PATTERN = re.compile(r'^([A-Z]+)(\d+)$')


# ============ 辅助函数 ============

def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(CHINESE_PATTERN.search(text))


def contains_vietnamese(text: str) -> bool:
    """检查文本是否包含越南文字符"""
    return bool(VIETNAMESE_PATTERN.search(text))


def contains_thai(text: str) -> bool:
    """检查文本是否包含泰文字符"""
    return bool(THAI_PATTERN.search(text))


def contains_latin_letters(text: str) -> bool:
    """检查文本是否包含拉丁字母（常用于识别英文文案）"""
    return bool(LATIN_LETTERS_PATTERN.search(text))


def contains_localized_text(text: str) -> bool:
    """
    检查文本是否包含需要本地化的字符（中文、越南文、泰文、拉丁字母）。

    会先排除 is_filterable_content 判定为配置/占位的内容（含资源标识符）。
    """
    if not text:
        return False
    value_str = str(text).strip()
    if not value_str or is_filterable_content(value_str):
        return False
    return bool(TEXT_PATTERN.search(value_str))


def is_translatable_text(value) -> bool:
    """
    判断单元格值是否应视为待翻译/本地化文本（全项目统一入口）。

    字段导出、多语言提取、批量改表等工具均应通过此函数或 is_filterable_content
    过滤纯数字、数组占位、游戏资源标识符（英文/数字 + 下划线片段）等非文案内容。
    """
    if value is None:
        return False
    value_str = str(value).strip()
    if not value_str or value_str.lower() == 'nan':
        return False
    return contains_localized_text(value_str)


def contains_cjk_vietnamese_or_thai(text: str) -> bool:
    """
    是否包含中文、越南文或泰文字符（不含仅拉丁字母）。

    用于字段导出器中「排除名字段」的列内容抽样：纯 ITEM_001、armor_a 等
    不应视为本地化文案，从而仍过滤 name/code/model 等列；若列内确有中越泰字符则保留，避免误伤。
    """
    return bool(
        contains_chinese(text)
        or contains_vietnamese(text)
        or contains_thai(text)
    )


def is_asset_identifier(value_str: str) -> bool:
    """
    检查是否为游戏资源/配置标识符。

    格式：由一个或多个「英文/数字 + 下划线」片段组成，末尾可再接一段英文/数字。
    示例: ass_sss_, ass_icon_001, npc104_ui
    """
    if not value_str:
        return False
    return bool(ASSET_IDENTIFIER_PATTERN.match(value_str))


def is_filterable_content(value_str: str) -> bool:
    """
    检查内容是否应该被过滤（不需要处理的内容）
    
    过滤条件：
    - 空括号 {} 或 []
    - 数组格式 [2,99] 或 {2,99}
    - 对象数组 [{},{}]
    - 纯数字
    - 配置关键字 null, None, true, false 等
    - 游戏资源/配置标识符（英文/数字 + 下划线片段，如 ass_sss_、ass_icon_001）
    
    Args:
        value_str: 要检查的字符串（已经strip过的）
        
    Returns:
        bool: 如果应该被过滤返回 True
    """
    if not value_str:
        return True
    
    # 空括号
    if EMPTY_BRACES_PATTERN.match(value_str):
        return True
    
    # 数组格式
    if ARRAY_PATTERN.match(value_str):
        return True
    
    # 对象数组
    if OBJECT_ARRAY_PATTERN.match(value_str):
        return True
    
    # 纯数字
    if PURE_NUMBER_PATTERN.match(value_str):
        return True
    
    # 配置关键字
    if value_str in ('null', 'None', 'true', 'false', 'True', 'False'):
        return True

    # 游戏资源/配置标识符（英文导出时易被误判为待翻译文案）
    if is_asset_identifier(value_str):
        return True
    
    return False


def parse_cell_reference(cell_ref: str) -> Optional[tuple]:
    """
    解析Excel单元格引用
    
    Args:
        cell_ref: 单元格引用字符串，如 "A1", "B5", "AA100"
        
    Returns:
        (row, col) 元组，如果解析失败返回 None
        row 和 col 都是从1开始的数字
    """
    match = CELL_REFERENCE_PATTERN.match(cell_ref.upper().strip())
    if not match:
        return None
    
    col_str, row_str = match.groups()
    
    # 将列字母转换为数字
    col_num = 0
    for char in col_str:
        col_num = col_num * 26 + (ord(char) - ord('A') + 1)
    
    row_num = int(row_str)
    
    return (row_num, col_num)
