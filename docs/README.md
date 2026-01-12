# GameTools 文档目录

> 游戏工具集 (v1.43.1) - 集成策划本地化、Excel处理、翻译提取等功能

## 📚 文档导航

### 🚀 快速入门
- **[BATCH_MODIFIER_GUIDE.md](BATCH_MODIFIER_GUIDE.md)** - 批量改表工具使用指南
- **[EXCEL_FIELD_EXTRACTOR_README.md](EXCEL_FIELD_EXTRACTOR_README.md)** - 表字段导出工具说明
- **[FIELD_FILTER_GUIDE.md](FIELD_FILTER_GUIDE.md)** - 字段过滤规则指南

### 🔧 核心功能文档

#### 多语言翻译
- **[MULTI_LANGUAGE_TEXT_EXTRACTOR.md](MULTI_LANGUAGE_TEXT_EXTRACTOR.md)** - 多语言文本提取工具
- **[TABLE_RANGE_TRANSLATOR_GUIDE.md](TABLE_RANGE_TRANSLATOR_GUIDE.md)** - 表范围翻译提取工具
- **[MULTILANG_JSON_GUIDE.md](MULTILANG_JSON_GUIDE.md)** - 多语言JSON配置指南
- **[MULTI_LANGUAGE_UI_LAYOUT.md](MULTI_LANGUAGE_UI_LAYOUT.md)** - 多语言UI布局文档

#### 缓存系统
- **[CACHE_SYSTEM_GUIDE.md](CACHE_SYSTEM_GUIDE.md)** - 翻译内容缓存机制详解

#### CSV格式支持
- **[CSV_MAPPING_SUPPORT.md](CSV_MAPPING_SUPPORT.md)** - CSV映射表格式说明
- **[TRANSLATION_CSV_SUPPORT.md](TRANSLATION_CSV_SUPPORT.md)** - 翻译CSV格式支持

### 📋 其他资源

- **[ERROR_LOGGING_FEATURE.md](ERROR_LOGGING_FEATURE.md)** - 错误日志和诊断功能
- **[BUILD_REPORT_v1.43.0.md](BUILD_REPORT_v1.43.0.md)** - 最新构建报告
- **[VERSION_HISTORY_ARCHIVE.md](VERSION_HISTORY_ARCHIVE.md)** - 版本历史归档

---

## 📖 按功能分类

### 🎯 表字段导出 (Excel Field Extractor)
用途：从Excel表格中提取字段名和类型信息

**相关文档：**
- EXCEL_FIELD_EXTRACTOR_README.md - 完整使用指南
- BATCH_MODIFIER_GUIDE.md - 批量改表配置

**快速开始：**
```bash
python gui/gametools_unified.py
# 选择"表字段导出"页签
```

---

### 🌍 多语言翻译提取 (Table Range Translator)
用途：按指定字段范围提取多语言翻译内容（中文、越南文、泰文等）

**相关文档：**
- TABLE_RANGE_TRANSLATOR_GUIDE.md - 完整功能指南
- MULTILANG_JSON_GUIDE.md - JSON配置格式说明
- MULTI_LANGUAGE_TEXT_EXTRACTOR.md - 文本提取详解

**快速开始：**
```bash
python gui/gametools_unified.py
# 选择"多语言翻译提取"页签
```

---

### 🔄 批量改表 (Batch Excel Modifier)
用途：批量修改多个Excel文件，支持映射表翻译

**相关文档：**
- BATCH_MODIFIER_GUIDE.md - 完整使用指南

**快速开始：**
```bash
python gui/gametools_unified.py
# 选择"批量改表"页签
```

---

### 💾 翻译缓存 (Translation Cache)
用途：加速跨项目翻译对应，通过缓存提升性能

**相关文档：**
- CACHE_SYSTEM_GUIDE.md - 缓存系统详解

---

## 🛠️ 配置文件说明

### config.json
运行时配置文件，包含：
- 缓存策略
- 并行处理设置
- 日志级别

### config_export.json
字段导出配置文件，包含：
- 字段提取规则
- 语言识别配置
- 表名/字段映射

---

## 📝 版本信息

当前版本：**v1.43.1** (2026-01-12)

最新特性：
- ⚡ GUI启动性能优化 4-6倍
- ✨ Excel转CSV功能
- 🛡️ 增强错误处理和诊断
- 📈 实时进度跟踪和ETA显示

详见：[BUILD_REPORT_v1.43.0.md](BUILD_REPORT_v1.43.0.md)

---

## 🔗 相关资源

- **项目主目录** - [../README.md](../README.md)
- **源代码** - [../core/](../core/) 核心模块
- **GUI程序** - [../gui/](../gui/) 用户界面
- **测试** - [../test/](../test/) 测试脚本

---

## ❓ 常见问题

### Q: 如何启动工具？
**A:** 双击运行 `启动策划工具.bat` 或执行 `python gui/gametools_unified.py`

### Q: 支持哪些文件格式？
**A:** .xlsx 和 .xls Excel文件格式

### Q: 如何使用缓存加速？
**A:** 参考 [CACHE_SYSTEM_GUIDE.md](CACHE_SYSTEM_GUIDE.md)

### Q: 遇到问题如何诊断？
**A:** 参考 [ERROR_LOGGING_FEATURE.md](ERROR_LOGGING_FEATURE.md)

---

## 📞 更新日期
- 文档最后更新：2026-01-12
- 对应程序版本：v1.43.1

