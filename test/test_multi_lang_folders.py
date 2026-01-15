#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多语言翻译提取 - 多文件夹支持
"""

import os
import json
import sys
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径（确保可导入 core 包）
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_test_folders():
    """创建测试文件夹结构"""
    # 根据图片中的文件夹结构创建测试目录
    base_dir = "test_multi_lang"
    
    folders = {
        'vn': os.path.join(base_dir, 'config'),           # 越南文（无后缀）
        'zh': os.path.join(base_dir, 'config_zh'),        # 中文（_zh后缀）
        'th': os.path.join(base_dir, 'config_th')         # 泰文（_th后缀）
    }
    
    # 创建目录
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
        print(f"✓ 创建目录: {folder}")
    
    # 创建测试Excel文件
    test_data = {
        'vn': [
            ['说明1', '说明2', '说明3', '说明4'],
            ['字段类型', '字段类型', '字段类型', '字段类型'],
            ['类型1', '类型2', '类型3', '类型4'],
            ['备注1', '备注2', '备注3', '备注4'],
            ['id', 'name_cn', 'desc_cn', 'type'],  # 第5行：字段名
            ['策划', '前端', '后端', '策划'],        # 第6行：字段类型
            [1, 'Vũ khí', 'Vũ khí mạnh mẽ', 'weapon'],
            [2, 'Áo giáp', 'Áo giáp bảo vệ', 'armor']
        ],
        'zh': [
            ['说明1', '说明2', '说明3', '说明4'],
            ['字段类型', '字段类型', '字段类型', '字段类型'],
            ['类型1', '类型2', '类型3', '类型4'],
            ['备注1', '备注2', '备注3', '备注4'],
            ['id', 'name_cn', 'desc_cn', 'type'],
            ['策划', '前端', '后端', '策划'],
            [1, '武器', '强大的武器', 'weapon'],
            [2, '护甲', '防护装甲', 'armor']
        ],
        'th': [
            ['说明1', '说明2', '说明3', '说明4'],
            ['字段类型', '字段类型', '字段类型', '字段类型'],
            ['类型1', '类型2', '类型3', '类型4'],
            ['备注1', '备注2', '备注3', '备注4'],
            ['id', 'name_cn', 'desc_cn', 'type'],
            ['策划', '前端', '后端', '策划'],
            [1, 'อาวุธ', 'อาวุธที่แข็งแกร่ง', 'weapon'],
            [2, 'เกราะ', 'เกราะป้องกัน', 'armor']
        ]
    }
    
    # 为每个语言创建Excel文件
    for lang, folder in folders.items():
        excel_file = os.path.join(folder, '物品配置.xlsx')
        df = pd.DataFrame(test_data[lang])
        df.to_excel(excel_file, index=False, header=False)
        print(f"✓ 创建Excel: {excel_file}")
    
    # 创建JSON配置文件
    json_config = {
        "no_text_tables": [],
        "text_tables": [
            {
                "table_name": "物品配置.xlsx",
                "sheet_name": "Sheet1",
                "fields_with_examples": [
                    "id,策划",
                    "name_cn,前端",
                    "desc_cn,后端",
                    "type,策划"
                ]
            }
        ]
    }
    
    json_file = os.path.join(base_dir, 'field_config.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_config, f, ensure_ascii=False, indent=2)
    print(f"✓ 创建JSON配置: {json_file}")
    
    # 创建README
    readme_content = f"""# 多语言翻译提取测试

## 文件夹结构

```
{base_dir}/
├── config/              # 越南文目录（无后缀）
│   └── 物品配置.xlsx
├── config_zh/           # 中文目录（_zh后缀）
│   └── 物品配置.xlsx
├── config_th/           # 泰文目录（_th后缀）
│   └── 物品配置.xlsx
└── field_config.json    # JSON配置文件
```

## 使用方法

### GUI测试
1. 启动 gametools
2. 选择"多语言翻译提取"页签
3. 选择JSON配置: {json_file}
4. 选择越南文目录: {folders['vn']}
5. 选择中文目录: {folders['zh']}
6. 选择泰文目录: {folders['th']}
7. 点击"开始提取"

### 命令行测试
```bash
python -c "from core.table_range_translator import TableRangeTranslator; \\
t = TableRangeTranslator(); \\
results = t.process_with_json_config_multi_lang('{json_file}', {{'vn': '{folders['vn']}', 'zh': '{folders['zh']}', 'th': '{folders['th']}'}}); \\
t.generate_translation_master_table_multi_lang('{base_dir}/翻译总表.xlsx'); \\
print(t.get_processing_report())"
```

## 预期结果

生成的翻译总表包含：
- 工作表名称: 物品配置
- 列: 字段名 | 字段类型 | Excel位置 | 中文内容 | 越南文 | 泰文
- 只包含 name_cn 和 desc_cn 两个字段（id和type是策划字段，被过滤）
"""
    
    readme_file = os.path.join(base_dir, 'README.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ 创建README: {readme_file}")
    
    return folders, json_file

def test_extraction():
    """测试提取功能"""
    print("\n" + "="*60)
    print("创建测试文件...")
    print("="*60 + "\n")
    
    folders, json_file = create_test_folders()
    
    print("\n" + "="*60)
    print("开始测试提取...")
    print("="*60 + "\n")
    
    from core.table_range_translator import TableRangeTranslator
    
    translator = TableRangeTranslator()
    
    # 构建语言目录字典
    lang_dirs = {
        'vn': folders['vn'],
        'zh': folders['zh'],
        'th': folders['th']
    }
    
    # 处理数据
    results = translator.process_with_json_config_multi_lang(json_file, lang_dirs)
    
    if results:
        print(f"\n✓ 成功提取 {len(results)} 条数据\n")
        
        # 显示前几条数据
        print("数据示例:")
        for i, row in enumerate(results[:4], 1):
            print(f"\n{i}. 字段: {row['field_name']} ({row['field_type']})")
            print(f"   位置: {row['excel_position']}")
            print(f"   中文: {row['chinese']}")
            print(f"   越南文: {row['vietnamese']}")
            print(f"   泰文: {row['thai']}")
        
        # 生成翻译总表
        output_file = "test_multi_lang/翻译总表.xlsx"
        success = translator.generate_translation_master_table_multi_lang(output_file)
        
        if success:
            print(f"\n✓ 翻译总表已生成: {output_file}")
        
        # 显示报告
        print("\n" + translator.get_processing_report())
    else:
        print("✗ 提取失败")

if __name__ == "__main__":
    test_extraction()
