"""
GuardBot - Professional Telegram Moderation Bot
Entry point
"""

import logging
from bot import run_bot

if __name__ == "__main__":
    run_bot()
from logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting GuardBot...")
    run_bot()
