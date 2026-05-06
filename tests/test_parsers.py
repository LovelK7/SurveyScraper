"""Parser regression tests against golden snapshots.

Each parser is asserted to produce the same `ParseResult` (survey dict,
cave name, survey date, splay flag) as the snapshot in `tests/golden/`.

If a deliberate output change is made, regenerate goldens:

    python -m scripts.regenerate_golden  # (or run the snippet in conftest)
"""
from __future__ import annotations

import pytest

from surveyscraper.core.errors import ParseError
from surveyscraper.parsers import parse_file
from surveyscraper.parsers.base import ParseResult
from surveyscraper.parsers.topodroid import TopoDroidParser

from .conftest import load_golden


def _to_serializable(result: ParseResult) -> dict:
    return {
        "survey": result.survey,
        "cave_name": result.cave_name,
        "survey_date": result.survey_date.isoformat() if result.survey_date else None,
        "has_splays": result.has_splays,
    }


def test_topodroid_v6_format(topodroid_v6_csv):
    result = parse_file("TopoDroid", topodroid_v6_csv)
    expected = load_golden("topodroid_jama_Edison_2.json")
    assert _to_serializable(result) == expected


def test_topodroid_old_format(topodroid_old_csv):
    result = parse_file("TopoDroid", topodroid_old_csv)
    expected = load_golden("topodroid_krkuz_uskrs.json")
    assert _to_serializable(result) == expected


def test_pockettopo(pockettopo_txt):
    result = parse_file("PocketTopo", pockettopo_txt)
    expected = load_golden("pockettopo_geyrovo.json")
    assert _to_serializable(result) == expected


def test_topodroid_marks_splays(topodroid_v6_csv):
    result = parse_file("TopoDroid", topodroid_v6_csv)
    assert result.has_splays is True
    splays = [s for s in result.survey["viz"][1:] if s.get("is_splay")]
    legs = [s for s in result.survey["viz"][1:] if not s.get("is_splay")]
    # Legs should not start with the splay-marker asterisk
    assert all(not leg["t2"].startswith("*") for leg in legs)
    # Splays should
    assert all(splay["t2"].startswith("*") for splay in splays)


def test_speleoliti_view_drops_splays(topodroid_v6_csv):
    result = parse_file("TopoDroid", topodroid_v6_csv)
    view = result.survey_for_speleoliti()
    assert all(not s.get("is_splay") for s in view["viz"][1:])
    assert len(view["viz"]) <= len(result.survey["viz"])


def test_speleoliti_view_passthrough_for_non_splay_parsers(pockettopo_txt):
    result = parse_file("PocketTopo", pockettopo_txt)
    view = result.survey_for_speleoliti()
    assert view["viz"] == result.survey["viz"]


def test_unknown_software_raises():
    with pytest.raises(ParseError):
        parse_file("Therion", "/nonexistent/path")


def test_topodroid_propagates_io_error_as_parse_error(tmp_path):
    fake = tmp_path / "missing.csv"
    with pytest.raises(ParseError):
        TopoDroidParser().parse(fake)
