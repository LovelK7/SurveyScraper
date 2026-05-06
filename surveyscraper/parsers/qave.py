"""Qave / Walls (.srv) parser.

Qave files are tab-delimited. Parsing stops at the first row whose `to`
field is "-". The shot dict preserves the legacy field order — note that
`f` (inclination) precedes `a` (azimuth) here, intentional for byte-identical
JSON output.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

from surveyscraper.core.errors import ParseError
from surveyscraper.parsers.base import BaseParser, ParseResult, empty_survey


class QaveParser(BaseParser):
    def parse(self, path: Path) -> ParseResult:
        try:
            return self._parse(path)
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse Qave file: {e}") from e

    def _parse(self, path: Path) -> ParseResult:
        survey = empty_survey()
        survey_date: _dt.datetime | None = None

        with open(path) as file:
            for _ in range(4):
                next(file)
            date = next(file).split(" ")[1].strip()
            survey_date = _dt.datetime.strptime(date, "%Y-%m-%d")
            next(file)
            next(file)
            for row in file:
                shot = row.strip().split("\t")
                if shot[1] == "-":
                    break
                survey["viz"].append({
                    "t1": shot[0],
                    "t2": shot[1],
                    "l": float(shot[2]),
                    "f": float(shot[4]),
                    "a": float(shot[3]),
                    "left": "null",
                    "right": "null",
                    "up": "null",
                    "down": "null",
                    "note": "",
                    "flags": "",
                })

        return ParseResult(survey=survey, survey_date=survey_date)
