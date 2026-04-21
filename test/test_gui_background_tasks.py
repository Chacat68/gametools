#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GUI 后台任务辅助逻辑测试。"""

import sys
import tempfile
from pathlib import Path

import tkinter as tk

sys.path.insert(0, str(Path(__file__).parent.parent))

import gui.gametools_unified as unified_module
from core.batch_excel_modifier import BatchExcelModifier
from gui.gametools_unified import GameToolsUnified


class FakeThread:
    """用于拦截线程创建，避免测试里真的启动后台任务。"""

    instances = []

    def __init__(self, target=None, args=()):
        self.target = target
        self.args = args
        self.daemon = False
        self.started = False
        FakeThread.instances.append(self)

    def start(self):
        self.started = True


def _create_app():
    root = tk.Tk()
    root.withdraw()
    app = GameToolsUnified(root)
    root.update_idletasks()
    return root, app


def test_field_extraction_snapshots_arguments():
    """启动字段提取时应冻结线程参数，而不是依赖后续 UI 变量。"""
    root, app = _create_app()
    original_thread = unified_module.threading.Thread
    FakeThread.instances = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zh_dir = temp_path / "zh"
            output_dir = temp_path / "output"
            zh_dir.mkdir()
            output_dir.mkdir()

            app.field_zh_check_var.set(True)
            app.field_zh_dir_var.set(str(zh_dir))
            app.field_vn_check_var.set(False)
            app.field_th_check_var.set(False)
            app.field_output_dir_var.set(str(output_dir))
            app.field_output_format_var.set("json")
            app.field_recursive_var.set(False)

            unified_module.threading.Thread = FakeThread
            app.start_field_extraction()

            if len(FakeThread.instances) != 1:
                print("❌ 未正确创建后台线程")
                return False

            worker_args = FakeThread.instances[0].args

            app.field_output_format_var.set("csv")
            app.field_recursive_var.set(True)

            if worker_args[2] != "json" or worker_args[3] is not False:
                print(f"❌ 线程参数未冻结: {worker_args}")
                return False

            if str(app.field_extract_button.cget('state')) != 'disabled':
                print("❌ 启动任务后按钮未禁用")
                return False

            if app.status_var.get() != "正在提取表字段...":
                print(f"❌ 状态栏不正确: {app.status_var.get()}")
                return False

        print("✅ 字段提取参数冻结正常")
        return True
    finally:
        unified_module.threading.Thread = original_thread
        root.destroy()


def test_replace_processor_refreshes_batch_modifier():
    """批量改表处理器应允许替换为新的实例，避免跨次运行污染。"""
    root, app = _create_app()
    try:
        original_modifier = app.batch_modifier
        refreshed_modifier = app._replace_processor('batch_modifier', BatchExcelModifier)

        if refreshed_modifier is original_modifier:
            print("❌ 批量改表处理器未刷新")
            return False

        if app.batch_modifier is not refreshed_modifier:
            print("❌ 刷新后的处理器未写回缓存")
            return False

        print("✅ 处理器替换逻辑正常")
        return True
    finally:
        try:
            app.batch_modifier.close()
        except Exception:
            pass
        root.destroy()


def test_finish_background_task_updates_status_and_message():
    """统一收尾逻辑应恢复按钮、更新状态并发出正确消息。"""
    root, app = _create_app()
    captured = []

    try:
        app.batch_process_button.config(state="disabled")
        app._show_message = lambda kind, title, message: captured.append((kind, title, message))

        app._finish_background_task(
            widgets_to_enable=(app.batch_process_button,),
            status_message="批量修改完成",
            dialog_kind='info',
            dialog_title="完成",
            dialog_message="任务完成",
        )

        if str(app.batch_process_button.cget('state')) != 'normal':
            print("❌ 统一收尾未恢复按钮")
            return False

        if app.status_var.get() != "批量修改完成":
            print(f"❌ 统一收尾未更新状态: {app.status_var.get()}")
            return False

        if captured != [('info', '完成', '任务完成')]:
            print(f"❌ 统一收尾消息不正确: {captured}")
            return False

        print("✅ 统一收尾逻辑正常")
        return True
    finally:
        root.destroy()


def test_result_format_helpers():
    """结果格式化 helper 应输出稳定的文本块。"""
    root, app = _create_app()

    try:
        banner = app._format_banner_block("标题", width=6, char='-')
        lines = app._format_key_value_lines([("键A", "值A"), ("键B", 2)])
        prefixed = app._format_prefixed_lines(["项目1", "项目2"], prefix="* ")

        if banner != "------\n标题\n------\n":
            print(f"❌ 标题块格式不正确: {banner!r}")
            return False

        if lines != "键A: 值A\n键B: 2\n":
            print(f"❌ 键值行格式不正确: {lines!r}")
            return False

        if prefixed != "* 项目1\n* 项目2\n":
            print(f"❌ 前缀行格式不正确: {prefixed!r}")
            return False

        app._append_result_batch('json_detector', 'A', 'B', 'C')
        if app.get_result('json_detector') != 'ABC':
            print(f"❌ 批量追加结果不正确: {app.get_result('json_detector')!r}")
            return False

        print("✅ 结果格式化 helper 正常")
        return True
    finally:
        root.destroy()


def test_task_tracking_updates_recent_history():
    """任务摘要应写入任务卡和最近任务列表。"""
    root, app = _create_app()
    original_save = unified_module.config_manager.save_config
    original_recent_tasks = list(app.ui_config.recent_tasks)

    try:
        unified_module.config_manager.save_config = lambda: True
        app.ui_config.recent_tasks = []

        app._begin_task_tracking(
            'json_detector',
            '正在扫描 JSON 文件...',
            {'json_detector.path': r'F:\demo\data.json'},
        )
        app._complete_task_tracking(
            'json_detector',
            'success',
            'JSON 检测完成',
            [('报告行数', 12)],
            '详细报告可在结果窗口中查看。',
        )

        panel = app.task_panels['json_detector']
        if panel['status_var'].get() != '已完成':
            print(f"❌ 任务卡状态不正确: {panel['status_var'].get()}")
            return False

        summary_text = panel['summary_var'].get()
        if 'JSON 检测完成' not in summary_text or '报告行数: 12' not in summary_text:
            print(f"❌ 任务卡摘要不正确: {summary_text}")
            return False

        history = app.ui_config.recent_tasks
        if len(history) != 1:
            print(f"❌ 最近任务数量不正确: {history}")
            return False

        entry = history[0]
        if entry.get('key') != 'json_detector' or entry.get('inputs', {}).get('json_detector.path') != r'F:\demo\data.json':
            print(f"❌ 最近任务内容不正确: {entry}")
            return False

        print("✅ 任务跟踪与最近任务正常")
        return True
    finally:
        app.ui_config.recent_tasks = original_recent_tasks
        unified_module.config_manager.save_config = original_save
        root.destroy()


def main():
    tests = [
        ("字段提取参数冻结", test_field_extraction_snapshots_arguments),
        ("处理器替换", test_replace_processor_refreshes_batch_modifier),
        ("统一收尾逻辑", test_finish_background_task_updates_status_and_message),
        ("结果格式化 helper", test_result_format_helpers),
        ("任务跟踪与最近任务", test_task_tracking_updates_recent_history),
    ]

    print("=" * 60)
    print("GUI 后台任务辅助逻辑测试")
    print("=" * 60)

    passed = 0
    for name, test_func in tests:
        print(f"\n[测试] {name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {name} 失败")
        except Exception as exc:
            print(f"❌ {name} 异常: {exc}")

    print("\n" + "=" * 60)
    print(f"通过: {passed}/{len(tests)}")
    print("=" * 60)
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())