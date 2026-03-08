"""
GuardBot Spam Detector
Three-layer detection: keyword → link → heuristic patterns
"""

import re
import logging
from dataclasses import dataclass
from typing import List

from config.settings import SPAM_KEYWORDS, SUSPICIOUS_LINK_PATTERNS

logger = logging.getLogger(__name__)


# Detect URLs in messages
URL_PATTERN = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|\b\w+\.(com|net|org|io|co|me|xyz|top|club|tk|ml|ga|cf)\b)",
    re.IGNORECASE,
)


# Result object returned by detector
@dataclass
class SpamResult:
    is_spam: bool
    score: float
    reasons: List[str]
    link_count: int


class SpamDetector:
    """
    GuardBot layered spam detector

    Score calculation:

    keyword hit        → +0.35 each (max 0.70)
    suspicious link    → +0.30 each (max 0.60)
    excessive CAPS     → +0.15
    repeated chars     → +0.10

    Spam threshold = 0.65
    """

    SPAM_THRESHOLD = 0.65

    def __init__(self):
        self.keywords = [k.lower() for k in SPAM_KEYWORDS]
        self.link_patterns = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_LINK_PATTERNS]

        logger.info("SpamDetector initialized.")

    # ------------------------------------------------
    # Main analysis function
    # ------------------------------------------------

    def analyze(self, text: str) -> SpamResult:

        if not text:
            return SpamResult(False, 0.0, [], 0)

        score = 0.0
        reasons = []
        text_lower = text.lower()

        # ------------------------------------------------
        # 1️⃣ Keyword detection
        # ------------------------------------------------

        keyword_hits = [kw for kw in self.keywords if kw in text_lower]

        if keyword_hits:
            keyword_score = min(0.70, len(keyword_hits) * 0.35)
            score += keyword_score
            reasons.append(f"Spam keywords: {keyword_hits[:3]}")

        # ------------------------------------------------
        # 2️⃣ Link detection
        # ------------------------------------------------

        urls = [u[0] if isinstance(u, tuple) else u for u in URL_PATTERN.findall(text)]
        link_count = len(urls)

        if urls:

            suspicious_links = [
                url for url in urls
                if any(pattern.search(url) for pattern in self.link_patterns)
            ]

            if suspicious_links:
                link_score = min(0.60, len(suspicious_links) * 0.30)
                score += link_score
                reasons.append(f"Suspicious links detected ({len(suspicious_links)})")

        # ------------------------------------------------
        # 3️⃣ Excessive CAPS
        # ------------------------------------------------

        letters = [c for c in text if c.isalpha()]

        if letters:
            caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)

            if caps_ratio > 0.70:
                score += 0.15
                reasons.append("Excessive capital letters")

        # ------------------------------------------------
        # 4️⃣ Repeated characters
        # ------------------------------------------------

        if re.search(r"(.)\1{4,}", text):
            score += 0.10
            reasons.append("Repeated characters")

        # ------------------------------------------------
        # Final score
        # ------------------------------------------------

        score = round(min(score, 1.0), 3)

        logger.debug(f"Spam score={score}, reasons={reasons}")

        return SpamResult(
            is_spam=score >= self.SPAM_THRESHOLD,
            score=score,
            reasons=reasons,
            link_count=link_count,
        )

    # ------------------------------------------------
    # Helper: count links
    # ------------------------------------------------

    def count_links(self, text: str) -> int:
        if not text:
            return 0

        urls = URL_PATTERN.findall(text)
        return len(urls)