# -*- coding: utf-8 -*-
"""
测试进度回调功能
确保 ExcelFieldExtractor 的进度回调在 GUI 中正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.excel_field_extractor import ExcelFieldExtractor


def test_progress_callback():
    """测试进度回调机制"""
    print("=" * 60)
    print("测试进度回调机制")
    print("=" * 60)
    
    progress_messages = []
    
    def test_callback(msg, pct=None):
        progress_messages.append((msg, pct))
        pct_str = f"{pct:.1f}%" if pct is not None else "N/A"
        print(f"  [进度] {pct_str} - {msg}")
    
    extractor = ExcelFieldExtractor()
    
    # 检查属性是否存在
    assert hasattr(extractor, 'set_progress_callback'), "缺少 set_progress_callback 方法"
    assert hasattr(extractor, '_report_progress'), "缺少 _report_progress 方法"
    assert hasattr(extractor, 'progress_callback'), "缺少 progress_callback 属性"
    
    print("✅ 属性检查通过")
    
    # 设置回调
    extractor.set_progress_callback(test_callback)
    assert extractor.progress_callback is not None, "回调设置失败"
    print("✅ 回调设置成功")
    
    # 测试回调调用
    extractor._report_progress("测试消息1", 25.0)
    extractor._report_progress("测试消息2", 50.0)
    extractor._report_progress("测试消息3", 100.0)
    
    assert len(progress_messages) == 3, f"回调调用次数错误: {len(progress_messages)}"
    print(f"✅ 回调调用成功 (共 {len(progress_messages)} 次)")
    
    # 验证消息内容
    assert progress_messages[0] == ("测试消息1", 25.0)
    assert progress_messages[1] == ("测试消息2", 50.0)
    assert progress_messages[2] == ("测试消息3", 100.0)
    print("✅ 消息内容正确")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_progress_callback()
    sys.exit(0 if success else 1)
