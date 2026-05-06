# Build & release

Replaces the legacy `za generiranje exea.txt` guide. Two paths:

1. **CI build (recommended)** — push a `vX.Y.Z` tag and let GitHub Actions
   build, test, and upload the exe to the release.
2. **Local build** — for testing the spec or producing a build without
   tagging.

## CI release (recommended)

```powershell
# 1. Bump the version in surveyscraper/__init__.py
# 2. Commit, push.
# 3. Tag and push the tag:
git tag v3.3.0
git push origin v3.3.0
```

The workflow at [.github/workflows/release.yml](../.github/workflows/release.yml)
runs on a Windows runner and:

1. Installs Python 3.11 + dev dependencies.
2. Runs `pytest`.
3. Runs `python build.py` — produces `dist/SurveyScraper-<version>.zip`.
4. Uploads the zip to the GitHub Release for the pushed tag.

A non-tag push to the workflow (or a `workflow_dispatch` trigger) still
builds and tests but uploads the zip as a workflow artifact instead of a
release.

## Local build

```powershell
# from the project root
.\.venv\Scripts\Activate.ps1            # if using a venv
pip install -r requirements-dev.txt     # one-time
python build.py
```

This:

1. Wipes `build/` and `dist/`.
2. Runs `pyinstaller build.spec` (single-file windowed exe).
3. Bundles the exe with `config_settings.json`, both README files, and
   `img/` into `dist/SurveyScraper-<version>/`.
4. Zips the bundle into `dist/SurveyScraper-<version>.zip`.

The output zip is what users download from GitHub Releases.

## What's bundled

The shipped zip has the structure:

```
SurveyScraper-3.3.0/
  surveyscraper_v3.exe
  config_settings.json
  surveyscraper_README.txt
  surveyscraper_README_EN.txt
  img/
    compass.png ... etc
    survey_point_icon_180376.ico
```

`survey_data.json` is **not** bundled — it's generated next to the exe at
runtime when the user opens a survey file. The `.gitignore` excludes it.

`surveyscraper.log` is also runtime-only — created next to the exe by the
rotating file handler in `surveyscraper/logging_setup.py`.

## Troubleshooting

### "Failed to execute script 'surveyscraper_v3' due to unhandled exception: No module named 'tkintermapview'"

PyInstaller didn't pick up tkintermapview's tile data. The hidden import
is declared in `build.spec`; if the error persists, also add the package's
data files via:

```python
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files("tkintermapview")
```

### Windows Defender flags the exe as a virus

False positive. PyInstaller-bundled exes get flagged by some heuristics.
Two mitigations:
1. Add a code-signing certificate (paid) — out of scope for this project.
2. Submit the exe to Microsoft for analysis at
   <https://www.microsoft.com/wdsi/filesubmission> — usually de-listed
   within a few days.

### ChromeDriver version mismatch on user machines

`webdriver_manager` auto-downloads the right driver at first run, but
needs internet access. If a user is behind a corporate proxy, the magdec
and Speleoliti workflows fail. The error appears in `surveyscraper.log`
next to the exe.

### Build fails on `customtkinter` themes

Recent customtkinter versions ship a `customtkinter/assets/themes/` folder
that PyInstaller may need help finding. If your build is missing the
"green" theme, add to `build.spec`:

```python
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files("customtkinter")
```

## Release checklist

1. `git status` — working tree clean.
2. `pytest` — green.
3. Bump `surveyscraper/__init__.py:__version__`.
4. Update `README.md` if user-facing behavior changed.
5. Commit: `release: v3.3.0`.
6. Tag: `git tag v3.3.0 && git push origin main v3.3.0`.
7. Verify CI succeeded; download the released zip; smoke-test on a clean
   Windows machine (no Python installed): open each of the three sample
   files, run a magdec lookup, export CSV.
