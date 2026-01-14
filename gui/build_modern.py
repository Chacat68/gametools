#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameTools 现代化版本打包脚本
用于构建现代化GUI的exe文件

基于 build_unified.py 优化，专门针对现代化界面
"""

import os
import sys
import subprocess
import shutil
import argparse
import time
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))
from version import get_version, get_build_date, get_author, get_description, increment_version


def create_spec_content(script_dir: Path, project_root: Path) -> str:
    """生成 PyInstaller spec 文件内容"""
    
    # 检查图标文件是否存在
    icon_path = project_root / "icon.ico"
    if icon_path.exists():
        icon_value = f"r'{icon_path}'"
    else:
        icon_value = "None"
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# GameTools Modern 打包配置文件
# 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# 收集必要的隐藏导入
hiddenimports = [
    # 核心模块
    'core',
    'core.batch_excel_modifier',
    'core.cache_manager',
    'core.config_manager',
    'core.constants',
    'core.cross_project_translator',
    'core.cross_project_translator_cached',
    'core.error_handler',
    'core.excel_config_sync',
    'core.excel_field_extractor',
    'core.excel_sheet_splitter',
    'core.excel_to_csv_converter',
    'core.log_manager',
    'core.output_formats',
    'core.progress_tracker',
    'core.result_filter',
    'core.table_range_translator',
    'core.task_controller',
    'core.text_patterns',
    
    # GUI 模块
    'gui',
    'gui.modern_theme',
    'gui.gametools_modern',
    'gui.import_helper',
    'gui.gui_utils',
    'gui.components',
    'gui.components.sidebar',
    'gui.components.widgets',
    'gui.pages',
    'gui.pages.base_page',
    'gui.pages.home_page',
    'gui.pages.about_page',
    'gui.pages.batch_modifier_page',
    'gui.pages.json_detector_page',
    'gui.pages.field_extractor_page',
    'gui.pages.csv_converter_page',
    'gui.pages.sheet_splitter_page',
    'gui.pages.config_sync_page',
    'gui.pages.cross_project_page',
    'gui.pages.table_range_page',
    'gui.pages.excel_processor_page',
    
    # 工具模块
    'tools',
    'tools.json_error_detector',
    'tools.json_error_detector.json_error_detector',
    'tools.excel_data_processor',
    
    # 第三方库
    'pandas',
    'openpyxl',
    'xlwings',
    'numpy',
    'numpy.core._multiarray_umath',
    'numpy.core._dtype_ctypes',
    
    # 版本信息
    'version',
]

a = Analysis(
    [r'{script_dir / "gametools_modern.py"}'],
    pathex=[r'{project_root}', r'{script_dir}'],
    binaries=[],
    datas=[
        # 配置文件
        (r'{project_root / "config.json"}', '.'),
        (r'{project_root / "config_export.json"}', '.'),
        # 版本文件
        (r'{project_root / "version.py"}', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[r'{script_dir}'],
    hooksconfig={{}},
    runtime_hooks=[r'{script_dir / "pyi_rth_numpy_fix.py"}'],
    excludes=[
        'matplotlib',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'docutils',
    ],
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
    name='gametools_v{get_version()}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_value},
)
'''
    return spec_content


def clean_build_artifacts(script_dir: Path, full_clean: bool = False):
    """清理构建产物"""
    print("[*] 清理构建产物...")
    
    dirs_to_clean = [
        script_dir / "dist",
    ]
    
    if full_clean:
        dirs_to_clean.extend([
            script_dir / "build",
            script_dir / "__pycache__",
        ])
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  删除: {dir_path}")
    
    # 删除临时 spec 文件
    spec_file = script_dir / "gametools_modern.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"  删除: {spec_file}")


def run_pyinstaller(spec_file: Path, verbose: bool = False):
    """运行 PyInstaller"""
    print("\n[*] 开始打包...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_file),
        "--noconfirm",
        "--clean",
    ]
    
    if not verbose:
        cmd.append("--log-level=WARN")
    
    env = os.environ.copy()
    env['PYTHONOPTIMIZE'] = '1'
    
    result = subprocess.run(cmd, env=env, cwd=str(spec_file.parent))
    return result.returncode == 0


def copy_to_project_dist(script_dir: Path, project_root: Path):
    """复制exe到项目根目录的dist文件夹"""
    src_dist = script_dir / "dist"
    dst_dist = project_root / "dist"
    
    # 创建目标目录
    dst_dist.mkdir(exist_ok=True)
    
    # 查找并复制exe
    for exe_file in src_dist.glob("*.exe"):
        dst_file = dst_dist / exe_file.name
        shutil.copy2(exe_file, dst_file)
        print(f"\n[OK] 已复制到: {dst_file}")
        return dst_file
    
    return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GameTools 现代化版本打包工具')
    parser.add_argument('--clean', action='store_true', help='完全清理后重新构建')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    parser.add_argument('--no-copy', action='store_true', help='不复制到项目dist目录')
    parser.add_argument('--no-bump', action='store_true', help='不自动递增版本号（用于排查打包问题/重复构建）')
    args = parser.parse_args()
    
    # 路径设置
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 自动递增版本号（可通过 --no-bump 关闭，避免排错时污染版本）
    if args.no_bump:
        new_version = get_version()
        print("\n[版本更新] 已禁用自动递增版本号 (--no-bump)")
    else:
        print("\n[版本更新] 自动递增版本号...")
        new_version = increment_version("patch")
    
    print("=" * 60)
    print(f"[GameTools] 现代化版本打包工具")
    print(f"   版本: v{new_version}")
    print(f"   构建日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    start_time = time.time()
    
    # 清理
    if args.clean:
        clean_build_artifacts(script_dir, full_clean=True)
    else:
        clean_build_artifacts(script_dir, full_clean=False)
    
    # 生成 spec 文件
    print("\n[*] 生成打包配置...")
    spec_content = create_spec_content(script_dir, project_root)
    spec_file = script_dir / "gametools_modern.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print(f"  已生成: {spec_file}")
    
    # 运行 PyInstaller
    success = run_pyinstaller(spec_file, verbose=args.verbose)
    
    if success:
        elapsed = time.time() - start_time
        print(f"\n[SUCCESS] 打包成功！耗时: {elapsed:.1f}秒")
        
        # 复制到项目目录
        if not args.no_copy:
            exe_path = copy_to_project_dist(script_dir, project_root)
            if exe_path:
                print(f"\n[OUTPUT] 最终产物: {exe_path}")
                print(f"   文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("\n[FAILED] 打包失败！请检查错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()
