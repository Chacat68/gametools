#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化构建脚本
用于构建JSON格式检测工具的exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """运行命令并处理错误"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, encoding='utf-8')
        print("✅ 成功!")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败!")
        print("错误:", e.stderr)
        return False


def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    
    # 检查Python
    try:
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    except:
        print("❌ Python未安装或版本不正确")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        if not run_command("pip install pyinstaller", "安装PyInstaller"):
            return False
    
    return True


def clean_build():
    """清理构建目录"""
    print("\n清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except:
                    pass


def build_exe():
    """构建exe文件"""
    print("\n开始构建exe文件...")
    
    # 确保dist目录存在
    dist_dir = Path("../dist")
    dist_dir.mkdir(exist_ok=True)
    
    # 使用spec文件构建
    if not run_command("pyinstaller json_format_detector.spec", "构建exe文件"):
        return False
    
    # 检查构建结果
    exe_path = Path("dist/JSON格式检测工具.exe")
    if exe_path.exists():
        # 将exe文件复制到项目根目录的dist文件夹
        target_exe = dist_dir / "JSON格式检测工具.exe"
        shutil.copy2(exe_path, target_exe)
        
        print(f"\n✅ 构建成功!")
        print(f"exe文件位置: {target_exe.absolute()}")
        print(f"文件大小: {target_exe.stat().st_size / 1024 / 1024:.2f} MB")
        return True
    else:
        print("❌ 构建失败，未找到exe文件")
        return False


def create_portable_package():
    """创建便携版包"""
    print("\n创建便携版包...")
    
    exe_path = Path("dist/JSON格式检测工具.exe")
    if not exe_path.exists():
        print("❌ exe文件不存在，无法创建便携版")
        return False
    
    # 创建便携版目录（在项目根目录的dist文件夹中）
    portable_dir = Path("../dist/JSON格式检测工具_便携版")
    portable_dir.mkdir(exist_ok=True)
    
    # 复制exe文件
    shutil.copy2(exe_path, portable_dir / "JSON格式检测工具.exe")
    
    # 创建说明文件
    readme_content = """JSON格式检测工具 - 便携版

使用说明:
1. 双击 "JSON格式检测工具.exe" 启动程序
2. 点击"浏览"按钮选择要检测的JSON文件
3. 设置要检测的字段名（默认为"text"）
4. 点击"开始检测"进行格式检测
5. 查看检测结果，可以保存报告到文件

功能特点:
- 自动分析JSON文件中指定字段的格式模式
- 检测与通用格式不一致的内容
- 支持多种格式特征检测（长度、行数、空格、换行符等）
- 生成详细的检测报告
- 支持嵌套JSON结构

注意事项:
- 确保JSON文件格式正确
- 程序会自动检测字段中的格式不一致问题
- 检测结果可以保存为文本文件

版本信息:
- 构建时间: {build_time}
- Python版本: {python_version}
- PyInstaller版本: {pyinstaller_version}
""".format(
        build_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        pyinstaller_version=__import__('PyInstaller').__version__
    )
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 便携版包已创建: {portable_dir.absolute()}")
    return True


def main():
    """主函数"""
    print("JSON格式检测工具 - 自动化构建脚本")
    print("="*50)
    
    # 检查当前目录
    if not os.path.exists("json_format_detector_gui.py"):
        print("❌ 请在gui目录中运行此脚本")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        return False
    
    # 清理构建目录
    clean_build()
    
    # 构建exe
    if not build_exe():
        print("❌ 构建失败")
        return False
    
    # 创建便携版包
    create_portable_package()
    
    print("\n" + "="*50)
    print("🎉 构建完成!")
    print("="*50)
    print("生成的文件:")
    print("- ../dist/JSON格式检测工具.exe (主程序)")
    print("- ../dist/JSON格式检测工具_便携版/ (便携版包)")
    print("\n使用方法:")
    print("1. 直接运行 ../dist/JSON格式检测工具.exe")
    print("2. 或使用便携版包中的程序")
    print("\n输出目录: ../dist/")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
