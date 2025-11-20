"""
查看翻译总表的详细内容
"""
import pandas as pd
import os

output_file = "test_table_range/translation_master_excel_position.xlsx"

if not os.path.exists(output_file):
    print(f"❌ 文件不存在: {output_file}")
    exit(1)

print("=" * 80)
print("翻译总表详细预览 - Excel位置格式测试")
print("=" * 80)

xl = pd.ExcelFile(output_file)

for sheet in xl.sheet_names:
    print(f"\n{'=' * 80}")
    print(f"📊 工作表: {sheet}")
    print("=" * 80)
    
    df = pd.read_excel(output_file, sheet_name=sheet)
    
    print(f"\n总行数: {len(df)}")
    print(f"列名: {', '.join(df.columns.tolist())}")
    
    print("\n前10行数据:")
    print("-" * 80)
    
    # 显示完整的前10行
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    print(df.head(10).to_string(index=False))
    
    # 统计Excel位置格式
    if 'Excel位置' in df.columns:
        print("\n" + "-" * 80)
        print("Excel位置统计:")
        positions = df['Excel位置'].tolist()
        print(f"  • 位置示例: {positions[:10]}")
        print(f"  • 总数: {len(positions)}")
        
        # 检查列字母分布
        col_letters = set([pos[0] if len(pos) > 0 else '' for pos in positions])
        print(f"  • 涉及的列: {sorted(col_letters)}")

print("\n" + "=" * 80)
print("✨ 预览完成！")
print("=" * 80)
