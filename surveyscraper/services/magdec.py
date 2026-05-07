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

import time

import requests

from surveyscraper.core.errors import NetworkError
from surveyscraper.logging_setup import get_logger
from surveyscraper.services import config_store

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search.php"
NOAA_DECLINATION_URL = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"
USER_AGENT = "SurveyScraper/4.0 (https://github.com/LovelK7/SurveyScraper)"
DEFAULT_NOAA_KEY = "zNEw7"  # legacy default; prefer setting `noaa_api_key` in config_settings.json
DEFAULT_TIMEOUT = 20
RETRY_ATTEMPTS = 2          # initial + one retry
RETRY_BACKOFF_SECONDS = 1.5

# NOAA-accepted year ranges per model (probed 2026-05). WMM is a 5-year model;
# its current epoch is WMM2025 covering 2025-2029. IGRF is updated every five
# years and currently covers 1900-2029. Bump these when NOAA releases the next
# epoch (the GUI labels are derived from these constants).
MODEL_YEAR_RANGES: dict[str, tuple[int, int]] = {
    "WMM": (2025, 2029),
    "IGRF": (1900, 2029),
}

_log = get_logger("magdec")


def years_for_model(model: str) -> list[int]:
    """Return the inclusive list of years NOAA currently accepts for `model`."""
    if model not in MODEL_YEAR_RANGES:
        return []
    lo, hi = MODEL_YEAR_RANGES[model]
    return list(range(lo, hi + 1))


def is_year_valid(model: str, year: int) -> bool:
    if model not in MODEL_YEAR_RANGES:
        return False
    lo, hi = MODEL_YEAR_RANGES[model]
    return lo <= year <= hi


def model_label(model: str) -> str:
    """Display label like `WMM (2025-2029)` for a radio button."""
    if model not in MODEL_YEAR_RANGES:
        return model
    lo, hi = MODEL_YEAR_RANGES[model]
    return f"{model} ({lo}-{hi})"


def _redact(params: dict) -> dict:
    """Return a copy of params with the API key redacted, safe to log."""
    if "key" not in params:
        return params
    return {k: ("<redacted>" if k == "key" else v) for k, v in params.items()}


def _request_json(url: str, *, params: dict, headers: dict | None = None, label: str) -> dict | list:
    """GET `url` and decode JSON, retrying once on transient failure.

    Logs status code, content-type, a body excerpt, and the (redacted) request
    params when something goes sideways so future failures are diagnosable
    from `surveyscraper.log`.
    """
    safe_params = _redact(params)
    last_error: Exception | None = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
        except requests.RequestException as e:
            last_error = e
            _log.warning(
                "%s request failed (attempt %d/%d): %s | params=%r",
                label, attempt + 1, RETRY_ATTEMPTS, e, safe_params,
            )
        else:
            if response.status_code != 200:
                last_error = NetworkError(f"{label} returned HTTP {response.status_code}")
                _log.warning(
                    "%s non-200 (attempt %d/%d): status=%s content-type=%s body[:500]=%r | params=%r",
                    label, attempt + 1, RETRY_ATTEMPTS,
                    response.status_code, response.headers.get("content-type"),
                    response.text[:500], safe_params,
                )
            else:
                try:
                    return response.json()
                except ValueError as e:
                    last_error = e
                    _log.warning(
                        "%s body was not JSON (attempt %d/%d): content-type=%s body[:500]=%r | params=%r",
                        label, attempt + 1, RETRY_ATTEMPTS,
                        response.headers.get("content-type"),
                        response.text[:500], safe_params,
                    )
        if attempt + 1 < RETRY_ATTEMPTS:
            time.sleep(RETRY_BACKOFF_SECONDS)

    raise NetworkError(f"{label} failed after {RETRY_ATTEMPTS} attempts: {last_error}")


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

    results = _request_json(
        NOMINATIM_URL,
        params={"q": location, "format": "jsonv2"},
        headers={"User-Agent": USER_AGENT},
        label="Nominatim",
    )
    try:
        return float(results[0]["lat"]), float(results[0]["lon"])
    except (IndexError, KeyError, TypeError) as e:
        _log.error("Nominatim returned no usable coordinate for %r: %r", location, results)
        raise NetworkError(f"Nominatim returned no coordinate for {location!r}") from e


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

    data = _request_json(
        NOAA_DECLINATION_URL,
        params={
            "lat1": latitude,
            "lon1": longitude,
            "model": model,
            "startYear": year,
            "startMonth": month,
            "startDay": day,
            "key": _noaa_api_key(),
            "resultFormat": "json",
        },
        label="NOAA",
    )
    try:
        return float(data["result"][0]["declination"])
    except (KeyError, IndexError, TypeError) as e:
        _log.error("NOAA response missing declination: %r", data)
        raise NetworkError("NOAA response did not contain a declination value") from e
