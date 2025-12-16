# GameTools v1.39.6 更新说明

**版本号**: 1.39.6  
**发布日期**: 2025-12-16  
**更新类型**: 功能增强 - 批量改表智能语言检测

---

## 🎯 核心更新

### 自动语言检测

批量改表功能现在能够自动从映射表列名中检测语言，并加载JSON中对应语言的配置，**无需用户手动输入**。

### 工作流程

```
1. 用户选择映射表文件 
   ↓
2. 系统自动读取映射表列名（如: 表名, Classification, ID, VN）
   ↓
3. 智能检测语言列（VN → 越南语）
   ↓
4. 自动加载JSON中对应语言的配置
   ↓
5. 开始批量修改
```

---

## ✨ 新增功能

### 1. 智能语言检测

**新增方法**: `detect_language_from_mapping_columns(mapping_columns)`

**支持的检测模式**:
- **英文列名**: VN, TH, CH, Support-CH, Vietnamese, Thai, Chinese
- **中文列名**: 越南语, 泰语, 中文, 繁体
- **模糊匹配**: 包含VN/VIET/TH/THAI/CH/ZH等标识

**检测优先级**: 
```
越南语(vn) > 泰语(th) > 中文(zh) > 英语(en) > 其他语言
```

### 2. 自动配置加载

系统根据检测到的语言自动调用：
```python
field_config = batch_modifier.load_json_config(
    json_file, 
    target_lang_code='vn'  # 自动传入检测到的语言代码
)
```

### 3. 详细日志输出

```
正在检测映射表语言...
  - 从映射表列名检测到语言: vn (列名: VN)
✓ 检测到映射表语言: 越南语 (vn)

正在加载JSON配置...
  - 根据映射表检测结果，加载语言配置: vn
  - 检测到格式3（语言代码顶层key）: 越南语 (vn)
  - 可用语言: ZH, VN, TH
✓ 已加载 X 个表的字段配置
```

---

## 📊 使用示例

### 场景1: 越南语映射表

**映射表结构**:
```
| 表名          | Classification | ID | VN          |
|---------------|----------------|----|-------------|
| armor.xlsx    | name           | 1  | Áo giáp     |
| weapon.xlsx   | des            | 2  | Vũ khí mạnh |
```

**JSON配置** (包含多种语言):
```json
{
    "ZH": {"text_tables": [...]},
    "VN": {"text_tables": [...]},
    "TH": {"text_tables": [...]}
}
```

**系统行为**:
1. 检测到映射表有"VN"列
2. 自动识别为越南语(vn)
3. 自动加载JSON中的VN配置
4. 使用VN配置的字段列表进行批量修改

### 场景2: 泰语映射表

**映射表结构**:
```
| 表名          | Classification | ID | TH          |
|---------------|----------------|----|-------------|
| armor.xlsx    | name           | 1  | ชุดเกราะ    |
```

**系统行为**:
1. 检测到"TH"列
2. 识别为泰语(th)
3. 加载JSON中的TH配置

### 场景3: 中文列名

**映射表结构**:
```
| 表名          | Classification | ID | 越南语      |
|---------------|----------------|----|-------------|
| armor.xlsx    | name           | 1  | Áo giáp     |
```

**系统行为**:
1. 检测到"越南语"列
2. 识别为越南语(vn)
3. 加载VN配置

---

## 🔧 技术改进

### 核心代码

**batch_excel_modifier.py**:
```python
def detect_language_from_mapping_columns(self, mapping_columns: List[str]) -> Optional[str]:
    """从映射表的列名中检测语言代码"""
    language_patterns = {
        'zh': ['Support-CH', 'Polish-CH', 'CH', 'CN', 'ZH', 'Chinese', '中文'],
        'vn': ['VN', 'VI', 'Vietnamese', '越南语', '越南'],
        'th': ['TH', 'Thai', '泰语', '泰文'],
        # ... 更多语言
    }
    
    # 精确匹配
    for lang_code in priority_order:
        for pattern in language_patterns[lang_code]:
            for col in mapping_columns:
                if col.strip().upper() == pattern.upper():
                    return lang_code
    
    # 模糊匹配
    for col in mapping_columns:
        if 'VN' in col.upper() or 'VIET' in col.upper():
            return 'vn'
        # ... 其他模糊匹配规则
    
    return None
```

**gametools_unified.py** (GUI):
```python
# 从映射表中自动检测语言
df, mapping_columns = self.batch_modifier.load_mapping_table(mapping_file)
if mapping_columns:
    detected_lang = self.batch_modifier.detect_language_from_mapping_columns(mapping_columns)
    if detected_lang:
        target_lang_code = detected_lang

# 使用检测到的语言加载JSON配置
field_config = self.batch_modifier.load_json_config(json_file, target_lang_code=target_lang_code)
```

---

## 🧪 测试结果

### 自动化测试

运行 `python test/test_language_detection.py`:

```
✅ 越南语映射表（VN列）
✅ 泰语映射表（TH列）  
✅ 中文映射表（CH列）
✅ 中文映射表（Support-CH列）
✅ 越南语映射表（Vietnamese列）
✅ 中文列名（越南语）
✅ 中文列名（泰语）
✅ 混合列名（优先VN）
✅ 无语言列（返回None）

总计: 9/9 通过 🎉
```

---

## 📝 与v1.39.5的对比

| 功能 | v1.39.5 | v1.39.6 |
|------|---------|---------|
| 语言选择方式 | 手动输入（如"越南语"） | **自动检测** |
| JSON加载 | 根据手动输入加载 | **根据映射表自动加载** |
| 用户操作 | 需要知道并输入语言名称 | **无需手动输入** |
| 适用场景 | 需要人工判断语言 | **完全自动化** |

---

## ⚠️ 兼容性说明

### 向后兼容

- ✅ 检测失败时使用JSON第一个语言（与v1.39.5行为相同）
- ✅ 单语言JSON继续正常工作
- ✅ 所有v1.39.5的功能保持不变

### 新增行为

- 🆕 自动读取映射表列名
- 🆕 智能识别语言类型
- 🆕 自动选择JSON配置

### 错误处理

**场景**: 映射表检测失败或无语言列

**行为**:
```
⚠️ 未能从映射表检测到语言，将使用JSON中的第一个语言
```
系统继续使用JSON中的第一个可用语言，不会中断处理。

---

## 🎉 用户体验提升

### 之前（v1.39.5）

```
1. 打开映射表，查看有哪些语言列（VN? TH? CH?）
2. 在GUI"目标语言列"输入框填写"越南语"
3. 点击开始批量修改
```

### 现在（v1.39.6）

```
1. 选择映射表文件
2. 点击开始批量修改
3. ✅ 完成！（系统自动处理一切）
```

**操作步骤减少**: 3步 → 2步  
**人工判断**: 需要 → 不需要  
**出错风险**: 可能输错 → 自动识别  

---

## 📚 相关文档

- [test_language_detection.py](../test/test_language_detection.py) - 语言检测测试
- [test_multilang_json.py](../test/test_multilang_json.py) - 多语言JSON测试
- [MULTILANG_JSON_GUIDE.md](MULTILANG_JSON_GUIDE.md) - 多语言配置完整指南

---

## 🚀 下一步计划

可能的未来增强：
- [ ] GUI显示检测到的语言
- [ ] 支持用户手动覆盖检测结果
- [ ] 映射表多语言列同时存在时的智能选择
- [ ] 更多语言支持（俄语、德语、法语等）

---

## 📦 安装说明

**文件**: `dist/gametools_v1.39.6.exe`  
**大小**: 43.67 MB  
**运行要求**: Windows 7及以上，无需安装Python

**使用方法**: 双击运行 `gametools_v1.39.6.exe`

---

**文档版本**: 1.0  
**最后更新**: 2025-12-16
