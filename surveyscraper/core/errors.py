"""Domain exceptions for the application.

Services raise these instead of returning None or showing message boxes, so
the UI can decide how to surface the error to the user.
"""
from __future__ import annotations


class SurveyScraperError(Exception):
    """Base class for all application errors."""


class ParseError(SurveyScraperError):
    """A survey file could not be parsed."""


class NetworkError(SurveyScraperError):
    """A network-dependent operation failed (geocode, declination lookup)."""


class SpeleolitiError(SurveyScraperError):
    """The Speleoliti Online automation failed."""
