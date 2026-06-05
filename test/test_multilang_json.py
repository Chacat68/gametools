#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 BatchExcelModifier 的多语言JSON支持
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.batch_excel_modifier import BatchExcelModifier

def test_get_available_languages():
    """测试获取JSON中的可用语言列表"""
    print("=" * 60)
    print("测试1: 获取多语言JSON中的可用语言")
    print("=" * 60)
    
    modifier = BatchExcelModifier()
    json_path = "test/test_multilang_config.json"
    
    if not os.path.exists(json_path):
        print(f"❌ 测试JSON文件不存在: {json_path}")
        return False
    
    languages = modifier.get_available_languages_from_json(json_path)
    
    if not languages:
        print("❌ 未检测到任何语言")
        return False
    
    print(f"✅ 检测到 {len(languages)} 种语言:")
    for lang in languages:
        print(f"  - {lang['name']} ({lang['code']}) [Key: {lang['key']}]")
    
    # 验证是否包含期望的语言
    expected_codes = {'zh', 'vn', 'th', 'en'}
    actual_codes = {lang['code'] for lang in languages}
    
    if expected_codes == actual_codes:
        print("✅ 语言代码完全匹配")
        return True
    else:
        print(f"❌ 语言代码不匹配")
        print(f"   期望: {expected_codes}")
        print(f"   实际: {actual_codes}")
        return False

def test_load_json_with_target_lang():
    """测试指定目标语言加载JSON"""
    print("\n" + "=" * 60)
    print("测试2: 指定目标语言加载JSON配置")
    print("=" * 60)
    
    modifier = BatchExcelModifier()
    json_path = "test/test_multilang_config.json"
    
    # 测试加载越南语配置
    print("\n--- 测试加载越南语 (vn) ---")
    config_vn = modifier.load_json_config(json_path, target_lang_code='vn')
    
    if not config_vn:
        print("❌ 加载越南语配置失败")
        return False
    
    print(f"✅ 成功加载配置")
    print(f"  - JSON语言: {modifier.json_language}")
    
    # 检查是否加载了正确的字段
    if 'armor.xlsx' in config_vn:
        table_info = config_vn['armor.xlsx']
        fields = table_info.get('fields', [])
        print(f"  - armor.xlsx 字段: {fields}")
        
        # 验证是否是越南语字段
        vn_fields = [f for f in fields if '_vn' in f]
        if vn_fields:
            print(f"✅ 正确加载了越南语字段: {vn_fields}")
        else:
            print(f"❌ 未找到越南语字段")
            return False
    
    # 测试加载泰语配置
    print("\n--- 测试加载泰语 (th) ---")
    config_th = modifier.load_json_config(json_path, target_lang_code='th')
    
    if not config_th:
        print("❌ 加载泰语配置失败")
        return False
    
    print(f"✅ 成功加载配置")
    print(f"  - JSON语言: {modifier.json_language}")
    
    if 'armor.xlsx' in config_th:
        table_info = config_th['armor.xlsx']
        fields = table_info.get('fields', [])
        print(f"  - armor.xlsx 字段: {fields}")
        
        th_fields = [f for f in fields if '_th' in f]
        if th_fields:
            print(f"✅ 正确加载了泰语字段: {th_fields}")
        else:
            print(f"❌ 未找到泰语字段")
            return False
    
    # 测试加载不存在的语言（应回退到 JSON 中第一个可用语言）
    print("\n--- 测试加载不存在的语言 (ja) ---")
    config_ja = modifier.load_json_config(json_path, target_lang_code='ja')
    
    if not config_ja:
        print("❌ 加载失败（应该使用默认语言）")
        return False
    
    print(f"✅ 使用默认语言加载成功")
    print(f"  - JSON语言: {modifier.json_language}")
    
    # 测试加载英语配置
    print("\n--- 测试加载英语 (en) ---")
    config_en = modifier.load_json_config(json_path, target_lang_code='en')
    
    if not config_en:
        print("❌ 加载英语配置失败")
        return False
    
    print(f"✅ 成功加载配置")
    print(f"  - JSON语言: {modifier.json_language}")
    
    if 'armor.xlsx' in config_en:
        table_info = config_en['armor.xlsx']
        fields = table_info.get('fields', [])
        print(f"  - armor.xlsx 字段: {fields}")
        
        en_fields = [f for f in fields if '_en' in f]
        if en_fields:
            print(f"✅ 正确加载了英语字段: {en_fields}")
        else:
            print(f"❌ 未找到英语字段")
            return False
    
    return True

def test_load_json_without_target_lang():
    """测试不指定目标语言加载JSON（使用第一个）"""
    print("\n" + "=" * 60)
    print("测试3: 不指定目标语言（使用第一个）")
    print("=" * 60)
    
    modifier = BatchExcelModifier()
    json_path = "test/test_multilang_config.json"
    
    config = modifier.load_json_config(json_path)
    
    if not config:
        print("❌ 加载配置失败")
        return False
    
    print(f"✅ 成功加载配置")
    print(f"  - JSON语言: {modifier.json_language}")
    
    if 'armor.xlsx' in config:
        table_info = config['armor.xlsx']
        fields = table_info.get('fields', [])
        print(f"  - armor.xlsx 字段: {fields}")
    
    return True

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("BatchExcelModifier 多语言JSON支持测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("获取可用语言列表", test_get_available_languages()))
    results.append(("指定目标语言加载", test_load_json_with_target_lang()))
    results.append(("默认语言加载", test_load_json_without_target_lang()))
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    # 统计
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
