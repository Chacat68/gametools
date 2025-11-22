# GameTools Tauri 客户端构建指南

## 📋 前置条件

在构建 Tauri 客户端之前，需要安装以下工具：

### 1. Node.js ✅ (已安装 v20.13.1)
无需操作，已经安装。

### 2. Rust ❌ (需要安装)

Rust 是 Tauri 的核心依赖，必须安装。

#### Windows 安装步骤：

**方法 1: 使用 rustup-init.exe (推荐)**

1. 访问：https://www.rust-lang.org/tools/install
2. 下载并运行 `rustup-init.exe`
3. 选择默认安装选项（输入 1 后按回车）
4. 等待安装完成（可能需要 5-10 分钟）
5. 重启 PowerShell 或命令提示符

**方法 2: 使用 winget**

```powershell
winget install Rustlang.Rustup
```

#### 验证安装

安装完成后，运行以下命令验证：

```powershell
rustc --version
cargo --version
```

应该看到类似输出：
```
rustc 1.75.0 (82e1608df 2023-12-21)
cargo 1.75.0 (1d8b05cdd 2023-11-20)
```

### 3. Python (已安装)
用于核心业务逻辑，已经具备。

## 🚀 构建步骤

### 步骤 1: 安装 Node.js 依赖

```powershell
cd d:\dev\gametools\tauri-app
npm install
```

这会安装：
- Tauri CLI
- Vite
- 其他前端依赖

### 步骤 2: 安装 Python 依赖

```powershell
cd d:\dev\gametools
pip install -r core\requirements.txt
```

### 步骤 3: 构建生产版本

```powershell
cd tauri-app
npm run tauri:build
```

或者直接双击：`构建生产版本.bat`

## 📦 构建输出

构建成功后，生成的文件位于：

```
tauri-app\src-tauri\target\release\
├── gametools.exe                    # 可执行文件 (~3-5MB)
└── bundle\
    ├── msi\                        # MSI 安装包
    │   └── gametools_1.30.0_x64_en-US.msi
    └── nsis\                       # NSIS 安装程序
        └── gametools_1.30.0_x64-setup.exe
```

## ⚡ 快速开发

如果只是想测试，可以使用开发模式（无需完整构建）：

```powershell
cd tauri-app
npm run tauri:dev
```

或双击：`启动开发模式.bat`

## 🔧 常见问题

### 问题 1: Rust 安装后命令不可用

**解决方案**：
1. 关闭所有 PowerShell 窗口
2. 重新打开 PowerShell
3. 运行 `rustc --version` 验证

### 问题 2: 构建时出现 "Visual Studio C++ Build Tools" 错误

Rust 在 Windows 上需要 Visual C++ 构建工具。

**解决方案**：
1. 访问：https://visualstudio.microsoft.com/downloads/
2. 下载 "Build Tools for Visual Studio 2022"
3. 安装时选择 "C++ build tools" 工作负载
4. 重启计算机后重试

### 问题 3: npm install 失败

**解决方案**：
```powershell
# 清理缓存
npm cache clean --force

# 删除 node_modules
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# 重新安装
npm install
```

### 问题 4: 构建时间很长

**说明**：首次构建 Rust 项目需要：
- 下载和编译 Tauri 依赖（约 5-10 分钟）
- 后续构建会快得多（使用缓存）

**提示**：可以先使用开发模式测试功能。

## 📊 构建时间参考

| 步骤 | 首次 | 后续 |
|------|------|------|
| npm install | 2-5 分钟 | 秒级 |
| Rust 编译 | 5-10 分钟 | 1-2 分钟 |
| 总计 | 7-15 分钟 | 1-3 分钟 |

## 🎯 下一步

安装完 Rust 后：

1. ✅ 运行 `检查环境.bat` 验证所有依赖
2. ✅ 运行 `npm install` 安装 Node 依赖
3. ✅ 运行 `启动开发模式.bat` 测试功能
4. ✅ 运行 `构建生产版本.bat` 生成安装包

## 💡 提示

- **开发时**：使用开发模式（`npm run tauri:dev`）
- **发布时**：使用生产构建（`npm run tauri:build`）
- **测试时**：开发模式启动快，支持热重载
- **分发时**：使用 bundle 目录中的 .msi 或 .exe 安装包

---

**需要帮助？** 查看完整文档：`README.md` 和 `QUICKSTART.md`
