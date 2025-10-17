#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本 - 便捷运行所有测试
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """运行所有测试文件"""
    test_dir = Path(__file__).parent
    test_files = sorted([f for f in test_dir.glob("test_*.py")])
    
    if not test_files:
        print("❌ 未找到任何测试文件")
        return
    
    print("=" * 70)
    print("GameTools 测试套件")
    print("=" * 70)
    print(f"\n📋 找到 {len(test_files)} 个测试文件:\n")
    
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file.name}")
    
    print("\n" + "=" * 70)
    print("开始运行测试...\n")
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        print(f"\n{'='*70}")
        print(f"运行: {test_file.name}")
        print("=" * 70)
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=str(test_dir.parent),
                capture_output=False
            )
            
            if result.returncode == 0:
                print(f"\n✓ {test_file.name} 通过")
                passed += 1
            else:
                print(f"\n✗ {test_file.name} 失败")
                failed += 1
                
        except Exception as e:
            print(f"\n✗ {test_file.name} 执行出错: {e}")
            failed += 1
    
    # 汇总报告
    print(f"\n{'='*70}")
    print("📊 测试汇总报告")
    print("=" * 70)
    print(f"总计: {passed + failed} 个测试")
    print(f"✓ 通过: {passed} 个")
    print(f"✗ 失败: {failed} 个")
    print(f"成功率: {100*passed/(passed+failed) if (passed+failed) > 0 else 0:.1f}%")
    print("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_tests())
