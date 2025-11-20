#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段过滤功能
验证 name 和 model 等字段是否被正确过滤
"""

from pathlib import Path
from core.excel_field_extractor import ExcelFieldExtractor

def test_field_filter():
    """测试字段过滤功能"""
    print("=" * 60)
    print("测试字段过滤功能")
    print("=" * 60)
    
    # 创建提取器实例
    extractor = ExcelFieldExtractor()
    
    # 显示过滤的字段名列表
    print(f"\n当前过滤的字段名: {extractor.excluded_field_names}")
    
    # 测试目录
    test_dir = Path("test_excel_files")
    
    if not test_dir.exists():
        print(f"\n❌ 测试目录不存在: {test_dir}")
        return
    
    # 扫描目录
    print(f"\n开始扫描目录: {test_dir}")
    print("-" * 60)
    
    results = extractor.scan_directory(test_dir, recursive=True)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("扫描结果:")
    print("=" * 60)
    
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result['excel_file']} - {result['sheet_name']}")
        print(f"    是否包含文本: {result['has_text']}")
        if result['has_text']:
            print(f"    字段数量: {result['field_count']}")
            print(f"    字段列表: {', '.join(result['fields'])}")
            
            # 检查是否成功过滤了 name 和 model
            filtered_fields = [f for f in result['fields'] if f.lower() in ['name', 'model', 'id', 'code', 'type']]
            if filtered_fields:
                print(f"    ⚠️ 警告: 以下字段应该被过滤但未被过滤: {filtered_fields}")
            else:
                print(f"    ✅ 过滤成功: name/model/id/code/type 字段已被过滤")
    
    # 显示错误和警告
    if extractor.error_logs:
        print("\n" + "=" * 60)
        print("错误日志:")
        print("=" * 60)
        for error in extractor.error_logs:
            print(error)
    
    if extractor.extraction_warnings:
        print("\n" + "=" * 60)
        print("警告信息:")
        print("=" * 60)
        for warning in extractor.extraction_warnings[:10]:  # 只显示前10条
            print(warning)
        if len(extractor.extraction_warnings) > 10:
            print(f"\n... 还有 {len(extractor.extraction_warnings) - 10} 条警告")

if __name__ == "__main__":
    test_field_filter()
