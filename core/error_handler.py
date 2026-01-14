#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理模块
提供自定义异常类和错误处理工具
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)


# ============ 自定义异常类 ============

class GameToolsError(Exception):
    """GameTools基础异常类"""
    def __init__(self, message: str, suggestion: Optional[str] = None, 
                 original_error: Optional[Exception] = None):
        self.message = message
        self.suggestion = suggestion
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self):
        result = self.message
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        if self.original_error:
            result += f"\n原始错误: {str(self.original_error)}"
        return result


class FileProcessingError(GameToolsError):
    """文件处理异常"""
    def __init__(self, file_path: str, message: str, suggestion: Optional[str] = None, 
                 original_error: Optional[Exception] = None):
        self.file_path = file_path
        full_message = f"处理文件 '{file_path}' 时出错: {message}"
        super().__init__(full_message, suggestion, original_error)


class DirectoryError(GameToolsError):
    """目录操作异常"""
    def __init__(self, directory_path: str, message: str, suggestion: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        self.directory_path = directory_path
        full_message = f"目录操作失败 '{directory_path}': {message}"
        super().__init__(full_message, suggestion, original_error)


class ExcelReadError(FileProcessingError):
    """Excel读取异常"""
    def __init__(self, file_path: str, sheet_name: Optional[str] = None, 
                 original_error: Optional[Exception] = None):
        message = f"无法读取Excel文件"
        if sheet_name:
            message += f" (工作表: {sheet_name})"
        
        suggestion = "请检查: 1) 文件是否损坏 2) 文件格式是否正确 3) 文件是否被其他程序占用"
        super().__init__(file_path, message, suggestion, original_error)


class CSVReadError(FileProcessingError):
    """CSV读取异常"""
    def __init__(self, file_path: str, original_error: Optional[Exception] = None):
        message = "无法读取CSV文件"
        suggestion = "请检查: 1) 文件编码 (尝试 UTF-8, GBK, GB2312) 2) 文件格式是否正确"
        super().__init__(file_path, message, suggestion, original_error)


class LanguageDetectionError(GameToolsError):
    """语言检测异常"""
    def __init__(self, text: str, original_error: Optional[Exception] = None):
        message = f"语言检测失败: '{text[:50]}...'"
        suggestion = "文本可能包含特殊字符或格式问题"
        super().__init__(message, suggestion, original_error)


class CacheError(GameToolsError):
    """缓存操作异常"""
    pass


class OutputError(GameToolsError):
    """输出文件异常"""
    def __init__(self, output_path: str, message: str, original_error: Optional[Exception] = None):
        self.output_path = output_path
        full_message = f"输出文件失败 '{output_path}': {message}"
        suggestion = "请检查: 1) 输出路径是否有写入权限 2) 磁盘空间是否充足 3) 文件是否被占用"
        super().__init__(full_message, suggestion, original_error)


# ============ 错误处理装饰器 ============

def handle_errors(default_return: Any = None, log_traceback: bool = True):
    """
    错误处理装饰器
    
    Args:
        default_return: 发生错误时的默认返回值
        log_traceback: 是否记录完整的堆栈跟踪
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except GameToolsError as e:
                logger.error(f"[{func.__name__}] {str(e)}")
                if log_traceback:
                    logger.debug(traceback.format_exc())
                return default_return
            except Exception as e:
                logger.error(f"[{func.__name__}] 未预期的错误: {str(e)}")
                if log_traceback:
                    logger.debug(traceback.format_exc())
                return default_return
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, error_msg: str = "操作失败", **kwargs) -> Any:
    """
    安全执行函数，捕获异常并返回默认值
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        default: 发生错误时的默认返回值
        error_msg: 错误消息前缀
        **kwargs: 函数关键字参数
        
    Returns:
        函数返回值或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_msg}: {str(e)}")
        return default


# ============ 文件操作错误处理 ============

def validate_file_path(file_path: str, must_exist: bool = True, 
                       extensions: Optional[list] = None) -> Path:
    """
    验证文件路径
    
    Args:
        file_path: 文件路径
        must_exist: 文件是否必须存在
        extensions: 允许的文件扩展名列表
        
    Returns:
        Path对象
        
    Raises:
        FileProcessingError: 文件验证失败
    """
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            raise FileProcessingError(
                file_path, 
                "文件不存在",
                suggestion="请检查文件路径是否正确"
            )
        
        if must_exist and not path.is_file():
            raise FileProcessingError(
                file_path,
                "路径不是文件",
                suggestion="请提供有效的文件路径"
            )
        
        if extensions and path.suffix.lower() not in extensions:
            raise FileProcessingError(
                file_path,
                f"不支持的文件格式: {path.suffix}",
                suggestion=f"支持的格式: {', '.join(extensions)}"
            )
        
        return path
        
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(file_path, "文件路径验证失败", original_error=e)


def validate_directory(directory_path: str, must_exist: bool = True, 
                       create_if_missing: bool = False) -> Path:
    """
    验证目录路径
    
    Args:
        directory_path: 目录路径
        must_exist: 目录是否必须存在
        create_if_missing: 如果不存在是否创建
        
    Returns:
        Path对象
        
    Raises:
        DirectoryError: 目录验证失败
    """
    try:
        path = Path(directory_path)
        
        if not path.exists():
            if create_if_missing:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"已创建目录: {directory_path}")
            elif must_exist:
                raise DirectoryError(
                    directory_path,
                    "目录不存在",
                    suggestion="请检查目录路径是否正确"
                )
        
        if path.exists() and not path.is_dir():
            raise DirectoryError(
                directory_path,
                "路径不是目录",
                suggestion="请提供有效的目录路径"
            )
        
        return path
        
    except DirectoryError:
        raise
    except Exception as e:
        raise DirectoryError(directory_path, "目录路径验证失败", original_error=e)


# ============ 用户友好的错误消息 ============

def format_error_message(error: Exception, include_suggestion: bool = True) -> str:
    """
    格式化错误消息为用户友好的格式
    
    Args:
        error: 异常对象
        include_suggestion: 是否包含建议
        
    Returns:
        格式化的错误消息
    """
    if isinstance(error, GameToolsError):
        message = f"❌ {error.message}"
        if include_suggestion and error.suggestion:
            message += f"\n💡 {error.suggestion}"
        return message
    else:
        return f"❌ 发生错误: {str(error)}"


def log_error_with_context(error: Exception, context: dict, logger_instance: logging.Logger = None):
    """
    记录带上下文信息的错误
    
    Args:
        error: 异常对象
        context: 上下文信息字典
        logger_instance: 日志记录器实例
    """
    if logger_instance is None:
        logger_instance = logger
    
    error_msg = format_error_message(error)
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
    
    logger_instance.error(f"{error_msg} [上下文: {context_str}]")
    
    if isinstance(error, GameToolsError) and error.original_error:
        tb_str = traceback.format_exception(type(error.original_error), 
                                            error.original_error, 
                                            error.original_error.__traceback__)
        logger_instance.debug(f"原始异常: {tb_str}")
