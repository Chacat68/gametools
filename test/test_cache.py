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
import pickle
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
        cache_path = file_cache._get_cache_path("test_file_key")
        with open(cache_path, 'rb') as f:
            raw_cache = pickle.load(f)
        assert 'value' not in raw_cache['entry'], "文件缓存元数据不应重复序列化 value"
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

        print("\n[4.1] 测试访问后淘汰顺序更新...")
        hot_cache = MemoryCache(max_size=2, default_ttl=3600)
        hot_cache.set("cold_key", "cold")
        hot_cache.set("hot_key", "hot")
        assert hot_cache.get("cold_key") == "cold", "cold_key 应能被读取"
        hot_cache.set("new_key", "new")
        assert hot_cache.get("cold_key") == "cold", "被访问后的 cold_key 不应被淘汰"
        assert hot_cache.get("hot_key") is None, "未被访问的 hot_key 应优先被淘汰"
        print("    ✅ 访问后淘汰顺序更新正常")
        results['访问后淘汰'] = True

        print("\n[4.2] 测试淘汰堆定期压缩...")
        compact_cache = MemoryCache(max_size=4, default_ttl=3600)
        compact_cache.set("hot_key", "hot_value")
        for _ in range(200):
            assert compact_cache.get("hot_key") == "hot_value", "热点键在压缩过程中应保持可读"
        max_heap_size = max(
            compact_cache._heap_compaction_min_size,
            len(compact_cache.cache) * compact_cache._heap_compaction_ratio,
        )
        assert len(compact_cache._eviction_heap) <= max_heap_size, "淘汰堆应在阈值内完成压缩"
        print("    ✅ 淘汰堆定期压缩正常")
        results['堆压缩'] = True

        print("\n[5] 测试替换现有键时的容量控制...")
        replace_cache = MemoryCache(max_size=3, default_ttl=3600, max_memory_mb=0.00025)
        replace_cache.set("same_key", "a" * 80)
        replace_cache.set("other_key", "b" * 80)
        replace_cache.set("same_key", "c" * 160)

        assert replace_cache.get("same_key") == "c" * 160, "same_key 应该被新值覆盖"
        assert replace_cache.current_memory_bytes <= replace_cache.max_memory_bytes, "替换现有键后缓存内存不应超过上限"
        print(f"    ✅ 替换现有键时容量控制正常")
        results['替换容量控制'] = True

        print("\n[6] 测试缓存条目大小复用...")
        sized_cache = MemoryCache(max_size=10, default_ttl=3600)
        sized_payload = {"rows": ["x" * 32 for _ in range(16)]}
        sized_cache.set("payload", sized_payload)
        entry = sized_cache.cache.get("payload")
        assert entry is not None and entry.size_bytes > 0, "缓存条目应保存估算大小"
        sized_cache.delete("payload")
        assert sized_cache.current_memory_bytes == 0, "删除缓存后内存统计应归零"
        print("    ✅ 缓存条目大小复用正常")
        results['大小复用'] = True
        
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
        print(f"    命中次数: {stats.get('hit_count', 'N/A')}")
        print(f"    未命中: {stats.get('miss_count', 'N/A')}")
        
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
