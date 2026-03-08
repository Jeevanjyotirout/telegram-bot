"""
GuardBot CRUD Operations
"""

import json
import logging
from datetime import datetime, date
from typing import Optional

from sqlalchemy.orm import Session

from database.models import User, Violation, DailyStat, ModerationAction, GroupConfig

logger = logging.getLogger(__name__)


# ─── User ─────────────────────────────────────────────────────────────────────

def get_or_create_user(db: Session, user_id: int, username: str = None,
                       full_name: str = None) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, username=username, full_name=full_name)
        db.add(user)
        db.flush()
        logger.debug(f"New user created: {user_id}")
    else:
        user.last_seen = datetime.utcnow()
        if username:
            user.username = username
        if full_name:
            user.full_name = full_name
    return user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def ban_user(db: Session, user_id: int, reason: str) -> None:
    user = get_user(db, user_id)
    if user:
        user.is_banned = True
        user.ban_reason = reason
        logger.info(f"User {user_id} banned: {reason}")


def update_reputation(db: Session, user_id: int, delta: float) -> float:
    user = get_user(db, user_id)
    if user:
        user.reputation = max(0.0, min(100.0, user.reputation + delta))
        return user.reputation
    return 100.0


# ─── Daily Stats ──────────────────────────────────────────────────────────────

def _today() -> str:
    return date.today().isoformat()


def get_daily_stat(db: Session, user_id: int, chat_id: int) -> DailyStat:
    today = _today()
    stat = (db.query(DailyStat)
              .filter(DailyStat.user_id == user_id,
                      DailyStat.chat_id == chat_id,
                      DailyStat.stat_date == today)
              .first())
    if not stat:
        stat = DailyStat(user_id=user_id, chat_id=chat_id, stat_date=today)
        db.add(stat)
        db.flush()
    return stat


def increment_message_count(db: Session, user_id: int, chat_id: int) -> int:
    stat = get_daily_stat(db, user_id, chat_id)
    stat.message_count += 1
    return stat.message_count


def increment_link_count(db: Session, user_id: int, chat_id: int) -> int:
    stat = get_daily_stat(db, user_id, chat_id)
    stat.link_count += 1
    return stat.link_count


def increment_irrelevant_count(db: Session, user_id: int, chat_id: int) -> int:
    stat = get_daily_stat(db, user_id, chat_id)
    stat.irrelevant_count += 1
    return stat.irrelevant_count


def increment_violation_count(db: Session, user_id: int, chat_id: int) -> int:
    stat = get_daily_stat(db, user_id, chat_id)
    stat.violation_count += 1
    return stat.violation_count


# ─── Violations ───────────────────────────────────────────────────────────────

def add_violation(db: Session, user_id: int, chat_id: int,
                  violation_type: str, message_text: str = None,
                  score: float = None, action_taken: str = None) -> Violation:
    v = Violation(
        user_id=user_id,
        chat_id=chat_id,
        violation_type=violation_type,
        message_text=message_text,
        score=score,
        action_taken=action_taken,
    )
    db.add(v)
    db.flush()
    return v


def count_violation_days(db: Session, user_id: int, chat_id: int) -> int:
    """Count distinct calendar days on which the user had violations."""
    rows = (db.query(Violation)
              .filter(Violation.user_id == user_id, Violation.chat_id == chat_id)
              .all())
    days = {v.violation_date.date() for v in rows}
    return len(days)


def get_all_violations(db: Session, user_id: int, chat_id: int):
    return (db.query(Violation)
              .filter(Violation.user_id == user_id, Violation.chat_id == chat_id)
              .order_by(Violation.violation_date.desc())
              .all())


# ─── Moderation Actions ───────────────────────────────────────────────────────

def log_action(db: Session, user_id: int, chat_id: int,
               action: str, reason: str = None, detail: dict = None) -> ModerationAction:
    ma = ModerationAction(
        user_id=user_id,
        chat_id=chat_id,
        action=action,
        reason=reason,
        detail=json.dumps(detail) if detail else None,
    )
    db.add(ma)
    db.flush()
    logger.info(f"Action logged: {action} | user={user_id} | reason={reason}")
    return ma


# ─── Group Config ─────────────────────────────────────────────────────────────

def get_or_create_group_config(db: Session, chat_id: int,
                               chat_title: str = None) -> GroupConfig:
    cfg = db.query(GroupConfig).filter(GroupConfig.chat_id == chat_id).first()
    if not cfg:
        cfg = GroupConfig(chat_id=chat_id, chat_title=chat_title)
        db.add(cfg)
        db.flush()
    return cfg
