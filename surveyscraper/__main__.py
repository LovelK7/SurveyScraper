"""Entry point for `python -m surveyscraper`.

During the phased refactor the package delegates to the legacy script at the
project root so the running app keeps working at every step. Later phases will
move the bootstrap fully into this package.
"""
from __future__ import annotations

import os
import sys


def _ensure_project_root_on_path() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def main() -> None:
    _ensure_project_root_on_path()
    from surveyscraper_v3 import SurveyScraper, config

    lang, last_used = config()
    SurveyScraper(lang, last_used)


if __name__ == "__main__":
    main()
