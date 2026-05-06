"""TopoDroid (.csv) parser.

Handles both pre-v6.4 and v6.4+ header formats. Splay shots are kept in the
result (with `is_splay=True`) so the GUI can include them in the CSV export;
they are filtered out of the version uploaded to Speleoliti Online.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

from surveyscraper.core.errors import ParseError
from surveyscraper.parsers.base import BaseParser, ParseResult, empty_survey


class TopoDroidParser(BaseParser):
    def parse(self, path: Path) -> ParseResult:
        try:
            return self._parse(path)
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse TopoDroid file: {e}") from e

    def _parse(self, path: Path) -> ParseResult:
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
