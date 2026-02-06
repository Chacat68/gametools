# 多语言翻译提取测试

## 文件夹结构

```
test_multi_lang/
├── config/              # 越南文目录（无后缀）
│   └── 物品配置.xlsx
├── config_zh/           # 中文目录（_zh后缀）
│   └── 物品配置.xlsx
├── config_th/           # 泰文目录（_th后缀）
│   └── 物品配置.xlsx
└── field_config.json    # JSON配置文件
```

## 使用方法

### GUI测试
1. 启动 gametools
2. 选择"多语言翻译提取"页签
3. 选择JSON配置: test_multi_lang/field_config.json
4. 选择越南文目录: test_multi_lang/config
5. 选择中文目录: test_multi_lang/config_zh
6. 选择泰文目录: test_multi_lang/config_th
7. 点击"开始提取"

### 命令行测试
```bash
python -c "from core.table_range_translator import TableRangeTranslator; \
t = TableRangeTranslator(); \
results = t.process_with_json_config_multi_lang('test_multi_lang/field_config.json', {'vn': 'test_multi_lang/config', 'zh': 'test_multi_lang/config_zh', 'th': 'test_multi_lang/config_th'}); \
t.generate_translation_master_table_multi_lang('test_multi_lang/翻译总表.xlsx'); \
print(t.get_processing_report())"
```

## 预期结果

生成的翻译总表包含：
- 工作表名称: 物品配置
- 列: 字段名 | 字段类型 | Excel位置 | 中文内容 | 越南文 | 泰文
- 只包含 name_cn 和 desc_cn 两个字段（id和type是策划字段，被过滤）
