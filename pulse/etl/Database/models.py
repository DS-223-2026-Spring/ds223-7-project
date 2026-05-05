"""
SQLAlchemy ORM models for the Pulse platform.

Note: user segmentation is handled via the user_segments join table,
not a column on users. Do not add a segment column here.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """ORM model for the users table."""

    __tablename__ = "users"

    user_id               = Column(String,   primary_key=True)
    email                 = Column(String,   nullable=False)
    display_name          = Column(String)
    plan                  = Column(String,   nullable=False, default="free")
    status                = Column(String,   nullable=False, default="active")
    created_at            = Column(DateTime)
    last_login_at         = Column(DateTime)
    days_since_last_login = Column(Integer)
    total_sessions        = Column(Integer,  default=0)
    total_exports         = Column(Integer,  default=0)
    total_paywall_hits    = Column(Integer,  default=0)
    total_thesaurus_uses  = Column(Integer,  default=0)


class Segment(Base):
    """ORM model for the segments table."""

    __tablename__ = "segments"

    segment_id  = Column(String,  primary_key=True)
    name        = Column(String,  nullable=False)
    label       = Column(String,  nullable=False)
    color_hex   = Column(String)
    description = Column(String)
    created_at  = Column(DateTime)


class Campaign(Base):
    """ORM model for the campaigns table."""

    __tablename__ = "campaigns"

    campaign_id       = Column(String,  primary_key=True)
    segment_id        = Column(String,  nullable=False)
    channel           = Column(String,  nullable=False)
    trigger_event     = Column(String,  nullable=False)
    status            = Column(String,  nullable=False, default="draft")
    active_message_id = Column(String)
    created_at        = Column(DateTime)
    launched_at       = Column(DateTime)


class SessionEvent(Base):
    """ORM model for the session_events table."""

    __tablename__ = "session_events"

    session_id       = Column(String,  primary_key=True)
    user_id          = Column(String,  nullable=False)
    started_at       = Column(DateTime)
    ended_at         = Column(DateTime)
    duration_seconds = Column(Integer)
    word_count       = Column(Integer, default=0)
    line_count       = Column(Integer, default=0)