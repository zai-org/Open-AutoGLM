# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('phone_agent', 'phone_agent'), ('resources', 'resources')]
binaries = []
hiddenimports = ['phone_agent', 'phone_agent.agent', 'phone_agent.model', 'phone_agent.model.client', 'phone_agent.adb', 'phone_agent.adb.connection', 'phone_agent.adb.device', 'phone_agent.adb.input', 'phone_agent.adb.screenshot', 'phone_agent.actions', 'phone_agent.actions.handler', 'phone_agent.config', 'phone_agent.config.apps', 'phone_agent.config.i18n', 'phone_agent.config.prompts', 'phone_agent.config.prompts_en', 'phone_agent.config.prompts_zh', 'PIL', 'openai']
tmp_ret = collect_all('phone_agent')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='phone-agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
