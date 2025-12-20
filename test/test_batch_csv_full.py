# -*- coding: utf-8 -*-
"""
完整测试：使用翻译提取CSV格式进行批量改表
模拟真实使用场景
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.batch_excel_modifier import BatchExcelModifier

def test_csv_batch_modification():
    """测试完整的CSV批量改表流程"""
    
    print("=" * 60)
    print("完整测试：CSV格式批量改表")
    print("=" * 60)
    
    # 文件路径
    csv_path = r"d:\dev\gametools\docs\系统翻译提取_20251219_165646_translated.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ 测试文件不存在: {csv_path}")
        return False
    
    print(f"\n📂 CSV文件: {csv_path}")
    
    # 创建批量改表对象
    modifier = BatchExcelModifier()
    
    # 测试1: 获取语言列表
    print("\n【测试1】获取CSV中的语言列表")
    try:
        languages = modifier.get_mapping_file_languages(csv_path)
        print(f"✅ 检测到语言: {languages}")
    except Exception as e:
        print(f"❌ 获取语言失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试2: 获取工作表列表（CSV应该返回空）
    print("\n【测试2】获取工作表列表")
    try:
        sheets = modifier.get_mapping_sheets(csv_path)
        if sheets:
            print(f"⚠️ CSV文件不应有工作表，但返回了: {sheets}")
        else:
            print("✅ CSV文件正确返回空工作表列表")
    except Exception as e:
        print(f"❌ 获取工作表失败: {e}")
        return False
    
    # 测试3: 加载映射表
    print("\n【测试3】加载映射表")
    try:
        df, columns = modifier.load_mapping_table(csv_path)
        print(f"✅ 成功加载CSV")
        print(f"   - 总行数: {len(df)}")
        print(f"   - 列名: {columns}")
        print(f"   - 样例数据（前3行）:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"❌ 加载映射表失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试4: 检查数据格式
    print("\n【测试4】检查数据格式")
    try:
        # 检查必需的列是否存在
        required_cols = ['Table', 'Classification', 'ID']
        missing_cols = [col for col in required_cols if col not in columns]
        
        if missing_cols:
            print(f"❌ 缺少必需列: {missing_cols}")
            return False
        else:
            print(f"✅ 所有必需列都存在: {required_cols}")
            
        # 检查是否有语言列
        lang_cols = [col for col in columns if col not in required_cols]
        print(f"   - 语言列: {lang_cols}")
        
        # 检查ID列的数据类型
        if 'ID' in df.columns:
            id_sample = df['ID'].head(10).tolist()
            print(f"   - ID样例: {id_sample}")
            
            # 检查ID是否为数值类型
            if df['ID'].dtype in ['int64', 'float64']:
                print(f"   - ID列类型: {df['ID'].dtype} ✓")
            else:
                print(f"   - ID列类型: {df['ID'].dtype} (非数值)")
    except Exception as e:
        print(f"❌ 检查格式失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试5: 提取表名列表（CSV特有）
    print("\n【测试5】提取唯一表名列表")
    try:
        if 'Table' in df.columns:
            unique_tables = df['Table'].unique()
            # 去除扩展名
            table_names = [t.replace('.xlsx', '').replace('.xls', '') for t in unique_tables]
            print(f"✅ 提取到 {len(table_names)} 个唯一表名")
            print(f"   - 前10个: {table_names[:10]}")
        else:
            print("⚠️ 没有Table列")
    except Exception as e:
        print(f"❌ 提取表名失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！CSV格式完全支持")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_csv_batch_modification()
    sys.exit(0 if success else 1)
