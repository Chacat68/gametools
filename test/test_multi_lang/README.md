# 多语言翻译提取测试夹具

## 用途

本目录位于 `test/` 下，只保存最小配置夹具，供测试脚本或人工复制参考。
真正运行 `test_multi_lang_folders.py` 时，会在项目根目录动态创建 `test_multi_lang/` 工作目录，并在其中生成 Excel 样例和导出文件。

生成的 Excel 样例行布局与 **[EXCEL_TABLE_LAYOUT.md](../docs/EXCEL_TABLE_LAYOUT.md)**（`FIELD_NAME_ROW` / `FIELD_TYPE_ROW` / `DATA_START_ROW`）一致，便于与字段导出、多语言提取联调。

## 当前目录结构

```
test/test_multi_lang/
├── field_config.json    # JSON配置文件
├── README.md
```

## 运行时目录

测试运行时会在项目根目录生成如下工作目录：

```text
test_multi_lang/
├── config/
├── config_zh/
├── config_th/
├── field_config.json
└── 翻译总表.xlsx
```

## 使用方法

### GUI测试
1. 启动 gametools
2. 选择"多语言翻译提取"页签
3. 先运行 `python test/test_multi_lang_folders.py` 生成根目录下的 `test_multi_lang/` 工作目录
4. 选择JSON配置: test_multi_lang\field_config.json
5. 选择越南文目录: test_multi_lang\config
6. 选择中文目录: test_multi_lang\config_zh
7. 选择泰文目录: test_multi_lang\config_th
8. 点击"开始提取"

### 命令行测试
```bash
python -c "from core.table_range_translator import TableRangeTranslator; \
t = TableRangeTranslator(); \
results = t.process_with_json_config_multi_lang('test_multi_lang\field_config.json', {'vn': 'test_multi_lang\config', 'zh': 'test_multi_lang\config_zh', 'th': 'test_multi_lang\config_th'}); \
t.generate_translation_master_table_multi_lang('test_multi_lang/翻译总表.xlsx'); \
print(t.get_processing_report())"
```

## 预期结果

生成的翻译总表包含：
- 工作表名称: 物品配置
- 列: 字段名 | 字段类型 | Excel位置 | 中文内容 | 越南文 | 泰文
- 只包含 name_cn 和 desc_cn 两个字段（id和type是策划字段，被过滤）

运行结束后，根目录下的 `test_multi_lang/config*` 目录和 `test_multi_lang/翻译总表.xlsx` 都属于可再生测试产物，可以随时删除。

