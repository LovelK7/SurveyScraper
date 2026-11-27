"""TopoDroid (.csv) parser.

Handles three TopoDroid CSV exports:
  * pre-v6.4 and v6.4+ reduced shot lists (`from,to,tape,compass,clino,...`);
  * the raw-data export (`# id from to dist azi clino roll G M dip ...`),
    with one row per measurement. See `_parse_raw` for the rules.
Splay shots are kept in the
result (with `is_splay=True`) so the GUI can include them in the CSV export;
they are filtered out of the version uploaded to Speleoliti Online.
"""
from __future__ import annotations

import datetime as _dt
import math
from pathlib import Path

from surveyscraper.core.errors import ParseError
from surveyscraper.parsers.base import BaseParser, ParseResult, empty_survey


RAW_HEADER_PREFIX = "# id from to dist azi clino"

# Raw-export column indexes (header: id from to dist azi clino roll G M dip
# time type addres extend flag leg-type status Mx My Mz Gx Gy Gz comment).
_R_FROM, _R_TO, _R_DIST, _R_AZI, _R_CLINO = 1, 2, 3, 4, 5
_R_LEG_TYPE, _R_STATUS = 15, 16
_R_MIN_COLS = 17
_LEG_TYPE_REPEAT = "1"  # extra measurement of the preceding leg
_STATUS_NORMAL = "0"    # 1 = deleted, 2 = overshoot; anything else is dropped too


def _shot(t1: str, t2: str, dist: float, azi: float, clino: float, is_splay: bool) -> dict:
    return {
        "t1": t1,
        "t2": t2,
        "l": dist,
        "a": azi,
        "f": clino,
        "left": "null",
        "right": "null",
        "up": "null",
        "down": "null",
        "note": "",
        "flags": "",
        "is_splay": is_splay,
    }


def _mean_azimuth(values: list[float]) -> float:
    """Circular mean, so 359.8 and 0.2 average to 0.0 rather than 180."""
    x = sum(math.cos(math.radians(a)) for a in values)
    y = sum(math.sin(math.radians(a)) for a in values)
    return math.degrees(math.atan2(y, x)) % 360.0


class TopoDroidParser(BaseParser):
    def parse(self, path: Path) -> ParseResult:
        try:
            return self._parse(path)
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse TopoDroid file: {e}") from e

    def _parse(self, path: Path) -> ParseResult:
        with open(path, encoding="utf-8") as file:
            head = [file.readline() for _ in range(3)]
        if head[2].startswith(RAW_HEADER_PREFIX):
            return self._parse_raw(path)
        survey = empty_survey()
        cave_name: str | None = None
        survey_date: _dt.datetime | None = None
        has_splays = False

        with open(path, encoding="utf-8") as file:
            line1 = next(file)
            line2 = next(file)
            if "# name:" in line2:
                # New format (TopoDroid v6.4+): name on line 2, date on line 3, 4 more header lines
                cave_name = line2.split("# name:")[1].strip()
                line3 = next(file)
                date = line3.split("# date:")[1].strip()
                survey_date = _dt.datetime.strptime(date, "%Y.%m.%d")
                next(file)  # team
                next(file)  # declination
                next(file)  # units
                next(file)  # column headers
            else:
                # Old format: date at chars 2-12 of line 1, cave name after '# ' on line 2
                date = line1.split(",")[0][2:12]
                survey_date = _dt.datetime.strptime(date, "%Y.%m.%d")
                cave_name = line2.split(",")[0][2:].strip()
                next(file)
                next(file)
            for row in file:
                shot = row.strip().split(",")
                if len(shot) >= 5 and shot[1] != "-":
                    shot_from = shot[0][0:shot[0].find("@")]
                    shot_to = shot[1][0:shot[1].find("@")]
                    survey["viz"].append({
                        "t1": shot_from,
                        "t2": shot_to,
                        "l": float(shot[2]),
                        "a": float(shot[3]),
                        "f": float(shot[4]),
                        "left": "null",
                        "right": "null",
                        "up": "null",
                        "down": "null",
                        "note": "",
                        "flags": "",
                        "is_splay": False,
                    })
                elif len(shot) >= 5 and shot[1] == "-":
                    shot_from = shot[0][0:shot[0].find("@")]
                    # Asterisk prefix marks splays so Speleoliti recognises them
                    shot_to = "*" + shot_from
                    survey["viz"].append({
                        "t1": shot_from,
                        "t2": shot_to,
                        "l": float(shot[2]),
                        "a": float(shot[3]),
                        "f": float(shot[4]),
                        "left": "null",
                        "right": "null",
                        "up": "null",
                        "down": "null",
                        "note": "",
                        "flags": "",
                        "is_splay": True,
                    })
                    has_splays = True

        return ParseResult(
            survey=survey,
            cave_name=cave_name,
            survey_date=survey_date,
            has_splays=has_splays,
        )

    def _parse_raw(self, path: Path) -> ParseResult:
        """TopoDroid raw-data export: one row per measurement.

        * from+to set           -> leg; following rows with empty from/to and
                                   leg-type 1 are repeat measurements of it.
                                   The leg is the average of its block, as in
                                   TopoDroid's reduced export.
        * from set, to empty    -> splay from `from`.
        * from empty, to set    -> splay from `to`.
        * status != 0           -> deleted/overshoot; dropped (with its repeats).
        * no stations, leg-type 0 -> unassigned shot; dropped.
        All other columns (roll, G, M, dip, raw sensor values, ...) are ignored.
        """
        survey = empty_survey()
        has_splays = False
        # Each leg block collects its measurements until the file ends.
        legs: list[tuple[dict, list[tuple[float, float, float]]]] = []
        current: list[tuple[float, float, float]] | None = None

        with open(path, encoding="utf-8") as file:
            line1 = next(file)
            line2 = next(file)
            next(file)  # column header
            survey_date = _dt.datetime.strptime(line1[2:12], "%Y.%m.%d")
            cave_name = line2[1:].split(",")[0].strip()

            for lineno, row in enumerate(file, start=4):
                if not row.strip() or row.startswith("#"):
                    continue
                cols = row.rstrip("\r\n").split(",", 23)
                if len(cols) < _R_MIN_COLS:
                    raise ParseError(f"Line {lineno}: expected at least {_R_MIN_COLS} columns, got {len(cols)}")
                st_from, st_to = cols[_R_FROM].strip(), cols[_R_TO].strip()
                ok = cols[_R_STATUS].strip() == _STATUS_NORMAL
                try:
                    meas = (float(cols[_R_DIST]), float(cols[_R_AZI]), float(cols[_R_CLINO]))
                except ValueError as e:
                    raise ParseError(f"Line {lineno}: bad number ({e})") from e

                if not st_from and not st_to:
                    if cols[_R_LEG_TYPE].strip() == _LEG_TYPE_REPEAT and current is not None and ok:
                        current.append(meas)
                    continue  # repeat of a dropped leg, or an unassigned shot
                current = None
                if not ok:
                    continue
                if st_from and st_to:
                    current = [meas]
                    shot = _shot(st_from, st_to, 0.0, 0.0, 0.0, is_splay=False)
                    legs.append((shot, current))
                    survey["viz"].append(shot)
                else:
                    dist, azi, clino = meas
                    station = st_from
                    if not st_from:  # shot from the 'to' side: reverse it
                        station, azi, clino = st_to, (azi + 180.0) % 360.0, -clino
                    survey["viz"].append(_shot(station, "*" + station, dist, azi, clino, is_splay=True))
                    has_splays = True

        for shot, block in legs:
            shot["l"] = round(sum(m[0] for m in block) / len(block), 3)
            shot["a"] = round(_mean_azimuth([m[1] for m in block]), 2) % 360.0  # never 360.0
            shot["f"] = round(sum(m[2] for m in block) / len(block), 2)

        return ParseResult(
            survey=survey,
            cave_name=cave_name,
            survey_date=survey_date,
            has_splays=has_splays,
        )
