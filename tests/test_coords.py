"""HTRS96/TM <-> WGS84 conversion tests."""
from __future__ import annotations

import pytest

from surveyscraper.services import coords


def test_central_meridian_at_45n_matches_grs80_meridian_arc():
    # On the central meridian E is exactly the false easting and N is
    # k0 * meridian arc length; GRS80 arc to 45° = 4 984 944.378 m.
    e, n = coords.wgs84_to_htrs96tm(45.0, 16.5)
    assert e == pytest.approx(500000.0, abs=1e-6)
    assert n == pytest.approx(0.9999 * 4984944.378, abs=0.01)


@pytest.mark.parametrize("lat, lon", [
    (45.8150, 15.9819),   # Zagreb
    (42.6507, 18.0944),   # Dubrovnik
    (45.3271, 13.5000),   # western edge, Istria
    (45.1600, 19.4500),   # eastern edge
    (44.2672, 15.8422),
])
def test_round_trip_is_submillimetre(lat, lon):
    e, n = coords.wgs84_to_htrs96tm(lat, lon)
    lat2, lon2 = coords.htrs96tm_to_wgs84(e, n)
    # 1e-8 deg ~ 1 mm
    assert lat2 == pytest.approx(lat, abs=1e-8)
    assert lon2 == pytest.approx(lon, abs=1e-8)


def test_zagreb_projects_into_expected_area():
    e, n = coords.wgs84_to_htrs96tm(45.8150, 15.9819)
    assert 450000 < e < 470000
    assert 5070000 < n < 5080000


@pytest.mark.parametrize("e, n", [
    (5073500.0, 458000.0),   # swapped
    (45.815, 15.98),         # degrees typed in HTRS mode
])
def test_out_of_range_raises(e, n):
    with pytest.raises(ValueError):
        coords.htrs96tm_to_wgs84(e, n)


@pytest.mark.parametrize("text, expected", [
    ("45.8150", 45.815), ("45,8150", 45.815), (" 5 073 500,25 ", 5073500.25),
])
def test_parse_number(text, expected):
    assert coords.parse_number(text) == pytest.approx(expected)


def test_parse_number_rejects_garbage():
    with pytest.raises(ValueError):
        coords.parse_number("abc")
