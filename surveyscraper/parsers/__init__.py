"""Cave survey file parsers.

Each parser turns a path on disk into an in-memory `ParseResult`. The result
holds the legacy on-disk JSON shape (preserved for Speleoliti compatibility),
plus optional metadata (cave name, survey date) the GUI displays. Parsers
do not write to disk and do not show UI; failures raise `ParseError`.

Add a new parser by:
  1. Subclassing `BaseParser` in a new module (e.g. `parsers/wallsxml.py`).
  2. Registering it in `PARSERS` below.
  3. Adding a sample file to `testing/` and a golden snapshot to `tests/golden/`.
"""
from __future__ import annotations

from pathlib import Path

from surveyscraper.parsers.base import BaseParser, ParseResult
from surveyscraper.parsers.pockettopo import PocketTopoParser
from surveyscraper.parsers.qave import QaveParser
from surveyscraper.parsers.topodroid import TopoDroidParser

PARSERS: dict[str, type[BaseParser]] = {
    "TopoDroid": TopoDroidParser,
    "PocketTopo": PocketTopoParser,
    "Qave": QaveParser,
}


def parse_file(software: str, path: str | Path) -> ParseResult:
    """Dispatch to the parser registered for `software` and return its result."""
    try:
        parser_cls = PARSERS[software]
    except KeyError as exc:
        from surveyscraper.core.errors import ParseError

        raise ParseError(f"No parser registered for software: {software!r}") from exc
    return parser_cls().parse(Path(path))


__all__ = [
    "PARSERS",
    "ParseResult",
    "BaseParser",
    "TopoDroidParser",
    "PocketTopoParser",
    "QaveParser",
    "parse_file",
]
