#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强日志管理模块
提供统一的日志配置和管理
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import os


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器（仅在支持的终端中使用）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m'       # 重置
    }
    
    def __init__(self, fmt: str = None, use_colors: bool = True):
        super().__init__(fmt)
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record):
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LogManager:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.log_dir = Path("logs")
            self.log_file = None
            self.console_handler = None
            self.file_handler = None
            self._initialized = True
    
    def setup_logging(
        self,
        level: int = logging.INFO,
        log_to_file: bool = True,
        log_to_console: bool = True,
        log_dir: Optional[str] = None,
        log_filename: Optional[str] = None,
        use_colors: bool = True,
        format_string: Optional[str] = None
    ):
        """
        设置日志系统
        
        Args:
            level: 日志级别
            log_to_file: 是否记录到文件
            log_to_console: 是否输出到控制台
            log_dir: 日志目录
            log_filename: 日志文件名（不提供则自动生成）
            use_colors: 是否使用彩色输出
            format_string: 自定义格式字符串
        """
        # 设置日志目录
        if log_dir:
            self.log_dir = Path(log_dir)
        
        if log_to_file and not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 清除现有处理器
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(level)
        
        # 默认格式
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 控制台处理器
        if log_to_console:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setLevel(level)
            
            if use_colors:
                console_formatter = ColoredFormatter(format_string, use_colors=True)
            else:
                console_formatter = logging.Formatter(format_string)
            
            self.console_handler.setFormatter(console_formatter)
            root_logger.addHandler(self.console_handler)
        
        # 文件处理器
        if log_to_file:
            if log_filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                log_filename = f"gametools_{timestamp}.log"
            
            self.log_file = self.log_dir / log_filename
            
            self.file_handler = logging.FileHandler(
                self.log_file, 
                mode='a', 
                encoding='utf-8'
            )
            self.file_handler.setLevel(level)
            
            file_formatter = logging.Formatter(format_string)
            self.file_handler.setFormatter(file_formatter)
            root_logger.addHandler(self.file_handler)
            
            logging.info(f"日志文件: {self.log_file}")
    
    def get_log_file_path(self) -> Optional[Path]:
        """获取当前日志文件路径"""
        return self.log_file
    
    def set_level(self, level: int):
        """
        动态设置日志级别
        
        Args:
            level: 新的日志级别
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        if self.console_handler:
            self.console_handler.setLevel(level)
        
        if self.file_handler:
            self.file_handler.setLevel(level)
        
        logging.info(f"日志级别已更新为: {logging.getLevelName(level)}")
    
    def disable_console_logging(self):
        """禁用控制台日志输出"""
        if self.console_handler:
            logging.getLogger().removeHandler(self.console_handler)
            self.console_handler = None
    
    def enable_console_logging(self, level: int = logging.INFO):
        """启用控制台日志输出"""
        if not self.console_handler:
            self.console_handler = logging.StreamHandler(sys.stdout)
            self.console_handler.setLevel(level)
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                use_colors=True
            )
            self.console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(self.console_handler)
    
    def clean_old_logs(self, keep_days: int = 7):
        """
        清理旧日志文件
        
        Args:
            keep_days: 保留最近几天的日志
        """
        if not self.log_dir.exists():
            return
        
        current_time = datetime.now().timestamp()
        days_in_seconds = keep_days * 24 * 60 * 60
        
        deleted_count = 0
        for log_file in self.log_dir.glob("*.log"):
            file_age = current_time - log_file.stat().st_mtime
            if file_age > days_in_seconds:
                try:
                    log_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logging.warning(f"删除旧日志文件失败 {log_file}: {e}")
        
        if deleted_count > 0:
            logging.info(f"已清理 {deleted_count} 个旧日志文件")


# 全局日志管理器实例
log_manager = LogManager()


def setup_logging(**kwargs):
    """
    设置日志系统的便捷函数
    
    Args:
        **kwargs: 传递给 LogManager.setup_logging() 的参数
    """
    log_manager.setup_logging(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 记录器名称（通常使用 __name__）
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


# 自动清理旧日志（在导入时执行一次）
def auto_cleanup_logs():
    """自动清理超过7天的旧日志"""
    try:
        log_manager.clean_old_logs(keep_days=7)
    except Exception:
        pass  # 静默失败，不影响主程序


# 如果日志目录存在，自动清理
if Path("logs").exists():
    auto_cleanup_logs()
