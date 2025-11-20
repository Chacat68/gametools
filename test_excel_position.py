"""
测试Excel位置格式输出
"""
from core.table_range_translator import TableRangeTranslator
import os
import pandas as pd

def test_excel_position():
    """测试Excel位置格式显示"""
    
    # 创建测试实例
    translator = TableRangeTranslator()
    
    # 测试列索引转换函数
    print("=" * 70)
    print("列索引转换测试")
    print("=" * 70)
    test_indices = [0, 1, 5, 25, 26, 27, 51, 52, 701, 702]
    for idx in test_indices:
        letter = translator.column_index_to_letter(idx)
        print(f"列索引 {idx:4d} -> Excel列字母: {letter}")
    
    print("\n" + "=" * 70)
    print("实际文件提取测试")
    print("=" * 70)
    
    # 使用之前的测试文件
    json_file = "test_table_range/field_config.json"
    excel_dir = "test_table_range"
    output_file = "test_table_range/translation_master_excel_position.xlsx"
    
    if not os.path.exists(json_file):
        print(f"❌ 测试文件不存在: {json_file}")
        print("请先运行 create_test_table_range.py 生成测试文件")
        return
    
    # 处理文件
    print(f"\n📂 JSON配置: {json_file}")
    print(f"📂 Excel目录: {excel_dir}")
    print(f"📂 输出文件: {output_file}\n")
    
    # 步骤1: 处理JSON配置和Excel文件
    all_data = translator.process_with_json_config(json_file, excel_dir)
    
    # 步骤2: 生成翻译总表
    translator.generate_translation_master_table(output_file)
    
    stats = translator.processing_stats
    
    # 显示统计信息
    print("\n" + "=" * 70)
    print("处理统计")
    print("=" * 70)
    print(f"✅ 处理的表格: {stats.get('processed_tables', 0)} 个")
    print(f"✅ 提取的行数: {stats.get('total_rows', 0)} 行")
    print(f"✅ 可导出字段: {stats.get('exportable_fields', 0)} 个")
    print(f"⏭️  跳过的字段: {stats.get('skipped_fields', 0)} 个（策划类字段）")
    
    # 读取输出文件检查Excel位置格式
    if os.path.exists(output_file):
        print("\n" + "=" * 70)
        print("输出文件预览（前5行）")
        print("=" * 70)
        
        xl = pd.ExcelFile(output_file)
        for sheet in xl.sheet_names[:1]:  # 只看第一个表
            df = pd.read_excel(output_file, sheet_name=sheet)
            print(f"\n📊 工作表: {sheet}")
            print(df.head())
            
            if 'Excel位置' in df.columns:
                print(f"\n✅ Excel位置列示例: {df['Excel位置'].head(3).tolist()}")
            else:
                print("\n❌ 未找到'Excel位置'列")
    
    print("\n✨ 测试完成！")

if __name__ == "__main__":
    test_excel_position()
