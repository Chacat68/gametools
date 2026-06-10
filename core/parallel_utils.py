#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行扫描工具。

读取 config.scan 中的 enable_parallel / max_workers，
为目录级 Excel 扫描等 I/O 密集型任务提供统一的 ThreadPool 封装。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Optional, TypeVar

T = TypeVar('T')
R = TypeVar('R')


def resolve_scan_parallel_settings(enable_parallel: Optional[bool] = None,
                                   max_workers: Optional[int] = None) -> tuple:
    """
    解析是否启用并行及 worker 数量。

    Returns:
        (use_parallel, workers)
    """
    from core.config_manager import get_config

    scan = get_config().scan
    if enable_parallel is None:
        enable_parallel = scan.enable_parallel
    if max_workers is None:
        max_workers = scan.max_workers

    workers = max(1, int(max_workers or 1))
    use_parallel = bool(enable_parallel) and workers > 1
    return use_parallel, workers


def map_parallel_items(items: Iterable[T], func: Callable[[T], R], *,
                       enable_parallel: Optional[bool] = None,
                       max_workers: Optional[int] = None,
                       on_complete: Optional[Callable[[int, int, T], None]] = None) -> List[R]:
    """
    对 items 并行或顺序执行 func，保持结果顺序与输入一致。

    Args:
        items: 待处理项
        func: 单项处理函数
        enable_parallel: 覆盖 config.scan.enable_parallel
        max_workers: 覆盖 config.scan.max_workers
        on_complete: 每项完成回调 (completed_count, total_count, item)
    """
    item_list = list(items)
    total = len(item_list)
    if total == 0:
        return []

    use_parallel, workers = resolve_scan_parallel_settings(enable_parallel, max_workers)
    if not use_parallel or total == 1:
        results: List[R] = []
        for index, item in enumerate(item_list, 1):
            results.append(func(item))
            if on_complete:
                on_complete(index, total, item)
        return results

    results: List[Optional[R]] = [None] * total
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_index = {
            executor.submit(func, item): index
            for index, item in enumerate(item_list)
        }
        completed = 0
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            item = item_list[index]
            results[index] = future.result()
            completed += 1
            if on_complete:
                on_complete(completed, total, item)
    return results  # type: ignore[return-value]
