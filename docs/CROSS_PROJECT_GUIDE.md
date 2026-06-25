# 跨项目翻译 - 使用说明

> 路径均在 **「工作台」** 选择；「跨项目翻译」页只读显示并执行。缓存行为见 [CACHE_SYSTEM_GUIDE.md](CACHE_SYSTEM_GUIDE.md)。

## 功能概述

根据映射表，在两个项目（或目录）的 Excel 之间对齐、查找并输出翻译对应关系。GUI 默认使用带 LRU 缓存的 `CrossProjectTranslatorWithCache`（`core/cross_project_translator_cached.py`）。

## 工作台路径

| 变量 | 说明 |
|------|------|
| 映射文件 | 翻译映射 Excel/CSV |
| 扫描目录 | 待比对的策划表目录 |
| 结果文件 | 输出对照表保存路径 |

## 操作步骤

1. 在 **「工作台」** 选择映射文件、扫描目录、结果文件  
2. 打开 **跨项目翻译** 页，确认路径只读显示正确  
3. 点击 **开始生成**（或页内等价主按钮）  
4. 完成后使用 **查看结果** / **导出结果** / **保存报告**

## 相关代码

- GUI：`gui/cross_project_page.py`
- 核心：`core/cross_project_translator.py`、`core/cross_project_translator_cached.py`
- 测试：`test/test_cross_project_translator_cached.py`

---

**文档版本**：与 [../version.py](../version.py) 同步维护  
**最后更新**：2026-06-25
