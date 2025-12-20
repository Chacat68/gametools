# -*- coding: utf-8 -*-
"""
测试 process_batch_modification_by_language 中的Position模式支持
验证翻译提取CSV格式能否正确使用Position定位
"""

import os
import sys
import pandas as pd
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.batch_excel_modifier import BatchExcelModifier

def test_position_mode_by_language():
    """测试基于语言的批量修改中的Position模式"""
    
    print("=" * 60)
    print("测试 process_batch_modification_by_language 的 Position 模式支持")
    print("=" * 60)
    
    test_dir = os.path.join(project_root, 'test', 'temp_position_lang_test')
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # 1. 创建测试Excel文件
        print("\n步骤1: 创建测试Excel文件...")
        excel_path = os.path.join(test_dir, 'test_table.xlsx')
        test_data = {
            'ID': [1, 2, 3],
            'name_vn': ['旧名称1', '旧名称2', '旧名称3'],
            'desc_vn': ['旧描述1', '旧描述2', '旧描述3'],
        }
        df_excel = pd.DataFrame(test_data)
        df_excel.to_excel(excel_path, index=False)
        print(f"✓ 创建测试Excel: {excel_path}")
        print(f"  包含字段: {list(test_data.keys())}")
        
        # 2. 创建翻译提取格式的CSV（带Position列）
        print("\n步骤2: 创建翻译提取格式CSV（带Position列）...")
        csv_path = os.path.join(test_dir, 'translation_mapping.csv')
        csv_data = {
            'Table': ['test_table.xlsx', 'test_table.xlsx', 'test_table.xlsx'],
            'ID': [1, 2, 3],
            'Classification': ['name_vn', 'name_vn', 'desc_vn'],
            'Position': ['B2', 'B3', 'C2'],  # 精确的Excel单元格位置
            'VN': ['新越南名1', '新越南名2', '新越南描述1']  # 越南语翻译
        }
        df_csv = pd.DataFrame(csv_data)
        df_csv.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✓ 创建CSV映射表: {csv_path}")
        print(f"  包含列: {list(csv_data.keys())}")
        print(f"  包含Position列: 是")
        
        # 3. 创建config.json（设置越南语）
        print("\n步骤3: 创建config.json...")
        config_path = os.path.join(test_dir, 'config.json')
        config = {
            'language': 'vn',  # 越南语
            'language_name': '越南语',
            'fields_by_language': {
                'vn': {
                    'test_table': ['name_vn', 'desc_vn']
                }
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✓ 创建配置文件: {config_path}")
        print(f"  语言: {config['language']} ({config['language_name']})")
        
        # 4. 执行批量修改
        print("\n步骤4: 执行批量修改（基于语言）...")
        modifier = BatchExcelModifier(json_config_path=config_path)
        
        # 设置进度回调
        def progress_callback(msg, percent=None):
            if percent is not None:
                print(f"  [{percent:.1f}%] {msg}")
            else:
                print(f"  {msg}")
        
        modifier.set_progress_callback(progress_callback)
        
        stats = modifier.process_batch_modification_by_language(
            mapping_path=csv_path,
            excel_directory=test_dir,
            backup=False
        )
        
        # 5. 验证结果
        print("\n步骤5: 验证修改结果...")
        print("\n统计信息:")
        print(f"  总行数: {stats['total_rows']}")
        print(f"  已处理行数: {stats['processed_rows']}")
        print(f"  修改的文件数: {stats['modified_files']}")
        print(f"  修改的单元格数: {stats['modified_cells']}")
        print(f"  错误数: {stats['errors']}")
        
        # 读取修改后的Excel验证
        df_result = pd.read_excel(excel_path)
        print("\n修改后的数据:")
        print(df_result)
        
        # 验证Position定位是否正确
        print("\n验证Position定位:")
        expected = {
            'B2': '新越南名1',  # name_vn row 2
            'B3': '新越南名2',  # name_vn row 3
            'C2': '新越南描述1'  # desc_vn row 2
        }
        
        success = True
        for pos, expected_value in expected.items():
            col = pos[0]
            row = int(pos[1:]) - 1  # Excel行号转DataFrame索引
            col_idx = ord(col) - ord('A')
            
            actual_value = df_result.iloc[row, col_idx]
            match = actual_value == expected_value
            status = '✓' if match else '✗'
            print(f"  {status} Position {pos}: 期望='{expected_value}', 实际='{actual_value}'")
            
            if not match:
                success = False
        
        # 验证错误日志
        if modifier.error_logs:
            print("\n错误日志:")
            for error in modifier.error_logs[:10]:  # 只显示前10个
                print(f"  ✗ {error}")
        
        # 最终结果
        print("\n" + "=" * 60)
        if success and stats['errors'] == 0:
            print("✓ 测试通过：Position模式在process_batch_modification_by_language中正常工作")
        else:
            print("✗ 测试失败：Position定位不正确或存在错误")
            if not success:
                print("  原因：Position定位结果与期望不符")
            if stats['errors'] > 0:
                print(f"  原因：存在 {stats['errors']} 个错误")
        print("=" * 60)
        
        return success and stats['errors'] == 0
        
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试文件
        print("\n清理测试文件...")
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✓ 已清理测试目录")

if __name__ == '__main__':
    success = test_position_mode_by_language()
    sys.exit(0 if success else 1)
