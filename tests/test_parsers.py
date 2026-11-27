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


# --- TopoDroid raw-data export (one row per measurement) -------------------

def _legs(result):
    return [s for s in result.survey["viz"][1:] if not s["is_splay"]]


def _splays(result):
    return [s for s in result.survey["viz"][1:] if s["is_splay"]]


def test_topodroid_raw_metadata(topodroid_raw_csv):
    result = parse_file("TopoDroid", topodroid_raw_csv)
    assert result.cave_name == "jama_nad_cestou"
    assert result.survey_date.date().isoformat() == "2026-10-12"
    assert result.has_splays is True
    assert result.survey["viz"][0] == "null"


def test_topodroid_raw_counts_drop_deleted_and_overshoot(topodroid_raw_csv):
    result = parse_file("TopoDroid", topodroid_raw_csv)
    # 32 leg rows, 2 deleted (blunder 23-24 re-shot, and last leg 30-31)
    legs = _legs(result)
    assert len(legs) == 30
    assert ("30", "31") not in {(s["t1"], s["t2"]) for s in legs}
    # 525 splay rows, 20 deleted + 2 overshoot (56.78 m, 117.52 m)
    splays = _splays(result)
    assert len(splays) == 503
    assert max(s["l"] for s in splays) < 50


def test_topodroid_raw_leg_is_average_of_repeats(topodroid_raw_csv):
    result = parse_file("TopoDroid", topodroid_raw_csv)
    leg = _legs(result)[0]
    assert (leg["t1"], leg["t2"]) == ("0", "1")
    assert leg["l"] == pytest.approx((13.670 + 13.593 + 13.583 + 13.564) / 4, abs=1e-3)
    assert leg["a"] == pytest.approx((178.48 + 178.40 + 178.46 + 178.34) / 4, abs=0.01)
    assert leg["f"] == pytest.approx((29.66 + 29.68 + 29.66 + 29.68) / 4, abs=0.01)


def test_topodroid_raw_deleted_blunder_replaced_by_reshot(topodroid_raw_csv):
    result = parse_file("TopoDroid", topodroid_raw_csv)
    leg = next(s for s in _legs(result) if (s["t1"], s["t2"]) == ("23", "24"))
    assert leg["l"] > 3  # the 0.224 m deleted shot is ignored


def test_topodroid_raw_splay_shape(topodroid_raw_csv):
    result = parse_file("TopoDroid", topodroid_raw_csv)
    first = _splays(result)[0]
    assert first["t1"] == "0" and first["t2"] == "*0"
    assert (first["l"], first["a"], first["f"]) == (3.601, 177.14, 12.86)
    assert list(first) == ["t1", "t2", "l", "a", "f", "left", "right", "up", "down", "note", "flags", "is_splay"]


def test_topodroid_raw_azimuth_mean_wraps_north(tmp_path):
    f = tmp_path / "wrap.csv"
    f.write_text(
        "# 2026.01.02 created by TopoDroid v 6.2.46\n# wrap\n"
        "# id from to dist azi clino roll G M dip time type addres extend flag leg-type status Mx, My, Mz, Gx, Gy, Gz comment\n"
        "1,0,1,2.000,359.80,10.00,0,0,0,0,0,0,x,1,0,0,0,0,0,0,0,0,0,\n"
        "2,,,2.000,0.20,10.00,0,0,0,0,0,0,x,2,0,1,0,0,0,0,0,0,0,\n"
        "3,,,9.999,90.00,10.00,0,0,0,0,0,0,x,2,0,1,1,0,0,0,0,0,0,\n"
        "4,1,,1.000,90.00,-5.00,0,0,0,0,0,0,x,2,0,0,0,0,0,0,0,0,0,a, comment, with commas\n",
        encoding="utf-8",
    )
    result = parse_file("TopoDroid", f)
    leg, splay = result.survey["viz"][1:]
    assert leg["l"] == 2.0
    assert leg["a"] == pytest.approx(0.0, abs=0.01)  # not 180, and never 360.0
    assert splay["t1"] == "1" and splay["is_splay"]
