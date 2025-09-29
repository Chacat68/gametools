# gametools
策划本地化工具

## 工具目录

### 📁 json_format_detector/
JSON文件text字段格式检测工具（命令行版本）

- 自动分析JSON文件中指定字段的格式模式
- 检测与通用格式不一致的内容
- 支持多种格式特征检测（长度、行数、空格、换行符等）
- 生成详细的检测报告
- 支持嵌套JSON结构

**快速开始：**
```bash
cd json_format_detector
python detect_format.py example_data.json
```

详细说明请查看 [json_format_detector/README.md](json_format_detector/README.md)

### 📁 gui/
JSON文件text字段格式检测工具（图形界面版本）

- 🖥️ 直观的图形界面，操作简单
- 📁 文件浏览和选择功能
- 🔍 自定义检测字段名
- 📊 实时显示检测结果
- 💾 保存检测报告到文件
- ⚡ 多线程处理，界面响应流畅
- 📦 可打包成独立的exe文件

**快速开始：**
```bash
cd gui
python run_gui.py
```

**打包成exe：**
```bash
cd gui
python build.py
```

详细说明请查看 [gui/README.md](gui/README.md)

### 📁 dist/
输出文件目录

- 存放构建生成的exe文件
- 包含主程序和便携版包
- 可直接分发给用户使用

**文件说明：**
- `JSON格式检测工具.exe` - 主程序
- `JSON格式检测工具_便携版/` - 便携版包（包含使用说明）

详细说明请查看 [dist/README.md](dist/README.md)