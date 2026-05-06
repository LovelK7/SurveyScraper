# Architecture

SurveyScraper is a single-window Windows desktop tool built on
[customtkinter](https://customtkinter.tomschimansky.com/). It imports cave
survey data from three field apps (TopoDroid, PocketTopo, Qave/Walls), filters
out splays, applies magnetic declination correction, drives a Selenium
automation against [Speleoliti Online](https://speleoliti.speleo.net/) to
compute cave dimensions, and exports a clean CSV.

This document is the entry point for anyone (human or AI agent) who needs to
make a change without first reading every source file.

## Top-level layout

```
SurveyScraper/
  surveyscraper_v3.py             # Entry point + GUI (legacy monolith, being slimmed)
  surveyscraper/                  # Package — all new code lives here
    __init__.py                   # __version__
    __main__.py                   # `python -m surveyscraper`
    paths.py                      # Filesystem paths (script vs frozen-exe)
    logging_setup.py              # Rotating-file logger
    i18n.py                       # Translator (HR / EN)
    core/
      errors.py                   # ParseError, NetworkError, SpeleolitiError
    parsers/
      __init__.py                 # PARSERS registry, parse_file(software, path)
      base.py                     # BaseParser, ParseResult, empty_survey()
      topodroid.py                # TopoDroidParser
      pockettopo.py               # PocketTopoParser
      qave.py                     # QaveParser
    services/
      config_store.py             # Read/write config_settings.json
      magdec.py                   # geocode(), magnetic_declination()
      speleoliti.py               # SpeleolitiOnline (Selenium driver)
      exporter.py                 # write_survey_json(), export_to_csv()
  config_settings.json            # Bilingual catalog + last-used software + NOAA key
  survey_data.json                # Generated at runtime (gitignored)
  surveyscraper_README.txt        # Bundled help (HR)
  surveyscraper_README_EN.txt     # Bundled help (EN)
  img/                            # Icons, .ico
  testing/                        # Local-only scratch files (gitignored)
  tests/                          # pytest suite
    fixtures/                     # Tracked sample files used by the parser tests
    golden/                       # JSON snapshots compared against parser output
  build.spec                      # PyInstaller spec
  build.py                        # build + zip wrapper
  .github/workflows/release.yml   # CI: build + release on tag push
  pyproject.toml                  # Project metadata + dependencies
  requirements.txt                # Pip mirror
  requirements-dev.txt            # Pip mirror with test/build extras
  ruff.toml                       # Linter config
```

## Data flow (happy path)

```
User clicks "Open survey file"
        │
        ▼
SurveyScraper.open_file_event   ──► reset survey state, persist last-used software
        │
        ▼
SurveyScraper.parse_event(software)
        │
        ▼
parsers.parse_file(software, path)              [pure, raises ParseError]
        │
        ▼
ParseResult(survey_dict, cave_name, survey_date, has_splays)
        │
        ▼
exporter.write_survey_json(speleoliti_view, ...)   # splays filtered for TopoDroid
        │
        ▼
SurveyScraper.run_speleoliti_calculation
        │
        ▼
services.speleoliti.SpeleolitiOnline   ──► chromedriver, XPath scraping
        │
        ▼
GUI fields populated (cave_name, fixed_station, dimensions)

User clicks "Lookup coordinates"      ──► services.magdec.geocode(...)
User clicks "Calculate declination"   ──► services.magdec.magnetic_declination(...)
User clicks "Save settings"           ──► save_json: apply prefix + declination, write
User clicks "Export to CSV"           ──► services.exporter.export_to_csv(...)
```

The GUI is the orchestrator. Services and parsers know nothing about
customtkinter and never call `messagebox.showerror`; they raise typed
exceptions, and the GUI decides whether to show a dialog or log silently.

## Cross-cutting concerns

| Concern        | Lives in                                    | Notes                                                                |
| -------------- | ------------------------------------------- | -------------------------------------------------------------------- |
| Filesystem     | `surveyscraper/paths.py`                    | One frozen-vs-script check; everything else derives from that.       |
| Logging        | `surveyscraper/logging_setup.py`            | RotatingFileHandler at `surveyscraper.log` next to the exe + stderr. |
| Bilingual UI   | `surveyscraper/i18n.py`                     | `Translator.t(key)` looks up `[hr_str, en_str]` in config JSON.      |
| Error model    | `surveyscraper/core/errors.py`              | `ParseError`, `NetworkError`, `SpeleolitiError`.                     |
| Config IO      | `surveyscraper/services/config_store.py`    | The only module that opens `config_settings.json`.                   |

## On-disk JSON shape (Speleoliti contract)

`survey_data.json` is uploaded to Speleoliti Online via Selenium. Its shape
is dictated by what the Speleoliti web app accepts and must not be changed
casually. Tests in `tests/golden/` snapshot the parser outputs in this exact
shape; if Speleoliti's expectations change, regenerate the goldens together
with the parser update.

```jsonc
{
  "fix": "",
  "x": "", "y": "", "z": "",
  "dcl": "",
  "name": "",
  "descr": "",
  "viz": [
    "null",                                // 0-th element is always the literal string "null"
    {
      "t1": "1", "t2": "2",
      "l": 5.000, "a": 123.0, "f": -3.0,
      "left": "null", "right": "null", "up": "null", "down": "null",
      "note": "", "flags": "",
      "is_splay": false                    // TopoDroid only
    }
    // ...
  ]
}
```

For TopoDroid, splays carry `is_splay: true` and a `t2` value prefixed with
`*` (Speleoliti's splay marker). The Speleoliti-friendly view filters splays
before upload; the in-memory `ParseResult` keeps them so the user's CSV
export can include them via the "Include splays" toggle.

## Why customtkinter (not Qt / Flet)

A Qt port would give a native look and Designer support but is a multi-week
rewrite of every widget. Flet has cleaner ergonomics but rougher Windows
packaging and a heavier runtime. Customtkinter works today, the user
considers the look acceptable, and the package layout above keeps
service/parser code framework-agnostic. A future framework swap touches
only `surveyscraper/ui/*` (planned, see "Deferred work" below).

## Known fragilities (preserved, not fixed in this refactor)

These behaviors are kept identical to the legacy code; flag them as risks
for future work:

- **Speleoliti XPaths** — `surveyscraper/services/speleoliti.py` reads cave
  dimensions and station altitudes from hardcoded XPaths
  (`//*[@id="table99"]/tbody/tr[N]/td[2]`, etc.). Any DOM change on
  speleoliti.speleo.net breaks the workflow. Mitigation: XPaths are now
  module-level constants so the blast radius is one file.
- **TopoDroid header parsing** — the old format extracts the date from
  literal character positions `[2:12]` of line 1 and the cave name from
  `[2:]` of line 2. Brittle to TopoDroid format changes.
- **PocketTopo brackets/arrows regex** — `re.sub(r'\[.\]', '', ...)` matches
  exactly one character inside brackets; multi-character bracket annotations
  are not handled.
- **Qave shot field order** — the on-disk shot dict for Qave emits `f`
  before `a` (a quirk of the legacy code, preserved for byte-identity).
- **NOAA API key** — the legacy hardcoded key `zNEw7` is the default in
  `config_settings.json` (`noaa_api_key`). Users can override via the JSON,
  but the project ships the same key it always shipped.
- **Speleoliti calculation runs synchronously on the main thread** — the
  legacy code wrapped it in `threading.Thread(target=...())` (note the
  parentheses: the method ran synchronously and the thread started a
  no-op). The downstream GUI reads attributes set by the call, so the
  synchronous behavior is load-bearing. Truly async execution requires a
  GUI redesign and is part of the deferred Phase 5.

## Bug fixes folded into this refactor

- **Parse rollback**: parsers no longer write `survey_data.json` mid-parse;
  the GUI writes it only after a successful parse so a failure half-way
  through can no longer leave a corrupted file behind.
- **Dead `latitude` / `longitude` globals** in `get_location` removed; the
  function returns its values directly via the magdec service.
- **NOAA API key** moved out of source into `config_settings.json`.
- **Misleading `threading.Thread(target=method())`** call replaced by a
  direct synchronous call (see "Known fragilities" above for context).

## Deferred work (Phase 4 + Phase 5)

This refactor delivered Phases 0–3, 6, 7, 8. Two phases were intentionally
deferred to keep the diff bounded:

- **Phase 4 — `Shot` / `CaveSurvey` dataclasses.** The plan called for
  replacing the loose dict shape with typed dataclasses. Implementing this
  while strictly preserving the byte-for-byte JSON output for Qave is
  awkward (the legacy field-order quirk is incompatible with a single
  canonical Shot type). Pick one of:
    1. Migrate to dataclasses and accept the schema-equivalent (but
       byte-different) JSON output for Qave. Update `tests/golden/` once.
    2. Keep two `to_legacy_dict()` variants — one canonical, one with the
       Qave order — and document the dialect.
  Either is small; both belong on a feature branch with a single CI run to
  confirm Speleoliti still accepts the new bytes.
- **Phase 5 — UI module split.** The 700-line widget construction in
  `SurveyScraper.__init__` is functional but hard to extend. The proposed
  split is:
    - `surveyscraper/ui/app.py` — orchestrator (~150 lines)
    - `surveyscraper/ui/tabs/{main,magdec,help}_tab.py` — one file each
    - `surveyscraper/ui/widgets/{loading,tooltip}.py`
    - `surveyscraper/ui/assets.py` — cached image loader
  After this split, swapping customtkinter for Qt/Flet would touch only
  `surveyscraper/ui/`.

Both of the above benefit from running this refactor's test suite as a
regression net.
