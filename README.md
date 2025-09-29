# 策划本地化工具

一个用于检测表格文件中越南文内容的本地化工具。

## 项目结构

```
gametools/
├── core/                    # 核心功能模块
│   ├── localization_checker.py
│   └── requirements.txt
├── tools/                   # 工具脚本
│   ├── demo.py
│   ├── quick_start.py
│   ├── run.bat
│   └── start_gui.bat
├── docs/                    # 文档
│   ├── README.md
│   └── 项目说明.md
├── config/                  # 配置文件
│   └── build_config.spec
├── samples/                 # 示例文件
│   ├── sample_valid.csv
│   ├── sample_invalid.csv
│   └── README.md
├── release/                 # 发布版本
│   ├── 策划本地化工具v0.0.2.exe
│   └── 使用说明v0.0.2.txt
├── gametool.py             # 主程序
└── README.md               # 项目说明
```

## 功能特性

- **批量扫描**: 检测目录下所有表格文件中的越南文
- **精确定位**: 单文件详细分析，定位越南文位置

## 快速开始

### 使用发布版本
1. 进入 `release/` 目录
2. 双击 `策划本地化工具v0.0.2.exe`

### 使用源码版本
1. 安装依赖: `pip install -r core/requirements.txt`
2. 启动GUI: `tools/start_gui.bat`
3. 或运行命令行版本: `tools/run.bat`

## 测试示例

使用 `samples/` 目录中的示例文件进行测试。

## 文档

详细文档请查看 `docs/` 目录。

## 版本信息

当前版本: v0.0.3 (已删除策划检测功能)
