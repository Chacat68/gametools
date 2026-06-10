#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文本模式与内容过滤规则测试"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.text_patterns import (
    is_asset_identifier,
    is_filterable_content,
    is_translatable_text,
    contains_localized_text,
)
from core.table_range_translator import TableRangeTranslator


def test_asset_identifier_detection():
    asset_samples = [
        'ass_sss_',
        'ass_icon_001',
        'npc104_ui',
        'item_sword_001',
        'res_ui_btn_',
        'ITEM_002',
        'a_b',
    ]
    non_asset_samples = [
        'Hello World',
        'Sword',
        '1001',
        '中文描述',
        'Tiểu Long Nữ',
        'type-a',
        'ass.icon',
        '_leading',
    ]

    for sample in asset_samples:
        assert is_asset_identifier(sample), sample
        assert is_filterable_content(sample), sample

    for sample in non_asset_samples:
        assert not is_asset_identifier(sample), sample


def test_translator_skips_asset_identifiers():
    translator = TableRangeTranslator()

    assert not translator.is_valid_translation_text('ass_icon_hero')
    assert not translator.is_valid_translation_text('npc105_ui')
    assert translator.detect_language_type('ass_icon_hero') == '其他'
    assert translator.is_valid_translation_text('Hero Description')
    assert translator.is_valid_translation_text('这是一段中文')


def test_unified_translatable_text():
    assert not is_translatable_text('ass_sss_')
    assert not is_translatable_text('1001')
    assert not contains_localized_text('ass_icon_001')
    assert is_translatable_text('Hello World')
    assert is_translatable_text('中文描述')


def main():
    test_asset_identifier_detection()
    test_translator_skips_asset_identifiers()
    test_unified_translatable_text()
    print('text_patterns filter tests passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
