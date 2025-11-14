#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2优化功能快速演示
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_config():
    """配置管理演示"""
    print("\n" + "=" * 60)
    print("1. 配置管理演示")
    print("=" * 60)
    
    from core.config_manager import ConfigManager
    
    config = ConfigManager()
    print(f"当前并行处理: {config.get('scan.enable_parallel')}")
    print(f"最大内存限制: {config.get('cache.max_memory_mb')}MB")
    
    config.set('scan.chunk_size', 15000)
    print(f"修改后分块大小: {config.get('scan.chunk_size')}")
    
    config.save_config()
    print("[OK] 配置已保存")


def demo_filter():
    """结果过滤演示"""
    print("\n" + "=" * 60)
    print("2. 结果过滤演示")
    print("=" * 60)
    
    from core.result_filter import ResultFilter, FilterOperator, quick_search
    
    # 示例数据
    data = [
        {'file': 'config.xlsx', 'language': '越南文', 'row': 10},
        {'file': 'data.xlsx', 'language': '中文', 'row': 20},
        {'file': 'test.xlsx', 'language': '越南文', 'row': 5},
    ]
    
    # 过滤越南文
    filter_obj = ResultFilter()
    filter_obj.add_filter('language', FilterOperator.EQUALS, '越南文')
    filtered = filter_obj.apply(data)
    
    print(f"原始记录: {len(data)} 条")
    print(f"过滤后: {len(filtered)} 条越南文记录")
    for item in filtered:
        print(f"  - {item['file']}, 行 {item['row']}")
    
    # 快速搜索
    results = quick_search(data, 'config')
    print(f"\n搜索 'config': 找到 {len(results)} 条")


def demo_export():
    """多格式输出演示"""
    print("\n" + "=" * 60)
    print("3. 多格式输出演示")
    print("=" * 60)
    
    from core.output_formats import ResultExporter, OutputFormat
    
    # 示例数据
    data = [
        {
            'file': 'test.xlsx',
            'sheet': 'Sheet1',
            'row': 5,
            'content': 'Xin chào',
            'language': '越南文'
        }
    ]
    
    exporter = ResultExporter()
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    # 导出为多种格式
    formats = [
        (OutputFormat.EXCEL, 'demo.xlsx'),
        (OutputFormat.CSV, 'demo.csv'),
        (OutputFormat.JSON, 'demo.json'),
        (OutputFormat.HTML, 'demo.html'),
    ]
    
    print("导出格式:")
    for format_type, filename in formats:
        path = output_dir / filename
        success = exporter.export(data, str(path), format_type=format_type)
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {filename}")
    
    print(f"\n输出目录: {output_dir}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Phase 2 优化功能快速演示")
    print("=" * 60)
    print("\n包含功能:")
    print("  1. 配置管理 (ConfigManager)")
    print("  2. 结果过滤 (ResultFilter)")
    print("  3. 多格式输出 (ResultExporter)")
    
    try:
        demo_config()
        demo_filter()
        demo_export()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        print("\n详细文档:")
        print("  - docs/OPTIMIZATION_REPORT_v1.24.0.md")
        print("  - docs/OPTIMIZATION_QUICKSTART.md")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
