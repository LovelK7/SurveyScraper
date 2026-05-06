"""Parser base class and shared helpers.

Field-order conventions in the survey/shot dicts are intentional: the
exact key order is preserved so the JSON written to disk is byte-identical
to the legacy script's output (Speleoliti Online consumes this shape).
"""
from __future__ import annotations

import datetime as _dt
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

SURVEY_KEYS: tuple[str, ...] = ("fix", "x", "y", "z", "dcl", "name", "descr", "viz")
NULL_PLACEHOLDER: str = "null"


def empty_survey() -> dict[str, Any]:
    """Return the standard empty survey dict, in the exact field order written to disk."""
    return {
        "fix": "",
        "x": "",
        "y": "",
        "z": "",
        "dcl": "",
        "name": "",
        "descr": "",
        "viz": [NULL_PLACEHOLDER],
    }


class ParseResult:
    """In-memory result of a parse run.

    `survey` matches the legacy on-disk shape including the `["null", ...]`
    placeholder at index 0 of `viz`. `cave_name` and `survey_date` are
    populated when the source format includes them (TopoDroid; Qave for
    the date only).
    """

    __slots__ = ("survey", "cave_name", "survey_date", "has_splays")

    def __init__(
        self,
        survey: dict[str, Any],
        cave_name: str | None = None,
        survey_date: _dt.datetime | None = None,
        has_splays: bool = False,
    ) -> None:
        self.survey = survey
        self.cave_name = cave_name
        self.survey_date = survey_date
        self.has_splays = has_splays

    def survey_for_speleoliti(self) -> dict[str, Any]:
        """Return a copy of the survey dict with splays filtered out.

        Speleoliti Online cannot render splay shots, so the upload-to-web
        version drops them. Non-splay parsers return a dict equivalent to
        `survey` (a shallow copy).
        """
        if not self.has_splays:
            # Cheap shallow copy is fine — viz contents are never mutated by
            # Speleoliti automation.
            return dict(self.survey)
        filtered = dict(self.survey)
        viz = self.survey["viz"]
        filtered["viz"] = [viz[0]] + [s for s in viz[1:] if not s.get("is_splay", False)]
        return filtered


class BaseParser(ABC):
    """Abstract base for survey-file parsers."""

    @abstractmethod
    def parse(self, path: Path) -> ParseResult:
        """Parse `path` and return a populated `ParseResult`. Raise `ParseError` on failure."""
        raise NotImplementedError
