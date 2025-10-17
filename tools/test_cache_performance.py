#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能对比测试脚本
演示带缓存和不带缓存的翻译对应工具的性能差异
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cross_project_translator import CrossProjectTranslator
from core.cross_project_translator_cached import CrossProjectTranslatorWithCache


def create_test_files():
    """创建测试文件"""
    test_dir = Path("test_cache_demo")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试数据文件
    data_files = [
        "table1.xlsx",
        "table2.xlsx",
        "table3.xlsx"
    ]
    
    for i, filename in enumerate(data_files):
        filepath = test_dir / filename
        
        # 创建含有多个工作表的Excel文件
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_idx in range(3):
                sheet_name = f"Sheet{sheet_idx+1}"
                # 创建包含100行50列的测试数据
                data = {
                    f'Column{j}': [f"Data_{i}_{sheet_idx}_{j}_{k}" for k in range(100)]
                    for j in range(50)
                }
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 创建映射文件
    mapping_data = {
        '文件名': [f"table{(i%3)+1}.xlsx" for i in range(50)],
        '位置': [f"Sheet{(i%3)+1}!A{(i%50)+1}" for i in range(50)]
    }
    
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df.to_excel(test_dir / "mapping.xlsx", index=False)
    
    return test_dir


def test_original_translator(test_dir: Path):
    """测试原始翻译对应工具（无缓存）"""
    print("\n" + "="*60)
    print("测试原始翻译对应工具（无缓存）")
    print("="*60)
    
    translator = CrossProjectTranslator()
    
    start_time = time.time()
    results = translator.process_translation_mapping(
        str(test_dir / "mapping.xlsx"),
        str(test_dir)
    )
    elapsed_time = time.time() - start_time
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    
    print(f"处理时间: {elapsed_time:.2f} 秒")
    print(f"成功数: {success_count}/{len(results)}")
    
    return elapsed_time


def test_cached_translator(test_dir: Path):
    """测试缓存版翻译对应工具"""
    print("\n" + "="*60)
    print("测试缓存版翻译对应工具")
    print("="*60)
    
    # 第一次运行（冷启动，缓存未命中）
    print("\n--- 第一次运行（冷启动）---")
    translator = CrossProjectTranslatorWithCache(
        cache_dir=str(Path("test_cache_demo/.cache")),
        enable_file_cache=True,
        cache_ttl=3600
    )
    
    start_time = time.time()
    results1 = translator.process_translation_mapping(
        str(test_dir / "mapping.xlsx"),
        str(test_dir)
    )
    elapsed_time_first = time.time() - start_time
    
    success_count = sum(1 for r in results1 if r['status'] == 'success')
    cache_stats_1 = translator.get_cache_stats()
    
    print(f"处理时间: {elapsed_time_first:.2f} 秒")
    print(f"成功数: {success_count}/{len(results1)}")
    print(f"缓存命中: {cache_stats_1['custom']['cache_hits']}")
    print(f"缓存未命中: {cache_stats_1['custom']['cache_misses']}")
    print(f"命中率: {cache_stats_1['custom']['hit_rate']}")
    
    # 第二次运行（热启动，缓存命中）
    print("\n--- 第二次运行（热启动，利用缓存）---")
    
    start_time = time.time()
    results2 = translator.process_translation_mapping(
        str(test_dir / "mapping.xlsx"),
        str(test_dir)
    )
    elapsed_time_second = time.time() - start_time
    
    success_count = sum(1 for r in results2 if r['status'] == 'success')
    cache_stats_2 = translator.get_cache_stats()
    
    print(f"处理时间: {elapsed_time_second:.2f} 秒")
    print(f"成功数: {success_count}/{len(results2)}")
    print(f"缓存命中: {cache_stats_2['custom']['cache_hits']}")
    print(f"缓存未命中: {cache_stats_2['custom']['cache_misses']}")
    print(f"命中率: {cache_stats_2['custom']['hit_rate']}")
    
    # 性能改进
    improvement = (elapsed_time_first - elapsed_time_second) / elapsed_time_first * 100 if elapsed_time_first > 0 else 0
    
    return elapsed_time_first, elapsed_time_second, improvement


def performance_comparison():
    """性能对比测试"""
    print("\n" + "="*60)
    print("翻译对应工具缓存性能对比测试")
    print("="*60)
    
    # 创建测试文件
    test_dir = create_test_files()
    print(f"\n测试文件已创建在: {test_dir}")
    
    # 测试原始工具
    original_time = test_original_translator(test_dir)
    
    # 测试缓存工具
    cached_time_first, cached_time_second, improvement = test_cached_translator(test_dir)
    
    # 性能对比总结
    print("\n" + "="*60)
    print("性能对比总结")
    print("="*60)
    print(f"原始工具耗时（无缓存）: {original_time:.2f} 秒")
    print(f"缓存工具第一次耗时（冷启动）: {cached_time_first:.2f} 秒")
    print(f"缓存工具第二次耗时（热启动）: {cached_time_second:.2f} 秒")
    print(f"缓存性能改进: {improvement:.1f}%")
    
    if original_time > 0:
        speedup = original_time / cached_time_second
        print(f"性能加速倍数（与原始工具对比）: {speedup:.1f}x")
    
    print("\n缓存优势:")
    print(f"  ✓ 内存缓存: 快速重复查询")
    print(f"  ✓ 文件缓存: 持久化存储，跨程序运行")
    print(f"  ✓ LRU淘汰: 自动管理缓存大小")
    print(f"  ✓ 过期管理: 自动清理过期数据")
    
    print("="*60)


def cache_stats_demo():
    """缓存统计演示"""
    print("\n" + "="*60)
    print("缓存统计信息演示")
    print("="*60)
    
    test_dir = Path("test_cache_demo")
    
    if not test_dir.exists():
        print("请先运行 performance_comparison() 创建测试文件")
        return
    
    translator = CrossProjectTranslatorWithCache(
        cache_dir=str(test_dir / ".cache"),
        enable_file_cache=True
    )
    
    # 处理映射文件
    translator.process_translation_mapping(
        str(test_dir / "mapping.xlsx"),
        str(test_dir)
    )
    
    # 获取缓存统计
    stats = translator.get_cache_stats()
    
    print("\n缓存管理器统计信息:")
    print(f"  内存缓存大小: {stats['memory']['size']}/{stats['memory']['max_size']}")
    print(f"  总请求数: {stats['memory']['total_requests']}")
    print(f"  缓存命中: {stats['memory']['hit_count']}")
    print(f"  缓存未命中: {stats['memory']['miss_count']}")
    print(f"  命中率: {stats['memory']['hit_rate']}")
    
    if stats['use_file_cache']:
        print(f"  文件缓存条目: {stats['file']['count']}")
    
    print("\n自定义缓存统计:")
    print(f"  缓存命中次数: {stats['custom']['cache_hits']}")
    print(f"  缓存未命中次数: {stats['custom']['cache_misses']}")
    print(f"  缓存命中率: {stats['custom']['hit_rate']}")
    
    # 获取处理报告
    print("\n处理报告:")
    print(translator.get_processing_report())


if __name__ == "__main__":
    import shutil
    
    # 清理之前的测试文件
    if Path("test_cache_demo").exists():
        shutil.rmtree("test_cache_demo")
    
    print("""
╔════════════════════════════════════════════════════════════╗
║         翻译内容缓存机制 - 性能测试演示                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("""
选择测试模式:
1. 性能对比测试（performance_comparison）
2. 缓存统计演示（cache_stats_demo）

使用示例:
  python test_cache_performance.py
    """)
    
    # 运行性能对比测试
    performance_comparison()
    
    # 运行缓存统计演示
    print("\n")
    cache_stats_demo()
    
    print("\n✓ 测试完成！")
    print(f"✓ 测试文件位置: test_cache_demo/")
    print(f"✓ 缓存文件位置: test_cache_demo/.cache/")
