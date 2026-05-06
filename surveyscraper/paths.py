"""Single source of truth for filesystem paths used by the app.

Resolves the application root for both script and frozen-exe execution. All
asset, config, and log locations are derived from `APPLICATION_PATH` so a
future packaging change touches only this module.
"""
from __future__ import annotations

import os
import sys


def _resolve_application_path() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


APPLICATION_PATH: str = _resolve_application_path()

IMG_DIR: str = os.path.join(APPLICATION_PATH, "img")
CONFIG_PATH: str = os.path.join(APPLICATION_PATH, "config_settings.json")
SURVEY_DATA_PATH: str = os.path.join(APPLICATION_PATH, "survey_data.json")
LOG_PATH: str = os.path.join(APPLICATION_PATH, "surveyscraper.log")


def readme_path(language: str) -> str:
    if language == "EN":
        return os.path.join(APPLICATION_PATH, "surveyscraper_README_EN.txt")
    return os.path.join(APPLICATION_PATH, "surveyscraper_README.txt")


def img(name: str) -> str:
    return os.path.join(IMG_DIR, name)
