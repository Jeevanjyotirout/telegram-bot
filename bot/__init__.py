"""
GuardBot - Bot Package
Initializes the Telegram bot package and exposes core entry functions.
"""

# Expose main bot runner
"""
GuardBot bot package
"""

from .bot import run_bot

__all__ = ["run_bot"]

# Optional: expose handlers if needed elsewhere
from .handlers import (
    handle_message,
    cmd_start,
    cmd_status,
    cmd_rules,
    error_handler,
    register_handlers,
)

__all__ = [
    "run_bot",
    "handle_message",
    "cmd_start",
    "cmd_status",
    "cmd_rules",
    "error_handler",
    "register_handlers",
]