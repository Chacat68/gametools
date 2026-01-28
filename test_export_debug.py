# -*- coding: utf-8 -*-
"""调试测试脚本 - 检测导出问题"""
import sys
import os

# 确保输出编码正确
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.excel_field_extractor import ExcelFieldExtractor

def test_field_export():
    """测试字段导出功能"""
    print("=" * 60)
    print("测试字段导出功能")
    print("=" * 60)
    
    # 检查测试目录
    test_dir = 'test_multi_lang/config_zh'
    output_dir = 'test_output'
    
    if not os.path.exists(test_dir):
        print(f"测试目录不存在: {test_dir}")
        # 列出可用的测试目录
        if os.path.exists('test_multi_lang'):
            print("test_multi_lang 目录下的内容:")
            for item in os.listdir('test_multi_lang'):
                print(f"  - {item}")
        return False
    
    print(f"测试目录: {test_dir}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = ExcelFieldExtractor()
    
    try:
        stats = extractor.process_directory(
            directory_path=test_dir,
            output_folder=output_dir,
            output_format='json',
            recursive=True,
            language='zh',
            write_output=True
        )
        
        print("\n处理结果:")
        print(f"  - 总文件数: {stats.get('total_files', 0)}")
        print(f"  - 总工作表: {stats.get('total_sheets', 0)}")
        print(f"  - 总字段数: {stats.get('total_fields', 0)}")
        print(f"  - 输出文件: {stats.get('output_file', '无')}")
        
        # 检查是否生成了文件
        import glob
        output_files = glob.glob(f'{output_dir}/field_extraction*.json')
        print(f"  - 实际生成文件: {output_files}")
        
        # 检查警告信息
        if extractor.extraction_warnings:
            print(f"\n警告信息 ({len(extractor.extraction_warnings)} 条):")
            for warning in extractor.extraction_warnings[:10]:
                print(f"  {warning}")
            if len(extractor.extraction_warnings) > 10:
                print(f"  ... 还有 {len(extractor.extraction_warnings) - 10} 条警告")
        
        return stats.get('total_files', 0) > 0
        
    except Exception as e:
        print(f"\n处理出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_table_range_translator():
    """测试多语言提取功能"""
    print("\n" + "=" * 60)
    print("测试多语言提取功能")
    print("=" * 60)
    
    from core.table_range_translator import TableRangeTranslator
    
    # 检查测试JSON配置
    json_config = 'test_multi_lang/field_config.json'
    if not os.path.exists(json_config):
        # 尝试查找其他JSON配置
        json_files = []
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.json') and 'field' in f.lower():
                    json_files.append(os.path.join(root, f))
        
        if json_files:
            print(f"未找到 {json_config}, 但找到以下配置文件:")
            for jf in json_files:
                print(f"  - {jf}")
        else:
            print(f"未找到JSON配置文件: {json_config}")
        return False
    
    print(f"JSON配置: {json_config}")
    
    translator = TableRangeTranslator()
    
    # 检查JSON内容
    try:
        import json
        with open(json_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\nJSON结构:")
        for key in config.keys():
            if isinstance(config[key], dict):
                sub_keys = list(config[key].keys())[:5]
                print(f"  - {key}: {sub_keys}...")
            elif isinstance(config[key], list):
                print(f"  - {key}: 列表 ({len(config[key])} 项)")
            else:
                print(f"  - {key}: {type(config[key]).__name__}")
        
        # 检查是否有 text_tables
        has_text_tables = False
        for lang_key in ['ZH', 'VN', 'TH', 'zh', 'vn', 'th']:
            if lang_key in config:
                lang_config = config[lang_key]
                if isinstance(lang_config, dict) and 'text_tables' in lang_config:
                    has_text_tables = True
                    print(f"  - {lang_key}/text_tables: {len(lang_config['text_tables'])} 个表")
        
        if not has_text_tables:
            print("\n警告: JSON中没有找到 text_tables 配置!")
            print("请确保JSON格式为: {'ZH': {'text_tables': [...]}, ...}")
            
    except Exception as e:
        print(f"读取JSON失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("GameTools 导出功能调试测试")
    print("=" * 60)
    
    # 切换到项目目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"工作目录: {os.getcwd()}")
    
    # 运行测试
    result1 = test_field_export()
    result2 = test_table_range_translator()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"字段导出: {'通过' if result1 else '失败'}")
    print(f"多语言提取: {'通过' if result2 else '失败'}")
