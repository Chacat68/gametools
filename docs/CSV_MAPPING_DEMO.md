# 批量改表功能 - CSV格式使用演示

## 演示场景

假设你有一个多语言游戏项目，需要批量修改装备和技能的翻译内容。

## 步骤1：准备CSV映射表

创建文件 `翻译映射表.csv`：

```csv
Table,Classification,ID,VN,TH,EN,Support-CH
armor_ancient.xlsx,des,1001,Mô tả áo giáp cổ đại,คำอธิบายชุดเกราะโบราณ,Ancient Armor Description,古代盔甲描述
armor_ancient.xlsx,name,1001,Áo giáp cổ đại,ชุดเกราะโบราณ,Ancient Armor,古代盔甲
weapon_master.xlsx,des,2001,Mô tả vũ khí bậc thầy,คำอธิบายอาวุธระดับปรมาจารย์,Master Weapon Description,大师武器描述
weapon_master.xlsx,name,2001,Vũ khí bậc thầy,อาวุธระดับปรมาจารย์,Master Weapon,大师武器
skill_magic.xlsx,des,3001,Mô tả kỹ năng phép thuật,คำอธิบายทักษะเวทมนตร์,Magic Skill Description,魔法技能描述
skill_magic.xlsx,name,3001,Kỹ năng phép thuật,ทักษะเวทมนตร์,Magic Skill,魔法技能
```

**列说明**：
- `Table`: 目标Excel文件名
- `Classification`: 字段类型（des=描述, name=名称）
- `ID`: 数据行标识
- `VN/TH/EN/Support-CH`: 各语言翻译内容

## 步骤2：准备JSON配置

创建文件 `装备技能配置.json`：

```json
{
  "language": "vn",
  "tables": [
    {
      "table_key": "armor_ancient",
      "table_name": "armor_ancient.xlsx",
      "fields": [
        {"field": "des", "column": "D"},
        {"field": "name", "column": "C"}
      ]
    },
    {
      "table_key": "weapon_master",
      "table_name": "weapon_master.xlsx",
      "fields": [
        {"field": "des", "column": "E"},
        {"field": "name", "column": "D"}
      ]
    },
    {
      "table_key": "skill_magic",
      "table_name": "skill_magic.xlsx",
      "fields": [
        {"field": "des", "column": "F"},
        {"field": "name", "column": "E"}
      ]
    }
  ]
}
```

## 步骤3：使用GUI执行

### 3.1 打开工具
双击运行 `启动策划工具.bat`

### 3.2 选择文件
1. 切换到"批量改表"页签
2. **JSON配置文件**：选择 `装备技能配置.json`
3. **映射表文件**：选择 `翻译映射表.csv` ⬅️ **CSV文件**
4. **语言**：选择 `VN`（越南语）
5. **Excel目录**：选择包含装备和技能Excel文件的文件夹
6. **报告文件**：系统会自动设置为 `翻译映射表_修改报告.xlsx`

### 3.3 预览（可选）
点击 **👁️ 预览映射表** 按钮查看CSV内容：

```
工作表: CSV文件 | 列数: 7 | 显示前20行

Table                | Classification       | ID                   | VN                   | ...
-----------------------------------------------------------------------------------------
armor_ancient.xlsx   | des                  | 1001                 | Mô tả áo giáp cổ đại | ...
armor_ancient.xlsx   | name                 | 1001                 | Áo giáp cổ đại       | ...
weapon_master.xlsx   | des                  | 2001                 | Mô tả vũ khí bậc thầy| ...
...
```

### 3.4 开始修改
1. 点击 **🚀 开始修改** 按钮
2. 等待进度条完成
3. 查看结果统计和修改报告

## 步骤4：查看结果

### 修改报告（自动生成的Excel）

| 表名 | ID | 字段 | 原值 | 新值 | 状态 |
|------|-----|------|------|------|------|
| armor_ancient.xlsx | 1001 | des | (旧描述) | Mô tả áo giáp cổ đại | ✅ 成功 |
| armor_ancient.xlsx | 1001 | name | (旧名称) | Áo giáp cổ đại | ✅ 成功 |
| weapon_master.xlsx | 2001 | des | (旧描述) | Mô tả vũ khí bậc thầy | ✅ 成功 |
| ... | ... | ... | ... | ... | ... |

### 统计信息

```
处理完成！
- 映射行数: 6
- 处理行数: 6
- 修改文件: 3
- 修改单元格: 6
- 跳过行数: 0
- 错误数: 0
```

## 步骤5：验证修改

打开修改后的Excel文件，检查对应列的内容是否已更新为CSV中的翻译。

## CSV vs Excel 对比

### 使用CSV的场景
✅ 翻译数据由外部系统导出（如翻译管理平台）
✅ 需要版本控制（Git友好）
✅ 大量数据自动生成
✅ 跨平台协作（无需Excel）
✅ 追求轻量级和快速加载

### 使用Excel的场景
✅ 需要多个工作表（按语言分类）
✅ 需要单元格格式（颜色标记等）
✅ 手动编辑和校对为主
✅ 包含批注和公式

## 常见问题

### Q: CSV文件中文乱码？
**A**: 使用UTF-8 with BOM编码保存。Excel中选择"CSV UTF-8 (逗号分隔)"。

### Q: 可以CSV和Excel混用吗？
**A**: 可以，但建议同一批次使用相同格式。

### Q: CSV文件如何快速生成？
**A**: 使用Python脚本：
```python
import pandas as pd
df = pd.DataFrame(data)
df.to_csv('映射表.csv', index=False, encoding='utf-8-sig')
```

## 总结

CSV格式让批量改表功能更加灵活和自动化友好，特别适合：
- 🤖 自动化工作流
- 🌐 多团队协作
- 📊 大数据量处理
- 🔄 频繁更新场景

---

**提示**：首次使用建议先用少量数据测试，确认配置正确后再进行大批量操作。
