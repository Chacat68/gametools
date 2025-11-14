#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果过滤和搜索模块
提供强大的结果过滤、搜索和排序功能
"""

import re
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FilterOperator(Enum):
    """过滤操作符"""
    EQUALS = "equals"              # 等于
    NOT_EQUALS = "not_equals"      # 不等于
    CONTAINS = "contains"          # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    STARTS_WITH = "starts_with"    # 开头是
    ENDS_WITH = "ends_with"        # 结尾是
    GREATER_THAN = "greater_than"  # 大于
    LESS_THAN = "less_than"        # 小于
    IN_LIST = "in_list"            # 在列表中
    REGEX = "regex"                # 正则匹配


class SortOrder(Enum):
    """排序顺序"""
    ASC = "asc"    # 升序
    DESC = "desc"  # 降序


@dataclass
class FilterRule:
    """过滤规则"""
    field: str                          # 字段名
    operator: FilterOperator            # 操作符
    value: Any                          # 比较值
    case_sensitive: bool = False        # 是否区分大小写
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.operator, str):
            self.operator = FilterOperator(self.operator)


@dataclass
class SortRule:
    """排序规则"""
    field: str               # 字段名
    order: SortOrder = SortOrder.ASC  # 排序顺序
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.order, str):
            self.order = SortOrder(self.order)


class ResultFilter:
    """结果过滤器"""
    
    def __init__(self):
        """初始化过滤器"""
        self.filters: List[FilterRule] = []
        self.sort_rules: List[SortRule] = []
    
    def add_filter(self, field: str, operator: FilterOperator, value: Any, 
                   case_sensitive: bool = False) -> 'ResultFilter':
        """
        添加过滤规则（链式调用）
        
        Args:
            field: 字段名
            operator: 操作符
            value: 比较值
            case_sensitive: 是否区分大小写
            
        Returns:
            self，支持链式调用
        """
        self.filters.append(FilterRule(field, operator, value, case_sensitive))
        return self
    
    def add_sort(self, field: str, order: SortOrder = SortOrder.ASC) -> 'ResultFilter':
        """
        添加排序规则（链式调用）
        
        Args:
            field: 字段名
            order: 排序顺序
            
        Returns:
            self，支持链式调用
        """
        self.sort_rules.append(SortRule(field, order))
        return self
    
    def clear_filters(self):
        """清空过滤规则"""
        self.filters.clear()
    
    def clear_sorts(self):
        """清空排序规则"""
        self.sort_rules.clear()
    
    def clear_all(self):
        """清空所有规则"""
        self.clear_filters()
        self.clear_sorts()
    
    def apply(self, data: List[Dict]) -> List[Dict]:
        """
        应用过滤和排序规则
        
        Args:
            data: 要处理的数据列表
            
        Returns:
            过滤和排序后的数据列表
        """
        # 应用过滤
        filtered_data = self._apply_filters(data)
        
        # 应用排序
        sorted_data = self._apply_sorts(filtered_data)
        
        return sorted_data
    
    def _apply_filters(self, data: List[Dict]) -> List[Dict]:
        """
        应用过滤规则
        
        Args:
            data: 数据列表
            
        Returns:
            过滤后的数据列表
        """
        if not self.filters:
            return data
        
        filtered = []
        for item in data:
            if self._match_all_filters(item):
                filtered.append(item)
        
        logger.debug(f"过滤结果: {len(data)} -> {len(filtered)} 项")
        return filtered
    
    def _match_all_filters(self, item: Dict) -> bool:
        """
        检查项目是否匹配所有过滤规则
        
        Args:
            item: 要检查的项目
            
        Returns:
            是否匹配
        """
        for rule in self.filters:
            if not self._match_filter(item, rule):
                return False
        return True
    
    def _match_filter(self, item: Dict, rule: FilterRule) -> bool:
        """
        检查项目是否匹配单个过滤规则
        
        Args:
            item: 要检查的项目
            rule: 过滤规则
            
        Returns:
            是否匹配
        """
        # 获取字段值
        field_value = item.get(rule.field)
        if field_value is None:
            return False
        
        # 字符串处理
        if isinstance(field_value, str):
            if not rule.case_sensitive:
                field_value = field_value.lower()
                if isinstance(rule.value, str):
                    compare_value = rule.value.lower()
                else:
                    compare_value = rule.value
            else:
                compare_value = rule.value
        else:
            compare_value = rule.value
        
        # 应用操作符
        try:
            if rule.operator == FilterOperator.EQUALS:
                return field_value == compare_value
            
            elif rule.operator == FilterOperator.NOT_EQUALS:
                return field_value != compare_value
            
            elif rule.operator == FilterOperator.CONTAINS:
                return compare_value in field_value
            
            elif rule.operator == FilterOperator.NOT_CONTAINS:
                return compare_value not in field_value
            
            elif rule.operator == FilterOperator.STARTS_WITH:
                return field_value.startswith(compare_value)
            
            elif rule.operator == FilterOperator.ENDS_WITH:
                return field_value.endswith(compare_value)
            
            elif rule.operator == FilterOperator.GREATER_THAN:
                return field_value > compare_value
            
            elif rule.operator == FilterOperator.LESS_THAN:
                return field_value < compare_value
            
            elif rule.operator == FilterOperator.IN_LIST:
                return field_value in compare_value
            
            elif rule.operator == FilterOperator.REGEX:
                pattern = re.compile(compare_value, re.IGNORECASE if not rule.case_sensitive else 0)
                return bool(pattern.search(str(field_value)))
            
            else:
                logger.warning(f"未知的过滤操作符: {rule.operator}")
                return True
                
        except Exception as e:
            logger.error(f"过滤规则应用失败: {e}")
            return False
    
    def _apply_sorts(self, data: List[Dict]) -> List[Dict]:
        """
        应用排序规则
        
        Args:
            data: 数据列表
            
        Returns:
            排序后的数据列表
        """
        if not self.sort_rules:
            return data
        
        sorted_data = list(data)
        
        # 按规则顺序依次排序（从最后一个规则开始）
        for rule in reversed(self.sort_rules):
            sorted_data.sort(
                key=lambda x: self._get_sort_key(x, rule.field),
                reverse=(rule.order == SortOrder.DESC)
            )
        
        return sorted_data
    
    def _get_sort_key(self, item: Dict, field: str) -> Any:
        """
        获取排序键值
        
        Args:
            item: 项目
            field: 字段名
            
        Returns:
            排序键值
        """
        value = item.get(field)
        
        # 处理None值
        if value is None:
            return ""
        
        # 字符串转小写以忽略大小写
        if isinstance(value, str):
            return value.lower()
        
        return value


class QuickSearch:
    """快速搜索"""
    
    @staticmethod
    def search(data: List[Dict], query: str, fields: Optional[List[str]] = None,
               case_sensitive: bool = False) -> List[Dict]:
        """
        在指定字段中搜索关键字
        
        Args:
            data: 数据列表
            query: 搜索关键字
            fields: 要搜索的字段列表（None表示搜索所有字段）
            case_sensitive: 是否区分大小写
            
        Returns:
            匹配的项目列表
        """
        if not query:
            return data
        
        search_query = query if case_sensitive else query.lower()
        results = []
        
        for item in data:
            if QuickSearch._item_matches(item, search_query, fields, case_sensitive):
                results.append(item)
        
        logger.debug(f"搜索 '{query}' 找到 {len(results)} 个结果")
        return results
    
    @staticmethod
    def _item_matches(item: Dict, query: str, fields: Optional[List[str]], 
                     case_sensitive: bool) -> bool:
        """
        检查项目是否匹配搜索条件
        
        Args:
            item: 项目
            query: 搜索查询
            fields: 字段列表
            case_sensitive: 是否区分大小写
            
        Returns:
            是否匹配
        """
        # 确定要搜索的字段
        search_fields = fields if fields else item.keys()
        
        for field in search_fields:
            value = item.get(field)
            if value is None:
                continue
            
            # 转换为字符串并搜索
            value_str = str(value)
            if not case_sensitive:
                value_str = value_str.lower()
            
            if query in value_str:
                return True
        
        return False
    
    @staticmethod
    def search_regex(data: List[Dict], pattern: str, fields: Optional[List[str]] = None,
                    flags: int = re.IGNORECASE) -> List[Dict]:
        """
        使用正则表达式搜索
        
        Args:
            data: 数据列表
            pattern: 正则表达式模式
            fields: 要搜索的字段列表
            flags: 正则表达式标志
            
        Returns:
            匹配的项目列表
        """
        try:
            regex = re.compile(pattern, flags)
            results = []
            
            for item in data:
                search_fields = fields if fields else item.keys()
                
                for field in search_fields:
                    value = item.get(field)
                    if value and regex.search(str(value)):
                        results.append(item)
                        break  # 找到一个匹配就加入结果
            
            logger.debug(f"正则搜索 '{pattern}' 找到 {len(results)} 个结果")
            return results
            
        except re.error as e:
            logger.error(f"正则表达式错误: {e}")
            return []


class ResultAnalyzer:
    """结果分析器"""
    
    @staticmethod
    def group_by(data: List[Dict], field: str) -> Dict[Any, List[Dict]]:
        """
        按字段分组
        
        Args:
            data: 数据列表
            field: 分组字段
            
        Returns:
            分组后的字典
        """
        groups = {}
        
        for item in data:
            key = item.get(field, "未分类")
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        return groups
    
    @staticmethod
    def count_by(data: List[Dict], field: str) -> Dict[Any, int]:
        """
        按字段统计数量
        
        Args:
            data: 数据列表
            field: 统计字段
            
        Returns:
            统计结果字典
        """
        counts = {}
        
        for item in data:
            key = item.get(field, "未分类")
            counts[key] = counts.get(key, 0) + 1
        
        return counts
    
    @staticmethod
    def get_unique_values(data: List[Dict], field: str) -> List[Any]:
        """
        获取字段的唯一值列表
        
        Args:
            data: 数据列表
            field: 字段名
            
        Returns:
            唯一值列表
        """
        values = set()
        
        for item in data:
            value = item.get(field)
            if value is not None:
                values.add(value)
        
        return sorted(list(values))
    
    @staticmethod
    def get_statistics(data: List[Dict]) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Args:
            data: 数据列表
            
        Returns:
            统计信息字典
        """
        if not data:
            return {'total': 0}
        
        stats = {
            'total': len(data),
            'fields': list(data[0].keys()) if data else []
        }
        
        # 统计每个字段的信息
        for field in stats['fields']:
            values = [item.get(field) for item in data if item.get(field) is not None]
            
            stats[f'{field}_count'] = len(values)
            stats[f'{field}_unique'] = len(set(values))
            
            # 如果是数字类型，添加统计信息
            if values and isinstance(values[0], (int, float)):
                stats[f'{field}_min'] = min(values)
                stats[f'{field}_max'] = max(values)
                stats[f'{field}_avg'] = sum(values) / len(values)
        
        return stats


# 便捷函数

def quick_filter(data: List[Dict], **conditions) -> List[Dict]:
    """
    快速过滤（便捷函数）
    
    Args:
        data: 数据列表
        **conditions: 字段=值的条件
        
    Returns:
        过滤后的数据
    
    示例:
        results = quick_filter(data, language_type="越南文", row=5)
    """
    filter_obj = ResultFilter()
    
    for field, value in conditions.items():
        filter_obj.add_filter(field, FilterOperator.EQUALS, value)
    
    return filter_obj.apply(data)


def quick_search(data: List[Dict], query: str, *fields) -> List[Dict]:
    """
    快速搜索（便捷函数）
    
    Args:
        data: 数据列表
        query: 搜索关键字
        *fields: 要搜索的字段
        
    Returns:
        搜索结果
    
    示例:
        results = quick_search(data, "test", "content", "sheet_name")
    """
    return QuickSearch.search(data, query, list(fields) if fields else None)
