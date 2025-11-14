#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度管理模块
提供统一的进度跟踪和显示功能
"""

import time
from typing import Optional, Callable
from datetime import datetime, timedelta


class ProgressTracker:
    """进度跟踪器（支持细粒度进度）"""
    
    def __init__(self, total: int, description: str = "处理中", 
                 callback: Optional[Callable] = None, enable_substeps: bool = False):
        """
        初始化进度跟踪器
        
        Args:
            total: 总任务数
            description: 任务描述
            callback: 进度更新回调函数，接收 (current, total, percent, eta, status_msg) 参数
            enable_substeps: 是否启用子步骤跟踪
        """
        self.total = total
        self.current = 0
        self.description = description
        self.callback = callback
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 0.5  # 最小更新间隔（秒）
        self.completed_items = []
        self.failed_items = []
        
        # 细粒度进度支持
        self.enable_substeps = enable_substeps
        self.current_substep = 0
        self.total_substeps = 0
        self.substep_progress = 0.0  # 当前项的子步骤进度 (0.0-1.0)
        
        # 速度统计
        self.processing_speeds = []  # 最近的处理速度记录
        self.max_speed_samples = 10  # 保留最近10个样本
    
    def update(self, increment: int = 1, status_msg: str = ""):
        """
        更新进度
        
        Args:
            increment: 增量（通常为1）
            status_msg: 状态消息
        """
        self.current += increment
        current_time = time.time()
        
        # 更新处理速度
        if increment > 0:
            elapsed = current_time - self.start_time
            if elapsed > 0:
                speed = self.current / elapsed
                self.processing_speeds.append(speed)
                # 只保留最近的样本
                if len(self.processing_speeds) > self.max_speed_samples:
                    self.processing_speeds.pop(0)
        
        # 节流：避免更新过于频繁
        if (current_time - self.last_update_time < self.update_interval and 
            self.current < self.total):
            return
        
        self.last_update_time = current_time
        
        # 计算百分比（考虑子步骤）
        percent = self._calculate_total_progress()
        
        # 估算剩余时间
        eta = self._calculate_eta()
        
        # 调用回调
        if self.callback:
            self.callback(self.current, self.total, percent, eta, status_msg)
    
    def start_substeps(self, total_substeps: int, description: str = ""):
        """
        开始子步骤跟踪
        
        Args:
            total_substeps: 子步骤总数
            description: 子步骤描述
        """
        if self.enable_substeps:
            self.total_substeps = total_substeps
            self.current_substep = 0
            self.substep_progress = 0.0
    
    def update_substep(self, increment: int = 1, status_msg: str = ""):
        """
        更新子步骤进度
        
        Args:
            increment: 子步骤增量
            status_msg: 状态消息
        """
        if self.enable_substeps and self.total_substeps > 0:
            self.current_substep += increment
            self.substep_progress = min(1.0, self.current_substep / self.total_substeps)
            
            # 触发更新
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                self.last_update_time = current_time
                percent = self._calculate_total_progress()
                eta = self._calculate_eta()
                
                if self.callback:
                    self.callback(self.current, self.total, percent, eta, status_msg)
    
    def finish_substeps(self):
        """完成当前项的子步骤"""
        if self.enable_substeps:
            self.substep_progress = 1.0
            self.total_substeps = 0
            self.current_substep = 0
    
    def _calculate_total_progress(self) -> float:
        """
        计算总进度（包含子步骤）
        
        Returns:
            进度百分比 (0-100)
        """
        if self.total == 0:
            return 0.0
        
        # 基础进度
        base_progress = self.current / self.total
        
        # 如果启用子步骤，加上当前项的子步骤进度
        if self.enable_substeps and self.total > 0:
            substep_contribution = self.substep_progress / self.total
            total_progress = base_progress + substep_contribution
        else:
            total_progress = base_progress
        
        return min(100.0, total_progress * 100)
    
    def _calculate_eta(self) -> str:
        """
        计算预计剩余时间（使用平均速度以提高准确性）
        
        Returns:
            格式化的ETA字符串
        """
        if self.current == 0:
            return "计算中..."
        
        # 使用最近的平均速度
        if self.processing_speeds:
            rate = sum(self.processing_speeds) / len(self.processing_speeds)
        else:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0
        
        if rate == 0:
            return "未知"
        
        # 考虑子步骤的剩余量
        if self.enable_substeps and self.total_substeps > 0:
            remaining = self.total - self.current - self.substep_progress
        else:
            remaining = self.total - self.current
        
        if remaining <= 0:
            return "即将完成"
        
        eta_seconds = remaining / rate
        
        # 格式化ETA
        if eta_seconds < 60:
            return f"{int(eta_seconds)}秒"
        elif eta_seconds < 3600:
            return f"{int(eta_seconds / 60)}分钟"
        else:
            hours = int(eta_seconds / 3600)
            minutes = int((eta_seconds % 3600) / 60)
            return f"{hours}小时{minutes}分钟"
    
    def mark_completed(self, item_name: str):
        """标记项目为完成"""
        self.completed_items.append(item_name)
    
    def mark_failed(self, item_name: str, error: str = ""):
        """标记项目为失败"""
        self.failed_items.append({'name': item_name, 'error': error})
    
    def get_summary(self) -> dict:
        """
        获取进度摘要
        
        Returns:
            包含进度统计的字典
        """
        elapsed = time.time() - self.start_time
        
        # 计算平均速度
        avg_speed = sum(self.processing_speeds) / len(self.processing_speeds) if self.processing_speeds else 0
        
        summary = {
            'total': self.total,
            'current': self.current,
            'completed': len(self.completed_items),
            'failed': len(self.failed_items),
            'percent': self._calculate_total_progress(),
            'elapsed_time': self._format_time(elapsed),
            'eta': self._calculate_eta() if self.current < self.total else "已完成",
            'speed': f"{avg_speed:.2f} 项/秒" if avg_speed > 0 else "计算中"
        }
        
        # 如果启用子步骤，添加子步骤信息
        if self.enable_substeps:
            summary['substep_progress'] = f"{self.substep_progress * 100:.1f}%"
            summary['current_substep'] = f"{self.current_substep}/{self.total_substeps}"
        
        return summary
    
    def get_speed(self) -> float:
        """
        获取平均处理速度
        
        Returns:
            处理速度（项/秒）
        """
        if self.processing_speeds:
            return sum(self.processing_speeds) / len(self.processing_speeds)
        
        elapsed = time.time() - self.start_time
        return self.current / elapsed if elapsed > 0 else 0
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            return f"{int(seconds / 60)}分{int(seconds % 60)}秒"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}小时{minutes}分钟"
    
    def is_complete(self) -> bool:
        """检查是否已完成"""
        return self.current >= self.total
    
    def reset(self):
        """重置进度"""
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.completed_items.clear()
        self.failed_items.clear()


class MultiStageProgress:
    """多阶段进度跟踪器"""
    
    def __init__(self, stages: list, callback: Optional[Callable] = None):
        """
        初始化多阶段进度跟踪器
        
        Args:
            stages: 阶段列表，每项为 (name, weight) 元组
            callback: 进度更新回调函数
        """
        self.stages = stages
        self.callback = callback
        self.current_stage_index = 0
        self.stage_progress = {}
        self.total_weight = sum(weight for _, weight in stages)
        
        for stage_name, _ in stages:
            self.stage_progress[stage_name] = 0.0
    
    def update_stage(self, stage_name: str, progress: float):
        """
        更新某个阶段的进度
        
        Args:
            stage_name: 阶段名称
            progress: 进度（0.0-1.0）
        """
        if stage_name in self.stage_progress:
            self.stage_progress[stage_name] = min(1.0, max(0.0, progress))
            self._notify_update()
    
    def complete_stage(self, stage_name: str):
        """标记阶段为完成"""
        self.update_stage(stage_name, 1.0)
        
        # 移动到下一阶段
        for i, (name, _) in enumerate(self.stages):
            if name == stage_name and i < len(self.stages) - 1:
                self.current_stage_index = i + 1
                break
    
    def get_overall_progress(self) -> float:
        """
        获取总体进度
        
        Returns:
            0.0-1.0之间的进度值
        """
        total_progress = 0.0
        
        for stage_name, weight in self.stages:
            stage_prog = self.stage_progress.get(stage_name, 0.0)
            total_progress += stage_prog * weight
        
        return total_progress / self.total_weight if self.total_weight > 0 else 0.0
    
    def _notify_update(self):
        """通知进度更新"""
        if self.callback:
            overall = self.get_overall_progress()
            current_stage = self.stages[self.current_stage_index][0]
            self.callback(overall, current_stage, self.stage_progress)
    
    def get_current_stage(self) -> str:
        """获取当前阶段名称"""
        if self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index][0]
        return "已完成"


class ConsoleProgressBar:
    """控制台进度条"""
    
    def __init__(self, total: int, description: str = "", width: int = 50):
        """
        初始化控制台进度条
        
        Args:
            total: 总任务数
            description: 描述
            width: 进度条宽度（字符数）
        """
        self.tracker = ProgressTracker(total, description, self._print_progress)
        self.width = width
        self.description = description
    
    def _print_progress(self, current: int, total: int, percent: float, 
                       eta: str, status_msg: str):
        """打印进度条"""
        filled = int(self.width * percent / 100)
        bar = '█' * filled + '░' * (self.width - filled)
        
        msg = f"\r{self.description}: |{bar}| {percent:.1f}% ({current}/{total})"
        
        if eta and eta != "已完成":
            msg += f" - 剩余: {eta}"
        
        if status_msg:
            msg += f" - {status_msg}"
        
        print(msg, end='', flush=True)
        
        # 完成时换行
        if current >= total:
            print()
    
    def update(self, increment: int = 1, status_msg: str = ""):
        """更新进度"""
        self.tracker.update(increment, status_msg)
    
    def mark_completed(self, item_name: str):
        """标记项目为完成"""
        self.tracker.mark_completed(item_name)
    
    def mark_failed(self, item_name: str, error: str = ""):
        """标记项目为失败"""
        self.tracker.mark_failed(item_name, error)
    
    def get_summary(self) -> dict:
        """获取进度摘要"""
        return self.tracker.get_summary()


def create_progress_tracker(total: int, description: str = "处理中",
                           use_console: bool = False, 
                           callback: Optional[Callable] = None) -> ProgressTracker:
    """
    创建进度跟踪器的工厂函数
    
    Args:
        total: 总任务数
        description: 任务描述
        use_console: 是否使用控制台进度条
        callback: 自定义回调函数
        
    Returns:
        ProgressTracker 或 ConsoleProgressBar 实例
    """
    if use_console:
        return ConsoleProgressBar(total, description)
    else:
        return ProgressTracker(total, description, callback)
