"""Read/write `config_settings.json`.

Wraps the raw JSON shape so a future schema migration touches only this file.
"""
from __future__ import annotations

import json
from typing import Any

from surveyscraper.paths import CONFIG_PATH


def read_config() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def write_config(config: dict[str, Any]) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def update_config(**fields: Any) -> dict[str, Any]:
    config = read_config()
    config.update(fields)
    write_config(config)
    return config
