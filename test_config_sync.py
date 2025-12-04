#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel配置同步工具测试脚本
"""

import os
import sys
import shutil
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from core.excel_config_sync import ExcelConfigSync


def create_test_directories():
    """创建测试目录和文件"""
    test_base = Path("test_config_sync")
    
    # 创建目录结构
    source_dir = test_base / "source"
    target1_dir = test_base / "target1"
    target2_dir = test_base / "target2"
    
    for d in [source_dir, target1_dir, target2_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # 创建测试Excel文件
    import pandas as pd
    
    # 源文件
    source_data = {
        'ID': [1, 2, 3],
        'Name': ['源-A', '源-B', '源-C'],
        'Value': [100, 200, 300]
    }
    df_source = pd.DataFrame(source_data)
    df_source.to_excel(source_dir / "test1.xlsx", index=False)
    df_source.to_excel(source_dir / "test2.xlsx", index=False)
    
    # 目标文件1（旧数据）
    target1_data = {
        'ID': [1, 2, 3],
        'Name': ['目标1-A', '目标1-B', '目标1-C'],
        'Value': [10, 20, 30]
    }
    df_target1 = pd.DataFrame(target1_data)
    df_target1.to_excel(target1_dir / "test1.xlsx", index=False)
    df_target1.to_excel(target1_dir / "test2.xlsx", index=False)
    
    # 目标文件2（旧数据）
    target2_data = {
        'ID': [1, 2, 3],
        'Name': ['目标2-A', '目标2-B', '目标2-C'],
        'Value': [11, 22, 33]
    }
    df_target2 = pd.DataFrame(target2_data)
    df_target2.to_excel(target2_dir / "test1.xlsx", index=False)
    # test2.xlsx 故意不创建，测试跳过逻辑
    
    print(f"测试目录已创建: {test_base}")
    print(f"  源目录: {source_dir}")
    print(f"  目标目录1: {target1_dir}")
    print(f"  目标目录2: {target2_dir}")
    
    return str(source_dir), str(target1_dir), str(target2_dir)


def test_config_sync():
    """测试配置同步功能"""
    print("\n" + "=" * 60)
    print("Excel配置同步工具测试")
    print("=" * 60)
    
    # 创建测试数据
    source_dir, target1_dir, target2_dir = create_test_directories()
    
    # 创建同步器
    syncer = ExcelConfigSync()
    
    # 设置进度回调
    def progress_callback(msg, percentage=None):
        if percentage is not None:
            print(f"[{percentage:.1f}%] {msg}")
        else:
            print(f"[...] {msg}")
    
    syncer.set_progress_callback(progress_callback)
    
    # 测试文件匹配
    print("\n1. 测试文件匹配...")
    matching = syncer.find_matching_files(source_dir, [target1_dir, target2_dir])
    print(f"   匹配的文件: {list(matching.keys())}")
    
    # 执行同步
    print("\n2. 执行同步...")
    stats = syncer.sync_directories(
        source_dir=source_dir,
        target_dir1=target1_dir,
        target_dir2=target2_dir
    )
    
    # 显示统计
    print("\n3. 同步统计:")
    print(syncer.get_stats_summary())
    
    # 生成报告
    report_path = "test_config_sync/sync_report.xlsx"
    print(f"\n4. 生成报告: {report_path}")
    syncer.generate_sync_report(report_path)
    
    # 验证同步结果
    print("\n5. 验证同步结果...")
    import pandas as pd
    
    target1_df = pd.read_excel(os.path.join(target1_dir, "test1.xlsx"))
    print(f"   目标1/test1.xlsx 第一行Name: {target1_df['Name'].iloc[0]}")
    
    if target1_df['Name'].iloc[0] == '源-A':
        print("   ✓ 同步成功！")
    else:
        print("   ✗ 同步失败！")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def cleanup_test_data():
    """清理测试数据"""
    test_base = Path("test_config_sync")
    if test_base.exists():
        shutil.rmtree(test_base)
        print("测试目录已清理")


if __name__ == "__main__":
    try:
        test_config_sync()
    finally:
        # 可选：清理测试数据
        # cleanup_test_data()
        pass
