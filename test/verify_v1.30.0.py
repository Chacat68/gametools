#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证 v1.30.0 新功能
"""

import sys
import os

def check_imports():
    """检查核心模块是否正常导入"""
    print("="*60)
    print("检查模块导入...")
    print("="*60)
    
    try:
        from core.table_range_translator import TableRangeTranslator
        print("✓ TableRangeTranslator 导入成功")
        
        # 检查新方法是否存在
        translator = TableRangeTranslator()
        
        if hasattr(translator, 'process_with_json_config_multi_lang'):
            print("✓ process_with_json_config_multi_lang 方法存在")
        else:
            print("✗ process_with_json_config_multi_lang 方法不存在")
            return False
        
        if hasattr(translator, 'generate_translation_master_table_multi_lang'):
            print("✓ generate_translation_master_table_multi_lang 方法存在")
        else:
            print("✗ generate_translation_master_table_multi_lang 方法不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def check_version():
    """检查版本信息"""
    print("\n" + "="*60)
    print("检查版本信息...")
    print("="*60)
    
    try:
        from version import __version__, __build_date__, VERSION_HISTORY
        
        print(f"版本号: {__version__}")
        print(f"构建日期: {__build_date__}")
        
        if __version__ == "1.30.0":
            print("✓ 版本号正确")
        else:
            print(f"✗ 版本号不正确，期望 1.30.0，实际 {__version__}")
            return False
        
        if "1.30.0" in VERSION_HISTORY:
            print("✓ 版本历史已更新")
            changes = VERSION_HISTORY["1.30.0"]["changes"]
            print("\n更新内容:")
            for change in changes:
                print(f"  {change}")
        else:
            print("✗ 版本历史未更新")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

def check_test_files():
    """检查测试文件是否存在"""
    print("\n" + "="*60)
    print("检查测试文件...")
    print("="*60)
    
    test_files = [
        "test_multi_lang_folders.py",
        "test_multi_lang/field_config.json",
        "test_multi_lang/config/物品配置.xlsx",
        "test_multi_lang/config_zh/物品配置.xlsx",
        "test_multi_lang/config_th/物品配置.xlsx"
    ]
    
    all_exist = True
    for file in test_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} 不存在")
            all_exist = False
    
    return all_exist

def check_dist_file():
    """检查打包文件"""
    print("\n" + "="*60)
    print("检查打包文件...")
    print("="*60)
    
    dist_files = [
        "dist/gametools_v1.30.0.exe"
    ]
    
    all_exist = True
    for file in dist_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024 * 1024)
            print(f"✓ {file} ({size:.2f} MB)")
        else:
            print(f"✗ {file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("\n" + "="*60)
    print("GameTools v1.30.0 功能验证")
    print("="*60 + "\n")
    
    results = {
        "模块导入": check_imports(),
        "版本信息": check_version(),
        "测试文件": check_test_files(),
        "打包文件": check_dist_file()
    }
    
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("\n🎉 所有检查通过！v1.30.0 已准备就绪！\n")
        return 0
    else:
        print("\n⚠️ 部分检查失败，请检查上述错误信息。\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
