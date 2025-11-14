#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
提供统一的配置文件管理和用户偏好设置
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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
    window_width: int = 1200
    window_height: int = 900
    font_size: int = 10
    auto_save_position: bool = True
    

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
class GameToolsConfig:
    """GameTools 主配置"""
    version: str = "1.23.0"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    scan: ScanConfig = field(default_factory=ScanConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    log: LogConfig = field(default_factory=LogConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    path: PathConfig = field(default_factory=PathConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
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
            self.config = self._load_config()
            self._initialized = True
    
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
                
                # 重建配置对象
                config = GameToolsConfig(
                    version=data.get('version', '1.23.0'),
                    last_updated=data.get('last_updated', datetime.now().isoformat()),
                    scan=ScanConfig(**data.get('scan', {})),
                    cache=CacheConfig(**data.get('cache', {})),
                    log=LogConfig(**data.get('log', {})),
                    ui=UIConfig(**data.get('ui', {})),
                    path=PathConfig(**data.get('path', {})),
                    detection=DetectionConfig(**data.get('detection', {}))
                )
                
                logger.info(f"配置已加载: {self.config_file}")
                return config
                
            except Exception as e:
                logger.warning(f"加载配置失败，使用默认配置: {e}")
                return GameToolsConfig()
        else:
            logger.info("配置文件不存在，使用默认配置")
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
            
            # 转换为字典
            config_dict = {
                'version': self.config.version,
                'last_updated': self.config.last_updated,
                'scan': asdict(self.config.scan),
                'cache': asdict(self.config.cache),
                'log': asdict(self.config.log),
                'ui': asdict(self.config.ui),
                'path': asdict(self.config.path),
                'detection': asdict(self.config.detection)
            }
            
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
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
            
            config_dict = {
                'version': self.config.version,
                'last_updated': self.config.last_updated,
                'scan': asdict(self.config.scan),
                'cache': asdict(self.config.cache),
                'log': asdict(self.config.log),
                'ui': asdict(self.config.ui),
                'path': asdict(self.config.path),
                'detection': asdict(self.config.detection)
            }
            
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
            
            # 重建配置对象
            self.config = GameToolsConfig(
                version=data.get('version', '1.23.0'),
                last_updated=data.get('last_updated', datetime.now().isoformat()),
                scan=ScanConfig(**data.get('scan', {})),
                cache=CacheConfig(**data.get('cache', {})),
                log=LogConfig(**data.get('log', {})),
                ui=UIConfig(**data.get('ui', {})),
                path=PathConfig(**data.get('path', {})),
                detection=DetectionConfig(**data.get('detection', {}))
            )
            
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
