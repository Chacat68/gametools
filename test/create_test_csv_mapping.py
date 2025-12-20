#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试CSV映射文件
用于测试批量改表功能对CSV格式的支持
"""

import pandas as pd
import os

def create_test_csv_mapping():
    """创建测试CSV映射文件"""
    
    # 测试数据
    data = {
        'Table': [
            'armor_ancient.xlsx',
            'armor_ancient.xlsx',
            'weapon_master.xlsx',
            'weapon_master.xlsx',
            'skill_magic.xlsx'
        ],
        'Classification': [
            'des',
            'name',
            'des',
            'name',
            'des'
        ],
        'ID': [
            1001,
            1001,
            2001,
            2001,
            3001
        ],
        'VN': [
            '古代盔甲描述越南文',
            '古代盔甲名称越南文',
            '大师武器描述越南文',
            '大师武器名称越南文',
            '魔法技能描述越南文'
        ],
        'TH': [
            '古代盔甲描述泰文',
            '古代盔甲名称泰文',
            '大师武器描述泰文',
            '大师武器名称泰文',
            '魔法技能描述泰文'
        ],
        'EN': [
            'Ancient Armor Description',
            'Ancient Armor Name',
            'Master Weapon Description',
            'Master Weapon Name',
            'Magic Skill Description'
        ],
        'Support-CH': [
            '古代盔甲描述',
            '古代盔甲',
            '大师武器描述',
            '大师武器',
            '魔法技能描述'
        ]
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存为CSV文件
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, '测试映射表.csv')
    
    # 使用UTF-8编码保存（带BOM以便Excel正确识别）
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ 测试CSV映射文件已创建: {output_path}")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}")
    print(f"   - 列名: {list(df.columns)}")
    print("\n数据预览:")
    print(df.head())
    
    return output_path

if __name__ == '__main__':
    create_test_csv_mapping()
