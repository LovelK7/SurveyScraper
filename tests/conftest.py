"""Test fixtures shared across the test suite."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"

# Make sure the package is importable when running `pytest` from any cwd.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def topodroid_v6_csv() -> Path:
    return FIXTURES_DIR / "jama_Edison_2.csv"


@pytest.fixture(scope="session")
def topodroid_old_csv() -> Path:
    return FIXTURES_DIR / "krkuž_uskrs.csv"


@pytest.fixture(scope="session")
def pockettopo_txt() -> Path:
    return FIXTURES_DIR / "geyrovo.txt"


def load_golden(name: str) -> dict:
    with open(GOLDEN_DIR / name, encoding="utf-8") as f:
        return json.load(f)
