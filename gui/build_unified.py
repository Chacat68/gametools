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

# 添加父目录到路径以导入版本信息
sys.path.append(str(Path(__file__).parent.parent))
from version import get_version, get_build_date, get_author, get_description


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
        if not run_command(f'"{sys.executable}" -m pip install pyinstaller', "安装PyInstaller"):
            return False

    # 关键依赖（打包时必须在同一Python环境中可导入）
    required_imports = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("xlwings", "xlwings"),
        ("openpyxl", "openpyxl"),
    ]
    missing = []
    for pkg_name, import_name in required_imports:
        try:
            __import__(import_name)
        except Exception:
            missing.append(pkg_name)

    if missing:
        print(f"[ERROR] 缺少或无法导入依赖: {', '.join(missing)}")
        print("[SUGGESTION] 请在当前Python环境中安装依赖后重试:")
        print(f"  {sys.executable} -m pip install -r requirements.txt")
        print("  或者:")
        print(f"  {sys.executable} -m pip install pandas numpy xlwings openpyxl")
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

# 排除不需要的大型库和模块以减小打包体积
excluded_modules = [
    # 测试相关
    'pytest', 'unittest',
    # 开发工具
    'IPython', 'jupyter', 'notebook', 'ipykernel', 'ipywidgets',
    'sphinx', 'docutils', 'jedi', 'parso',
    # 不需要的科学计算库
    'scipy', 'matplotlib', 'PIL', 'cv2', 'sklearn', 'tensorflow', 'torch',
    # 网络相关（本项目不需要）
    'flask', 'django', 'tornado', 'aiohttp',
    'urllib3', 'httpx', 'websocket',
    # 数据库相关
    'sqlalchemy', 'psycopg2', 'pymysql',
    # 其他不需要的
    'cryptography',
    'pygments', 'colorama',
    'setuptools', 'pkg_resources', 'pip',
    'lib2to3',
    # PyQt/PySide (我们用tkinter)
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx',
]

a = Analysis(
    ['gametools_unified.py'],
    pathex=['.', '..'],
    binaries=[],
    datas=[
        ('../core', 'core'),
        ('../tools/json_error_detector', 'tools/json_error_detector'),
        ('../tools', 'tools'),
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'xlwings',
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
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉不需要的二进制文件（但保留tkinter需要的tcl/tk）
a.binaries = [x for x in a.binaries if not any(
    excl in x[0].lower() for excl in [
        'qt5', 'qt6', 'pyside', 'pyqt',
        '_test', 'test_',
    ]
)]

# 过滤掉不需要的数据文件（但保留tcl/tk数据）
a.datas = [x for x in a.datas if not any(
    excl in x[0].lower() for excl in [
        'tests', 'testing',
        'examples', 'sample',
        '__pycache__',
        'qt5', 'qt6',
    ]
)]

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
    strip=True,  # 启用strip减小体积
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
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
    if not run_command(f'"{sys.executable}" -m PyInstaller gametools_unified.spec', "构建exe文件"):
        return False
    
    # 检查构建结果
    exe_path = Path("dist/gametools.exe")
    if exe_path.exists():
        # 生成带版本号的文件名
        version = get_version()
        versioned_exe_name = f"gametools_v{version}.exe"
        target_exe = dist_dir / versioned_exe_name
        
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
    
    # 生成带版本号的便携版目录名
    version = get_version()
    portable_dir_name = f"gametools_v{version}_便携版"
    portable_dir = Path(f"../dist/{portable_dir_name}")
    portable_dir.mkdir(exist_ok=True)
    
    # 复制exe文件
    shutil.copy2(exe_path, portable_dir / "gametools.exe")
    
    # 创建说明文件
    readme_content = f"""gametools - 游戏工具集 便携版

{get_description()}

版本信息:
- 版本号: v{get_version()}
- 构建日期: {get_build_date()}
- 作者: {get_author()}
- 构建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
- PyInstaller版本: {__import__('PyInstaller').__version__}

   使用说明:
   1. 双击 "gametools.exe" 启动程序
   2. 选择相应的功能页签：
      - 越南文检测导出：检测表格文件中的越南文并导出结果
      - JSON错误检测工具：检测JSON文件中的语法错误、结构错误、编码错误
      - Excel数据处理工具：根据A列内容对Excel数据进行分组和处理
      - 翻译提取：检测目录中的Excel文件并提取文本内容
      - 多语言翻译提取：基于JSON配置提取Excel指定字段的翻译内容
   3. 按照界面提示操作
   4. 查看检测结果

   功能特点:
   - 越南文检测导出：支持Excel和CSV文件，检测越南文内容并导出详细结果
   - JSON错误检测工具：检测JSON文件中的语法错误、结构错误、编码错误
   - Excel数据处理工具：智能分组Excel数据，支持多文件输出
   - 翻译提取：批量提取Excel文件中的文本内容，智能文本识别
   - 多语言翻译提取：智能字段过滤（前端/后端/前后端），多语言支持（中文/越南文/泰文），Excel位置精确定位
   - 图形化界面，操作简单直观
   - 多线程处理，界面响应流畅
   - 支持保存检测报告

注意事项:
- 确保文件格式正确
- 大文件处理可能需要较长时间
- 建议在检测前备份重要文件

技术支持:
如有问题或建议，请联系开发团队。

版权所有 © 2024 gametools
"""
    
    # 创建说明文件
    with open(portable_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[SUCCESS] 便携版包已创建:")
    print(f"  便携版位置: {portable_dir.absolute()}")
    return True


def main():
    """主函数"""
    print("gametools统一版本构建脚本")
    print(f"版本: v{get_version()}")
    print(f"构建日期: {get_build_date()}")
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
    
    print("\n" + "="*50)
    print("[SUCCESS] 构建完成!")
    print("="*50)
    print("生成的文件:")
    version = get_version()
    print(f"- dist/gametools_v{version}.exe (主程序)")
    print("\n使用方法:")
    print(f"直接运行 dist/gametools_v{version}.exe")
    print("\n输出目录: dist/")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
