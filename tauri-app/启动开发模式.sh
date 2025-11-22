#!/bin/bash

echo "===================================="
echo "GameTools Tauri 版本 - 开发模式"
echo "===================================="
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查 Node.js
echo "[1/3] 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    echo "请访问 https://nodejs.org/ 下载安装"
    exit 1
fi
echo "✅ Node.js 已安装"

# 检查 Rust
echo ""
echo "[2/3] 检查 Rust..."
if ! command -v cargo &> /dev/null; then
    echo "❌ 错误: 未找到 Rust"
    echo "请访问 https://www.rust-lang.org/tools/install 下载安装"
    exit 1
fi
echo "✅ Rust 已安装"

# 检查依赖
echo ""
echo "[3/3] 检查依赖..."
if [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi
echo "✅ 依赖已就绪"

echo ""
echo "===================================="
echo "启动开发服务器..."
echo "===================================="
echo ""

npm run tauri:dev
