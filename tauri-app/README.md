# GameTools Tauri 版本

这是使用 Tauri 框架重新实现的 GameTools 图形界面版本。

## ✨ 特性

- 🚀 **更快的性能**: 使用 Rust 和现代 Web 技术，启动速度和运行性能显著提升
- 📦 **更小的体积**: 相比 Electron，安装包体积减少 70%+
- 🔒 **更安全**: Tauri 提供更严格的安全机制和权限控制
- 🎨 **现代化 UI**: 采用现代 Web 技术构建，界面更美观流畅
- 🌍 **跨平台**: 支持 Windows、macOS 和 Linux

## 📋 系统要求

### 开发环境

1. **Node.js**: 16.x 或更高版本
2. **Rust**: 最新稳定版
3. **Python**: 3.7+ (用于核心功能)

### Windows 特定要求

- Microsoft C++ Build Tools
- WebView2 Runtime (Windows 10 1803+ 自带)

### macOS 特定要求

- Xcode Command Line Tools
- macOS 10.13 或更高版本

### Linux 特定要求

```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev

# Fedora
sudo dnf install webkit2gtk3-devel \
    openssl-devel \
    curl \
    wget \
    libappindicator-gtk3 \
    librsvg2-devel

# Arch
sudo pacman -S webkit2gtk \
    base-devel \
    curl \
    wget \
    openssl \
    appmenu-gtk-module \
    gtk3 \
    libappindicator-gtk3 \
    librsvg
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd tauri-app
npm install
```

### 2. 开发模式运行

```bash
npm run tauri:dev
```

### 3. 构建生产版本

```bash
npm run tauri:build
```

构建完成后，所有安装包和可执行文件将自动复制到 `../dist/` 目录。

## 📦 安装包

构建后的安装包位于 `../dist/` 目录：

- **Windows**: `.msi` 或 `.exe` 文件
- **macOS**: `.dmg` 或 `.app` 文件
- **Linux**: `.deb`, `.rpm` 或 `.AppImage` 文件

## 🛠️ 技术栈

### 前端
- HTML5 + CSS3 + JavaScript (原生)
- Vite (开发服务器和构建工具)
- Tauri API (系统调用)

### 后端
- Rust (Tauri 核心)
- Python (业务逻辑)

## 📖 项目结构

```
tauri-app/
├── src/                    # 前端源代码
│   ├── main.js            # 主 JavaScript 文件
│   └── styles.css         # 样式文件
├── src-tauri/             # Tauri Rust 后端
│   ├── src/
│   │   └── main.rs       # Rust 主程序
│   ├── Cargo.toml        # Rust 依赖配置
│   ├── tauri.conf.json   # Tauri 配置
│   └── build.rs          # 构建脚本
├── index.html             # 主 HTML 文件
├── package.json           # Node.js 依赖
└── vite.config.js         # Vite 配置
```

## 🎯 功能模块

### 1. 越南文检测导出
- 扫描目录中的 Excel 和 CSV 文件
- 检测越南文内容并导出结果
- 支持递归扫描子目录

### 2. JSON 格式检测
- 检测 JSON 文件格式一致性
- 识别常见的格式错误
- 支持批量检测

### 3. Excel 数据处理
- 根据指定列分组数据
- 多文件或单文件输出模式
- 自动生成文件名

### 4. 翻译提取工具
- 批量提取 Excel 文件中的文本
- 支持多语言内容提取
- 生成统一格式的翻译表

### 5. 表字段导出
- 自动检测包含文本的列
- 智能过滤代码字段
- 支持 JSON/Excel/CSV 输出

### 6. 多语言翻译提取
- 基于 JSON 配置的智能提取
- 支持多个语言目录
- 字段类型筛选

## ⚙️ 配置说明

### Tauri 配置 (`src-tauri/tauri.conf.json`)

主要配置项：
- `identifier`: 应用标识符
- `windows`: 窗口设置（大小、标题等）
- `allowlist`: 权限配置
- `bundle`: 打包配置

### Python 集成

Tauri 通过 Rust 的 `Command` API 调用 Python 脚本。确保：
1. Python 已正确安装并在 PATH 中
2. 所有 Python 依赖已安装（见 `../core/requirements.txt`）
3. Python 脚本路径正确

## 🔧 开发说明

### 添加新功能

1. **前端**: 在 `src/main.js` 中添加事件处理
2. **Rust**: 在 `src-tauri/src/main.rs` 中添加 Tauri 命令
3. **Python**: 在 `../core/` 中实现业务逻辑

### 调试

```bash
# 开启开发者工具
npm run tauri:dev
# 在应用中按 F12 打开开发者工具
```

### 日志

Rust 日志会输出到控制台，可通过以下方式查看：

```rust
println!("调试信息: {:?}", data);
```

## 🐛 常见问题

### 1. Rust 编译失败

确保已安装最新的 Rust 工具链：
```bash
rustup update
```

### 2. Python 脚本执行失败

检查 Python 路径和依赖：
```bash
python --version
pip list
```

### 3. WebView2 错误 (Windows)

下载并安装 WebView2 Runtime：
https://developer.microsoft.com/microsoft-edge/webview2/

### 4. 权限错误

检查 `tauri.conf.json` 中的 `allowlist` 配置，确保所需权限已启用。

## 📝 与原 Tkinter 版本对比

| 特性 | Tkinter 版本 | Tauri 版本 |
|------|-------------|-----------|
| 启动速度 | ~2-3秒 | ~0.5-1秒 |
| 内存占用 | ~80-120MB | ~40-60MB |
| 安装包大小 | ~100MB | ~15-25MB |
| 界面美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 跨平台支持 | ✅ | ✅ |
| 开发维护 | Python | Rust + Web |

## 🤝 贡献

欢迎贡献代码！请确保：
1. 代码风格一致
2. 添加必要的注释
3. 测试所有功能

## 📄 许可证

与主项目保持一致

## 🔗 相关链接

- [Tauri 官方文档](https://tauri.app/)
- [Rust 学习资源](https://www.rust-lang.org/learn)
- [Vite 文档](https://vitejs.dev/)
