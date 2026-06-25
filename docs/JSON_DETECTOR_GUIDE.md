# JSON 错误检测 - 使用说明

> 检测目录/文件路径在 **「工作台」** 选择；「JSON 检测」页只读显示并执行。

## 功能概述

扫描 JSON 文件或整个目录，检测语法错误（尾随逗号、单引号、注释等）、编码问题，并生成可读报告。底层模块：`tools/json_error_detector/json_error_detector.py`。

## 工作台路径

- **JSON 检测目录**：可为单个 `.json` 文件，或包含 JSON 的文件夹（程序会自动识别）

## 操作步骤

1. 在 **「工作台」** 选择待检测路径  
2. 打开 **JSON 检测** 页，确认路径只读显示  
3. 点击 **开始检测**  
4. 在结果区查看报告；可用 **查看结果**、**保存报告**、**清空结果**

## 相关代码

- GUI：`gui/json_detector_page.py`
- 核心：`tools/json_error_detector/json_error_detector.py`
- 测试：`test/test_json_error_detector.py`

---

**文档版本**：与 [../version.py](../version.py) 同步维护  
**最后更新**：2026-06-25
