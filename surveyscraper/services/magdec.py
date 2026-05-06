"""Magnetic declination services.

Two HTTP calls power the MagDec tab:
  * `geocode(location)` resolves a free-text location to (lat, lon) via OSM
    Nominatim.
  * `magnetic_declination(lat, lon, model, year, month, day)` queries NOAA's
    geomag calculator.

Both raise `NetworkError` on failure so the UI can surface a single, focused
message rather than silently returning None as the legacy code did.

The NOAA endpoint expects an API key. The key is read from
`config_settings.json` (`noaa_api_key`); the prior hardcoded default is
preserved as a fallback so existing installations keep working.
"""
from __future__ import annotations

import requests

from surveyscraper.core.errors import NetworkError
from surveyscraper.logging_setup import get_logger
from surveyscraper.services import config_store

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search.php"
NOAA_DECLINATION_URL = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"
USER_AGENT = "SurveyScraper/3.3 (https://github.com/LovelK7/SurveyScraper)"
DEFAULT_NOAA_KEY = "zNEw7"  # legacy default; prefer setting `noaa_api_key` in config_settings.json
DEFAULT_TIMEOUT = 15

_log = get_logger("magdec")


def _noaa_api_key() -> str:
    try:
        config = config_store.read_config()
    except Exception:
        return DEFAULT_NOAA_KEY
    return config.get("noaa_api_key", DEFAULT_NOAA_KEY)


def geocode(location: str) -> tuple[float, float]:
    """Resolve a free-text location to (latitude, longitude) via OSM Nominatim."""
    if not location:
        raise NetworkError("Location string is empty")

    headers = {"User-Agent": USER_AGENT}
    params = {"q": location, "format": "jsonv2"}
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as e:
        _log.exception("Nominatim request failed for %r", location)
        raise NetworkError(f"Could not reach Nominatim: {e}") from e

    if response.status_code != 200:
        _log.error("Nominatim non-200: %s -- %s", response.status_code, response.text[:200])
        raise NetworkError(f"Nominatim returned HTTP {response.status_code}")

    try:
        results = response.json()
        return float(results[0]["lat"]), float(results[0]["lon"])
    except (ValueError, IndexError, KeyError) as e:
        _log.exception("Nominatim response did not contain a coordinate")
        raise NetworkError(f"Could not parse Nominatim response: {e}") from e


def magnetic_declination(
    latitude: float,
    longitude: float,
    model: str,
    year: int | str,
    month: int | str,
    day: int | str,
) -> float:
    """Return magnetic declination (degrees) for a point and date via NOAA's API."""
    if latitude is None or longitude is None:
        raise NetworkError("Latitude/longitude are required to compute declination")

    params = {
        "lat1": latitude,
        "lon1": longitude,
        "model": model,
        "startYear": year,
        "startMonth": month,
        "startDay": day,
        "key": _noaa_api_key(),
        "resultFormat": "json",
    }
    try:
        response = requests.get(NOAA_DECLINATION_URL, params=params, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as e:
        _log.exception("NOAA request failed (lat=%s lon=%s)", latitude, longitude)
        raise NetworkError(f"Could not reach NOAA: {e}") from e

    try:
        data = response.json()
        return float(data["result"][0]["declination"])
    except (ValueError, KeyError, IndexError, TypeError) as e:
        _log.exception("NOAA response did not contain a declination value")
        raise NetworkError(f"Could not parse NOAA response: {e}") from e
