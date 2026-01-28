# -*- coding: utf-8 -*-
"""
新版 UI 全面测试脚本
检查所有页面的关键功能和潜在问题
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_module_imports():
    """测试模块导入"""
    print("=" * 60)
    print("1. 测试模块导入")
    print("=" * 60)
    
    modules = [
        'gui.gametools_modern',
        'gui.pages.base_page',
        'gui.pages.home_page',
        'gui.pages.about_page',
        'gui.pages.batch_modifier_page',
        'gui.pages.json_detector_page',
        'gui.pages.field_extractor_page',
        'gui.pages.cross_project_page',
        'gui.pages.table_range_page',
        'gui.pages.excel_processor_page',
    ]
    
    errors = []
    for mod_name in modules:
        try:
            __import__(mod_name)
            print(f"  ✅ {mod_name}")
        except Exception as e:
            print(f"  ❌ {mod_name}: {e}")
            errors.append((mod_name, str(e)))
    
    return len(errors) == 0, errors


def test_core_modules():
    """测试核心模块"""
    print("\n" + "=" * 60)
    print("2. 测试核心模块")
    print("=" * 60)
    
    modules = [
        ('core.batch_excel_modifier', 'BatchExcelModifier'),
        ('core.excel_field_extractor', 'ExcelFieldExtractor'),
        ('core.table_range_translator', 'TableRangeTranslator'),
        ('core.cross_project_translator', 'CrossProjectTranslator'),
    ]
    
    errors = []
    for mod_name, class_name in modules:
        try:
            mod = __import__(mod_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            instance = cls()
            print(f"  ✅ {class_name}")
        except Exception as e:
            print(f"  ❌ {class_name}: {e}")
            errors.append((class_name, str(e)))
    
    return len(errors) == 0, errors


def test_progress_callback_support():
    """测试进度回调支持"""
    print("\n" + "=" * 60)
    print("3. 测试进度回调支持")
    print("=" * 60)
    
    classes_to_check = [
        ('core.batch_excel_modifier', 'BatchExcelModifier'),
        ('core.excel_field_extractor', 'ExcelFieldExtractor'),
    ]
    
    errors = []
    for mod_name, class_name in classes_to_check:
        try:
            mod = __import__(mod_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            instance = cls()
            
            # 检查是否有进度回调支持
            has_callback = hasattr(instance, 'set_progress_callback')
            has_report = hasattr(instance, '_report_progress')
            
            if has_callback and has_report:
                print(f"  ✅ {class_name} - 支持进度回调")
            elif has_callback:
                print(f"  ⚠️ {class_name} - 有 set_progress_callback 但缺少 _report_progress")
                errors.append((class_name, "缺少 _report_progress"))
            else:
                print(f"  ❌ {class_name} - 不支持进度回调")
                errors.append((class_name, "缺少进度回调支持"))
        except Exception as e:
            print(f"  ❌ {class_name}: {e}")
            errors.append((class_name, str(e)))
    
    return len(errors) == 0, errors


def test_page_class_structure():
    """测试页面类结构"""
    print("\n" + "=" * 60)
    print("4. 测试页面类结构")
    print("=" * 60)
    
    pages = [
        ('gui.pages.batch_modifier_page', 'BatchModifierPage'),
        ('gui.pages.field_extractor_page', 'FieldExtractorPage'),
        ('gui.pages.cross_project_page', 'CrossProjectPage'),
        ('gui.pages.table_range_page', 'TableRangePage'),
        ('gui.pages.json_detector_page', 'JsonDetectorPage'),
        ('gui.pages.excel_processor_page', 'ExcelProcessorPage'),
    ]
    
    required_attrs = ['PAGE_KEY', 'PAGE_TITLE', 'PAGE_ICON', 'PAGE_DESCRIPTION', 'create_widgets']
    
    errors = []
    for mod_name, class_name in pages:
        try:
            mod = __import__(mod_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            
            missing = []
            for attr in required_attrs:
                if not hasattr(cls, attr):
                    missing.append(attr)
            
            if missing:
                print(f"  ⚠️ {class_name} - 缺少: {', '.join(missing)}")
                errors.append((class_name, f"缺少属性: {missing}"))
            else:
                print(f"  ✅ {class_name}")
        except Exception as e:
            print(f"  ❌ {class_name}: {e}")
            errors.append((class_name, str(e)))
    
    return len(errors) == 0, errors


def test_theme_and_components():
    """测试主题和组件"""
    print("\n" + "=" * 60)
    print("5. 测试主题和组件")
    print("=" * 60)
    
    components = [
        ('gui.modern_theme', 'ModernTheme'),
        ('gui.components.sidebar', 'ModernSidebar'),
        ('gui.components.widgets', 'ModernStatusBar'),
    ]
    
    errors = []
    for mod_name, class_name in components:
        try:
            mod = __import__(mod_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            print(f"  ✅ {class_name}")
        except Exception as e:
            print(f"  ❌ {class_name}: {e}")
            errors.append((class_name, str(e)))
    
    return len(errors) == 0, errors


def main():
    """运行所有测试"""
    print("=" * 60)
    print("GameTools 新版 UI 全面测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("模块导入", test_module_imports()))
    results.append(("核心模块", test_core_modules()))
    results.append(("进度回调", test_progress_callback_support()))
    results.append(("页面结构", test_page_class_structure()))
    results.append(("主题组件", test_theme_and_components()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    total_errors = []
    
    for name, (passed, errors) in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
            total_errors.extend(errors)
    
    print()
    if all_passed:
        print("🎉 所有测试通过！")
        return 0
    else:
        print(f"⚠️ 发现 {len(total_errors)} 个问题：")
        for item, error in total_errors:
            print(f"  - {item}: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
