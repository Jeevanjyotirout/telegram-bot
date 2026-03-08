"""
GuardBot Activity Tracker
Tracks per-user message bursts and activity patterns.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List

logger = logging.getLogger(__name__)

BURST_WINDOW = 300   # 5-minute window for pattern analysis


class ActivityTracker:
    """
    Tracks recent message timestamps and text for pattern detection.

    Detects:
        - Message repetition (copy-paste spam)
        - Rapid-fire burst activity
    """

    def __init__(self):
        # {(user_id, chat_id): [(timestamp, text), ...]}
        self._history: Dict = defaultdict(list)
        logger.info("ActivityTracker initialised.")

    def record(self, user_id: int, chat_id: int, text: str) -> None:
        key = (user_id, chat_id)
        now = time.monotonic()
        self._history[key].append((now, text.lower().strip()))
        # Prune entries older than BURST_WINDOW
        cutoff = now - BURST_WINDOW
        self._history[key] = [(t, m) for t, m in self._history[key] if t > cutoff]

    def is_repeated_message(self, user_id: int, chat_id: int,
                            text: str, threshold: int = 3) -> bool:
        """Returns True if the same message has been sent ≥ threshold times."""
        key    = (user_id, chat_id)
        t_text = text.lower().strip()
        count  = sum(1 for _, m in self._history[key] if m == t_text)
        return count >= threshold

    def recent_message_count(self, user_id: int, chat_id: int) -> int:
        return len(self._history[(user_id, chat_id)])
