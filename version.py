#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools 版本信息管理模块

注意：v1.30.0 之前的版本历史已归档到 docs/VERSION_HISTORY_ARCHIVE.md
"""

# 版本信息
__version__ = "1.46.65"
__version_info__ = (1, 46, 65)
__build_date__ = "2026-06-23"
__author__ = "gametools开发团队"
__description__ = "游戏工具集 - 集成策划本地化、跨项目翻译对应、JSON检测、Excel处理、Excel分页拆分、翻译提取、表字段导出、多语言翻译提取、批量改表、Excel配置同步、Excel转CSV等功能、GUI启动优化"

# 版本历史（仅保留部分近期版本，更早版本请查看 docs/VERSION_HISTORY_ARCHIVE.md）
VERSION_HISTORY = {
    "1.46.55": {
        "date": "2026-04-25",
        "changes": [
            "🔘 统一各功能页主按钮与二级按钮文案，形成一致的交互层级",
            "🧭 将结果、清理、保存、导出等动作统一为同一套命名规则",
            "🎨 继续减少多工具拼接感，强化单一产品的操作语言"
        ]
    },
    "1.46.54": {
        "date": "2026-04-25",
        "changes": [
            "🧩 统一各功能页的区块标题和步骤编号，形成一致的流程语言",
            "📋 为右侧操作区补齐统一标题与说明，减少页面结构割裂感",
            "🎨 继续强化单一工作流工具的页面一致性"
        ]
    },
    "1.46.53": {
        "date": "2026-04-25",
        "changes": [
            "📝 统一各功能页的页头说明文案，收口为同一套产品化句式",
            "🧭 顶栏默认说明改用共享描述表，避免各页说明再次漂移",
            "🎨 继续降低多工具拼接感，强化单一工作流产品的一致性"
        ]
    },
    "1.46.52": {
        "date": "2026-04-25",
        "changes": [
            "🧭 左侧导航改为主要流程、辅助工具、工作台三段式分组",
            "⭐ 工作台入口改为主流程大卡 + 次级工具紧凑卡的层级设计",
            "🎨 统一品牌文案与导航文案，进一步降低后台菜单感"
        ]
    },
    "1.46.51": {
        "date": "2026-04-25",
        "changes": [
            "🎨 收紧工作台首页，去除弱信息和大面积留白",
            "🧭 将首页整合为统一工具入口，集中展示核心任务",
            "📌 顶栏压缩为紧凑结构，保留最近一次与工具状态摘要"
        ]
    },
    "1.46.50": {
        "date": "2026-04-25",
        "changes": [
            "📦 重新打包当前修复后的发布版本",
            "🧪 保留打包后 GUI 冒烟校验与验证脚本修复",
            "🔧 同步构建签名与版本元数据一致性调整"
        ]
    },
    "1.46.49": {
        "date": "2026-04-25",
        "changes": [
            "🛠️ 修复 PyInstaller 对 NumPy 2.x 的打包兼容问题",
            "📦 保留 libscipy_openblas 依赖，修复打包后 pandas/numpy 启动失败",
            "✅ 新增打包后 GUI 冒烟校验脚本 verify_proc.ps1"
        ]
    },
    "1.46.31": {
        "date": "2026-01-28",
        "changes": [
            "✨ 现代化GUI批量改表页面增加刷新语言列表功能",
            "🔄 支持从映射表自动读取可用语言列",
            "🎯 语言选择变化时自动更新目标语言显示"
        ]
    },
    "1.46.29": {
        "date": "2026-01-28",
        "changes": [
            "✨ 现代化GUI字段导出页面支持多语言目录配置",
            "📁 支持中文、越南语、泰语三个语言目录分别配置",
            "✅ 语言目录可独立勾选启用/禁用",
            "📤 JSON格式输出支持合并多语言结果（带语言标记）"
        ]
    },
    "1.46.25": {
        "date": "2026-01-28",
        "changes": [
            "✨ 字段提取功能新增边界检测规则",
            "🛑 任意单元格等于行边界关键字时自动停止扫描（默认 over，常量 ROW_BOUNDARY_KEYWORD）",
            "📊 与翻译提取功能保持一致的边界检测机制"
        ]
    },
    "1.46.24": {
        "date": "2026-01-28",
        "changes": [
            "✨ 翻译提取功能新增边界检测规则",
            "🛑 任意单元格等于行边界关键字时自动停止该表导出（默认 over，常量 ROW_BOUNDARY_KEYWORD）",
            "📊 后续行的文本不再被提取，支持策划表格数据边界标记"
        ]
    },
    "1.46.0": {
        "date": "2026-01-13",
        "changes": [
            "📦 版本更新重新打包",
            "✅ 所有功能正常运行验证"
        ]
    },
    "1.45.0": {
        "date": "2026-01-13",
        "changes": [
            "✨ 现代化UI设为默认启动界面",
            "📄 新增5个功能页面：Sheet分割、配置同步、跨项目翻译、多语言提取、数据处理",
            "🎨 侧边栏增强：支持分组折叠/展开（▼/▶切换）",
            "📜 侧边栏滚动支持：功能过多时自动显示滚动条",
            "🔧 修复打包脚本Unicode编码问题（GBK控制台兼容）"
        ]
    },
    "1.44.0": {
        "date": "2026-01-12",
        "changes": [
            "⚡ 打包脚本性能优化",
            "🚀 增量构建支持：通过文件哈希缓存检测变化，未变化时跳过构建",
            "📦 精简打包体积：扩展排除列表，激进过滤不需要的binaries/datas",
            "🔧 优化runtime hook：减少启动时间开销",
            "✨ 新增构建选项：--fast（快速模式）、--skip-unchanged（增量构建）",
            "📊 构建耗时统计和智能清理功能"
        ]
    },
    "1.43.1": {
        "date": "2026-01-12",
        "changes": [
            "🔧 修复 PyInstaller 打包后 numpy 导入错误",
            "📦 添加运行时钩子 pyi_rth_numpy_fix.py 解决 numpy 源目录检测问题",
            "✨ 更新 hiddenimports 包含必需的 numpy 模块（__config__, _multiarray_tests等）",
            "🛠️ 修复二进制文件过滤规则，保留 numpy 必需的测试模块"
        ]
    },
    "1.43.0": {
        "date": "2026-01-10",
        "changes": [
            "⚡ GUI启动性能优化 4-6倍快",
            "🚀 实施Tab延迟加载机制（仅在用户切换时创建Tab UI）",
            "📖 模块延迟导入优化（减少启动时导入时间）",
            "🔧 后台预加载常用处理器（避免首次使用卡顿）",
            "📊 启动时间从2-3秒降至0.5秒",
            "📝 添加性能诊断工具（gui_startup_profiler.py）"
        ]
    },
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


def _parse_version_key(version_key: str):
    """将版本号字符串转换为可比较的元组。"""
    try:
        return tuple(int(part) for part in version_key.split('.'))
    except Exception:
        return (0, 0, 0)


def get_latest_changes():
    """获取最新版本的更新内容"""
    if __version__ in VERSION_HISTORY:
        return VERSION_HISTORY[__version__]["changes"]

    if not VERSION_HISTORY:
        return []

    latest_version = max(VERSION_HISTORY.keys(), key=_parse_version_key)
    return VERSION_HISTORY[latest_version]["changes"]


def increment_version(part: str = "patch") -> str:
    """
    自动递增版本号并更新 version.py 文件
    
    Args:
        part: 要递增的部分，可选 'major', 'minor', 'patch'
              - major: 1.0.0 -> 2.0.0
              - minor: 1.0.0 -> 1.1.0  
              - patch: 1.0.0 -> 1.0.1 (默认)
    
    Returns:
        新版本号字符串
    """
    import re
    from datetime import datetime
    from pathlib import Path
    
    global __version__, __version_info__, __build_date__
    old_version = __version__
    
    # 解析当前版本
    major, minor, patch = __version_info__
    
    # 递增版本号
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    new_version_info = (major, minor, patch)
    new_build_date = datetime.now().strftime("%Y-%m-%d")
    
    # 读取当前文件
    version_file = Path(__file__)
    content = version_file.read_text(encoding='utf-8')
    
    # 更新版本信息
    content = re.sub(
        r'__version__ = "[\d.]+"',
        f'__version__ = "{new_version}"',
        content
    )
    content = re.sub(
        r'__version_info__ = \([\d, ]+\)',
        f'__version_info__ = ({major}, {minor}, {patch})',
        content
    )
    content = re.sub(
        r'__build_date__ = "[\d-]+"',
        f'__build_date__ = "{new_build_date}"',
        content
    )
    
    # 写回文件
    version_file.write_text(content, encoding='utf-8')
    
    # 更新全局变量
    __version__ = new_version
    __version_info__ = new_version_info
    __build_date__ = new_build_date
    
    print(f"[VERSION] 版本已更新: {old_version} -> {new_version}")
    print(f"[VERSION] 构建日期: {new_build_date}")
    
    return new_version


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
