# 配置同步测试夹具

本目录位于 `test/` 下，只保存配置同步测试的最小夹具文件。

当前保留内容：
- `filter_config.json`：供配置同步测试读取的过滤规则样例。

说明：
- 运行 `test/test_config_sync.py` 时，会在项目根目录动态创建 `test_config_sync/` 工作目录。
- 根目录下的 `test_config_sync/source/`、`target1/`、`target2/`、`sync_report.xlsx` 都属于可再生测试产物，不需要长期保留在仓库中。