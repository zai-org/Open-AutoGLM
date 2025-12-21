# -*- coding: utf-8 -*-
"""
AI Phone PC Build Script
一键构建 Windows 可执行程序

版本规范：
- 主版本号(Major): 重大功能变更或不兼容更新
- 次版本号(Minor): 新增功能，向下兼容
- 修订号(Patch): Bug修复，小改动
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

# 版本配置
VERSION = "1.0.0"
APP_NAME = "AI_Phone PC"

# 路径配置
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
PC_APP_DIR = ROOT_DIR / "pc-app"
FRONTEND_DIR = PC_APP_DIR / "frontend"
BACKEND_DIR = PC_APP_DIR / "backend"
EXE_APP_DIR = ROOT_DIR / "exe-app"
OUTPUT_DIR = EXE_APP_DIR / "output"
SPEC_FILE = EXE_APP_DIR / "autoglm.spec"


def run_command(cmd, cwd=None, check=True):
    """运行命令并打印输出"""
    print(f"\n🔧 执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print("-" * 50)
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"❌ 命令失败，退出码: {result.returncode}")
        sys.exit(1)
    return result


def clean_output():
    """清理输出目录"""
    print("\n🧹 清理旧的构建文件...")

    dirs_to_clean = [
        EXE_APP_DIR / "pyinstaller_build",
        EXE_APP_DIR / "pyinstaller_dist",
        OUTPUT_DIR,
    ]

    for d in dirs_to_clean:
        if d.exists():
            shutil.rmtree(d)
            print(f"   已删除: {d}")


def build_frontend():
    """构建前端"""
    print("\n📦 构建前端...")

    # 检查 node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        print("   安装依赖...")
        run_command("npm install", cwd=FRONTEND_DIR)

    # 构建
    run_command("npm run build", cwd=FRONTEND_DIR)

    dist_dir = FRONTEND_DIR / "dist"
    if not dist_dir.exists():
        print("❌ 前端构建失败，dist 目录不存在")
        sys.exit(1)

    print(f"✅ 前端构建完成: {dist_dir}")


def copy_backend_files():
    """复制后端文件到 exe-app 目录"""
    print("\n📋 复制后端文件...")

    # 复制 web_server.py
    src = BACKEND_DIR / "web_server.py"
    dst = EXE_APP_DIR / "web_server.py"
    shutil.copy2(src, dst)
    print(f"   复制: {src.name}")

    # 复制 ADBKeyboard.apk
    apk_src = BACKEND_DIR / "ADBKeyboard.apk"
    if apk_src.exists():
        shutil.copy2(apk_src, EXE_APP_DIR / "ADBKeyboard.apk")
        print(f"   复制: {apk_src.name}")


def build_executable():
    """使用 PyInstaller 构建可执行文件"""
    print("\n🔨 构建可执行文件...")

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 运行 PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        f'--workpath={EXE_APP_DIR / "pyinstaller_build"}',
        f"--distpath={OUTPUT_DIR}",
        str(SPEC_FILE),
    ]

    run_command(cmd, cwd=ROOT_DIR)

    # PyInstaller 生成的原始文件名
    old_exe_path = OUTPUT_DIR / "AutoGLM.exe"
    # 新文件名
    exe_name = f"{APP_NAME} v{VERSION}.exe"
    new_exe_path = OUTPUT_DIR / exe_name

    if old_exe_path.exists():
        # 重命名为新格式
        shutil.move(old_exe_path, new_exe_path)
        print(f"✅ 可执行文件构建完成: {new_exe_path}")
        print(f"   文件大小: {new_exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("❌ 构建失败，exe 文件不存在")
        sys.exit(1)

    return new_exe_path


def create_portable_package(exe_path):
    """创建便携版 ZIP 包"""
    print("\n📦 创建便携版压缩包...")

    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f"{APP_NAME}-Portable-v{VERSION}-{timestamp}.zip"
    zip_path = OUTPUT_DIR / zip_name

    exe_name = f"{APP_NAME} v{VERSION}.exe"

    # 需要打包的文件
    files_to_pack = [
        (exe_path, exe_name),
        (EXE_APP_DIR / "README.md", "README.md"),
    ]

    # 打包 ADBKeyboard.apk
    apk_file = EXE_APP_DIR / "ADBKeyboard.apk"
    if apk_file.exists():
        files_to_pack.append((apk_file, "ADBKeyboard.apk"))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arc_name in files_to_pack:
            if src.exists():
                zf.write(src, arc_name)
                print(f"   添加: {arc_name}")

    print(f"✅ 便携版创建完成: {zip_path}")
    print(f"   文件大小: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    return zip_path


def print_summary():
    """打印构建摘要"""
    print("\n" + "=" * 60)
    print("🎉 构建完成!")
    print("=" * 60)
    print(f"\n版本: v{VERSION}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("\n生成的文件:")

    for f in OUTPUT_DIR.iterdir():
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  • {f.name} ({size_mb:.1f} MB)")

    print("\n使用说明:")
    print(f"  1. 解压 {APP_NAME}-Portable-*.zip 到任意目录")
    print(f"  2. 双击 {APP_NAME} v{VERSION}.exe 运行")
    print("  3. 在设置中配置 API Key")
    print()


def main():
    """主构建流程"""
    print("=" * 60)
    print(f"🚀 {APP_NAME} Windows 应用构建脚本")
    print(f"   版本: v{VERSION}")
    print("=" * 60)

    # 检查 PyInstaller
    try:
        import PyInstaller

        print(f"✅ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 请先安装 PyInstaller: pip install pyinstaller")
        sys.exit(1)

    # 检查 Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js 版本: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ 请先安装 Node.js")
        sys.exit(1)

    # 执行构建步骤
    clean_output()
    build_frontend()
    copy_backend_files()
    exe_path = build_executable()
    create_portable_package(exe_path)
    print_summary()


if __name__ == "__main__":
    main()
