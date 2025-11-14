#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化功能测试脚本
测试新增的并行处理、流式读取、缓存优化等功能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vietnamese_excel_processor import VietnameseExcelProcessor
from core.cache_manager import MemoryCache
from core.log_manager import setup_logging, get_logger
from core.progress_tracker import ConsoleProgressBar


def test_parallel_processing():
    """测试并行处理功能"""
    print("\n" + "="*60)
    print("测试1: 并行处理功能")
    print("="*60)
    
    test_dir = project_root / "test" / "test_excel_files"
    
    if not test_dir.exists():
        print(f"❌ 测试目录不存在: {test_dir}")
        return
    
    # 串行处理
    print("\n🔄 串行处理模式...")
    processor_serial = VietnameseExcelProcessor(enable_parallel=False)
    start_time = time.time()
    results_serial = processor_serial.scan_directory(str(test_dir), recursive=True)
    serial_time = time.time() - start_time
    print(f"✅ 串行处理完成: {len(results_serial)} 个结果, 耗时 {serial_time:.2f}秒")
    
    # 并行处理
    print("\n⚡ 并行处理模式...")
    processor_parallel = VietnameseExcelProcessor(enable_parallel=True, max_workers=4)
    start_time = time.time()
    results_parallel = processor_parallel.scan_directory(str(test_dir), recursive=True)
    parallel_time = time.time() - start_time
    print(f"✅ 并行处理完成: {len(results_parallel)} 个结果, 耗时 {parallel_time:.2f}秒")
    
    # 性能提升
    if serial_time > 0:
        speedup = serial_time / parallel_time if parallel_time > 0 else 1.0
        print(f"\n📊 性能提升: {speedup:.2f}x")


def test_cache_optimization():
    """测试缓存优化功能"""
    print("\n" + "="*60)
    print("测试2: 缓存优化功能")
    print("="*60)
    
    # 创建缓存实例
    cache = MemoryCache(max_size=100, max_memory_mb=50.0)
    
    print("\n📝 添加缓存数据...")
    
    # 添加一些测试数据
    for i in range(50):
        cache.set(f"key_{i}", f"value_{i}" * 100)  # 创建较大的值
    
    print(f"✅ 已添加 50 个缓存项")
    
    # 获取统计信息
    stats = cache.get_stats()
    print(f"\n📊 缓存统计:")
    print(f"  - 缓存大小: {stats['size']}/{stats['max_size']}")
    print(f"  - 内存使用: {stats['memory_usage_mb']} / {stats['max_memory_mb']}")
    print(f"  - 内存使用率: {stats['memory_usage_percent']}")
    
    # 测试缓存命中
    print("\n🔍 测试缓存命中...")
    for i in range(10):
        value = cache.get(f"key_{i}")
        if value:
            print(f"  ✓ key_{i}: 命中")
    
    # 测试缓存未命中
    print("\n❌ 测试缓存未命中...")
    value = cache.get("nonexistent_key")
    print(f"  查询不存在的键: {'未找到' if value is None else '找到'}")
    
    # 最终统计
    final_stats = cache.get_stats()
    print(f"\n📈 最终统计:")
    print(f"  - 命中次数: {final_stats['hit_count']}")
    print(f"  - 未命中次数: {final_stats['miss_count']}")
    print(f"  - 命中率: {final_stats['hit_rate']}")
    print(f"  - 淘汰次数: {final_stats['eviction_count']}")


def test_progress_tracking():
    """测试进度跟踪功能"""
    print("\n" + "="*60)
    print("测试3: 进度跟踪功能")
    print("="*60)
    
    total_tasks = 50
    progress = ConsoleProgressBar(total_tasks, "处理任务", width=40)
    
    print("\n⏳ 模拟任务处理...")
    
    for i in range(total_tasks):
        # 模拟任务处理
        time.sleep(0.05)
        
        if i % 10 == 0:
            progress.update(1, f"处理项目 {i+1}")
        else:
            progress.update(1)
    
    # 显示摘要
    summary = progress.get_summary()
    print(f"\n✅ 任务完成!")
    print(f"📊 摘要:")
    print(f"  - 总任务数: {summary['total']}")
    print(f"  - 已完成: {summary['completed']}")
    print(f"  - 失败: {summary['failed']}")
    print(f"  - 耗时: {summary['elapsed_time']}")


def test_error_handling():
    """测试错误处理功能"""
    print("\n" + "="*60)
    print("测试4: 错误处理功能")
    print("="*60)
    
    from core.error_handler import (
        validate_file_path, validate_directory, 
        FileProcessingError, DirectoryError
    )
    
    # 测试文件验证
    print("\n📁 测试文件验证...")
    
    # 测试不存在的文件
    try:
        validate_file_path("nonexistent_file.xlsx")
        print("  ❌ 应该抛出异常")
    except FileProcessingError as e:
        print(f"  ✅ 正确捕获文件错误")
        print(f"     {e}")
    
    # 测试目录验证
    print("\n📂 测试目录验证...")
    
    # 测试不存在的目录
    try:
        validate_directory("nonexistent_directory", must_exist=True)
        print("  ❌ 应该抛出异常")
    except DirectoryError as e:
        print(f"  ✅ 正确捕获目录错误")
        print(f"     {e}")
    
    # 测试创建目录
    try:
        test_dir = project_root / "temp_test_dir"
        validate_directory(str(test_dir), must_exist=False, create_if_missing=True)
        print(f"  ✅ 成功创建测试目录")
        
        # 清理
        if test_dir.exists():
            test_dir.rmdir()
            print(f"  🧹 已清理测试目录")
    except Exception as e:
        print(f"  ❌ 目录创建失败: {e}")


def test_logging():
    """测试日志系统"""
    print("\n" + "="*60)
    print("测试5: 日志系统")
    print("="*60)
    
    # 设置日志
    setup_logging(
        level=10,  # DEBUG
        log_to_file=True,
        log_to_console=True,
        log_dir="logs",
        use_colors=True
    )
    
    logger = get_logger(__name__)
    
    print("\n📝 测试各级别日志...")
    logger.debug("这是调试信息")
    logger.info("这是信息日志")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    print("✅ 日志测试完成（请检查 logs 目录）")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 GameTools 优化功能测试")
    print("="*60)
    
    try:
        # 运行各项测试
        test_logging()
        test_error_handling()
        test_cache_optimization()
        test_progress_tracking()
        test_parallel_processing()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
