"""
GuardBot Sentiment Analyser
Uses vaderSentiment (fast, no GPU required) with optional transformer upgrade path.
"""

import logging
from dataclasses import dataclass

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Toxic / abusive word list for rule-based fallback
TOXIC_KEYWORDS = [
    "idiot", "stupid", "moron", "dumb", "loser", "hate you",
    "shut up", "go die", "kill yourself", "scam", "fraud", "liar",
    "useless", "pathetic", "trash", "garbage", "worst", "disgusting",
    "bastard", "fool", "beggar", "harass", "threat", "abuse",
]


@dataclass
class SentimentResult:
    is_toxic: bool
    score: float          # 0.0 (neutral) → 1.0 (very toxic)
    compound: float       # VADER compound: -1.0 → +1.0
    label: str            # POSITIVE | NEUTRAL | NEGATIVE | TOXIC


class SentimentAnalyzer:
    """
    Analyses message toxicity.

    Scoring:
        VADER compound < -0.5   → base toxic score 0.55
        VADER compound < -0.7   → base toxic score 0.75
        Toxic keyword match     → +0.20 per hit (capped at +0.40)
        Fallback (no VADER)     → keyword-only scoring
    """

    def __init__(self):
        if VADER_AVAILABLE:
            self._analyzer = SentimentIntensityAnalyzer()
            logger.info("SentimentAnalyzer: VADER loaded.")
        else:
            self._analyzer = None
            logger.warning("SentimentAnalyzer: vaderSentiment not installed. "
                           "Using keyword-only fallback.")

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(self, text: str) -> SentimentResult:
        if not text:
            return SentimentResult(False, 0.0, 0.0, "NEUTRAL")

        text_lc  = text.lower()
        compound = 0.0
        score    = 0.0

        # VADER scoring
        if self._analyzer:
            vs       = self._analyzer.polarity_scores(text)
            compound = vs["compound"]
            if compound < -0.70:
                score = 0.75
            elif compound < -0.50:
                score = 0.55
            elif compound < -0.30:
                score = 0.35

        # Keyword boost
        hits = [kw for kw in TOXIC_KEYWORDS if kw in text_lc]
        if hits:
            score += min(0.40, len(hits) * 0.20)

        score = round(min(score, 1.0), 3)

        if score >= 0.60:
            label = "TOXIC"
        elif compound < -0.30 or score >= 0.35:
            label = "NEGATIVE"
        elif compound > 0.30:
            label = "POSITIVE"
        else:
            label = "NEUTRAL"

        logger.debug(f"SentimentAnalyzer compound={compound} score={score} label={label}")
        return SentimentResult(
            is_toxic=score >= 0.60,
            score=score,
            compound=compound,
            label=label,
        )
