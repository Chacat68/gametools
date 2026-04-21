#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
提供统一的配置文件管理和用户偏好设置
"""

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field, fields
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

LEGACY_VISIBLE_PAGES_TO_TABS = {
    'cross_project': 'cross_project_translator',
    'json_detector': 'json_detector',
    'excel_processor': 'excel_data_processor',
    'field_extractor': 'field_extractor',
    'table_range': 'table_range_translator',
    'batch_modifier': 'batch_modifier',
}


def _get_app_version() -> str:
    """获取应用版本，避免在多个模块中硬编码版本号。"""
    try:
        from version import get_version
        return get_version()
    except Exception:
        return "unknown"


def _filter_section_data(section_cls, section_data: Any) -> Dict[str, Any]:
    """过滤掉配置节中的未知字段，兼容旧版本或扩展字段。"""
    if not isinstance(section_data, dict):
        return {}

    valid_keys = {item.name for item in fields(section_cls)}
    return {key: value for key, value in section_data.items() if key in valid_keys}


def _deep_merge_dict(base: Any, updates: Any) -> Any:
    """递归合并字典，保留未知字段。"""
    if not isinstance(base, dict) or not isinstance(updates, dict):
        return deepcopy(updates)

    merged = deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dict(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


@dataclass
class ScanConfig:
    """扫描配置"""
    recursive: bool = True
    enable_parallel: bool = True
    max_workers: int = 4
    chunk_size: int = 10000
    auto_open_result: bool = False
    
    
@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    max_size: int = 1000
    max_memory_mb: float = 500.0
    default_ttl: Optional[float] = 3600.0  # 1小时
    

@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    use_colors: bool = True
    keep_days: int = 7
    

@dataclass
class UIConfig:
    """界面配置"""
    theme: str = "default"  # default, dark
    window_width: int = 1260
    window_height: int = 820
    window_x: int = -1
    window_y: int = -1
    font_size: int = 10
    auto_save_position: bool = True
    sidebar_collapsed: bool = False
    sidebar_width: int = 240
    last_active_tab: str = "about"
    recent_tasks: list = field(default_factory=list)
    saved_form_state: Dict[str, Any] = field(default_factory=dict)
    recent_paths: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class PathConfig:
    """路径配置"""
    last_scan_dir: str = ""
    last_output_dir: str = ""
    default_output_format: str = "xlsx"  # xlsx, csv, json
    

@dataclass
class DetectionConfig:
    """检测配置"""
    detect_vietnamese: bool = True
    detect_chinese: bool = True
    detect_english: bool = True
    min_confidence: float = 0.8
    

@dataclass
class TabVisibilityConfig:
    """页签可见性配置"""
    cross_project_translator: bool = True  # 跨项目翻译
    json_detector: bool = True  # JSON检测
    excel_data_processor: bool = True  # Excel数据处理
    field_extractor: bool = True  # 字段导出
    table_range_translator: bool = True  # 多语言提取
    batch_modifier: bool = True  # 批量改表
    

@dataclass
class GameToolsConfig:
    """GameTools 主配置"""
    version: str = field(default_factory=_get_app_version)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    scan: ScanConfig = field(default_factory=ScanConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    log: LogConfig = field(default_factory=LogConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    path: PathConfig = field(default_factory=PathConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    tabs: TabVisibilityConfig = field(default_factory=TabVisibilityConfig)


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        if not self._initialized:
            self.config_file = Path(config_file)
            self._raw_config_data: Dict[str, Any] = {}
            self.config = self._load_config()
            self._initialized = True

    def _build_config_from_data(self, data: Dict[str, Any]) -> GameToolsConfig:
        """从原始 JSON 数据构建配置对象，并忽略未知字段。"""
        if not isinstance(data, dict):
            data = {}

        return GameToolsConfig(
            version=data.get('version') or _get_app_version(),
            last_updated=data.get('last_updated') or datetime.now().isoformat(),
            scan=ScanConfig(**_filter_section_data(ScanConfig, data.get('scan', {}))),
            cache=CacheConfig(**_filter_section_data(CacheConfig, data.get('cache', {}))),
            log=LogConfig(**_filter_section_data(LogConfig, data.get('log', {}))),
            ui=UIConfig(**_filter_section_data(UIConfig, data.get('ui', {}))),
            path=PathConfig(**_filter_section_data(PathConfig, data.get('path', {}))),
            detection=DetectionConfig(**_filter_section_data(DetectionConfig, data.get('detection', {}))),
            tabs=TabVisibilityConfig(**_filter_section_data(TabVisibilityConfig, data.get('tabs', {}))),
        )

    def _migrate_config_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """迁移旧版配置结构到当前 schema，同时保留原始未知字段。"""
        migrated = deepcopy(data) if isinstance(data, dict) else {}
        applied_migrations = []

        current_version = _get_app_version()
        if current_version != "unknown" and migrated.get('version') != current_version:
            migrated['version'] = current_version
            applied_migrations.append('version')

        visible_pages = migrated.get('visible_pages')
        current_tabs = _filter_section_data(TabVisibilityConfig, migrated.get('tabs', {}))
        normalized_tabs = asdict(TabVisibilityConfig())
        normalized_tabs.update(current_tabs)

        if isinstance(visible_pages, dict):
            for legacy_key, current_key in LEGACY_VISIBLE_PAGES_TO_TABS.items():
                if current_key not in current_tabs and legacy_key in visible_pages:
                    normalized_tabs[current_key] = bool(visible_pages[legacy_key])
                    applied_migrations.append(f'visible_pages.{legacy_key}->{current_key}')

        migrated['tabs'] = normalized_tabs

        if applied_migrations:
            logger.info("配置迁移已应用: %s", ", ".join(dict.fromkeys(applied_migrations)))

        return migrated

    def _serialize_config(self) -> Dict[str, Any]:
        """序列化配置，同时保留当前 schema 外的原始字段。"""
        known_config = {
            'version': self.config.version,
            'last_updated': self.config.last_updated,
            'scan': asdict(self.config.scan),
            'cache': asdict(self.config.cache),
            'log': asdict(self.config.log),
            'ui': asdict(self.config.ui),
            'path': asdict(self.config.path),
            'detection': asdict(self.config.detection),
            'tabs': asdict(self.config.tabs),
        }
        return _deep_merge_dict(self._raw_config_data, known_config)
    
    def _load_config(self) -> GameToolsConfig:
        """
        加载配置文件
        
        Returns:
            配置对象
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                migrated_data = self._migrate_config_data(data)
                self._raw_config_data = deepcopy(migrated_data)
                config = self._build_config_from_data(migrated_data)
                
                logger.info(f"配置已加载: {self.config_file}")
                return config
                
            except Exception as e:
                logger.warning(f"加载配置失败，使用默认配置: {e}")
                self._raw_config_data = {}
                return GameToolsConfig()
        else:
            logger.info("配置文件不存在，使用默认配置")
            self._raw_config_data = {}
            return GameToolsConfig()
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            # 更新最后修改时间
            self.config.last_updated = datetime.now().isoformat()
            config_dict = self._serialize_config()
            
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            self._raw_config_data = deepcopy(config_dict)
            
            logger.info(f"配置已保存: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号路径）
        
        Args:
            key_path: 配置键路径，如 "scan.recursive"
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if hasattr(value, key):
                    value = getattr(value, key)
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        设置配置值（支持点号路径）
        
        Args:
            key_path: 配置键路径，如 "scan.recursive"
            value: 要设置的值
            
        Returns:
            是否设置成功
        """
        try:
            keys = key_path.split('.')
            obj = self.config
            
            # 导航到倒数第二层
            for key in keys[:-1]:
                if hasattr(obj, key):
                    obj = getattr(obj, key)
                else:
                    return False
            
            # 设置最后一层的值
            if hasattr(obj, keys[-1]):
                setattr(obj, keys[-1], value)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"设置配置失败 {key_path}: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            是否重置成功
        """
        try:
            self.config = GameToolsConfig()
            self._raw_config_data = {}
            self.save_config()
            logger.info("配置已重置为默认值")
            return True
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定路径
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            export_file = Path(export_path)
            config_dict = self._serialize_config()
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已导出到: {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从指定路径导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否导入成功
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                logger.error(f"配置文件不存在: {import_file}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            migrated_data = self._migrate_config_data(data)
            self._raw_config_data = deepcopy(migrated_data)
            self.config = self._build_config_from_data(migrated_data)
            
            # 保存导入的配置
            self.save_config()
            
            logger.info(f"配置已导入: {import_file}")
            return True
            
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要
        
        Returns:
            配置摘要字典
        """
        return {
            'version': self.config.version,
            'last_updated': self.config.last_updated,
            'scan': {
                'parallel_enabled': self.config.scan.enable_parallel,
                'workers': self.config.scan.max_workers,
                'chunk_size': self.config.scan.chunk_size
            },
            'cache': {
                'enabled': self.config.cache.enabled,
                'max_memory': f"{self.config.cache.max_memory_mb}MB"
            },
            'log': {
                'level': self.config.log.level,
                'to_file': self.config.log.log_to_file
            }
        }


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> GameToolsConfig:
    """
    获取配置对象
    
    Returns:
        配置对象
    """
    return config_manager.config


def save_config() -> bool:
    """
    保存配置
    
    Returns:
        是否保存成功
    """
    return config_manager.save_config()


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    获取配置值的便捷函数
    
    Args:
        key_path: 配置键路径
        default: 默认值
        
    Returns:
        配置值
    """
    return config_manager.get(key_path, default)


def set_config_value(key_path: str, value: Any) -> bool:
    """
    设置配置值的便捷函数
    
    Args:
        key_path: 配置键路径
        value: 要设置的值
        
    Returns:
        是否设置成功
    """
    return config_manager.set(key_path, value)
