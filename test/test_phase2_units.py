#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 模块单元测试
测试配置管理、结果过滤、输出格式等核心功能
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
    
    def tearDown(self):
        """测试后清理"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_config_get_set(self):
        """测试配置读写"""
        from core.config_manager import ConfigManager
        
        config = ConfigManager(str(self.config_file))
        
        # 测试读取默认值
        self.assertTrue(config.get('scan.enable_parallel'))
        self.assertEqual(config.get('cache.max_memory_mb'), 500.0)
        
        # 测试设置值
        config.set('scan.chunk_size', 20000)
        self.assertEqual(config.get('scan.chunk_size'), 20000)
        
        # 测试不存在的键
        self.assertIsNone(config.get('non.existent.key'))
    
    def test_config_save_load(self):
        """测试配置保存和加载"""
        from core.config_manager import ConfigManager
        
        config = ConfigManager(str(self.config_file))
        config.set('scan.max_workers', 8)
        config.save_config()
        
        # 验证文件存在
        self.assertTrue(self.config_file.exists())
        
        # 重新加载
        config2 = ConfigManager(str(self.config_file))
        config2.load_config()
        self.assertEqual(config2.get('scan.max_workers'), 8)
    
    def test_config_export_import(self):
        """测试配置导入导出"""
        from core.config_manager import ConfigManager
        
        config = ConfigManager(str(self.config_file))
        config.set('cache.max_memory_mb', 1000)
        
        export_file = Path(self.temp_dir) / "export.json"
        config.export_config(str(export_file))
        
        # 验证导出文件
        self.assertTrue(export_file.exists())
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['cache']['max_memory_mb'], 1000)


class TestResultFilter(unittest.TestCase):
    """结果过滤器测试"""
    
    def setUp(self):
        """准备测试数据"""
        self.test_data = [
            {'file': 'test1.xlsx', 'language': '越南文', 'row': 10, 'score': 8.5},
            {'file': 'test2.xlsx', 'language': '中文', 'row': 20, 'score': 7.0},
            {'file': 'test3.xlsx', 'language': '越南文', 'row': 5, 'score': 9.0},
            {'file': 'config.xlsx', 'language': '中越混合', 'row': 15, 'score': 6.5},
        ]
    
    def test_filter_equals(self):
        """测试等于过滤"""
        from core.result_filter import ResultFilter, FilterOperator
        
        filter_obj = ResultFilter()
        filter_obj.add_filter('language', FilterOperator.EQUALS, '越南文')
        results = filter_obj.apply(self.test_data)
        
        self.assertEqual(len(results), 2)
        for item in results:
            self.assertEqual(item['language'], '越南文')
    
    def test_filter_contains(self):
        """测试包含过滤"""
        from core.result_filter import ResultFilter, FilterOperator
        
        filter_obj = ResultFilter()
        filter_obj.add_filter('language', FilterOperator.CONTAINS, '越南')
        results = filter_obj.apply(self.test_data)
        
        self.assertEqual(len(results), 3)  # 越南文 + 中越混合
    
    def test_filter_greater_than(self):
        """测试大于过滤"""
        from core.result_filter import ResultFilter, FilterOperator
        
        filter_obj = ResultFilter()
        filter_obj.add_filter('row', FilterOperator.GREATER_THAN, 10)
        results = filter_obj.apply(self.test_data)
        
        self.assertEqual(len(results), 2)  # row=20 和 row=15
        for item in results:
            self.assertGreater(item['row'], 10)
    
    def test_filter_chain(self):
        """测试链式过滤"""
        from core.result_filter import ResultFilter, FilterOperator
        
        filter_obj = ResultFilter()
        results = (filter_obj
            .add_filter('language', FilterOperator.EQUALS, '越南文')
            .add_filter('score', FilterOperator.GREATER_THAN, 8.0)
            .apply(self.test_data))
        
        self.assertEqual(len(results), 2)  # score>8 的越南文
    
    def test_filter_regex(self):
        """测试正则过滤"""
        from core.result_filter import ResultFilter, FilterOperator
        
        filter_obj = ResultFilter()
        filter_obj.add_filter('file', FilterOperator.REGEX, r'test\d+')
        results = filter_obj.apply(self.test_data)
        
        self.assertEqual(len(results), 3)  # test1, test2, test3
    
    def test_quick_search(self):
        """测试快速搜索"""
        from core.result_filter import QuickSearch
        
        results = QuickSearch.search(self.test_data, 'config', fields=['file'])
        self.assertEqual(len(results), 1)
        self.assertIn('config', results[0]['file'])
    
    def test_quick_filter(self):
        """测试快速过滤"""
        from core.result_filter import quick_filter
        
        results = quick_filter(self.test_data, language='越南文')
        self.assertEqual(len(results), 2)


class TestOutputFormats(unittest.TestCase):
    """输出格式测试"""
    
    def setUp(self):
        """准备测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = [
            {
                'file': 'test.xlsx',
                'sheet': 'Sheet1',
                'row': 5,
                'content': 'Xin chào',
                'language': '越南文'
            }
        ]
    
    def tearDown(self):
        """清理"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_export_excel(self):
        """测试Excel导出"""
        from core.output_formats import ResultExporter, OutputFormat
        
        exporter = ResultExporter()
        output_path = Path(self.temp_dir) / "test.xlsx"
        
        success = exporter.export(
            self.test_data, 
            str(output_path), 
            format_type=OutputFormat.EXCEL
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
    
    def test_export_csv(self):
        """测试CSV导出"""
        from core.output_formats import ResultExporter, OutputFormat
        
        exporter = ResultExporter()
        output_path = Path(self.temp_dir) / "test.csv"
        
        success = exporter.export(
            self.test_data,
            str(output_path),
            format_type=OutputFormat.CSV
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
    
    def test_export_json(self):
        """测试JSON导出"""
        from core.output_formats import ResultExporter, OutputFormat
        
        exporter = ResultExporter()
        output_path = Path(self.temp_dir) / "test.json"
        
        metadata = {'version': '1.24.0', 'test': True}
        success = exporter.export(
            self.test_data,
            str(output_path),
            format_type=OutputFormat.JSON,
            metadata=metadata
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # 验证JSON内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('metadata', data)
            self.assertIn('data', data)
            self.assertEqual(data['metadata']['version'], '1.24.0')
    
    def test_export_html(self):
        """测试HTML导出"""
        from core.output_formats import ResultExporter, OutputFormat
        
        exporter = ResultExporter()
        output_path = Path(self.temp_dir) / "test.html"
        
        success = exporter.export(
            self.test_data,
            str(output_path),
            format_type=OutputFormat.HTML,
            title='测试报告'
        )
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
        
        # 验证HTML内容
        content = output_path.read_text(encoding='utf-8')
        self.assertIn('测试报告', content)
        self.assertIn('Xin chào', content)
    
    def test_auto_format_detection(self):
        """测试自动格式识别"""
        from core.output_formats import ResultExporter
        
        exporter = ResultExporter()
        
        # 测试各种扩展名
        extensions = ['.xlsx', '.csv', '.json', '.html', '.md', '.txt']
        for ext in extensions:
            output_path = Path(self.temp_dir) / f"test{ext}"
            success = exporter.export(self.test_data, str(output_path))
            self.assertTrue(success, f"Failed to export {ext}")
            self.assertTrue(output_path.exists(), f"File not created: {ext}")


class TestTaskController(unittest.TestCase):
    """任务控制器测试"""
    
    def test_task_lifecycle(self):
        """测试任务生命周期"""
        from core.task_controller import TaskController, TaskState
        
        controller = TaskController()
        
        # 初始状态
        self.assertEqual(controller.state, TaskState.IDLE)
        
        # 启动
        controller.start(10)
        self.assertEqual(controller.state, TaskState.RUNNING)
        
        # 暂停
        controller.pause()
        self.assertEqual(controller.state, TaskState.PAUSED)
        
        # 恢复
        controller.resume()
        self.assertEqual(controller.state, TaskState.RUNNING)
        
        # 完成
        controller.complete()
        self.assertEqual(controller.state, TaskState.COMPLETED)
    
    def test_task_cancel(self):
        """测试任务取消"""
        from core.task_controller import TaskController, TaskState
        
        controller = TaskController()
        controller.start(10)
        controller.cancel()
        
        self.assertEqual(controller.state, TaskState.CANCELLED)
    
    def test_check_point(self):
        """测试检查点"""
        from core.task_controller import TaskController
        
        controller = TaskController()
        controller.start(10)
        
        # 正常检查点
        should_continue = controller.check_point()
        self.assertTrue(should_continue)
        
        # 取消后检查点
        controller.cancel()
        should_continue = controller.check_point()
        self.assertFalse(should_continue)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestResultFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormats))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskController))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 60)
    print("Phase 2 模块单元测试")
    print("=" * 60)
    print()
    
    success = run_tests()
    
    print()
    print("=" * 60)
    if success:
        print("所有测试通过！")
    else:
        print("部分测试失败，请检查错误信息")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
