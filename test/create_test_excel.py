#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用的Excel文件
用于测试Excel数据整合工具
"""

import pandas as pd
import os
from pathlib import Path


def create_test_excel():
    """创建测试用的Excel文件"""
    
    # 创建测试数据（模拟您图片中的数据）
    test_data = [
        # act_20206_shilian_0.xlsx 组
        ["act_20206_shilian_0.xlsx", "des", 1080601, "神兵天降", "Thần Binh Thiên Giáng"],
        ["act_20206_shilian_0.xlsx", "des", 1090601, "罗刹试炼", "Thí Luyện La Sát"],
        ["act_20206_shilian_0.xlsx", "des", 1090610, "凌虚试炼", "Thí Luyện Lăng Hư"],
        ["act_20206_shilian_0.xlsx", "des", 1090606, "悟空试炼", "Lệnh Hồ Ngộ Kiếm"],
        ["act_20206_shilian_0.xlsx", "des", 1090604, "神皇试炼", "Thí Luyện Chính Tôn"],
        ["act_20206_shilian_0.xlsx", "des", 1090602, "神将挑战", "Khiêu Chiến Chính Đạo"],
        ["act_20206_shilian_0.xlsx", "des", 1040601, "合纵连横", "Bang Phái Võ Lâm"],
        ["act_20206_shilian_0.xlsx", "des", 2020601, "火神试炼", "Thí Luyện Tuyệt Thế"],
        ["act_20206_shilian_0.xlsx", "des", 1060601, "联军抗魔", "Quần Hiệp Chu Tà"],
        ["act_20206_shilian_0.xlsx", "des", 1090611, "战神试炼", "Thí Luyện Anh Hùng"],
        ["act_20206_shilian_0.xlsx", "des", 2011601, "神将挑战", "Thí Luyện Đạo Tôn"],
        ["act_20206_shilian_0.xlsx", "des", 1090605, "魔尊试炼", "Thí Luyện Tà Đế"],
        ["act_20206_shilian_0.xlsx", "des", 1090603, "魔将试炼", "Thí Luyện Tà Phái"],
        ["act_20206_shilian_0.xlsx", "des", 1090607, "木兰试炼", "Hoàng Dung Đấu Trí"],
        
        # act_23201_rank_flower_list.xlsx 组
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "合服狂欢-花语心愿", "Gộp Server - Hoa Tâm Nguyện"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "登录1次", "Đăng nhập 1 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "赠送好友鲜花1次", "Tặng hoa Hảo Hữu 1 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "赠送好友鲜花5次", "Tặng hoa Hảo Hữu 5 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "赠送好友鲜花10次", "Tặng hoa Hảo Hữu 10 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "幸运夺宝10次", "Đoạt Bảo May Mắn 10 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "幸运夺宝20次", "Đoạt Bảo May Mắn 20 lần"],
        ["act_23201_rank_flower_list.xlsx", "task_name", 5010501, "高级夺宝1次", "Đoạt Bảo Cao Cấp 1 lần"],
    ]
    
    # 创建DataFrame
    columns = ["文件名", "分类", "ID", "中文描述", "越南文描述"]
    df = pd.DataFrame(test_data, columns=columns)
    
    # 创建输出目录
    output_dir = Path("test_data")
    output_dir.mkdir(exist_ok=True)
    
    # 保存Excel文件
    output_file = output_dir / "test_data.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"测试Excel文件已创建: {output_file}")
    print(f"文件包含 {len(df)} 行数据")
    print(f"列名: {list(df.columns)}")
    print(f"第一列唯一值: {df['文件名'].unique()}")
    
    return str(output_file)


if __name__ == "__main__":
    create_test_excel()
