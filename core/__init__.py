#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameTools Core 模块
初始化日志配置和公共组件
"""

import logging
import sys
from pathlib import Path

# ============ 日志配置 ============
def setup_logging(level=logging.INFO, log_to_console=True, log_to_file=False, log_dir=None):
    """
    设置全局日志配置
    
    Args:
        level: 日志级别
        log_to_console: 是否输出到控制台
        log_to_file: 是否输出到文件
        log_dir: 日志目录（仅当 log_to_file=True 时有效）
    """
    # 格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
    
    # 文件处理器
    if log_to_file and log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        log_file = log_path / f"gametools_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # 配置根日志器
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers if handlers else None
    )


# 默认日志配置（在模块首次导入时执行）
# 检查是否已经配置过日志，避免重复配置
if not logging.getLogger().handlers:
    setup_logging()


# ============ 版本信息 ============
try:
    from version import __version__, __build_date__
except ImportError:
    __version__ = "unknown"
    __build_date__ = "unknown"


# ============ 常量导出 ============
from core.constants import (
    SUPPORTED_LANGUAGES,
    SUPPORTED_EXCEL_EXTENSIONS,
    SUPPORTED_MAPPING_FORMATS,
    EXPORTABLE_FIELD_TYPES,
    FIELD_NAME_ROW,
    FIELD_TYPE_ROW,
    DATA_START_ROW,
    COLUMN_MARKER,
)

from core.text_patterns import (
    CHINESE_PATTERN,
    VIETNAMESE_PATTERN,
    THAI_PATTERN,
    TEXT_PATTERN,
    contains_chinese,
    contains_vietnamese,
    contains_thai,
    contains_localized_text,
    is_filterable_content,
    parse_cell_reference,
)

__all__ = [
    # 日志
    'setup_logging',
    # 常量
    'SUPPORTED_LANGUAGES',
    'SUPPORTED_EXCEL_EXTENSIONS',
    'SUPPORTED_MAPPING_FORMATS',
    'EXPORTABLE_FIELD_TYPES',
    'FIELD_NAME_ROW',
    'FIELD_TYPE_ROW',
    'DATA_START_ROW',
    'COLUMN_MARKER',
    # 文本模式
    'CHINESE_PATTERN',
    'VIETNAMESE_PATTERN',
    'THAI_PATTERN',
    'TEXT_PATTERN',
    'contains_chinese',
    'contains_vietnamese',
    'contains_thai',
    'contains_localized_text',
    'is_filterable_content',
    'parse_cell_reference',
    # 版本
    '__version__',
    '__build_date__',
]
