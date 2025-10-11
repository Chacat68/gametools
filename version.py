#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools 版本信息管理模块
"""

# 版本信息
__version__ = "1.10.0"
__version_info__ = (1, 10, 0)
__build_date__ = "2025-01-11"
__author__ = "gametools开发团队"
__description__ = "游戏工具集 - 集成策划本地化、JSON检测、Excel处理、翻译提取等功能"

# 版本历史
VERSION_HISTORY = {
    "1.10.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具重要修复和优化",
            "修复策划检测规则：正确识别第6行策划标识并跳过提取",
            "优化输出列顺序：C列和E列位置调换，字段名在C列，文本内容在E列",
            "完善策划文件跳过机制：避免提取不需要翻译的策划文件",
            "改进数据组织结构：更合理的列顺序便于查看和使用",
            "增强策划行检测准确性：支持标准游戏策划表格格式",
            "优化文本提取逻辑：从第7行开始提取，跳过策划行",
            "提升工具实用性：更符合实际工作流程的列布局",
            "修复检测算法：确保策划文件被正确识别和跳过"
        ]
    },
    "1.9.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具输出格式进一步完善",
            "新增E列字段名显示：显示原Excel第五行字段名（一般是英文）",
            "完善Excel物理位置格式：B列显示标准Excel单元格引用（如F5）",
            "增强数据追溯能力：可以准确知道文本来源的字段",
            "支持英文字段名映射：id, name, title, description, category, type等",
            "优化输出数据结构：提供更完整的元数据信息",
            "改进字段名获取算法：支持超出范围索引的默认处理",
            "提升数据完整性：A列id、B列位置、C列name、D列doc、E列字段名",
            "增强翻译工作流程：便于后续翻译和数据处理工作"
        ]
    },
    "1.8.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具智能过滤功能重大升级",
            "新增数值内容过滤：跳过纯数字、浮点数、数学表达式",
            "新增数组格式过滤：跳过方括号、花括号、圆括号数组",
            "新增JSON格式过滤：跳过JSON数组和对象格式",
            "新增数值列表过滤：跳过逗号、分号分隔的数值列表",
            "智能识别数据内容，避免提取不需要翻译的数值和数组",
            "提高提取效率，专注真正需要翻译的文本内容",
            "优化文本检测算法，更准确地识别可翻译内容",
            "减少无用内容干扰，提升翻译工作质量"
        ]
    },
    "1.7.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具UI界面重大改进",
            "增强日志窗口显示，包含时间戳和状态图标",
            "实时显示处理的文件名和处理状态",
            "进度条实时更新，显示处理进度百分比",
            "添加状态图标：🚀开始、ℹ️信息、✅成功、❌失败、⏭️跳过",
            "详细的开始信息显示：目录、格式、语言、检测行等",
            "改进的完成和错误信息显示",
            "更直观的用户界面反馈",
            "提升整体用户体验和操作便利性"
        ]
    },
    "1.6.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具输出格式重大改进",
            "跳过纯英文内容的提取，专注中文和越南文",
            "输出文件名移除'_文本提取'后缀，更加简洁",
            "当提取内容为0时不创建新的Excel文件",
            "全新的输出Excel格式：A列=原A列内容，B列=行号，C列后=文本内容",
            "第一行显示原Excel第5行的字段名",
            "B列显示Excel行号引用（如B4、C7）",
            "优化文件处理逻辑，避免创建无用文件",
            "改进日志记录，区分跳过和失败情况",
            "更清晰的进度显示和统计信息"
        ]
    },
    "1.5.0": {
        "date": "2025-01-11",
        "changes": [
            "翻译提取工具重大升级",
            "支持中文、越南文、英文多语言检测",
            "从第7行开始检测文本内容",
            "提取文本时同时提取对应行A列内容",
            "添加策划文件自动检测和跳过功能",
            "增强的进度显示和日志记录",
            "实时显示处理进度百分比和文件名",
            "详细的处理步骤日志输出",
            "GUI界面添加进度条和实时日志显示",
            "优化文本类型识别（中越混合、越英混合等）",
            "输出格式包含行号、列名、A列内容等详细信息"
        ]
    },
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
            "调整主程序窗口大小为1000x800",
            "调整统一界面窗口大小为1200x900",
            "设置合理的最小窗口尺寸",
            "修复底部内容显示不全的问题",
            "优化界面布局和间距"
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
