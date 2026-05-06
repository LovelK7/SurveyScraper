"""Translator tests."""
from __future__ import annotations

import pytest

from surveyscraper.i18n import LANGUAGES, Translator


@pytest.fixture
def catalog():
    return {
        "language_setting": "HR",
        "import_frm_lbl": ["Uvoz", "Import"],
        "open_file": ["Otvori datoteku", "Open file"],
    }


def test_default_language_is_hr(catalog):
    t = Translator(catalog)
    assert t.language == "HR"
    assert t.t("import_frm_lbl") == "Uvoz"


def test_set_language_switches_index(catalog):
    t = Translator(catalog)
    t.set_language("EN")
    assert t.t("import_frm_lbl") == "Import"
    assert t.t("open_file") == "Open file"


def test_unknown_language_raises(catalog):
    t = Translator(catalog)
    with pytest.raises(ValueError):
        t.set_language("DE")


def test_missing_key_returns_marker(catalog):
    t = Translator(catalog)
    assert t.t("nonexistent") == "<missing:nonexistent>"


def test_missing_key_with_default(catalog):
    t = Translator(catalog)
    assert t.t("nonexistent", default="fallback") == "fallback"


def test_languages_constant():
    assert LANGUAGES == ("HR", "EN")
