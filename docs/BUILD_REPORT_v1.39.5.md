# GameTools v1.39.5 构建报告

**版本号**: 1.39.5  
**构建日期**: 2025-12-16  
**构建类型**: 功能增强 - 批量改表支持根据用户选择语言加载JSON

---

## 📋 更新摘要

本次更新主要增强批量改表功能，支持根据用户在GUI中选择的目标语言来加载JSON配置中对应语言的内容。这使得一个JSON文件可以包含多种语言的配置，系统会根据用户选择动态读取对应的配置。

### 🎯 核心功能

1. **load_json_config() 支持语言参数**
   - 新增 `target_lang_code` 可选参数
   - 格式3时根据参数选择要加载的语言配置
   - 未指定或未找到时使用第一个可用语言

2. **新增语言列表获取方法**
   - `get_available_languages_from_json()`: 获取JSON中所有可用语言
   - 返回格式: `[{'code': 'vn', 'name': '越南语', 'key': 'VN'}, ...]`

3. **GUI 手动模式增强**
   - 根据用户选择的目标语言列传递语言代码
   - 支持语言名称到代码的映射（如"越南语" -> "vn"）
   - 显示当前加载的语言代码

---

## 🔧 技术实现

### 1. 核心修改 - load_json_config()

**文件**: `core/batch_excel_modifier.py`

```python
def load_json_config(self, json_path: str, target_lang_code: str = None) -> Dict:
    """
    加载JSON配置文件，提取字段信息
    
    Args:
        json_path: JSON配置文件路径
        target_lang_code: 目标语言代码（如'vn', 'zh'），用于格式3
        
    Returns:
        Dict: 表名到字段信息的映射
    """
```

**关键逻辑**:
1. 检测JSON中所有可用的语言key
2. 如果指定了 `target_lang_code`，优先使用该语言
3. 未找到时使用第一个可用语言并输出警告
4. 记录加载的语言到 `self.json_language`

### 2. GUI 集成

**文件**: `gui/gametools_unified.py`

**修改点**: `_batch_modification_thread` 方法

```python
# 如果是手动模式且指定了目标语言，尝试加载对应语言的配置
target_lang_code = None
if not auto_match and target_language:
    # 从目标语言列名推断语言代码
    lang_mapping = {
        '中文': 'zh', '越南语': 'vn', '泰语': 'th',
        'zh': 'zh', 'vn': 'vn', 'th': 'th',
        'ZH': 'zh', 'VN': 'vn', 'TH': 'th',
        '繁体': 'tw', 'TW': 'tw', 'tw': 'tw'
    }
    target_lang_code = lang_mapping.get(target_language, target_language.lower())

field_config = self.batch_modifier.load_json_config(json_file, target_lang_code=target_lang_code)
```

### 3. 新增方法 - get_available_languages_from_json()

**功能**: 预扫描JSON文件，返回所有可用的语言

**用途**: 
- 未来可用于GUI中自动填充语言选择下拉框
- 帮助用户了解JSON中包含哪些语言配置

**返回示例**:
```python
[
    {'code': 'zh', 'name': '中文', 'key': 'ZH'},
    {'code': 'vn', 'name': '越南语', 'key': 'VN'},
    {'code': 'th', 'name': '泰语', 'key': 'TH'}
]
```

---

## 📊 支持的JSON格式

### 格式3（多语言配置）
```json
{
    "ZH": {
        "text_tables": [
            {
                "table_name": "armor.xlsx",
                "fields": ["des_zh", "name_zh"]
            }
        ]
    },
    "VN": {
        "text_tables": [
            {
                "table_name": "armor.xlsx",
                "fields": ["des_vn", "name_vn"]
            }
        ]
    },
    "TH": {
        "text_tables": [
            {
                "table_name": "armor.xlsx",
                "fields": ["des_th", "name_th"]
            }
        ]
    }
}
```

**行为**:
- 自动模式：使用第一个语言（ZH）
- 手动模式（选择越南语）：使用VN配置
- 手动模式（选择泰语）：使用TH配置

---

## 🔄 使用场景

### 场景1: 单语言JSON
```json
{
    "language": {"code": "vn", "name": "越南语"},
    "text_tables": [...]
}
```
- 自动/手动模式都使用该语言配置
- `target_lang_code` 参数被忽略

### 场景2: 多语言JSON（格式3）
```json
{
    "ZH": {...},
    "VN": {...},
    "TH": {...}
}
```
- **自动模式**: 使用第一个检测到的语言
- **手动模式 + 选择"越南语"**: 使用VN配置
- **手动模式 + 选择"泰语"**: 使用TH配置

### 场景3: 语言代码不匹配
JSON有 `{"ZH": {...}, "VN": {...}}`，用户选择"EN"
- 输出警告: "未找到语言 'en'，使用 'ZH'"
- 使用第一个可用语言（ZH）继续处理

---

## 🧪 测试建议

### 测试用例1: 单语言JSON + 手动模式
1. 准备单语言JSON（只有VN）
2. GUI手动模式选择"中文"
3. **预期**: 使用VN配置（因为JSON只有VN）

### 测试用例2: 多语言JSON + 手动模式匹配
1. 准备多语言JSON（ZH、VN、TH）
2. GUI手动模式选择"越南语"
3. **预期**: 使用VN配置

### 测试用例3: 多语言JSON + 手动模式不匹配
1. 准备多语言JSON（ZH、VN）
2. GUI手动模式选择"泰语"
3. **预期**: 输出警告，使用ZH配置

### 测试用例4: 多语言JSON + 自动模式
1. 准备多语言JSON（ZH、VN、TH）
2. GUI自动模式
3. **预期**: 使用第一个语言（通常是ZH）

---

## 📝 代码改动清单

### 修改文件

1. **core/batch_excel_modifier.py**
   - 新增: `get_available_languages_from_json()` 方法
   - 修改: `load_json_config()` 增加 `target_lang_code` 参数
   - 改进: 多语言选择逻辑

2. **gui/gametools_unified.py**
   - 修改: `_batch_modification_thread()` 增加语言代码推断
   - 改进: 手动模式下传递用户选择的语言代码

3. **version.py**
   - 更新: 版本号 1.39.4 → 1.39.5
   - 新增: v1.39.5 版本历史记录

### 新增文件

- `docs/BUILD_REPORT_v1.39.5.md` (本文档)

---

## 🚀 构建步骤

```bash
# 1. 更新版本信息
已完成 - version.py 已更新

# 2. 测试核心功能
python test/test_batch_modifier.py

# 3. 打包exe
python gui/build_unified.py

# 4. 输出验证
# 确认生成: dist/gametools_v1.39.5.exe
```

---

## 📌 兼容性说明

### 向后兼容
- ✅ 格式1和格式2的JSON继续正常工作
- ✅ 不传 `target_lang_code` 参数时行为不变
- ✅ GUI自动模式不受影响

### 新增特性
- ✨ 手动模式根据用户选择语言加载配置
- ✨ 支持一个JSON包含多种语言配置
- ✨ 提供语言列表获取API

---

## ⚠️ 注意事项

1. **语言代码映射**
   - 中文: zh/cn/ZH/CN
   - 越南语: vn/VN
   - 泰语: th/TH
   - 繁体: tw/TW

2. **格式优先级**
   - 检测到格式3时优先按格式3处理
   - 格式1和格式2共享相同处理逻辑

3. **日志输出**
   - 加载时显示检测到的所有可用语言
   - 语言不匹配时输出警告信息

---

## 🎉 总结

v1.39.5 版本实现了根据用户选择的目标语言动态加载JSON配置的功能，增强了批量改表的灵活性。用户现在可以:

- 在一个JSON文件中维护多种语言的配置
- 手动模式下自由选择要使用的语言
- 系统自动处理语言代码映射和匹配

这使得批量改表工具更加智能和易用，特别适合需要同时维护多个语言版本的项目。

---

**构建状态**: ⏳ 待打包  
**下一步**: 运行 `python gui/build_unified.py` 生成 v1.39.5 exe
