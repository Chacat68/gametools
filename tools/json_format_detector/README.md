# JSON格式检测工具

这个工具用于检测JSON文件中text字段的格式一致性，能够自动识别通用格式模式并找出与格式不一致的内容。

## 功能特点

- 自动分析JSON文件中指定字段的格式模式
- 检测与通用格式不一致的内容
- 支持多种格式特征检测（长度、行数、空格、换行符等）
- 生成详细的检测报告
- 支持嵌套JSON结构

## 文件说明

- `json_format_detector.py` - 完整的格式检测工具（支持命令行参数）
- `detect_format.py` - 简化的使用脚本
- `example_data.json` - 包含格式不一致内容的测试数据
- `requirements.txt` - 依赖说明（本工具只使用Python标准库）

## 使用方法

### 方法1：使用简化脚本
```bash
python detect_format.py example_data.json text
```

### 方法2：使用完整工具
```bash
python json_format_detector.py example_data.json --text-key text
```

### 方法3：输出到文件
```bash
python json_format_detector.py example_data.json --text-key text --output report.txt
```

## 检测的格式特征

- 文本长度
- 行数
- 是否包含换行符
- 是否包含制表符
- 是否包含空格
- 开头是否有空格
- 结尾是否有空格
- 是否包含引号
- 是否包含括号
- 是否包含特殊字符
- 单词数量
- 字符数量

## 示例

运行检测工具：
```bash
python detect_format.py example_data.json
```

输出示例：
```
正在检测文件: example_data.json
检测字段: text

============================================================
JSON文件text字段格式检测报告
============================================================
总文本数量: 10
格式不一致数量: 4

通用格式模式:
------------------------------
lengths: 不一致 (最常见: 6次, 占比: 60.0%)
line_counts: 1 (占比: 90.0%)
has_newlines: False (占比: 90.0%)
has_tabs: False (占比: 90.0%)
starts_with_space: False (占比: 90.0%)
ends_with_space: False (占比: 90.0%)
...

格式不一致的内容:
------------------------------
索引 3:
  文本: ' 这是有开头空格的文本，格式不一致。'
  问题: 开头空格不一致: 期望False, 实际True

索引 4:
  文本: '这是有结尾空格的文本，格式不一致。 '
  问题: 结尾空格不一致: 期望False, 实际True
...
```

## 技术实现

工具使用Python标准库实现，主要功能包括：

1. **JSON解析** - 支持单个对象和对象数组
2. **递归字段提取** - 支持嵌套JSON结构
3. **模式分析** - 统计各种格式特征
4. **通用模式识别** - 基于70%阈值识别通用格式
5. **不一致检测** - 对比每个文本与通用模式
6. **报告生成** - 生成详细的检测报告
