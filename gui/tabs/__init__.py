# -*- coding: utf-8 -*-
"""
GUI标签页模块包
提供标签页基类和独立标签页模块
"""

from .base_tab import BaseTab
from .cross_project_tab import CrossProjectTranslatorTab
from .json_detector_tab import JsonDetectorTab
from .about_tab import AboutTab
from .sheet_splitter_tab import SheetSplitterTab
from .field_extractor_tab import FieldExtractorTab
from .table_range_translator_tab import TableRangeTranslatorTab
from .batch_modifier_tab import BatchModifierTab
from .config_sync_tab import ConfigSyncTab
from .csv_converter_tab import CsvConverterTab

__all__ = [
    'BaseTab',
    'CrossProjectTranslatorTab',
    'JsonDetectorTab',
    'AboutTab',
    'SheetSplitterTab',
    'FieldExtractorTab',
    'TableRangeTranslatorTab',
    'BatchModifierTab',
    'ConfigSyncTab',
    'CsvConverterTab'
]
