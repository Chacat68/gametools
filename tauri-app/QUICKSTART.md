# Tauri 版本快速上手指南

本指南将帮助你快速开始使用 GameTools 的 Tauri 版本。

## 📋 前置要求检查

在开始之前，请确保已安装以下工具：

### 1. Node.js (必需)

```bash
# 检查是否已安装
node --version

# 应该显示 v16.x 或更高版本
```

**未安装？** 访问 https://nodejs.org/ 下载安装

### 2. Rust (必需)

```bash
# 检查是否已安装
rustc --version
cargo --version

# 应该显示最新稳定版本
```

**未安装？** 访问 https://www.rust-lang.org/tools/install 下载安装

#### Windows 用户
运行官方安装程序，它会自动安装 Rust 和 Microsoft C++ Build Tools

#### macOS 用户
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Linux 用户
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 3. Python (必需，用于核心功能)

```bash
# 检查是否已安装
python --version

# 应该显示 3.7 或更高版本
```

## 🚀 5分钟快速启动

### 步骤 1: 克隆或下载项目

```bash
cd gametools
cd tauri-app
```

### 步骤 2: 安装依赖

```bash
npm install
```

这会安装所有前端依赖，包括 Tauri CLI 和 Vite。

### 步骤 3: 安装 Python 依赖

```bash
cd ..
pip install -r core/requirements.txt
cd tauri-app
```

### 步骤 4: 启动开发模式

#### 方法 A: 使用命令行

```bash
npm run tauri:dev
```

#### 方法 B: 使用脚本

**Windows**:
```bash
.\启动开发模式.bat
```

**macOS/Linux**:
```bash
chmod +x 启动开发模式.sh
./启动开发模式.sh
```

### 步骤 5: 开始使用

应用会自动打开！现在你可以：
- 🔍 使用越南文检测功能
- 📊 检测 JSON 格式
- 📈 处理 Excel 数据
- 📄 提取翻译内容
- ...更多功能

## 🎯 常用命令

### 开发模式
```bash
npm run tauri:dev
```
- 自动热重载
- 打开开发者工具 (F12)
- 实时查看代码修改

### 构建生产版本
```bash
npm run tauri:build
```
- 生成优化后的可执行文件
- 位置: `src-tauri/target/release/`
- 包含安装包: `src-tauri/target/release/bundle/`

### 仅构建前端
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 📁 生成的文件位置

构建完成后：

```
src-tauri/target/release/
├── gametools.exe           # Windows 可执行文件
├── gametools               # macOS/Linux 可执行文件
└── bundle/
    ├── msi/               # Windows 安装包
    │   └── gametools_1.30.0_x64.msi
    ├── nsis/              # Windows 安装程序
    │   └── gametools_1.30.0_x64-setup.exe
    ├── dmg/               # macOS 磁盘镜像
    │   └── gametools_1.30.0_x64.dmg
    ├── deb/               # Debian/Ubuntu 包
    │   └── gametools_1.30.0_amd64.deb
    └── appimage/          # Linux 通用包
        └── gametools_1.30.0_amd64.AppImage
```

## 🛠️ 开发调试

### 打开开发者工具

开发模式下，按 **F12** 打开 Chrome DevTools，可以：
- 查看控制台日志
- 调试 JavaScript 代码
- 检查 HTML/CSS 元素
- 监控网络请求

### 查看 Rust 日志

Rust 后端的日志会输出到启动的终端窗口。

### 修改代码后

- **前端代码** (HTML/CSS/JS): 保存后自动刷新
- **Rust 代码**: 保存后自动重新编译并重启

## ⚙️ 自定义配置

### 修改窗口设置

编辑 `src-tauri/tauri.conf.json`:

```json
{
  "tauri": {
    "windows": [
      {
        "width": 1200,      // 窗口宽度
        "height": 900,      // 窗口高度
        "minWidth": 1000,   // 最小宽度
        "minHeight": 800,   // 最小高度
        "title": "GameTools - 游戏工具集"
      }
    ]
  }
}
```

### 修改应用信息

编辑 `src-tauri/tauri.conf.json`:

```json
{
  "package": {
    "productName": "GameTools",
    "version": "1.30.0"
  }
}
```

### 修改图标

替换 `src-tauri/icons/` 目录下的图标文件。

## 🎨 界面自定义

### 修改样式

编辑 `src/styles.css`，所有 CSS 变量定义在 `:root` 中：

```css
:root {
  --primary-color: #2563eb;    /* 主色调 */
  --bg-primary: #ffffff;        /* 背景色 */
  /* ... 更多变量 */
}
```

### 修改布局

编辑 `index.html` 调整页面结构。

### 修改交互逻辑

编辑 `src/main.js` 添加或修改功能。

## 🐛 故障排除

### 问题 1: Rust 编译失败

**症状**: 构建时报错 "cargo build failed"

**解决**:
```bash
# 更新 Rust
rustup update

# 清理缓存
cd src-tauri
cargo clean
```

### 问题 2: Node 模块错误

**症状**: npm install 失败或模块找不到

**解决**:
```bash
# 删除 node_modules 和锁文件
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 问题 3: Python 脚本执行失败

**症状**: 点击功能按钮没有反应

**解决**:
1. 检查 Python 是否在 PATH 中
2. 确认已安装所有依赖: `pip install -r ../core/requirements.txt`
3. 检查 Rust 代码中的路径是否正确

### 问题 4: WebView2 错误 (Windows)

**症状**: Windows 上应用无法启动

**解决**:
下载安装 WebView2 Runtime:
https://developer.microsoft.com/microsoft-edge/webview2/

### 问题 5: 权限错误

**症状**: 无法读写文件

**解决**:
检查 `src-tauri/tauri.conf.json` 中的权限配置:
```json
{
  "tauri": {
    "allowlist": {
      "fs": {
        "scope": ["**"]  // 允许访问所有文件
      }
    }
  }
}
```

## 📚 进阶学习

### Tauri 官方文档
https://tauri.app/v1/guides/

### Rust 学习资源
- Rust 程序设计语言: https://doc.rust-lang.org/book/
- Rust by Example: https://doc.rust-lang.org/rust-by-example/

### 前端技术
- HTML/CSS: https://developer.mozilla.org/
- JavaScript: https://javascript.info/
- Vite: https://vitejs.dev/

## 🎓 下一步

1. ✅ 熟悉基本操作
2. ✅ 尝试修改样式和布局
3. ✅ 理解 Tauri Commands 机制
4. ✅ 添加新功能
5. ✅ 构建并分发应用

## 💡 提示

- 开发时使用开发模式，响应快
- 正式发布前务必进行完整测试
- 定期备份重要数据
- 查看日志排查问题

## 🤝 获取帮助

遇到问题？
1. 查看本文档的故障排除部分
2. 阅读 [完整 README](README.md)
3. 查看 [Tauri vs Tkinter 对比](../docs/TAURI_VS_TKINTER.md)
4. 联系开发团队

---

**祝你使用愉快！** 🎉
