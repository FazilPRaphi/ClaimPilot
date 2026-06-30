"""
Application logging configuration.

Provides a single logger factory used throughout ClaimPilot.
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)


@lru_cache(maxsize=1)
def _configure_logging() -> None:
    """
    Configure application logging once.

    The lru_cache ensures multiple imports do not attach
    duplicate handlers.
    """

    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        logging.Formatter(LOG_FORMAT)
    )

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured application logger.

    Example:
        logger = get_logger(__name__)
        logger.info("OCR completed.")
    """

    _configure_logging()

    return logging.getLogger(name)