#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2优化功能集成示例
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
from core.vietnamese_excel_processor import VietnameseExcelProcessor


# ========== 示例1：配置管理 ==========

def demo_config_management():
    """演示配置管理功能"""
    print("=" * 60)
    print("示例1：配置管理")
    print("=" * 60)
    
    # 获取配置管理器（单例）
    config = ConfigManager()
    
    # 读取配置
    print(f"\n当前缓存配置: 启用={config.get('cache.enabled')}, "
          f"最大内存={config.get('cache.max_memory_mb')}MB")
    
    # 修改配置
    config.set('cache.max_memory_mb', 1000)
    config.set('scan.chunk_size', 20000)
    print(f"修改后: 最大内存={config.get('cache.max_memory_mb')}MB, "
          f"分块大小={config.get('scan.chunk_size')}")
    
    # 保存配置
    config.save_config()
    print("配置已保存到文件")
    
    # 导出配置
    export_path = project_root / "config_export.json"
    config.export_config(str(export_path))
    print(f"配置已导出到: {export_path}")


# ========== 示例2：任务控制 ==========

@controllable
def long_running_task(total_items: int, controller: TaskController = None):
    """可控制的长时间任务"""
    import time
    
    for i in range(total_items):
        # 检查是否应该暂停/取消
        if controller:
            controller.check_point()
        
        # 模拟处理
        time.sleep(0.1)
        print(f"处理进度: {i+1}/{total_items}")
        
        # 在中间位置暂停一次演示
        if i == total_items // 2:
            print("\n[自动暂停演示]")
            if controller:
                controller.pause()
                time.sleep(2)  # 暂停2秒
                controller.resume()
                print("[已恢复]\n")
    
    return f"完成处理 {total_items} 个项目"


def demo_task_control():
    """演示任务控制功能"""
    print("\n" + "=" * 60)
    print("示例2：任务控制（暂停/恢复/取消）")
    print("=" * 60)
    
    # 创建任务控制器
    controller = TaskController()
    
    # 启动任务
    print("\n启动任务...")
    task = controller.start(long_running_task, 10)
    
    # 等待任务完成
    result = task.wait()
    print(f"\n任务结果: {result}")
    print(f"最终状态: {controller.get_status()}")


# ========== 示例3：进度跟踪 ==========

def demo_progress_tracking():
    """演示进度跟踪功能"""
    print("\n" + "=" * 60)
    print("示例3：进度跟踪（含子步骤）")
    print("=" * 60)
    
    import time
    
    # 创建进度跟踪器
    tracker = ProgressTracker(total=100, desc="处理文件")
    
    # 启用子步骤
    tracker.enable_substeps(True)
    
    # 模拟主任务进度
    for i in range(10):
        # 主步骤
        tracker.update(i * 10)
        
        # 子步骤
        tracker.start_substeps(5, f"处理文件 {i+1}")
        for j in range(5):
            time.sleep(0.1)
            tracker.update_substep(j + 1, f"子任务 {j+1}")
        
        time.sleep(0.1)
    
    tracker.close()
    print(f"\n任务完成！统计信息: {tracker.get_stats()}")


# ========== 示例4：结果过滤 ==========

def demo_result_filtering():
    """演示结果过滤功能"""
    print("\n" + "=" * 60)
    print("示例4：结果过滤和搜索")
    print("=" * 60)
    
    # 创建示例数据
    sample_data = [
        {'file': 'config1.xlsx', 'sheet': 'Sheet1', 'language': '越南文', 'row': 10},
        {'file': 'config2.xlsx', 'sheet': 'Sheet1', 'language': '中文', 'row': 20},
        {'file': 'data1.xlsx', 'sheet': 'Data', 'language': '越南文', 'row': 5},
        {'file': 'data2.xlsx', 'sheet': 'Data', 'language': '中越混合', 'row': 15},
        {'file': 'test.xlsx', 'sheet': 'Test', 'language': '越南文', 'row': 25},
    ]
    
    # 创建过滤器
    filter_obj = ResultFilter()
    
    # 添加过滤条件：只要越南文
    filter_obj.add_filter('language', FilterOperator.EQUALS, '越南文')
    
    # 应用过滤
    filtered = filter_obj.apply(sample_data)
    print(f"\n过滤后（只要越南文）: {len(filtered)} 条记录")
    for item in filtered:
        print(f"  - {item['file']}, 行 {item['row']}")
    
    # 快速搜索
    print("\n快速搜索 'data' 关键字:")
    search_results = QuickSearch.search(sample_data, 'data', ['file'])
    for item in search_results:
        print(f"  - {item['file']}")


# ========== 示例5：多格式输出 ==========

def demo_output_formats():
    """演示多格式输出功能"""
    print("\n" + "=" * 60)
    print("示例5：多格式输出（Excel、CSV、JSON、HTML、Markdown）")
    print("=" * 60)
    
    # 示例数据
    sample_data = [
        {
            'excel_file': 'test.xlsx',
            'sheet_name': 'Sheet1',
            'row': 5,
            'col': 3,
            'column_name': 'Description',
            'content': 'Xin chào',
            'language_type': '越南文',
            'position': 'C5'
        },
        {
            'excel_file': 'test.xlsx',
            'sheet_name': 'Sheet1',
            'row': 10,
            'col': 3,
            'column_name': 'Description',
            'content': '你好 và Xin chào',
            'language_type': '中越混合',
            'position': 'C10'
        }
    ]
    
    # 创建导出器
    exporter = ResultExporter()
    
    # 输出目录
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    # 元数据
    metadata = {
        'title': '越南文检测结果',
        'scan_time': '2024-01-15 10:30:00',
        'total_files': 1,
        'total_issues': len(sample_data)
    }
    
    # 导出为不同格式
    formats = [
        (OutputFormat.EXCEL, 'result.xlsx'),
        (OutputFormat.CSV, 'result.csv'),
        (OutputFormat.JSON, 'result.json'),
        (OutputFormat.HTML, 'result.html'),
        (OutputFormat.MARKDOWN, 'result.md'),
        (OutputFormat.TEXT, 'result.txt'),
    ]
    
    print("\n导出文件:")
    for format_type, filename in formats:
        output_path = output_dir / filename
        success = exporter.export(
            sample_data, 
            str(output_path), 
            format_type=format_type,
            metadata=metadata,
            title='越南文检测结果'
        )
        if success:
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (失败)")
    
    print(f"\n所有文件已导出到: {output_dir}")


# ========== 示例6：完整工作流 ==========

def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n" + "=" * 60)
    print("示例6：完整工作流（配置→扫描→过滤→导出）")
    print("=" * 60)
    
    # 1. 加载配置
    config = ConfigManager()
    print(f"\n1. 配置加载: 并行={config.get('scan.enable_parallel')}, "
          f"工作进程={config.get('scan.max_workers')}")
    
    # 2. 创建处理器
    processor = VietnameseExcelProcessor(
        max_workers=config.get('scan.max_workers'),
        enable_parallel=config.get('scan.enable_parallel'),
        chunk_size=config.get('scan.chunk_size')
    )
    print(f"2. 处理器创建完成")
    
    # 3. 模拟扫描（这里不实际扫描，使用示例数据）
    print("3. 扫描文件... (使用示例数据)")
    sample_results = [
        {
            'excel_file': 'config.xlsx',
            'sheet_name': 'Config',
            'row': 5,
            'col': 2,
            'column_name': 'Name',
            'content': 'Tên người dùng',
            'language_type': '越南文',
            'position': 'B5'
        },
        {
            'excel_file': 'data.xlsx',
            'sheet_name': 'Data',
            'row': 10,
            'col': 3,
            'column_name': 'Description',
            'content': '说明 và giải thích',
            'language_type': '中越混合',
            'position': 'C10'
        },
        {
            'excel_file': 'items.xlsx',
            'sheet_name': 'Items',
            'row': 15,
            'col': 1,
            'column_name': 'ID',
            'content': 'Item_001',
            'language_type': '其他',
            'position': 'A15'
        }
    ]
    print(f"   扫描完成: 共 {len(sample_results)} 条记录")
    
    # 4. 过滤结果
    print("4. 过滤结果...")
    filter_obj = ResultFilter()
    filter_obj.add_filter('language_type', FilterOperator.CONTAINS, '越南')
    filtered_results = filter_obj.apply(sample_results)
    print(f"   过滤后: {len(filtered_results)} 条越南文相关记录")
    
    # 5. 导出结果
    print("5. 导出结果...")
    output_dir = project_root / "workflow_output"
    output_dir.mkdir(exist_ok=True)
    
    exporter = ResultExporter()
    
    # 导出为Excel和HTML
    excel_path = output_dir / "vietnamese_results.xlsx"
    html_path = output_dir / "vietnamese_results.html"
    
    metadata = {
        'scan_directory': 'test_files/',
        'total_scanned': 3,
        'total_found': len(filtered_results)
    }
    
    exporter.export(filtered_results, str(excel_path), metadata=metadata)
    exporter.export(filtered_results, str(html_path), metadata=metadata, 
                   title='越南文检测报告')
    
    print(f"   ✓ Excel: {excel_path}")
    print(f"   ✓ HTML: {html_path}")
    
    print("\n✓ 工作流程完成！")


# ========== 主函数 ==========

def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Phase 2 优化功能演示")
    print("=" * 60)
    print("\n包含以下模块:")
    print("  1. 配置管理 (config_manager.py)")
    print("  2. 任务控制 (task_controller.py)")
    print("  3. 进度跟踪 (progress_tracker.py)")
    print("  4. 结果过滤 (result_filter.py)")
    print("  5. 输出格式 (output_formats.py)")
    
    try:
        # 运行各个示例
        demo_config_management()
        demo_task_control()
        demo_progress_tracking()
        demo_result_filtering()
        demo_output_formats()
        demo_complete_workflow()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
