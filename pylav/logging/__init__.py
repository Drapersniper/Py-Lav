from __future__ import annotations

import logging
import os

from red_commons.logging import RedTraceLogger  # type: ignore
from red_commons.logging import getLogger as redgetLogger
from red_commons.logging import maybe_update_logger_class

__all__ = ("getLogger",)

maybe_update_logger_class()

LOGGER_PREFIX = os.getenv("PYLAV__LOGGER_PREFIX", "")

logging.getLogger("deepdiff.diff").setLevel(logging.FATAL)
logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("aiohttp_client_cache").setLevel(logging.ERROR)


def getLogger(name: str) -> RedTraceLogger:
    return redgetLogger(f"{LOGGER_PREFIX}{name}")
