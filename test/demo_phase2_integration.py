#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 优化功能集成示例
演示如何使用配置管理、任务控制、进度跟踪、结果过滤和多格式输出
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config_manager import ConfigManager, GameToolsConfig
from core.task_controller import TaskController, controllable
from core.progress_tracker import ProgressTracker
from core.result_filter import ResultFilter, QuickSearch, FilterOperator
from core.output_formats import ResultExporter, OutputFormat

import tempfile
import time


def demo_config_manager():
    """演示配置管理器功能"""
    print("\n" + "=" * 60)
    print("配置管理器演示")
    print("=" * 60)
    
    # 使用临时配置文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        config_path = f.name
    
    config = ConfigManager(config_path)
    
    # 获取配置值
    print(f"扫描块大小: {config.get('scan.chunk_size')}")
    print(f"启用并行: {config.get('scan.enable_parallel')}")
    print(f"最大工作线程: {config.get('scan.max_workers')}")
    
    # 修改并保存配置
    config.set('scan.chunk_size', 20000)
    config.save_config()
    print(f"修改后扫描块大小: {config.get('scan.chunk_size')}")
    
    # 使用结构化配置
    structured = GameToolsConfig()
    print(f"默认扫描配置: {structured.scan}")


def demo_task_controller():
    """演示任务控制器功能"""
    print("\n" + "=" * 60)
    print("任务控制器演示")
    print("=" * 60)
    
    controller = TaskController()
    
    @controllable
    def simulated_task(controller: TaskController):
        """模拟可控制的任务"""
        for i in range(10):
            if controller.should_stop():
                print(f"任务在第 {i} 步被停止")
                return
            print(f"执行步骤 {i + 1}/10")
            time.sleep(0.1)
    
    # 启动任务
    controller.start(total_tasks=10)
    print(f"任务状态: {controller.status.value}")
    
    # 模拟取消
    controller.cancel()
    print(f"取消后状态: {controller.status.value}")


def demo_progress_tracker():
    """演示进度跟踪器功能"""
    print("\n" + "=" * 60)
    print("进度跟踪器演示")
    print("=" * 60)
    
    tracker = ProgressTracker(
        total=100,
        min_update_interval=0.1,  # 100ms更新间隔
        show_speed=True
    )
    
    def progress_callback(message, percentage):
        """进度回调"""
        print(f"[{percentage:.1f}%] {message}")
    
    tracker.set_callback(progress_callback)
    
    # 模拟处理
    for i in range(100):
        tracker.update(i + 1, f"处理项目 {i + 1}")
        time.sleep(0.02)  # 模拟处理时间
    
    # 获取统计信息
    stats = tracker.get_stats()
    print(f"处理统计: 用时 {stats['elapsed']:.2f}秒, 速度 {stats['speed']:.1f}项/秒")


def demo_result_filter():
    """演示结果过滤器功能"""
    print("\n" + "=" * 60)
    print("结果过滤器演示")
    print("=" * 60)
    
    # 测试数据
    test_data = [
        {"name": "配置表A", "error_count": 5, "status": "需修复"},
        {"name": "配置表B", "error_count": 0, "status": "正常"},
        {"name": "技能表C", "error_count": 12, "status": "需修复"},
        {"name": "道具表D", "error_count": 3, "status": "需修复"},
    ]
    
    # 过滤：错误数 > 3
    result = ResultFilter.filter(test_data, "error_count", FilterOperator.GREATER_THAN, 3)
    print(f"错误数 > 3: {[r['name'] for r in result]}")
    
    # 过滤：状态包含'修复'
    result = ResultFilter.filter(test_data, "status", FilterOperator.CONTAINS, "修复")
    print(f"需要修复: {[r['name'] for r in result]}")
    
    # 快速搜索
    result = QuickSearch.search(test_data, "技能")
    print(f"搜索'技能': {[r['name'] for r in result]}")


def demo_output_formats():
    """演示多格式输出功能"""
    print("\n" + "=" * 60)
    print("多格式输出演示")
    print("=" * 60)
    
    # 测试数据
    test_data = [
        {"表名": "Item", "字段": "name", "中文": "短剑", "越南文": "Kiếm ngắn"},
        {"表名": "Item", "字段": "desc", "中文": "基础武器", "越南文": "Vũ khí cơ bản"},
        {"表名": "Skill", "字段": "name", "中文": "火球术", "越南文": "Quả cầu lửa"},
    ]
    
    # 输出到临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # CSV输出
        csv_path = Path(temp_dir) / "result.csv"
        ResultExporter.export(test_data, str(csv_path), OutputFormat.CSV)
        print(f"已导出CSV: {csv_path}")
        
        # JSON输出
        json_path = Path(temp_dir) / "result.json"
        ResultExporter.export(test_data, str(json_path), OutputFormat.JSON)
        print(f"已导出JSON: {json_path}")
        
        # Excel输出
        excel_path = Path(temp_dir) / "result.xlsx"
        ResultExporter.export(test_data, str(excel_path), OutputFormat.EXCEL)
        print(f"已导出Excel: {excel_path}")


def main():
    """运行所有演示"""
    print("=" * 60)
    print("Phase 2 优化功能集成演示")
    print("=" * 60)
    
    demo_config_manager()
    demo_task_controller()
    demo_progress_tracker()
    demo_result_filter()
    demo_output_formats()
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
