"""
GuardBot Topic Detector
Determines whether a message is relevant to the group's allowed topics.
"""

import re
import logging
from dataclasses import dataclass
from typing import List

from config.settings import ALLOWED_TOPIC_KEYWORDS

logger = logging.getLogger(__name__)

# Phrases that are always acceptable (greetings, meta-conversation)
ALWAYS_ALLOWED = [
    "hello", "hi", "hey", "good morning", "good evening", "good night",
    "thanks", "thank you", "ok", "okay", "yes", "no", "sure", "agree",
    "welcome", "congratulations", "happy", "bye", "goodbye",
    "please", "sorry", "excuse me",
]


@dataclass
class TopicResult:
    is_relevant: bool
    score: float         # 0.0 (irrelevant) → 1.0 (highly relevant)
    matched_keywords: List[str]
    is_greeting: bool


class TopicDetector:
    """
    Checks whether a message belongs to the configured allowed topics.

    Scoring:
        Each keyword match   → +0.25 (capped at 1.0)
        Greeting detected    → always relevant
        Short message (<4w)  → treated as neutral (relevant)
    """

    def __init__(self):
        self._topics    = [kw.lower() for kw in ALLOWED_TOPIC_KEYWORDS]
        self._greetings = [g.lower() for g in ALWAYS_ALLOWED]
        logger.info("TopicDetector initialised.")

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(self, text: str) -> TopicResult:
        if not text:
            return TopicResult(True, 1.0, [], False)

        text_lc = text.lower()
        words   = re.findall(r"\b\w+\b", text_lc)

        # Short messages / greetings → allow
        if len(words) <= 4:
            return TopicResult(True, 1.0, [], False)

        is_greeting = any(g in text_lc for g in self._greetings)
        if is_greeting and len(words) <= 10:
            return TopicResult(True, 1.0, [], True)

        # Keyword matching
        matched = [kw for kw in self._topics if kw in text_lc]
        score   = round(min(1.0, len(matched) * 0.25), 3)

        logger.debug(f"TopicDetector score={score} matched={matched}")
        return TopicResult(
            is_relevant=score >= 0.25 or is_greeting,
            score=score,
            matched_keywords=matched,
            is_greeting=is_greeting,
        )
