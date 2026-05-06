"""Build the SurveyScraper exe and zip the deployment bundle.

Steps:
    1. Wipe `build/` and `dist/`.
    2. Run `pyinstaller build.spec`.
    3. Zip the produced exe together with the supporting assets users need
       (config_settings.json, README files, img/) into a single
       `dist/SurveyScraper-<version>.zip` ready for GitHub Releases.

Usage:
    python build.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"


def _read_version() -> str:
    init_py = ROOT / "surveyscraper" / "__init__.py"
    for line in init_py.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("__version__ not found in surveyscraper/__init__.py")


def _clean() -> None:
    for path in (DIST, BUILD):
        if path.exists():
            shutil.rmtree(path)


def _run_pyinstaller() -> None:
    cmd = [sys.executable, "-m", "PyInstaller", "build.spec"]
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def _make_zip(version: str) -> Path:
    bundle_dir = DIST / f"SurveyScraper-{version}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # The single-file exe lives at dist/surveyscraper_v3.exe
    exe = DIST / "surveyscraper_v3.exe"
    if not exe.exists():
        raise FileNotFoundError(f"Expected exe at {exe} but did not find it.")
    shutil.copy2(exe, bundle_dir / exe.name)

    # Bundled runtime files users need next to the exe
    extras = [
        "config_settings.json",
        "surveyscraper_README.txt",
        "surveyscraper_README_EN.txt",
    ]
    for name in extras:
        shutil.copy2(ROOT / name, bundle_dir / name)
    shutil.copytree(ROOT / "img", bundle_dir / "img")

    zip_path = DIST / f"SurveyScraper-{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_dir.rglob("*"):
            zf.write(path, path.relative_to(DIST))
    return zip_path


def main() -> None:
    version = _read_version()
    print(f"Building SurveyScraper {version}")
    _clean()
    _run_pyinstaller()
    zip_path = _make_zip(version)
    print(f"\nBuilt zip: {zip_path}")


if __name__ == "__main__":
    main()
