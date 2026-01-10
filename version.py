#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools 版本信息管理模块

注意：v1.30.0 之前的版本历史已归档到 docs/VERSION_HISTORY_ARCHIVE.md
"""

# 版本信息
__version__ = "1.42.0"
__version_info__ = (1, 42, 0)
__build_date__ = "2026-01-07"
__author__ = "gametools开发团队"
__description__ = "游戏工具集 - 集成策划本地化、跨项目翻译对应、JSON检测、Excel处理、Excel分页拆分、翻译提取、表字段导出、多语言翻译提取、批量改表、Excel配置同步、Excel转CSV等功能"

# 版本历史（仅保留最近5个版本，更早版本请查看 docs/VERSION_HISTORY_ARCHIVE.md）
VERSION_HISTORY = {
    "1.42.0": {
        "date": "2026-01-07",
        "changes": [
            "✨ 新增Excel转CSV功能",
            "📄 支持批量转换Excel文件为CSV格式",
            "🔧 支持多种编码格式（UTF-8-sig、UTF-8、GBK、GB2312）",
            "📊 支持多工作表处理和合并",
            "🎯 保持内容完整，支持特殊字符和多行文本",
            "⚡ 支持递归处理子目录"
        ]
    },
    "1.41.1": {
        "date": "2025-12-25",
        "changes": [
            "📦 重新打包：补齐运行时配置文件（config.json / config_export.json）",
            "🔧 构建脚本增强：允许从任意目录执行 build_unified.py"
        ]
    },
    "1.41.0": {
        "date": "2025-12-23",
        "changes": [
            "✨ 新增三维表（多工作表）支持",
            "🔧 批量改表支持按Sheet列定位不同工作表",
            "📊 翻译提取CSV保留Sheet列信息",
            "🎯 字段导出已支持遍历所有工作表",
            "⚡ 数据按(Table, Sheet)分组处理",
            "📝 智能工作表选择，不存在时回退到第一个"
        ]
    },
    "1.40.6": {
        "date": "2025-12-20",
        "changes": [
            "🐛 修复 process_batch_modification_by_language 未使用Position模式的问题",
            "✨ 翻译提取CSV现在会自动检测Position列并使用Position直接定位",
            "🎯 解决'行号超出范围'大量错误问题",
            "📊 处理进度显示定位模式信息[Position模式]"
        ]
    },
    "1.40.5": {
        "date": "2025-12-20",
        "changes": [
            "📝 更新批量改表UI提示文本",
            "💡 添加定位模式说明（界面上显示）",
            "✨ 确认对话框显示定位模式信息",
            "📊 完成对话框显示使用的定位模式",
            "🎨 优化界面布局和提示信息"
        ]
    }
    # 更早的版本历史请查看 docs/VERSION_HISTORY_ARCHIVE.md
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
