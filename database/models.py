"""
GuardBot Database Models
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Float,
    DateTime, Boolean, Text, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Tracks every user GuardBot has seen."""
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(BigInteger, unique=True, nullable=False, index=True)
    username        = Column(String(64), nullable=True)
    full_name       = Column(String(128), nullable=True)
    first_seen      = Column(DateTime, default=datetime.utcnow)
    last_seen       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_banned       = Column(Boolean, default=False)
    ban_reason      = Column(Text, nullable=True)
    reputation      = Column(Float, default=100.0)   # 0–100 score

    violations  = relationship("Violation",   back_populates="user", cascade="all, delete-orphan")
    daily_stats = relationship("DailyStat",   back_populates="user", cascade="all, delete-orphan")
    actions     = relationship("ModerationAction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.user_id} name={self.full_name} banned={self.is_banned}>"


class Violation(Base):
    """One row per violation incident."""
    __tablename__ = "violations"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    chat_id         = Column(BigInteger, nullable=False)
    violation_type  = Column(String(32), nullable=False)   # SPAM | TOXIC | IRRELEVANT | LINK_SPAM | FLOOD
    violation_date  = Column(DateTime, default=datetime.utcnow)
    message_text    = Column(Text, nullable=True)
    score           = Column(Float, nullable=True)
    action_taken    = Column(String(32), nullable=True)    # DELETED | WARNED | MUTED | BANNED

    user = relationship("User", back_populates="violations")

    def __repr__(self):
        return f"<Violation user={self.user_id} type={self.violation_type}>"


class DailyStat(Base):
    """Per-user, per-chat daily counters (reset each UTC day)."""
    __tablename__ = "daily_stats"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    chat_id             = Column(BigInteger, nullable=False)
    stat_date           = Column(String(10), nullable=False)   # "YYYY-MM-DD"
    message_count       = Column(Integer, default=0)
    link_count          = Column(Integer, default=0)
    irrelevant_count    = Column(Integer, default=0)
    violation_count     = Column(Integer, default=0)
    warning_count       = Column(Integer, default=0)

    user = relationship("User", back_populates="daily_stats")

    def __repr__(self):
        return f"<DailyStat user={self.user_id} date={self.stat_date}>"


class ModerationAction(Base):
    """Full audit log of every action GuardBot took."""
    __tablename__ = "moderation_actions"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    chat_id     = Column(BigInteger, nullable=False)
    action      = Column(String(32), nullable=False)   # DELETE | WARN | MUTE | BAN
    reason      = Column(Text, nullable=True)
    detail      = Column(Text, nullable=True)          # JSON payload (scores, etc.)
    performed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="actions")

    def __repr__(self):
        return f"<ModerationAction action={self.action} user={self.user_id}>"


class GroupConfig(Base):
    """Per-group configurable settings (future admin dashboard support)."""
    __tablename__ = "group_configs"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    chat_id                 = Column(BigInteger, unique=True, nullable=False, index=True)
    chat_title              = Column(String(256), nullable=True)
    spam_enabled            = Column(Boolean, default=True)
    sentiment_enabled       = Column(Boolean, default=True)
    topic_filter_enabled    = Column(Boolean, default=True)
    link_filter_enabled     = Column(Boolean, default=True)
    flood_filter_enabled    = Column(Boolean, default=True)
    violation_ban_days      = Column(Integer, default=3)
    created_at              = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GroupConfig chat_id={self.chat_id}>"
