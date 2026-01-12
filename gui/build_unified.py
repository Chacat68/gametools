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
import argparse
from pathlib import Path
from datetime import datetime

# 添加父目录到路径以导入版本信息
sys.path.append(str(Path(__file__).parent.parent))
from version import get_version, get_build_date, get_author, get_description

# 最近一次成功生成到项目根目录 dist/ 的exe路径（用于打印准确产物名）
LAST_BUILT_EXE: Path | None = None


def run_command(command, description):
    """运行命令并处理错误（流式输出，避免长时间无响应与大输出缓存）"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*50)

    try:
        use_shell = isinstance(command, str)
        process = subprocess.Popen(
            command,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
        )

        assert process.stdout is not None
        for line in process.stdout:
            print(line, end='')

        return_code = process.wait()
        if return_code == 0:
            print("[OK] 成功!")
            return True

        print("[ERROR] 失败!")
        print(f"返回码: {return_code}")
        return False
    except FileNotFoundError as e:
        print("[ERROR] 命令不存在或不可执行!")
        print("错误:", e)
        return False
    except Exception as e:
        print("[ERROR] 执行异常!")
        print("错误:", e)
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
        if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], "安装PyInstaller"):
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


def _write_text_if_changed(file_path: Path, content: str) -> bool:
    """仅在内容变化时写入文件，避免无意义触发全量重打包。"""
    try:
        existing = file_path.read_text(encoding='utf-8') if file_path.exists() else None
    except Exception:
        existing = None

    if existing == content:
        return False

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding='utf-8')
    return True


def clean_build(clean_build_dir: bool, clean_dist_dir: bool, clean_pyc: bool):
    """清理构建目录。

    性能优化策略：默认仅清理 dist（输出），保留 build 缓存以支持 PyInstaller 增量构建。
    """
    print("\n清理构建目录...")

    if clean_dist_dir and os.path.exists('dist'):
        print("删除目录: dist")
        shutil.rmtree('dist')

    if clean_build_dir and os.path.exists('build'):
        print("删除目录: build")
        shutil.rmtree('build')

    if clean_pyc:
        if os.path.exists('__pycache__'):
            print("删除目录: __pycache__")
            shutil.rmtree('__pycache__')

        # 清理pyc文件（可选，较慢）
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass


def create_spec_file(console: bool = False, upx: bool = True):
    """创建/更新 PyInstaller 的 spec 配置文件。

    - 默认 console=False：打包为 GUI 程序（不弹命令行窗口）
    - 默认 upx=True：体积更小但会增加构建耗时；如追求速度可关闭
    """
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
    ['run_unified.py'],
    pathex=['.', '..'],
    binaries=[],
    datas=[
        ('../core', 'core'),
        ('../tools/json_error_detector', 'tools/json_error_detector'),
        ('../tools', 'tools'),
        ('../config.json', '.'),
        ('../config_export.json', '.'),
        ('../README.md', '.'),
    ],
    hiddenimports=[
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas.core',
        'pandas.core.arrays',
        'pandas.io',
        'pandas.io.formats',
        'pandas.io.excel',
        'pandas.io.excel._xlrd',
        'pandas.io.excel._openpyxl',
        'numpy',
        'numpy.__config__',
        'numpy._core',
        'numpy._core._multiarray_umath',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.core._dtype_ctypes',
        'numpy.core.multiarray',
        'numpy.lib',
        'numpy.random',
        'numpy.random.mtrand',
        'numpy.linalg',
        'numpy.linalg._umath_linalg',
        'numpy.fft',
        'numpy.fft._pocketfft_internal',
        'numpy._distributor_init',
        'numpy.compat',
        'numpy.testing',
        'xlwings',
        'xlwings.main',
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'gui.import_helper',
        'core',
        'core.cross_project_translator',
        'core.excel_field_extractor',
        'core.table_range_translator',
        'core.excel_sheet_splitter',
        'core.batch_excel_modifier',
        'core.excel_config_sync',
        'core.excel_to_csv_converter',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['pyi_rth_numpy_fix.py'],  # 修复 numpy 导入问题
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉不需要的二进制文件（但保留tkinter需要的tcl/tk和numpy必需的_multiarray_tests）
a.binaries = [x for x in a.binaries if not any(
    excl in x[0].lower() for excl in [
        'qt5', 'qt6', 'pyside', 'pyqt',
    ]
) or '_multiarray_tests' in x[0].lower()]

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
    strip=False,  # 关闭strip以保持debug信息用于故障排除
    upx=__UPX__,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=__CONSOLE__,  # GUI程序默认不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
'''

    # 使用占位符替换，避免 f-string 与 spec 内部 "{}" 冲突
    spec_content = (
        spec_content
        .replace('__UPX__', 'True' if upx else 'False')
        .replace('__CONSOLE__', 'True' if console else 'False')
    )

    spec_path = Path(__file__).resolve().parent / 'gametools_unified.spec'
    changed = _write_text_if_changed(spec_path, spec_content)
    if changed:
        print("[OK] 创建/更新spec文件成功")
    else:
        print("[OK] spec未变化，跳过重写")


def build_exe():
    """构建exe文件"""
    global LAST_BUILT_EXE
    LAST_BUILT_EXE = None
    print("\n开始构建exe文件...")

    script_dir = Path(__file__).resolve().parent
    # 确保dist目录存在（项目根目录的 dist/）
    dist_dir = script_dir.parent / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 使用spec文件构建（--noconfirm 避免交互；保留 build 缓存以增量构建）
    pyinstaller_cmd = [sys.executable, '-m', 'PyInstaller', '--noconfirm', 'gametools_unified.spec']
    if not run_command(pyinstaller_cmd, "构建exe文件"):
        return False
    
    # 检查构建结果
    exe_path = Path("dist/gametools.exe")
    if exe_path.exists():
        # 生成带版本号的文件名
        version = get_version()
        versioned_exe_name = f"gametools_v{version}.exe"
        target_exe = dist_dir / versioned_exe_name

        # 如果目标文件已存在，尝试删除；若被占用则换一个新名字避免失败
        if target_exe.exists():
            try:
                target_exe.unlink()
            except PermissionError:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                target_exe = dist_dir / f"gametools_v{version}_{timestamp}.exe"
            except Exception:
                # 其他异常也降级为生成新名字，避免整个打包流程失败
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                target_exe = dist_dir / f"gametools_v{version}_{timestamp}.exe"

        try:
            shutil.copy2(exe_path, target_exe)
            LAST_BUILT_EXE = target_exe
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
    script_dir = Path(__file__).resolve().parent
    portable_dir = script_dir.parent / "dist" / portable_dir_name
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
    parser = argparse.ArgumentParser(description="gametools 统一版本构建脚本")
    parser.add_argument('--clean', action='store_true', help='全量清理（删除 build 与 dist），最慢但最干净')
    parser.add_argument('--clean-pyc', action='store_true', help='额外清理 __pycache__/pyc（较慢）')
    parser.add_argument('--with-console', action='store_true', help='打包为控制台程序（用于排错，会弹出命令行窗口）')
    parser.add_argument('--no-upx', action='store_true', help='禁用UPX压缩以加快构建速度（体积会变大）')
    args = parser.parse_args()

    # 无论从哪里调用，都切到 gui/ 目录，避免相对路径导致打包到错误目录或漏打文件
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    print("gametools统一版本构建脚本")
    print(f"版本: v{get_version()}")
    print(f"构建日期: {get_build_date()}")
    print("="*50)
    
    # 检查当前目录
    if not os.path.exists("gametools_unified.py"):
        print("[ERROR] 未找到 gametools_unified.py（预期在 gui/ 目录）")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("[ERROR] 依赖检查失败")
        return False
    
    # 清理构建目录：默认不清理 build/dist，依赖 PyInstaller 覆盖输出并复用缓存以加速
    clean_build_dir = bool(args.clean)
    clean_dist_dir = bool(args.clean)
    clean_build(
        clean_build_dir=clean_build_dir,
        clean_dist_dir=clean_dist_dir,
        clean_pyc=bool(args.clean_pyc),
    )

    # 创建/更新spec文件（内容未变则跳过写入，减少无意义全量重打包）
    create_spec_file(console=bool(args.with_console), upx=not bool(args.no_upx))
    
    # 构建exe
    if not build_exe():
        print("[ERROR] 构建失败")
        return False
    
    print("\n" + "="*50)
    print("[SUCCESS] 构建完成!")
    print("="*50)
    version = get_version()
    print("生成的文件:")
    if LAST_BUILT_EXE is not None:
        print(f"- {LAST_BUILT_EXE} (主程序)")
    else:
        print(f"- dist/gametools_v{version}.exe (主程序)")
    print("\n使用方法:")
    if LAST_BUILT_EXE is not None:
        print(f"直接运行 {LAST_BUILT_EXE}")
    else:
        print(f"直接运行 dist/gametools_v{version}.exe")
    print("\n输出目录: dist/")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
