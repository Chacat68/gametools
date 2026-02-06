#!/bin/bash
# GameTools Linux 环境设置脚本
# 用于在Linux系统上安装所需的系统依赖和Python依赖

set -e  # 遇到错误立即退出

echo "============================================"
echo "GameTools Linux 环境设置"
echo "============================================"
echo ""

# 检测发行版
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "⚠️  无法检测Linux发行版"
    exit 1
fi

# 安装tkinter系统依赖
echo "📦 安装tkinter系统依赖..."
case $OS in
    ubuntu|debian)
        echo "检测到 Ubuntu/Debian 系统"
        sudo apt-get update
        sudo apt-get install -y python3-tk
        ;;
    fedora|rhel|centos)
        echo "检测到 Fedora/RHEL/CentOS 系统"
        sudo yum install -y python3-tkinter
        ;;
    arch|manjaro)
        echo "检测到 Arch Linux 系统"
        sudo pacman -S --noconfirm tk
        ;;
    *)
        echo "⚠️  不支持的Linux发行版: $OS"
        echo "请手动安装 python3-tk 包"
        exit 1
        ;;
esac

echo "✅ tkinter安装完成"
echo ""

# 安装Python依赖
echo "📦 安装Python依赖包..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "✅ Python依赖安装完成"
else
    echo "⚠️  未找到 requirements.txt 文件"
fi

echo ""
echo "============================================"
echo "✨ 环境设置完成！"
echo "============================================"
echo ""
echo "现在可以运行："
echo "  python gui/run_unified.py"
echo ""
echo "或运行测试："
echo "  python test/run_all_tests.py"
echo ""
