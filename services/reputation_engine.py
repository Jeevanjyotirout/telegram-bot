"""
GuardBot Reputation Engine
Manages user reputation scores (0–100).
"""

import logging
from database.db   import get_db
from database.crud import update_reputation, get_user

logger = logging.getLogger(__name__)

# Points awarded / deducted
REPUTATION_EVENTS = {
    "good_message"    : +1.0,
    "spam"            : -10.0,
    "toxic"           : -15.0,
    "irrelevant"      : -3.0,
    "link_spam"       : -5.0,
    "flood"           : -8.0,
    "ban"             : -50.0,
}


class ReputationEngine:

    def apply_event(self, user_id: int, event: str) -> float:
        delta = REPUTATION_EVENTS.get(event, 0.0)
        if delta == 0.0:
            return 100.0
        with get_db() as db:
            new_score = update_reputation(db, user_id, delta)
        logger.debug(f"Reputation event={event} delta={delta} user={user_id} new={new_score}")
        return new_score

    def get_score(self, user_id: int) -> float:
        with get_db() as db:
            user = get_user(db, user_id)
            return user.reputation if user else 100.0
