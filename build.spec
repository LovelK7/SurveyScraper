# PyInstaller spec for SurveyScraper.
#
# Build with:
#   pyinstaller build.spec
#
# Or via the convenience wrapper:
#   python build.py
#
# Replaces the legacy `za generiranje exea.txt` guide. Edit paths here when
# adding new bundled assets so the build is reproducible.

# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

PROJECT_ROOT = Path.cwd()

datas = [
    ("img", "img"),
    ("config_settings.json", "."),
    ("surveyscraper_README.txt", "."),
    ("surveyscraper_README_EN.txt", "."),
]

hiddenimports = [
    "tkintermapview",
    "PIL.Image",
    "selenium",
    "webdriver_manager.chrome",
    # idlelib is part of the stdlib but not auto-discovered by PyInstaller
    "idlelib.tooltip",
]

a = Analysis(
    ["surveyscraper_v3.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="surveyscraper_v3",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                     # --windowed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "img" / "survey_point_icon_180376.ico"),
)
