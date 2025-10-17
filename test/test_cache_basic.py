#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版缓存性能测试脚本
验证缓存机制的基本功能
"""

import sys
import os
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试基本导入
print("=" * 60)
print("缓存系统功能测试")
print("=" * 60)

try:
    print("\n[1] 测试缓存管理器导入...")
    from core.cache_manager import CacheManager, MemoryCache, FileCache
    print("    ✓ 成功导入缓存管理器")
    
    print("\n[2] 测试内存缓存功能...")
    mem_cache = MemoryCache(max_size=100, default_ttl=3600)
    mem_cache.set("test_key", {"data": "test_value"})
    result = mem_cache.get("test_key")
    assert result == {"data": "test_value"}, "内存缓存数据不匹配"
    print(f"    ✓ 内存缓存正常工作")
    print(f"      数据: {result}")
    
    stats = mem_cache.get_stats()
    print(f"    ✓ 缓存统计: {stats}")
    
    print("\n[3] 测试文件缓存功能...")
    file_cache = FileCache(cache_dir=".test_cache", default_ttl=3600)
    file_cache.set("test_file_key", {"file_data": "test"})
    result = file_cache.get("test_file_key")
    assert result == {"file_data": "test"}, "文件缓存数据不匹配"
    print(f"    ✓ 文件缓存正常工作")
    print(f"      数据: {result}")
    
    # 清理测试文件
    file_cache.clear()
    if Path(".test_cache").exists():
        import shutil
        shutil.rmtree(".test_cache")
    print(f"    ✓ 测试文件已清理")
    
    print("\n[4] 测试统一缓存管理器...")
    mgr = CacheManager(memory_size=100, cache_dir=".test_cache2", default_ttl=3600)
    mgr.set("key1", "value1")
    mgr.set("key2", {"nested": "data"})
    
    assert mgr.get("key1") == "value1"
    assert mgr.get("key2") == {"nested": "data"}
    print(f"    ✓ 统一缓存管理器正常工作")
    
    stats = mgr.get_stats()
    print(f"    ✓ 管理器统计信息:")
    print(f"      - 内存缓存大小: {stats['memory']['size']}")
    print(f"      - 命中率: {stats['memory']['hit_rate']}")
    
    # 清理
    mgr.clear()
    if Path(".test_cache2").exists():
        import shutil
        shutil.rmtree(".test_cache2")
    print(f"    ✓ 测试资源已清理")
    
    print("\n[5] 测试增强版翻译工具导入...")
    from core.cross_project_translator_cached import CrossProjectTranslatorWithCache
    print("    ✓ 成功导入增强版翻译工具")
    
    print("\n[6] 创建翻译工具实例...")
    translator = CrossProjectTranslatorWithCache(
        cache_dir=".test_cache3",
        enable_file_cache=True,
        memory_cache_size=500,
        cache_ttl=3600
    )
    print("    ✓ 翻译工具实例创建成功")
    
    stats = translator.get_cache_stats()
    print(f"    ✓ 翻译工具缓存统计:")
    print(f"      - 内存缓存大小: {stats['memory']['size']}/{stats['memory']['max_size']}")
    print(f"      - 文件缓存启用: {stats['use_file_cache']}")
    
    # 清理
    translator.clear_cache()
    if Path(".test_cache3").exists():
        import shutil
        shutil.rmtree(".test_cache3")
    print(f"    ✓ 测试资源已清理")
    
    print("\n" + "=" * 60)
    print("✓ 所有功能测试通过！缓存系统工作正常")
    print("=" * 60)
    
    print("\n🎯 下一步:")
    print("  1. 使用增强版工具处理实际的翻译映射")
    print("  2. 监控缓存统计和性能提升")
    print("  3. 使用 GUI 进行可视化管理")
    
    print("\n📚 更多信息请查看:")
    print("  - docs/CACHE_SYSTEM_GUIDE.md - 详细使用指南")
    print("  - docs/CACHE_IMPLEMENTATION.md - 实现说明")
    print("  - gui/cross_project_translator_cache_gui.py - GUI 示例")

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
