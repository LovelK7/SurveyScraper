"""Bilingual (HR/EN) string lookup.

The on-disk `config_settings.json` stores entries as `[hr_string, en_string]`
lists, indexed by language. This module wraps that shape with a key-based
`t(key)` API while still exposing the raw catalog so legacy call sites that
read `catalog[key][index]` keep working until the GUI rewrite phase.
"""
from __future__ import annotations

import json
from typing import Any

LANGUAGES: tuple[str, ...] = ("HR", "EN")
DEFAULT_LANGUAGE: str = "HR"


class Translator:
    def __init__(self, catalog: dict[str, Any], language: str = DEFAULT_LANGUAGE) -> None:
        self._catalog = catalog
        self._index = 0
        self.language = language
        self.set_language(language)

    @classmethod
    def from_file(cls, path: str, language: str = DEFAULT_LANGUAGE) -> "Translator":
        with open(path, encoding="utf-8") as f:
            catalog = json.load(f)
        return cls(catalog, language)

    def set_language(self, language: str) -> None:
        if language not in LANGUAGES:
            raise ValueError(f"Unknown language {language!r}; expected one of {LANGUAGES}")
        self.language = language
        self._index = LANGUAGES.index(language)

    def t(self, key: str, default: str | None = None) -> str:
        entry = self._catalog.get(key)
        if entry is None:
            return default if default is not None else f"<missing:{key}>"
        if isinstance(entry, list) and len(entry) > self._index:
            return str(entry[self._index])
        return str(entry)

    def available_languages(self) -> list[str]:
        return list(LANGUAGES)

    @property
    def index(self) -> int:
        return self._index

    @property
    def catalog(self) -> dict[str, Any]:
        """Raw catalog. Mutating it persists across `t()` calls."""
        return self._catalog
