#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译内容缓存管理模块
用于缓存Excel数据和查询结果，提升性能
"""

import os
import json
import pickle
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from threading import RLock
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta

# 可选依赖：用于估算 DataFrame 内存占用
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None

logger = logging.getLogger(__name__)

# Python 3.7+ 兼容性处理
try:
    from dataclasses import dataclass, asdict
except ImportError:
    # 如果不支持dataclass，使用简单的类替代
    def dataclass(cls):
        return cls
    
    def asdict(obj):
        return obj.__dict__


@dataclass
class CacheEntry:
    """缓存条目数据类"""
    key: str  # 缓存键
    value: Any  # 缓存值
    timestamp: float = field(default_factory=time.time)  # 创建时间
    access_count: int = 0  # 访问次数
    last_accessed: float = field(default_factory=time.time)  # 最后访问时间
    ttl: Optional[float] = None  # 生存时间（秒）
    
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'key': self.key,
            'timestamp': self.timestamp,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'ttl': self.ttl
        }


class MemoryCache:
    """内存缓存管理器 - 使用LRU淘汰策略（支持内存大小限制）"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None, 
                 max_memory_mb: float = 500.0):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
            max_memory_mb: 最大内存使用量（MB），默认500MB
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = RLock()
        self.hit_count = 0  # 命中次数
        self.miss_count = 0  # 未命中次数
        self.eviction_count = 0  # 淘汰次数
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        with self._lock:
            if key not in self.cache:
                self.miss_count += 1
                return None
            
            entry = self.cache[key]
            
            # 检查过期
            if entry.is_expired():
                del self.cache[key]
                self.miss_count += 1
                logger.debug(f"缓存已过期: {key}")
                return None
            
            # 更新访问信息
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.hit_count += 1
            
            logger.debug(f"缓存命中: {key} (访问次数: {entry.access_count})")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        设置缓存值（支持内存大小检查）
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），如果为None则使用默认值
        """
        with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            
            # 计算value的大小
            value_size = self._estimate_size(value)
            
            # 如果新值太大，直接拒绝
            if value_size > self.max_memory_bytes:
                logger.warning(f"缓存值过大，拒绝缓存: {key} ({value_size / 1024 / 1024:.2f}MB)")
                return
            
            # 如果要替换现有key，先减去旧值的大小
            if key in self.cache:
                old_size = self._estimate_size(self.cache[key].value)
                self.current_memory_bytes -= old_size
            
            # 当内存不足或条目数过多时进行淘汰
            while (self.current_memory_bytes + value_size > self.max_memory_bytes or 
                   len(self.cache) >= self.max_size) and key not in self.cache:
                if not self._evict_lru():
                    break  # 无法继续淘汰
            
            entry = CacheEntry(key=key, value=value, ttl=ttl)
            self.cache[key] = entry
            self.current_memory_bytes += value_size
            logger.debug(f"缓存已设置: {key} (大小: {value_size / 1024:.2f}KB)")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        with self._lock:
            if key in self.cache:
                value_size = self._estimate_size(self.cache[key].value)
                del self.cache[key]
                self.current_memory_bytes -= value_size
                logger.debug(f"缓存已删除: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self.cache.clear()
            self.current_memory_bytes = 0
            logger.info("缓存已清空")
    
    def _evict_lru(self) -> bool:
        """
        删除最少使用的缓存条目
        
        Returns:
            是否成功淘汰
        """
        if not self.cache:
            return False
        
        # 使用更智能的评分系统：考虑访问频率、最后访问时间和数据大小
        current_time = time.time()
        
        def calculate_score(key: str) -> float:
            entry = self.cache[key]
            time_factor = current_time - entry.last_accessed  # 时间越久分数越高
            access_factor = 1.0 / (entry.access_count + 1)  # 访问越少分数越高
            # 综合评分（时间因素权重更高）
            return time_factor * 0.7 + access_factor * 0.3
        
        # 找到评分最高（最应该被淘汰）的条目
        lru_key = max(self.cache.keys(), key=calculate_score)
        
        value_size = self._estimate_size(self.cache[lru_key].value)
        del self.cache[lru_key]
        self.current_memory_bytes -= value_size
        self.eviction_count += 1
        
        logger.debug(f"LRU淘汰: {lru_key} (释放: {value_size / 1024:.2f}KB)")
        return True
    
    def _estimate_size(self, obj: Any) -> int:
        """
        估算对象的内存大小
        
        Args:
            obj: 要估算的对象
            
        Returns:
            估算的字节数
        """
        try:
            import sys
            
            # 对于常见类型进行特殊处理
            if isinstance(obj, (str, bytes)):
                return sys.getsizeof(obj)
            elif isinstance(obj, dict):
                return sys.getsizeof(obj) + sum(
                    self._estimate_size(k) + self._estimate_size(v) 
                    for k, v in obj.items()
                )
            elif isinstance(obj, (list, tuple)):
                return sys.getsizeof(obj) + sum(self._estimate_size(item) for item in obj)
            elif pd is not None and isinstance(obj, pd.DataFrame):
                return int(obj.memory_usage(deep=True).sum())
            else:
                return sys.getsizeof(obj)
        except Exception as e:
            logger.warning(f"估算对象大小失败: {e}")
            return 1024  # 默认1KB
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            memory_usage_mb = self.current_memory_bytes / 1024 / 1024
            memory_usage_percent = (self.current_memory_bytes / self.max_memory_bytes * 100) if self.max_memory_bytes > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': f"{hit_rate*100:.1f}%",
                'total_requests': total_requests,
                'eviction_count': self.eviction_count,
                'memory_usage_mb': f"{memory_usage_mb:.2f}MB",
                'max_memory_mb': f"{self.max_memory_bytes / 1024 / 1024:.2f}MB",
                'memory_usage_percent': f"{memory_usage_percent:.1f}%"
            }
    
    def cleanup_expired(self) -> int:
        """清理过期的缓存条目"""
        with self._lock:
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for key in expired_keys:
                value_size = self._estimate_size(self.cache[key].value)
                del self.cache[key]
                self.current_memory_bytes -= value_size
            
            if expired_keys:
                logger.info(f"清理过期缓存: {len(expired_keys)} 个条目")
            
            return len(expired_keys)


class FileCache:
    """文件缓存管理器 - 持久化缓存"""
    
    def __init__(self, cache_dir: str = ".cache", default_ttl: Optional[float] = None):
        """
        初始化文件缓存
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._lock = RLock()
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用SHA-256替代MD5以避免潜在的碰撞问题
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        从文件中获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值或None
        """
        with self._lock:
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                return None
            
            try:
                with open(cache_path, 'rb') as f:
                    entry_data = pickle.load(f)
                
                entry = CacheEntry(**entry_data['entry'])
                
                # 检查过期
                if entry.is_expired():
                    cache_path.unlink()
                    logger.debug(f"文件缓存已过期: {key}")
                    return None
                
                logger.debug(f"文件缓存命中: {key}")
                return entry_data['value']
            
            except Exception as e:
                logger.error(f"读取文件缓存失败 {key}: {e}")
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        设置文件缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            
        Returns:
            是否设置成功
        """
        with self._lock:
            cache_path = self._get_cache_path(key)
            ttl = ttl if ttl is not None else self.default_ttl
            
            try:
                entry = CacheEntry(key=key, value=value, ttl=ttl)
                cache_data = {
                    'entry': asdict(entry),
                    'value': value
                }
                
                with open(cache_path, 'wb') as f:
                    pickle.dump(cache_data, f)
                
                logger.debug(f"文件缓存已设置: {key}")
                return True
            
            except Exception as e:
                logger.error(f"写入文件缓存失败 {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除文件缓存"""
        with self._lock:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    logger.debug(f"文件缓存已删除: {key}")
                    return True
                except Exception as e:
                    logger.error(f"删除文件缓存失败: {e}")
            return False
    
    def clear(self) -> int:
        """清空所有文件缓存"""
        with self._lock:
            count = 0
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                    count += 1
                logger.info(f"文件缓存已清空: {count} 个文件")
            except Exception as e:
                logger.error(f"清空文件缓存失败: {e}")
            
            return count
    
    def cleanup_expired(self) -> int:
        """清理过期的文件缓存"""
        with self._lock:
            count = 0
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            cache_data = pickle.load(f)
                        
                        entry = CacheEntry(**cache_data['entry'])
                        if entry.is_expired():
                            cache_file.unlink()
                            count += 1
                    except Exception as e:
                        logger.warning(f"清理文件缓存失败 {cache_file}: {e}")
                
                if count > 0:
                    logger.info(f"清理过期文件缓存: {count} 个文件")
            
            except Exception as e:
                logger.error(f"清理文件缓存失败: {e}")
            
            return count


class CacheManager:
    """统一的缓存管理器 - 整合内存和文件缓存"""
    
    def __init__(self, memory_size: int = 1000, cache_dir: str = ".cache", 
                 default_ttl: Optional[float] = None, use_file_cache: bool = True):
        """
        初始化缓存管理器
        
        Args:
            memory_size: 内存缓存最大条目数
            cache_dir: 文件缓存目录
            default_ttl: 默认过期时间（秒）
            use_file_cache: 是否启用文件缓存
        """
        self.memory_cache = MemoryCache(max_size=memory_size, default_ttl=default_ttl)
        self.file_cache = FileCache(cache_dir=cache_dir, default_ttl=default_ttl) if use_file_cache else None
        self.use_file_cache = use_file_cache
        self.default_ttl = default_ttl
    
    def get(self, key: str, level: str = 'all') -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            level: 缓存级别 ('memory', 'file', 'all')
            
        Returns:
            缓存值或None
        """
        # 优先从内存缓存获取
        if level in ('memory', 'all'):
            value = self.memory_cache.get(key)
            if value is not None:
                logger.debug(f"从内存缓存获取: {key}")
                return value
        
        # 其次从文件缓存获取
        if level in ('file', 'all') and self.use_file_cache:
            value = self.file_cache.get(key)
            if value is not None:
                # 将文件缓存结果也加入内存缓存
                self.memory_cache.set(key, value, self.default_ttl)
                logger.debug(f"从文件缓存获取: {key}")
                return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, 
            level: str = 'all') -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            level: 缓存级别 ('memory', 'file', 'all')
        """
        if level in ('memory', 'all'):
            self.memory_cache.set(key, value, ttl)
        
        if level in ('file', 'all') and self.use_file_cache:
            self.file_cache.set(key, value, ttl)
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        self.memory_cache.delete(key)
        if self.use_file_cache:
            self.file_cache.delete(key)
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.memory_cache.clear()
        if self.use_file_cache:
            self.file_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            'memory': self.memory_cache.get_stats(),
            'use_file_cache': self.use_file_cache
        }
        
        if self.use_file_cache:
            # 统计文件缓存数量
            try:
                file_count = len(list(self.file_cache.cache_dir.glob("*.cache")))
                stats['file'] = {'count': file_count}
            except Exception as e:
                logger.error(f"获取文件缓存统计信息失败: {e}")
                stats['file'] = {'count': 0}
        
        return stats
    
    def cleanup_expired(self) -> Dict[str, int]:
        """清理过期缓存"""
        stats = {
            'memory_cleaned': self.memory_cache.cleanup_expired()
        }
        
        if self.use_file_cache:
            stats['file_cleaned'] = self.file_cache.cleanup_expired()
        
        return stats


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager(memory_size: int = 1000, cache_dir: str = ".cache",
                     default_ttl: Optional[float] = None,
                     use_file_cache: bool = True) -> CacheManager:
    """获取或创建全局缓存管理器"""
    global _global_cache_manager
    
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager(
            memory_size=memory_size,
            cache_dir=cache_dir,
            default_ttl=default_ttl,
            use_file_cache=use_file_cache
        )
    
    return _global_cache_manager


if __name__ == "__main__":
    # 测试缓存管理器
    cache_mgr = CacheManager(memory_size=100, default_ttl=3600)
    
    # 设置缓存
    cache_mgr.set("user:1", {"name": "Alice", "age": 30})
    cache_mgr.set("user:2", {"name": "Bob", "age": 25})
    
    # 获取缓存
    print("User 1:", cache_mgr.get("user:1"))
    print("User 2:", cache_mgr.get("user:2"))
    
    # 获取统计信息
    print("Cache Stats:", cache_mgr.get_stats())
    
    # 清理过期缓存
    print("Cleanup Stats:", cache_mgr.cleanup_expired())
