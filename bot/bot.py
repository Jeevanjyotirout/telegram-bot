"""
GuardBot Application Bootstrap
Initializes database, registers handlers, and starts the Telegram bot.
"""

import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import BOT_TOKEN
from database.db import init_db
from bot.handlers import (
    handle_message,
    cmd_start,
    cmd_status,
    cmd_rules,
    error_handler,
)

# ----------------------------------------------------
# Logging configuration
# ----------------------------------------------------

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("guardbot")


# ----------------------------------------------------
# Bot runner
# ----------------------------------------------------

def run_bot() -> None:
    """
    Entry point to start GuardBot.
    """

    logger.info("Starting GuardBot...")

    # 1️⃣ Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # 2️⃣ Build Telegram application
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
    except Exception as e:
        logger.error(f"Failed to create Telegram application: {e}")
        raise

    # 3️⃣ Register command handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("rules", cmd_rules))

    # 4️⃣ Register message handler (groups only)
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
            handle_message,
        )
    )

    # 5️⃣ Register error handler
    application.add_error_handler(error_handler)

    logger.info("GuardBot is now running and monitoring messages.")

    # 6️⃣ Start polling
    application.run_polling(drop_pending_updates=True)