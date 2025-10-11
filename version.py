#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools 版本信息管理模块
"""

# 版本信息
__version__ = "1.4.0"
__version_info__ = (1, 4, 0)
__build_date__ = "2024-12-19"
__author__ = "gametools开发团队"
__description__ = "游戏工具集 - 集成策划本地化、JSON检测、Excel处理、翻译提取等功能"

# 版本历史
VERSION_HISTORY = {
    "1.4.0": {
        "date": "2024-12-19",
        "changes": [
            "添加统一的版本号管理系统",
            "优化GUI界面版本显示",
            "更新构建脚本以支持版本号管理",
            "打包后的exe文件名包含版本号",
            "便携版包名称包含版本号",
            "同时生成兼容性版本文件",
            "优化GUI界面大小以显示所有内容",
            "调整主程序窗口大小为1000x750",
            "调整统一界面窗口大小为1200x800",
            "设置合理的最小窗口尺寸"
        ]
    },
    "1.3.0": {
        "date": "2024-10-XX",
        "changes": [
            "Excel数据拆分工具多文件输出功能",
            "翻译提取工具集成"
        ]
    },
    "1.2.0": {
        "date": "2024-10-XX", 
        "changes": [
            "Excel工具自动文件名生成和重复检测功能"
        ]
    },
    "1.1.0": {
        "date": "2024-10-XX",
        "changes": [
            "Excel工具文件夹输出功能"
        ]
    },
    "1.0.0": {
        "date": "2024-10-XX",
        "changes": [
            "初始版本，包含策划本地化工具和JSON格式检测工具"
        ]
    }
}

def get_version():
    """获取当前版本号"""
    return __version__

def get_version_info():
    """获取版本信息元组"""
    return __version_info__

def get_build_date():
    """获取构建日期"""
    return __build_date__

def get_author():
    """获取作者信息"""
    return __author__

def get_description():
    """获取项目描述"""
    return __description__

def get_version_history():
    """获取版本历史"""
    return VERSION_HISTORY

def get_full_version_info():
    """获取完整的版本信息"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build_date": __build_date__,
        "author": __author__,
        "description": __description__,
        "history": VERSION_HISTORY
    }

def format_version_string():
    """格式化版本字符串"""
    return f"v{__version__} | 构建日期: {__build_date__}"

def get_latest_changes():
    """获取最新版本的更新内容"""
    latest_version = max(VERSION_HISTORY.keys(), key=lambda x: VERSION_HISTORY[x]["date"])
    return VERSION_HISTORY[latest_version]["changes"]

if __name__ == "__main__":
    # 测试版本信息
    print("=== gametools 版本信息 ===")
    print(f"版本号: {get_version()}")
    print(f"版本信息: {get_version_info()}")
    print(f"构建日期: {get_build_date()}")
    print(f"作者: {get_author()}")
    print(f"描述: {get_description()}")
    print(f"格式化版本: {format_version_string()}")
    print("\n=== 最新更新内容 ===")
    for change in get_latest_changes():
        print(f"- {change}")
