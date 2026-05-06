"""Survey persistence: JSON for Speleoliti, CSV for the user.

`write_survey_json` is the on-disk writer the parsers don't perform; it's
called by the GUI after a successful parse.

`export_to_csv` is a pure-ish writer for the user's CSV. It receives the
survey dict, the cave dimensions (or None when offline), and a few flags
gathered from the GUI; the GUI is responsible for picking the destination
path and showing any user-facing dialogs.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from surveyscraper.logging_setup import get_logger

_log = get_logger("exporter")


def write_survey_json(survey: dict[str, Any], path: str | Path) -> None:
    """Write the survey dict to disk in the legacy `{viz: ["null", ...]}` shape."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(survey, f, indent=4)


def export_to_csv(
    survey: dict[str, Any],
    path: str | Path,
    *,
    software: str,
    keep_splays: bool,
    include_original_angles: bool,
    original_shots: list[dict[str, Any]] | None,
    dimensions: tuple[float | str, float | str, float | str, float | str] | None,
) -> None:
    """Write the survey to `path` as a Windows-Excel-friendly CSV.

    `dimensions` is `(poly, horizontal, elevation, depth)` when Speleoliti ran;
    `None` triggers the offline header without dimensions.
    `original_shots` carries pre-declination azimuths used when
    `include_original_angles` is True.
    """
    with open(path, "w", encoding="utf-8-sig", errors="ignore", newline="") as csv_file:
        if dimensions is not None:
            poly, horiz, elev, depth = dimensions
            description = (
                f"Ime objekta:,{survey['name']}\n"
                f"X:,{survey['x']}\n"
                f"Y:,{survey['y']}\n"
                f"Z:,{survey['z']}\n"
                f"Fiksna točka:,{survey['fix']}\n"
                f"Magn. deklinacija:,{survey['dcl']}\n"
                f"Poligonalna duljina:,{float(poly):.1f}\n"
                f"Horizontalna duljina:,{float(horiz):.1f}\n"
                f"Visinska razlika:,{float(elev):.1f}\n"
                f"Dubina od fiksne točke:,{float(depth):.1f}\n"
            )
        else:
            description = (
                f"Ime objekta:,{survey['name']}\n"
                f"X:,{survey['x']}\n"
                f"Y:,{survey['y']}\n"
                f"Z:,{survey['z']}\n"
                f"Fiksna točka:,{survey['fix']}\n"
            )
        csv_file.write(description)

        # Splay filter: only TopoDroid shots carry an `is_splay` flag.
        if software == "TopoDroid" and not keep_splays:
            filtered_shots = [s for s in survey["viz"][1:] if not s.get("is_splay", False)]
        else:
            filtered_shots = list(survey["viz"][1:])

        # Build fieldnames from the first shot (legacy behavior), excluding `is_splay`.
        fieldnames = [k for k in survey["viz"][1].keys() if k != "is_splay"]
        if include_original_angles:
            fieldnames = fieldnames + ["a_original"]
            paired = zip(filtered_shots, original_shots or [])
        else:
            paired = ((shot, None) for shot in filtered_shots)

        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for shot, original_shot in paired:
            row = {k: v for k, v in shot.items() if k != "is_splay"}
            if original_shot is not None:
                row["a_original"] = round(float(original_shot["a"]), 2)
            writer.writerow(row)
