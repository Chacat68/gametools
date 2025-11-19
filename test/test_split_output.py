"""测试拆分输出格式（包含空表格和非空表格）"""
import os
import sys
import pandas as pd
import json

# 添加core目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.excel_field_extractor import ExcelFieldExtractor

def create_test_files():
    """创建测试文件：一个有文本内容，一个没有文本内容"""
    test_dir = os.path.join(os.path.dirname(__file__), 'test_output')
    os.makedirs(test_dir, exist_ok=True)
    
    # 文件1：有文本内容的表格
    df1 = pd.DataFrame({
        'c_classic_battle': ['标记1', '', '', '', '', ''],
        'level_name': ['字段名', '', '', '', '', '新手村'],
        'level_desc': ['描述', '', '', '', '', '这是一个简单的关卡'],
        'c_classic_battle_2': ['标记2', '', '', '', '', ''],
    })
    file1 = os.path.join(test_dir, 'has_text.xlsx')
    df1.to_excel(file1, index=False, sheet_name='关卡配置')
    
    # 文件2：没有文本内容的表格（只有英文和数字）
    df2 = pd.DataFrame({
        'c_classic_battle': ['marker1', '', '', '', '', ''],
        'level_id': ['id', '', '', '', '', '1001'],
        'level_type': ['type', '', '', '', '', 'normal'],
        'c_classic_battle_2': ['marker2', '', '', '', '', ''],
    })
    file2 = os.path.join(test_dir, 'no_text.xlsx')
    df2.to_excel(file2, index=False, sheet_name='配置表')
    
    print(f"✓ 测试文件已创建:")
    print(f"  - {file1}")
    print(f"  - {file2}")
    print()
    
    return test_dir, [file1, file2]

def test_split_output():
    """测试拆分输出功能"""
    print("=" * 70)
    print("测试拆分输出格式（空表格 vs 非空表格）")
    print("=" * 70)
    print()
    
    # 创建测试文件
    test_dir, test_files = create_test_files()
    
    # 初始化提取器
    extractor = ExcelFieldExtractor()
    
    # 提取字段
    print("开始提取字段...")
    results = []
    for file_path in test_files:
        result = extractor.extract_fields_from_excel(file_path)
        if result:
            results.extend(result)
    
    print(f"✓ 提取完成")
    print(f"  - 有文本表格数: {len(results)}")
    print(f"  - 无文本表格数: {len(extractor.empty_tables)}")
    print()
    
    # 导出到各种格式
    output_base = os.path.join(test_dir, 'split_test_result')
    
    print("导出到 JSON...")
    json_file = extractor.export_to_json(results, output_base + '.json')
    
    print("导出到 CSV...")
    csv_file = extractor.export_to_csv(results, output_base + '.csv')
    
    print("导出到 Excel...")
    excel_file = extractor.export_to_excel(results, output_base + '.xlsx')
    print()
    
    # 验证 JSON 结构
    print("=" * 70)
    print("验证 JSON 输出结构:")
    print("=" * 70)
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    print(json.dumps(json_data, ensure_ascii=False, indent=2))
    print()
    
    # 验证结构
    assert 'empty_tables' in json_data, "JSON 缺少 empty_tables 字段"
    assert 'tables_with_text' in json_data, "JSON 缺少 tables_with_text 字段"
    assert len(json_data['empty_tables']) == 1, f"应该有1个空表格，实际: {len(json_data['empty_tables'])}"
    assert len(json_data['tables_with_text']) == 1, f"应该有1个非空表格，实际: {len(json_data['tables_with_text'])}"
    
    print("=" * 70)
    print("✅ 所有验证通过！")
    print("=" * 70)
    print()
    print("输出文件:")
    print(f"  - JSON: {json_file}")
    print(f"  - CSV: {csv_file}")
    print(f"  - Excel: {excel_file}")
    print()

if __name__ == '__main__':
    test_split_output()
