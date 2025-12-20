#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试批量改表功能对翻译提取CSV格式的支持
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.batch_excel_modifier import BatchExcelModifier
import pandas as pd


def test_translation_csv_format():
    """测试翻译提取CSV格式支持"""
    
    print("=" * 60)
    print("测试批量改表功能 - 翻译提取CSV格式支持")
    print("=" * 60)
    
    # 测试文件路径
    csv_path = Path(__file__).parent.parent / "docs" / "系统翻译提取_20251219_165646_translated.csv"
    
    if not csv_path.exists():
        print(f"\n❌ 测试文件不存在: {csv_path}")
        return False
    
    print(f"\n📂 测试文件: {csv_path.name}")
    
    # 创建批量改表实例
    modifier = BatchExcelModifier()
    
    # 测试1：加载翻译提取格式的CSV
    print("\n【测试1】加载翻译提取格式CSV")
    df, columns = modifier.load_mapping_table(str(csv_path))
    
    if df.empty:
        print("❌ CSV加载失败")
        return False
    
    print(f"✅ 成功加载CSV文件")
    print(f"   - 总行数: {len(df)}")
    print(f"   - 列名: {columns}")
    
    # 检查转换后的格式
    print("\n【测试2】检查格式转换")
    required_cols = ['Table', 'Classification', 'ID']
    missing_cols = [col for col in required_cols if col not in columns]
    
    if missing_cols:
        print(f"❌ 缺少必需列: {missing_cols}")
        return False
    
    print(f"✅ 格式转换成功")
    print(f"   - Table列: ✓")
    print(f"   - Classification列: ✓")
    print(f"   - ID列: ✓")
    
    # 检查语言列
    lang_cols = [col for col in columns if col not in required_cols]
    print(f"   - 语言列: {lang_cols}")
    
    # 测试3：查看转换后的数据样例
    print("\n【测试3】数据样例（前5行）")
    print(df.head().to_string())
    
    # 测试4：验证ID提取
    print("\n【测试4】验证ID提取")
    sample_ids = df['ID'].head(10).tolist()
    print(f"   - 样例ID: {sample_ids}")
    
    if all(pd.isna(id) for id in sample_ids):
        print("❌ ID提取失败，所有ID都是空值")
        return False
    
    print("✅ ID提取正常")
    
    # 测试5：统计信息
    print("\n【测试5】统计信息")
    print(f"   - 总数据行: {len(df)}")
    print(f"   - 唯一表文件数: {df['Table'].nunique()}")
    print(f"   - 字段类型数: {df['Classification'].nunique()}")
    print(f"   - Classification统计:")
    for field, count in df['Classification'].value_counts().head(5).items():
        print(f"     • {field}: {count}行")
    
    # 测试6：表文件统计
    print("\n【测试6】表文件分布（前10个）")
    for table, count in df['Table'].value_counts().head(10).items():
        print(f"   • {table}: {count}行")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！翻译提取CSV格式支持正常")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = test_translation_csv_format()
    if not success:
        sys.exit(1)
