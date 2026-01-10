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

# 版本历史（仅保留 v1.30.0 及以上版本，更早版本请查看 docs/VERSION_HISTORY_ARCHIVE.md）
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
    },
    "1.40.4": {
        "date": "2025-12-20",
        "changes": [
            "🔧 删除复杂的ID列匹配逻辑",
            "✨ 行号模式：ID值直接作为Excel行号使用",
            "🎯 两种定位模式：Position直接定位 / 行号直接定位",
            "⚡ 大幅简化代码，提升执行效率",
            "🐛 彻底解决'未找到ID'错误",
            "📝 更新测试和文档说明"
        ]
    },
    "1.40.3": {
        "date": "2025-12-20",
        "changes": [
            "🔧 修复批量改表Position定位错误",
            "✨ 新增Position直接定位模式（无需ID匹配）",
            "🎯 Position列（如B7）直接定位到Excel单元格",
            "🔄 自动检测CSV是否有Position列并切换模式",
            "📝 新增列字母↔列号转换函数",
            "✅ 支持翻译提取CSV精确位置修改",
            "📚 新增POSITION_MODE_FIX.md详细说明文档"
        ]
    },
    "1.40.2": {
        "date": "2025-12-20",
        "changes": [
            "🐛 修复CSV映射表表名提取逻辑错误",
            "✨ CSV文件现从Table列自动提取150个唯一表名",
            "🔧 process_batch_modification_by_language正确遍历CSV表名",
            "🔧 process_batch_modification正确遍历CSV表名",
            "✅ 修复'未找到修改后的文件'问题"
        ]
    },
    "1.40.1": {
        "date": "2025-12-20",
        "changes": [
            "🐛 修复批量改表读取CSV映射表时的Excel格式错误",
            "🔧 process_batch_modification方法完整支持CSV格式",
            "🔧 process_batch_modification_by_language方法完整支持CSV格式",
            "✅ 所有方法均检查文件扩展名并正确处理CSV/Excel",
            "✨ 经过78000+行真实数据验证"
        ]
    },
    "1.40.0": {
        "date": "2025-12-20",
        "changes": [
            "🎉 批量改表支持翻译提取CSV格式（无缝集成）",
            "🔄 自动检测并转换翻译提取格式为批量改表格式",
            "✨ Position列自动提取行号作为ID",
            "📊 支持78000+行大文件快速加载",
            "📚 新增翻译CSV格式支持文档"
        ]
    },
    "1.39.0": {
        "date": "2025-12-15",
        "changes": [
            "✨ 批量改表支持新JSON格式：fields_by_language按语言组织字段",
            "✨ 新增自动匹配模式：根据JSON中的language字段自动匹配映射表语言列和Excel字段",
            "✨ GUI增加自动匹配选项：可选择自动或手动指定目标语言",
            "🔧 改进语言代码映射和识别逻辑"
        ]
    },
    "1.38.0": {
        "date": "2025-12-13",
        "changes": [
            "🔧 统一字段导出和翻译提取的过滤规则",
            "✨ 字段导出使用与翻译提取相同的正则表达式过滤{}、[]、数组、纯数字",
            "🐛 增强对象数组过滤：支持过滤[{22},{333}]等纯数字对象数组"
        ]
    },
    "1.37.0": {
        "date": "2025-12-12",
        "changes": [
            "✨ 字段导出新增多语言分支支持：可选择中文、越南语、泰语目录",
            "📝 JSON输出添加语言标记：包含language字段标识语言信息",
            "🔧 输出文件带语言后缀：如field_extraction_result_zh.json",
            "🎯 新增process_multi_language_directories批量处理方法",
            "🔄 翻译提取输出改为CSV格式：更便于查看和处理"
        ]
    },
    "1.36.0": {
        "date": "2025-12-10",
        "changes": [
            "🆕 批量改表新增语言选择功能",
            "🌍 支持选择目标语言（VN、EN、TH等）只修改对应语言列",
            "✨ 新增xlwings引擎支持：使用Excel原生引擎修改文件，完全保留文件结构",
            "🐛 修复批量改表功能：解决处理Excel文件时可能导致未修改文件数据错误的问题"
        ]
    },
    "1.35.0": {
        "date": "2025-12-06",
        "changes": [
            "🎨 界面全面精简：移除所有页签的标题和描述区域",
            "📐 紧凑布局：缩小窗口尺寸(800x600)，减少内边距",
            "📝 页签名称简化：跨项目翻译→翻译对应，JSON错误检测→JSON检测等",
            "🔧 移除各页签的冗余说明文字，将关键信息集成到LabelFrame标题中"
        ]
    },
    "1.34.0": {
        "date": "2025-12-06",
        "changes": [
            "🎨 界面优化：简化多个页签的界面布局",
            "📋 结果信息统一显示在查看结果弹窗中",
            "🔧 优化跨项目翻译对应、JSON检测、Excel处理、分页拆分、多语言翻译提取等页签"
        ]
    },
    "1.33.0": {
        "date": "2025-12-03",
        "changes": [
            "🆕 新功能：Excel配置同步工具",
            "🔄 将源目录的Excel文件配置同步到多个目标目录的同名文件",
            "📁 支持同时同步到两个目标目录",
            "📝 可选择JSON配置文件作为参考（不做修改）",
            "⚙️ 丰富的同步选项：同步值、公式、样式、列宽",
            "💾 支持同步前自动备份目标文件"
        ]
    },
    "1.32.0": {
        "date": "2025-11-27",
        "changes": [
            "🆕 新功能：批量改表工具",
            "📊 根据映射表批量修改多个Excel文件",
            "🔗 JSON配置自动匹配：根据JSON配置自动确定需要修改的字段",
            "📋 智能过滤：只修改JSON中定义的字段，其他列保持不变",
            "📝 修改报告：生成详细的Excel修改报告",
            "💾 备份支持：可选创建.bak备份文件"
        ]
    },
    "1.31.0": {
        "date": "2025-11-25",
        "changes": [
            "📄 新功能：Excel分页拆分工具",
            "📊 根据第一列文件名将数据拆分到对应分页",
            "🔄 支持从路径中自动提取文件名（去除扩展名）",
            "📋 可选包含汇总工作表，显示分组统计信息",
            "🎨 自动应用格式化样式（表头高亮、列宽自适应）"
        ]
    },
    "1.30.0": {
        "date": "2025-11-20",
        "changes": [
            "🎯 多文件夹支持：多语言翻译提取支持选择多个独立语言目录",
            "📁 智能识别：无后缀=越南文、_zh=中文、_th=泰文",
            "🌐 灵活配置：可选择1-3个语言目录，自动合并提取",
            "📊 统一输出：所有语言内容在一个表格中对比展示",
            "✨ 改进体验：界面更清晰，功能更灵活"
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
