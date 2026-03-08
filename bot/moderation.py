"""
GuardBot Moderation Engine
Central brain that evaluates messages and decides moderation actions.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from ai.spam_detector import SpamDetector, SpamResult
from ai.sentiment_analyzer import SentimentAnalyzer, SentimentResult
from ai.topic_detector import TopicDetector, TopicResult
from ai.anomaly_detector import AnomalyDetector, FloodResult

from config.settings import (
    LINK_WARN_THRESHOLD,
    TOPIC_WARN_THRESHOLD,
    VIOLATION_BAN_DAYS,
)

from database.db import get_db
from database.crud import (
    get_or_create_user,
    add_violation,
    count_violation_days,
    increment_link_count,
    increment_irrelevant_count,
    increment_violation_count,
    log_action,
    ban_user,
)
# ----------------------------------------
# Moderation thresholds
# ----------------------------------------

SPAM_SCORE_THRESHOLD = 0.65
TOXICITY_SCORE_THRESHOLD = 0.60

LINK_WARN_THRESHOLD = 3
TOPIC_WARN_THRESHOLD = 5

VIOLATION_BAN_DAYS = 3

logger = logging.getLogger(__name__)


# ----------------------------------------------------
# Moderation Decision Object
# ----------------------------------------------------

@dataclass
class ModerationDecision:

    delete_message: bool = False
    warn_user: bool = False
    ban_user: bool = False
    alert_admins: bool = False

    reasons: List[str] = field(default_factory=list)
    violation_type: Optional[str] = None

    score: float = 0.0
    violation_days: int = 0


# ----------------------------------------------------
# Moderation Engine
# ----------------------------------------------------

class ModerationEngine:

    def __init__(self):

        self.spam = SpamDetector()
        self.sentiment = SentimentAnalyzer()
        self.topic = TopicDetector()
        self.anomaly = AnomalyDetector()

        logger.info("ModerationEngine initialized.")

    # ------------------------------------------------

    def evaluate(
        self,
        user_id: int,
        chat_id: int,
        username: str,
        full_name: str,
        text: str,
    ) -> ModerationDecision:

        decision = ModerationDecision()

        with get_db() as db:

            # ensure user exists
            get_or_create_user(db, user_id, username, full_name)

            # ------------------------------------------------
            # Flood detection
            # ------------------------------------------------

            flood: FloodResult = self.anomaly.check_flood(user_id, chat_id)

            if flood.is_flood:

                decision.delete_message = True
                decision.violation_type = "FLOOD"

                decision.reasons.append(
                    f"Flood detected: {flood.message_count} messages"
                )

                add_violation(
                    db,
                    user_id,
                    chat_id,
                    "FLOOD",
                    text[:200],
                    action_taken="DELETED",
                )

                log_action(db, user_id, chat_id, "DELETE", "Flood detected")

                return decision

            # ------------------------------------------------
            # Spam detection
            # ------------------------------------------------

            spam: SpamResult = self.spam.analyze(text)

            if spam.is_spam:

                decision.delete_message = True
                decision.warn_user = True
                decision.score = spam.score
                decision.violation_type = "SPAM"

                decision.reasons.extend(spam.reasons)

                add_violation(
                    db,
                    user_id,
                    chat_id,
                    "SPAM",
                    text[:200],
                    spam.score,
                    "WARNED",
                )

                increment_violation_count(db, user_id, chat_id)

                log_action(
                    db,
                    user_id,
                    chat_id,
                    "WARN",
                    "Spam detected",
                    {"score": spam.score},
                )

            # ------------------------------------------------
            # Link quota detection
            # ------------------------------------------------

            link_count = self.spam.count_links(text)

            if link_count > 0:

                daily_links = increment_link_count(db, user_id, chat_id)

                if daily_links > LINK_WARN_THRESHOLD:

                    decision.warn_user = True
                    decision.violation_type = decision.violation_type or "LINK_SPAM"

                    decision.reasons.append(
                        f"Too many links today ({daily_links})"
                    )

                    add_violation(
                        db,
                        user_id,
                        chat_id,
                        "LINK_SPAM",
                        text[:200],
                        action_taken="WARNED",
                    )

                    increment_violation_count(db, user_id, chat_id)

            # ------------------------------------------------
            # Toxicity detection
            # ------------------------------------------------

            sentiment: SentimentResult = self.sentiment.analyze(text)

            if sentiment.is_toxic:

                decision.delete_message = True
                decision.warn_user = True
                decision.violation_type = decision.violation_type or "TOXIC"

                decision.reasons.append(
                    f"Toxic message (score={sentiment.score})"
                )

                add_violation(
                    db,
                    user_id,
                    chat_id,
                    "TOXIC",
                    text[:200],
                    sentiment.score,
                    "WARNED",
                )

                increment_violation_count(db, user_id, chat_id)

            # ------------------------------------------------
            # Topic relevance detection
            # ------------------------------------------------

            topic: TopicResult = self.topic.analyze(text)

            if not topic.is_relevant:

                daily_irrelevant = increment_irrelevant_count(db, user_id, chat_id)

                if daily_irrelevant >= TOPIC_WARN_THRESHOLD:

                    decision.delete_message = True
                    decision.warn_user = True
                    decision.violation_type = decision.violation_type or "IRRELEVANT"

                    decision.reasons.append(
                        f"Off-topic messages today: {daily_irrelevant}"
                    )

                    add_violation(
                        db,
                        user_id,
                        chat_id,
                        "IRRELEVANT",
                        text[:200],
                        topic.score,
                        "WARNED",
                    )

                    increment_violation_count(db, user_id, chat_id)

            # ------------------------------------------------
            # Ban logic
            # ------------------------------------------------

            if decision.warn_user or decision.delete_message:

                violation_days = count_violation_days(db, user_id, chat_id)
                decision.violation_days = violation_days

                if violation_days >= VIOLATION_BAN_DAYS:

                    decision.ban_user = True
                    decision.alert_admins = True

                    ban_user(
                        db,
                        user_id,
                        f"Repeated violations for {violation_days} days",
                    )

                    log_action(
                        db,
                        user_id,
                        chat_id,
                        "BAN",
                        f"Auto-ban after {violation_days} days",
                    )

                elif violation_days >= VIOLATION_BAN_DAYS - 1:

                    decision.alert_admins = True

        return decision