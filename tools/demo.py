#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本 - 展示工具功能
"""

import os
import pandas as pd
from pathlib import Path


def create_demo_files():
    """创建演示用的表格文件"""
    demo_dir = "demo_tables"
    
    # 创建演示目录
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
    
    print("创建演示文件...")
    
    # 创建包含越南文的文件
    vietnamese_data = {
        'ID': [1, 2, 3, 4],
        'Name': ['Xin chào', 'Tôi là người Việt Nam', 'Cảm ơn bạn', 'Hẹn gặp lại'],
        'Description': ['Lời chào', 'Giới thiệu bản thân', 'Lời cảm ơn', 'Lời tạm biệt']
    }
    df_vn = pd.DataFrame(vietnamese_data)
    df_vn.to_csv(os.path.join(demo_dir, 'vietnamese_items.csv'), index=False, encoding='utf-8')
    print("OK - Created vietnamese_items.csv (contains Vietnamese)")
    
    # 创建不包含越南文的文件
    english_data = {
        'ID': [1, 2, 3, 4],
        'Name': ['Hello', 'I am Vietnamese', 'Thank you', 'See you later'],
        'Description': ['Greeting', 'Self introduction', 'Thanks', 'Goodbye']
    }
    df_en = pd.DataFrame(english_data)
    df_en.to_csv(os.path.join(demo_dir, 'english_items.csv'), index=False, encoding='utf-8')
    print("OK - Created english_items.csv (no Vietnamese)")
    
    # 创建混合内容的文件
    mixed_data = {
        'ID': [1, 2, 3, 4],
        'Name': ['Hello', 'Xin chào', 'Thank you', 'Cảm ơn'],
        'Description': ['Greeting', 'Lời chào', 'Thanks', 'Lời cảm ơn']
    }
    df_mixed = pd.DataFrame(mixed_data)
    df_mixed.to_csv(os.path.join(demo_dir, 'mixed_content.csv'), index=False, encoding='utf-8')
    print("OK - Created mixed_content.csv (mixed content)")
    
    print(f"\nDemo files created in '{demo_dir}' directory")
    print("You can test the tool using:")
    print("1. Run start_gui.bat to launch GUI")
    print("2. Select demo_tables directory for scanning")
    print("3. View the detection results")


def main():
    """主函数"""
    print("=" * 50)
    print("Localization Tool - Demo Script")
    print("=" * 50)
    
    create_demo_files()
    
    print("\n" + "=" * 50)
    print("Demo files created successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
