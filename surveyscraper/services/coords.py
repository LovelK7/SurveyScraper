"""Coordinate system conversion between WGS84 and HTRS96/TM (EPSG:3765).

HTRS96/TM is Croatia's official projected system: Transverse Mercator on the
GRS80 ellipsoid, central meridian 16.5°E, scale factor 0.9999, false easting
500 000 m, false northing 0. Coordinates are (E, N) in metres.

The projection is computed locally with the Krüger n-series (Karney 2011,
6th order), accurate to well under a millimetre across Croatia, so no
network call or pyproj dependency is needed.

Datum note: HTRS96 is realised from ETRS89; ETRS89 and WGS84 differ by well
under a metre in Croatia, far below anything that affects magnetic
declination, so geographic HTRS96 coordinates are treated as WGS84.
"""
from __future__ import annotations

import math

WGS84 = "WGS84"
HTRS96TM = "HTRS96/TM"
SYSTEMS: tuple[str, ...] = (WGS84, HTRS96TM)

# GRS80
_A = 6378137.0
_F = 1 / 298.257222101
_E = math.sqrt(_F * (2 - _F))

# HTRS96/TM projection parameters
_LON0 = math.radians(16.5)
_K0 = 0.9999
_FE = 500000.0
_FN = 0.0

# Plausible HTRS96/TM extent (Croatia plus a generous margin). Used to catch
# swapped E/N or WGS84 degrees typed while HTRS96/TM is selected.
E_RANGE = (150000.0, 850000.0)
N_RANGE = (4500000.0, 5300000.0)

_n = _F / (2 - _F)
_n2, _n3, _n4, _n5, _n6 = _n**2, _n**3, _n**4, _n**5, _n**6
_AA = _A / (1 + _n) * (1 + _n2 / 4 + _n4 / 64 + _n6 / 256)

_ALPHA = (
    _n / 2 - 2 * _n2 / 3 + 5 * _n3 / 16 + 41 * _n4 / 180 - 127 * _n5 / 288 + 7891 * _n6 / 37800,
    13 * _n2 / 48 - 3 * _n3 / 5 + 557 * _n4 / 1440 + 281 * _n5 / 630 - 1983433 * _n6 / 1935360,
    61 * _n3 / 240 - 103 * _n4 / 140 + 15061 * _n5 / 26880 + 167603 * _n6 / 181440,
    49561 * _n4 / 161280 - 179 * _n5 / 168 + 6601661 * _n6 / 7257600,
    34729 * _n5 / 80640 - 3418889 * _n6 / 1995840,
    212378941 * _n6 / 319334400,
)
_BETA = (
    _n / 2 - 2 * _n2 / 3 + 37 * _n3 / 96 - _n4 / 360 - 81 * _n5 / 512 + 96199 * _n6 / 604800,
    _n2 / 48 + _n3 / 15 - 437 * _n4 / 1440 + 46 * _n5 / 105 - 1118711 * _n6 / 3870720,
    17 * _n3 / 480 - 37 * _n4 / 840 - 209 * _n5 / 4480 + 5569 * _n6 / 90720,
    4397 * _n4 / 161280 - 11 * _n5 / 504 - 830251 * _n6 / 7257600,
    4583 * _n5 / 161280 - 108847 * _n6 / 3991680,
    20648693 * _n6 / 638668800,
)
_DELTA = (
    2 * _n - 2 * _n2 / 3 - 2 * _n3 + 116 * _n4 / 45 + 26 * _n5 / 45 - 2854 * _n6 / 675,
    7 * _n2 / 3 - 8 * _n3 / 5 - 227 * _n4 / 45 + 2704 * _n5 / 315 + 2323 * _n6 / 945,
    56 * _n3 / 15 - 136 * _n4 / 35 - 1262 * _n5 / 105 + 73814 * _n6 / 2835,
    4279 * _n4 / 630 - 332 * _n5 / 35 - 399572 * _n6 / 14175,
    4174 * _n5 / 315 - 144838 * _n6 / 6237,
    601676 * _n6 / 22275,
)


def wgs84_to_htrs96tm(lat: float, lon: float) -> tuple[float, float]:
    """(lat, lon) in degrees -> (easting, northing) in metres."""
    phi = math.radians(lat)
    lam = math.radians(lon) - _LON0
    t = math.sinh(math.atanh(math.sin(phi)) - _E * math.atanh(_E * math.sin(phi)))
    xi_p = math.atan2(t, math.cos(lam))
    eta_p = math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    xi, eta = xi_p, eta_p
    for j, a in enumerate(_ALPHA, start=1):
        xi += a * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p)
        eta += a * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p)
    return _FE + _K0 * _AA * eta, _FN + _K0 * _AA * xi


def htrs96tm_to_wgs84(easting: float, northing: float) -> tuple[float, float]:
    """(easting, northing) in metres -> (lat, lon) in degrees.

    Raises ValueError if the point is outside the plausible HTRS96/TM extent
    (most often E and N swapped, or degrees entered instead of metres).
    """
    if not (E_RANGE[0] <= easting <= E_RANGE[1] and N_RANGE[0] <= northing <= N_RANGE[1]):
        raise ValueError(f"HTRS96/TM coordinates out of range: E={easting}, N={northing}")
    xi = (northing - _FN) / (_K0 * _AA)
    eta = (easting - _FE) / (_K0 * _AA)
    xi_p, eta_p = xi, eta
    for j, b in enumerate(_BETA, start=1):
        xi_p -= b * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta_p -= b * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
    chi = math.asin(math.sin(xi_p) / math.cosh(eta_p))
    phi = chi + sum(d * math.sin(2 * j * chi) for j, d in enumerate(_DELTA, start=1))
    lam = _LON0 + math.atan2(math.sinh(eta_p), math.cos(xi_p))
    return math.degrees(phi), math.degrees(lam)


def parse_number(text: str) -> float:
    """float() that also accepts a decimal comma and stray spaces."""
    return float(text.strip().replace(" ", "").replace(",", "."))
