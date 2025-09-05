# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add the project directory to Python path
try:
    project_dir = Path(__file__).parent
except NameError:
    # When executed by some runners, __file__ may be undefined
    project_dir = Path.cwd()
sys.path.insert(0, str(project_dir))

block_cipher = None

# GTK and GI related files
gi_typelibs_path = None
gtk_libs_path = None

# Try to find GTK installation paths
if sys.platform == 'win32':
    # Prefer explicit environment configuration if provided
    env_gi = os.environ.get('GI_TYPELIB_PATH')
    if env_gi and os.path.exists(env_gi):
        gi_typelibs_path = env_gi
    # Common GTK installation paths on Windows (MSYS2, GVSBuild, custom)
    possible_paths = [
        gi_typelibs_path,
        r'C:\msys64\mingw64\lib\girepository-1.0',
        r'C:\gtk\lib\girepository-1.0',
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            gi_typelibs_path = path
            break

    # GTK runtime bin path
    env_gtk_root = os.environ.get('GTK_RUNTIME_DIR') or os.environ.get('GVSBUILD_ROOT')
    if env_gtk_root:
        candidate = os.path.join(env_gtk_root, 'bin')
        if os.path.exists(candidate):
            gtk_libs_path = candidate
    if not gtk_libs_path:
        gtk_possible_paths = [
            r'C:\msys64\mingw64\bin',
            r'C:\gtk\bin'
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
    # Support both MSYS2-style (libgtk-4-1.dll) and GVSBuild-style (gtk-4-1.dll) names
    gtk_dlls = [
        ('libgtk-4-1.dll', 'gtk-4-1.dll'),
        ('libgdk-4-1.dll', 'gdk-4-1.dll'),
        ('libglib-2.0-0.dll', 'glib-2.0-0.dll'),
        ('libgobject-2.0-0.dll', 'gobject-2.0-0.dll'),
        ('libgio-2.0-0.dll', 'gio-2.0-0.dll'),
        ('libcairo-2.dll', 'cairo-2.dll'),
        ('libpango-1.0-0.dll', 'pango-1.0-0.dll'),
        ('libpangocairo-1.0-0.dll', 'pangocairo-1.0-0.dll'),
        ('libgdk_pixbuf-2.0-0.dll', 'gdk_pixbuf-2.0-0.dll'),
        ('libadwaita-1-0.dll', 'adwaita-1-0.dll')
    ]

    for pair in gtk_dlls:
        for dll in pair:
            dll_path = os.path.join(gtk_libs_path, dll)
            if os.path.exists(dll_path):
                binaries.append((dll_path, '.'))
                break

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
