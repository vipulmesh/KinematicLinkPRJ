# FourBarSimulator.spec
#
# PyInstaller spec file for the Four-Bar Kinematic Chain Simulator.
#
# Design decisions that reduce antivirus false-positive risk:
#
#  1. --onedir (COLLECT) instead of --onefile
#     --onefile extracts a hidden temporary archive to %TEMP% at launch,
#     which is a recognised pattern used by malware droppers and is the
#     single most common trigger for Defender / SmartScreen heuristics.
#     --onedir ships every file in plain sight inside the dist folder;
#     nothing is unpacked or executed from a temporary location.
#
#  2. console=False with windowed=True
#     A GUI application has no reason to open a console window.  Hiding
#     it is the standard practice for GUI apps; showing it would look
#     suspicious for a GUI-only tool.
#
#  3. No UPX compression
#     UPX-compressed executables share byte patterns with many packers
#     used in malware.  Disabling UPX (upx=False) ships the files
#     uncompressed and unobfuscated, which is easier for scanners to
#     classify as benign.
#
#  4. Full Windows version-info block
#     Windows Authenticode trust and SmartScreen reputation are tied to
#     the PE version-info resource.  A properly filled-in VERSIONINFO
#     block (company, product, copyright, version) reduces the "unsigned
#     unknown publisher" risk and is required for code-signing to convey
#     meaningful publisher information.
#
#  5. Only legitimate, necessary dependencies are collected.
#     No network access, no registry writes, no self-modifying code, no
#     subprocess spawning of other executables at runtime.
#
# ---------------------------------------------------------------------------
# How to build
#   pip install pyinstaller
#   pyinstaller FourBarSimulator.spec
#
# Output will be in:
#   dist\FourBarSimulator\FourBarSimulator.exe   (main executable)
#   dist\FourBarSimulator\                       (all supporting files)
# ---------------------------------------------------------------------------

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None  # No encryption — transparent build

# ---------------------------------------------------------------------------
# Hidden imports
# ---------------------------------------------------------------------------
# PySide6 Qt plugins are loaded by Qt at runtime through its plugin system;
# PyInstaller cannot always detect them via static analysis alone.
hidden_imports = (
    collect_submodules('PySide6')
    + collect_submodules('scipy')
    + collect_submodules('scipy.optimize')
    + collect_submodules('scipy.linalg')
    + collect_submodules('numpy')
    + collect_submodules('matplotlib')
    + collect_submodules('pandas')
    + [
        # Application packages
        'core',
        'core.constants',
        'core.mechanism',
        'core.solver',
        'core.validation',
        'core.utils',
        'gui',
        'gui.gui',
        'gui.animation',
        'plots',
        'plots.graphs',
        'export',
        'export.export',
    ]
)

# ---------------------------------------------------------------------------
# Data files  (source, dest-dir-inside-bundle)
# ---------------------------------------------------------------------------
datas = [
    # Application assets (icon, splash image)
    ('assets',  'assets'),
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test / development frameworks not needed at runtime
        'pytest',
        'unittest',
        'doctest',
        'pdb',
        'IPython',
        'ipykernel',
        'notebook',
        'tkinter',      # Not used; PySide6 is the UI toolkit
        'wx',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# ---------------------------------------------------------------------------
# EXE — the launcher stub only; payloads live beside it in the directory
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],                     # No scripts merged into the EXE itself (onedir)
    exclude_binaries=True,  # Binaries go into COLLECT, not the EXE stub
    name='FourBarSimulator',
    debug=False,            # No debug output
    bootloader_ignore_signals=False,
    strip=False,            # Do not strip debug symbols (reduces false positives)
    upx=False,              # Disable UPX — compressed PE patterns trigger heuristics
    console=False,          # GUI application — no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
    # Windows PE version-info resource
    version='version_info.txt',
)

# ---------------------------------------------------------------------------
# COLLECT — assembles the full onedir distribution folder
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FourBarSimulator',
)
