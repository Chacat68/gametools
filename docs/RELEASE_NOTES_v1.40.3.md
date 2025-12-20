# GameTools v1.40.3 发布说明

**发布日期**：2025年12月20日  
**文件大小**：42.74 MB  
**文件位置**：`dist/gametools_v1.40.3.exe`

---

## 🎯 本次更新亮点

### 重大修复：批量改表Position定位错误

修复了使用"翻译提取"格式CSV进行批量改表时，修改位置不正确的关键问题。

#### 问题描述
在修复前，当使用多语言提取功能导出的CSV（包含Position列，如"B7"、"E24"）进行批量改表时：
- 系统会从Position提取行号，再去Excel的ID列中查找
- 这导致定位错误，因为Excel的ID列值≠实际行号
- 修改会应用到错误的单元格

#### 解决方案
✅ **Position直接定位模式**
- 检测到Position列时，直接使用"B7"定位到B列第7行
- 无需通过ID匹配，精确到具体单元格
- 自动识别CSV格式，无需用户配置

✅ **完整兼容性**
- 支持翻译提取格式（含Position列）→ 直接定位
- 支持标准批量改表格式（无Position列）→ ID匹配
- 两种模式自动切换，向后兼容

---

## 📦 完整更新内容

### v1.40.3 (2025-12-20)
- 🔧 修复批量改表Position定位错误
- ✨ 新增Position直接定位模式（无需ID匹配）
- 🎯 Position列（如B7）直接定位到Excel单元格
- 🔄 自动检测CSV是否有Position列并切换模式
- 📝 新增列字母↔列号转换函数
- ✅ 支持翻译提取CSV精确位置修改
- 📚 新增POSITION_MODE_FIX.md详细说明文档

---

## 🚀 功能特性

### 批量改表功能增强
1. **智能格式识别**
   - 自动检测CSV格式类型
   - 翻译提取格式 → Position直接定位
   - 标准格式 → 传统ID匹配

2. **精确定位**
   ```
   CSV格式：Table,Sheet,Field,Type,Position,ZH,VN,TH
   示例行：artifact.xlsx,artifact,name,前端,B7,打狗棒,Xuyên Long Thương,หอก
   ```
   - Position "B7" = Excel的B列第7行
   - 直接写入单元格，无需查找ID

3. **完整工作流**
   - 多语言提取 → 导出CSV（含Position）
   - 翻译处理 → 填充VN/TH列
   - 批量改表 → 自动使用Position定位
   - 精确回写 → 修改原Excel文件

---

## 📋 使用示例

### 场景：使用翻译提取CSV批量改表

**步骤1：多语言提取**
```
功能：多语言文本提取
导出：系统翻译提取_20251220.csv
格式：Table,Sheet,Field,Type,Position,ZH,VN,TH
```

**步骤2：翻译处理**
```csv
artifact.xlsx,artifact,name,前端,B7,打狗棒,Xuyên Long Thương,หอก
artifact.xlsx,artifact,desc,前端,H7,对敌方...,Tạo sát thương...,สร้าง...
```

**步骤3：批量改表**
```
功能：批量改表
映射文件：系统翻译提取_20251220.csv
Excel目录：D:\项目\配置表
表名列：Table
ID列：ID（自动生成，不影响定位）
目标语言：VN / TH
```

系统自动：
1. 检测到Position列 → 启用Position模式
2. 读取artifact.xlsx
3. 定位B7单元格 → 写入"Xuyên Long Thương"
4. 定位H7单元格 → 写入"Tạo sát thương..."
5. 保存文件

**结果**：每个翻译精确写入到CSV中Position指定的单元格

---

## 🔧 技术改进

### 新增函数
```python
def get_column_number(col_letter: str) -> int:
    """Excel列字母转列号：A→1, B→2, AA→27"""
    
def get_column_letter(col_num: int) -> str:
    """Excel列号转列字母：1→A, 2→B, 27→AA"""
```

### 修改模块
- `core/batch_excel_modifier.py`
  - CSV格式转换保留Position列
  - Excel修改支持Position直接定位
  - 批量处理自动检测模式

### 测试验证
- `test/test_position_mode.py`
  - Position列检测 ✅
  - 列字母↔列号转换 ✅
  - CSV格式转换 ✅

---

## 📚 相关文档

- [POSITION_MODE_FIX.md](../docs/POSITION_MODE_FIX.md) - 详细修复说明
- [BATCH_MODIFIER_GUIDE.md](../docs/BATCH_MODIFIER_GUIDE.md) - 批量改表使用指南
- [MULTI_LANGUAGE_TEXT_EXTRACTOR.md](../docs/MULTI_LANGUAGE_TEXT_EXTRACTOR.md) - 多语言提取说明

---

## ⚠️ 重要提示

1. **备份数据**
   - 批量改表前建议启用"创建备份"选项
   - 备份文件名：原文件名.bak

2. **Excel要求**
   - 需要安装Microsoft Excel（使用xlwings引擎）
   - 建议关闭Excel文件后再执行批量改表

3. **大文件处理**
   - 支持78000+行CSV文件
   - 自动编码检测（UTF-8/GBK/GB2312）

---

## 🔄 升级建议

### 适用用户
- ✅ 使用多语言提取功能的用户（**强烈推荐升级**）
- ✅ 使用批量改表功能的用户
- ✅ 遇到"修改位置不正确"问题的用户

### 升级步骤
1. 关闭旧版程序
2. 备份重要数据
3. 运行 `gametools_v1.40.3.exe`
4. 无需额外配置，自动启用新功能

---

## 🐛 已知问题

无重大已知问题。

---

## 📞 技术支持

如有问题或建议，请联系开发团队。

**版权所有 © 2025 gametools开发团队**
