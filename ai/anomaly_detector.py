"""
GuardBot Anomaly Detector
Flood detection and raid protection.
"""

import time
import logging
from collections import defaultdict
from dataclasses import dataclass

from config.settings import MESSAGE_FLOOD_LIMIT, MESSAGE_FLOOD_WINDOW

logger = logging.getLogger(__name__)


@dataclass
class FloodResult:
    is_flood: bool
    message_count: int
    window_seconds: int


class AnomalyDetector:
    """
    Detects message flooding (too many messages in a short window).

    Uses an in-memory sliding-window counter.
    Resets automatically as time passes.
    """

    def __init__(self):
        # {(user_id, chat_id): [timestamp, ...]}
        self._timestamps: dict = defaultdict(list)
        logger.info("AnomalyDetector initialised.")

    def check_flood(self, user_id: int, chat_id: int) -> FloodResult:
        key = (user_id, chat_id)
        now = time.monotonic()
        window_start = now - MESSAGE_FLOOD_WINDOW

        # Prune old entries
        self._timestamps[key] = [t for t in self._timestamps[key] if t > window_start]
        self._timestamps[key].append(now)

        count = len(self._timestamps[key])
        is_flood = count > MESSAGE_FLOOD_LIMIT

        if is_flood:
            logger.warning(f"Flood detected: user={user_id} chat={chat_id} count={count}")

        return FloodResult(
            is_flood=is_flood,
            message_count=count,
            window_seconds=MESSAGE_FLOOD_WINDOW,
        )

    def reset(self, user_id: int, chat_id: int) -> None:
        self._timestamps.pop((user_id, chat_id), None)
