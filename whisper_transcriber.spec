# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

block_cipher = None

# GTK and GI related files
gi_typelibs_path = None
gtk_libs_path = None

# Try to find GTK installation paths
if sys.platform == 'win32':
    # Common GTK installation paths on Windows
    possible_paths = [
        r'C:\msys64\mingw64\lib\girepository-1.0',
        r'C:\gtk\lib\girepository-1.0',
        r'C:\Program Files\GTK3-Runtime Win64\lib\girepository-1.0'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            gi_typelibs_path = path
            break
    
    # GTK library paths
    gtk_possible_paths = [
        r'C:\msys64\mingw64\bin',
        r'C:\gtk\bin',
        r'C:\Program Files\GTK3-Runtime Win64\bin'
    ]
    
    for path in gtk_possible_paths:
        if os.path.exists(path):
            gtk_libs_path = path
            break

# Data files to include
datas = []

# Include GTK typelibs if found
if gi_typelibs_path:
    datas.append((gi_typelibs_path, 'gi_typelibs'))

# Include any additional data files your app needs
# datas.append(('data', 'data'))

# Binary files to include
binaries = []

# Include GTK libraries if found
if gtk_libs_path:
    gtk_dlls = [
        'libgtk-4-1.dll',
        'libgdk-4-1.dll',
        'libglib-2.0-0.dll',
        'libgobject-2.0-0.dll',
        'libgio-2.0-0.dll',
        'libcairo-2.dll',
        'libpango-1.0-0.dll',
        'libpangocairo-1.0-0.dll',
        'libgdk_pixbuf-2.0-0.dll',
        'libadwaita-1-0.dll'
    ]
    
    for dll in gtk_dlls:
        dll_path = os.path.join(gtk_libs_path, dll)
        if os.path.exists(dll_path):
            binaries.append((dll_path, '.'))

# Hidden imports for GTK and other dependencies
hiddenimports = [
    'gi',
    'gi.repository',
    'gi.repository.Gtk',
    'gi.repository.Gio',
    'gi.repository.GLib',
    'gi.repository.Adw',
    'gi.repository.GObject',
    'gi.repository.Gdk',
    'gi.repository.Pango',
    'gi.repository.GdkPixbuf',
    'whisper',
    'torch',
    'torchaudio',
    'numpy',
    'ffmpeg',
    'psutil',
    'tqdm',
    'numba',
    'pkg_resources.py2_warn'
]

a = Analysis(
    ['whisper_transcriber.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhisperTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperTranscriber',
)
