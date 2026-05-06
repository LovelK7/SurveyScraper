"""Magdec service tests.

Both HTTP endpoints are stubbed with `responses`; no real network calls.
"""
from __future__ import annotations

import pytest
import responses

from surveyscraper.core.errors import NetworkError
from surveyscraper.services import magdec


@responses.activate
def test_geocode_success():
    responses.add(
        responses.GET,
        magdec.NOMINATIM_URL,
        json=[{"lat": "44.2672", "lon": "15.8422", "display_name": "Krkuž, Croatia"}],
        status=200,
    )
    lat, lon = magdec.geocode("Krkuz")
    assert lat == pytest.approx(44.2672)
    assert lon == pytest.approx(15.8422)


@responses.activate
def test_geocode_empty_result_raises():
    responses.add(
        responses.GET,
        magdec.NOMINATIM_URL,
        json=[],
        status=200,
    )
    with pytest.raises(NetworkError):
        magdec.geocode("Atlantis")


@responses.activate
def test_geocode_http_error_raises():
    responses.add(
        responses.GET,
        magdec.NOMINATIM_URL,
        status=500,
    )
    with pytest.raises(NetworkError):
        magdec.geocode("Anywhere")


def test_geocode_empty_string_raises():
    with pytest.raises(NetworkError):
        magdec.geocode("")


@responses.activate
def test_magnetic_declination_success():
    responses.add(
        responses.GET,
        magdec.NOAA_DECLINATION_URL,
        json={"result": [{"declination": 4.123}]},
        status=200,
    )
    value = magdec.magnetic_declination(44.2672, 15.8422, "WMM", 2025, 6, 16)
    assert value == pytest.approx(4.123)


@responses.activate
def test_magnetic_declination_missing_field_raises():
    responses.add(
        responses.GET,
        magdec.NOAA_DECLINATION_URL,
        json={"result": []},
        status=200,
    )
    with pytest.raises(NetworkError):
        magdec.magnetic_declination(44.2672, 15.8422, "WMM", 2025, 6, 16)


def test_magnetic_declination_missing_coords_raises():
    with pytest.raises(NetworkError):
        magdec.magnetic_declination(None, None, "WMM", 2025, 6, 16)
