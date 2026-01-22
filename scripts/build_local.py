#!/usr/bin/env python3
"""
Local build script for Phone Agent.

This script provides a convenient way to build the executable locally

Usage:
    python scripts/build_local.py [--platform PLATFORM] [--clean]
    
Examples:
    python scripts/build_local.py                    # Build for current platform
    python scripts/build_local.py --clean            # Clean build
    python scripts/build_local.py --use-spec         # Use spec file
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_platform_info():
    """Get current platform information."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Normalize architecture names
    if machine in ('x86_64', 'amd64'):
        arch = 'x64'
    elif machine in ('arm64', 'aarch64'):
        arch = 'arm64'
    else:
        arch = machine
    
    # Normalize OS names
    if system == 'darwin':
        os_name = 'macos'
    else:
        os_name = system
    
    return os_name, arch


def get_pyinstaller_path(venv_path: Path):
    """Get the path to pyinstaller executable in the virtual environment."""
    if platform.system() == 'Windows':
        return venv_path / 'Scripts' / 'pyinstaller.exe'
    else:
        return venv_path / 'bin' / 'pyinstaller'


def install_dependencies(project_root: Path):
    """Install project dependencies."""
    print("📦 Installing project dependencies...")
    
    venv_path = project_root / '.venv'
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            check=True
        )
    
    # Determine pip path
    if platform.system() == 'Windows':
        pip_path = venv_path / 'Scripts' / 'pip'
    else:
        pip_path = venv_path / 'bin' / 'pip'
    
    # Install requirements
    subprocess.run(
        [str(pip_path), 'install', '-r', 'requirements.txt'],
        cwd=project_root,
        check=True
    )
    
    # Install project in editable mode
    subprocess.run(
        [str(pip_path), 'install', '-e', '.'],
        cwd=project_root,
        check=True
    )
    
    # Install PyInstaller in the virtual environment
    print("📦 Installing PyInstaller in virtual environment...")
    subprocess.run(
        [str(pip_path), 'install', 'pyinstaller'],
        cwd=project_root,
        check=True
    )
    
    print("✅ Dependencies installed successfully")
    return venv_path


def build_executable(project_root: Path, venv_path: Path, use_spec: bool = False):
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    os_name, arch = get_platform_info()
    artifact_name = f"phone-agent-{os_name}-{arch}"
    
    # Get pyinstaller path from virtual environment
    pyinstaller_path = get_pyinstaller_path(venv_path)
    
    if not pyinstaller_path.exists():
        print(f"❌ PyInstaller not found at {pyinstaller_path}")
        return None
    
    if use_spec and (project_root / 'phone-agent.spec').exists():
        # Use spec file
        cmd = [
            str(pyinstaller_path),
            '--clean',
            '--noconfirm',
            str(project_root / 'phone-agent.spec')
        ]
    else:
        # Build with command line options
        cmd = [
            str(pyinstaller_path),
            '--name=phone-agent',
            '--onefile',
            '--clean',
            '--noconfirm',
            f'--add-data=phone_agent{os.pathsep}phone_agent',
            f'--add-data=resources{os.pathsep}resources',
            '--hidden-import=phone_agent',
            '--hidden-import=phone_agent.agent',
            '--hidden-import=phone_agent.model',
            '--hidden-import=phone_agent.model.client',
            '--hidden-import=phone_agent.adb',
            '--hidden-import=phone_agent.adb.connection',
            '--hidden-import=phone_agent.adb.device',
            '--hidden-import=phone_agent.adb.input',
            '--hidden-import=phone_agent.adb.screenshot',
            '--hidden-import=phone_agent.actions',
            '--hidden-import=phone_agent.actions.handler',
            '--hidden-import=phone_agent.config',
            '--hidden-import=phone_agent.config.apps',
            '--hidden-import=phone_agent.config.i18n',
            '--hidden-import=phone_agent.config.prompts',
            '--hidden-import=phone_agent.config.prompts_en',
            '--hidden-import=phone_agent.config.prompts_zh',
            '--hidden-import=PIL',
            '--hidden-import=openai',
            '--collect-all=phone_agent',
            'main.py'
        ]
    
    # Set PYTHONPATH to include venv site-packages
    env = os.environ.copy()
    if platform.system() == 'Windows':
        site_packages = venv_path / 'Lib' / 'site-packages'
    else:
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = venv_path / 'lib' / python_version / 'site-packages'
    
    env['PYTHONPATH'] = str(site_packages)
    
    subprocess.run(cmd, cwd=project_root, env=env, check=True)
    
    # Verify build
    dist_path = project_root / 'dist'
    if platform.system() == 'Windows':
        executable = dist_path / 'phone-agent.exe'
    else:
        executable = dist_path / 'phone-agent'
    
    if executable.exists():
        print(f"✅ Build successful: {executable}")
        
        # Rename to include platform/arch info
        new_name = artifact_name + ('.exe' if platform.system() == 'Windows' else '')
        new_path = dist_path / new_name
        shutil.copy(executable, new_path)
        print(f"📦 Artifact: {new_path}")
        
        return new_path
    else:
        print("❌ Build failed: executable not found")
        return None


def clean_build(project_root: Path):
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")
    
    # Clean pycache in subdirectories
    for pycache in project_root.rglob('__pycache__'):
        shutil.rmtree(pycache)
    
    print("✅ Clean complete")


def main():
    parser = argparse.ArgumentParser(
        description='Build Phone Agent executable locally'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts before building'
    )
    parser.add_argument(
        '--use-spec',
        action='store_true',
        help='Use the spec file for building'
    )
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='Only clean, do not build'
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent.absolute()
    os.chdir(project_root)
    
    print(f"📁 Project root: {project_root}")
    
    os_name, arch = get_platform_info()
    print(f"🖥️  Platform: {os_name} ({arch})")
    
    # Clean if requested
    if args.clean or args.clean_only:
        clean_build(project_root)
        if args.clean_only:
            return
    
    # Install dependencies (including PyInstaller)
    venv_path = install_dependencies(project_root)
    
    # Build
    result = build_executable(project_root, venv_path, args.use_spec)
    
    if result:
        print("\n" + "=" * 50)
        print("🎉 Build completed successfully!")
        print(f"📦 Executable: {result}")
        print("=" * 50)
    else:
        print("\n❌ Build failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
