#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理迁移测试。"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from version import get_version


def _reset_config_manager():
    ConfigManager._instance = None
    ConfigManager._initialized = False


def test_legacy_visible_pages_migration():
    temp_dir = tempfile.mkdtemp()
    try:
        config_path = Path(temp_dir) / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "version": "1.27.0",
                    "visible_pages": {
                        "excel_processor": False,
                        "cross_project": True,
                        "about": True,
                    }
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        _reset_config_manager()
        manager = ConfigManager(str(config_path))

        assert manager.config.version == get_version(), "配置版本应迁移到当前应用版本"
        assert manager.config.tabs.excel_data_processor is False, "excel_processor 应迁移为 excel_data_processor=False"
        assert manager.config.tabs.cross_project_translator is True, "cross_project 应迁移为 cross_project_translator=True"

        manager.save_config()
        saved_data = json.loads(config_path.read_text(encoding="utf-8"))
        assert saved_data["visible_pages"]["about"] is True, "未知旧字段应继续保留"
        assert saved_data["tabs"]["excel_data_processor"] is False, "迁移后的 tabs 值应持久化"
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_tabs_take_precedence_over_legacy_visible_pages():
    temp_dir = tempfile.mkdtemp()
    try:
        config_path = Path(temp_dir) / "config.json"
        config_path.write_text(
            json.dumps(
                {
                    "tabs": {
                        "excel_data_processor": True,
                    },
                    "visible_pages": {
                        "excel_processor": False,
                    }
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        _reset_config_manager()
        manager = ConfigManager(str(config_path))
        assert manager.config.tabs.excel_data_processor is True, "现有 tabs 配置应优先于 legacy visible_pages"
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    tests = [
        ("legacy visible_pages 迁移", test_legacy_visible_pages_migration),
        ("tabs 优先级", test_tabs_take_precedence_over_legacy_visible_pages),
    ]

    all_passed = True
    print("=" * 60)
    print("配置管理迁移测试")
    print("=" * 60)

    for name, test_func in tests:
        try:
            passed = test_func()
        except Exception as exc:
            passed = False
            print(f"❌ {name}: {exc}")
        else:
            print(f"✅ {name}" if passed else f"❌ {name}")

        all_passed = all_passed and passed

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())