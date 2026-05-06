# Contributing

This document covers the most common change workflows. Read
[ARCHITECTURE.md](ARCHITECTURE.md) first for a map of the codebase.

## Dev environment

```powershell
# Windows, PowerShell, from the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

`pip install -e .` installs the project in editable mode — code edits take
effect without reinstalling. The `[dev]` extra brings in pytest, responses,
ruff, and PyInstaller.

## Running the app

```powershell
python -m surveyscraper          # via the package entry point
# or, equivalently for now (legacy entry point):
python surveyscraper_v3.py
```

## Running the tests

```powershell
pytest                # full suite (≈0.4 s)
pytest -k topodroid   # subset
pytest -v             # verbose
```

The tests in `tests/test_parsers.py` are golden-snapshot tests: they
compare the parser output against committed JSON in `tests/golden/`. If you
intentionally change parser output, regenerate the goldens (see "Adding a
new parser" below) and review the diff carefully — Speleoliti Online
consumes this exact shape.

## Linting

```powershell
ruff check .
ruff format --check .   # see ruff.toml for config
```

## Common tasks

### Add a new survey-format parser (e.g. Therion)

1. Create `surveyscraper/parsers/therion.py`:
   ```python
   from pathlib import Path
   from surveyscraper.core.errors import ParseError
   from surveyscraper.parsers.base import BaseParser, ParseResult, empty_survey

   class TherionParser(BaseParser):
       def parse(self, path: Path) -> ParseResult:
           # ...read the file, populate `survey['viz']` with shot dicts...
           survey = empty_survey()
           # ...
           return ParseResult(survey=survey, cave_name=..., survey_date=...)
   ```
   Field order in each shot dict matters for byte-identical JSON output;
   match the convention used by the existing parsers.
2. Register the parser in `surveyscraper/parsers/__init__.py`:
   ```python
   PARSERS = {
       "TopoDroid": TopoDroidParser,
       "PocketTopo": PocketTopoParser,
       "Qave": QaveParser,
       "Therion": TherionParser,           # ← new
   }
   ```
3. Wire the file-extension dispatch in
   [`surveyscraper_v3.py:open_file_event`](../surveyscraper_v3.py)
   (the `endswith('.csv') / .txt / .srv` ladder).
4. Drop a sample file in `testing/`.
5. Generate a golden snapshot:
   ```powershell
   python -X utf8 -c "import json; from surveyscraper.parsers import parse_file; r = parse_file('Therion', 'testing/example.th'); json.dump({'survey': r.survey, 'cave_name': r.cave_name, 'survey_date': r.survey_date.isoformat() if r.survey_date else None, 'has_splays': r.has_splays}, open('tests/golden/therion_example.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)"
   ```
6. Add a test in `tests/test_parsers.py` that loads the golden and asserts
   the parser produces it.

### Add a new translation key

1. Add the key to `config_settings.json` with `[hr_string, en_string]`:
   ```json
   "new_button_label": ["Novi gumb", "New button"]
   ```
2. Use it in the GUI: `lcat["new_button_label"][self.lc]` (legacy access)
   or `translator.t("new_button_label")` (new style — see `i18n.py`).
3. The translator's `available_languages()` is fixed at HR / EN. Adding
   a third language is a follow-up that requires changing
   `surveyscraper/i18n.py:LANGUAGES` and extending every catalog entry.

### Add a new GUI feature

The GUI is currently a single class in `surveyscraper_v3.py`. Until Phase 5
(see [ARCHITECTURE.md](ARCHITECTURE.md#deferred-work-phase-4--phase-5))
ships, follow this pattern:

1. Decide which tab the feature belongs to (Main / MagDec / Help). Find the
   tab's setup in `SurveyScraper.__init__`.
2. **Business logic** goes in `surveyscraper/services/` or
   `surveyscraper/parsers/`, not in the GUI class. Think: can this be unit-
   tested without spinning up a window? If yes, it does not belong in the
   widget tree.
3. The GUI calls into the service, catches the typed exceptions
   (`ParseError`, `NetworkError`, `SpeleolitiError`) and decides what to
   show. Never let a service `messagebox.showerror`.
4. Log via `surveyscraper.logging_setup.get_logger(<module-name>)` instead
   of `print()`.

### Update the magnetic-declination NOAA API key

The key lives in `config_settings.json` under `noaa_api_key`. The default
is the legacy `zNEw7`; users can override by editing that file. The
hardcoded fallback is in `surveyscraper/services/magdec.py:DEFAULT_NOAA_KEY`
and is only used when the key is missing from config.

### Bump the version

1. Update `surveyscraper/__init__.py:__version__`.
2. The `pyproject.toml` reads it dynamically.
3. The build script reads it for the zip name.
4. Tag a git release: `git tag v3.3.1 && git push origin v3.3.1` — the
   GitHub Actions workflow at `.github/workflows/release.yml` builds the
   exe, runs tests, and uploads the zip.

## Commit style

Short imperative subject, optional body explaining *why* (not what).
Examples:

```
extract parsers into surveyscraper.parsers
update v3.3 — fold rollback fix; threading no-op removed
docs: explain Qave field-order quirk
```

## Pull-request checklist

- [ ] Tests pass (`pytest`).
- [ ] Ruff is clean (`ruff check .`).
- [ ] If parser output changed, the golden snapshot is regenerated and the
      diff is reviewed.
- [ ] If a service signature changed, the GUI call site is updated.
- [ ] If a UI string is added, both HR and EN values are present in
      `config_settings.json`.
- [ ] Version bumped in `surveyscraper/__init__.py` for releases.
