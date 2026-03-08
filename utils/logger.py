"""
GuardBot Logger Setup
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import LOG_FILE, LOG_LEVEL, LOG_FORMAT


def setup_logger() -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = logging.Formatter(LOG_FORMAT)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # Rotating file handler (5 MB × 3 files)
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(fmt)
    root.addHandler(fh)
