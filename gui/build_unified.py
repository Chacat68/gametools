#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools统一版本构建脚本
用于构建包含两个功能模块的exe文件
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
        print("[OK] 成功!")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("[ERROR] 失败!")
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
        print("[ERROR] Python未安装或版本不正确")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller未安装，正在安装...")
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


def create_spec_file():
    """创建PyInstaller的spec配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gametools_unified.py'],
    pathex=['.', '..'],
    binaries=[],
    datas=[
        ('../core', 'core'),
        ('../tools/json_format_detector', 'tools/json_format_detector'),
        ('../tools', 'tools'),
        ('../docs', 'docs'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gametools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
    version_file=None,
)
'''
    
    with open('gametools_unified.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("[OK] 创建spec文件成功")


def build_exe():
    """构建exe文件"""
    print("\n开始构建exe文件...")
    
    # 确保dist目录存在
    dist_dir = Path("../dist")
    dist_dir.mkdir(exist_ok=True)
    
    # 使用spec文件构建
    if not run_command("pyinstaller gametools_unified.spec", "构建exe文件"):
        return False
    
    # 检查构建结果
    exe_path = Path("dist/gametools.exe")
    if exe_path.exists():
        # 将exe文件复制到项目根目录的dist文件夹
        target_exe = dist_dir / "gametools.exe"
        
        # 如果目标文件已存在，先删除
        if target_exe.exists():
            try:
                target_exe.unlink()
            except:
                pass
        
        try:
            shutil.copy2(exe_path, target_exe)
            print(f"\n[SUCCESS] 构建成功!")
            print(f"exe文件位置: {target_exe.absolute()}")
            print(f"文件大小: {target_exe.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        except Exception as e:
            print(f"[WARNING] 复制文件失败: {e}")
            print(f"[INFO] exe文件位置: {exe_path.absolute()}")
            return True
    else:
        print("[ERROR] 构建失败，未找到exe文件")
        return False


def create_portable_package():
    """创建便携版包"""
    print("\n创建便携版包...")
    
    exe_path = Path("dist/gametools.exe")
    if not exe_path.exists():
        print("[ERROR] exe文件不存在，无法创建便携版")
        return False
    
    # 创建便携版目录
    portable_dir = Path("../dist/gametools_便携版")
    portable_dir.mkdir(exist_ok=True)
    
    # 复制exe文件
    shutil.copy2(exe_path, portable_dir / "gametools.exe")
    
    # 创建说明文件
    readme_content = """gametools - 游戏工具集 便携版

使用说明:
1. 双击 "gametools.exe" 启动程序
2. 选择相应的功能页签：
   - 策划本地化工具：检测表格文件中的越南文
   - JSON格式检测工具：检测JSON文件格式一致性
3. 按照界面提示操作
4. 查看检测结果

功能特点:
- 策划本地化工具：支持Excel和CSV文件，检测越南文内容
- JSON格式检测工具：检测JSON文件中text字段的格式一致性
- 图形化界面，操作简单直观
- 多线程处理，界面响应流畅
- 支持保存检测报告

注意事项:
- 确保文件格式正确
- 大文件处理可能需要较长时间
- 建议在检测前备份重要文件

版本信息:
- 构建时间: {build_time}
- Python版本: {python_version}
- PyInstaller版本: {pyinstaller_version}

技术支持:
如有问题或建议，请联系开发团队。

版权所有 © 2024 gametools
""".format(
        build_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        pyinstaller_version=__import__('PyInstaller').__version__
    )
    
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[SUCCESS] 便携版包已创建: {portable_dir.absolute()}")
    return True


def main():
    """主函数"""
    print("gametools统一版本构建脚本")
    print("="*50)
    
    # 检查当前目录
    if not os.path.exists("gametools_unified.py"):
        print("[ERROR] 请在gui目录中运行此脚本")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("[ERROR] 依赖检查失败")
        return False
    
    # 清理构建目录
    clean_build()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建exe
    if not build_exe():
        print("[ERROR] 构建失败")
        return False
    
    # 创建便携版包
    create_portable_package()
    
    print("\n" + "="*50)
    print("[SUCCESS] 构建完成!")
    print("="*50)
    print("生成的文件:")
    print("- dist/gametools.exe (主程序)")
    print("- dist/gametools_便携版/ (便携版包)")
    print("\n使用方法:")
    print("1. 直接运行 dist/gametools.exe")
    print("2. 或使用便携版包中的程序")
    print("\n输出目录: dist/")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
