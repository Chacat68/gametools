# 本地化主流程 UI 增强方案

> 状态：**已实施**（2026-06-05）—— 详见 `gui/gametools_unified.py` 与 `docs/TABLE_RANGE_TRANSLATOR_GUIDE.md`「从字段导出接续」。

---

## 1. 目标

1. **对齐认知**：界面顺序或说明能反映真实数据流（字段 → 合并 JSON → 多语言提取 → 批量改表）。  
2. **减少重复操作**：字段导出成功后，一键把「合并 JSON + 各语言目录」带到多语言提取页。  
3. **侧栏顺序**：已按数据流排列（字段 → 多语言 → 改表 → 跨项目）；高频改表仍在主要流程内靠前完成多语言之后。  
4. **文档同步**：README / 指南与当前统一 GUI 一致。

---

## 2. 建议的标准流水线（数据依赖）

```text
字段导出（多语言目录 → 输出目录）
    → field_extraction_result_merged.json（仅 output_format=json 时生成）
多语言提取（合并 JSON + 同套语言目录 → 输出）
    → 译员/流程外处理
批量改表（映射表 + JSON 配置 → 回写 Excel）
```

**跨项目翻译**、**JSON 检测**、**Excel 数据处理** 与上链并行，不在此链强制顺序内。

---

## 3. 分阶段实施

| 阶段 | 内容 | 风险 | 建议优先级 |
|------|------|------|------------|
| A | 一键衔接：字段导出 → 填充多语言提取 | 低 | P0 |
| B | 导航/首页：流水线顺序 + 双入口说明 | 低（纯文案与元组顺序） | P1 |
| C | README「界面说明」重写为统一工作台 | 低 | P1 |
| D | 合并 JSON 文件名常量抽取（避免硬编码两处） | 低 | P2（可与 A 一起做） |
| E | 冷启动：按页签延迟 import | 中（重构面大） | 待定 |

---

## 4. 改动清单（按文件）

### 4.1 `gui/gametools_unified.py`（主改动）

| 改动项 | 位置/线索 | 说明 |
|--------|-----------|------|
| **A1. 新方法** | 新增如 `_apply_field_export_to_trt(merged_json_path=None)` | 设置 `trt_merged_json_var`；将 `field_*_dir_var` 复制到 `trt_*_dir_var`（仅当字段目录非空时可复制）；调用已有 `_detect_merged_json_languages`；可选将 `trt_output_dir_var` 设为字段 `field_output_dir_var` 或保持用户原值（方案建议：默认同步输出目录为字段输出目录，避免用户再找路径）。 |
| **A2. 完成回调** | `_field_extraction_thread` 成功分支末尾 | 若 `output_format == 'json'` 且 `all_stats['output_files']` 中含合并文件路径（或拼接 `output_dir / field_extraction_result_merged.json` 并 `os.path.exists`），在 UI 线程提示中增加「下一步」：例如在 `dialog_message` 中说明，或增加独立按钮状态（见 A3）。 |
| **A3. 新按钮** | `create_field_extractor_tab` 的 `action_panel` | 例如「将结果用于多语言提取」：`state=disabled`，仅在本次 JSON 导出成功后在 `_field_extraction_thread` 末尾 `after(0)` 设为 `normal`；点击后调用 A1 并 `select_tab`/`_show_tab` 切换到 `table_range_translator`（需查现有切页 API）。 |
| **A4. 常量** | 与 `core/excel_field_extractor.py` 一致 | 合并文件名 `field_extraction_result_merged.json` 建议抽到 `core/constants.py` 或提取器模块常量，GUI 与 core 共用，避免改名不同步。 |
| **B1. `NAV_SECTIONS`** | 约 85–88 行 | 「主要流程」元组改为依赖顺序示例：`field_extractor` → `table_range_translator` → `batch_modifier` → `cross_project_translator`（若产品坚持改表置顶，可仅改文案不改顺序，见 §5）。 |
| **B2. `HOME_FLOW_SPECS` / `HOME_SUPPORT_SPECS`** | 约 91–101 行 | 首页卡片：增加「标准出包流」三步简述；保留「批量改表」为高频入口说明。 |
| **B3. `TAB_DESCRIPTIONS`** | 约 103–110 行 | 各页一句话中体现上下游（如字段导出「为多语言提取生成合并 JSON」）。 |

**需查阅的现有 API**（实现时确认）：

- 切换页签：搜索 `_select_nav`、`show_tab`、`notebook` 等与 `last_active_tab` 相关的逻辑。  
- 表单持久化：`_FORM_STATE_MAP` 已含 `field.*` / `trt.*`（约 343–358 行），A1 写入后若需立即落盘可调用已有 `_save_form_state`（若存在）。

### 4.2 `core/excel_field_extractor.py`

| 改动项 | 说明 |
|--------|------|
| **D1** | 将 `"field_extraction_result_merged.json"` 改为模块级或 `core.constants` 中的常量，生成文件时使用该常量。 |

### 4.3 `core/constants.py`（若采用集中常量）

| 改动项 | 说明 |
|--------|------|
| **D2** | 新增例如 `FIELD_EXTRACTION_MERGED_JSON_NAME = "field_extraction_result_merged.json"`；`excel_field_extractor` 与 GUI 衔接逻辑引用之。 |

### 4.4 `README.md`

| 改动项 | 说明 |
|--------|------|
| **C1** | 「界面说明」一节改为统一工作台：字段导出 → 多语言提取 → 批量改表；辅助工具单独小节。 |
| **C2** | 删除或改写已不再存在的独立页签叙述（如与当前 GUI 不符的「越南文检测」「Excel 扫描导出」独立流程），改为指向实际页签名。 |

### 4.5 `docs/TABLE_RANGE_TRANSLATOR_GUIDE.md` 或 `docs/MULTILANG_JSON_GUIDE.md`（择一或两处各加一小节）

| 改动项 | 说明 |
|--------|------|
| **C3** | 增加「从字段导出接续」：合并 JSON 文件名、与字段页语言目录一致、界面上「将结果用于多语言提取」按钮行为说明。 |

### 4.6 测试（可选但推荐）

| 文件 | 说明 |
|------|------|
| `test/test_gui_background_tasks.py` 或新建 `test/test_workflow_handoff.py` | 若难以测 Tk，可对抽出的纯函数（例如「根据字段 vars 生成 trt 填充 dict」）做单测；否则以手工验收为主。 |

---

## 5. 产品二选一（评审时定）

**侧栏顺序**

- **方案 5a（推荐）**：侧栏「主要流程」按数据流排序（字段 → 多语言 → 改表 → 跨项目），与方案一致。  
- **方案 5b**：侧栏保持「改表优先」，仅在首页与 `TAB_DESCRIPTIONS` 中写清推荐流水线，改动更小、老用户习惯不变。

请在评审中选定 5a 或 5b。

---

## 6. 验收标准

1. JSON 字段导出成功后，用户可一键填充多语言提取页的 JSON 路径与各语言目录（与字段页一致），并触发语言检测标签更新。  
2. 若导出格式为 CSV/Excel，无合并 JSON：按钮保持禁用或点击时提示「请先使用 JSON 格式导出以生成合并配置」。  
3. 合并文件不存在时：提示错误，不覆盖用户已有 TRT 有效配置（可选：仅填充存在的字段）。  
4. README 与至少一篇 `docs/*` 指南描述与上述行为一致。  
5.（若做 5a）新用户按侧栏从上到下即可完成标准出包流。

---

## 7. 不在本方案内

- PyInstaller 打包脚本、版本号策略不变。  
- 批量改表与多语言提取之间的 CSV/映射自动衔接（若需另开需求）。  
- 大范围延迟 import（阶段 E）单独评估。

---

## 8. 预估工作量

| 阶段 | 人天（量级） |
|------|----------------|
| A + D | 0.5–1 |
| B + C | 0.5 |
| 测试与打磨 | 0.5 |

---

*文档版本：初稿，与代码仓库同步迭代。*
