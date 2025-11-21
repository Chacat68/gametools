#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多语言翻译提取进度显示 - 多表格版本
"""

import os
import json
import pandas as pd
from pathlib import Path

def create_multi_table_test():
    """创建包含多个表格的测试"""
    base_dir = "test_multi_lang_progress"
    
    folders = {
        'vn': os.path.join(base_dir, 'config'),
        'zh': os.path.join(base_dir, 'config_zh'),
        'th': os.path.join(base_dir, 'config_th')
    }
    
    # 创建目录
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
        print(f"✓ 创建目录: {folder}")
    
    # 创建多个测试表格
    tables_config = [
        {
            'name': '角色配置.xlsx',
            'sheet': '角色列表',
            'fields': ['id,策划', 'name_cn,前端', 'name_vn,前端', 'desc_cn,后端', 'model,策划'],
            'data_vn': [
                [1, 'Chiến binh', 'Chiến binh', 'Nhân vật mạnh mẽ', 'warrior_01'],
                [2, 'Pháp sư', 'Pháp sư', 'Nhân vật phép thuật', 'mage_01'],
                [3, 'Sát thủ', 'Sát thủ', 'Nhân vật nhanh nhẹn', 'assassin_01']
            ],
            'data_zh': [
                [1, '战士', '战士', '强大的角色', 'warrior_01'],
                [2, '法师', '法师', '魔法角色', 'mage_01'],
                [3, '刺客', '刺客', '敏捷角色', 'assassin_01']
            ],
            'data_th': [
                [1, 'นักรบ', 'นักรบ', 'ตัวละครที่แข็งแกร่ง', 'warrior_01'],
                [2, 'นักเวทย์', 'นักเวทย์', 'ตัวละครเวทมนตร์', 'mage_01'],
                [3, 'มือสังหาร', 'มือสังหาร', 'ตัวละครว่องไว', 'assassin_01']
            ]
        },
        {
            'name': '物品配置.xlsx',
            'sheet': '物品列表',
            'fields': ['id,策划', 'item_name,前端', 'item_desc,后端', 'type,策划'],
            'data_vn': [
                [1, 'Kiếm dài', 'Vũ khí công phá', 'weapon'],
                [2, 'Giáp nặng', 'Áo giáp phòng thủ', 'armor'],
                [3, 'Thuốc hồi máu', 'Phục hồi sinh lực', 'potion']
            ],
            'data_zh': [
                [1, '长剑', '攻击武器', 'weapon'],
                [2, '重甲', '防御护甲', 'armor'],
                [3, '生命药水', '恢复生命', 'potion']
            ],
            'data_th': [
                [1, 'ดาบยาว', 'อาวุธโจมตี', 'weapon'],
                [2, 'เกราะหนัก', 'เกราะป้องกัน', 'armor'],
                [3, 'ยาฟื้นฟู', 'ฟื้นฟูชีวิต', 'potion']
            ]
        },
        {
            'name': '任务配置.xlsx',
            'sheet': '任务列表',
            'fields': ['quest_id,策划', 'title,前端', 'desc,前后端', 'reward,策划'],
            'data_vn': [
                [1, 'Nhiệm vụ đầu tiên', 'Hoàn thành nhiệm vụ hướng dẫn', 'gold_100'],
                [2, 'Săn quái vật', 'Tiêu diệt 10 quái vật', 'exp_500']
            ],
            'data_zh': [
                [1, '第一个任务', '完成新手教程', 'gold_100'],
                [2, '猎杀怪物', '消灭10个怪物', 'exp_500']
            ],
            'data_th': [
                [1, 'ภารกิจแรก', 'ทำภารกิจแนะนำให้เสร็จ', 'gold_100'],
                [2, 'ล่ามอนสเตอร์', 'กำจัดมอนสเตอร์ 10 ตัว', 'exp_500']
            ]
        }
    ]
    
    # 创建表格文件
    json_tables = []
    for table_config in tables_config:
        for lang in ['vn', 'zh', 'th']:
            excel_path = os.path.join(folders[lang], table_config['name'])
            
            # 准备数据
            header_rows = [
                ['说明1', '说明2', '说明3', '说明4', '说明5'],
                ['字段类型', '字段类型', '字段类型', '字段类型', '字段类型'],
                ['类型1', '类型2', '类型3', '类型4', '类型5'],
                ['备注1', '备注2', '备注3', '备注4', '备注5']
            ]
            
            # 字段名行
            field_names = [f.split(',')[0] for f in table_config['fields']]
            header_rows.append(field_names)
            
            # 字段类型行
            field_types = [f.split(',')[1] for f in table_config['fields']]
            header_rows.append(field_types)
            
            # 数据行
            data_key = f'data_{lang}'
            data_rows = table_config[data_key]
            
            all_rows = header_rows + data_rows
            
            df = pd.DataFrame(all_rows)
            df.to_excel(excel_path, index=False, header=False)
        
        print(f"✓ 创建表格: {table_config['name']}")
        
        # 添加到JSON配置
        json_tables.append({
            "table_name": table_config['name'],
            "sheet_name": "Sheet1",  # 使用默认工作表名
            "fields_with_examples": table_config['fields']
        })
    
    # 创建JSON配置
    json_config = {
        "no_text_tables": [],
        "text_tables": json_tables
    }
    
    json_file = os.path.join(base_dir, 'field_config.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_config, f, ensure_ascii=False, indent=2)
    print(f"✓ 创建JSON配置: {json_file}")
    
    return folders, json_file

def test_progress_display():
    """测试进度显示"""
    print("\n" + "="*60)
    print("创建测试文件...")
    print("="*60 + "\n")
    
    folders, json_file = create_multi_table_test()
    
    print("\n" + "="*60)
    print("开始测试进度显示...")
    print("="*60 + "\n")
    
    from core.table_range_translator import TableRangeTranslator
    
    translator = TableRangeTranslator()
    
    # 构建语言目录字典
    lang_dirs = {
        'vn': folders['vn'],
        'zh': folders['zh'],
        'th': folders['th']
    }
    
    # 定义进度回调
    def progress_callback(msg):
        print(msg)
    
    # 处理数据（带进度显示）
    results = translator.process_with_json_config_multi_lang(
        json_file, lang_dirs, progress_callback=progress_callback)
    
    if results:
        print(f"\n{'='*60}")
        print(f"提取结果汇总")
        print(f"{'='*60}")
        print(f"总数据条数: {len(results)}")
        
        # 按表格统计
        table_stats = {}
        for row in results:
            table_name = row['table_name']
            if table_name not in table_stats:
                table_stats[table_name] = 0
            table_stats[table_name] += 1
        
        print("\n各表格数据量:")
        for table_name, count in table_stats.items():
            print(f"  • {table_name}: {count} 条")
        
        # 生成翻译总表
        output_file = "test_multi_lang_progress/翻译总表_进度测试.xlsx"
        success = translator.generate_translation_master_table_multi_lang(output_file)
        
        if success:
            print(f"\n✓ 翻译总表已生成: {output_file}")
        
        print("\n" + translator.get_processing_report())
    else:
        print("✗ 提取失败")

if __name__ == "__main__":
    test_progress_display()
