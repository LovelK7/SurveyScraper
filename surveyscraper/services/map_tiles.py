"""Make tkintermapview fetch map tiles with an app-specific User-Agent.

tkintermapview hard-codes ``User-Agent: TkinterMapView`` on every tile
request. OpenStreetMap has blocked that shared UA under its tile usage
policy (https://operations.osmfoundation.org/policies/tiles/): the server
still answers HTTP 200 but returns an "Access blocked" PNG instead of the
map. The policy asks each application to identify itself, so we swap the
``requests`` reference inside tkintermapview for a thin proxy that
rewrites the header.
"""

from __future__ import annotations

import requests

_installed = False


class _RequestsWithUserAgent:
    """Delegates to ``requests`` but forces our User-Agent on ``get``."""

    def __init__(self, user_agent: str):
        self._user_agent = user_agent

    def get(self, url, **kwargs):
        headers = dict(kwargs.pop("headers", None) or {})
        headers["User-Agent"] = self._user_agent
        kwargs.setdefault("timeout", 15)
        return requests.get(url, headers=headers, **kwargs)

    def __getattr__(self, name):
        return getattr(requests, name)


def user_agent(version: str) -> str:
    return f"SurveyScraper/{version} (cave survey desktop tool)"


def install_user_agent(version: str) -> None:
    """Patch tkintermapview's tile fetchers. Safe to call more than once."""
    global _installed
    if _installed:
        return
    from tkintermapview import map_widget, offline_loading

    proxy = _RequestsWithUserAgent(user_agent(version))
    map_widget.requests = proxy
    offline_loading.requests = proxy
    _installed = True
