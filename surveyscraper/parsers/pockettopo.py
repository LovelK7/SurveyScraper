"""PocketTopo (.txt) parser.

PocketTopo records each leg three times for redundancy. When three repeats
share both endpoints, their length/azimuth/inclination are averaged into
one shot; otherwise the first repeat is kept.
"""
from __future__ import annotations

import re
from pathlib import Path

from surveyscraper.core.errors import ParseError
from surveyscraper.parsers.base import BaseParser, ParseResult, empty_survey

_BRACKET_RE = re.compile(r"\[.\]")
_ARROW_RE = re.compile(r"<")


class PocketTopoParser(BaseParser):
    def parse(self, path: Path) -> ParseResult:
        try:
            return self._parse(path)
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse PocketTopo file: {e}") from e

    def _parse(self, path: Path) -> ParseResult:
        survey = empty_survey()

        with open(path) as file:
            for _ in range(6):
                next(file)

            three_shots: list[list[str]] = []
            for row in file:
                row_data = _BRACKET_RE.sub("", row)
                row_data = _ARROW_RE.sub("", row_data)
                shot = row_data.split()
                if len(shot) != 5:
                    continue

                three_shots.append(shot)
                if len(three_shots) == 2 and (
                    three_shots[1][0] != three_shots[0][0]
                    or three_shots[1][1] != three_shots[0][1]
                ):
                    survey["viz"].append({
                        "t1": three_shots[0][0],
                        "t2": three_shots[0][1],
                        "l": f"{float(three_shots[0][2]):.3f}",
                        "a": f"{float(three_shots[0][3]):.3f}",
                        "f": f"{float(three_shots[0][4]):.3f}",
                        "left": "null",
                        "right": "null",
                        "up": "null",
                        "down": "null",
                        "note": "",
                        "flags": "",
                    })
                    three_shots.pop(0)
                elif len(three_shots) == 3:
                    mean_len = (
                        float(three_shots[0][2])
                        + float(three_shots[1][2])
                        + float(three_shots[2][2])
                    ) / 3
                    mean_dir = (
                        float(three_shots[0][3])
                        + float(three_shots[1][3])
                        + float(three_shots[2][3])
                    ) / 3
                    mean_inc = (
                        float(three_shots[0][4])
                        + float(three_shots[1][4])
                        + float(three_shots[2][4])
                    ) / 3
                    survey["viz"].append({
                        "t1": three_shots[0][0],
                        "t2": three_shots[0][1],
                        "l": mean_len,
                        "a": mean_dir,
                        "f": mean_inc,
                        "left": "null",
                        "right": "null",
                        "up": "null",
                        "down": "null",
                        "note": "",
                        "flags": "",
                    })
                    three_shots.clear()

        return ParseResult(survey=survey)
