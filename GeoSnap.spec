# -*- mode: python ; coding: utf-8 -*-
"""
GeoSnap PyInstaller Spec File
Improved for maximum portability across Windows systems.
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = []
binaries = []
hiddenimports = []

# ==============================================================================
# COLLECT ALL DEPENDENCIES WITH NATIVE COMPONENTS
# ==============================================================================

# ttkbootstrap - UI framework with themes and assets
tmp_ret = collect_all('ttkbootstrap')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# pillow_heif - HEIC/HEIF image support (includes libheif DLLs)
tmp_ret = collect_all('pillow_heif')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# python-docx - Word document generation
tmp_ret = collect_all('docx')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# tkinterdnd2 - Drag and drop support (includes platform-specific DLLs)
try:
    tmp_ret = collect_all('tkinterdnd2')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except Exception:
    pass  # Optional dependency

# geomag - Magnetic declination data files
try:
    tmp_ret = collect_all('geomag')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except Exception:
    pass  # Optional dependency

# openpyxl - Excel file support
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# simplekml - KML/KMZ file generation
tmp_ret = collect_all('simplekml')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# ==============================================================================
# EXPLICIT HIDDEN IMPORTS
# These are modules that PyInstaller may not detect automatically
# ==============================================================================
hiddenimports += [
    # Pillow internals
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ExifTags',
    'PIL.TiffTags',
    'PIL.JpegImagePlugin',
    'PIL.PngImagePlugin',
    'PIL.HeifImagePlugin',
    
    # Tkinter components
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # openpyxl internals
    'openpyxl.cell._writer',
    'openpyxl.workbook.child',
    
    # simplekml internals
    'simplekml',
    'simplekml.kml',
    'simplekml.featgeom',
    'simplekml.coordinates',
    'simplekml.base',
    
    # Standard library that might be missed
    'json',
    'logging',
    'threading',
    'pathlib',
    'zipfile',
    'datetime',
    'concurrent.futures',
]

# ==============================================================================
# ANALYSIS
# ==============================================================================
a = Analysis(
    ['geosnap_app.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused large libraries to reduce size
        'matplotlib',
        'numpy', 
        'scipy',
        'pandas',
        'IPython',
        'notebook',
        'pytest',
    ],
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
