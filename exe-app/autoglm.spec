# -*- mode: python ; coding: utf-8 -*-
"""
AutoGLM PyInstaller Spec File
打包配置，将前后端整合为单个可执行文件
"""

import os
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(os.path.abspath(SPECPATH)).parent
PC_APP_DIR = ROOT_DIR / 'pc-app'
BACKEND_DIR = PC_APP_DIR / 'backend'
FRONTEND_DIST = PC_APP_DIR / 'frontend' / 'dist'
PHONE_AGENT_DIR = ROOT_DIR / 'phone_agent'
EXE_APP_DIR = ROOT_DIR / 'exe-app'

# 收集所有数据文件
datas = [
    # 前端构建产物
    (str(FRONTEND_DIST), 'static'),
    # ADB Keyboard APK
    (str(BACKEND_DIR / 'ADBKeyboard.apk'), '.'),
    # phone_agent 配置文件
    (str(PHONE_AGENT_DIR / 'config'), 'phone_agent/config'),
]

# 收集隐式导入的模块
hiddenimports = [
    'flask',
    'flask_cors',
    'dotenv',
    'PIL',
    'PIL.Image',
    'openai',
    'requests',
    'phone_agent',
    'phone_agent.agent',
    'phone_agent.model',
    'phone_agent.model.client',
    'phone_agent.adb',
    'phone_agent.adb.connection',
    'phone_agent.adb.device',
    'phone_agent.adb.input',
    'phone_agent.adb.screenshot',
    'phone_agent.hdc',
    'phone_agent.hdc.connection',
    'phone_agent.hdc.device',
    'phone_agent.hdc.input',
    'phone_agent.hdc.screenshot',
    'phone_agent.actions',
    'phone_agent.actions.handler',
    'phone_agent.config',
    'phone_agent.config.apps',
    'phone_agent.config.apps_harmonyos',
    'phone_agent.config.i18n',
    'phone_agent.config.prompts_en',
    'phone_agent.config.prompts_zh',
    'phone_agent.config.timing',
    'phone_agent.device_factory',
]

# 排除不需要的模块以减小体积
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

a = Analysis(
    [str(EXE_APP_DIR / 'launcher.py')],
    pathex=[
        str(ROOT_DIR),
        str(BACKEND_DIR),
    ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoGLM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保留控制台窗口显示日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(EXE_APP_DIR / 'assets' / 'icon.ico') if (EXE_APP_DIR / 'assets' / 'icon.ico').exists() else None,
)
