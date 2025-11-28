# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas_ttk, binaries_ttk, hiddenimports_ttk = collect_all('ttkbootstrap')
datas_heif, binaries_heif, hiddenimports_heif = collect_all('pillow_heif')

datas = datas_ttk + datas_heif
binaries = binaries_ttk + binaries_heif
hiddenimports = hiddenimports_ttk + hiddenimports_heif

a = Analysis(
    ['src\\run.py'],
    pathex=['src'],
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
    name='GeoSnap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
