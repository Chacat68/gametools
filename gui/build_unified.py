#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gametools统一版本构建脚本
用于构建包含两个功能模块的exe文件

性能优化特性:
- 增量构建：默认保留build缓存，仅重新编译变更部分
- 并行分析：启用多进程分析加速依赖解析
- 智能清理：按需清理，避免不必要的全量重建
- UPX压缩：可选压缩，平衡体积与构建速度
"""

import os
import sys
import subprocess
import shutil
import argparse
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

# 添加父目录到路径以导入版本信息
sys.path.append(str(Path(__file__).parent.parent))
from version import get_version, get_build_date, get_author, get_description, increment_version

# 最近一次成功生成到项目根目录 dist/ 的exe路径（用于打印准确产物名）
LAST_BUILT_EXE: Optional[Path] = None

# 构建缓存文件路径
BUILD_CACHE_FILE = Path(__file__).parent / ".build_cache.json"


def get_file_hash(filepath: Path) -> str:
    """计算文件的MD5哈希值用于增量构建检测"""
    if not filepath.exists():
        return ""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def get_source_files_hash() -> dict:
    """获取所有源文件的哈希值"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    source_patterns = [
        (script_dir, "*.py"),
        (project_root / "core", "*.py"),
        (project_root / "tools", "*.py"),
        (project_root, "*.json"),
        (project_root, "version.py"),
    ]
    
    hashes = {}
    for base_path, pattern in source_patterns:
        if base_path.exists():
            for filepath in base_path.glob(pattern):
                rel_path = str(filepath.relative_to(project_root))
                hashes[rel_path] = get_file_hash(filepath)
    
    return hashes


def load_build_cache() -> dict:
    """加载构建缓存"""
    if BUILD_CACHE_FILE.exists():
        try:
            with open(BUILD_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_build_cache(cache: dict):
    """保存构建缓存"""
    try:
        with open(BUILD_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def check_rebuild_needed() -> tuple[bool, list]:
    """检查是否需要重新构建，返回(是否需要, 变更文件列表)"""
    cache = load_build_cache()
    current_hashes = get_source_files_hash()
    cached_hashes = cache.get("file_hashes", {})
    
    changed_files = []
    for filepath, hash_val in current_hashes.items():
        if cached_hashes.get(filepath) != hash_val:
            changed_files.append(filepath)
    
    # 检查是否有文件被删除
    for filepath in cached_hashes:
        if filepath not in current_hashes:
            changed_files.append(f"[deleted] {filepath}")
    
    return len(changed_files) > 0, changed_files


def run_command(command, description, capture_output=False):
    """运行命令并处理错误（流式输出，避免长时间无响应与大输出缓存）"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print('='*50)

    start_time = time.time()
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

        output_lines = []
        assert process.stdout is not None
        for line in process.stdout:
            if capture_output:
                output_lines.append(line)
            print(line, end='')

        return_code = process.wait()
        elapsed = time.time() - start_time
        
        if return_code == 0:
            print(f"[OK] 成功! (耗时: {elapsed:.1f}秒)")
            return True if not capture_output else (True, output_lines)

        print("[ERROR] 失败!")
        print(f"返回码: {return_code}")
        return False if not capture_output else (False, output_lines)
    except FileNotFoundError as e:
        print("[ERROR] 命令不存在或不可执行!")
        print("错误:", e)
        return False if not capture_output else (False, [])
    except Exception as e:
        print("[ERROR] 执行异常!")
        print("错误:", e)
        return False if not capture_output else (False, [])


def check_dependencies(parallel: bool = True):
    """检查依赖是否安装
    
    Args:
        parallel: 是否并行检查依赖（加速检测）
    """
    print("检查依赖...")
    start_time = time.time()
    
    # 检查Python
    try:
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception:
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
    
    def check_import(pkg_info):
        """检查单个包是否可导入"""
        pkg_name, import_name = pkg_info
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            return (pkg_name, True, version)
        except Exception as e:
            return (pkg_name, False, str(e))
    
    # 并行或串行检查依赖
    missing = []
    if parallel:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(check_import, pkg): pkg for pkg in required_imports}
            for future in as_completed(futures):
                pkg_name, success, info = future.result()
                if success:
                    print(f"  ✓ {pkg_name}: v{info}")
                else:
                    missing.append(pkg_name)
    else:
        for pkg_info in required_imports:
            pkg_name, success, info = check_import(pkg_info)
            if success:
                print(f"  ✓ {pkg_name}: v{info}")
            else:
                missing.append(pkg_name)

    elapsed = time.time() - start_time
    print(f"依赖检查完成 (耗时: {elapsed:.2f}秒)")

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


def clean_build(clean_build_dir: bool, clean_dist_dir: bool, clean_pyc: bool, smart_clean: bool = True):
    """清理构建目录。

    性能优化策略：
    - 默认仅清理 dist（输出），保留 build 缓存以支持 PyInstaller 增量构建
    - smart_clean: 智能清理，只删除过期的缓存文件
    """
    print("\n清理构建目录...")
    start_time = time.time()

    if clean_dist_dir and os.path.exists('dist'):
        print("删除目录: dist")
        shutil.rmtree('dist')

    if clean_build_dir and os.path.exists('build'):
        if smart_clean:
            # 智能清理：只清理超过7天的缓存
            build_path = Path('build')
            old_files_count = 0
            cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7天前
            
            for item in build_path.rglob('*'):
                if item.is_file():
                    try:
                        if item.stat().st_mtime < cutoff_time:
                            item.unlink()
                            old_files_count += 1
                    except Exception:
                        pass
            
            if old_files_count > 0:
                print(f"智能清理: 删除了 {old_files_count} 个过期缓存文件")
        else:
            print("删除目录: build")
            shutil.rmtree('build')

    if clean_pyc:
        pyc_count = 0
        if os.path.exists('__pycache__'):
            print("删除目录: __pycache__")
            shutil.rmtree('__pycache__')

        # 并行清理pyc文件
        def remove_pyc(file_path):
            try:
                os.remove(file_path)
                return 1
            except Exception:
                return 0

        pyc_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    pyc_files.append(os.path.join(root, file))
        
        if pyc_files:
            with ThreadPoolExecutor(max_workers=8) as executor:
                results = list(executor.map(remove_pyc, pyc_files))
                pyc_count = sum(results)
            if pyc_count > 0:
                print(f"删除了 {pyc_count} 个pyc/pyo文件")
    
    elapsed = time.time() - start_time
    print(f"清理完成 (耗时: {elapsed:.2f}秒)")


def create_spec_file(console: bool = False, upx: bool = True, optimize: int = 2):
    """创建/更新 PyInstaller 的 spec 配置文件。

    - 默认 console=False：打包为 GUI 程序（不弹命令行窗口）
    - 默认 upx=True：体积更小但会增加构建耗时；如追求速度可关闭
    - optimize: Python优化级别 (0=无优化, 1=移除assert, 2=移除assert和docstring)
    """
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 配置文件
性能优化版本 - 最小化打包体积，加速启动
"""

block_cipher = None

# 排除不需要的大型库和模块以减小打包体积
excluded_modules = [
    # 测试相关
    'pytest', 'unittest', 'nose', 'mock', 'coverage',
    # 开发工具
    'IPython', 'jupyter', 'notebook', 'ipykernel', 'ipywidgets',
    'sphinx', 'docutils', 'jedi', 'parso', 'black', 'flake8', 'pylint',
    # 不需要的科学计算库
    'scipy', 'matplotlib', 'PIL', 'pillow', 'cv2', 'opencv',
    'sklearn', 'scikit-learn', 'tensorflow', 'torch', 'keras',
    'seaborn', 'plotly', 'bokeh', 'altair',
    # 网络相关（本项目不需要）
    'flask', 'django', 'tornado', 'aiohttp', 'fastapi', 'starlette',
    'urllib3', 'httpx', 'websocket', 'requests', 'httplib2',
    # 数据库相关
    'sqlalchemy', 'psycopg2', 'pymysql', 'sqlite3', 'redis', 'pymongo',
    # 其他不需要的
    'cryptography', 'bcrypt', 'passlib',
    'pygments', 'colorama', 'rich', 'click', 'typer',
    'setuptools', 'pkg_resources', 'pip', 'wheel', 'twine',
    'lib2to3', 'distutils', 'ensurepip',
    # PyQt/PySide (我们用tkinter)
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx', 'kivy',
    # 调试工具
    'pdb', 'pdbpp', 'ipdb', 'pudb',
    # 序列化（不需要的格式）
    'yaml', 'toml', 'msgpack', 'pickle5',
    # numpy 不需要的子模块
    'numpy.f2py', 'numpy.distutils', 'numpy.doc',
    # pandas 测试模块
    'pandas.tests',
    # email相关（不需要）
    'smtplib', 'imaplib',
]

# 只包含必需的 hiddenimports（减少分析时间）
minimal_hiddenimports = [
    # pandas 核心（让PyInstaller自动处理pandas的完整依赖）
    'pandas',
    # numpy 核心
    'numpy', 'numpy.core', 'numpy.core._multiarray_umath',
    'numpy.lib', 'numpy.random',
    # Excel处理
    'xlwings', 'xlwings.main',
    'openpyxl', 'openpyxl.workbook', 'openpyxl.worksheet',
    # tkinter GUI
    'tkinter', 'tkinter.ttk', 'tkinter.filedialog',
    'tkinter.messagebox', 'tkinter.scrolledtext',
    # 项目模块
    'gui.import_helper', 'core',
    'core.cross_project_translator', 'core.excel_field_extractor',
    'core.table_range_translator', 'core.excel_sheet_splitter',
    'core.batch_excel_modifier', 'core.excel_config_sync',
    'core.excel_to_csv_converter', 'core.cache_manager',
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
    ],
    hiddenimports=minimal_hiddenimports,
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=['pyi_rth_numpy_fix.py'],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 更激进的二进制文件过滤
a.binaries = [x for x in a.binaries if not any(
    excl in x[0].lower() for excl in [
        'qt5', 'qt6', 'pyside', 'pyqt',
        'matplotlib', 'scipy', 'cv2',
        'libssl', 'libcrypto',  # 不需要SSL
        'mklml', 'mkl_',  # Intel MKL（如果有OpenBLAS则不需要）
    ]
)]

# 更激进的数据文件过滤
a.datas = [x for x in a.datas if not any(
    excl in x[0].lower() for excl in [
        'tests', 'testing', 'test_',
        'examples', 'sample', 'demo',
        '__pycache__', '.pyc',
        'qt5', 'qt6',
        'matplotlib', 'mpl-data',
        'sphinx', 'doc', 'docs',
        'locale',  # 多语言包（如果不需要）
        '.git', '.svn',
        'readme', 'license', 'changelog',
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
    strip=__STRIP__,  # 移除调试符号以减小体积
    upx=__UPX__,
    upx_exclude=['vcruntime140.dll', 'python*.dll', 'ucrtbase.dll'],  # 排除不应压缩的DLL
    runtime_tmpdir=None,
    console=__CONSOLE__,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
    optimize=__OPTIMIZE__,  # Python字节码优化级别
)
'''

    # 使用占位符替换
    spec_content = (
        spec_content
        .replace('__UPX__', 'True' if upx else 'False')
        .replace('__CONSOLE__', 'True' if console else 'False')
        # Windows 默认禁用 strip：PyInstaller 需要外部 strip 工具，否则会在处理二进制时触发 WinError 2。
        # 非 Windows 环境默认开启以减小体积。
        .replace('__STRIP__', 'False' if os.name == 'nt' else 'True')
        .replace('__OPTIMIZE__', str(optimize))
    )

    spec_path = Path(__file__).resolve().parent / 'gametools_unified.spec'
    changed = _write_text_if_changed(spec_path, spec_content)
    if changed:
        print("[OK] 创建/更新spec文件成功")
    else:
        print("[OK] spec未变化，跳过重写")


def build_exe(skip_if_unchanged: bool = False, parallel_build: bool = True):
    """构建exe文件
    
    Args:
        skip_if_unchanged: 如果源文件未变化则跳过构建
        parallel_build: 是否使用并行构建（暂时保留供未来扩展）
    """
    global LAST_BUILT_EXE
    LAST_BUILT_EXE = None
    
    # 增量构建检测
    if skip_if_unchanged:
        rebuild_needed, changed_files = check_rebuild_needed()
        if not rebuild_needed:
            print("\n[SKIP] 源文件未变化，跳过构建")
            # 查找已有的exe
            version = get_version()
            script_dir = Path(__file__).resolve().parent
            dist_dir = script_dir.parent / "dist"
            existing_exe = dist_dir / f"gametools_v{version}.exe"
            if existing_exe.exists():
                LAST_BUILT_EXE = existing_exe
                print(f"已有exe文件: {existing_exe}")
                return True
            print("[INFO] 未找到已有exe，继续构建...")
        else:
            print(f"\n检测到 {len(changed_files)} 个文件变化:")
            for f in changed_files[:10]:  # 只显示前10个
                print(f"  - {f}")
            if len(changed_files) > 10:
                print(f"  ... 还有 {len(changed_files) - 10} 个文件")
    
    print("\n开始构建exe文件...")
    build_start_time = time.time()

    script_dir = Path(__file__).resolve().parent
    # 确保dist目录存在（项目根目录的 dist/）
    dist_dir = script_dir.parent / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 使用spec文件构建
    # --noconfirm 避免交互
    # 保留 build 缓存以增量构建
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--log-level=WARN',  # 减少日志输出加速构建
        'gametools_unified.spec'
    ]
    
    if not run_command(pyinstaller_cmd, "构建exe文件"):
        return False
    
    build_elapsed = time.time() - build_start_time
    print(f"\n构建耗时: {build_elapsed:.1f}秒")
    
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
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                target_exe = dist_dir / f"gametools_v{version}_{timestamp}.exe"

        try:
            shutil.copy2(exe_path, target_exe)
            LAST_BUILT_EXE = target_exe
            
            # 更新构建缓存
            cache = load_build_cache()
            cache["file_hashes"] = get_source_files_hash()
            cache["last_build_time"] = datetime.now().isoformat()
            cache["build_duration"] = build_elapsed
            save_build_cache(cache)
            
            file_size_mb = target_exe.stat().st_size / 1024 / 1024
            print(f"\n[SUCCESS] 构建成功!")
            print(f"exe文件位置: {target_exe.absolute()}")
            print(f"文件大小: {file_size_mb:.2f} MB")
            
            # 性能提示
            if file_size_mb > 100:
                print(f"[TIP] 文件较大，可考虑使用 --no-upx 加快构建速度")
            
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
    parser = argparse.ArgumentParser(
        description="gametools 统一版本构建脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
性能优化选项示例:
  快速构建（开发测试）:    python build_unified.py --fast
  完整构建（发布版本）:    python build_unified.py --clean
  增量构建（默认）:        python build_unified.py
  跳过未变化（CI/CD）:     python build_unified.py --skip-unchanged
        """
    )
    parser.add_argument('--clean', action='store_true', 
                       help='全量清理（删除 build 与 dist），最慢但最干净')
    parser.add_argument('--clean-pyc', action='store_true', 
                       help='额外清理 __pycache__/pyc（较慢）')
    parser.add_argument('--with-console', action='store_true', 
                       help='打包为控制台程序（用于排错，会弹出命令行窗口）')
    parser.add_argument('--no-upx', action='store_true', 
                       help='禁用UPX压缩以加快构建速度（体积会变大）')
    parser.add_argument('--fast', action='store_true',
                       help='快速构建模式：禁用UPX，减少优化，最快速度')
    parser.add_argument('--no-bump', action='store_true',
                       help='不自动递增版本号（用于排查打包问题/重复构建）')
    parser.add_argument('--skip-unchanged', action='store_true',
                       help='如果源文件未变化则跳过构建（适合CI/CD）')
    parser.add_argument('--optimize', type=int, choices=[0, 1, 2], default=2,
                       help='Python优化级别 (0=无, 1=移除assert, 2=移除assert+docstring，默认2)')
    args = parser.parse_args()

    # 无论从哪里调用，都切到 gui/ 目录，避免相对路径导致打包到错误目录或漏打文件
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    # 自动递增版本号（可通过 --no-bump 关闭，避免排错时污染版本）
    if args.no_bump:
        new_version = get_version()
        print("\n[版本更新] 已禁用自动递增版本号 (--no-bump)")
    else:
        print("\n[版本更新] 自动递增版本号...")
        new_version = increment_version("patch")

    total_start_time = time.time()
    
    print("=" * 60)
    print("gametools 统一版本构建脚本 (性能优化版)")
    print("=" * 60)
    print(f"版本: v{new_version}")
    print(f"构建日期: {get_build_date()}")
    print(f"构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 快速模式
    if args.fast:
        args.no_upx = True
        args.optimize = 0
        print("[MODE] 快速构建模式")
    
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("gametools_unified.py"):
        print("[ERROR] 未找到 gametools_unified.py（预期在 gui/ 目录）")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("[ERROR] 依赖检查失败")
        return False
    
    # 清理构建目录
    clean_build_dir = bool(args.clean)
    clean_dist_dir = bool(args.clean)
    clean_build(
        clean_build_dir=clean_build_dir,
        clean_dist_dir=clean_dist_dir,
        clean_pyc=bool(args.clean_pyc),
        smart_clean=not args.clean,  # 非全量清理时使用智能清理
    )

    # 创建/更新spec文件
    create_spec_file(
        console=bool(args.with_console), 
        upx=not bool(args.no_upx),
        optimize=args.optimize,
    )
    
    # 构建exe
    if not build_exe(skip_if_unchanged=args.skip_unchanged):
        print("[ERROR] 构建失败")
        return False
    
    total_elapsed = time.time() - total_start_time
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 构建完成!")
    print("=" * 60)
    print(f"总耗时: {total_elapsed:.1f}秒")
    
    version = get_version()
    print("\n生成的文件:")
    if LAST_BUILT_EXE is not None:
        file_size = LAST_BUILT_EXE.stat().st_size / 1024 / 1024
        print(f"- {LAST_BUILT_EXE} ({file_size:.1f} MB)")
    else:
        print(f"- dist/gametools_v{version}.exe (主程序)")
    
    print("\n使用方法:")
    if LAST_BUILT_EXE is not None:
        print(f"  直接运行 {LAST_BUILT_EXE}")
    else:
        print(f"  直接运行 dist/gametools_v{version}.exe")
    
    print("\n构建选项提示:")
    print("  --fast          快速构建（开发测试用）")
    print("  --skip-unchanged 增量构建（CI/CD推荐）")
    print("  --clean         全量清理构建（发布时使用）")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
