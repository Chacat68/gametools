#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建跨项目翻译对应演示文件
"""

import os
import pandas as pd
from pathlib import Path


def create_demo_files():
    """创建演示文件"""
    demo_dir = "demo_cross_project"
    
    # 创建演示目录
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
    
    # 创建项目文件目录
    project_dir = os.path.join(demo_dir, "project_files")
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    print(f"创建演示文件到目录: {demo_dir}")
    
    # 1. 创建映射文件（包含B列表格名和C列表内位置）
    mapping_data = {
        'A': ['序号', '1', '2', '3', '4', '5'],
        'B': ['表格名', 'items', 'skills', 'items', 'characters', 'items'],
        'C': ['表内位置', 'A1', 'B2', 'C3', 'A1', 'D4'],
        'D': ['说明', '物品名称', '技能描述', '物品价格', '角色名称', '物品类型']
    }
    
    mapping_df = pd.DataFrame(mapping_data)
    mapping_file = os.path.join(demo_dir, "翻译映射表.xlsx")
    mapping_df.to_excel(mapping_file, index=False)
    print(f"创建映射文件: {mapping_file}")
    
    # 2. 创建项目文件 - items.xlsx
    items_data = {
        'A': ['物品名称', '剑', '盾', '药水'],
        'B': ['物品ID', 'sword_001', 'shield_001', 'potion_001'],
        'C': ['物品价格', '100', '80', '50'],
        'D': ['物品类型', '武器', '防具', '消耗品']
    }
    
    items_df = pd.DataFrame(items_data)
    items_file = os.path.join(project_dir, "items.xlsx")
    items_df.to_excel(items_file, index=False)
    print(f"创建项目文件: {items_file}")
    
    # 3. 创建项目文件 - skills.xlsx
    skills_data = {
        'A': ['技能ID', 'skill_001', 'skill_002', 'skill_003'],
        'B': ['技能描述', '火球术', '治疗术', '闪电术'],
        'C': ['技能等级', '1', '2', '3'],
        'D': ['技能类型', '攻击', '治疗', '攻击']
    }
    
    skills_df = pd.DataFrame(skills_data)
    skills_file = os.path.join(project_dir, "skills.xlsx")
    skills_df.to_excel(skills_file, index=False)
    print(f"创建项目文件: {skills_file}")
    
    # 4. 创建项目文件 - characters.xlsx
    characters_data = {
        'A': ['角色名称', '战士', '法师', '牧师'],
        'B': ['角色ID', 'char_001', 'char_002', 'char_003'],
        'C': ['角色等级', '10', '8', '12'],
        'D': ['角色职业', '近战', '远程', '辅助']
    }
    
    characters_df = pd.DataFrame(characters_data)
    characters_file = os.path.join(project_dir, "characters.xlsx")
    characters_df.to_excel(characters_file, index=False)
    print(f"创建项目文件: {characters_file}")
    
    # 5. 创建使用说明文件
    readme_content = """跨项目翻译对应工具演示文件

文件结构:
├── 翻译映射表.xlsx          # 映射文件（包含B列表格名和C列表内位置）
└── project_files/           # 项目文件目录
    ├── items.xlsx          # 物品表
    ├── skills.xlsx         # 技能表
    └── characters.xlsx     # 角色表

使用方法:
1. 打开gametools程序
2. 选择"跨项目翻译对应"页签
3. 映射文件选择: 翻译映射表.xlsx
4. 项目目录选择: project_files/
5. 设置输出文件路径
6. 点击"开始对应"按钮

映射文件说明:
- A列: 序号和说明
- B列: 表格名（对应project_files目录中的文件名）
- C列: 表内位置（Excel单元格引用，如A1, B2等）
- D列: 说明信息

预期结果:
- 第1行: items -> 剑 (A1位置)
- 第2行: skills -> 治疗术 (B2位置)
- 第3行: items -> 50 (C3位置)
- 第4行: characters -> 战士 (A1位置)
- 第5行: items -> 消耗品 (D4位置)

注意事项:
- 表内位置格式: 工作表名!单元格引用 或 直接单元格引用
- 如果没有指定工作表名，将使用第一个工作表
- 支持标准的Excel单元格引用格式（如A1, B2, C3等）
"""
    
    readme_file = os.path.join(demo_dir, "使用说明.txt")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"创建说明文件: {readme_file}")
    
    print("\n演示文件创建完成！")
    print(f"请使用以下路径进行测试:")
    print(f"映射文件: {os.path.abspath(mapping_file)}")
    print(f"项目目录: {os.path.abspath(project_dir)}")


if __name__ == "__main__":
    create_demo_files()
