"""Application logging.

A single rotating file handler at `paths.LOG_PATH` plus a stderr handler.
Replaces `print()` and `traceback.print_exc()` calls scattered through the
legacy script.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from surveyscraper.paths import LOG_PATH

_LOGGER_NAME = "surveyscraper"
_configured = False


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure the root app logger. Idempotent."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    if _configured:
        return logger

    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    try:
        file_handler = RotatingFileHandler(
            LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        # Disk read-only / permission denied — fall back to stderr only.
        pass

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(fmt)
    logger.addHandler(stderr_handler)

    _configured = True
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    if name is None or name == _LOGGER_NAME:
        return logging.getLogger(_LOGGER_NAME)
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")
