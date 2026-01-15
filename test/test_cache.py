#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统测试 - 合并版
包含基本功能测试和性能对比测试

使用方法:
    python test_cache.py [选项]
    
选项:
    --all       运行所有测试
    --basic     运行基本功能测试
    --perf      运行性能对比测试
"""

import sys
import os
import time
import shutil
import argparse
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_basic_cache():
    """测试缓存系统基本功能"""
    print("\n" + "=" * 60)
    print("缓存系统基本功能测试")
    print("=" * 60)
    
    results = {}
    
    try:
        print("\n[1] 测试缓存管理器导入...")
        from core.cache_manager import CacheManager, MemoryCache, FileCache
        print("    ✅ 成功导入缓存管理器")
        results['导入'] = True
        
        print("\n[2] 测试内存缓存功能...")
        mem_cache = MemoryCache(max_size=100, default_ttl=3600)
        mem_cache.set("test_key", {"data": "test_value"})
        result = mem_cache.get("test_key")
        assert result == {"data": "test_value"}, "内存缓存数据不匹配"
        print(f"    ✅ 内存缓存正常工作")
        stats = mem_cache.get_stats()
        print(f"    缓存统计: {stats}")
        results['内存缓存'] = True
        
        print("\n[3] 测试文件缓存功能...")
        cache_dir = Path(".test_cache")
        file_cache = FileCache(cache_dir=str(cache_dir), default_ttl=3600)
        file_cache.set("test_file_key", {"file_data": "test"})
        result = file_cache.get("test_file_key")
        assert result == {"file_data": "test"}, "文件缓存数据不匹配"
        print(f"    ✅ 文件缓存正常工作")
        
        # 清理测试文件
        file_cache.clear()
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        print(f"    ✅ 测试文件已清理")
        results['文件缓存'] = True
        
        print("\n[4] 测试LRU淘汰机制...")
        small_cache = MemoryCache(max_size=3, default_ttl=3600)
        for i in range(5):
            small_cache.set(f"key_{i}", f"value_{i}")
        
        # 前两个应该被淘汰
        assert small_cache.get("key_0") is None, "key_0 应该被淘汰"
        assert small_cache.get("key_1") is None, "key_1 应该被淘汰"
        assert small_cache.get("key_4") == "value_4", "key_4 应该存在"
        print(f"    ✅ LRU淘汰机制正常")
        results['LRU淘汰'] = True
        
    except Exception as e:
        print(f"    ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return all(results.values())


def test_cache_performance():
    """测试缓存性能对比"""
    print("\n" + "=" * 60)
    print("缓存性能对比测试")
    print("=" * 60)
    
    try:
        from core.cache_manager import MemoryCache
        
        cache = MemoryCache(max_size=1000, default_ttl=3600)
        iterations = 1000
        
        # 测试写入性能
        print(f"\n[1] 测试写入性能 ({iterations} 次)...")
        start = time.time()
        for i in range(iterations):
            cache.set(f"key_{i}", {"index": i, "data": "x" * 100})
        write_time = time.time() - start
        write_ops = (iterations / write_time) if write_time > 0 else float('inf')
        print(f"    写入耗时: {write_time:.4f}s ({write_ops:.0f} ops/s)")
        
        # 测试读取性能
        print(f"\n[2] 测试读取性能 ({iterations} 次)...")
        start = time.time()
        hits = 0
        for i in range(iterations):
            if cache.get(f"key_{i}") is not None:
                hits += 1
        read_time = time.time() - start
        read_ops = (iterations / read_time) if read_time > 0 else float('inf')
        print(f"    读取耗时: {read_time:.4f}s ({read_ops:.0f} ops/s)")
        print(f"    命中率: {hits/iterations*100:.1f}%")
        
        # 测试缓存统计
        print("\n[3] 缓存统计...")
        stats = cache.get_stats()
        print(f"    当前条目: {stats.get('size', 'N/A')}")
        print(f"    命中次数: {stats.get('hits', 'N/A')}")
        print(f"    未命中: {stats.get('misses', 'N/A')}")
        
        print("\n✅ 性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='缓存系统测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--basic', action='store_true', help='运行基本功能测试')
    parser.add_argument('--perf', action='store_true', help='运行性能对比测试')
    
    args = parser.parse_args()
    
    if not any([args.all, args.basic, args.perf]):
        args.all = True
    
    print("=" * 60)
    print("缓存系统测试")
    print("=" * 60)
    
    results = {}
    
    if args.all or args.basic:
        results['基本功能'] = test_basic_cache()
    if args.all or args.perf:
        results['性能测试'] = test_cache_performance()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
