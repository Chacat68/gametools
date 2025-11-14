#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务控制模块
提供任务暂停、恢复、取消等控制功能
"""

import threading
import time
from typing import Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """任务状态枚举"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 已暂停
    CANCELLED = "cancelled" # 已取消
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败


@dataclass
class TaskStatus:
    """任务状态信息"""
    state: TaskState
    current: int
    total: int
    progress: float
    message: str = ""
    error: Optional[Exception] = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            'state': self.state.value,
            'current': self.current,
            'total': self.total,
            'progress': self.progress,
            'message': self.message,
            'error': str(self.error) if self.error else None
        }


class TaskController:
    """任务控制器"""
    
    def __init__(self):
        """初始化任务控制器"""
        self._state = TaskState.IDLE
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()
        self._pause_event.set()  # 默认不暂停
        self._lock = threading.Lock()
        
        self.current_task = 0
        self.total_tasks = 0
        self.status_message = ""
        self.error = None
    
    @property
    def state(self) -> TaskState:
        """获取当前状态"""
        return self._state
    
    @state.setter
    def state(self, value: TaskState):
        """设置状态"""
        with self._lock:
            old_state = self._state
            self._state = value
            if old_state != value:
                logger.info(f"任务状态: {old_state.value} -> {value.value}")
    
    def start(self, total: int):
        """
        开始任务
        
        Args:
            total: 总任务数
        """
        with self._lock:
            self._state = TaskState.RUNNING
            self.current_task = 0
            self.total_tasks = total
            self.status_message = "任务已启动"
            self.error = None
            self._pause_event.set()
            self._cancel_event.clear()
            logger.info(f"任务启动，共 {total} 个任务")
    
    def pause(self):
        """暂停任务"""
        if self._state == TaskState.RUNNING:
            self._pause_event.clear()
            self.state = TaskState.PAUSED
            self.status_message = "任务已暂停"
            logger.info("任务已暂停")
            return True
        return False
    
    def resume(self):
        """恢复任务"""
        if self._state == TaskState.PAUSED:
            self._pause_event.set()
            self.state = TaskState.RUNNING
            self.status_message = "任务已恢复"
            logger.info("任务已恢复")
            return True
        return False
    
    def cancel(self):
        """取消任务"""
        if self._state in [TaskState.RUNNING, TaskState.PAUSED]:
            self._cancel_event.set()
            self._pause_event.set()  # 确保不会阻塞
            self.state = TaskState.CANCELLED
            self.status_message = "任务已取消"
            logger.info("任务已取消")
            return True
        return False
    
    def complete(self):
        """标记任务完成"""
        with self._lock:
            if self._state == TaskState.RUNNING:
                self.state = TaskState.COMPLETED
                self.status_message = "任务已完成"
                logger.info("任务已完成")
    
    def fail(self, error: Exception):
        """
        标记任务失败
        
        Args:
            error: 错误信息
        """
        with self._lock:
            self.state = TaskState.FAILED
            self.error = error
            self.status_message = f"任务失败: {str(error)}"
            logger.error(f"任务失败: {error}")
    
    def check_point(self, increment: int = 1, message: str = "") -> bool:
        """
        检查点：检查是否应该暂停或取消
        
        Args:
            increment: 进度增量
            message: 状态消息
            
        Returns:
            是否应该继续执行（False表示已取消）
        """
        # 检查取消标志
        if self._cancel_event.is_set():
            return False
        
        # 等待暂停解除
        self._pause_event.wait()
        
        # 再次检查取消标志（可能在暂停期间被取消）
        if self._cancel_event.is_set():
            return False
        
        # 更新进度
        with self._lock:
            self.current_task += increment
            if message:
                self.status_message = message
        
        return True
    
    def get_status(self) -> TaskStatus:
        """
        获取任务状态
        
        Returns:
            任务状态对象
        """
        with self._lock:
            progress = (self.current_task / self.total_tasks * 100) if self.total_tasks > 0 else 0
            return TaskStatus(
                state=self._state,
                current=self.current_task,
                total=self.total_tasks,
                progress=progress,
                message=self.status_message,
                error=self.error
            )
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._state == TaskState.RUNNING
    
    def is_paused(self) -> bool:
        """检查是否已暂停"""
        return self._state == TaskState.PAUSED
    
    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        return self._state == TaskState.CANCELLED
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self._state == TaskState.COMPLETED
    
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self._state == TaskState.FAILED
    
    def can_pause(self) -> bool:
        """检查是否可以暂停"""
        return self._state == TaskState.RUNNING
    
    def can_resume(self) -> bool:
        """检查是否可以恢复"""
        return self._state == TaskState.PAUSED
    
    def can_cancel(self) -> bool:
        """检查是否可以取消"""
        return self._state in [TaskState.RUNNING, TaskState.PAUSED]
    
    def reset(self):
        """重置控制器状态"""
        with self._lock:
            self._state = TaskState.IDLE
            self.current_task = 0
            self.total_tasks = 0
            self.status_message = ""
            self.error = None
            self._pause_event.set()
            self._cancel_event.clear()
            logger.debug("任务控制器已重置")


class ControllableTask:
    """可控制的任务包装器"""
    
    def __init__(self, func: Callable, *args, controller: Optional[TaskController] = None, **kwargs):
        """
        初始化可控制任务
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            controller: 任务控制器
            **kwargs: 函数关键字参数
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.controller = controller or TaskController()
        self.thread = None
        self.result = None
    
    def run(self) -> Any:
        """
        运行任务
        
        Returns:
            任务结果
        """
        try:
            self.controller.start(1)
            self.result = self.func(*self.args, controller=self.controller, **self.kwargs)
            self.controller.complete()
            return self.result
        except Exception as e:
            self.controller.fail(e)
            raise
    
    def run_async(self, callback: Optional[Callable] = None):
        """
        异步运行任务
        
        Args:
            callback: 完成回调函数
        """
        def _run():
            try:
                self.run()
                if callback:
                    callback(self.result, None)
            except Exception as e:
                if callback:
                    callback(None, e)
        
        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()
    
    def pause(self) -> bool:
        """暂停任务"""
        return self.controller.pause()
    
    def resume(self) -> bool:
        """恢复任务"""
        return self.controller.resume()
    
    def cancel(self) -> bool:
        """取消任务"""
        return self.controller.cancel()
    
    def get_status(self) -> TaskStatus:
        """获取任务状态"""
        return self.controller.get_status()
    
    def wait(self, timeout: Optional[float] = None):
        """
        等待任务完成
        
        Args:
            timeout: 超时时间（秒）
        """
        if self.thread:
            self.thread.join(timeout)


def controllable(func: Callable) -> Callable:
    """
    装饰器：将函数转换为可控制的任务
    
    使用示例:
    @controllable
    def process_files(file_list, controller: TaskController):
        controller.start(len(file_list))
        for file in file_list:
            if not controller.check_point():
                break  # 任务被取消
            process_file(file)
    """
    def wrapper(*args, controller: Optional[TaskController] = None, **kwargs):
        if controller is None:
            controller = TaskController()
        return func(*args, controller=controller, **kwargs)
    
    return wrapper


# 使用示例函数
def example_long_task(items: list, controller: TaskController):
    """
    示例：长时间运行的任务
    
    Args:
        items: 要处理的项目列表
        controller: 任务控制器
    """
    controller.start(len(items))
    
    for i, item in enumerate(items):
        # 检查点：检查是否应该暂停或取消
        if not controller.check_point(increment=1, message=f"处理项目 {i+1}/{len(items)}"):
            logger.info("任务被取消")
            return None
        
        # 模拟处理
        time.sleep(0.1)
        process_item(item)
    
    controller.complete()
    return "任务完成"


def process_item(item):
    """处理单个项目（示例）"""
    pass
